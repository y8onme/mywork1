# src/utils/error/error_recovery.py

import asyncio
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
from ..config import config
from ..logger import logger
from ..state.state_manager import StateManager

@dataclass
class RecoveryStrategy:
    strategy_type: str
    steps: List[Dict]
    estimated_success: float
    required_resources: Dict
    fallback_strategy: Optional[Dict]
    max_attempts: int
    timeout: int

@dataclass
class RecoveryResult:
    success: bool
    strategy_used: str
    attempts_made: int
    error_details: Optional[Dict]
    state_changes: List[Dict]
    recovery_time: float

class ErrorRecovery:
    def __init__(self):
        self.state_manager = StateManager()
        self.active_recoveries: Dict[str, RecoveryStrategy] = {}
        self.recovery_history: Dict[str, List[RecoveryResult]] = {}
        
        # Initialize recovery strategies
        self.strategies = self._initialize_strategies()
        
    def _initialize_strategies(self) -> Dict[str, Dict]:
        """Initialize recovery strategies for different error types"""
        return {
            'transaction_failure': {
                'retry': {
                    'priority': 1,
                    'max_attempts': 3,
                    'delay_between_attempts': 2
                },
                'adjust_gas': {
                    'priority': 2,
                    'max_gas_increase': 1.5,
                    'max_attempts': 2
                },
                'resubmit': {
                    'priority': 3,
                    'nonce_handling': 'increment',
                    'max_attempts': 2
                }
            },
            'state_inconsistency': {
                'resync': {
                    'priority': 1,
                    'sync_depth': 'full',
                    'max_attempts': 2
                },
                'rollback': {
                    'priority': 2,
                    'rollback_blocks': 1,
                    'max_attempts': 1
                }
            },
            'protocol_error': {
                'retry_with_params': {
                    'priority': 1,
                    'param_adjustment': 0.1,
                    'max_attempts': 3
                },
                'alternative_route': {
                    'priority': 2,
                    'route_search_depth': 2,
                    'max_attempts': 2
                }
            }
        }

    async def handle_error(self,
                          error: Exception,
                          context: Dict,
                          chain_id: int) -> RecoveryResult:
        """Handle error and attempt recovery"""
        try:
            # Generate recovery ID
            recovery_id = self._generate_recovery_id(error, context)
            
            # Analyze error
            error_type = self._analyze_error(error)
            
            # Get appropriate strategy
            strategy = await self._get_recovery_strategy(error_type, context, chain_id)
            
            if not strategy:
                raise ValueError("No suitable recovery strategy found")
                
            # Track active recovery
            self.active_recoveries[recovery_id] = strategy
            
            # Execute recovery
            result = await self._execute_recovery(strategy, context, chain_id)
            
            # Update history
            self._update_recovery_history(recovery_id, result)
            
            # Clean up
            del self.active_recoveries[recovery_id]
            
            return result
            
        except Exception as e:
            logger.error(f"Error in recovery handling: {str(e)}")
            return RecoveryResult(
                success=False,
                strategy_used="none",
                attempts_made=0,
                error_details={"error": str(e)},
                state_changes=[],
                recovery_time=0
            )

    async def _execute_recovery(self,
                              strategy: RecoveryStrategy,
                              context: Dict,
                              chain_id: int) -> RecoveryResult:
        """Execute recovery strategy"""
        start_time = asyncio.get_event_loop().time()
        attempts_made = 0
        
        try:
            for step in strategy.steps:
                success = False
                
                for attempt in range(strategy.max_attempts):
                    attempts_made += 1
                    
                    try:
                        # Execute recovery step
                        result = await self._execute_recovery_step(
                            step,
                            context,
                            chain_id
                        )
                        
                        if result['success']:
                            success = True
                            break
                            
                        # Check if we should try fallback
                        if attempt == strategy.max_attempts - 1 and strategy.fallback_strategy:
                            fallback_result = await self._execute_fallback(
                                strategy.fallback_strategy,
                                context,
                                chain_id
                            )
                            if fallback_result['success']:
                                success = True
                                break
                                
                    except Exception as e:
                        logger.error(f"Error in recovery step: {str(e)}")
                        await asyncio.sleep(1)
                        
                if not success:
                    return RecoveryResult(
                        success=False,
                        strategy_used=strategy.strategy_type,
                        attempts_made=attempts_made,
                        error_details={"step": step, "error": "Max attempts reached"},
                        state_changes=[],
                        recovery_time=asyncio.get_event_loop().time() - start_time
                    )
                    
            return RecoveryResult(
                success=True,
                strategy_used=strategy.strategy_type,
                attempts_made=attempts_made,
                error_details=None,
                state_changes=await self._get_state_changes(context, chain_id),
                recovery_time=asyncio.get_event_loop().time() - start_time
            )
            
        except Exception as e:
            logger.error(f"Error executing recovery: {str(e)}")
            return RecoveryResult(
                success=False,
                strategy_used=strategy.strategy_type,
                attempts_made=attempts_made,
                error_details={"error": str(e)},
                state_changes=[],
                recovery_time=asyncio.get_event_loop().time() - start_time
            )

    async def _execute_recovery_step(self,
                                   step: Dict,
                                   context: Dict,
                                   chain_id: int) -> Dict:
        """Execute single recovery step"""
        try:
            step_type = step['type']
            
            if step_type == 'retry_transaction':
                return await self._retry_transaction(step, context, chain_id)
            elif step_type == 'adjust_parameters':
                return await self._adjust_parameters(step, context, chain_id)
            elif step_type == 'resync_state':
                return await self._resync_state(step, context, chain_id)
            elif step_type == 'rollback_state':
                return await self._rollback_state(step, context, chain_id)
            else:
                raise ValueError(f"Unknown recovery step type: {step_type}")
                
        except Exception as e:
            logger.error(f"Error in recovery step: {str(e)}")
            return {'success': False, 'error': str(e)}

    async def _retry_transaction(self,
                               step: Dict,
                               context: Dict,
                               chain_id: int) -> Dict:
        """Retry failed transaction"""
        try:
            chain_config = config.get_chain_config(chain_id)
            
            # Get transaction
            tx = context.get('transaction')
            if not tx:
                raise ValueError("No transaction in context")
                
            # Adjust gas if needed
            if step.get('adjust_gas'):
                tx['gas_price'] = int(tx['gas_price'] * 1.2)
                
            # Send transaction
            result = await chain_config.send_transaction(tx)
            
            return {
                'success': result['success'],
                'tx_hash': result.get('tx_hash'),
                'gas_used': result.get('gas_used')
            }
            
        except Exception as e:
            logger.error(f"Error retrying transaction: {str(e)}")
            return {'success': False, 'error': str(e)}

    async def _adjust_parameters(self,
                               step: Dict,
                               context: Dict,
                               chain_id: int) -> Dict:
        """Adjust parameters for recovery"""
        try:
            # Get parameters to adjust
            params = step.get('parameters', {})
            
            # Apply adjustments
            adjusted_context = context.copy()
            for param, adjustment in params.items():
                if param in adjusted_context:
                    adjusted_context[param] = self._apply_adjustment(
                        adjusted_context[param],
                        adjustment
                    )
                    
            return {
                'success': True,
                'adjusted_context': adjusted_context
            }
            
        except Exception as e:
            logger.error(f"Error adjusting parameters: {str(e)}")
            return {'success': False, 'error': str(e)}

    async def _resync_state(self,
                           step: Dict,
                           context: Dict,
                           chain_id: int) -> Dict:
        """Resynchronize state"""
        try:
            # Get sync depth
            sync_depth = step.get('sync_depth', 'full')
            
            # Perform resync
            await self.state_manager._update_chain_state(chain_id)
            
            return {'success': True}
            
        except Exception as e:
            logger.error(f"Error resyncing state: {str(e)}")
            return {'success': False, 'error': str(e)}

    async def _rollback_state(self,
                             step: Dict,
                             context: Dict,
                             chain_id: int) -> Dict:
        """Rollback state to previous block"""
        try:
            blocks = step.get('blocks', 1)
            
            # Get current state
            current_state = await self.state_manager.get_state(chain_id)
            
            # Calculate target block
            target_block = current_state.block_number - blocks
            
            # Perform rollback
            await self.state_manager._update_chain_state(chain_id)
            
            return {'success': True, 'target_block': target_block}
            
        except Exception as e:
            logger.error(f"Error rolling back state: {str(e)}")
            return {'success': False, 'error': str(e)}

    def _analyze_error(self, error: Exception) -> str:
        """Analyze error to determine type"""
        error_str = str(error).lower()
        
        if 'nonce too low' in error_str or 'transaction underpriced' in error_str:
            return 'transaction_failure'
        elif 'state' in error_str and ('invalid' in error_str or 'inconsistent' in error_str):
            return 'state_inconsistency'
        elif 'revert' in error_str or 'invalid opcode' in error_str:
            return 'protocol_error'
        else:
            return 'unknown'

    async def _get_recovery_strategy(self,
                                   error_type: str,
                                   context: Dict,
                                   chain_id: int) -> Optional[RecoveryStrategy]:
        """Get appropriate recovery strategy"""
        try:
            if error_type not in self.strategies:
                return None
                
            strategies = self.strategies[error_type]
            
            # Sort strategies by priority
            sorted_strategies = sorted(
                strategies.items(),
                key=lambda x: x[1]['priority']
            )
            
            for strategy_name, strategy_config in sorted_strategies:
                if self._is_strategy_applicable(strategy_name, context, chain_id):
                    return self._create_recovery_strategy(
                        strategy_name,
                        strategy_config,
                        context
                    )
                    
            return None
            
        except Exception as e:
            logger.error(f"Error getting recovery strategy: {str(e)}")
            return None

    def _is_strategy_applicable(self,
                              strategy_name: str,
                              context: Dict,
                              chain_id: int) -> bool:
        """Check if recovery strategy is applicable"""
        try:
            if strategy_name == 'retry':
                return 'transaction' in context
            elif strategy_name == 'adjust_gas':
                return 'transaction' in context and 'gas_price' in context['transaction']
            elif strategy_name == 'resync':
                return True
            elif strategy_name == 'rollback':
                return context.get('can_rollback', False)
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error checking strategy applicability: {str(e)}")
            return False

    def _create_recovery_strategy(self,
                                strategy_name: str,
                                strategy_config: Dict,
                                context: Dict) -> RecoveryStrategy:
        """Create recovery strategy instance"""
        try:
            steps = self._generate_recovery_steps(strategy_name, strategy_config, context)
            
            return RecoveryStrategy(
                strategy_type=strategy_name,
                steps=steps,
                estimated_success=0.7,
                required_resources={},
                fallback_strategy=self._get_fallback_strategy(strategy_name),
                max_attempts=strategy_config['max_attempts'],
                timeout=30
            )
            
        except Exception as e:
            logger.error(f"Error creating recovery strategy: {str(e)}")
            raise

    def _generate_recovery_steps(self,
                               strategy_name: str,
                               strategy_config: Dict,
                               context: Dict) -> List[Dict]:
        """Generate steps for recovery strategy"""
        try:
            if strategy_name == 'retry':
                return [{
                    'type': 'retry_transaction',
                    'adjust_gas': False
                }]
            elif strategy_name == 'adjust_gas':
                return [{
                    'type': 'retry_transaction',
                    'adjust_gas': True
                }]
            elif strategy_name == 'resync':
                return [{
                    'type': 'resync_state',
                    'sync_depth': strategy_config.get('sync_depth', 'full')
                }]
            elif strategy_name == 'rollback':
                return [{
                    'type': 'rollback_state',
                    'blocks': strategy_config.get('rollback_blocks', 1)
                }]
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error generating recovery steps: {str(e)}")
            return []

    def _get_fallback_strategy(self, strategy_name: str) -> Optional[Dict]:
        """Get fallback strategy configuration"""
        try:
            if strategy_name == 'retry':
                return {'type': 'adjust_gas'}
            elif strategy_name == 'adjust_gas':
                return {'type': 'resync'}
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error getting fallback strategy: {str(e)}")
            return None

    def _generate_recovery_id(self, error: Exception, context: Dict) -> str:
        """Generate unique recovery ID"""
        import hashlib
        
        # Create unique string from error and context
        unique_string = f"{str(error)}:{str(context)}"
        
        # Generate hash
        return hashlib.sha256(unique_string.encode()).hexdigest()[:16]

    def _update_recovery_history(self,
                               recovery_id: str,
                               result: RecoveryResult):
        """Update recovery history"""
        if recovery_id not in self.recovery_history:
            self.recovery_history[recovery_id] = []
            
        self.recovery_history[recovery_id].append(result)
        
        # Limit history size
        if len(self.recovery_history[recovery_id]) > 10:
            self.recovery_history[recovery_id] = self.recovery_history[recovery_id][-10:]

    async def _get_state_changes(self,
                               context: Dict,
                               chain_id: int) -> List[Dict]:
        """Get state changes from recovery"""
        try:
            if 'transaction' in context:
                return await self.state_manager.calculate_state_change(
                    context['transaction'],
                    chain_id
                )
            return []
            
        except Exception as e:
            logger.error(f"Error getting state changes: {str(e)}")
            return []

    def _apply_adjustment(self,
                         value: Union[int, float, str],
                         adjustment: Union[int, float, str]) -> Union[int, float, str]:
        """Apply adjustment to value"""
        try:
            if isinstance(value, (int, float)) and isinstance(adjustment, (int, float)):
                return value * (1 + adjustment)
            elif isinstance(value, str):
                return str(float(value) * (1 + float(adjustment)))
            else:
                return value
                
        except Exception as e:
            logger.error(f"Error applying adjustment: {str(e)}")
            return value
