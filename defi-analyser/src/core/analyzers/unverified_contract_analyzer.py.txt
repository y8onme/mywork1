from octopus.platforms.ETH.explorer import EthereumExplorer
from octopus.platforms.ETH.cfg import EthereumCFG
from octopus.platforms.ETH.disassembler import EthereumDisassembler
from octopus.analysis.graph import CFGGraph
from octopus.core.function import Function
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class UnverifiedContractAnalyzer:
    """Analyzer for contracts with no verified source code using Octopus"""

    def __init__(self, web3_client):
        self.web3 = web3_client
        self.explorer = EthereumExplorer()
        
    async def analyze_unverified_contract(self, contract_address: str) -> Dict:
        """Analyze unverified contract bytecode"""
        try:
            # Get contract bytecode
            bytecode = await self.web3.eth.get_code(contract_address)
            if bytecode == '0x':
                return {'error': 'No bytecode found'}

            # Disassemble bytecode
            disassembler = EthereumDisassembler(bytecode)
            instructions = disassembler.disassemble()

            # Generate control flow graph
            cfg = EthereumCFG(instructions)
            cfg.visualize()  # Creates visual representation of the CFG

            # Extract functions
            functions = self._extract_functions(cfg)

            # Analyze storage layout
            storage = await self._analyze_storage_layout(contract_address, instructions)

            # Identify key patterns
            patterns = self._identify_patterns(instructions)

            # Generate pseudo-Solidity code
            pseudocode = self._generate_pseudocode(instructions, functions)

            return {
                'functions': functions,
                'storage_layout': storage,
                'patterns': patterns,
                'pseudocode': pseudocode,
                'cfg': cfg.graph.to_dict(),
                'possible_standard_interfaces': self._detect_standard_interfaces(functions)
            }

        except Exception as e:
            logger.error(f"Error analyzing unverified contract: {str(e)}")
            return {'error': str(e)}

    def _extract_functions(self, cfg: EthereumCFG) -> List[Dict]:
        """Extract function information from CFG"""
        functions = []
        
        for node in cfg.graph.nodes:
            if node.type == 'FUNCTION_ENTRY':
                function = {
                    'selector': node.function_selector,
                    'signature': self._reverse_function_selector(node.function_selector),
                    'entry_point': node.start_addr,
                    'exits': self._get_function_exits(node, cfg),
                    'instructions': self._get_function_instructions(node, cfg),
                    'calls': self._get_external_calls(node, cfg),
                    'storage_access': self._get_storage_access(node, cfg)
                }
                functions.append(function)

        return functions

    async def _analyze_storage_layout(self, address: str, instructions: List) -> Dict:
        """Analyze contract storage layout"""
        storage_layout = {
            'slots': {},
            'arrays': [],
            'mappings': []
        }

        # Track SLOAD and SSTORE instructions
        for instr in instructions:
            if instr.name in ['SLOAD', 'SSTORE']:
                slot = self._get_storage_slot(instr)
                if slot:
                    value = await self.web3.eth.get_storage_at(address, slot)
                    storage_layout['slots'][slot] = {
                        'value': value,
                        'access_type': 'read' if instr.name == 'SLOAD' else 'write',
                        'context': self._get_instruction_context(instr)
                    }

        # Detect arrays and mappings
        storage_layout.update(self._detect_complex_storage(instructions))

        return storage_layout

    def _identify_patterns(self, instructions: List) -> Dict:
        """Identify common patterns in bytecode"""
        patterns = {
            'proxy_pattern': False,
            'upgradeable': False,
            'erc20': False,
            'erc721': False,
            'access_control': False,
            'reentrancy_guard': False
        }

        # Check for proxy patterns
        if self._has_delegatecall(instructions):
            patterns['proxy_pattern'] = True
            patterns['upgradeable'] = self._check_upgradeability(instructions)

        # Check for standard interfaces
        patterns.update(self._check_standard_interfaces(instructions))

        # Check for security patterns
        patterns.update(self._check_security_patterns(instructions))

        return patterns

    def _generate_pseudocode(self, instructions: List, functions: List[Dict]) -> str:
        """Generate pseudo-Solidity code from bytecode"""
        pseudocode = []
        
        # Generate contract definition
        pseudocode.append("// Decompiled using Octopus\n")
        pseudocode.append("contract UnverifiedContract {")

        # Generate storage variables
        storage_vars = self._generate_storage_variables(instructions)
        pseudocode.extend(storage_vars)

        # Generate function definitions
        for function in functions:
            func_code = self._generate_function_code(function, instructions)
            pseudocode.extend(func_code)

        pseudocode.append("}")
        return "\n".join(pseudocode)

    def _detect_standard_interfaces(self, functions: List[Dict]) -> List[str]:
        """Detect standard interfaces implemented by the contract"""
        interfaces = []
        
        # ERC20 interface detection
        erc20_selectors = {
            '0x70a08231': 'balanceOf(address)',
            '0xa9059cbb': 'transfer(address,uint256)',
            '0x095ea7b3': 'approve(address,uint256)',
            '0x23b872dd': 'transferFrom(address,address,uint256)'
        }
        
        # ERC721 interface detection
        erc721_selectors = {
            '0x70a08231': 'balanceOf(address)',
            '0x6352211e': 'ownerOf(uint256)',
            '0x42842e0e': 'safeTransferFrom(address,address,uint256)'
        }

        # Check function selectors against known interfaces
        function_selectors = set(f['selector'] for f in functions)
        
        if all(selector in function_selectors for selector in erc20_selectors):
            interfaces.append('ERC20')
            
        if all(selector in function_selectors for selector in erc721_selectors):
            interfaces.append('ERC721')

        return interfaces

    def _has_delegatecall(self, instructions: List) -> bool:
        """Check if contract uses delegatecall"""
        return any(instr.name == 'DELEGATECALL' for instr in instructions)

    def _check_upgradeability(self, instructions: List) -> bool:
        """Check if contract is upgradeable"""
        # Look for storage patterns used in upgradeable contracts
        implementation_slots = [
            '0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc',  # EIP-1967
            '0x7050c9e0f4ca769c69bd3a8ef740bc37934f8e2c036e5a723fd8ee048ed3f8c3'   # OpenZeppelin
        ]
        
        return any(
            self._check_storage_slot_access(instr, slot)
            for instr in instructions
            for slot in implementation_slots
        )

    def _check_storage_slot_access(self, instruction, slot: str) -> bool:
        """Check if instruction accesses specific storage slot"""
        if instruction.name in ['SLOAD', 'SSTORE']:
            # Extract slot from instruction operands
            accessed_slot = self._get_storage_slot(instruction)
            return accessed_slot == slot
        return False

    def _get_instruction_context(self, instruction) -> Dict:
        """Get context information for an instruction"""
        return {
            'address': instruction.address,
            'function': self._get_containing_function(instruction),
            'basic_block': self._get_containing_block(instruction),
            'stack_impact': self._analyze_stack_impact(instruction)
        }

    def _analyze_stack_impact(self, instruction) -> Dict:
        """Analyze how instruction affects the stack"""
        return {
            'stack_push': instruction.stack_push,
            'stack_pop': instruction.stack_pop,
            'net_impact': instruction.stack_push - instruction.stack_pop
        } 