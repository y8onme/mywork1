# src/utils/calculators/profit_analyzer.py

import asyncio
from typing import Dict, List, Optional, Union
from decimal import Decimal
from dataclasses import dataclass
from ..config import config
from ..logger import logger
from .profit_calculator import ProfitCalculator, ProfitResult

@dataclass
class ProfitAnalysis:
    chain_id: int
    total_opportunities: int
    best_opportunity: Dict
    estimated_profits: List[ProfitResult]
    risk_assessment: Dict
    execution_timeline: List[Dict]
    gas_optimization: Dict
    confidence_metrics: Dict
    chain_specific_factors: Dict

class ProfitAnalyzer:
    def __init__(self):
        self.profit_calculator = ProfitCalculator()
        
    async def analyze_opportunities(self,
                                  opportunities: List[Dict],
                                  chain_id: int,
                                  options: Optional[Dict] = None) -> ProfitAnalysis:
        """Analyze multiple profit opportunities"""
        try:
            options = options or {}
            chain_config = config.get_chain_config(chain_id)
            
            # Calculate profits for each opportunity
            profit_results = []
            for opp in opportunities:
                result = await self.profit_calculator.calculate_profit(
                    opp['transactions'],
                    chain_id,
                    options
                )
                profit_results.append(result)
            
            # Sort by net profit
            profit_results.sort(key=lambda x: x.net_profit, reverse=True)
            
            # Find best opportunity
            best_opp = self._identify_best_opportunity(profit_results, options)
            
            # Analyze risks
            risk_assessment = await self._assess_risks(profit_results, chain_id)
            
            # Create execution timeline
            timeline = self._create_execution_timeline(profit_results)
            
            # Optimize gas usage
            gas_optimization = await self._optimize_gas_usage(profit_results, chain_id)
            
            # Calculate confidence metrics
            confidence_metrics = self._calculate_confidence_metrics(profit_results)
            
            # Analyze chain-specific factors
            chain_factors = await self._analyze_chain_factors(chain_id, profit_results)
            
            return ProfitAnalysis(
                chain_id=chain_id,
                total_opportunities=len(profit_results),
                best_opportunity=best_opp,
                estimated_profits=profit_results,
                risk_assessment=risk_assessment,
                execution_timeline=timeline,
                gas_optimization=gas_optimization,
                confidence_metrics=confidence_metrics,
                chain_specific_factors=chain_factors
            )
            
        except Exception as e:
            logger.error(f"Error in profit analysis: {str(e)}")
            raise

    def _identify_best_opportunity(self,
                                 results: List[ProfitResult],
                                 options: Dict) -> Dict:
        """Identify the best profit opportunity"""
        try:
            if not results:
                return {}
                
            # Get minimum profit threshold
            min_profit = Decimal(str(options.get('min_profit', '0.1')))
            max_risk = float(options.get('max_risk', 0.8))
            
            # Filter viable opportunities
            viable_results = [
                r for r in results
                if r.net_profit >= min_profit and r.risk_score <= max_risk
            ]
            
            if not viable_results:
                return {}
                
            # Score each opportunity
            scored_results = []
            for result in viable_results:
                score = self._calculate_opportunity_score(result)
                scored_results.append((score, result))
                
            # Get best opportunity
            best_result = max(scored_results, key=lambda x: x[0])[1]
            
            return {
                'profit_result': best_result,
                'score': score,
                'execution_priority': 'high',
                'optimization_suggestions': self._get_optimization_suggestions(best_result)
            }
            
        except Exception as e:
            logger.error(f"Error identifying best opportunity: {str(e)}")
            return {}

    async def _assess_risks(self,
                          results: List[ProfitResult],
                          chain_id: int) -> Dict:
        """Assess risks for profit opportunities"""
        try:
            chain_config = config.get_chain_config(chain_id)
            
            risk_factors = {
                'high_risk_count': 0,
                'medium_risk_count': 0,
                'low_risk_count': 0,
                'risk_factors': [],
                'mitigation_suggestions': []
            }
            
            for result in results:
                # Categorize risk
                if result.risk_score >= 0.7:
                    risk_factors['high_risk_count'] += 1
                elif result.risk_score >= 0.4:
                    risk_factors['medium_risk_count'] += 1
                else:
                    risk_factors['low_risk_count'] += 1
                    
                # Analyze specific risk factors
                factors = await self._analyze_risk_factors(result, chain_id)
                risk_factors['risk_factors'].extend(factors)
                
                # Get mitigation suggestions
                suggestions = self._get_risk_mitigation_suggestions(factors)
                risk_factors['mitigation_suggestions'].extend(suggestions)
                
            return risk_factors
            
        except Exception as e:
            logger.error(f"Error assessing risks: {str(e)}")
            return {}

    def _create_execution_timeline(self,
                                 results: List[ProfitResult]) -> List[Dict]:
        """Create execution timeline for opportunities"""
        try:
            timeline = []
            current_time = 0
            
            for result in results:
                # Estimate execution time
                execution_time = self._estimate_execution_time(result)
                
                timeline.append({
                    'start_time': current_time,
                    'duration': execution_time,
                    'profit_result': result,
                    'dependencies': self._get_execution_dependencies(result),
                    'parallel_execution': self._can_execute_parallel(result)
                })
                
                current_time += execution_time
                
            return timeline
            
        except Exception as e:
            logger.error(f"Error creating timeline: {str(e)}")
            return []

    async def _optimize_gas_usage(self,
                                results: List[ProfitResult],
                                chain_id: int) -> Dict:
        """Optimize gas usage for opportunities"""
        try:
            chain_config = config.get_chain_config(chain_id)
            
            optimization = {
                'total_gas_saved': 0,
                'optimizations': [],
                'suggestions': []
            }
            
            for result in results:
                # Find gas optimization opportunities
                gas_opts = await self._find_gas_optimizations(result, chain_id)
                
                optimization['optimizations'].extend(gas_opts)
                optimization['total_gas_saved'] += sum(
                    opt['gas_saved'] for opt in gas_opts
                )
                
                # Generate optimization suggestions
                suggestions = self._generate_gas_suggestions(gas_opts)
                optimization['suggestions'].extend(suggestions)
                
            return optimization
            
        except Exception as e:
            logger.error(f"Error optimizing gas usage: {str(e)}")
            return {}

    def _calculate_confidence_metrics(self,
                                   results: List[ProfitResult]) -> Dict:
        """Calculate confidence metrics for opportunities"""
        try:
            metrics = {
                'average_confidence': 0,
                'confidence_distribution': {
                    'high': 0,
                    'medium': 0,
                    'low': 0
                },
                'reliability_factors': []
            }
            
            total_confidence = 0
            for result in results:
                total_confidence += result.confidence_score
                
                # Categorize confidence
                if result.confidence_score >= 0.7:
                    metrics['confidence_distribution']['high'] += 1
                elif result.confidence_score >= 0.4:
                    metrics['confidence_distribution']['medium'] += 1
                else:
                    metrics['confidence_distribution']['low'] += 1
                    
                # Analyze reliability factors
                factors = self._analyze_reliability_factors(result)
                metrics['reliability_factors'].extend(factors)
                
            if results:
                metrics['average_confidence'] = total_confidence / len(results)
                
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating confidence metrics: {str(e)}")
            return {}

    async def _analyze_chain_factors(self,
                                   chain_id: int,
                                   results: List[ProfitResult]) -> Dict:
        """Analyze chain-specific factors"""
        try:
            chain_config = config.get_chain_config(chain_id)
            
            factors = {
                'block_time': chain_config.block_time,
                'gas_price_impact': await self._analyze_gas_price_impact(chain_id),
                'liquidity_factors': await self._analyze_liquidity_factors(chain_id),
                'network_congestion': await self._get_network_congestion(chain_id),
                'chain_specific_risks': self._get_chain_specific_risks(chain_id)
            }
            
            return factors
            
        except Exception as e:
            logger.error(f"Error analyzing chain factors: {str(e)}")
            return {}

    def _calculate_opportunity_score(self, result: ProfitResult) -> float:
        """Calculate comprehensive opportunity score"""
        try:
            # Base score from profit
            score = float(result.net_profit) * 0.4
            
            # Adjust for risk
            risk_factor = 1 - result.risk_score
            score *= risk_factor
            
            # Adjust for confidence
            score *= result.confidence_score
            
            # Adjust for execution time
            if result.execution_time > 0:
                time_factor = min(1.0, 5.0 / result.execution_time)
                score *= time_factor
                
            return score
            
        except Exception as e:
            logger.error(f"Error calculating opportunity score: {str(e)}")
            return 0.0

    async def _analyze_risk_factors(self,
                                  result: ProfitResult,
                                  chain_id: int) -> List[Dict]:
        """Analyze specific risk factors"""
        # Implementation for risk factor analysis
        return []

    def _get_risk_mitigation_suggestions(self,
                                       risk_factors: List[Dict]) -> List[str]:
        """Get risk mitigation suggestions"""
        # Implementation for risk mitigation suggestions
        return []

    def _estimate_execution_time(self, result: ProfitResult) -> float:
        """Estimate execution time for opportunity"""
        # Implementation for execution time estimation
        return 0.0

    def _get_execution_dependencies(self, result: ProfitResult) -> List[str]:
        """Get execution dependencies"""
        # Implementation for getting dependencies
        return []

    def _can_execute_parallel(self, result: ProfitResult) -> bool:
        """Check if opportunity can be executed in parallel"""
        # Implementation for parallel execution check
        return False

    async def _find_gas_optimizations(self,
                                    result: ProfitResult,
                                    chain_id: int) -> List[Dict]:
        """Find gas optimization opportunities"""
        # Implementation for gas optimization
        return []

    def _generate_gas_suggestions(self,
                                optimizations: List[Dict]) -> List[str]:
        """Generate gas optimization suggestions"""
        # Implementation for gas suggestions
        return []

    def _analyze_reliability_factors(self,
                                   result: ProfitResult) -> List[Dict]:
        """Analyze reliability factors"""
        # Implementation for reliability analysis
        return []

    async def _analyze_gas_price_impact(self, chain_id: int) -> Dict:
        """Analyze gas price impact"""
        # Implementation for gas price impact analysis
        return {}

    async def _analyze_liquidity_factors(self, chain_id: int) -> Dict:
        """Analyze liquidity factors"""
        # Implementation for liquidity analysis
        return {}

    async def _get_network_congestion(self, chain_id: int) -> Dict:
        """Get network congestion metrics"""
        # Implementation for network congestion analysis
        return {}

    def _get_chain_specific_risks(self, chain_id: int) -> List[Dict]:
        """Get chain-specific risks"""
        # Implementation for chain-specific risks
        return []

    def _get_optimization_suggestions(self,
                                    result: ProfitResult) -> List[str]:
        """Get optimization suggestions"""
        # Implementation for optimization suggestions
        return []