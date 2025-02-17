from typing import Dict, List, Optional, Tuple
from eth_utils import to_hex, to_checksum_address
from eth_abi import decode_abi
import logging

logger = logging.getLogger(__name__)

class ProxyAnalyzer:
    """Analyzer for proxy contract patterns and implementations"""

    # Standard proxy patterns
    PROXY_PATTERNS = {
        'EIP1967': {
            'implementation_slot': '0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc',
            'admin_slot': '0xb53127684a568b3173ae13b9f8a6016e243e63b6e8ee1178d6a717850b5d6103',
            'beacon_slot': '0xa3f0ad74e5423aebfd80d3ef4346578335a9a72aeaee59ff6cb3582b35133d50'
        },
        'Transparent': {
            'implementation_slot': '0x7050c9e0f4ca769c69bd3a8ef740bc37934f8e2c036e5a723fd8ee048ed3f8c3'
        },
        'UUPS': {
            'implementation_slot': '0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc'
        },
        'Beacon': {
            'beacon_slot': '0xa3f0ad74e5423aebfd80d3ef4346578335a9a72aeaee59ff6cb3582b35133d50'
        }
    }

    def __init__(self, web3_client):
        self.web3 = web3_client
        
    async def analyze_proxy(self, contract_address: str) -> Dict:
        """Analyze proxy contract and return implementation details"""
        try:
            contract_address = to_checksum_address(contract_address)
            
            # Get contract code
            code = await self.web3.eth.get_code(contract_address)
            if code == '0x':
                return {'error': 'Contract not found'}

            # Detect proxy pattern
            proxy_type = await self._detect_proxy_pattern(contract_address, code)
            if not proxy_type:
                return {'error': 'Not a proxy contract'}

            # Get implementation
            impl_address = await self._get_implementation_address(contract_address, proxy_type)
            
            # Get admin if applicable
            admin = await self._get_admin_address(contract_address, proxy_type)
            
            # Get beacon if applicable
            beacon = await self._get_beacon_address(contract_address, proxy_type)
            
            # Get upgrade history
            upgrades = await self._get_upgrade_history(contract_address)
            
            # Map storage layout
            storage_layout = await self._map_storage_layout(contract_address, impl_address)
            
            return {
                'proxy_type': proxy_type,
                'implementation': impl_address,
                'admin': admin,
                'beacon': beacon,
                'upgrades': upgrades,
                'storage_layout': storage_layout
            }
            
        except Exception as e:
            logger.error(f"Error analyzing proxy {contract_address}: {str(e)}")
            return {'error': str(e)}

    async def _detect_proxy_pattern(self, address: str, code: bytes) -> Optional[str]:
        """Detect which proxy pattern the contract implements"""
        # Check storage slots for different patterns
        for pattern, slots in self.PROXY_PATTERNS.items():
            impl_slot = slots.get('implementation_slot')
            if impl_slot:
                value = await self.web3.eth.get_storage_at(address, impl_slot)
                if value != '0x' + '0'*64:
                    return pattern
                    
        # Check bytecode patterns
        if b'delegatecall' in code:
            return 'Custom Proxy'
            
        return None

    async def _get_implementation_address(self, proxy: str, proxy_type: str) -> Optional[str]:
        """Get implementation contract address"""
        try:
            slot = self.PROXY_PATTERNS[proxy_type]['implementation_slot']
            value = await self.web3.eth.get_storage_at(proxy, slot)
            return to_checksum_address(to_hex(value)[-40:])
        except:
            return None

    async def _get_admin_address(self, proxy: str, proxy_type: str) -> Optional[str]:
        """Get proxy admin address if applicable"""
        try:
            if 'admin_slot' in self.PROXY_PATTERNS[proxy_type]:
                slot = self.PROXY_PATTERNS[proxy_type]['admin_slot']
                value = await self.web3.eth.get_storage_at(proxy, slot)
                return to_checksum_address(to_hex(value)[-40:])
        except:
            return None
            
        return None

    async def _get_beacon_address(self, proxy: str, proxy_type: str) -> Optional[str]:
        """Get beacon address if applicable"""
        try:
            if 'beacon_slot' in self.PROXY_PATTERNS[proxy_type]:
                slot = self.PROXY_PATTERNS[proxy_type]['beacon_slot']
                value = await self.web3.eth.get_storage_at(proxy, slot)
                return to_checksum_address(to_hex(value)[-40:])
        except:
            return None
            
        return None

    async def _get_upgrade_history(self, proxy: str) -> List[Dict]:
        """Get history of implementation upgrades"""
        try:
            # Get upgrade events
            upgrade_events = await self._get_upgrade_events(proxy)
            
            # Get implementation changes from storage
            storage_changes = await self._get_implementation_changes(proxy)
            
            return sorted(upgrade_events + storage_changes, key=lambda x: x['block_number'])
            
        except Exception as e:
            logger.error(f"Error getting upgrade history: {str(e)}")
            return []

    async def _map_storage_layout(self, proxy: str, implementation: str) -> Dict:
        """Map storage layout of proxy and implementation"""
        try:
            layout = {
                'proxy_slots': {},
                'implementation_slots': {}
            }
            
            # Map known proxy slots
            for pattern, slots in self.PROXY_PATTERNS.items():
                for name, slot in slots.items():
                    value = await self.web3.eth.get_storage_at(proxy, slot)
                    layout['proxy_slots'][name] = {
                        'slot': slot,
                        'value': to_hex(value)
                    }
                    
            # Try to map implementation storage
            impl_layout = await self._analyze_implementation_storage(implementation)
            layout['implementation_slots'] = impl_layout
            
            return layout
            
        except Exception as e:
            logger.error(f"Error mapping storage layout: {str(e)}")
            return {} 