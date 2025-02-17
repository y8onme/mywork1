# Implementing LLM interface... 

import asyncio
from typing import Dict, List, Optional
from dataclasses import dataclass
import openai
from ..utils.config import config
from ..utils.logger import logger
import json
import uuid
import time

@dataclass
class LLMResponse:
    content: str
    confidence: float
    metadata: Dict
    tokens_used: int
    model: str

class LLMInterface:
    def __init__(self):
        self.config = config.get_llm_config()
        self.openai_client = openai.AsyncOpenAI(
            api_key=self.config.get('openai_api_key')
        )
        self.models = {
            'analysis': 'gpt-4',
            'classification': 'gpt-3.5-turbo',
            'generation': 'gpt-4',
            'explanation': 'gpt-4'
        }
        
    async def analyze_contract(self,
                             code: str,
                             abi: Dict,
                             chain_id: int) -> Dict:
        """Analyze contract code for vulnerabilities"""
        try:
            # Prepare context
            context = self._prepare_analysis_context(code, abi, chain_id)
            
            # Generate analysis prompt
            prompt = self._generate_analysis_prompt(context)
            
            # Get analysis from GPT-4
            response = await self._get_completion(
                prompt,
                model=self.models['analysis'],
                temperature=0.3
            )
            
            # Parse and validate findings
            findings = self._parse_analysis_response(response)
            
            return {
                'findings': findings,
                'metadata': response.metadata
            }
            
        except Exception as e:
            logger.error(f"Error in contract analysis: {str(e)}")
            return {'findings': []}

    async def classify_query(self,
                           query: str,
                           history: List[Dict],
                           context: Optional[Dict]) -> Dict:
        """Classify user query intent"""
        try:
            # Prepare classification prompt
            prompt = self._generate_classification_prompt(
                query,
                history,
                context
            )
            
            # Get classification from GPT-3.5
            response = await self._get_completion(
                prompt,
                model=self.models['classification'],
                temperature=0.1
            )
            
            # Parse classification
            intent = self._parse_classification_response(response)
            
            return intent
            
        except Exception as e:
            logger.error(f"Error classifying query: {str(e)}")
            return {'type': 'unknown'}

    async def explain_vulnerability(self,
                                  vulnerability: Dict,
                                  context: Dict) -> str:
        """Generate detailed vulnerability explanation"""
        try:
            # Prepare explanation prompt
            prompt = self._generate_vulnerability_prompt(
                vulnerability,
                context
            )
            
            # Get explanation from GPT-4
            response = await self._get_completion(
                prompt,
                model=self.models['explanation'],
                temperature=0.5
            )
            
            return response.content
            
        except Exception as e:
            logger.error(f"Error explaining vulnerability: {str(e)}")
            return "Failed to generate explanation."

    async def explain_exploit(self,
                            vulnerability: Dict,
                            attack_vectors: List[Dict],
                            state: Dict) -> str:
        """Generate exploit explanation"""
        try:
            # Prepare exploit prompt
            prompt = self._generate_exploit_prompt(
                vulnerability,
                attack_vectors,
                state
            )
            
            # Get explanation from GPT-4
            response = await self._get_completion(
                prompt,
                model=self.models['explanation'],
                temperature=0.7
            )
            
            return response.content
            
        except Exception as e:
            logger.error(f"Error explaining exploit: {str(e)}")
            return "Failed to generate exploit explanation."

    async def analyze_profit_potential(self,
                                     attack_vector: Dict,
                                     contract_state: Dict,
                                     market_state: Dict) -> Dict:
        """Analyze profit potential of attack vector"""
        try:
            # Prepare analysis prompt
            prompt = self._generate_profit_analysis_prompt(
                attack_vector,
                contract_state,
                market_state
            )
            
            # Get analysis from GPT-4
            response = await self._get_completion(
                prompt,
                model=self.models['analysis'],
                temperature=0.2
            )
            
            # Parse profit analysis
            analysis = self._parse_profit_analysis(response)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing profit potential: {str(e)}")
            return {}

    async def generate_mitigation_advice(self,
                                       vulnerability: Dict,
                                       context: Dict) -> str:
        """Generate mitigation advice"""
        try:
            # Prepare mitigation prompt
            prompt = self._generate_mitigation_prompt(
                vulnerability,
                context
            )
            
            # Get advice from GPT-4
            response = await self._get_completion(
                prompt,
                model=self.models['generation'],
                temperature=0.4
            )
            
            return response.content
            
        except Exception as e:
            logger.error(f"Error generating mitigation advice: {str(e)}")
            return "Failed to generate mitigation advice."

    async def _get_completion(self,
                            prompt: str,
                            model: str,
                            temperature: float = 0.7) -> LLMResponse:
        """Get completion from OpenAI API"""
        try:
            response = await self.openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=2000
            )
            
            return LLMResponse(
                content=response.choices[0].message.content,
                confidence=1 - temperature,
                metadata={
                    'model': model,
                    'temperature': temperature,
                    'tokens': response.usage.total_tokens
                },
                tokens_used=response.usage.total_tokens,
                model=model
            )
            
        except Exception as e:
            logger.error(f"Error getting completion: {str(e)}")
            raise 

    def _get_system_prompt(self) -> str:
        """Get system prompt for LLM"""
        return """You are an expert smart contract security researcher and exploit developer. 
        Your task is to analyze smart contracts for vulnerabilities, generate detailed exploit explanations,
        and calculate profitability of attacks. Be thorough in your analysis and precise in your explanations.
        Focus on actionable insights and practical attack vectors."""

    def _prepare_analysis_context(self, code: str, abi: Dict, chain_id: int) -> Dict:
        """Prepare context for contract analysis"""
        try:
            chain_config = config.get_chain_config(chain_id)
            return {
                'code': code,
                'abi': abi,
                'chain_id': chain_id,
                'chain_type': chain_config.chain_type,
                'flash_loan_providers': chain_config.flash_loan_providers,
                'dex_addresses': chain_config.dex_addresses,
                'lending_protocols': chain_config.lending_protocols,
                'oracle_addresses': chain_config.oracle_addresses
            }
        except Exception as e:
            logger.error(f"Error preparing analysis context: {str(e)}")
            return {}

    def _generate_analysis_prompt(self, context: Dict) -> str:
        """Generate prompt for contract analysis"""
        return f"""Analyze the following smart contract for security vulnerabilities:

Contract Code:
{context['code']}

ABI:
{context['abi']}

Chain Context:
- Chain ID: {context['chain_id']}
- Chain Type: {context['chain_type']}
- Available Flash Loan Providers: {list(context['flash_loan_providers'].keys())}
- Available DEXes: {list(context['dex_addresses'].keys())}
- Available Lending Protocols: {list(context['lending_protocols'].keys())}

Focus on:
1. Critical vulnerabilities that could lead to loss of funds
2. Flash loan attack vectors
3. Price manipulation opportunities
4. Governance vulnerabilities
5. Cross-contract dependencies
6. Oracle manipulation vectors
7. Access control issues
8. Reentrancy vulnerabilities
9. Integer overflow/underflow risks
10. Logic errors and edge cases

For each vulnerability found, provide:
1. Detailed description
2. Severity (0-1 scale)
3. Confidence score
4. Attack vector description
5. Potential impact
6. Required conditions
7. Estimated profitability
8. Possible mitigations

Format your response as a JSON object."""

    def _parse_analysis_response(self, response: LLMResponse) -> List[Dict]:
        """Parse and validate analysis response"""
        try:
            # Parse JSON response
            findings = json.loads(response.content)
            
            # Validate and normalize findings
            validated = []
            for finding in findings:
                if self._validate_finding(finding):
                    normalized = self._normalize_finding(finding)
                    validated.append(normalized)
            
            return validated
            
        except Exception as e:
            logger.error(f"Error parsing analysis response: {str(e)}")
            return []

    def _generate_exploit_prompt(self,
                               vulnerability: Dict,
                               attack_vectors: List[Dict],
                               state: Dict) -> str:
        """Generate prompt for exploit explanation"""
        return f"""Generate a detailed exploit explanation for the following vulnerability:

Vulnerability:
{json.dumps(vulnerability, indent=2)}

Available Attack Vectors:
{json.dumps(attack_vectors, indent=2)}

Current Contract State:
{json.dumps(state, indent=2)}

Provide:
1. Step-by-step exploit process
2. Required setup and conditions
3. Code snippets for key steps
4. Gas optimization suggestions
5. Risk factors and potential failure points
6. Estimated success probability
7. Required tools and dependencies
8. Testing methodology

Format the response as a detailed technical document."""

    def _generate_profit_analysis_prompt(self,
                                       attack_vector: Dict,
                                       contract_state: Dict,
                                       market_state: Dict) -> str:
        """Generate prompt for profit analysis"""
        return f"""Analyze the profitability of the following attack vector:

Attack Vector:
{json.dumps(attack_vector, indent=2)}

Contract State:
{json.dumps(contract_state, indent=2)}

Market Conditions:
{json.dumps(market_state, indent=2)}

Calculate:
1. Potential profit in USD
2. Required initial capital
3. Gas costs (consider current prices)
4. Flash loan fees if applicable
5. Success probability
6. Risk factors
7. Market impact
8. Optimal execution path
9. Alternative profitable variations

Format response as a JSON object with detailed calculations."""

    def _parse_profit_analysis(self, response: LLMResponse) -> Dict:
        """Parse profit analysis response"""
        try:
            # Parse JSON response
            analysis = json.loads(response.content)
            
            # Validate required fields
            required_fields = [
                'estimated_profit',
                'required_capital',
                'gas_costs',
                'flash_loan_fees',
                'success_probability'
            ]
            
            if not all(field in analysis for field in required_fields):
                raise ValueError("Missing required fields in profit analysis")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error parsing profit analysis: {str(e)}")
            return {
                'estimated_profit': 0,
                'required_capital': 0,
                'gas_costs': 0,
                'flash_loan_fees': 0,
                'success_probability': 0
            }

    def _validate_finding(self, finding: Dict) -> bool:
        """Validate vulnerability finding"""
        required_fields = [
            'description',
            'severity',
            'confidence',
            'attack_vectors',
            'impact',
            'conditions',
            'profitability',
            'mitigations'
        ]
        
        return all(field in finding for field in required_fields)

    def _normalize_finding(self, finding: Dict) -> Dict:
        """Normalize vulnerability finding format"""
        return {
            'id': str(uuid.uuid4()),
            'description': finding['description'],
            'severity': float(finding['severity']),
            'confidence': float(finding['confidence']),
            'attack_vectors': finding['attack_vectors'],
            'impact': finding['impact'],
            'conditions': finding['conditions'],
            'profitability': finding['profitability'],
            'mitigations': finding['mitigations'],
            'timestamp': time.time()
        }

    def _generate_classification_prompt(self,
                                      query: str,
                                      history: List[Dict],
                                      context: Optional[Dict]) -> str:
        """Generate prompt for query classification"""
        return f"""Classify the following user query in the context of smart contract security analysis:

Query: {query}

Chat History:
{json.dumps(history[-5:], indent=2)}  # Last 5 messages for context

Analysis Context:
{json.dumps(context, indent=2) if context else "No active analysis"}

Classify the query into one of these categories:
1. vulnerability_details - User wants details about a specific vulnerability
2. exploit_generation - User wants to understand how to exploit a vulnerability
3. profitability_analysis - User wants to analyze attack profitability
4. mitigation_advice - User wants advice on fixing vulnerabilities
5. general_question - General security-related question
6. chain_specific - Chain-specific security question
7. tool_usage - Question about security tools
8. market_conditions - Question about market conditions affecting exploits

Return a JSON object with:
1. type: The classification category
2. confidence: Confidence score (0-1)
3. parameters: Any relevant parameters (e.g., vulnerability_id)
4. context_requirements: Additional context needed"""

    def _generate_vulnerability_prompt(self,
                                     vulnerability: Dict,
                                     context: Dict) -> str:
        """Generate prompt for vulnerability explanation"""
        return f"""Explain the following smart contract vulnerability in detail:

Vulnerability:
{json.dumps(vulnerability, indent=2)}

Contract Context:
{json.dumps(context, indent=2)}

Provide:
1. Technical explanation of the vulnerability
2. How it can be identified
3. Why it's dangerous
4. Real-world examples if any
5. Common variations
6. Detection methods
7. Verification steps
8. Impact assessment
9. Chain-specific considerations
10. Related vulnerabilities

Format the response as a detailed technical document with markdown formatting."""

    def _generate_mitigation_prompt(self,
                                  vulnerability: Dict,
                                  context: Dict) -> str:
        """Generate prompt for mitigation advice"""
        return f"""Provide detailed mitigation strategies for the following vulnerability:

Vulnerability:
{json.dumps(vulnerability, indent=2)}

Contract Context:
{json.dumps(context, indent=2)}

Provide:
1. Immediate actions to take
2. Code-level fixes with examples
3. Best practices to implement
4. Testing strategies to verify fixes
5. Monitoring recommendations
6. Long-term security improvements
7. Chain-specific considerations
8. Impact on existing functionality
9. Deployment considerations
10. Additional security measures

Include code snippets where relevant and explain any trade-offs.
Format the response as a detailed technical document with markdown formatting."""

    async def generate_attack_simulation(self,
                                       vulnerability: Dict,
                                       chain_id: int,
                                       options: Optional[Dict] = None) -> Dict:
        """Generate complete attack simulation"""
        try:
            # Get chain configuration
            chain_config = config.get_chain_config(chain_id)
            
            # Generate simulation steps
            simulation = await self._create_attack_simulation(
                vulnerability,
                chain_config,
                options
            )
            
            # Generate test scripts
            test_scripts = await self._generate_test_scripts(
                simulation,
                chain_config
            )
            
            # Calculate success metrics
            metrics = await self._calculate_simulation_metrics(simulation)
            
            return {
                'simulation': simulation,
                'test_scripts': test_scripts,
                'metrics': metrics,
                'requirements': self._get_simulation_requirements(simulation)
            }
            
        except Exception as e:
            logger.error(f"Error generating attack simulation: {str(e)}")
            return {}

    async def _create_attack_simulation(self,
                                      vulnerability: Dict,
                                      chain_config: 'ChainConfig',
                                      options: Optional[Dict]) -> Dict:
        """Create detailed attack simulation"""
        try:
            # Generate simulation prompt
            prompt = self._generate_simulation_prompt(
                vulnerability,
                chain_config,
                options
            )
            
            # Get simulation from GPT-4
            response = await self._get_completion(
                prompt,
                model=self.models['generation'],
                temperature=0.4
            )
            
            # Parse and validate simulation
            simulation = self._parse_simulation_response(response)
            
            return simulation
            
        except Exception as e:
            logger.error(f"Error creating attack simulation: {str(e)}")
            return {}

    def _generate_simulation_prompt(self,
                                  vulnerability: Dict,
                                  chain_config: 'ChainConfig',
                                  options: Optional[Dict]) -> str:
        """Generate prompt for attack simulation"""
        return f"""Create a detailed attack simulation for the following vulnerability:

Vulnerability:
{json.dumps(vulnerability, indent=2)}

Chain Configuration:
{json.dumps(chain_config.to_dict(), indent=2)}

Options:
{json.dumps(options, indent=2) if options else "Default options"}

Generate a complete attack simulation including:
1. Initial setup requirements
2. Contract deployment steps
3. State manipulation requirements
4. Transaction sequence
5. Required balances and approvals
6. Flash loan integration details
7. MEV considerations
8. Gas optimization strategies
9. Error handling
10. Validation checks

For each step, provide:
1. Detailed description
2. Required code
3. Expected outcome
4. Potential failure points
5. Alternative approaches
6. Success criteria

Format the response as a JSON object with full technical details."""

    def _parse_simulation_response(self, response: LLMResponse) -> Dict:
        """Parse and validate simulation response"""
        try:
            simulation = json.loads(response.content)
            
            # Validate simulation structure
            required_sections = [
                'setup',
                'steps',
                'validation',
                'requirements',
                'alternatives'
            ]
            
            if not all(section in simulation for section in required_sections):
                raise ValueError("Invalid simulation structure")
            
            # Normalize and enhance simulation
            enhanced = self._enhance_simulation(simulation)
            
            return enhanced
            
        except Exception as e:
            logger.error(f"Error parsing simulation: {str(e)}")
            return {}

    def _enhance_simulation(self, simulation: Dict) -> Dict:
        """Enhance simulation with additional details"""
        try:
            # Add execution metadata
            simulation['metadata'] = {
                'id': str(uuid.uuid4()),
                'timestamp': time.time(),
                'version': '1.0'
            }
            
            # Add gas estimates
            simulation['gas_estimates'] = self._estimate_gas_usage(
                simulation['steps']
            )
            
            # Add risk assessment
            simulation['risk_assessment'] = self._assess_simulation_risks(
                simulation
            )
            
            # Add monitoring points
            simulation['monitoring'] = self._generate_monitoring_points(
                simulation
            )
            
            return simulation
            
        except Exception as e:
            logger.error(f"Error enhancing simulation: {str(e)}")
            return simulation

    def _parse_classification_response(self, response: LLMResponse) -> Dict:
        """Parse classification response"""
        try:
            # Parse JSON response
            intent = json.loads(response.content)
            
            # Validate required fields
            required_fields = ['type', 'confidence', 'parameters', 'context_requirements']
            
            if not all(field in intent for field in required_fields):
                raise ValueError("Missing required fields in classification response")
            
            return intent
            
        except Exception as e:
            logger.error(f"Error parsing classification response: {str(e)}")
            return {'type': 'unknown'}

    def _get_simulation_requirements(self, simulation: Dict) -> Dict:
        """Get simulation requirements"""
        try:
            # Extract requirements from simulation
            requirements = {
                'setup': simulation['setup'],
                'steps': simulation['steps'],
                'validation': simulation['validation'],
                'requirements': simulation['requirements'],
                'alternatives': simulation['alternatives']
            }
            
            return requirements
            
        except Exception as e:
            logger.error(f"Error getting simulation requirements: {str(e)}")
            return {}

    def _calculate_simulation_metrics(self, simulation: Dict) -> Dict:
        """Calculate simulation metrics"""
        try:
            # Extract metrics from simulation
            metrics = {
                'success_probability': simulation['success_probability'],
                'risk_level': simulation['risk_assessment']['level'],
                'estimated_profit': simulation['estimated_profit'],
                'required_capital': simulation['required_capital'],
                'gas_costs': simulation['gas_estimates']['total'],
                'flash_loan_fees': simulation['flash_loan_fees'],
                'market_impact': simulation['risk_assessment']['market_impact'],
                'execution_time': simulation['gas_estimates']['total_time'],
                'validation_success': simulation['validation']['success'],
                'validation_time': simulation['validation']['time']
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating simulation metrics: {str(e)}")
            return {}

    def _estimate_gas_usage(self, steps: List[Dict]) -> Dict:
        """Estimate gas usage for a list of steps"""
        try:
            # Calculate total gas usage
            total_gas = sum(step['gas_cost'] for step in steps)
            
            # Calculate total execution time
            total_time = sum(step['execution_time'] for step in steps)
            
            return {
                'total': total_gas,
                'total_time': total_time
            }
            
        except Exception as e:
            logger.error(f"Error estimating gas usage: {str(e)}")
            return {}

    def _assess_simulation_risks(self, simulation: Dict) -> Dict:
        """Assess simulation risks"""
        try:
            # Extract risk factors from simulation
            risk_factors = simulation['risk_assessment']['factors']
            
            # Calculate risk level
            level = sum(risk['severity'] for risk in risk_factors) / len(risk_factors)
            
            # Calculate market impact
            market_impact = simulation['risk_assessment']['market_impact']
            
            return {
                'level': level,
                'market_impact': market_impact
            }
            
        except Exception as e:
            logger.error(f"Error assessing simulation risks: {str(e)}")
            return {}

    def _generate_monitoring_points(self, simulation: Dict) -> List[Dict]:
        """Generate monitoring points for simulation"""
        try:
            # Extract monitoring points from simulation
            monitoring_points = simulation['monitoring']
            
            return monitoring_points
            
        except Exception as e:
            logger.error(f"Error generating monitoring points: {str(e)}")
            return []

    def _generate_test_scripts(self, simulation: Dict, chain_config: 'ChainConfig') -> List[Dict]:
        """Generate test scripts for simulation"""
        try:
            # Extract test scripts from simulation
            test_scripts = simulation['test_scripts']
            
            # Enhance test scripts with chain-specific details
            enhanced_scripts = []
            for script in test_scripts:
                enhanced_script = self._enhance_test_script(script, chain_config)
                enhanced_scripts.append(enhanced_script)
            
            return enhanced_scripts
            
        except Exception as e:
            logger.error(f"Error generating test scripts: {str(e)}")
            return []

    def _enhance_test_script(self, script: Dict, chain_config: 'ChainConfig') -> Dict:
        """Enhance test script with chain-specific details"""
        try:
            # Add chain-specific details to script
            script['chain_specific'] = {
                'chain_id': chain_config.chain_id,
                'chain_type': chain_config.chain_type,
                'flash_loan_providers': list(chain_config.flash_loan_providers.keys()),
                'dex_addresses': list(chain_config.dex_addresses.keys()),
                'lending_protocols': list(chain_config.lending_protocols.keys()),
                'oracle_addresses': list(chain_config.oracle_addresses.keys())
            }
            
            return script
            
        except Exception as e:
            logger.error(f"Error enhancing test script: {str(e)}")
            return script 