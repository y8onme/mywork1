# src/utils/chain/chain_adapter.py

import asyncio
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
from web3 import Web3, AsyncWeb3
from eth_typing import Address, HexStr
from ..config import config
from ..logger import logger

@dataclass
class ChainConnection:
    chain_id: int
    web3: AsyncWeb3
    last_block: int
    active: bool
    connected_at: float
    last_error: Optional[str]

class ChainAdapter:
    def __init__(self):
        self.connections: Dict[int, ChainConnection] = {}
        self.fallback_providers: Dict[int, List[str]] = {}
        self.connection_retries: Dict[int, int] = {}
        self.max_retries = 3
        
        # Initialize connections
        self._initialize_connections()
        
    def _initialize_connections(self):
        """Initialize connections for all supported chains"""
        for chain_id in config.get_all_chain_ids():
            self._setup_chain_connection(chain_id)
            
    def _setup_chain_connection(self, chain_id: int):
        """Set up connection for specific chain"""
        try:
            chain_config = config.get_chain_config(chain_id)
            
            # Initialize Web3
            web3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(
                chain_config.rpc_url,
                request_kwargs={'timeout': 30}
            ))
            
            # Store connection
            self.connections[chain_id] = ChainConnection(
                chain_id=chain_id,
                web3=web3,
                last_block=0,
                active=True,
                connected_at=asyncio.get_event_loop().time(),
                last_error=None
            )
            
            # Store fallback providers
            self.fallback_providers[chain_id] = chain_config.fallback_rpcs
            
        except Exception as e:
            logger.error(f"Error setting up chain {chain_id}: {str(e)}")
            raise

    async def get_web3(self, chain_id: int) -> AsyncWeb3:
        """Get Web3 instance for chain"""
        try:
            connection = self.connections.get(chain_id)
            if not connection:
                raise ValueError(f"Chain {chain_id} not supported")
                
            if not connection.active:
                await self._reconnect_chain(chain_id)
                
            return connection.web3
            
        except Exception as e:
            logger.error(f"Error getting Web3 for chain {chain_id}: {str(e)}")
            raise

    async def send_transaction(self,
                             chain_id: int,
                             transaction: Dict) -> Dict:
        """Send transaction to chain"""
        try:
            web3 = await self.get_web3(chain_id)
            
            # Sign and send transaction
            signed_tx = await web3.eth.sign_transaction(transaction)
            tx_hash = await web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            # Wait for receipt
            receipt = await web3.eth.wait_for_transaction_receipt(
                tx_hash,
                timeout=60
            )
            
            return {
                'success': receipt.status == 1,
                'tx_hash': tx_hash.hex(),
                'receipt': receipt
            }
            
        except Exception as e:
            logger.error(f"Error sending transaction on chain {chain_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    async def get_contract(self,
                          chain_id: int,
                          address: str,
                          abi: List) -> Optional[Any]:
        """Get contract instance"""
        try:
            web3 = await self.get_web3(chain_id)
            return web3.eth.contract(
                address=Web3.to_checksum_address(address),
                abi=abi
            )
        except Exception as e:
            logger.error(f"Error getting contract on chain {chain_id}: {str(e)}")
            return None

    async def estimate_gas(self,
                          chain_id: int,
                          transaction: Dict) -> Optional[int]:
        """Estimate gas for transaction"""
        try:
            web3 = await self.get_web3(chain_id)
            return await web3.eth.estimate_gas(transaction)
        except Exception as e:
            logger.error(f"Error estimating gas on chain {chain_id}: {str(e)}")
            return None

    async def get_balance(self,
                         chain_id: int,
                         address: str) -> Optional[int]:
        """Get account balance"""
        try:
            web3 = await self.get_web3(chain_id)
            return await web3.eth.get_balance(
                Web3.to_checksum_address(address)
            )
        except Exception as e:
            logger.error(f"Error getting balance on chain {chain_id}: {str(e)}")
            return None

    async def _reconnect_chain(self, chain_id: int) -> bool:
        """Attempt to reconnect to chain"""
        try:
            retries = self.connection_retries.get(chain_id, 0)
            
            if retries >= self.max_retries:
                logger.error(f"Max reconnection attempts reached for chain {chain_id}")
                return False
                
            # Try fallback providers
            for rpc_url in self.fallback_providers[chain_id]:
                try:
                    web3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(
                        rpc_url,
                        request_kwargs={'timeout': 30}
                    ))
                    
                    # Test connection
                    await web3.eth.chain_id
                    
                    # Update connection
                    self.connections[chain_id].web3 = web3
                    self.connections[chain_id].active = True
                    self.connections[chain_id].last_error = None
                    self.connections[chain_id].connected_at = \
                        asyncio.get_event_loop().time()
                        
                    return True
                    
                except Exception as e:
                    logger.error(f"Error with fallback RPC: {str(e)}")
                    continue
                    
            # Update retry count
            self.connection_retries[chain_id] = retries + 1
            
            return False
            
        except Exception as e:
            logger.error(f"Error reconnecting to chain {chain_id}: {str(e)}")
            return False

    async def monitor_connections(self):
        """Monitor chain connections"""
        while True:
            try:
                for chain_id, connection in self.connections.items():
                    if not connection.active:
                        continue
                        
                    try:
                        # Test connection
                        web3 = connection.web3
                        await web3.eth.chain_id
                        
                        # Update last block
                        connection.last_block = await web3.eth.block_number
                        
                    except Exception as e:
                        logger.error(f"Connection error for chain {chain_id}: {str(e)}")
                        
                        # Mark as inactive
                        connection.active = False
                        connection.last_error = str(e)
                        
                        # Attempt reconnection
                        await self._reconnect_chain(chain_id)
                        
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error monitoring connections: {str(e)}")
                await asyncio.sleep(60)

    async def close(self):
        """Close all connections"""
        try:
            for connection in self.connections.values():
                if hasattr(connection.web3.provider, 'close'):
                    await connection.web3.provider.close()
        except Exception as e:
            logger.error(f"Error closing connections: {str(e)}")
