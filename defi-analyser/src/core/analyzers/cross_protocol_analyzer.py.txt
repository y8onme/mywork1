from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from eth_utils import to_hex, to_checksum_address
import networkx as nx
from web3.exceptions import ContractLogicError
import asyncio
from ..vulnerability_scanner import VulnerabilityScanner
from .bytecode_analyzer import BytecodeAnalyzer
from .governance_analyzer import GovernanceAnalyzer

@dataclass
class CrossProtocolVector:
    source_protocol: str
    target_protocol: str
    interaction_type: str  # 'flash_loan', 'price_impact', 'governance', etc.
    vector_type: str      # 'atomic', 'multi-tx', 'sandwich', etc.
    entry_points: List[str]
    required_assets: Dict[str, float]
    estimated_profit: float
    complexity: int       # 1-10 scale
    success_probability: float
    risk_factors: List[str]
    detection_probability: float

class CrossProtocolAnalyzer:
    """Advanced analyzer for cross-protocol interactions and MEV opportunities"""

    def __init__(self, web3_client, state_manager):
        self.web3 = web3_client
        self.state_manager = state_manager
        self.bytecode_analyzer = BytecodeAnalyzer(web3_client)
        self.governance_analyzer = GovernanceAnalyzer(web3_client)
        self.vulnerability_scanner = VulnerabilityScanner()
        self.protocol_graph = nx.DiGraph()
        self.known_protocols = set()
        self.interaction_patterns = self._load_interaction_patterns()
        
    async def analyze_cross_protocol_vectors(self, 
                                           protocol_address: str,
                                           chain_id: int,
                                           max_depth: int = 3) -> Dict:
        """Analyze cross-protocol attack vectors and MEV opportunities"""
        try:
            protocol_address = self.web3.to_checksum_address(protocol_address)
            
            # Build protocol interaction graph
            await self._build_protocol_graph(protocol_address, chain_id, max_depth)
            
            # Analyze potential vectors
            vectors = await self._analyze_interaction_vectors(protocol_address)
            
            # Analyze MEV opportunities
            mev_opportunities = await self._analyze_mev_opportunities(protocol_address)
            
            # Analyze governance impacts
            governance_vectors = await self._analyze_governance_vectors(protocol_address)
            
            # Analyze liquidity dependencies
            liquidity_analysis = await self._analyze_liquidity_dependencies(protocol_address)
            
            # Generate combined risk assessment
            risk_assessment = self._assess_cross_protocol_risks(
                vectors,
                mev_opportunities,
                governance_vectors,
                liquidity_analysis
            )
            
            return {
                'interaction_vectors': vectors,
                'mev_opportunities': mev_opportunities,
                'governance_vectors': governance_vectors,
                'liquidity_dependencies': liquidity_analysis,
                'risk_assessment': risk_assessment,
                'protocol_graph': self._export_protocol_graph(),
                'mitigation_strategies': self._generate_mitigation_strategies(risk_assessment)
            }
            
        except Exception as e:
            logger.error(f"Error in cross-protocol analysis: {str(e)}")
            return {'error': str(e)}

    async def _build_protocol_graph(self, 
                                  start_address: str, 
                                  chain_id: int,
                                  max_depth: int) -> None:
        """Build directed graph of protocol interactions"""
        try:
            # Initialize graph with starting protocol
            self.protocol_graph.add_node(
                start_address,
                protocol_type=await self._identify_protocol_type(start_address),
                chain_id=chain_id
            )
            
            # BFS to discover protocol interactions
            queue = [(start_address, 0)]
            visited = {start_address}
            
            while queue and queue[0][1] < max_depth:
                current_address, depth = queue.pop(0)
                
                # Get external calls from bytecode
                external_calls = await self._get_external_calls(current_address)
                
                # Analyze each external call
                for target_address in external_calls:
                    if target_address not in visited:
                        # Verify it's a protocol
                        if await self._is_protocol(target_address):
                            visited.add(target_address)
                            protocol_type = await self._identify_protocol_type(target_address)
                            
                            # Add node and edge
                            self.protocol_graph.add_node(
                                target_address,
                                protocol_type=protocol_type,
                                chain_id=chain_id
                            )
                            self.protocol_graph.add_edge(
                                current_address,
                                target_address,
                                interaction_type=await self._identify_interaction_type(
                                    current_address,
                                    target_address
                                )
                            )
                            
                            if depth + 1 < max_depth:
                                queue.append((target_address, depth + 1))
                                
        except Exception as e:
            logger.error(f"Error building protocol graph: {str(e)}")

    async def _analyze_interaction_vectors(self, protocol_address: str) -> List[Dict]:
        """Analyze potential cross-protocol attack vectors"""
        vectors = []
        
        try:
            # Get all paths in protocol graph
            paths = list(nx.all_simple_paths(
                self.protocol_graph,
                protocol_address,
                cutoff=3
            ))
            
            for path in paths:
                # Analyze path for potential vectors
                vector = await self._analyze_path_vector(path)
                if vector:
                    vectors.append(vector)
                    
            # Analyze parallel execution possibilities
            parallel_vectors = await self._analyze_parallel_vectors(vectors)
            vectors.extend(parallel_vectors)
            
            # Sort by estimated profit
            vectors.sort(key=lambda x: x.estimated_profit, reverse=True)
            
            return vectors
            
        except Exception as e:
            logger.error(f"Error analyzing interaction vectors: {str(e)}")
            return []

    async def _analyze_mev_opportunities(self, protocol_address: str) -> List[Dict]:
        """Analyze potential MEV opportunities"""
        opportunities = []
        
        try:
            # Analyze sandwich attack opportunities
            sandwich_ops = await self._analyze_sandwich_opportunities(protocol_address)
            opportunities.extend(sandwich_ops)
            
            # Analyze arbitrage opportunities
            arb_ops = await self._analyze_arbitrage_opportunities(protocol_address)
            opportunities.extend(arb_ops)
            
            # Analyze liquidation opportunities
            liq_ops = await self._analyze_liquidation_opportunities(protocol_address)
            opportunities.extend(liq_ops)
            
            # Sort by expected value
            opportunities.sort(key=lambda x: x['expected_value'], reverse=True)
            
            return opportunities
            
        except Exception as e:
            logger.error(f"Error analyzing MEV opportunities: {str(e)}")
            return []

    async def _analyze_governance_vectors(self, protocol_address: str) -> List[Dict]:
        """Analyze governance-related attack vectors"""
        vectors = []
        
        try:
            # Get all connected governance protocols
            governance_nodes = [
                node for node in self.protocol_graph.nodes
                if self.protocol_graph.nodes[node]['protocol_type'] == 'governance'
            ]
            
            for gov_address in governance_nodes:
                # Analyze governance influence
                influence = await self._analyze_governance_influence(
                    gov_address,
                    protocol_address
                )
                
                if influence['has_influence']:
                    vectors.append({
                        'governance_protocol': gov_address,
                        'influence_type': influence['type'],
                        'required_voting_power': influence['required_power'],
                        'time_delay': influence['time_delay'],
                        'estimated_cost': influence['estimated_cost'],
                        'success_probability': influence['success_probability']
                    })
                    
            return vectors
            
        except Exception as e:
            logger.error(f"Error analyzing governance vectors: {str(e)}")
            return []

    async def _analyze_liquidity_dependencies(self, protocol_address: str) -> Dict:
        """Analyze liquidity dependencies and risks"""
        try:
            dependencies = {
                'direct_dependencies': [],
                'indirect_dependencies': [],
                'risk_score': 0,
                'concentration_risk': 0,
                'systemic_risk': 0
            }
            
            # Analyze direct liquidity providers
            direct_deps = await self._get_liquidity_providers(protocol_address)
            dependencies['direct_dependencies'] = direct_deps
            
            # Analyze indirect dependencies
            indirect_deps = await self._get_indirect_liquidity_dependencies(
                protocol_address,
                direct_deps
            )
            dependencies['indirect_dependencies'] = indirect_deps
            
            # Calculate risk scores
            dependencies['concentration_risk'] = self._calculate_concentration_risk(
                direct_deps,
                indirect_deps
            )
            
            dependencies['systemic_risk'] = self._calculate_systemic_risk(
                direct_deps,
                indirect_deps
            )
            
            dependencies['risk_score'] = max(
                dependencies['concentration_risk'],
                dependencies['systemic_risk']
            )
            
            return dependencies
            
        except Exception as e:
            logger.error(f"Error analyzing liquidity dependencies: {str(e)}")
            return {}

    def _assess_cross_protocol_risks(self,
                                   vectors: List[Dict],
                                   mev_opportunities: List[Dict],
                                   governance_vectors: List[Dict],
                                   liquidity_analysis: Dict) -> Dict:
        """Assess overall cross-protocol risks"""
        try:
            assessment = {
                'risk_score': 0,
                'risk_factors': [],
                'attack_paths': [],
                'critical_dependencies': [],
                'recommendations': []
            }
            
            # Assess vector risks
            vector_risk = self._calculate_vector_risk(vectors)
            assessment['risk_factors'].extend(vector_risk['factors'])
            
            # Assess MEV risks
            mev_risk = self._calculate_mev_risk(mev_opportunities)
            assessment['risk_factors'].extend(mev_risk['factors'])
            
            # Assess governance risks
            gov_risk = self._calculate_governance_risk(governance_vectors)
            assessment['risk_factors'].extend(gov_risk['factors'])
            
            # Assess liquidity risks
            liq_risk = self._calculate_liquidity_risk(liquidity_analysis)
            assessment['risk_factors'].extend(liq_risk['factors'])
            
            # Calculate overall risk score
            assessment['risk_score'] = self._calculate_combined_risk_score([
                vector_risk['score'],
                mev_risk['score'],
                gov_risk['score'],
                liq_risk['score']
            ])
            
            # Generate recommendations
            assessment['recommendations'] = self._generate_risk_recommendations(
                assessment['risk_factors']
            )
            
            return assessment
            
        except Exception as e:
            logger.error(f"Error assessing cross-protocol risks: {str(e)}")
            return {'risk_score': 1.0}  # Maximum risk on error 