# src/core/analyzers/batch_analyzer.py

import asyncio
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from ...utils.config import config
from ...utils.logger import logger
from ...utils.state.state_manager import StateManager
from ..multi_stage_executor import MultiStageExecutor

@dataclass
class BatchOpportunity:
    chain_id: int
    transactions: List[Dict]
    estimated_profit: float
    gas_savings: float
    execution_order: List[int]
    dependencies: Dict[int, List[int]]
    risk_score: float
    confidence_score: float
    optimization_level: str
    batch_size: int

class BatchAnalyzer:
    def __init__(self):
        self.state_manager = StateManager()
        self.executor = MultiStageExecutor()
        self.min_batch_size = 2
        self.max_batch_size = 15
        
    async def analyze_batch_opportunities(self,
                                        transactions: List[Dict],
                                        chain_id: int,
                                        options: Optional[Dict] = None) -> List[BatchOpportunity]:
        """Analyze opportunities for batch execution"""
        try:
            options = options or {}
            opportunities = []
            
            # Get chain state
            state = await self.state_manager.get_state(chain_id)
            
            # Group compatible transactions
            transaction_groups = self._group_compatible_transactions(
                transactions,
                chain_id
            )
            
            # Analyze each group
            for group in transaction_groups:
                if len(group) < self.min_batch_size:
                    continue
                    
                # Find optimal batches
                batch_opportunities = await self._analyze_transaction_group(
                    group,
                    chain_id,
                    state,
                    options
                )
                
                opportunities.extend(batch_opportunities)
                
            return opportunities
            
        except Exception as e:
            logger.error(f"Error analyzing batch opportunities: {str(e)}")
            return []

    def _group_compatible_transactions(self,
                                    transactions: List[Dict],
                                    chain_id: int) -> List[List[Dict]]:
        """Group transactions that can be batched together"""
        try:
            groups = []
            current_group = []
            
            for tx in transactions:
                if self._can_add_to_group(tx, current_group):
                    current_group.append(tx)
                else:
                    if current_group:
                        groups.append(current_group)
                    current_group = [tx]
                    
            if current_group:
                groups.append(current_group)
                
            return groups
            
        except Exception as e:
            logger.error(f"Error grouping transactions: {str(e)}")
            return []

    async def _analyze_transaction_group(self,
                                       transactions: List[Dict],
                                       chain_id: int,
                                       state: Dict,
                                       options: Dict) -> List[BatchOpportunity]:
        """Analyze transaction group for batching opportunities"""
        try:
            opportunities = []
            
            # Generate possible batch sizes
            for size in range(self.min_batch_size, min(len(transactions) + 1, self.max_batch_size + 1)):
                # Generate batch combinations
                batches = self._generate_batch_combinations(
                    transactions,
                    size
                )
                
                for batch in batches:
                    # Analyze batch
                    opportunity = await self._analyze_batch(
                        batch,
                        chain_id,
                        state,
                        options
                    )
                    
                    if opportunity:
                        opportunities.append(opportunity)
                        
            return opportunities
            
        except Exception as e:
            logger.error(f"Error analyzing transaction group: {str(e)}")
            return []

    async def _analyze_batch(self,
                           transactions: List[Dict],
                           chain_id: int,
                           state: Dict,
                           options: Dict) -> Optional[BatchOpportunity]:
        """Analyze specific batch of transactions"""
        try:
            # Calculate gas savings
            individual_gas = sum(tx.get('gas', 0) for tx in transactions)
            batch_gas = await self._estimate_batch_gas(
                transactions,
                chain_id
            )
            
            gas_savings = individual_gas - batch_gas
            
            if gas_savings <= 0:
                return None
                
            # Determine execution order
            execution_order = await self._determine_execution_order(
                transactions,
                chain_id
            )
            
            # Calculate dependencies
            dependencies = self._calculate_dependencies(
                transactions,
                execution_order
            )
            
            # Calculate profit
            profit = self._calculate_batch_profit(
                gas_savings,
                chain_id
            )
            
            if profit <= options.get('min_profit', 0):
                return None
                
            return BatchOpportunity(
                chain_id=chain_id,
                transactions=transactions,
                estimated_profit=profit,
                gas_savings=gas_savings,
                execution_order=execution_order,
                dependencies=dependencies,
                risk_score=self._calculate_risk_score(transactions),
                confidence_score=self._calculate_confidence_score(transactions),
                optimization_level=self._determine_optimization_level(gas_savings),
                batch_size=len(transactions)
            )
            
        except Exception as e:
            logger.error(f"Error analyzing batch: {str(e)}")
            return None

    def _can_add_to_group(self, transaction: Dict, group: List[Dict]) -> bool:
        """Check if transaction can be added to group"""
        try:
            if not group:
                return True
                
            # Check transaction type compatibility
            if transaction.get('type') != group[0].get('type'):
                return False
                
            # Check target contract compatibility
            if transaction.get('to') != group[0].get('to'):
                return False
                
            # Check for conflicts
            for tx in group:
                if self._transactions_conflict(transaction, tx):
                    return False
                    
            return True
            
        except Exception as e:
            logger.error(f"Error checking group compatibility: {str(e)}")
            return False

    def _transactions_conflict(self, tx1: Dict, tx2: Dict) -> bool:
        """Check if transactions conflict"""
        try:
            # Check for nonce conflicts
            if tx1.get('nonce') == tx2.get('nonce'):
                return True
                
            # Check for state conflicts
            if self._state_conflicts(tx1, tx2):
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Error checking transaction conflicts: {str(e)}")
            return True

    def _state_conflicts(self, tx1: Dict, tx2: Dict) -> bool:
        """Check for state conflicts between transactions"""
        try:
            # Check for overlapping state changes
            state_changes1 = set(tx1.get('state_changes', []))
            state_changes2 = set(tx2.get('state_changes', []))
            
            return bool(state_changes1.intersection(state_changes2))
            
        except Exception as e:
            logger.error(f"Error checking state conflicts: {str(e)}")
            return True

    def _generate_batch_combinations(self,
                                   transactions: List[Dict],
                                   size: int) -> List[List[Dict]]:
        """Generate possible batch combinations"""
        try:
            from itertools import combinations
            return list(combinations(transactions, size))
        except Exception as e:
            logger.error(f"Error generating batch combinations: {str(e)}")
            return []

    async def _estimate_batch_gas(self,
                                transactions: List[Dict],
                                chain_id: int) -> int:
        """Estimate gas cost for batch execution"""
        try:
            chain_config = config.get_chain_config(chain_id)
            
            # Create batch transaction
            batch_tx = {
                'to': transactions[0].get('to'),
                'data': self._encode_batch_data(transactions),
                'value': sum(tx.get('value', 0) for tx in transactions)
            }
            
            # Estimate gas
            web3 = chain_config.get_web3()
            return await web3.eth.estimate_gas(batch_tx)
            
        except Exception as e:
            logger.error(f"Error estimating batch gas: {str(e)}")
            return sum(tx.get('gas', 0) for tx in transactions)

    async def _determine_execution_order(self,
                                       transactions: List[Dict],
                                       chain_id: int) -> List[int]:
        """Determine optimal execution order"""
        try:
            # Create dependency graph
            graph = self._create_dependency_graph(transactions)
            
            # Perform topological sort
            return self._topological_sort(graph)
            
        except Exception as e:
            logger.error(f"Error determining execution order: {str(e)}")
            return list(range(len(transactions)))

    def _calculate_dependencies(self,
                              transactions: List[Dict],
                              execution_order: List[int]) -> Dict[int, List[int]]:
        """Calculate transaction dependencies"""
        try:
            dependencies = {}
            
            for i, tx_index in enumerate(execution_order):
                deps = []
                for j in range(i):
                    if self._depends_on(
                        transactions[tx_index],
                        transactions[execution_order[j]]
                    ):
                        deps.append(execution_order[j])
                dependencies[tx_index] = deps
                
            return dependencies
            
        except Exception as e:
            logger.error(f"Error calculating dependencies: {str(e)}")
            return {}

    def _calculate_batch_profit(self,
                              gas_savings: int,
                              chain_id: int) -> float:
        """Calculate profit from batch execution"""
        try:
            chain_config = config.get_chain_config(chain_id)
            gas_price = chain_config.get_gas_price()
            
            return gas_savings * gas_price
            
        except Exception as e:
            logger.error(f"Error calculating batch profit: {str(e)}")
            return 0.0

    def _calculate_risk_score(self, transactions: List[Dict]) -> float:
        """Calculate risk score for batch"""
        try:
            base_risk = 0.1 * len(transactions)  # More transactions = higher risk
            
            # Add risk for complex dependencies
            dependency_risk = len(self._create_dependency_graph(transactions)) * 0.05
            
            # Add risk for high value transactions
            value_risk = sum(tx.get('value', 0) for tx in transactions) * 0.0001
            
            return min(base_risk + dependency_risk + value_risk, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating risk score: {str(e)}")
            return 1.0

    def _calculate_confidence_score(self, transactions: List[Dict]) -> float:
        """Calculate confidence score for batch"""
        try:
            base_confidence = 1.0
            
            # Reduce confidence based on batch size
            size_factor = 1.0 - (len(transactions) * 0.05)
            
            # Reduce confidence based on dependencies
            dependency_factor = 1.0 - (len(self._create_dependency_graph(transactions)) * 0.1)
            
            return max(base_confidence * size_factor * dependency_factor, 0.0)
            
        except Exception as e:
            logger.error(f"Error calculating confidence score: {str(e)}")
            return 0.0

    def _determine_optimization_level(self, gas_savings: float) -> str:
        """Determine optimization level based on gas savings"""
        try:
            if gas_savings >= 1000000:
                return 'high'
            elif gas_savings >= 500000:
                return 'medium'
            else:
                return 'low'
                
        except Exception as e:
            logger.error(f"Error determining optimization level: {str(e)}")
            return 'low'

    def _encode_batch_data(self, transactions: List[Dict]) -> str:
        """Encode transaction data for batch execution"""
        try:
            # Implementation depends on specific batching mechanism
            return "0x"  # Placeholder
        except Exception as e:
            logger.error(f"Error encoding batch data: {str(e)}")
            return "0x"

    def _create_dependency_graph(self, transactions: List[Dict]) -> Dict[int, List[int]]:
        """Create dependency graph for transactions"""
        try:
            graph = {}
            
            for i, tx1 in enumerate(transactions):
                graph[i] = []
                for j, tx2 in enumerate(transactions):
                    if i != j and self._depends_on(tx1, tx2):
                        graph[i].append(j)
                        
            return graph
            
        except Exception as e:
            logger.error(f"Error creating dependency graph: {str(e)}")
            return {}

    def _depends_on(self, tx1: Dict, tx2: Dict) -> bool:
        """Check if transaction1 depends on transaction2"""
        try:
            # Check nonce dependency
            if tx1.get('nonce', 0) > tx2.get('nonce', 0):
                return True
                
            # Check state dependency
            tx1_reads = set(tx1.get('reads', []))
            tx2_writes = set(tx2.get('writes', []))
            
            return bool(tx1_reads.intersection(tx2_writes))
            
        except Exception as e:
            logger.error(f"Error checking dependencies: {str(e)}")
            return False

    def _topological_sort(self, graph: Dict[int, List[int]]) -> List[int]:
        """Perform topological sort on dependency graph"""
        try:
            visited = set()
            temp = set()
            order = []
            
            def visit(vertex):
                if vertex in temp:
                    raise ValueError("Cycle detected")
                if vertex not in visited:
                    temp.add(vertex)
                    for neighbor in graph.get(vertex, []):
                        visit(neighbor)
                    temp.remove(vertex)
                    visited.add(vertex)
                    order.insert(0, vertex)
                    
            for vertex in graph:
                if vertex not in visited:
                    visit(vertex)
                    
            return order
            
        except Exception as e:
            logger.error(f"Error in topological sort: {str(e)}")
            return list(graph.keys())
