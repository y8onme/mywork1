# src/core/analyzers/governance_analyzer.py

import asyncio
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from ...utils.config import config
from ...utils.logger import logger
from ...utils.state.state_manager import StateManager
from ..multi_stage_executor import MultiStageExecutor
from ..vulnerability_scanner import VulnerabilityScanner
from eth_utils import to_hex, to_checksum_address
from .bytecode_analyzer import BytecodeAnalyzer

@dataclass
class GovernanceVulnerability:
    protocol_address: str
    governance_type: str  # DAO, TimeLock, Admin, etc.
    vulnerability_type: str
    attack_vector: str
    required_voting_power: float
    flash_loan_potential: bool
    estimated_cost: float
    time_constraints: Dict[str, int]
    affected_functions: List[str]
    risk_score: float
    confidence_score: float

@dataclass
class GovernanceAnalysis:
    vulnerabilities: List[GovernanceVulnerability]
    governance_structure: Dict
    voting_mechanisms: Dict
    time_locks: Dict
    admin_controls: Dict
    proposal_history: List[Dict]
    flash_loan_analysis: Dict
    risk_assessment: Dict
    timestamp: float

class GovernanceAnalyzer:
    """Analyzer for DAO and governance contracts"""

    GOVERNANCE_SIGNATURES = {
        # OpenZeppelin Governor
        '0x56781388': 'execute(uint256)',
        '0x7d5e81e2': 'propose(address[],uint256[],string[],bytes[],string)',
        '0xc01f9e37': 'castVote(uint256,uint8)',
        '0x3bccf4fd': 'propose(address[],uint256[],bytes[],string)',
        # Compound Governor
        '0x15373e3d': 'cancel(uint256)',
        '0x9a802a6d': 'queue(uint256)',
        '0x8a977cac': 'state(uint256)',
        # Snapshot
        '0x3ec796ba': 'submitVote(bytes32,uint8,uint8,uint8,bytes32,bytes32)',
        # Aave Governance
        '0x160217b4': 'submitVote(uint256,bool)',
        '0xf8567cab': 'setVotingDelay(uint256)',
    }

    def __init__(self, web3_client):
        self.web3 = web3_client
        self.bytecode_analyzer = BytecodeAnalyzer(web3_client)
        self.state_manager = StateManager()
        self.executor = MultiStageExecutor()
        self.vulnerability_scanner = VulnerabilityScanner()
        self.analyzed_protocols: Set[str] = set()
        self.flash_loan_providers: Dict = {}
        self.voting_power_thresholds = {
            'critical': 0.51,
            'significant': 0.33,
            'minor': 0.10
        }
        
    async def analyze_governance(self, contract_address: str) -> Dict:
        """Analyze governance contract for security and functionality"""
        try:
            contract_address = self.web3.to_checksum_address(contract_address)
            
            # Get basic contract analysis
            bytecode_analysis = await self.bytecode_analyzer.analyze_bytecode(
                contract_address, 
                deep_analysis=True
            )

            # Identify governance type
            gov_type = self._identify_governance_type(bytecode_analysis)

            # Get governance parameters
            params = await self._get_governance_parameters(contract_address, gov_type)

            # Analyze voting power
            voting_analysis = await self._analyze_voting_power(contract_address)

            # Analyze proposal mechanism
            proposal_analysis = await self._analyze_proposal_mechanism(
                contract_address,
                gov_type
            )

            # Analyze timelock
            timelock_analysis = await self._analyze_timelock(contract_address)

            # Analyze quorum and thresholds
            threshold_analysis = await self._analyze_thresholds(contract_address)

            # Check for vulnerabilities
            security_analysis = await self._analyze_governance_security(
                contract_address,
                bytecode_analysis
            )

            return {
                'governance_type': gov_type,
                'parameters': params,
                'voting_analysis': voting_analysis,
                'proposal_analysis': proposal_analysis,
                'timelock_analysis': timelock_analysis,
                'threshold_analysis': threshold_analysis,
                'security_analysis': security_analysis,
                'risk_assessment': self._assess_governance_risks(
                    voting_analysis,
                    proposal_analysis,
                    security_analysis
                )
            }

        except Exception as e:
            logger.error(f"Error in governance analysis: {str(e)}")
            return {'error': str(e)}

    def _identify_governance_type(self, analysis: Dict) -> str:
        """Identify the type of governance implementation"""
        functions = analysis.get('functions', {})
        
        # Check OpenZeppelin Governor
        if all(sig in functions for sig in ['propose', 'execute', 'castVote']):
            return 'OpenZeppelin'
            
        # Check Compound Governor
        if all(sig in functions for sig in ['propose', 'queue', 'execute']):
            return 'Compound'
            
        # Check Snapshot
        if 'submitVote' in functions and 'space' in analysis.get('storage', {}):
            return 'Snapshot'
            
        # Check Aave Governance
        if 'submitVote' in functions and 'VOTING_DURATION' in analysis.get('storage', {}):
            return 'Aave'
            
        return 'Unknown'

    async def _get_governance_parameters(self, address: str, gov_type: str) -> Dict:
        """Get governance configuration parameters"""
        params = {
            'voting_delay': 0,
            'voting_period': 0,
            'proposal_threshold': 0,
            'quorum': 0,
            'timelock_delay': 0
        }

        try:
            # Get parameters based on governance type
            if gov_type == 'OpenZeppelin':
                params.update(await self._get_oz_parameters(address))
            elif gov_type == 'Compound':
                params.update(await self._get_compound_parameters(address))
            elif gov_type == 'Aave':
                params.update(await self._get_aave_parameters(address))

            return params

        except Exception as e:
            logger.error(f"Error getting governance parameters: {str(e)}")
            return params

    async def _analyze_voting_power(self, address: str) -> Dict:
        """Analyze voting power distribution and delegation"""
        try:
            # Get token address
            token_address = await self._get_governance_token(address)
            
            # Analyze token distribution
            distribution = await self._analyze_token_distribution(token_address)
            
            # Analyze delegation patterns
            delegation = await self._analyze_delegation_patterns(token_address)
            
            # Check for voting power concentration
            concentration = self._calculate_voting_power_concentration(distribution)
            
            return {
                'distribution': distribution,
                'delegation_patterns': delegation,
                'concentration': concentration,
                'risks': self._assess_voting_power_risks(
                    distribution,
                    delegation,
                    concentration
                )
            }

        except Exception as e:
            logger.error(f"Error analyzing voting power: {str(e)}")
            return {}

    async def _analyze_proposal_mechanism(self, address: str, gov_type: str) -> Dict:
        """Analyze proposal creation and execution mechanism"""
        try:
            # Get historical proposals
            proposals = await self._get_historical_proposals(address)
            
            # Analyze proposal patterns
            patterns = self._analyze_proposal_patterns(proposals)
            
            # Check execution paths
            execution_analysis = await self._analyze_execution_paths(
                address,
                gov_type
            )
            
            return {
                'historical_analysis': patterns,
                'execution_paths': execution_analysis,
                'risks': self._assess_proposal_risks(patterns, execution_analysis)
            }

        except Exception as e:
            logger.error(f"Error analyzing proposal mechanism: {str(e)}")
            return {}

    async def _analyze_timelock(self, address: str) -> Dict:
        """Analyze timelock configuration and usage"""
        try:
            # Get timelock address
            timelock_address = await self._get_timelock_address(address)
            
            if not timelock_address:
                return {'has_timelock': False}
                
            # Analyze timelock configuration
            config = await self._get_timelock_config(timelock_address)
            
            # Analyze historical usage
            history = await self._analyze_timelock_history(timelock_address)
            
            return {
                'has_timelock': True,
                'address': timelock_address,
                'configuration': config,
                'historical_usage': history,
                'risks': self._assess_timelock_risks(config, history)
            }

        except Exception as e:
            logger.error(f"Error analyzing timelock: {str(e)}")
            return {'has_timelock': False}

    async def _analyze_thresholds(self, address: str) -> Dict:
        """Analyze quorum and threshold requirements"""
        try:
            # Get current thresholds
            thresholds = await self._get_current_thresholds(address)
            
            # Get historical changes
            threshold_history = await self._get_threshold_history(address)
            
            # Analyze voting patterns
            voting_patterns = await self._analyze_voting_patterns(address)
            
            return {
                'current_thresholds': thresholds,
                'historical_changes': threshold_history,
                'voting_patterns': voting_patterns,
                'recommendations': self._generate_threshold_recommendations(
                    thresholds,
                    voting_patterns
                )
            }

        except Exception as e:
            logger.error(f"Error analyzing thresholds: {str(e)}")
            return {}

    async def _analyze_governance_security(self, address: str, bytecode_analysis: Dict) -> Dict:
        """Analyze governance-specific security concerns"""
        security_analysis = {
            'vulnerabilities': [],
            'warnings': [],
            'recommendations': []
        }

        # Check for common governance vulnerabilities
        checks = [
            self._check_vote_delegation_security,
            self._check_proposal_creation_security,
            self._check_execution_security,
            self._check_timelock_security,
            self._check_upgrade_security
        ]

        for check in checks:
            result = await check(address, bytecode_analysis)
            if result.get('vulnerable'):
                security_analysis['vulnerabilities'].append(result)
            elif result.get('warning'):
                security_analysis['warnings'].append(result)

        # Generate recommendations
        security_analysis['recommendations'] = self._generate_security_recommendations(
            security_analysis['vulnerabilities'],
            security_analysis['warnings']
        )

        return security_analysis

    async def _analyze_governance_structure(self,
                                         protocol_address: str,
                                         chain_id: int) -> Dict:
        """Analyze the governance structure of the protocol"""
        try:
            structure = {
                'type': None,
                'controllers': [],
                'voting_token': None,
                'quorum': 0,
                'proposal_threshold': 0,
                'execution_delay': 0,
                'guardian': None
            }
            
            # Check for common governance patterns
            if await self._is_compound_governance(protocol_address):
                structure['type'] = 'compound'
                # Add Compound-specific analysis
            elif await self._is_openzeppelin_governance(protocol_address):
                structure['type'] = 'openzeppelin'
                # Add OpenZeppelin-specific analysis
            elif await self._is_snapshot_governance(protocol_address):
                structure['type'] = 'snapshot'
                # Add Snapshot-specific analysis
            
            # Get governance parameters
            structure.update(await self._get_governance_params(protocol_address))
            
            return structure
            
        except Exception as e:
            logger.error(f"Error analyzing governance structure: {str(e)}")
            return {}

    async def _analyze_voting_mechanisms(self,
                                      protocol_address: str,
                                      governance_structure: Dict) -> Dict:
        """Analyze voting mechanisms and potential vulnerabilities"""
        try:
            mechanisms = {
                'token_based': False,
                'delegation_enabled': False,
                'voting_delay': 0,
                'voting_period': 0,
                'vote_differential': 0,
                'vote_counting': None,
                'vulnerabilities': []
            }
            
            # Check voting token
            if governance_structure.get('voting_token'):
                mechanisms['token_based'] = True
                
                # Check for flash loan vulnerability
                if await self._is_flash_loan_vulnerable(
                    governance_structure['voting_token']
                ):
                    mechanisms['vulnerabilities'].append({
                        'type': 'flash_loan_voting',
                        'severity': 'high',
                        'description': 'Voting power can be manipulated via flash loans'
                    })
            
            # Check delegation
            if await self._supports_delegation(protocol_address):
                mechanisms['delegation_enabled'] = True
                
                # Check for delegation attacks
                if await self._is_delegation_vulnerable(protocol_address):
                    mechanisms['vulnerabilities'].append({
                        'type': 'delegation_abuse',
                        'severity': 'medium',
                        'description': 'Delegation mechanism can be exploited'
                    })
            
            return mechanisms
            
        except Exception as e:
            logger.error(f"Error analyzing voting mechanisms: {str(e)}")
            return {}

    async def _analyze_time_locks(self,
                                protocol_address: str,
                                governance_structure: Dict) -> Dict:
        """Analyze timelock mechanisms and potential bypasses"""
        try:
            time_locks = {
                'has_timelock': False,
                'timelock_address': None,
                'min_delay': 0,
                'max_delay': 0,
                'bypass_methods': [],
                'vulnerabilities': []
            }
            
            # Check for timelock contract
            timelock_address = await self._get_timelock_address(protocol_address)
            if timelock_address:
                time_locks['has_timelock'] = True
                time_locks['timelock_address'] = timelock_address
                
                # Get timelock parameters
                delays = await self._get_timelock_delays(timelock_address)
                time_locks.update(delays)
                
                # Check for bypass methods
                bypasses = await self._find_timelock_bypasses(
                    protocol_address,
                    timelock_address
                )
                if bypasses:
                    time_locks['bypass_methods'] = bypasses
                    time_locks['vulnerabilities'].append({
                        'type': 'timelock_bypass',
                        'severity': 'critical',
                        'description': 'Timelock can be bypassed',
                        'methods': bypasses
                    })
            
            return time_locks
            
        except Exception as e:
            logger.error(f"Error analyzing time locks: {str(e)}")
            return {}

    async def _analyze_admin_controls(self,
                                   protocol_address: str,
                                   governance_structure: Dict) -> Dict:
        """Analyze admin controls and privileges"""
        try:
            controls = {
                'admin_address': None,
                'guardian_address': None,
                'privileged_functions': [],
                'upgrade_capability': False,
                'emergency_powers': [],
                'vulnerabilities': []
            }
            
            # Get admin address
            admin = await self._get_admin_address(protocol_address)
            if admin:
                controls['admin_address'] = admin
                
                # Check admin privileges
                privileges = await self._get_admin_privileges(
                    protocol_address,
                    admin
                )
                controls['privileged_functions'] = privileges
                
                # Check for excessive privileges
                if len(privileges) > 10:  # Arbitrary threshold
                    controls['vulnerabilities'].append({
                        'type': 'excessive_privileges',
                        'severity': 'high',
                        'description': 'Admin has excessive privileges'
                    })
            
            # Check upgrade capability
            if await self._is_upgradeable(protocol_address):
                controls['upgrade_capability'] = True
                
                # Check upgrade mechanism security
                if not await self._has_secure_upgrade_pattern(protocol_address):
                    controls['vulnerabilities'].append({
                        'type': 'insecure_upgrade',
                        'severity': 'critical',
                        'description': 'Upgrade mechanism lacks proper security controls'
                    })
            
            return controls
            
        except Exception as e:
            logger.error(f"Error analyzing admin controls: {str(e)}")
            return {}

    async def _find_vulnerabilities(self,
                                  protocol_address: str,
                                  governance_structure: Dict,
                                  voting_mechanisms: Dict,
                                  time_locks: Dict,
                                  admin_controls: Dict,
                                  flash_loan_analysis: Dict) -> List[GovernanceVulnerability]:
        """Find governance-related vulnerabilities"""
        try:
            vulnerabilities = []
            
            # Check voting power manipulation
            if flash_loan_analysis.get('vulnerable_to_flash_loans'):
                vulnerabilities.append(
                    GovernanceVulnerability(
                        protocol_address=protocol_address,
                        governance_type=governance_structure['type'],
                        vulnerability_type='flash_loan_attack',
                        attack_vector='voting_power_manipulation',
                        required_voting_power=flash_loan_analysis['required_voting_power'],
                        flash_loan_potential=True,
                        estimated_cost=flash_loan_analysis['estimated_cost'],
                        time_constraints={
                            'voting_delay': voting_mechanisms['voting_delay'],
                            'voting_period': voting_mechanisms['voting_period']
                        },
                        affected_functions=flash_loan_analysis['affected_functions'],
                        risk_score=0.9,
                        confidence_score=flash_loan_analysis['confidence_score']
                    )
                )
            
            # Check timelock bypasses
            if time_locks.get('bypass_methods'):
                vulnerabilities.append(
                    GovernanceVulnerability(
                        protocol_address=protocol_address,
                        governance_type=governance_structure['type'],
                        vulnerability_type='timelock_bypass',
                        attack_vector='admin_function',
                        required_voting_power=0,
                        flash_loan_potential=False,
                        estimated_cost=0,
                        time_constraints={},
                        affected_functions=time_locks['bypass_methods'],
                        risk_score=0.95,
                        confidence_score=0.9
                    )
                )
            
            # Check admin vulnerabilities
            for vuln in admin_controls.get('vulnerabilities', []):
                if vuln['type'] == 'excessive_privileges':
                    vulnerabilities.append(
                        GovernanceVulnerability(
                            protocol_address=protocol_address,
                            governance_type=governance_structure['type'],
                            vulnerability_type='admin_abuse',
                            attack_vector='privileged_functions',
                            required_voting_power=0,
                            flash_loan_potential=False,
                            estimated_cost=0,
                            time_constraints={},
                            affected_functions=admin_controls['privileged_functions'],
                            risk_score=0.8,
                            confidence_score=0.85
                        )
                    )
            
            return vulnerabilities
            
        except Exception as e:
            logger.error(f"Error finding vulnerabilities: {str(e)}")
            return []

    def _assess_risk(self, vulnerabilities: List[GovernanceVulnerability]) -> Dict:
        """Assess overall risk based on found vulnerabilities"""
        try:
            risk_assessment = {
                'overall_risk_score': 0,
                'critical_vulnerabilities': 0,
                'high_risk_vulnerabilities': 0,
                'medium_risk_vulnerabilities': 0,
                'risk_factors': [],
                'immediate_threats': [],
                'required_actions': []
            }
            
            # Count vulnerabilities by severity
            for vuln in vulnerabilities:
                if vuln.risk_score >= 0.9:
                    risk_assessment['critical_vulnerabilities'] += 1
                    risk_assessment['immediate_threats'].append({
                        'type': vuln.vulnerability_type,
                        'attack_vector': vuln.attack_vector,
                        'estimated_cost': vuln.estimated_cost
                    })
                elif vuln.risk_score >= 0.7:
                    risk_assessment['high_risk_vulnerabilities'] += 1
                else:
                    risk_assessment['medium_risk_vulnerabilities'] += 1
            
            # Calculate overall risk score
            if risk_assessment['critical_vulnerabilities'] > 0:
                risk_assessment['overall_risk_score'] = 0.95
            elif risk_assessment['high_risk_vulnerabilities'] > 0:
                risk_assessment['overall_risk_score'] = 0.8
            elif risk_assessment['medium_risk_vulnerabilities'] > 0:
                risk_assessment['overall_risk_score'] = 0.6
            
            # Generate required actions
            if risk_assessment['overall_risk_score'] >= 0.9:
                risk_assessment['required_actions'].append(
                    "Immediate action required: Critical vulnerabilities detected"
                )
            
            return risk_assessment
            
        except Exception as e:
            logger.error(f"Error assessing risk: {str(e)}")
            return {'overall_risk_score': 1.0}  # Maximum risk on error

    async def _is_compound_governance(self, protocol_address: str) -> bool:
        """Check if protocol uses Compound governance pattern"""
        try:
            # Check contract bytecode for Compound governance signatures
            signatures = [
                "propose(address[],uint256[],string[],bytes[],string)",
                "castVote(uint256,bool)",
                "castVoteBySig(uint256,bool,uint8,bytes32,bytes32)"
            ]
            return await self._check_signatures(protocol_address, signatures)
        except Exception as e:
            logger.error(f"Error checking Compound governance: {str(e)}")
            return False

    async def _is_openzeppelin_governance(self, protocol_address: str) -> bool:
        """Check if protocol uses OpenZeppelin governance pattern"""
        try:
            signatures = [
                "propose(address[],uint256[],bytes[],string)",
                "queue(uint256)",
                "execute(uint256)",
                "cancel(uint256)"
            ]
            return await self._check_signatures(protocol_address, signatures)
        except Exception as e:
            logger.error(f"Error checking OpenZeppelin governance: {str(e)}")
            return False

    async def _is_snapshot_governance(self, protocol_address: str) -> bool:
        """Check if protocol uses Snapshot governance"""
        try:
            # Check for Snapshot integration
            snapshot_events = [
                "ProposalCreated(bytes32,string)",
                "VoteCast(address,bytes32,uint8,uint256,string)"
            ]
            return await self._check_events(protocol_address, snapshot_events)
        except Exception as e:
            logger.error(f"Error checking Snapshot governance: {str(e)}")
            return False

    async def _get_governance_params(self, protocol_address: str) -> Dict:
        """Get governance parameters from contract"""
        try:
            params = {}
            # Get voting token
            params['voting_token'] = await self._get_voting_token(protocol_address)
            
            # Get quorum
            params['quorum'] = await self._get_quorum(protocol_address)
            
            # Get proposal threshold
            params['proposal_threshold'] = await self._get_proposal_threshold(protocol_address)
            
            # Get execution delay
            params['execution_delay'] = await self._get_execution_delay(protocol_address)
            
            # Get guardian
            params['guardian'] = await self._get_guardian(protocol_address)
            
            return params
        except Exception as e:
            logger.error(f"Error getting governance params: {str(e)}")
            return {}

    async def _analyze_flash_loan_vectors(self, 
                                        protocol_address: str,
                                        voting_mechanisms: Dict,
                                        chain_id: int) -> Dict:
        """Analyze potential flash loan attack vectors"""
        try:
            analysis = {
                'vulnerable_to_flash_loans': False,
                'required_voting_power': 0,
                'estimated_cost': 0,
                'affected_functions': [],
                'confidence_score': 0,
                'attack_paths': []
            }
            
            if not voting_mechanisms.get('token_based'):
                return analysis
                
            # Get voting token details
            token_address = await self._get_voting_token(protocol_address)
            if not token_address:
                return analysis
                
            # Check if token can be flash loaned
            flash_loan_sources = await self._find_flash_loan_sources(
                token_address,
                chain_id
            )
            
            if not flash_loan_sources:
                return analysis
                
            # Calculate required voting power
            required_power = await self._calculate_required_voting_power(
                protocol_address,
                voting_mechanisms
            )
            
            # Estimate flash loan costs
            costs = await self._estimate_flash_loan_costs(
                token_address,
                required_power,
                flash_loan_sources
            )
            
            # Find vulnerable functions
            vulnerable_functions = await self._find_vulnerable_functions(
                protocol_address,
                required_power
            )
            
            if vulnerable_functions and costs['total_cost'] > 0:
                analysis.update({
                    'vulnerable_to_flash_loans': True,
                    'required_voting_power': required_power,
                    'estimated_cost': costs['total_cost'],
                    'affected_functions': vulnerable_functions,
                    'confidence_score': 0.9,
                    'attack_paths': [{
                        'flash_loan_source': source,
                        'amount': costs['amounts'][source],
                        'cost': costs['costs'][source]
                    } for source in flash_loan_sources]
                })
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing flash loan vectors: {str(e)}")
            return {}

    async def _find_flash_loan_sources(self, 
                                     token_address: str,
                                     chain_id: int) -> List[str]:
        """Find potential sources for flash loans of the token"""
        try:
            sources = []
            
            # Check major lending protocols
            for protocol, address in self.flash_loan_providers.items():
                if await self._supports_flash_loans(address, token_address):
                    sources.append(protocol)
            
            return sources
            
        except Exception as e:
            logger.error(f"Error finding flash loan sources: {str(e)}")
            return []

    async def _calculate_required_voting_power(self,
                                            protocol_address: str,
                                            voting_mechanisms: Dict) -> float:
        """Calculate required voting power for successful attack"""
        try:
            # Get total voting power
            total_power = await self._get_total_voting_power(protocol_address)
            
            # Get quorum requirement
            quorum = await self._get_quorum(protocol_address)
            
            # Calculate based on voting mechanism
            if voting_mechanisms.get('vote_differential'):
                required = (total_power * quorum * 
                          (1 + voting_mechanisms['vote_differential']))
            else:
                required = total_power * quorum
                
            # Add safety margin
            return required * 1.1
            
        except Exception as e:
            logger.error(f"Error calculating required voting power: {str(e)}")
            return 0

    async def _estimate_flash_loan_costs(self,
                                       token_address: str,
                                       required_amount: float,
                                       sources: List[str]) -> Dict:
        """Estimate costs for flash loan attack"""
        try:
            estimates = {
                'total_cost': 0,
                'amounts': {},
                'costs': {}
            }
            
            for source in sources:
                # Get flash loan fee
                fee = await self._get_flash_loan_fee(
                    self.flash_loan_providers[source],
                    token_address
                )
                
                # Calculate cost
                cost = required_amount * fee
                
                estimates['amounts'][source] = required_amount
                estimates['costs'][source] = cost
                
                if cost < estimates['total_cost'] or estimates['total_cost'] == 0:
                    estimates['total_cost'] = cost
                    
            return estimates
            
        except Exception as e:
            logger.error(f"Error estimating flash loan costs: {str(e)}")
            return {'total_cost': 0, 'amounts': {}, 'costs': {}}

    async def _check_signatures(self, address: str, signatures: List[str]) -> bool:
        """Check if contract implements specific function signatures"""
        try:
            bytecode = await self.state_manager.get_contract_bytecode(address)
            for sig in signatures:
                if not self._find_signature_in_bytecode(bytecode, sig):
                    return False
            return True
        except Exception as e:
            logger.error(f"Error checking signatures: {str(e)}")
            return False

    async def _check_events(self, address: str, events: List[str]) -> bool:
        """Check if contract implements specific events"""
        try:
            abi = await self.state_manager.get_contract_abi(address)
            for event in events:
                if not self._find_event_in_abi(abi, event):
                    return False
            return True
        except Exception as e:
            logger.error(f"Error checking events: {str(e)}")
            return False

    async def _get_voting_token(self, protocol_address: str) -> Optional[str]:
        """Get governance token address"""
        try:
            # Try common function names
            functions = [
                "getVotingToken()",
                "governanceToken()",
                "token()",
                "votingPower()"
            ]
            
            for func in functions:
                try:
                    result = await self.state_manager.call_function(
                        protocol_address,
                        func
                    )
                    if result and self._is_valid_address(result):
                        return result
                except:
                    continue
                    
            return None
            
        except Exception as e:
            logger.error(f"Error getting voting token: {str(e)}")
            return None

    async def _get_quorum(self, protocol_address: str) -> float:
        """Get quorum requirement"""
        try:
            functions = [
                "quorumVotes()",
                "quorumNumerator()",
                "quorum(uint256)",  # Try with block number
                "quorumThreshold()"
            ]
            
            for func in functions:
                try:
                    result = await self.state_manager.call_function(
                        protocol_address,
                        func,
                        args=[self.state_manager.get_current_block()]
                    )
                    if result is not None:
                        return float(result) / 1e18  # Convert from wei
                except:
                    continue
                    
            return 0.5  # Default to 50% if not found
            
        except Exception as e:
            logger.error(f"Error getting quorum: {str(e)}")
            return 0.5

    async def _get_proposal_threshold(self, protocol_address: str) -> float:
        """Get proposal threshold"""
        try:
            functions = [
                "proposalThreshold()",
                "getProposalThreshold()",
                "minimumProposalPower()"
            ]
            
            for func in functions:
                try:
                    result = await self.state_manager.call_function(
                        protocol_address,
                        func
                    )
                    if result is not None:
                        return float(result) / 1e18
                except:
                    continue
                    
            return 0.01  # Default to 1% if not found
            
        except Exception as e:
            logger.error(f"Error getting proposal threshold: {str(e)}")
            return 0.01

    async def _get_execution_delay(self, protocol_address: str) -> int:
        """Get execution delay in seconds"""
        try:
            functions = [
                "getMinDelay()",
                "delay()",
                "timelock()",
                "executionDelay()"
            ]
            
            for func in functions:
                try:
                    result = await self.state_manager.call_function(
                        protocol_address,
                        func
                    )
                    if result is not None:
                        return int(result)
                except:
                    continue
                    
            return 172800  # Default to 48 hours if not found
            
        except Exception as e:
            logger.error(f"Error getting execution delay: {str(e)}")
            return 172800

    async def _get_guardian(self, protocol_address: str) -> Optional[str]:
        """Get guardian address if exists"""
        try:
            functions = [
                "guardian()",
                "getGuardian()",
                "emergencyAdmin()",
                "admin()"
            ]
            
            for func in functions:
                try:
                    result = await self.state_manager.call_function(
                        protocol_address,
                        func
                    )
                    if result and self._is_valid_address(result):
                        return result
                except:
                    continue
                    
            return None
            
        except Exception as e:
            logger.error(f"Error getting guardian: {str(e)}")
            return None

    async def _supports_flash_loans(self, provider: str, token: str) -> bool:
        """Check if provider supports flash loans for token"""
        try:
            # Check if token is listed
            result = await self.state_manager.call_function(
                provider,
                "getReserveData(address)",
                args=[token]
            )
            
            if not result:
                return False
                
            # Check if flash loans are enabled
            try:
                enabled = await self.state_manager.call_function(
                    provider,
                    "flashLoanEnabled(address)",
                    args=[token]
                )
                return bool(enabled)
            except:
                # If function doesn't exist, assume enabled
                return True
                
        except Exception as e:
            logger.error(f"Error checking flash loan support: {str(e)}")
            return False

    async def _get_flash_loan_fee(self, provider: str, token: str) -> float:
        """Get flash loan fee percentage"""
        try:
            functions = [
                "FLASH_LOAN_FEE()",
                "flashLoanFee()",
                "getFee(address)",
                "flashFee(address,uint256)"
            ]
            
            for func in functions:
                try:
                    result = await self.state_manager.call_function(
                        provider,
                        func,
                        args=[token, 1e18] if "flashFee" in func else None
                    )
                    if result is not None:
                        return float(result) / 10000  # Convert basis points to percentage
                except:
                    continue
                    
            return 0.0009  # Default to 0.09% if not found
            
        except Exception as e:
            logger.error(f"Error getting flash loan fee: {str(e)}")
            return 0.0009 