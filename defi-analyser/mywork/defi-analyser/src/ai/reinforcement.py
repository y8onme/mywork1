# src/ai/reinforcement.py

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from collections import deque, namedtuple
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import random
from ..utils.config import config
from ..utils.config.base_config import ChainConfig

Experience = namedtuple('Experience', ['state', 'action', 'reward', 'next_state', 'done'])

@dataclass
class RLState:
    chain_id: int
    protocol_states: Dict[str, Dict]
    balances: Dict[str, float]
    gas_prices: Dict[str, float]
    block_number: int
    timestamp: int

@dataclass
class RLAction:
    protocol: str
    action_type: str
    parameters: Dict
    gas_limit: int
    priority_fee: int

class DQNetwork(nn.Module):
    def __init__(self, state_size: int, action_size: int, hidden_size: int = 256):
        super().__init__()
        
        self.network = nn.Sequential(
            nn.Linear(state_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, action_size)
        )
        
        # Dueling DQN architecture
        self.advantage = nn.Sequential(
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, action_size)
        )
        
        self.value = nn.Sequential(
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, 1)
        )

    def forward(self, state: torch.Tensor) -> torch.Tensor:
        features = self.network(state)
        advantage = self.advantage(features)
        value = self.value(features)
        return value + (advantage - advantage.mean(dim=1, keepdim=True))

class ChainEnvironment:
    def __init__(self, chain_id: int):
        self.chain_config = config.get_chain_config(chain_id)
        self.chain_id = chain_id
        self.reset()
        
        # Initialize protocol states
        self.protocol_states = {
            'dexes': {name: {'liquidity': 1000.0} for name in self.chain_config.dex_addresses.keys()},
            'lending': {name: {'tvl': 1000.0} for name in self.chain_config.lending_protocols.keys()},
            'flash_loans': {name: {'available': 1000.0} for name in self.chain_config.flash_loan_providers.keys()}
        }
        
        # Gas price tracking
        self.base_gas_price = self.chain_config.max_gas_price.get(self.chain_id, 100)
        self.gas_price_history = deque(maxlen=100)

    def reset(self) -> RLState:
        """Reset environment to initial state"""
        self.current_block = 0
        self.current_timestamp = int(time.time())
        self.balances = {token: 0.0 for token in self.chain_config.stable_coins}
        self.balances[self.chain_config.wrapped_native] = 0.0
        
        return self._get_state()

    def step(self, action: RLAction) -> Tuple[RLState, float, bool, Dict]:
        """Execute action and return new state, reward, done flag, and info"""
        
        # Validate action
        if not self._is_valid_action(action):
            return self._get_state(), -1.0, True, {'error': 'Invalid action'}
            
        # Execute action
        success, profit, gas_used = self._execute_action(action)
        
        # Calculate reward
        reward = self._calculate_reward(success, profit, gas_used, action)
        
        # Update state
        self.current_block += 1
        self.current_timestamp += int(self.chain_config.block_time)
        
        # Update protocol states
        self._update_protocol_states()
        
        # Get new state
        new_state = self._get_state()
        
        # Check if episode should end
        done = self._is_episode_done()
        
        info = {
            'profit': profit,
            'gas_used': gas_used,
            'success': success
        }
        
        return new_state, reward, done, info

    def _get_state(self) -> RLState:
        """Get current state of the environment"""
        return RLState(
            chain_id=self.chain_id,
            protocol_states=self.protocol_states,
            balances=self.balances,
            gas_prices=self._get_gas_prices(),
            block_number=self.current_block,
            timestamp=self.current_timestamp
        )

    def _is_valid_action(self, action: RLAction) -> bool:
        """Validate if action is possible in current state"""
        
        # Check if protocol exists
        if action.protocol not in (list(self.chain_config.dex_addresses.keys()) +
                                 list(self.chain_config.lending_protocols.keys()) +
                                 list(self.chain_config.flash_loan_providers.keys())):
            return False
            
        # Validate gas parameters
        if action.gas_limit <= 0 or action.priority_fee < 0:
            return False
            
        # Validate action type
        valid_actions = ['swap', 'borrow', 'flash_loan', 'repay', 'provide_liquidity']
        if action.action_type not in valid_actions:
            return False
            
        return True

    def _execute_action(self, action: RLAction) -> Tuple[bool, float, int]:
        """Execute action and return success, profit, and gas used"""
        
        gas_used = random.randint(50000, 500000)  # Simulated gas usage
        
        if action.action_type == 'flash_loan':
            success, profit = self._execute_flash_loan(action)
        elif action.action_type == 'swap':
            success, profit = self._execute_swap(action)
        elif action.action_type == 'borrow':
            success, profit = self._execute_borrow(action)
        else:
            success, profit = False, 0.0
            
        return success, profit, gas_used

    def _calculate_reward(self, success: bool, profit: float, gas_used: int, action: RLAction) -> float:
        """Calculate reward for the action"""
        
        if not success:
            return -1.0
            
        # Calculate gas cost in native token
        gas_cost = gas_used * (self.base_gas_price + action.priority_fee)
        
        # Convert gas cost to ETH
        gas_cost_eth = gas_cost / 1e9  # Convert from gwei to ETH
        
        # Calculate net profit
        net_profit = profit - gas_cost_eth
        
        # Base reward on net profit
        reward = net_profit * 10  # Scale factor
        
        # Add bonus for successful complex actions
        if action.action_type == 'flash_loan' and success:
            reward += 0.5
            
        # Penalize high gas usage
        if gas_used > 300000:
            reward *= 0.9
            
        return reward

class DQNAgent:
    def __init__(self, 
                 state_size: int,
                 action_size: int,
                 chain_id: int,
                 hidden_size: int = 256,
                 memory_size: int = 100000,
                 batch_size: int = 64,
                 gamma: float = 0.99,
                 learning_rate: float = 0.001,
                 target_update: int = 10):
                 
        self.chain_config = config.get_chain_config(chain_id)
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=memory_size)
        self.batch_size = batch_size
        self.gamma = gamma
        self.target_update = target_update
        self.update_counter = 0
        
        # Networks
        self.policy_net = DQNetwork(state_size, action_size, hidden_size)
        self.target_net = DQNetwork(state_size, action_size, hidden_size)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        
        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=learning_rate)
        
        # Exploration parameters
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995

    def act(self, state: RLState, training: bool = True) -> RLAction:
        """Select action using epsilon-greedy policy"""
        
        if training and random.random() < self.epsilon:
            return self._random_action()
            
        state_tensor = self._preprocess_state(state)
        with torch.no_grad():
            q_values = self.policy_net(state_tensor)
            action_idx = q_values.argmax().item()
            
        return self._idx_to_action(action_idx)

    def train(self, experiences: List[Experience]) -> float:
        """Train the agent on a batch of experiences"""
        
        if len(self.memory) < self.batch_size:
            return 0.0
            
        # Sample batch
        batch = random.sample(self.memory, self.batch_size)
        
        # Preprocess batch
        states = torch.stack([self._preprocess_state(e.state) for e in batch])
        actions = torch.tensor([self._action_to_idx(e.action) for e in batch])
        rewards = torch.tensor([e.reward for e in batch])
        next_states = torch.stack([self._preprocess_state(e.next_state) for e in batch])
        dones = torch.tensor([e.done for e in batch])
        
        # Compute Q values
        current_q_values = self.policy_net(states).gather(1, actions.unsqueeze(1))
        next_q_values = self.target_net(next_states).max(1)[0].detach()
        target_q_values = rewards + (self.gamma * next_q_values * (1 - dones))
        
        # Compute loss
        loss = nn.MSELoss()(current_q_values, target_q_values.unsqueeze(1))
        
        # Optimize
        self.optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.policy_net.parameters(), 1.0)
        self.optimizer.step()
        
        # Update target network
        self.update_counter += 1
        if self.update_counter % self.target_update == 0:
            self.target_net.load_state_dict(self.policy_net.state_dict())
            
        # Decay epsilon
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
        
        return loss.item()

    def _preprocess_state(self, state: RLState) -> torch.Tensor:
        """Convert RLState to tensor"""
        
        # Flatten protocol states
        protocol_features = []
        for protocol_type, protocols in state.protocol_states.items():
            for protocol, values in protocols.items():
                protocol_features.extend(list(values.values()))
                
        # Flatten balances
        balance_features = list(state.balances.values())
        
        # Combine features
        features = (
            protocol_features +
            balance_features +
            [state.block_number, state.timestamp] +
            list(state.gas_prices.values())
        )
        
        return torch.tensor(features, dtype=torch.float32)

    def _random_action(self) -> RLAction:
        """Generate random action for exploration"""
        
        protocol_type = random.choice(['dex', 'lending', 'flash_loan'])
        
        if protocol_type == 'dex':
            protocol = random.choice(list(self.chain_config.dex_addresses.keys()))
            action_type = 'swap'
        elif protocol_type == 'lending':
            protocol = random.choice(list(self.chain_config.lending_protocols.keys()))
            action_type = random.choice(['borrow', 'repay'])
        else:
            protocol = random.choice(list(self.chain_config.flash_loan_providers.keys()))
            action_type = 'flash_loan'
            
        return RLAction(
            protocol=protocol,
            action_type=action_type,
            parameters={},
            gas_limit=random.randint(100000, 500000),
            priority_fee=random.randint(1, 10)
        )

    def save(self, path: str):
        """Save model weights"""
        torch.save({
            'policy_net': self.policy_net.state_dict(),
            'target_net': self.target_net.state_dict(),
            'optimizer': self.optimizer.state_dict(),
            'epsilon': self.epsilon
        }, path)

    def load(self, path: str):
        """Load model weights"""
        checkpoint = torch.load(path)
        self.policy_net.load_state_dict(checkpoint['policy_net'])
        self.target_net.load_state_dict(checkpoint['target_net'])
        self.optimizer.load_state_dict(checkpoint['optimizer'])
        self.epsilon = checkpoint['epsilon']