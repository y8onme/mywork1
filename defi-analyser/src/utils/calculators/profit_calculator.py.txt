# src/utils/calculators/profit_calculator.py

import asyncio
from typing import Dict, List, Optional, Union
from decimal import Decimal
from dataclasses import dataclass
from ..config import config
from ..logger import logger
from ..state.state_manager import StateManager
from ..validation.validator import Validator

@dataclass
class ProfitResult:
    chain_id: int
    total_profit: Decimal
    gas_cost: Decimal
    net_profit: Decimal
    profit_sources: Dict[str, Decimal]
    execution_time: float
    risk_score: float
    confidence_score: float
    state_changes: List[Dict]

class ProfitCalculator:
    def __init__(self):
        self.state_manager = StateManager()
        self.validator = Validator()
        
    async def calculate_profit(self,
                             transactions: List[Dict],
                             chain_id: int,
                             options: Optional[Dict] = None) -> ProfitResult:
        """Calculate potential profit from a set of transactions"""
        try:
            start_time = asyncio.get_event_loop().time()
            chain_config = config.get_chain_config(chain_id)
            options = options or {}
            
            # Validate transactions
            if not await self._validate_transactions(transactions, chain_id):
                raise ValueError("Invalid transaction sequence")
                
            # Calculate components
            gas_cost = await self._calculate_gas_cost(transactions, chain_id)
            dex_profits = await self._calculate_dex_profits(transactions, chain_id)
            lending_profits = await self._calculate_lending_profits(transactions, chain_id)
            flash_loan_profits = await self._calculate_flash_loan_profits(transactions, chain_id)
            
            # Aggregate profits
            profit_sources = {
                'dex': dex_profits,
                'lending': lending_profits,
                'flash_loans': flash_loan_profits
            }
            
            total_profit = sum(profit_sources.values())
            net_profit = total_profit - gas_cost
            
            # Calculate metrics
            risk_score = self._calculate_risk_score(transactions, net_profit)
            confidence_score = self._calculate_confidence_score(transactions, profit_sources)
            
            # Get state changes
            state_changes = await self._get_state_changes(transactions, chain_id)
            
            return ProfitResult(
                chain_id=chain_id,
                total_profit=total_profit,
                gas_cost=gas_cost,
                net_profit=net_profit,
                profit_sources=profit_sources,
                execution_time=asyncio.get_event_loop().time() - start_time,
                risk_score=risk_score,
                confidence_score=confidence_score,
                state_changes=state_changes
            )
            
        except Exception as e:
            logger.error(f"Error calculating profit: {str(e)}")
            raise

    async def _validate_transactions(self,
                                   transactions: List[Dict],
                                   chain_id: int) -> bool:
        """Validate transaction sequence"""
        try:
            for tx in transactions:
                if not await self.validator.validate_transaction(tx, chain_id):
                    return False
            return True
        except Exception as e:
            logger.error(f"Transaction validation error: {str(e)}")
            return False

    async def _calculate_gas_cost(self,
                                transactions: List[Dict],
                                chain_id: int) -> Decimal:
        """Calculate total gas cost for transactions"""
        try:
            chain_config = config.get_chain_config(chain_id)
            total_gas = Decimal('0')
            
            for tx in transactions:
                gas_limit = tx.get('gas_limit', 500000)
                gas_price = tx.get('gas_price') or await self._get_gas_price(chain_id)
                total_gas += Decimal(str(gas_limit * gas_price))
                
            return total_gas
            
        except Exception as e:
            logger.error(f"Gas calculation error: {str(e)}")
            return Decimal('0')

    async def _calculate_dex_profits(self,
                                   transactions: List[Dict],
                                   chain_id: int) -> Decimal:
        """Calculate profits from DEX operations"""
        try:
            profit = Decimal('0')
            chain_config = config.get_chain_config(chain_id)
            
            for tx in transactions:
                if tx.get('type') == 'swap':
                    # Get token prices
                    token_in_price = await self._get_token_price(
                        tx['token_in'],
                        chain_id
                    )
                    token_out_price = await self._get_token_price(
                        tx['token_out'],
                        chain_id
                    )
                    
                    # Calculate profit
                    amount_in = Decimal(str(tx['amount_in']))
                    amount_out = Decimal(str(tx['amount_out']))
                    
                    value_in = amount_in * token_in_price
                    value_out = amount_out * token_out_price
                    
                    tx_profit = value_out - value_in
                    profit += tx_profit
                    
            return profit
            
        except Exception as e:
            logger.error(f"DEX profit calculation error: {str(e)}")
            return Decimal('0')

    async def _calculate_lending_profits(self,
                                      transactions: List[Dict],
                                      chain_id: int) -> Decimal:
        """Calculate profits from lending operations"""
        try:
            profit = Decimal('0')
            chain_config = config.get_chain_config(chain_id)
            
            for tx in transactions:
                if tx.get('type') in ['borrow', 'repay']:
                    amount = Decimal(str(tx.get('amount', 0)))
                    interest_rate = Decimal(str(tx.get('interest_rate', 0)))
                    
                    if tx['type'] == 'borrow':
                        profit -= amount * interest_rate
                    else:  # repay
                        collateral = Decimal(str(tx.get('collateral_amount', 0)))
                        collateral_price = await self._get_token_price(
                            tx['collateral_token'],
                            chain_id
                        )
                        profit += collateral * collateral_price
                        
            return profit
            
        except Exception as e:
            logger.error(f"Lending profit calculation error: {str(e)}")
            return Decimal('0')

    async def _calculate_flash_loan_profits(self,
                                         transactions: List[Dict],
                                         chain_id: int) -> Decimal:
        """Calculate profits from flash loan operations"""
        try:
            profit = Decimal('0')
            
            for tx in transactions:
                if tx.get('type') == 'flash_loan':
                    amount = Decimal(str(tx.get('amount', 0)))
                    fee_rate = Decimal(str(tx.get('fee_rate', '0.001')))  # 0.1% typical fee
                    
                    # Subtract flash loan fee
                    profit -= amount * fee_rate
                    
            return profit
            
        except Exception as e:
            logger.error(f"Flash loan profit calculation error: {str(e)}")
            return Decimal('0')

    async def _get_gas_price(self, chain_id: int) -> int:
        """Get current gas price from chain"""
        try:
            chain_config = config.get_chain_config(chain_id)
            web3 = chain_config.get_web3()
            return await web3.eth.gas_price
        except Exception as e:
            logger.error(f"Error getting gas price: {str(e)}")
            return chain_config.default_gas_price

    async def _get_token_price(self,
                             token_address: str,
                             chain_id: int) -> Decimal:
        """Get token price from oracle or DEX"""
        try:
            chain_config = config.get_chain_config(chain_id)
            
            # Try price feed first
            price_feed = chain_config.get_price_feed(token_address)
            if price_feed:
                return Decimal(str(await price_feed.get_price()))
                
            # Fallback to DEX price
            return await self._get_dex_price(token_address, chain_id)
            
        except Exception as e:
            logger.error(f"Error getting token price: {str(e)}")
            return Decimal('0')

    async def _get_dex_price(self,
                           token_address: str,
                           chain_id: int) -> Decimal:
        """Get token price from DEX"""
        try:
            chain_config = config.get_chain_config(chain_id)
            
            # Get price from largest DEX pool
            for dex in chain_config.dex_addresses.values():
                price = await dex.get_token_price(token_address)
                if price > 0:
                    return Decimal(str(price))
                    
            return Decimal('0')
            
        except Exception as e:
            logger.error(f"Error getting DEX price: {str(e)}")
            return Decimal('0')

    def _calculate_risk_score(self,
                            transactions: List[Dict],
                            net_profit: Decimal) -> float:
        """Calculate risk score for transaction sequence"""
        try:
            base_risk = 0.5
            
            # Adjust for complexity
            base_risk += len(transactions) * 0.05
            
            # Adjust for profit potential
            if net_profit > Decimal('10.0'):
                base_risk += 0.2
                
            # Adjust for transaction types
            for tx in transactions:
                if tx.get('type') == 'flash_loan':
                    base_risk += 0.1
                elif tx.get('type') in ['borrow', 'repay']:
                    base_risk += 0.15
                    
            return min(base_risk, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating risk score: {str(e)}")
            return 1.0

    def _calculate_confidence_score(self,
                                 transactions: List[Dict],
                                 profit_sources: Dict[str, Decimal]) -> float:
        """Calculate confidence score for profit calculation"""
        try:
            base_confidence = 0.8
            
            # Adjust for profit sources
            if len(profit_sources) > 2:
                base_confidence -= 0.1
                
            # Adjust for transaction count
            if len(transactions) > 5:
                base_confidence -= 0.1
                
            # Adjust for profit distribution
            total_profit = sum(profit_sources.values())
            if total_profit > 0:
                max_source_ratio = max(profit_sources.values()) / total_profit
                if max_source_ratio > 0.8:
                    base_confidence += 0.1
                    
            return min(max(base_confidence, 0.0), 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating confidence score: {str(e)}")
            return 0.0

    async def _get_state_changes(self,
                               transactions: List[Dict],
                               chain_id: int) -> List[Dict]:
        """Get expected state changes from transactions"""
        try:
            changes = []
            
            for tx in transactions:
                state_change = await self.state_manager.calculate_state_change(
                    tx,
                    chain_id
                )
                if state_change:
                    changes.append(state_change)
                    
            return changes
            
        except Exception as e:
            logger.error(f"Error getting state changes: {str(e)}")
            return []