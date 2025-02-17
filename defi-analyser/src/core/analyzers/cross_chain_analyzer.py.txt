# src/core/analyzers/cross_chain_analyzer.py

import asyncio
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from ...utils.config import config
from ...utils.logger import logger
from ...utils.state.state_manager import StateManager
from ..multi_stage_executor import MultiStageExecutor

@dataclass
class CrossChainOpportunity:
    source_chain_id: int
    target_chain_id: int
    opportunity_type: str
    estimated_profit: float
    required_capital: float
    execution_steps: List[Dict]
    risk_score: float
    confidence_score: float
    gas_estimates: Dict[int, int]
    bridging_routes: List[Dict]
    dependencies: List[str]

class CrossChainAnalyzer:
    def __init__(self):
        self.state_manager = StateManager()
        self.executor = MultiStageExecutor()
        self.analyzed_pairs: Set[str] = set()
        
    async def analyze_opportunities(self,
                                  chain_pairs: List[Dict],
                                  options: Optional[Dict] = None) -> List[CrossChainOpportunity]:
        """Analyze cross-chain opportunities"""
        try:
            opportunities = []
            options = options or {}
            
            for pair in chain_pairs:
                source_id = pair['source_chain']
                target_id = pair['target_chain']
                
                # Skip if already analyzed
                pair_key = f"{source_id}_{target_id}"
                if pair_key in self.analyzed_pairs:
                    continue
                    
                # Analyze pair
                pair_opportunities = await self._analyze_chain_pair(
                    source_id,
                    target_id,
                    options
                )
                
                opportunities.extend(pair_opportunities)
                self.analyzed_pairs.add(pair_key)
                
            return opportunities
            
        except Exception as e:
            logger.error(f"Error analyzing cross-chain opportunities: {str(e)}")
            return []

    async def _analyze_chain_pair(self,
                                source_chain: int,
                                target_chain: int,
                                options: Dict) -> List[CrossChainOpportunity]:
        """Analyze opportunities between chain pair"""
        try:
            opportunities = []
            
            # Get chain states
            source_state = await self.state_manager.get_state(source_chain)
            target_state = await self.state_manager.get_state(target_chain)
            
            # Analyze arbitrage opportunities
            arb_opportunities = await self._find_arbitrage_opportunities(
                source_chain,
                target_chain,
                source_state,
                target_state,
                options
            )
            opportunities.extend(arb_opportunities)
            
            # Analyze bridging opportunities
            bridge_opportunities = await self._find_bridging_opportunities(
                source_chain,
                target_chain,
                source_state,
                target_state,
                options
            )
            opportunities.extend(bridge_opportunities)
            
            # Analyze liquidity opportunities
            liquidity_opportunities = await self._find_liquidity_opportunities(
                source_chain,
                target_chain,
                source_state,
                target_state,
                options
            )
            opportunities.extend(liquidity_opportunities)
            
            return opportunities
            
        except Exception as e:
            logger.error(f"Error analyzing chain pair: {str(e)}")
            return []

    async def _find_arbitrage_opportunities(self,
                                          source_chain: int,
                                          target_chain: int,
                                          source_state: Dict,
                                          target_state: Dict,
                                          options: Dict) -> List[CrossChainOpportunity]:
        """Find arbitrage opportunities between chains"""
        try:
            opportunities = []
            
            # Get token prices on both chains
            source_prices = await self._get_token_prices(source_chain)
            target_prices = await self._get_token_prices(target_chain)
            
            # Find price discrepancies
            for token, source_price in source_prices.items():
                if token not in target_prices:
                    continue
                    
                target_price = target_prices[token]
                price_diff = abs(source_price - target_price)
                
                # Calculate potential profit
                if price_diff / min(source_price, target_price) >= options.get('min_price_diff', 0.02):
                    opportunity = await self._create_arbitrage_opportunity(
                        source_chain,
                        target_chain,
                        token,
                        source_price,
                        target_price,
                        options
                    )
                    
                    if opportunity:
                        opportunities.append(opportunity)
                        
            return opportunities
            
        except Exception as e:
            logger.error(f"Error finding arbitrage opportunities: {str(e)}")
            return []

    async def _find_bridging_opportunities(self,
                                         source_chain: int,
                                         target_chain: int,
                                         source_state: Dict,
                                         target_state: Dict,
                                         options: Dict) -> List[CrossChainOpportunity]:
        """Find bridging opportunities between chains"""
        try:
            opportunities = []
            
            # Get bridge routes
            routes = await self._get_bridge_routes(
                source_chain,
                target_chain
            )
            
            for route in routes:
                # Analyze route efficiency
                efficiency = await self._analyze_bridge_efficiency(
                    route,
                    source_chain,
                    target_chain
                )
                
                if efficiency['score'] >= options.get('min_bridge_efficiency', 0.8):
                    opportunity = await self._create_bridge_opportunity(
                        source_chain,
                        target_chain,
                        route,
                        efficiency,
                        options
                    )
                    
                    if opportunity:
                        opportunities.append(opportunity)
                        
            return opportunities
            
        except Exception as e:
            logger.error(f"Error finding bridging opportunities: {str(e)}")
            return []

    async def _find_liquidity_opportunities(self,
                                          source_chain: int,
                                          target_chain: int,
                                          source_state: Dict,
                                          target_state: Dict,
                                          options: Dict) -> List[CrossChainOpportunity]:
        """Find liquidity opportunities between chains"""
        try:
            opportunities = []
            
            # Analyze liquidity distribution
            source_liquidity = await self._analyze_liquidity(source_chain)
            target_liquidity = await self._analyze_liquidity(target_chain)
            
            # Find imbalances
            imbalances = self._find_liquidity_imbalances(
                source_liquidity,
                target_liquidity
            )
            
            for imbalance in imbalances:
                if imbalance['severity'] >= options.get('min_imbalance_severity', 0.3):
                    opportunity = await self._create_liquidity_opportunity(
                        source_chain,
                        target_chain,
                        imbalance,
                        options
                    )
                    
                    if opportunity:
                        opportunities.append(opportunity)
                        
            return opportunities
            
        except Exception as e:
            logger.error(f"Error finding liquidity opportunities: {str(e)}")
            return []

    async def _get_token_prices(self, chain_id: int) -> Dict[str, float]:
        """Get token prices on chain"""
        try:
            chain_config = config.get_chain_config(chain_id)
            prices = {}
            
            for token_address in chain_config.tracked_tokens:
                price = await self._get_token_price(token_address, chain_id)
                if price:
                    prices[token_address] = price
                    
            return prices
            
        except Exception as e:
            logger.error(f"Error getting token prices: {str(e)}")
            return {}

    async def _get_bridge_routes(self,
                               source_chain: int,
                               target_chain: int) -> List[Dict]:
        """Get available bridge routes between chains"""
        try:
            source_config = config.get_chain_config(source_chain)
            target_config = config.get_chain_config(target_chain)
            
            routes = []
            
            # Check official bridges
            official_bridges = self._get_official_bridges(
                source_chain,
                target_chain
            )
            routes.extend(official_bridges)
            
            # Check third-party bridges
            third_party_bridges = self._get_third_party_bridges(
                source_chain,
                target_chain
            )
            routes.extend(third_party_bridges)
            
            return routes
            
        except Exception as e:
            logger.error(f"Error getting bridge routes: {str(e)}")
            return []

    async def _analyze_bridge_efficiency(self,
                                       route: Dict,
                                       source_chain: int,
                                       target_chain: int) -> Dict:
        """Analyze bridge route efficiency"""
        try:
            # Calculate metrics
            speed = await self._calculate_bridge_speed(route)
            cost = await self._calculate_bridge_cost(route)
            reliability = await self._calculate_bridge_reliability(route)
            
            # Calculate overall score
            score = (speed * 0.3 + cost * 0.3 + reliability * 0.4)
            
            return {
                'score': score,
                'metrics': {
                    'speed': speed,
                    'cost': cost,
                    'reliability': reliability
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing bridge efficiency: {str(e)}")
            return {'score': 0, 'metrics': {}}

    async def _analyze_liquidity(self, chain_id: int) -> Dict:
        """Analyze chain liquidity"""
        try:
            chain_config = config.get_chain_config(chain_id)
            
            # Get DEX liquidity
            dex_liquidity = await self._get_dex_liquidity(chain_id)
            
            # Get lending protocol liquidity
            lending_liquidity = await self._get_lending_liquidity(chain_id)
            
            return {
                'dex': dex_liquidity,
                'lending': lending_liquidity,
                'total': sum(dex_liquidity.values()) + sum(lending_liquidity.values())
            }
            
        except Exception as e:
            logger.error(f"Error analyzing liquidity: {str(e)}")
            return {}

    def _find_liquidity_imbalances(self,
                                  source_liquidity: Dict,
                                  target_liquidity: Dict) -> List[Dict]:
        """Find liquidity imbalances between chains"""
        try:
            imbalances = []
            
            # Compare DEX liquidity
            for token, source_amount in source_liquidity['dex'].items():
                if token in target_liquidity['dex']:
                    target_amount = target_liquidity['dex'][token]
                    imbalance = abs(source_amount - target_amount) / max(source_amount, target_amount)
                    
                    if imbalance >= 0.2:  # 20% threshold
                        imbalances.append({
                            'token': token,
                            'type': 'dex',
                            'source_amount': source_amount,
                            'target_amount': target_amount,
                            'severity': imbalance
                        })
                        
            # Compare lending liquidity
            for token, source_amount in source_liquidity['lending'].items():
                if token in target_liquidity['lending']:
                    target_amount = target_liquidity['lending'][token]
                    imbalance = abs(source_amount - target_amount) / max(source_amount, target_amount)
                    
                    if imbalance >= 0.2:  # 20% threshold
                        imbalances.append({
                            'token': token,
                            'type': 'lending',
                            'source_amount': source_amount,
                            'target_amount': target_amount,
                            'severity': imbalance
                        })
                        
            return imbalances
            
        except Exception as e:
            logger.error(f"Error finding liquidity imbalances: {str(e)}")
            return []

    async def _create_arbitrage_opportunity(self,
                                          source_chain: int,
                                          target_chain: int,
                                          token: str,
                                          source_price: float,
                                          target_price: float,
                                          options: Dict) -> Optional[CrossChainOpportunity]:
        """Create arbitrage opportunity"""
        try:
            # Calculate optimal amount
            amount = self._calculate_optimal_amount(
                source_price,
                target_price,
                options
            )
            
            # Calculate gas costs
            gas_estimates = await self._estimate_gas_costs(
                source_chain,
                target_chain,
                amount,
                'arbitrage'
            )
            
            # Calculate profit
            profit = self._calculate_arbitrage_profit(
                amount,
                source_price,
                target_price,
                gas_estimates
            )
            
            if profit <= 0:
                return None
                
            # Create execution steps
            steps = self._create_arbitrage_steps(
                source_chain,
                target_chain,
                token,
                amount
            )
            
            return CrossChainOpportunity(
                source_chain_id=source_chain,
                target_chain_id=target_chain,
                opportunity_type='arbitrage',
                estimated_profit=profit,
                required_capital=amount * source_price,
                execution_steps=steps,
                risk_score=self._calculate_risk_score(steps),
                confidence_score=self._calculate_confidence_score(steps),
                gas_estimates=gas_estimates,
                bridging_routes=[],
                dependencies=[]
            )
            
        except Exception as e:
            logger.error(f"Error creating arbitrage opportunity: {str(e)}")
            return None

    async def _create_bridge_opportunity(self,
                                       source_chain: int,
                                       target_chain: int,
                                       route: Dict,
                                       efficiency: Dict,
                                       options: Dict) -> Optional[CrossChainOpportunity]:
        """Create bridge opportunity"""
        try:
            # Calculate optimal amount
            amount = self._calculate_optimal_bridge_amount(
                route,
                efficiency,
                options
            )
            
            # Calculate gas costs
            gas_estimates = await self._estimate_gas_costs(
                source_chain,
                target_chain,
                amount,
                'bridge'
            )
            
            # Calculate profit
            profit = self._calculate_bridge_profit(
                amount,
                route,
                gas_estimates
            )
            
            if profit <= 0:
                return None
                
            # Create execution steps
            steps = self._create_bridge_steps(
                source_chain,
                target_chain,
                route,
                amount
            )
            
            return CrossChainOpportunity(
                source_chain_id=source_chain,
                target_chain_id=target_chain,
                opportunity_type='bridge',
                estimated_profit=profit,
                required_capital=amount,
                execution_steps=steps,
                risk_score=self._calculate_risk_score(steps),
                confidence_score=self._calculate_confidence_score(steps),
                gas_estimates=gas_estimates,
                bridging_routes=[route],
                dependencies=[]
            )
            
        except Exception as e:
            logger.error(f"Error creating bridge opportunity: {str(e)}")
            return None

    async def _create_liquidity_opportunity(self,
                                          source_chain: int,
                                          target_chain: int,
                                          imbalance: Dict,
                                          options: Dict) -> Optional[CrossChainOpportunity]:
        """Create liquidity opportunity"""
        try:
            # Calculate optimal amount
            amount = self._calculate_optimal_liquidity_amount(
                imbalance,
                options
            )
            
            # Calculate gas costs
            gas_estimates = await self._estimate_gas_costs(
                source_chain,
                target_chain,
                amount,
                'liquidity'
            )
            
            # Calculate profit
            profit = self._calculate_liquidity_profit(
                amount,
                imbalance,
                gas_estimates
            )
            
            if profit <= 0:
                return None
                
            # Create execution steps
            steps = self._create_liquidity_steps(
                source_chain,
                target_chain,
                imbalance,
                amount
            )
            
            return CrossChainOpportunity(
                source_chain_id=source_chain,
                target_chain_id=target_chain,
                opportunity_type='liquidity',
                estimated_profit=profit,
                required_capital=amount,
                execution_steps=steps,
                risk_score=self._calculate_risk_score(steps),
                confidence_score=self._calculate_confidence_score(steps),
                gas_estimates=gas_estimates,
                bridging_routes=[],
                dependencies=[]
            )
            
        except Exception as e:
            logger.error(f"Error creating liquidity opportunity: {str(e)}")
            return None
