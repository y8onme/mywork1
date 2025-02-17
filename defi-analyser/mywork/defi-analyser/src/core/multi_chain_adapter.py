# src/core/multi_chain_adapter.py

import asyncio
from typing import Dict, List, Optional, Union, Any
from web3 import Web3, AsyncWeb3
from eth_typing import Address, HexStr
from dataclasses import dataclass
import aiohttp
from ..utils.config import config

@dataclass
class ChainConnection:
    web3: AsyncWeb3
    chain_id: int
    last_block: int
    pending_txs: Dict[str, Any]
    active_subscriptions: Dict[str, Any]
    fork_instances: Dict[str, Any]

@dataclass
class TransactionResult:
    success: bool
    tx_hash: Optional[str]
    gas_used: int
    block_number: int
    events: List[Dict]
    state_changes: List[Dict]
    error: Optional[str]

class MultiChainAdapter:
    def __init__(self):
        self.connections: Dict[int, ChainConnection] = {}
        self.active_forks: Dict[str, Dict] = {}
        self.session = aiohttp.ClientSession()
        
        # Initialize connections for all supported chains
        self._initialize_connections()

    def _initialize_connections(self):
        """Initialize connections for all supported chains"""
        for chain_id in config.get_all_chain_ids():
            chain_config = config.get_chain_config(chain_id)
            web3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(chain_config.rpc_url))
            
            self.connections[chain_id] = ChainConnection(
                web3=web3,
                chain_id=chain_id,
                last_block=0,
                pending_txs={},
                active_subscriptions={},
                fork_instances={}
            )

    async def get_contract_code(self, chain_id: int, address: str) -> str:
        """Get contract bytecode from chain"""
        try:
            connection = self._get_connection(chain_id)
            code = await connection.web3.eth.get_code(Web3.to_checksum_address(address))
            return code.hex()
        except Exception as e:
            print(f"Error getting contract code: {str(e)}")
            return ""

    async def get_protocol_states(self,
                                chain_id: int,
                                addresses: List[str]) -> Dict[str, Dict]:
        """Get current state of protocols"""
        states = {}
        connection = self._get_connection(chain_id)
        
        for address in addresses:
            try:
                # Get basic contract state
                balance = await connection.web3.eth.get_balance(
                    Web3.to_checksum_address(address)
                )
                
                # Get protocol-specific state
                protocol_state = await self._get_protocol_specific_state(
                    chain_id,
                    address
                )
                
                states[address] = {
                    'balance': balance,
                    'last_block': connection.last_block,
                    **protocol_state
                }
                
            except Exception as e:
                print(f"Error getting protocol state for {address}: {str(e)}")
                states[address] = {'error': str(e)}
        
        return states

    async def estimate_gas(self,
                          chain_id: int,
                          to_address: str,
                          data: Union[str, bytes],
                          value: int = 0) -> int:
        """Estimate gas for transaction"""
        try:
            connection = self._get_connection(chain_id)
            
            # Prepare transaction
            tx = {
                'to': Web3.to_checksum_address(to_address),
                'data': data if isinstance(data, bytes) else bytes.fromhex(data.replace('0x', '')),
                'value': value,
                'from': Web3.to_checksum_address('0x' + '0' * 40)  # Zero address for estimation
            }
            
            # Estimate gas
            gas_estimate = await connection.web3.eth.estimate_gas(tx)
            
            # Add buffer for safety
            return int(gas_estimate * 1.2)
            
        except Exception as e:
            print(f"Error estimating gas: {str(e)}")
            return 500000  # Default gas limit

    async def create_fork(self,
                         chain_id: int,
                         block_number: Optional[Union[int, str]] = 'latest') -> str:
        """Create a fork of the chain"""
        try:
            connection = self._get_connection(chain_id)
            
            # Generate unique fork ID
            fork_id = f"fork_{chain_id}_{block_number}_{len(connection.fork_instances)}"
            
            # Initialize fork
            fork_instance = await self._initialize_fork(
                chain_id,
                block_number
            )
            
            connection.fork_instances[fork_id] = fork_instance
            
            return fork_id
            
        except Exception as e:
            print(f"Error creating fork: {str(e)}")
            raise

    async def simulate_transaction(self,
                                 fork_id: str,
                                 to_address: str,
                                 data: Union[str, bytes],
                                 value: int = 0,
                                 gas_limit: Optional[int] = None) -> Dict:
        """Simulate transaction on forked chain"""
        try:
            fork_instance = self._get_fork_instance(fork_id)
            
            # Prepare transaction
            tx = {
                'to': Web3.to_checksum_address(to_address),
                'data': data if isinstance(data, bytes) else bytes.fromhex(data.replace('0x', '')),
                'value': value,
                'gas': gas_limit or 500000
            }
            
            # Simulate transaction
            result = await self._simulate_on_fork(
                fork_instance,
                tx
            )
            
            return {
                'success': result.success,
                'gas_used': result.gas_used,
                'state_changes': result.state_changes,
                'events': result.events,
                'error': result.error
            }
            
        except Exception as e:
            print(f"Error simulating transaction: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    async def send_transaction(self,
                             fork_id: str,
                             to_address: str,
                             data: Union[str, bytes],
                             value: int = 0,
                             gas_limit: Optional[int] = None,
                             priority_fee: Optional[int] = None) -> TransactionResult:
        """Send transaction on forked chain"""
        try:
            fork_instance = self._get_fork_instance(fork_id)
            
            # Prepare transaction
            tx = {
                'to': Web3.to_checksum_address(to_address),
                'data': data if isinstance(data, bytes) else bytes.fromhex(data.replace('0x', '')),
                'value': value,
                'gas': gas_limit or 500000
            }
            
            if priority_fee is not None:
                tx['maxPriorityFeePerGas'] = priority_fee
            
            # Send transaction
            result = await self._send_transaction_on_fork(
                fork_instance,
                tx
            )
            
            return result
            
        except Exception as e:
            print(f"Error sending transaction: {str(e)}")
            return TransactionResult(
                success=False,
                tx_hash=None,
                gas_used=0,
                block_number=0,
                events=[],
                state_changes=[],
                error=str(e)
            )

    async def delete_fork(self, fork_id: str):
        """Delete chain fork"""
        try:
            chain_id = int(fork_id.split('_')[1])
            connection = self._get_connection(chain_id)
            
            if fork_id in connection.fork_instances:
                await self._cleanup_fork(connection.fork_instances[fork_id])
                del connection.fork_instances[fork_id]
                
        except Exception as e:
            print(f"Error deleting fork: {str(e)}")

    async def get_token_price(self, chain_id: int, token_address: str) -> float:
        """Get token price from oracle or DEX"""
        try:
            connection = self._get_connection(chain_id)
            chain_config = config.get_chain_config(chain_id)
            
            # Try Chainlink oracle first
            price = await self._get_chainlink_price(
                connection,
                token_address,
                chain_config.oracle_addresses.get('chainlink')
            )
            
            if price > 0:
                return price
            
            # Fallback to DEX price
            return await self._get_dex_price(
                connection,
                token_address,
                chain_config
            )
            
        except Exception as e:
            print(f"Error getting token price: {str(e)}")
            return 0.0

    async def get_protocol_tvl(self, chain_id: int, protocol_address: str) -> float:
        """Get Total Value Locked in protocol"""
        try:
            connection = self._get_connection(chain_id)
            
            # Get protocol type
            protocol_type = self._determine_protocol_type(
                protocol_address,
                config.get_chain_config(chain_id)
            )
            
            # Get TVL based on protocol type
            if protocol_type == 'dex':
                return await self._get_dex_tvl(connection, protocol_address)
            elif protocol_type == 'lending':
                return await self._get_lending_tvl(connection, protocol_address)
            else:
                return await self._get_generic_tvl(connection, protocol_address)
                
        except Exception as e:
            print(f"Error getting protocol TVL: {str(e)}")
            return 0.0

    def _get_connection(self, chain_id: int) -> ChainConnection:
        """Get chain connection"""
        if chain_id not in self.connections:
            raise ValueError(f"Chain {chain_id} not supported")
        return self.connections[chain_id]

    async def _get_protocol_specific_state(self,
                                         chain_id: int,
                                         address: str) -> Dict:
        """Get protocol-specific state information"""
        # Implementation depends on protocol type
        return {}

    async def _initialize_fork(self,
                             chain_id: int,
                             block_number: Union[int, str]) -> Any:
        """Initialize fork instance"""
        # Implementation depends on forking mechanism
        return {}

    async def _simulate_on_fork(self,
                              fork_instance: Any,
                              transaction: Dict) -> TransactionResult:
        """Simulate transaction on fork"""
        # Implementation depends on forking mechanism
        return TransactionResult(
            success=True,
            tx_hash=None,
            gas_used=0,
            block_number=0,
            events=[],
            state_changes=[],
            error=None
        )

    async def _send_transaction_on_fork(self,
                                      fork_instance: Any,
                                      transaction: Dict) -> TransactionResult:
        """Send transaction on fork"""
        # Implementation depends on forking mechanism
        return TransactionResult(
            success=True,
            tx_hash="0x",
            gas_used=0,
            block_number=0,
            events=[],
            state_changes=[],
            error=None
        )

    def _get_fork_instance(self, fork_id: str) -> Any:
        """Get fork instance"""
        chain_id = int(fork_id.split('_')[1])
        connection = self._get_connection(chain_id)
        
        if fork_id not in connection.fork_instances:
            raise ValueError(f"Fork {fork_id} not found")
            
        return connection.fork_instances[fork_id]

    async def _cleanup_fork(self, fork_instance: Any):
        """Clean up fork instance"""
        # Implementation depends on forking mechanism
        pass

    async def _get_chainlink_price(self,
                                  connection: ChainConnection,
                                  token_address: str,
                                  oracle_address: Optional[str]) -> float:
        """Get price from Chainlink oracle"""
        # Implementation for Chainlink price fetching
        return 0.0

    async def _get_dex_price(self,
                            connection: ChainConnection,
                            token_address: str,
                            chain_config: Any) -> float:
        """Get price from DEX"""
        # Implementation for DEX price fetching
        return 0.0

    def _determine_protocol_type(self,
                               address: str,
                               chain_config: Any) -> str:
        """Determine protocol type from address"""
        # Implementation for protocol type determination
        return "unknown"

    async def _get_dex_tvl(self,
                          connection: ChainConnection,
                          protocol_address: str) -> float:
        """Get TVL for DEX protocol"""
        # Implementation for DEX TVL calculation
        return 0.0

    async def _get_lending_tvl(self,
                              connection: ChainConnection,
                              protocol_address: str) -> float:
        """Get TVL for lending protocol"""
        # Implementation for lending protocol TVL calculation
        return 0.0

    async def _get_generic_tvl(self,
                              connection: ChainConnection,
                              protocol_address: str) -> float:
        """Get TVL for generic protocol"""
        # Implementation for generic TVL calculation
        return 0.0

    async def close(self):
        """Close all connections and clean up resources"""
        for connection in self.connections.values():
            for fork_id in list(connection.fork_instances.keys()):
                await self.delete_fork(fork_id)
        
        await self.session.close()