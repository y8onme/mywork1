# src/utils/state/state_manager.py

import asyncio
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
import time
from ..config import config
from ..logger import logger
from ..error.error_recovery import ErrorRecovery

@dataclass
class ChainState:
    chain_id: int
    block_number: int
    timestamp: int
    gas_price: int
    protocol_states: Dict[str, Dict]
    pending_transactions: List[Dict]
    last_update: float
    state_hash: str

@dataclass
class StateUpdate:
    chain_id: int
    updates: Dict[str, Dict]
    block_number: int
    timestamp: int
    source: str
    priority: int

class StateManager:
    def __init__(self):
        self.states: Dict[int, ChainState] = {}
        self.update_queue: asyncio.Queue = asyncio.Queue()
        self.error_recovery = ErrorRecovery()
        self.update_locks: Dict[int, asyncio.Lock] = {}
        
        # Initialize state for each chain
        self._initialize_chain_states()
        
        # Start update processor
        asyncio.create_task(self._process_updates())

    def _initialize_chain_states(self):
        """Initialize state tracking for all supported chains"""
        for chain_id in config.get_all_chain_ids():
            self.states[chain_id] = ChainState(
                chain_id=chain_id,
                block_number=0,
                timestamp=int(time.time()),
                gas_price=0,
                protocol_states={},
                pending_transactions=[],
                last_update=0,
                state_hash=""
            )
            self.update_locks[chain_id] = asyncio.Lock()

    async def get_state(self, chain_id: int) -> ChainState:
        """Get current state for a chain"""
        try:
            if chain_id not in self.states:
                raise ValueError(f"Chain {chain_id} not supported")
                
            async with self.update_locks[chain_id]:
                # Update state if stale
                if self._is_state_stale(chain_id):
                    await self._update_chain_state(chain_id)
                    
                return self.states[chain_id]
                
        except Exception as e:
            logger.error(f"Error getting state for chain {chain_id}: {str(e)}")
            raise

    async def update_state(self, update: StateUpdate) -> bool:
        """Queue state update"""
        try:
            await self.update_queue.put(update)
            return True
        except Exception as e:
            logger.error(f"Error queueing state update: {str(e)}")
            return False

    async def calculate_state_change(self,
                                   transaction: Dict,
                                   chain_id: int) -> Optional[Dict]:
        """Calculate expected state change from transaction"""
        try:
            current_state = await self.get_state(chain_id)
            
            # Get transaction type and target
            tx_type = transaction.get('type')
            target = transaction.get('target')
            
            if not tx_type or not target:
                return None
                
            # Calculate state changes based on transaction type
            if tx_type == 'swap':
                return await self._calculate_swap_state_change(
                    transaction,
                    current_state
                )
            elif tx_type == 'flash_loan':
                return await self._calculate_flash_loan_state_change(
                    transaction,
                    current_state
                )
            elif tx_type in ['borrow', 'repay']:
                return await self._calculate_lending_state_change(
                    transaction,
                    current_state
                )
                
            return None
            
        except Exception as e:
            logger.error(f"Error calculating state change: {str(e)}")
            return None

    async def _process_updates(self):
        """Process queued state updates"""
        while True:
            try:
                update = await self.update_queue.get()
                
                async with self.update_locks[update.chain_id]:
                    # Validate update
                    if not self._validate_update(update):
                        continue
                        
                    # Apply update
                    await self._apply_update(update)
                    
                    # Update state hash
                    self._update_state_hash(update.chain_id)
                    
                self.update_queue.task_done()
                
            except Exception as e:
                logger.error(f"Error processing state update: {str(e)}")
                await asyncio.sleep(1)

    async def _update_chain_state(self, chain_id: int):
        """Update chain state from network"""
        try:
            chain_config = config.get_chain_config(chain_id)
            web3 = chain_config.get_web3()
            
            # Get current block
            block = await web3.eth.get_block('latest')
            
            # Update basic state
            self.states[chain_id].block_number = block.number
            self.states[chain_id].timestamp = block.timestamp
            self.states[chain_id].gas_price = await web3.eth.gas_price
            
            # Update protocol states
            await self._update_protocol_states(chain_id)
            
            # Update pending transactions
            await self._update_pending_transactions(chain_id)
            
            # Update timestamp
            self.states[chain_id].last_update = time.time()
            
            # Update state hash
            self._update_state_hash(chain_id)
            
        except Exception as e:
            logger.error(f"Error updating chain state: {str(e)}")
            raise

    async def _update_protocol_states(self, chain_id: int):
        """Update states for all protocols on chain"""
        try:
            chain_config = config.get_chain_config(chain_id)
            
            # Update DEX states
            for dex_name, dex_address in chain_config.dex_addresses.items():
                self.states[chain_id].protocol_states[dex_address] = \
                    await self._get_dex_state(dex_address, chain_id)
                    
            # Update lending protocol states
            for protocol_name, protocol_address in chain_config.lending_protocols.items():
                self.states[chain_id].protocol_states[protocol_address] = \
                    await self._get_lending_state(protocol_address, chain_id)
                    
            # Update flash loan provider states
            for provider_name, provider_address in chain_config.flash_loan_providers.items():
                self.states[chain_id].protocol_states[provider_address] = \
                    await self._get_flash_loan_state(provider_address, chain_id)
                    
        except Exception as e:
            logger.error(f"Error updating protocol states: {str(e)}")
            raise

    async def _update_pending_transactions(self, chain_id: int):
        """Update pending transactions list"""
        try:
            chain_config = config.get_chain_config(chain_id)
            web3 = chain_config.get_web3()
            
            # Get pending transactions
            pending = await web3.eth.get_pending_transactions()
            
            # Filter relevant transactions
            relevant_pending = [
                tx for tx in pending
                if self._is_relevant_transaction(tx, chain_id)
            ]
            
            self.states[chain_id].pending_transactions = relevant_pending
            
        except Exception as e:
            logger.error(f"Error updating pending transactions: {str(e)}")
            raise

    def _validate_update(self, update: StateUpdate) -> bool:
        """Validate state update"""
        try:
            current_state = self.states[update.chain_id]
            
            # Check block number
            if update.block_number < current_state.block_number:
                return False
                
            # Check timestamp
            if update.timestamp < current_state.timestamp:
                return False
                
            # Validate updates
            for address, state_update in update.updates.items():
                if not self._validate_protocol_state(address, state_update):
                    return False
                    
            return True
            
        except Exception as e:
            logger.error(f"Error validating update: {str(e)}")
            return False

    async def _apply_update(self, update: StateUpdate):
        """Apply state update"""
        try:
            state = self.states[update.chain_id]
            
            # Update block info
            if update.block_number > state.block_number:
                state.block_number = update.block_number
                state.timestamp = update.timestamp
                
            # Apply protocol state updates
            for address, state_update in update.updates.items():
                state.protocol_states[address] = {
                    **state.protocol_states.get(address, {}),
                    **state_update
                }
                
            state.last_update = time.time()
            
        except Exception as e:
            logger.error(f"Error applying update: {str(e)}")
            raise

    def _is_state_stale(self, chain_id: int) -> bool:
        """Check if chain state is stale"""
        try:
            state = self.states[chain_id]
            chain_config = config.get_chain_config(chain_id)
            
            # Check last update time
            if time.time() - state.last_update > chain_config.state_refresh_interval:
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Error checking state staleness: {str(e)}")
            return True

    async def _get_dex_state(self,
                            dex_address: str,
                            chain_id: int) -> Dict:
        """Get current state for DEX"""
        try:
            chain_config = config.get_chain_config(chain_id)
            dex = chain_config.get_dex_interface(dex_address)
            
            return {
                'liquidity': await dex.get_total_liquidity(),
                'pools': await dex.get_pool_states(),
                'fees': await dex.get_fee_info(),
                'last_update': int(time.time())
            }
            
        except Exception as e:
            logger.error(f"Error getting DEX state: {str(e)}")
            return {}

    async def _get_lending_state(self,
                               protocol_address: str,
                               chain_id: int) -> Dict:
        """Get current state for lending protocol"""
        try:
            chain_config = config.get_chain_config(chain_id)
            protocol = chain_config.get_lending_interface(protocol_address)
            
            return {
                'tvl': await protocol.get_total_value_locked(),
                'markets': await protocol.get_market_states(),
                'rates': await protocol.get_interest_rates(),
                'last_update': int(time.time())
            }
            
        except Exception as e:
            logger.error(f"Error getting lending state: {str(e)}")
            return {}

    async def _get_flash_loan_state(self,
                                  provider_address: str,
                                  chain_id: int) -> Dict:
        """Get current state for flash loan provider"""
        try:
            chain_config = config.get_chain_config(chain_id)
            provider = chain_config.get_flash_loan_interface(provider_address)
            
            return {
                'available_liquidity': await provider.get_available_liquidity(),
                'fee_rate': await provider.get_fee_rate(),
                'supported_tokens': await provider.get_supported_tokens(),
                'last_update': int(time.time())
            }
            
        except Exception as e:
            logger.error(f"Error getting flash loan state: {str(e)}")
            return {}

    def _validate_protocol_state(self,
                               address: str,
                               state: Dict) -> bool:
        """Validate protocol state update"""
        try:
            required_fields = ['last_update']
            
            # Check required fields
            if not all(field in state for field in required_fields):
                return False
                
            # Validate values
            if not isinstance(state['last_update'], int):
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error validating protocol state: {str(e)}")
            return False

    def _is_relevant_transaction(self,
                               transaction: Dict,
                               chain_id: int) -> bool:
        """Check if transaction is relevant for state tracking"""
        try:
            chain_config = config.get_chain_config(chain_id)
            
            # Get target address
            to_address = transaction.get('to', '').lower()
            
            # Check if target is tracked protocol
            return (
                to_address in chain_config.dex_addresses.values() or
                to_address in chain_config.lending_protocols.values() or
                to_address in chain_config.flash_loan_providers.values()
            )
            
        except Exception as e:
            logger.error(f"Error checking transaction relevance: {str(e)}")
            return False

    def _update_state_hash(self, chain_id: int):
        """Update state hash for chain"""
        try:
            state = self.states[chain_id]
            
            # Create hash input
            hash_input = f"{state.block_number}:{state.timestamp}:"
            
            # Add protocol states
            for address, protocol_state in sorted(state.protocol_states.items()):
                hash_input += f"{address}:{self._hash_dict(protocol_state)}:"
                
            # Update hash
            state.state_hash = self._calculate_hash(hash_input)
            
        except Exception as e:
            logger.error(f"Error updating state hash: {str(e)}")

    def _hash_dict(self, d: Dict) -> str:
        """Create deterministic hash of dictionary"""
        try:
            # Sort dictionary items
            items = sorted(d.items())
            
            # Create string representation
            return ':'.join(f"{k}={v}" for k, v in items)
            
        except Exception as e:
            logger.error(f"Error hashing dictionary: {str(e)}")
            return ""

    def _calculate_hash(self, input_string: str) -> str:
        """Calculate hash of input string"""
        try:
            import hashlib
            return hashlib.sha256(input_string.encode()).hexdigest()
        except Exception as e:
            logger.error(f"Error calculating hash: {str(e)}")
            return ""
