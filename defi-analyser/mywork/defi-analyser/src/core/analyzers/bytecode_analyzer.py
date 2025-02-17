from typing import Dict, List, Optional, Set, Tuple
from eth_utils import to_hex, function_signature_to_4byte_selector, encode_hex
from eth_hash.auto import keccak
from eth_abi import decode_single, encode_single
import logging
import re
from collections import defaultdict
import z3  # For symbolic execution
from z3 import BitVec, BitVecVal, Solver, sat, unsat, simplify
import networkx as nx
import itertools

logger = logging.getLogger(__name__)

class BytecodeAnalyzer:
    """Advanced analyzer for contract bytecode and decompilation"""

    # Expanded common signatures
    COMMON_SIGNATURES = {
        # ERC20
        '0x70a08231': 'balanceOf(address)',
        '0xa9059cbb': 'transfer(address,uint256)',
        '0x095ea7b3': 'approve(address,uint256)',
        '0x23b872dd': 'transferFrom(address,address,uint256)',
        # ERC721
        '0x6352211e': 'ownerOf(uint256)',
        '0x42842e0e': 'safeTransferFrom(address,address,uint256)',
        # Proxy
        '0x3659cfe6': 'upgradeTo(address)',
        '0x4f1ef286': 'upgradeToAndCall(address,bytes)',
        # Admin
        '0x8456cb59': 'pause()',
        '0x3f4ba83a': 'unpause()',
        # Add more advanced protocol signatures
        '0x150b7a02': 'onERC721Received(address,address,uint256,bytes)',
        '0xf23a6e61': 'onERC1155Received(address,address,uint256,uint256,bytes)',
        '0xbc197c81': 'onERC1155BatchReceived(address,address,uint256[],uint256[],bytes)',
        # Governance
        '0x7d5e81e2': 'propose(address[],uint256[],string[],bytes[],string)',
        '0x56781388': 'execute(uint256)',
        # DeFi
        '0x38ed1739': 'swapExactTokensForTokens(uint256,uint256,address[],address,uint256)',
        '0x5c11d795': 'flashLoan(address,address[],uint256[],bytes)',
    }

    # EVM Opcodes for analysis
    OPCODES = {
        '0x00': 'STOP',
        '0x01': 'ADD',
        # ... (full opcode map)
    }

    def __init__(self, web3_client):
        self.web3 = web3_client
        self.symbolic_executor = SymbolicExecutor()
        self.storage_analyzer = StorageAnalyzer()
        self.control_flow_analyzer = ControlFlowAnalyzer()
        self.cache = {}  # Add caching for expensive operations
        
    async def analyze_bytecode(self, contract_address: str, deep_analysis: bool = False) -> Dict:
        """Enhanced bytecode analysis with advanced features"""
        try:
            # Cache check
            cache_key = f"{contract_address}_{deep_analysis}"
            if cache_key in self.cache:
                return self.cache[cache_key]

            contract_address = self.web3.to_checksum_address(contract_address)
            
            # Get runtime and creation bytecode
            runtime_code = await self.web3.eth.get_code(contract_address)
            creation_code = await self._get_creation_code(contract_address)
            
            if runtime_code == '0x':
                return {'error': 'No bytecode found'}

            # Enhanced basic analysis
            analysis = {
                'functions': await self._map_functions(
                    await self._extract_function_selectors(runtime_code)
                ),
                'storage': await self._analyze_storage_layout(
                    contract_address, 
                    runtime_code,
                    historical=True  # Add historical storage analysis
                ),
                'patterns': await self._identify_patterns(
                    runtime_code, 
                    creation_code,
                    include_variants=True  # Check for pattern variants
                ),
                'interface': await self._generate_interface(
                    self.functions,
                    include_events=True,  # Include events in interface
                    include_errors=True   # Include custom errors
                ),
                'metrics': self._calculate_metrics(runtime_code),
            }

            if deep_analysis:
                # Enhanced advanced analysis
                analysis.update({
                    'control_flow': await self._analyze_control_flow(
                        runtime_code,
                        optimize_paths=True
                    ),
                    'symbolic_paths': await self._symbolic_execution(
                        runtime_code,
                        coverage_target=0.95  # Target 95% code coverage
                    ),
                    'storage_layout': await self._deep_storage_analysis(
                        contract_address,
                        include_historical=True
                    ),
                    'dependencies': await self._analyze_dependencies(
                        runtime_code,
                        recursive=True  # Analyze nested dependencies
                    ),
                    'security_analysis': await self._enhanced_security_scan(
                        runtime_code,
                        creation_code
                    ),
                    'gas_analysis': await self._analyze_gas_patterns(
                        runtime_code,
                        optimize=True
                    ),
                    'assembly_analysis': await self._analyze_assembly(
                        runtime_code,
                        detect_patterns=True
                    ),
                    'creation_analysis': await self._analyze_constructor(
                        creation_code,
                        trace_funds=True  # Track fund flows in constructor
                    ),
                    'cross_function_analysis': await self._analyze_cross_function_flows(
                        runtime_code
                    ),
                    'state_mutation_analysis': await self._analyze_state_mutations(
                        runtime_code
                    ),
                })

            # Cache results
            self.cache[cache_key] = analysis
            return analysis

        except Exception as e:
            logger.error(f"Error in advanced bytecode analysis: {str(e)}")
            return {'error': str(e)}

    async def _analyze_control_flow(self, bytecode: bytes) -> Dict:
        """Advanced control flow analysis"""
        try:
            # Build control flow graph
            cfg = self.control_flow_analyzer.build_cfg(bytecode)
            
            # Identify loops and their conditions
            loops = self.control_flow_analyzer.find_loops(cfg)
            
            # Find conditional branches
            branches = self.control_flow_analyzer.find_branches(cfg)
            
            # Identify function boundaries
            functions = self.control_flow_analyzer.identify_functions(cfg)
            
            return {
                'cfg': cfg.to_dict(),
                'loops': loops,
                'branches': branches,
                'functions': functions,
                'complexity': self.control_flow_analyzer.calculate_complexity(cfg)
            }
        except Exception as e:
            logger.error(f"Control flow analysis error: {str(e)}")
            return {}

    async def _symbolic_execution(self, bytecode: bytes) -> Dict:
        """Symbolic execution of bytecode paths"""
        try:
            # Initialize symbolic executor
            executor = self.symbolic_executor
            
            # Create symbolic variables for inputs
            symbolic_inputs = executor.create_symbolic_inputs()
            
            # Execute paths
            paths = executor.explore_paths(bytecode, symbolic_inputs)
            
            # Analyze path conditions
            conditions = executor.analyze_path_conditions(paths)
            
            # Find potential vulnerabilities
            vulnerabilities = executor.find_vulnerabilities(paths)
            
            return {
                'paths': paths,
                'conditions': conditions,
                'vulnerabilities': vulnerabilities,
                'coverage': executor.calculate_coverage(bytecode, paths)
            }
        except Exception as e:
            logger.error(f"Symbolic execution error: {str(e)}")
            return {}

    async def _deep_storage_analysis(self, contract_address: str) -> Dict:
        """Advanced storage layout analysis"""
        try:
            # Initialize storage analyzer
            analyzer = self.storage_analyzer
            
            # Get historical storage access patterns
            access_patterns = await analyzer.get_storage_access_patterns(contract_address)
            
            # Identify storage packing
            packing = analyzer.analyze_storage_packing(access_patterns)
            
            # Map complex data structures
            data_structures = analyzer.map_data_structures(access_patterns)
            
            # Detect storage collisions
            collisions = analyzer.detect_storage_collisions(access_patterns)
            
            return {
                'access_patterns': access_patterns,
                'packing': packing,
                'data_structures': data_structures,
                'collisions': collisions,
                'optimization_suggestions': analyzer.suggest_optimizations(packing)
            }
        except Exception as e:
            logger.error(f"Storage analysis error: {str(e)}")
            return {}

    async def _enhanced_security_scan(self, runtime_code: bytes, creation_code: bytes) -> Dict:
        """Enhanced security scanning with advanced detection"""
        vulnerabilities = []
        
        # Expanded security checks
        checks = {
            'reentrancy': {
                'checker': self._check_reentrancy,
                'params': {'cross_function': True, 'state_tracking': True}
            },
            'overflow': {
                'checker': self._check_overflow,
                'params': {'include_underflow': True}
            },
            'access_control': {
                'checker': self._check_access_control,
                'params': {'check_modifiers': True}
            },
            'delegatecall': {
                'checker': self._check_delegatecall,
                'params': {'trace_calls': True}
            },
            'tx_origin': {
                'checker': self._check_tx_origin,
                'params': {}
            },
            'timestamp_dependency': {
                'checker': self._check_timestamp,
                'params': {'block_number': True}
            },
            'assembly_usage': {
                'checker': self._check_assembly,
                'params': {'detect_patterns': True}
            },
            'selfdestruct': {
                'checker': self._check_selfdestruct,
                'params': {}
            },
            'unchecked_calls': {
                'checker': self._check_unchecked_calls,
                'params': {'external_only': True}
            },
            'arbitrary_jump': {
                'checker': self._check_arbitrary_jump,
                'params': {}
            },
            'dos_patterns': {
                'checker': self._check_dos_patterns,
                'params': {'gas_analysis': True}
            },
            'front_running': {
                'checker': self._check_front_running,
                'params': {'mev_analysis': True}
            }
        }
        
        results = {}
        for check_name, check_info in checks.items():
            try:
                result = await check_info['checker'](
                    runtime_code,
                    creation_code,
                    **check_info['params']
                )
                results[check_name] = result
                if result.get('vulnerable'):
                    vulnerabilities.append(result)
            except Exception as e:
                logger.error(f"Security check {check_name} failed: {str(e)}")
                
        return {
            'vulnerabilities': vulnerabilities,
            'check_results': results,
            'risk_score': self._calculate_risk_score(results),
            'mitigation_suggestions': self._generate_mitigations(vulnerabilities),
            'exploit_scenarios': self._generate_exploit_scenarios(vulnerabilities),
            'security_score': self._calculate_security_score(results),
            'audit_recommendations': self._generate_audit_recommendations(results)
        }

class SymbolicExecutor:
    """Handles symbolic execution of bytecode"""
    
    def __init__(self):
        self.solver = z3.Solver()
        self.path_conditions = []
        self.symbolic_vars = {}
        
    def create_symbolic_inputs(self) -> Dict:
        """Create symbolic variables for contract inputs"""
        symbolic_inputs = {
            'msg.value': z3.BitVec('msg.value', 256),
            'msg.sender': z3.BitVec('msg.sender', 160),
            'block.timestamp': z3.BitVec('block.timestamp', 256),
            'block.number': z3.BitVec('block.number', 256)
        }
        self.symbolic_vars.update(symbolic_inputs)
        return symbolic_inputs
        
    def explore_paths(self, bytecode: bytes, inputs: Dict) -> List[Dict]:
        """Symbolically execute different paths"""
        paths = []
        self.symbolic_vars.update(inputs)
        
        # Initialize execution state
        state = {
            'pc': 0,
            'stack': [],
            'memory': {},
            'storage': {},
            'path_condition': True
        }
        
        # Explore paths until fixed point
        while self._has_unexplored_paths(state):
            path = self._execute_path(bytecode, state)
            if path:
                paths.append(path)
                
        return paths
        
    def analyze_path_conditions(self, paths: List[Dict]) -> Dict:
        """Analyze conditions for each path"""
        analysis = {
            'feasible_paths': [],
            'infeasible_paths': [],
            'constraints': {},
            'invariants': []
        }
        
        for path in paths:
            if self._is_feasible(path['condition']):
                analysis['feasible_paths'].append(path)
            else:
                analysis['infeasible_paths'].append(path)
                
            analysis['constraints'][path['id']] = self._extract_constraints(path)
            
        analysis['invariants'] = self._find_invariants(paths)
        return analysis
        
    def find_vulnerabilities(self, paths: List[Dict]) -> List[Dict]:
        """Look for vulnerable patterns in execution paths"""
        vulnerabilities = []
        
        for path in paths:
            # Check for integer overflow
            overflow = self._check_overflow(path)
            if overflow:
                vulnerabilities.append(overflow)
                
            # Check for reentrancy
            reentrancy = self._check_reentrancy(path)
            if reentrancy:
                vulnerabilities.append(reentrancy)
                
            # Check for unchecked external calls
            unchecked = self._check_unchecked_calls(path)
            if unchecked:
                vulnerabilities.append(unchecked)
                
        return vulnerabilities

    def _execute_path(self, bytecode: bytes, state: Dict) -> Optional[Dict]:
        """Execute a single path through the bytecode"""
        path = {
            'id': len(self.path_conditions),
            'instructions': [],
            'condition': state['path_condition'],
            'effects': {
                'storage': {},
                'calls': [],
                'events': []
            }
        }
        
        while state['pc'] < len(bytecode):
            instruction = self._decode_instruction(bytecode, state['pc'])
            
            # Handle control flow
            if instruction.name in ['JUMP', 'JUMPI']:
                branches = self._handle_branch(state, instruction)
                if branches:
                    path['branches'] = branches
                    break
                    
            # Handle state changes
            if instruction.name in ['SSTORE', 'SLOAD']:
                self._handle_storage(state, instruction, path)
                
            # Handle external calls
            if instruction.name in ['CALL', 'DELEGATECALL']:
                self._handle_call(state, instruction, path)
                
            path['instructions'].append(instruction)
            state['pc'] += instruction.size
            
        return path

class StorageAnalyzer:
    """Advanced storage layout analysis"""
    
    def get_storage_access_patterns(self, address: str) -> Dict:
        """Analyze how storage is accessed"""
        patterns = {
            'reads': defaultdict(list),
            'writes': defaultdict(list),
            'access_frequency': defaultdict(int),
            'access_patterns': []
        }
        
        # Analyze storage access in functions
        for func_name, accesses in self._get_storage_accesses(address).items():
            for access in accesses:
                slot = access['slot']
                if access['type'] == 'read':
                    patterns['reads'][slot].append(func_name)
                else:
                    patterns['writes'][slot].append(func_name)
                patterns['access_frequency'][slot] += 1
                
        # Identify access patterns
        patterns['access_patterns'] = self._identify_patterns(patterns)
        return patterns
        
    def analyze_storage_packing(self, patterns: Dict) -> Dict:
        """Analyze how variables are packed"""
        packing = {
            'packed_slots': [],
            'unpacked_slots': [],
            'optimization_opportunities': []
        }
        
        # Find packed variables
        for slot, accesses in patterns['access_frequency'].items():
            if self._is_packed_slot(slot):
                packing['packed_slots'].append(self._analyze_packed_slot(slot))
            else:
                packing['unpacked_slots'].append(slot)
                
        # Find optimization opportunities
        packing['optimization_opportunities'] = self._find_packing_opportunities(
            packing['unpacked_slots']
        )
        
        return packing
        
    def map_data_structures(self, patterns: Dict) -> Dict:
        """Map complex data structures"""
        structures = {
            'arrays': [],
            'mappings': [],
            'nested': []
        }
        
        # Identify arrays
        for slot in patterns['access_patterns']:
            if self._is_array_access(slot):
                structures['arrays'].append(self._analyze_array(slot))
                
        # Identify mappings
        for slot in patterns['access_patterns']:
            if self._is_mapping_access(slot):
                structures['mappings'].append(self._analyze_mapping(slot))
                
        # Identify nested structures
        structures['nested'] = self._find_nested_structures(
            structures['arrays'],
            structures['mappings']
        )
        
        return structures

class ControlFlowAnalyzer:
    """Control flow graph analysis"""
    
    def build_cfg(self, bytecode: bytes) -> 'CFG':
        """Build control flow graph"""
        cfg = CFG()
        
        # First pass: identify basic blocks
        blocks = self._identify_basic_blocks(bytecode)
        
        # Second pass: connect blocks
        for block in blocks:
            successors = self._find_successors(block, blocks)
            cfg.add_block(block, successors)
            
        # Identify entry points
        cfg.entry_points = self._find_entry_points(cfg)
        
        return cfg
        
    def find_loops(self, cfg: 'CFG') -> List[Dict]:
        """Identify loops and conditions"""
        loops = []
        
        # Find strongly connected components
        sccs = self._find_sccs(cfg)
        
        # Analyze each potential loop
        for scc in sccs:
            if self._is_loop(scc):
                loop_info = {
                    'blocks': scc,
                    'condition': self._extract_loop_condition(scc),
                    'type': self._determine_loop_type(scc),
                    'variables': self._find_loop_variables(scc)
                }
                loops.append(loop_info)
                
        return loops
        
    def find_branches(self, cfg: 'CFG') -> List[Dict]:
        """Find conditional branches"""
        branches = []
        
        for block in cfg.blocks:
            if self._is_conditional_branch(block):
                branch_info = {
                    'block': block,
                    'condition': self._extract_branch_condition(block),
                    'true_branch': self._get_true_branch(block),
                    'false_branch': self._get_false_branch(block),
                    'variables': self._find_branch_variables(block)
                }
                branches.append(branch_info)
                
        return branches

class CFG:
    """Control Flow Graph implementation"""
    
    def __init__(self):
        self.blocks = []
        self.edges = defaultdict(list)
        self.entry_points = []
        
    def add_block(self, block: Dict, successors: List[Dict]):
        """Add a basic block and its successors to the CFG"""
        self.blocks.append(block)
        self.edges[block['id']] = [s['id'] for s in successors]
        
    def get_successors(self, block_id: int) -> List[Dict]:
        """Get successor blocks for a given block"""
        return [self.get_block(bid) for bid in self.edges[block_id]]
        
    def get_block(self, block_id: int) -> Optional[Dict]:
        """Get block by ID"""
        return next((b for b in self.blocks if b['id'] == block_id), None)
        
    def to_dict(self) -> Dict:
        """Convert CFG to dictionary representation"""
        return {
            'blocks': self.blocks,
            'edges': dict(self.edges),
            'entry_points': self.entry_points
        }