# src/core/analyzers/protocol_analyzer.py

import asyncio
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from ...utils.config import config
from ...utils.logger import logger
from ...utils.state.state_manager import StateManager

@dataclass
class ProtocolMetrics:
    tvl: float
    daily_volume: float
    user_count: int
    transaction_count: int
    fee_revenue: float
    token_price: Optional[float]
    market_cap: Optional[float]

@dataclass
class ProtocolAnalysis:
    protocol_address: str
    chain_id: int
    protocol_type: str
    metrics: ProtocolMetrics
    dependencies: List[str]
    integrations: List[Dict]
    risk_factors: Dict
    market_position: Dict
    competitive_analysis: Dict
    timestamp: float

class ProtocolAnalyzer:
    def __init__(self):
        self.state_manager = StateManager()
        self.analyzed_protocols: Set[str] = set()
        self.analysis_history: Dict[str, List[ProtocolAnalysis]] = {}
        
    async def analyze_protocol(self,
                             protocol_address: str,
                             chain_id: int,
                             options: Optional[Dict] = None) -> Optional[ProtocolAnalysis]:
        """Analyze protocol characteristics and behavior"""
        try:
            start_time = asyncio.get_event_loop().time()
            options = options or {}
            
            # Get protocol state
            state = await self.state_manager.get_state(chain_id)
            protocol_state = state.protocol_states.get(protocol_address, {})
            
            # Determine protocol type
            protocol_type = await self._determine_protocol_type(
                protocol_address,
                chain_id
            )
            
            # Get protocol metrics
            metrics = await self._get_protocol_metrics(
                protocol_address,
                chain_id
            )
            
            # Analyze dependencies
            dependencies = await self._analyze_dependencies(
                protocol_address,
                chain_id
            )
            
            # Analyze integrations
            integrations = await self._analyze_integrations(
                protocol_address,
                chain_id
            )
            
            # Assess risk factors
            risk_factors = await self._assess_risk_factors(
                protocol_address,
                chain_id,
                metrics,
                dependencies
            )
            
            # Analyze market position
            market_position = await self._analyze_market_position(
                protocol_address,
                chain_id,
                metrics
            )
            
            # Analyze competition
            competitive_analysis = await self._analyze_competition(
                protocol_address,
                chain_id,
                protocol_type
            )
            
            analysis = ProtocolAnalysis(
                protocol_address=protocol_address,
                chain_id=chain_id,
                protocol_type=protocol_type,
                metrics=metrics,
                dependencies=dependencies,
                integrations=integrations,
                risk_factors=risk_factors,
                market_position=market_position,
                competitive_analysis=competitive_analysis,
                timestamp=start_time
            )
            
            # Update history
            self._update_analysis_history(analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing protocol: {str(e)}")
            return None

    async def _determine_protocol_type(self,
                                     protocol_address: str,
                                     chain_id: int) -> str:
        """Determine protocol type based on behavior"""
        try:
            chain_config = config.get_chain_config(chain_id)
            
            # Check known protocol addresses
            if protocol_address in chain_config.dex_addresses.values():
                return 'dex'
            elif protocol_address in chain_config.lending_protocols.values():
                return 'lending'
            elif protocol_address in chain_config.flash_loan_providers.values():
                return 'flash_loan'
                
            # Analyze contract behavior
            contract = await self._get_contract(protocol_address, chain_id)
            functions = await self._get_contract_functions(contract)
            
            # Determine type from functions
            if self._has_dex_functions(functions):
                return 'dex'
            elif self._has_lending_functions(functions):
                return 'lending'
            elif self._has_flash_loan_functions(functions):
                return 'flash_loan'
                
            return 'unknown'
            
        except Exception as e:
            logger.error(f"Error determining protocol type: {str(e)}")
            return 'unknown'

    async def _get_protocol_metrics(self,
                                  protocol_address: str,
                                  chain_id: int) -> ProtocolMetrics:
        """Get protocol metrics"""
        try:
            # Get TVL
            tvl = await self._get_tvl(protocol_address, chain_id)
            
            # Get volume
            volume = await self._get_daily_volume(protocol_address, chain_id)
            
            # Get user count
            users = await self._get_user_count(protocol_address, chain_id)
            
            # Get transaction count
            transactions = await self._get_transaction_count(
                protocol_address,
                chain_id
            )
            
            # Get fee revenue
            revenue = await self._get_fee_revenue(protocol_address, chain_id)
            
            # Get token metrics
            token_metrics = await self._get_token_metrics(
                protocol_address,
                chain_id
            )
            
            return ProtocolMetrics(
                tvl=tvl,
                daily_volume=volume,
                user_count=users,
                transaction_count=transactions,
                fee_revenue=revenue,
                token_price=token_metrics.get('price'),
                market_cap=token_metrics.get('market_cap')
            )
            
        except Exception as e:
            logger.error(f"Error getting protocol metrics: {str(e)}")
            return ProtocolMetrics(0, 0, 0, 0, 0, None, None)

    async def _analyze_dependencies(self,
                                  protocol_address: str,
                                  chain_id: int) -> List[str]:
        """Analyze protocol dependencies"""
        try:
            dependencies = set()
            
            # Get contract dependencies
            contract_deps = await self._get_contract_dependencies(
                protocol_address,
                chain_id
            )
            dependencies.update(contract_deps)
            
            # Get oracle dependencies
            oracle_deps = await self._get_oracle_dependencies(
                protocol_address,
                chain_id
            )
            dependencies.update(oracle_deps)
            
            # Get token dependencies
            token_deps = await self._get_token_dependencies(
                protocol_address,
                chain_id
            )
            dependencies.update(token_deps)
            
            return list(dependencies)
            
        except Exception as e:
            logger.error(f"Error analyzing dependencies: {str(e)}")
            return []

    async def _analyze_integrations(self,
                                  protocol_address: str,
                                  chain_id: int) -> List[Dict]:
        """Analyze protocol integrations"""
        try:
            integrations = []
            
            # Get DEX integrations
            dex_integrations = await self._get_dex_integrations(
                protocol_address,
                chain_id
            )
            integrations.extend(dex_integrations)
            
            # Get lending integrations
            lending_integrations = await self._get_lending_integrations(
                protocol_address,
                chain_id
            )
            integrations.extend(lending_integrations)
            
            # Get bridge integrations
            bridge_integrations = await self._get_bridge_integrations(
                protocol_address,
                chain_id
            )
            integrations.extend(bridge_integrations)
            
            return integrations
            
        except Exception as e:
            logger.error(f"Error analyzing integrations: {str(e)}")
            return []

    async def _assess_risk_factors(self,
                                 protocol_address: str,
                                 chain_id: int,
                                 metrics: ProtocolMetrics,
                                 dependencies: List[str]) -> Dict:
        """Assess protocol risk factors"""
        try:
            # Assess centralization risks
            centralization_risks = self._assess_centralization(
                protocol_address,
                chain_id
            )
            
            # Assess economic risks
            economic_risks = self._assess_economic_risks(metrics)
            
            # Assess technical risks
            technical_risks = await self._assess_technical_risks(
                protocol_address,
                chain_id,
                dependencies
            )
            
            # Calculate overall risk score
            risk_score = self._calculate_risk_score(
                centralization_risks,
                economic_risks,
                technical_risks
            )
            
            return {
                'risk_score': risk_score,
                'centralization_risks': centralization_risks,
                'economic_risks': economic_risks,
                'technical_risks': technical_risks,
                'risk_factors': self._identify_risk_factors(
                    centralization_risks,
                    economic_risks,
                    technical_risks
                )
            }
            
        except Exception as e:
            logger.error(f"Error assessing risk factors: {str(e)}")
            return {'risk_score': 1.0}

    def _update_analysis_history(self, analysis: ProtocolAnalysis):
        """Update analysis history"""
        try:
            key = f"{analysis.protocol_address}_{analysis.chain_id}"
            
            if key not in self.analysis_history:
                self.analysis_history[key] = []
                
            self.analysis_history[key].append(analysis)
            
            # Limit history size
            if len(self.analysis_history[key]) > 10:
                self.analysis_history[key] = self.analysis_history[key][-10:]
                
        except Exception as e:
            logger.error(f"Error updating analysis history: {str(e)}")
