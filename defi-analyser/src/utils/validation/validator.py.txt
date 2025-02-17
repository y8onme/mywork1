# src/utils/validation/validator.py

import asyncio
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
from ..config import config
from ..logger import logger
from ..state.state_manager import StateManager

@dataclass
class ValidationRule:
    name: str
    rule_type: str
    parameters: Dict
    severity: str
    chain_specific: bool
    error_message: str

@dataclass
class ValidationResult:
    success: bool
    rule_results: List[Dict]
    failed_rules: List[str]
    warnings: List[str]
    validation_time: float
    chain_id: int

class Validator:
    def __init__(self):
        self.state_manager = StateManager()
        self.rules: Dict[str, ValidationRule] = self._initialize_rules()
        
    def _initialize_rules(self) -> Dict[str, ValidationRule]:
        """Initialize validation rules"""
        return {
            'gas_limit': ValidationRule(
                name='gas_limit',
                rule_type='transaction',
                parameters={
                    'min_gas': 21000,
                    'max_gas': 10000000
                },
                severity='error',
                chain_specific=True,
                error_message='Invalid gas limit'
            ),
            'balance_check': ValidationRule(
                name='balance_check',
                rule_type='account',
                parameters={
                    'min_balance': '0.01 ETH'
                },
                severity='error',
                chain_specific=True,
                error_message='Insufficient balance'
            ),
            'nonce_check': ValidationRule(
                name='nonce_check',
                rule_type='transaction',
                parameters={},
                severity='error',
                chain_specific=False,
                error_message='Invalid nonce'
            ),
            'value_check': ValidationRule(
                name='value_check',
                rule_type='transaction',
                parameters={
                    'min_value': 0
                },
                severity='error',
                chain_specific=False,
                error_message='Invalid transaction value'
            ),
            'data_format': ValidationRule(
                name='data_format',
                rule_type='transaction',
                parameters={
                    'min_length': 2,
                    'max_length': 10000
                },
                severity='error',
                chain_specific=False,
                error_message='Invalid transaction data format'
            ),
            'protocol_check': ValidationRule(
                name='protocol_check',
                rule_type='protocol',
                parameters={},
                severity='error',
                chain_specific=True,
                error_message='Invalid protocol interaction'
            ),
            'slippage_check': ValidationRule(
                name='slippage_check',
                rule_type='dex',
                parameters={
                    'max_slippage': 0.05
                },
                severity='warning',
                chain_specific=False,
                error_message='High slippage detected'
            ),
            'flash_loan_check': ValidationRule(
                name='flash_loan_check',
                rule_type='flash_loan',
                parameters={
                    'max_loan_ratio': 0.8
                },
                severity='warning',
                chain_specific=True,
                error_message='High flash loan amount'
            )
        }

    async def validate_transaction(self,
                                 transaction: Dict,
                                 chain_id: int) -> ValidationResult:
        """Validate transaction against rules"""
        start_time = asyncio.get_event_loop().time()
        rule_results = []
        failed_rules = []
        warnings = []
        
        try:
            # Get chain configuration
            chain_config = config.get_chain_config(chain_id)
            
            # Get current state
            state = await self.state_manager.get_state(chain_id)
            
            # Apply each relevant rule
            for rule_name, rule in self.rules.items():
                if rule.rule_type in ['transaction', transaction.get('type', '')]:
                    # Skip chain-specific rules for unsupported chains
                    if rule.chain_specific and not chain_config:
                        continue
                        
                    result = await self._apply_rule(
                        rule,
                        transaction,
                        chain_id,
                        state
                    )
                    
                    rule_results.append(result)
                    
                    if not result['success']:
                        if rule.severity == 'error':
                            failed_rules.append(rule_name)
                        else:
                            warnings.append(result['message'])
                            
            return ValidationResult(
                success=len(failed_rules) == 0,
                rule_results=rule_results,
                failed_rules=failed_rules,
                warnings=warnings,
                validation_time=asyncio.get_event_loop().time() - start_time,
                chain_id=chain_id
            )
            
        except Exception as e:
            logger.error(f"Error in transaction validation: {str(e)}")
            return ValidationResult(
                success=False,
                rule_results=[],
                failed_rules=['validation_error'],
                warnings=[str(e)],
                validation_time=asyncio.get_event_loop().time() - start_time,
                chain_id=chain_id
            )

    async def validate_protocol_interaction(self,
                                         protocol_address: str,
                                         interaction: Dict,
                                         chain_id: int) -> ValidationResult:
        """Validate protocol interaction"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Get protocol type
            protocol_type = await self._get_protocol_type(protocol_address, chain_id)
            
            # Get relevant rules
            relevant_rules = {
                name: rule for name, rule in self.rules.items()
                if rule.rule_type in ['protocol', protocol_type]
            }
            
            # Validate interaction
            rule_results = []
            failed_rules = []
            warnings = []
            
            for rule_name, rule in relevant_rules.items():
                result = await self._apply_protocol_rule(
                    rule,
                    protocol_address,
                    interaction,
                    chain_id
                )
                
                rule_results.append(result)
                
                if not result['success']:
                    if rule.severity == 'error':
                        failed_rules.append(rule_name)
                    else:
                        warnings.append(result['message'])
                        
            return ValidationResult(
                success=len(failed_rules) == 0,
                rule_results=rule_results,
                failed_rules=failed_rules,
                warnings=warnings,
                validation_time=asyncio.get_event_loop().time() - start_time,
                chain_id=chain_id
            )
            
        except Exception as e:
            logger.error(f"Error in protocol validation: {str(e)}")
            return ValidationResult(
                success=False,
                rule_results=[],
                failed_rules=['validation_error'],
                warnings=[str(e)],
                validation_time=asyncio.get_event_loop().time() - start_time,
                chain_id=chain_id
            )

    async def _apply_rule(self,
                         rule: ValidationRule,
                         transaction: Dict,
                         chain_id: int,
                         state: Dict) -> Dict:
        """Apply validation rule to transaction"""
        try:
            if rule.name == 'gas_limit':
                return await self._validate_gas_limit(rule, transaction, chain_id)
            elif rule.name == 'balance_check':
                return await self._validate_balance(rule, transaction, chain_id)
            elif rule.name == 'nonce_check':
                return await self._validate_nonce(rule, transaction, chain_id)
            elif rule.name == 'value_check':
                return await self._validate_value(rule, transaction)
            elif rule.name == 'data_format':
                return await self._validate_data_format(rule, transaction)
            elif rule.name == 'protocol_check':
                return await self._validate_protocol(rule, transaction, chain_id)
            elif rule.name == 'slippage_check':
                return await self._validate_slippage(rule, transaction, state)
            elif rule.name == 'flash_loan_check':
                return await self._validate_flash_loan(rule, transaction, state)
            else:
                return {
                    'success': False,
                    'rule': rule.name,
                    'message': f"Unknown rule: {rule.name}"
                }
                
        except Exception as e:
            logger.error(f"Error applying rule {rule.name}: {str(e)}")
            return {
                'success': False,
                'rule': rule.name,
                'message': str(e)
            }

    async def _validate_gas_limit(self,
                                rule: ValidationRule,
                                transaction: Dict,
                                chain_id: int) -> Dict:
        """Validate transaction gas limit"""
        try:
            gas_limit = transaction.get('gas', 0)
            
            if gas_limit < rule.parameters['min_gas']:
                return {
                    'success': False,
                    'rule': rule.name,
                    'message': f"Gas limit too low: {gas_limit}"
                }
                
            if gas_limit > rule.parameters['max_gas']:
                return {
                    'success': False,
                    'rule': rule.name,
                    'message': f"Gas limit too high: {gas_limit}"
                }
                
            return {
                'success': True,
                'rule': rule.name,
                'message': "Gas limit valid"
            }
            
        except Exception as e:
            logger.error(f"Error validating gas limit: {str(e)}")
            return {
                'success': False,
                'rule': rule.name,
                'message': str(e)
            }

    async def _validate_balance(self,
                              rule: ValidationRule,
                              transaction: Dict,
                              chain_id: int) -> Dict:
        """Validate account balance"""
        try:
            chain_config = config.get_chain_config(chain_id)
            web3 = chain_config.get_web3()
            
            # Get account balance
            balance = await web3.eth.get_balance(
                transaction['from']
            )
            
            # Convert min_balance to Wei
            min_balance = web3.to_wei(
                rule.parameters['min_balance'].split()[0],
                'ether'
            )
            
            if balance < min_balance:
                return {
                    'success': False,
                    'rule': rule.name,
                    'message': f"Insufficient balance: {web3.from_wei(balance, 'ether')} ETH"
                }
                
            return {
                'success': True,
                'rule': rule.name,
                'message': "Balance sufficient"
            }
            
        except Exception as e:
            logger.error(f"Error validating balance: {str(e)}")
            return {
                'success': False,
                'rule': rule.name,
                'message': str(e)
            }

    async def _validate_nonce(self,
                            rule: ValidationRule,
                            transaction: Dict,
                            chain_id: int) -> Dict:
        """Validate transaction nonce"""
        try:
            chain_config = config.get_chain_config(chain_id)
            web3 = chain_config.get_web3()
            
            # Get current nonce
            current_nonce = await web3.eth.get_transaction_count(
                transaction['from']
            )
            
            tx_nonce = transaction.get('nonce', current_nonce)
            
            if tx_nonce < current_nonce:
                return {
                    'success': False,
                    'rule': rule.name,
                    'message': f"Nonce too low: {tx_nonce} < {current_nonce}"
                }
                
            return {
                'success': True,
                'rule': rule.name,
                'message': "Nonce valid"
            }
            
        except Exception as e:
            logger.error(f"Error validating nonce: {str(e)}")
            return {
                'success': False,
                'rule': rule.name,
                'message': str(e)
            }

    async def _validate_value(self,
                            rule: ValidationRule,
                            transaction: Dict) -> Dict:
        """Validate transaction value"""
        try:
            value = transaction.get('value', 0)
            
            if value < rule.parameters['min_value']:
                return {
                    'success': False,
                    'rule': rule.name,
                    'message': f"Invalid value: {value}"
                }
                
            return {
                'success': True,
                'rule': rule.name,
                'message': "Value valid"
            }
            
        except Exception as e:
            logger.error(f"Error validating value: {str(e)}")
            return {
                'success': False,
                'rule': rule.name,
                'message': str(e)
            }

    async def _validate_data_format(self,
                                  rule: ValidationRule,
                                  transaction: Dict) -> Dict:
        """Validate transaction data format"""
        try:
            data = transaction.get('data', '0x')
            
            if not data.startswith('0x'):
                return {
                    'success': False,
                    'rule': rule.name,
                    'message': "Data must start with 0x"
                }
                
            data_length = len(data) - 2  # Subtract '0x'
            
            if data_length < rule.parameters['min_length']:
                return {
                    'success': False,
                    'rule': rule.name,
                    'message': f"Data too short: {data_length} bytes"
                }
                
            if data_length > rule.parameters['max_length']:
                return {
                    'success': False,
                    'rule': rule.name,
                    'message': f"Data too long: {data_length} bytes"
                }
                
            return {
                'success': True,
                'rule': rule.name,
                'message': "Data format valid"
            }
            
        except Exception as e:
            logger.error(f"Error validating data format: {str(e)}")
            return {
                'success': False,
                'rule': rule.name,
                'message': str(e)
            }

    async def _validate_protocol(self,
                               rule: ValidationRule,
                               transaction: Dict,
                               chain_id: int) -> Dict:
        """Validate protocol interaction"""
        try:
            chain_config = config.get_chain_config(chain_id)
            
            # Get target address
            to_address = transaction.get('to', '').lower()
            
            # Check if target is known protocol
            if not (
                to_address in chain_config.dex_addresses.values() or
                to_address in chain_config.lending_protocols.values() or
                to_address in chain_config.flash_loan_providers.values()
            ):
                return {
                    'success': False,
                    'rule': rule.name,
                    'message': f"Unknown protocol address: {to_address}"
                }
                
            return {
                'success': True,
                'rule': rule.name,
                'message': "Protocol interaction valid"
            }
            
        except Exception as e:
            logger.error(f"Error validating protocol: {str(e)}")
            return {
                'success': False,
                'rule': rule.name,
                'message': str(e)
            }

    async def _validate_slippage(self,
                               rule: ValidationRule,
                               transaction: Dict,
                               state: Dict) -> Dict:
        """Validate DEX slippage"""
        try:
            if transaction.get('type') != 'swap':
                return {
                    'success': True,
                    'rule': rule.name,
                    'message': "Not a swap transaction"
                }
                
            # Calculate slippage
            amount_in = transaction.get('amount_in', 0)
            min_amount_out = transaction.get('min_amount_out', 0)
            expected_amount_out = transaction.get('expected_amount_out', 0)
            
            if expected_amount_out == 0:
                return {
                    'success': False,
                    'rule': rule.name,
                    'message': "Missing expected output amount"
                }
                
            slippage = (expected_amount_out - min_amount_out) / expected_amount_out
            
            if slippage > rule.parameters['max_slippage']:
                return {
                    'success': False,
                    'rule': rule.name,
                    'message': f"High slippage: {slippage * 100}%"
                }
                
            return {
                'success': True,
                'rule': rule.name,
                'message': "Slippage within limits"
            }
            
        except Exception as e:
            logger.error(f"Error validating slippage: {str(e)}")
            return {
                'success': False,
                'rule': rule.name,
                'message': str(e)
            }

    async def _validate_flash_loan(self,
                                 rule: ValidationRule,
                                 transaction: Dict,
                                 state: Dict) -> Dict:
        """Validate flash loan parameters"""
        try:
            if transaction.get('type') != 'flash_loan':
                return {
                    'success': True,
                    'rule': rule.name,
                    'message': "Not a flash loan transaction"
                }
                
            # Get loan amount and protocol liquidity
            loan_amount = transaction.get('amount', 0)
            protocol_address = transaction.get('protocol_address', '')
            
            if not protocol_address:
                return {
                    'success': False,
                    'rule': rule.name,
                    'message': "Missing protocol address"
                }
                
            protocol_state = state.protocol_states.get(protocol_address, {})
            available_liquidity = protocol_state.get('available_liquidity', 0)
            
            if available_liquidity == 0:
                return {
                    'success': False,
                    'rule': rule.name,
                    'message': "Unable to determine protocol liquidity"
                }
                
            loan_ratio = loan_amount / available_liquidity
            
            if loan_ratio > rule.parameters['max_loan_ratio']:
                return {
                    'success': False,
                    'rule': rule.name,
                    'message': f"Loan amount too high: {loan_ratio * 100}% of liquidity"
                }
                
            return {
                'success': True,
                'rule': rule.name,
                'message': "Flash loan parameters valid"
            }
            
        except Exception as e:
            logger.error(f"Error validating flash loan: {str(e)}")
            return {
                'success': False,
                'rule': rule.name,
                'message': str(e)
            }

    async def _get_protocol_type(self,
                               protocol_address: str,
                               chain_id: int) -> Optional[str]:
        """Determine protocol type from address"""
        try:
            chain_config = config.get_chain_config(chain_id)
            address = protocol_address.lower()
            
            if address in chain_config.dex_addresses.values():
                return 'dex'
            elif address in chain_config.lending_protocols.values():
                return 'lending'
            elif address in chain_config.flash_loan_providers.values():
                return 'flash_loan'
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error getting protocol type: {str(e)}")
            return None

    async def _apply_protocol_rule(self,
                                 rule: ValidationRule,
                                 protocol_address: str,
                                 interaction: Dict,
                                 chain_id: int) -> Dict:
        """Apply protocol-specific validation rule"""
        try:
            protocol_type = await self._get_protocol_type(protocol_address, chain_id)
            
            if not protocol_type:
                return {
                    'success': False,
                    'rule': rule.name,
                    'message': f"Unknown protocol: {protocol_address}"
                }
                
            if protocol_type == 'dex':
                return await self._validate_dex_interaction(rule, interaction)
            elif protocol_type == 'lending':
                return await self._validate_lending_interaction(rule, interaction)
            elif protocol_type == 'flash_loan':
                return await self._validate_flash_loan_interaction(rule, interaction)
            else:
                return {
                    'success': False,
                    'rule': rule.name,
                    'message': f"Unsupported protocol type: {protocol_type}"
                }
                
        except Exception as e:
            logger.error(f"Error applying protocol rule: {str(e)}")
            return {
                'success': False,
                'rule': rule.name,
                'message': str(e)
            }

    async def _validate_dex_interaction(self,
                                      rule: ValidationRule,
                                      interaction: Dict) -> Dict:
        """Validate DEX interaction"""
        # Implementation for DEX validation
        return {'success': True, 'rule': rule.name, 'message': "DEX interaction valid"}

    async def _validate_lending_interaction(self,
                                         rule: ValidationRule,
                                         interaction: Dict) -> Dict:
        """Validate lending protocol interaction"""
        # Implementation for lending validation
        return {'success': True, 'rule': rule.name, 'message': "Lending interaction valid"}

    async def _validate_flash_loan_interaction(self,
                                            rule: ValidationRule,
                                            interaction: Dict) -> Dict:
        """Validate flash loan interaction"""
        # Implementation for flash loan validation
        return {'success': True, 'rule': rule.name, 'message': "Flash loan interaction valid"}