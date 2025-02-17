import asyncio
from typing import Dict, List, Optional
from dataclasses import dataclass
from ..utils.config import config
from ..utils.logger import logger
from ..utils.llm_interface import LLMInterface

@dataclass
class ChatMessage:
    role: str  # 'user', 'assistant', or 'system'
    content: str
    timestamp: float
    context: Optional[Dict] = None

@dataclass
class AnalysisContext:
    contract_address: str
    chain_id: int
    vulnerabilities: List[Dict]
    attack_vectors: List[Dict]
    profitability: Dict
    dependencies: List[str]
    state: Dict

class AIChatInterface:
    def __init__(self):
        self.llm = LLMInterface()
        self.conversation_history: List[ChatMessage] = []
        self.current_context: Optional[AnalysisContext] = None
        self.analysis_mode = False
        
    async def process_message(self, message: str) -> str:
        """Process user message and generate response"""
        try:
            # Add user message to history
            self.conversation_history.append(
                ChatMessage(
                    role='user',
                    content=message,
                    timestamp=asyncio.get_event_loop().time()
                )
            )
            
            # Generate response based on context
            if self.analysis_mode:
                response = await self._handle_analysis_query(message)
            else:
                response = await self._handle_general_query(message)
            
            # Add assistant response to history
            self.conversation_history.append(
                ChatMessage(
                    role='assistant',
                    content=response,
                    timestamp=asyncio.get_event_loop().time()
                )
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return "I encountered an error. Please try again."

    async def start_analysis(self, 
                           contract_address: str,
                           chain_id: int) -> str:
        """Start contract analysis mode"""
        try:
            self.analysis_mode = True
            
            # Initialize analysis context
            self.current_context = await self._initialize_analysis_context(
                contract_address,
                chain_id
            )
            
            # Generate initial analysis summary
            summary = await self._generate_analysis_summary()
            
            return f"Analysis started for contract {contract_address} on chain {chain_id}.\n\n{summary}"
            
        except Exception as e:
            logger.error(f"Error starting analysis: {str(e)}")
            return "Failed to start analysis. Please check the contract address and chain ID."

    async def _handle_analysis_query(self, query: str) -> str:
        """Handle query in analysis mode"""
        try:
            # Parse query intent
            intent = await self._parse_query_intent(query)
            
            if intent.get('type') == 'vulnerability_details':
                return await self._get_vulnerability_details(
                    intent.get('vulnerability_id')
                )
            elif intent.get('type') == 'exploit_generation':
                return await self._generate_exploit_explanation(
                    intent.get('vulnerability_id')
                )
            elif intent.get('type') == 'profitability_analysis':
                return await self._analyze_profitability(
                    intent.get('attack_vector')
                )
            elif intent.get('type') == 'mitigation_advice':
                return await self._provide_mitigation_advice(
                    intent.get('vulnerability_id')
                )
            else:
                return await self._generate_general_analysis_response(query)
                
        except Exception as e:
            logger.error(f"Error handling analysis query: {str(e)}")
            return "I encountered an error analyzing your query. Please try again."

    async def _initialize_analysis_context(self,
                                         contract_address: str,
                                         chain_id: int) -> AnalysisContext:
        """Initialize analysis context"""
        try:
            # Get vulnerability scan results
            vulnerabilities = await self._get_vulnerabilities(
                contract_address,
                chain_id
            )
            
            # Get attack vectors
            attack_vectors = await self._get_attack_vectors(vulnerabilities)
            
            # Calculate profitability
            profitability = await self._calculate_profitability(
                vulnerabilities,
                attack_vectors,
                chain_id
            )
            
            # Get dependencies
            dependencies = await self._get_dependencies(contract_address)
            
            # Get current state
            state = await self._get_contract_state(
                contract_address,
                chain_id
            )
            
            return AnalysisContext(
                contract_address=contract_address,
                chain_id=chain_id,
                vulnerabilities=vulnerabilities,
                attack_vectors=attack_vectors,
                profitability=profitability,
                dependencies=dependencies,
                state=state
            )
            
        except Exception as e:
            logger.error(f"Error initializing analysis context: {str(e)}")
            raise

    async def _generate_analysis_summary(self) -> str:
        """Generate summary of current analysis"""
        try:
            if not self.current_context:
                return "No active analysis context."
                
            # Generate summary using LLM
            summary = await self.llm.generate_analysis_summary(
                self.current_context
            )
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating analysis summary: {str(e)}")
            return "Failed to generate analysis summary."

    async def _parse_query_intent(self, query: str) -> Dict:
        """Parse user query to determine intent"""
        try:
            # Use LLM to classify query intent
            intent = await self.llm.classify_query(
                query,
                self.conversation_history,
                self.current_context
            )
            
            # Enhance intent with context
            if self.current_context:
                intent['context'] = {
                    'contract': self.current_context.contract_address,
                    'chain': self.current_context.chain_id,
                    'state': self.current_context.state
                }
            
            return intent
            
        except Exception as e:
            logger.error(f"Error parsing query intent: {str(e)}")
            return {'type': 'unknown'}

    async def _get_vulnerability_details(self, vuln_id: str) -> str:
        """Get detailed information about a specific vulnerability"""
        try:
            if not self.current_context:
                return "No active analysis context."
                
            # Find vulnerability
            vuln = next(
                (v for v in self.current_context.vulnerabilities 
                 if v['id'] == vuln_id),
                None
            )
            
            if not vuln:
                return f"Vulnerability {vuln_id} not found."
                
            # Generate detailed explanation
            details = await self.llm.explain_vulnerability(
                vuln,
                self.current_context
            )
            
            return details
            
        except Exception as e:
            logger.error(f"Error getting vulnerability details: {str(e)}")
            return "Failed to get vulnerability details."

    async def _generate_exploit_explanation(self, vuln_id: str) -> str:
        """Generate detailed exploit explanation"""
        try:
            if not self.current_context:
                return "No active analysis context."
                
            # Find vulnerability
            vuln = next(
                (v for v in self.current_context.vulnerabilities 
                 if v['id'] == vuln_id),
                None
            )
            
            if not vuln:
                return f"Vulnerability {vuln_id} not found."
                
            # Generate exploit explanation
            explanation = await self.llm.explain_exploit(
                vuln,
                self.current_context.attack_vectors,
                self.current_context.state
            )
            
            # Add profitability analysis
            profit_analysis = await self._analyze_profitability(
                vuln['attack_vectors'][0] if vuln.get('attack_vectors') else None
            )
            
            return f"{explanation}\n\nProfitability Analysis:\n{profit_analysis}"
            
        except Exception as e:
            logger.error(f"Error generating exploit explanation: {str(e)}")
            return "Failed to generate exploit explanation."

    async def _analyze_profitability(self, attack_vector: Optional[Dict]) -> str:
        """Analyze profitability of an attack vector"""
        try:
            if not self.current_context or not attack_vector:
                return "Insufficient context for profitability analysis."
                
            # Get current market conditions
            market_state = await self._get_market_state(
                self.current_context.chain_id
            )
            
            # Calculate potential profit
            profit_analysis = await self.llm.analyze_profit_potential(
                attack_vector,
                self.current_context.state,
                market_state
            )
            
            # Format analysis
            return self._format_profit_analysis(profit_analysis)
            
        except Exception as e:
            logger.error(f"Error analyzing profitability: {str(e)}")
            return "Failed to analyze profitability."

    async def _provide_mitigation_advice(self, vuln_id: str) -> str:
        """Provide mitigation advice for vulnerability"""
        try:
            if not self.current_context:
                return "No active analysis context."
                
            # Find vulnerability
            vuln = next(
                (v for v in self.current_context.vulnerabilities 
                 if v['id'] == vuln_id),
                None
            )
            
            if not vuln:
                return f"Vulnerability {vuln_id} not found."
                
            # Generate mitigation advice
            advice = await self.llm.generate_mitigation_advice(
                vuln,
                self.current_context
            )
            
            return advice
            
        except Exception as e:
            logger.error(f"Error providing mitigation advice: {str(e)}")
            return "Failed to generate mitigation advice."

    async def _get_market_state(self, chain_id: int) -> Dict:
        """Get current market state for profitability analysis"""
        try:
            # Get chain config
            chain_config = config.get_chain_config(chain_id)
            
            # Get gas prices
            gas_price = await self._get_gas_price(chain_id)
            
            # Get flash loan rates
            flash_loan_rates = await self._get_flash_loan_rates(chain_config)
            
            # Get DEX liquidity
            dex_liquidity = await self._get_dex_liquidity(chain_config)
            
            return {
                'gas_price': gas_price,
                'flash_loan_rates': flash_loan_rates,
                'dex_liquidity': dex_liquidity,
                'timestamp': asyncio.get_event_loop().time()
            }
            
        except Exception as e:
            logger.error(f"Error getting market state: {str(e)}")
            return {}

    def _format_profit_analysis(self, analysis: Dict) -> str:
        """Format profit analysis for display"""
        try:
            return f"""
Profit Analysis:
- Estimated Profit: ${analysis.get('estimated_profit', 0):,.2f}
- Required Capital: ${analysis.get('required_capital', 0):,.2f}
- Gas Costs: ${analysis.get('gas_costs', 0):,.2f}
- Flash Loan Fees: ${analysis.get('flash_loan_fees', 0):,.2f}
- Success Probability: {analysis.get('success_probability', 0)*100:.1f}%

Risk Factors:
{self._format_risk_factors(analysis.get('risk_factors', []))}

Optimal Attack Path:
{self._format_attack_path(analysis.get('optimal_path', []))}
"""
        except Exception as e:
            logger.error(f"Error formatting profit analysis: {str(e)}")
            return "Error formatting analysis."

    def _format_risk_factors(self, risk_factors: List[Dict]) -> str:
        """Format risk factors for display"""
        try:
            if not risk_factors:
                return "No risk factors identified."
                
            formatted = []
            for risk in risk_factors:
                formatted.append(
                    f"- {risk['description']} (Impact: {risk['impact']}, "
                    f"Probability: {risk['probability']*100:.1f}%)"
                )
            
            return "\n".join(formatted)
            
        except Exception as e:
            logger.error(f"Error formatting risk factors: {str(e)}")
            return "Error formatting risk factors."

    def _format_attack_path(self, path: List[Dict]) -> str:
        """Format attack path steps for display"""
        try:
            if not path:
                return "No attack path available."
                
            formatted = []
            for i, step in enumerate(path, 1):
                formatted.append(
                    f"{i}. {step['description']}\n"
                    f"   Contract: {step.get('contract', 'N/A')}\n"
                    f"   Function: {step.get('function', 'N/A')}\n"
                    f"   Expected Outcome: {step.get('outcome', 'N/A')}"
                )
            
            return "\n".join(formatted)
            
        except Exception as e:
            logger.error(f"Error formatting attack path: {str(e)}")
            return "Error formatting attack path."

    async def _get_gas_price(self, chain_id: int) -> float:
        """Get current gas price for chain"""
        try:
            # Get chain config
            chain_config = config.get_chain_config(chain_id)
            
            # Get gas price from node
            gas_price = await self.state_manager.get_gas_price(chain_id)
            
            # Convert to USD
            eth_price = await self._get_eth_price(chain_id)
            
            return gas_price * eth_price / 1e9  # Convert from Gwei to USD
            
        except Exception as e:
            logger.error(f"Error getting gas price: {str(e)}")
            return 0.0

    async def _get_flash_loan_rates(self, chain_config: 'ChainConfig') -> Dict[str, float]:
        """Get current flash loan rates from providers"""
        try:
            rates = {}
            for provider, address in chain_config.flash_loan_providers.items():
                try:
                    rate = await self.state_manager.call_function(
                        address,
                        "getFlashLoanRate()"
                    )
                    rates[provider] = float(rate) / 10000  # Convert basis points
                except:
                    continue
            return rates
            
        except Exception as e:
            logger.error(f"Error getting flash loan rates: {str(e)}")
            return {}

    async def _get_dex_liquidity(self, chain_config: 'ChainConfig') -> Dict[str, Dict]:
        """Get liquidity information from DEXes"""
        try:
            liquidity = {}
            for dex, address in chain_config.dex_addresses.items():
                try:
                    # Get total liquidity
                    total = await self.state_manager.call_function(
                        address,
                        "getTotalLiquidity()"
                    )
                    
                    # Get top pools
                    pools = await self._get_top_pools(address)
                    
                    liquidity[dex] = {
                        'total': float(total),
                        'pools': pools
                    }
                except:
                    continue
            return liquidity
            
        except Exception as e:
            logger.error(f"Error getting DEX liquidity: {str(e)}")
            return {}

    async def _get_top_pools(self, dex_address: str) -> List[Dict]:
        """Get information about top liquidity pools"""
        try:
            pools = []
            # Get pool addresses
            pool_addresses = await self.state_manager.call_function(
                dex_address,
                "getAllPools()"
            )
            
            # Get pool details
            for pool in pool_addresses[:10]:  # Top 10 pools
                try:
                    details = await self._get_pool_details(pool)
                    if details:
                        pools.append(details)
                except:
                    continue
                    
            return sorted(
                pools,
                key=lambda x: x['tvl'],
                reverse=True
            )
            
        except Exception as e:
            logger.error(f"Error getting top pools: {str(e)}")
            return []

    async def _get_eth_price(self, chain_id: int) -> float:
        """Get current ETH price in USD"""
        try:
            # Get chain config
            chain_config = config.get_chain_config(chain_id)
            
            # Get price from Chainlink oracle
            price = await self.state_manager.call_function(
                chain_config.oracle_addresses['ETH_USD'],
                "latestAnswer()"
            )
            
            return float(price) / 1e8  # Convert from oracle format
            
        except Exception as e:
            logger.error(f"Error getting ETH price: {str(e)}")
            return 0.0 