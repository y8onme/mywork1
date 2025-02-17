from .proxy_analyzer import ProxyAnalyzer
from .unverified_contract_analyzer import UnverifiedContractAnalyzer
from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)

class AdvancedProxyAnalyzer:
    """Enhanced proxy analyzer that can handle unverified implementations"""

    def __init__(self, web3_client):
        self.web3 = web3_client
        self.proxy_analyzer = ProxyAnalyzer(web3_client)
        self.unverified_analyzer = UnverifiedContractAnalyzer(web3_client)
        
    async def analyze_proxy_system(self, proxy_address: str) -> Dict:
        """Analyze entire proxy system including unverified implementations"""
        try:
            # First analyze proxy
            proxy_analysis = await self.proxy_analyzer.analyze_proxy(proxy_address)
            
            if not proxy_analysis.get('implementation'):
                return {'error': 'No implementation found'}

            # Analyze implementation
            impl_address = proxy_analysis['implementation']
            impl_code = await self.web3.eth.get_code(impl_address)
            
            # Check if implementation has verified source code
            impl_analysis = await self._analyze_implementation(impl_address, impl_code)
            
            # Combine analyses
            return {
                'proxy': proxy_analysis,
                'implementation': impl_analysis,
                'security_analysis': await self._analyze_proxy_security(
                    proxy_analysis,
                    impl_analysis
                ),
                'upgrade_history': await self._get_upgrade_history(proxy_address),
                'storage_analysis': await self._analyze_combined_storage(
                    proxy_address,
                    impl_address
                )
            }
            
        except Exception as e:
            logger.error(f"Error in advanced proxy analysis: {str(e)}")
            return {'error': str(e)}

    async def _analyze_implementation(self, address: str, code: bytes) -> Dict:
        """Analyze implementation contract"""
        # Try to get verified source code first
        source_code = await self._get_verified_source(address)
        
        if source_code:
            return await self._analyze_verified_implementation(address, source_code)
        else:
            # Use Octopus to analyze unverified implementation
            return await self.unverified_analyzer.analyze_unverified_contract(address)

    async def _analyze_proxy_security(self, proxy_analysis: Dict, impl_analysis: Dict) -> Dict:
        """Analyze security of proxy system"""
        return {
            'storage_collisions': self._check_storage_collisions(
                proxy_analysis,
                impl_analysis
            ),
            'initialization_risks': self._check_initialization_risks(
                proxy_analysis,
                impl_analysis
            ),
            'upgrade_risks': self._check_upgrade_risks(
                proxy_analysis,
                impl_analysis
            ),
            'access_control': self._check_access_control(
                proxy_analysis,
                impl_analysis
            ),
            'function_clashing': self._check_function_clashing(
                proxy_analysis,
                impl_analysis
            )
        } 

    async def _get_verified_source(self, address: str) -> Optional[str]:
        """Try to get verified source code from multiple sources"""
        try:
            # Try Etherscan first
            if hasattr(self, 'etherscan_api_key'):
                source = await self._get_etherscan_source(address)
                if source:
                    return source

            # Try Sourcify
            source = await self._get_sourcify_source(address)
            if source:
                return source

            # Try other sources (BlockScout, etc.)
            return None

        except Exception as e:
            logger.error(f"Error getting verified source: {str(e)}")
            return None

    async def _analyze_verified_implementation(self, address: str, source_code: str) -> Dict:
        """Analyze verified implementation contract"""
        try:
            # Use Slither for static analysis
            slither_analysis = await self._run_slither_analysis(source_code)
            
            # Use Mythril for symbolic execution
            mythril_analysis = await self._run_mythril_analysis(address)
            
            return {
                'source_code': source_code,
                'static_analysis': slither_analysis,
                'symbolic_analysis': mythril_analysis,
                'verified': True
            }
            
        except Exception as e:
            logger.error(f"Error analyzing verified implementation: {str(e)}")
            return {'error': str(e)}

    def _check_storage_collisions(self, proxy: Dict, impl: Dict) -> Dict:
        """Check for storage slot collisions between proxy and implementation"""
        collisions = {
            'direct_collisions': [],
            'potential_collisions': [],
            'risk_level': 'LOW'
        }

        proxy_slots = self._get_proxy_storage_slots(proxy)
        impl_slots = self._get_implementation_storage_slots(impl)

        # Check for direct collisions
        for slot in proxy_slots:
            if slot in impl_slots:
                collisions['direct_collisions'].append({
                    'slot': slot,
                    'proxy_usage': proxy_slots[slot],
                    'impl_usage': impl_slots[slot]
                })

        # Check for potential collisions (e.g., dynamic arrays, mappings)
        potential = self._check_potential_collisions(proxy_slots, impl_slots)
        collisions['potential_collisions'] = potential

        # Assess risk level
        if collisions['direct_collisions']:
            collisions['risk_level'] = 'HIGH'
        elif collisions['potential_collisions']:
            collisions['risk_level'] = 'MEDIUM'

        return collisions

    def _check_initialization_risks(self, proxy: Dict, impl: Dict) -> Dict:
        """Check for initialization-related vulnerabilities"""
        risks = {
            'uninitialized_implementation': False,
            'multiple_initialization': False,
            'missing_initializer': False,
            'insecure_initialization': False,
            'details': []
        }

        # Check for initializer function
        initializer = self._find_initializer(impl)
        if not initializer:
            risks['missing_initializer'] = True
            risks['details'].append('No initializer function found')

        # Check initialization state
        if not self._is_initialized(proxy):
            risks['uninitialized_implementation'] = True
            risks['details'].append('Implementation not initialized')

        # Check for multiple initialization possibility
        if self._can_reinitialize(impl):
            risks['multiple_initialization'] = True
            risks['details'].append('Implementation can be reinitialized')

        # Check initialization security
        if initializer and not self._is_secure_initializer(initializer):
            risks['insecure_initialization'] = True
            risks['details'].append('Insecure initializer implementation')

        return risks

    def _check_upgrade_risks(self, proxy: Dict, impl: Dict) -> Dict:
        """Analyze upgrade-related security risks"""
        return {
            'unauthorized_upgrade': self._check_unauthorized_upgrade(proxy, impl),
            'function_shadowing': self._check_function_shadowing(proxy, impl),
            'storage_gaps': self._check_storage_gaps(impl),
            'upgrade_safety': self._check_upgrade_safety(proxy, impl),
            'beacon_risks': self._check_beacon_risks(proxy) if proxy.get('beacon') else None
        }

    def _check_access_control(self, proxy: Dict, impl: Dict) -> Dict:
        """Analyze access control mechanisms"""
        return {
            'admin_access': self._analyze_admin_access(proxy),
            'ownership_pattern': self._detect_ownership_pattern(impl),
            'role_based_access': self._analyze_role_based_access(impl),
            'missing_access_control': self._find_missing_access_control(impl),
            'privileged_functions': self._identify_privileged_functions(impl)
        }

    def _check_function_clashing(self, proxy: Dict, impl: Dict) -> Dict:
        """Check for function selector clashing"""
        clashes = {
            'direct_clashes': [],
            'shadow_clashes': [],
            'risk_level': 'LOW'
        }

        proxy_selectors = self._get_function_selectors(proxy)
        impl_selectors = self._get_function_selectors(impl)

        # Check for direct selector clashes
        for selector in proxy_selectors:
            if selector in impl_selectors:
                clashes['direct_clashes'].append({
                    'selector': selector,
                    'proxy_function': proxy_selectors[selector],
                    'impl_function': impl_selectors[selector]
                })

        # Check for shadow clashes (similar functions with different selectors)
        shadows = self._find_shadow_clashes(proxy_selectors, impl_selectors)
        clashes['shadow_clashes'] = shadows

        # Assess risk level
        if clashes['direct_clashes']:
            clashes['risk_level'] = 'CRITICAL'
        elif clashes['shadow_clashes']:
            clashes['risk_level'] = 'MEDIUM'

        return clashes

    async def _analyze_combined_storage(self, proxy_address: str, impl_address: str) -> Dict:
        """Analyze combined storage layout of proxy and implementation"""
        try:
            proxy_storage = await self._get_storage_layout(proxy_address)
            impl_storage = await self._get_storage_layout(impl_address)

            return {
                'proxy_storage': proxy_storage,
                'implementation_storage': impl_storage,
                'combined_layout': self._merge_storage_layouts(proxy_storage, impl_storage),
                'storage_safety': self._analyze_storage_safety(proxy_storage, impl_storage)
            }

        except Exception as e:
            logger.error(f"Error analyzing combined storage: {str(e)}")
            return {'error': str(e)}

    async def _get_upgrade_history(self, proxy_address: str) -> List[Dict]:
        """Get history of implementation upgrades"""
        try:
            # Get historical events
            upgrade_events = await self._get_upgrade_events(proxy_address)
            
            # Analyze each upgrade
            history = []
            for event in upgrade_events:
                upgrade_info = {
                    'block_number': event['blockNumber'],
                    'timestamp': event['timestamp'],
                    'old_implementation': event['oldImplementation'],
                    'new_implementation': event['newImplementation'],
                    'upgrader': event['upgrader'],
                    'analysis': await self._analyze_upgrade_transaction(event)
                }
                history.append(upgrade_info)

            return history

        except Exception as e:
            logger.error(f"Error getting upgrade history: {str(e)}")
            return [] 

    def _analyze_role_based_access(self, impl: Dict) -> Dict:
        """Analyze role-based access control (RBAC) in the implementation"""
        rbac_analysis = {
            'has_rbac': False,
            'roles': [],
            'role_admins': {},
            'role_members': {},
            'critical_functions': [],
            'risk_level': 'LOW'
        }

        # Check for AccessControl or similar patterns
        if self._has_role_management(impl):
            rbac_analysis['has_rbac'] = True
            
            # Extract roles
            roles = self._extract_roles(impl)
            rbac_analysis['roles'] = roles
            
            # Get role administrators
            for role in roles:
                admins = self._get_role_admins(impl, role)
                rbac_analysis['role_admins'][role] = admins
                
                members = self._get_role_members(impl, role)
                rbac_analysis['role_members'][role] = members

            # Analyze critical functions
            critical_funcs = self._get_critical_functions(impl)
            rbac_analysis['critical_functions'] = [
                {
                    'function': func,
                    'required_role': self._get_required_role(impl, func)
                }
                for func in critical_funcs
            ]

            # Assess risk level
            rbac_analysis['risk_level'] = self._assess_rbac_risk(
                rbac_analysis['role_admins'],
                rbac_analysis['critical_functions']
            )

        return rbac_analysis

    def _has_role_management(self, impl: Dict) -> bool:
        """Check if contract implements role management"""
        role_functions = {
            'grantRole',
            'revokeRole',
            'renounceRole',
            'hasRole',
            'getRoleMember',
            'getRoleMemberCount'
        }
        
        return any(
            func in impl.get('functions', {})
            for func in role_functions
        )

    def _extract_roles(self, impl: Dict) -> List[str]:
        """Extract defined roles from implementation"""
        roles = set()
        
        # Check storage for role hashes
        for slot, info in impl.get('storage_layout', {}).get('slots', {}).items():
            if self._is_role_slot(slot, info):
                role_name = self._decode_role_name(slot)
                if role_name:
                    roles.add(role_name)

        # Check events for role-related events
        for event in impl.get('events', []):
            if 'Role' in event.get('name', ''):
                role_param = self._extract_role_from_event(event)
                if role_param:
                    roles.add(role_param)

        return list(roles)

    def _get_role_admins(self, impl: Dict, role: str) -> List[str]:
        """Get administrators for a specific role"""
        admins = set()
        
        # Check getRoleAdmin function
        admin_role = self._call_role_admin(impl, role)
        if admin_role:
            admins.add(admin_role)

        # Check role admin mapping
        admin_slot = self._get_role_admin_slot(role)
        admin_addresses = self._get_slot_addresses(impl, admin_slot)
        admins.update(admin_addresses)

        return list(admins)

    def _get_role_members(self, impl: Dict, role: str) -> List[str]:
        """Get members assigned to a specific role"""
        members = set()
        
        # Get role member count
        member_count = self._get_role_member_count(impl, role)
        
        # Get members
        for i in range(member_count):
            member = self._get_role_member(impl, role, i)
            if member:
                members.add(member)

        return list(members)

    def _get_critical_functions(self, impl: Dict) -> List[Dict]:
        """Identify critical functions that require role access"""
        critical_functions = []
        
        for name, func in impl.get('functions', {}).items():
            if self._is_critical_function(func):
                critical_functions.append({
                    'name': name,
                    'signature': func.get('signature'),
                    'modifiers': func.get('modifiers', []),
                    'access_level': self._get_function_access_level(func)
                })

        return critical_functions

    def _assess_rbac_risk(self, role_admins: Dict, critical_functions: List) -> str:
        """Assess the risk level of the RBAC implementation"""
        risk_level = 'LOW'
        
        # Check for single admin controlling multiple roles
        admin_role_count = {}
        for role, admins in role_admins.items():
            for admin in admins:
                admin_role_count[admin] = admin_role_count.get(admin, 0) + 1
                
        if any(count > 2 for count in admin_role_count.values()):
            risk_level = 'MEDIUM'

        # Check critical functions
        for func in critical_functions:
            if not func.get('access_level'):
                risk_level = 'HIGH'
                break
            if func.get('access_level') == 'DEFAULT_ADMIN_ROLE':
                risk_level = max(risk_level, 'MEDIUM')

        return risk_level 