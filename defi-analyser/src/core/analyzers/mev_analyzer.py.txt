from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from eth_utils import to_hex, to_checksum_address
import networkx as nx
from web3.exceptions import ContractLogicError
import asyncio
from ..utils.config import config
from ..utils.logger import logger
from .bytecode_analyzer import BytecodeAnalyzer

@dataclass
class MEVOpportunity:
    type: str  # 'sandwich', 'arbitrage', 'liquidation', 'frontrun'
    entry_points: List[str]
    tokens: List[str]
    estimated_profit: float
    required_capital: float
    gas_cost: float
    complexity: int  # 1-10 scale
    success_probability: float
    competition_level: float  # 0-1 scale
    execution_time: int  # in blocks
    risk_factors: List[str]

class MEVAnalyzer:
    """Advanced analyzer for MEV opportunities and arbitrage"""

    def __init__(self, web3_client, state_manager):
        self.web3 = web3_client
        self.state_manager = state_manager
        self.bytecode_analyzer = BytecodeAnalyzer(web3_client)
        self.dex_graph = nx.DiGraph()
        self.token_graph = nx.DiGraph()
        self.known_searchers = set()
        self.competition_data = {}
        
    async def analyze_mev_opportunities(self, 
                                      contract_address: str,
                                      chain_id: int,
                                      max_routes: int = 3) -> Dict:
        """Analyze MEV opportunities related to the contract"""
        try:
            contract_address = self.web3.to_checksum_address(contract_address)
            
            # Build DEX and token graphs
            await self._build_market_graphs(contract_address, chain_id)
            
            # Find sandwich opportunities
            sandwich_ops = await self._find_sandwich_opportunities(contract_address)
            
            # Find arbitrage opportunities
            arb_ops = await self._find_arbitrage_opportunities(max_routes)
            
            # Find liquidation opportunities
            liq_ops = await self._find_liquidation_opportunities(contract_address)
            
            # Find frontrunning opportunities
            frontrun_ops = await self._find_frontrun_opportunities(contract_address)
            
            # Analyze competition
            competition = await self._analyze_competition(
                sandwich_ops + arb_ops + liq_ops + frontrun_ops
            )
            
            # Calculate optimal execution
            execution = await self._calculate_optimal_execution(
                sandwich_ops + arb_ops + liq_ops + frontrun_ops,
                competition
            )
            
            return {
                'sandwich_opportunities': sandwich_ops,
                'arbitrage_opportunities': arb_ops,
                'liquidation_opportunities': liq_ops,
                'frontrun_opportunities': frontrun_ops,
                'competition_analysis': competition,
                'optimal_execution': execution,
                'estimated_total_value': sum(op.estimated_profit for op in 
                    sandwich_ops + arb_ops + liq_ops + frontrun_ops),
                'risk_assessment': self._assess_mev_risks(
                    sandwich_ops + arb_ops + liq_ops + frontrun_ops
                )
            }
            
        except Exception as e:
            logger.error(f"Error in MEV analysis: {str(e)}")
            return {'error': str(e)}

    async def _build_market_graphs(self, contract_address: str, chain_id: int) -> None:
        """Build graphs of DEX and token relationships"""
        try:
            # Get all DEXes on the chain
            dexes = await self._get_chain_dexes(chain_id)
            
            # Add DEX nodes and edges
            for dex in dexes:
                self.dex_graph.add_node(
                    dex['address'],
                    type=dex['type'],
                    protocol=dex['protocol']
                )
                
                # Add pools as edges
                pools = await self._get_dex_pools(dex['address'])
                for pool in pools:
                    self.dex_graph.add_edge(
                        dex['address'],
                        pool['address'],
                        type='pool',
                        tokens=[pool['token0'], pool['token1']],
                        reserves=pool['reserves']
                    )
                    
                    # Add tokens to token graph
                    self.token_graph.add_edge(
                        pool['token0'],
                        pool['token1'],
                        pools=[{
                            'address': pool['address'],
                            'dex': dex['address'],
                            'reserves': pool['reserves']
                        }]
                    )
                    
        except Exception as e:
            logger.error(f"Error building market graphs: {str(e)}")

    async def _find_sandwich_opportunities(self, contract_address: str) -> List[MEVOpportunity]:
        """Find sandwich attack opportunities"""
        opportunities = []
        
        try:
            # Get pending transactions involving the contract
            pending_txs = await self._get_pending_transactions(contract_address)
            
            for tx in pending_txs:
                if self._is_sandwichable(tx):
                    # Calculate optimal sandwich parameters
                    sandwich = await self._calculate_sandwich_parameters(tx)
                    
                    if sandwich['profit'] > 0:
                        opportunities.append(MEVOpportunity(
                            type='sandwich',
                            entry_points=[tx['hash']],
                            tokens=sandwich['tokens'],
                            estimated_profit=sandwich['profit'],
                            required_capital=sandwich['required_capital'],
                            gas_cost=sandwich['gas_cost'],
                            complexity=sandwich['complexity'],
                            success_probability=sandwich['success_probability'],
                            competition_level=sandwich['competition_level'],
                            execution_time=1,
                            risk_factors=sandwich['risk_factors']
                        ))
                    
            return sorted(opportunities, key=lambda x: x.estimated_profit, reverse=True)
            
        except Exception as e:
            logger.error(f"Error finding sandwich opportunities: {str(e)}")
            return []

    async def _find_arbitrage_opportunities(self, max_routes: int) -> List[MEVOpportunity]:
        """Find arbitrage opportunities across DEXes"""
        opportunities = []
        
        try:
            # Find negative cycles in token graph
            cycles = self._find_negative_cycles(self.token_graph, max_length=max_routes)
            
            for cycle in cycles:
                # Calculate arbitrage parameters
                arb = await self._calculate_arbitrage_parameters(cycle)
                
                if arb['profit'] > 0:
                    opportunities.append(MEVOpportunity(
                        type='arbitrage',
                        entry_points=arb['route'],
                        tokens=arb['tokens'],
                        estimated_profit=arb['profit'],
                        required_capital=arb['required_capital'],
                        gas_cost=arb['gas_cost'],
                        complexity=len(cycle),
                        success_probability=arb['success_probability'],
                        competition_level=arb['competition_level'],
                        execution_time=1,
                        risk_factors=arb['risk_factors']
                    ))
                    
            return sorted(opportunities, key=lambda x: x.estimated_profit, reverse=True)
            
        except Exception as e:
            logger.error(f"Error finding arbitrage opportunities: {str(e)}")
            return []

    async def _find_liquidation_opportunities(self, contract_address: str) -> List[MEVOpportunity]:
        """Find liquidation opportunities"""
        opportunities = []
        
        try:
            # Get accounts near liquidation
            accounts = await self._get_liquidatable_accounts(contract_address)
            
            for account in accounts:
                # Calculate liquidation parameters
                liq = await self._calculate_liquidation_parameters(account)
                
                if liq['profit'] > 0:
                    opportunities.append(MEVOpportunity(
                        type='liquidation',
                        entry_points=[account['address']],
                        tokens=liq['tokens'],
                        estimated_profit=liq['profit'],
                        required_capital=liq['required_capital'],
                        gas_cost=liq['gas_cost'],
                        complexity=3,
                        success_probability=liq['success_probability'],
                        competition_level=liq['competition_level'],
                        execution_time=1,
                        risk_factors=liq['risk_factors']
                    ))
                    
            return sorted(opportunities, key=lambda x: x.estimated_profit, reverse=True)
            
        except Exception as e:
            logger.error(f"Error finding liquidation opportunities: {str(e)}")
            return []

    async def _analyze_competition(self, opportunities: List[MEVOpportunity]) -> Dict:
        """Analyze competition for MEV opportunities"""
        try:
            competition = {
                'searchers': await self._get_active_searchers(),
                'historical_success_rates': {},
                'gas_price_statistics': {},
                'strategy_analysis': {},
                'risk_factors': []
            }
            
            # Analyze historical success rates
            for searcher in competition['searchers']:
                success_rate = await self._calculate_searcher_success_rate(searcher)
                competition['historical_success_rates'][searcher] = success_rate
                
            # Analyze gas price strategies
            competition['gas_price_statistics'] = await self._analyze_gas_strategies(
                competition['searchers']
            )
            
            # Analyze searcher strategies
            competition['strategy_analysis'] = await self._analyze_searcher_strategies(
                competition['searchers']
            )
            
            # Identify risk factors
            competition['risk_factors'] = self._identify_competition_risks(
                competition['searchers'],
                competition['historical_success_rates'],
                competition['strategy_analysis']
            )
            
            return competition
            
        except Exception as e:
            logger.error(f"Error analyzing competition: {str(e)}")
            return {}

    async def _calculate_optimal_execution(self, 
                                        opportunities: List[MEVOpportunity],
                                        competition: Dict) -> Dict:
        """Calculate optimal execution parameters"""
        try:
            execution = {
                'optimal_gas_price': 0,
                'bundle_transactions': [],
                'execution_route': [],
                'fallback_strategies': [],
                'risk_mitigation': {}
            }
            
            # Calculate optimal gas price
            execution['optimal_gas_price'] = self._calculate_optimal_gas_price(
                opportunities,
                competition
            )
            
            # Generate transaction bundle
            execution['bundle_transactions'] = await self._generate_transaction_bundle(
                opportunities,
                execution['optimal_gas_price']
            )
            
            # Calculate optimal route
            execution['execution_route'] = self._calculate_execution_route(
                opportunities,
                competition
            )
            
            # Generate fallback strategies
            execution['fallback_strategies'] = self._generate_fallback_strategies(
                opportunities,
                competition
            )
            
            # Generate risk mitigation strategies
            execution['risk_mitigation'] = self._generate_risk_mitigation(
                opportunities,
                competition
            )
            
            return execution
            
        except Exception as e:
            logger.error(f"Error calculating optimal execution: {str(e)}")
            return {}

    def _assess_mev_risks(self, opportunities: List[MEVOpportunity]) -> Dict:
        """Assess risks associated with MEV opportunities"""
        try:
            assessment = {
                'overall_risk_score': 0,
                'risk_factors': [],
                'mitigation_strategies': [],
                'opportunity_specific_risks': {}
            }
            
            # Calculate risk scores for each opportunity
            for op in opportunities:
                risk_score = self._calculate_opportunity_risk(op)
                assessment['opportunity_specific_risks'][op.type] = risk_score
                
            # Calculate overall risk score
            assessment['overall_risk_score'] = sum(
                score['total_score'] * score['weight']
                for score in assessment['opportunity_specific_risks'].values()
            )
            
            # Identify risk factors
            assessment['risk_factors'] = self._identify_risk_factors(
                opportunities,
                assessment['opportunity_specific_risks']
            )
            
            # Generate mitigation strategies
            assessment['mitigation_strategies'] = self._generate_mitigation_strategies(
                assessment['risk_factors']
            )
            
            return assessment
            
        except Exception as e:
            logger.error(f"Error assessing MEV risks: {str(e)}")
            return {'overall_risk_score': 1.0}  # Maximum risk on error 