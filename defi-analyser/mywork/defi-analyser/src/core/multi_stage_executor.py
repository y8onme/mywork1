# src/core/multi_stage_executor.py

import asyncio
from typing import Dict, List, Optional
from dataclasses import dataclass

# Tool imports
from foundry import Foundry, AnvilFork
from hardhat import HardhatRuntime
from slither import Slither
from mythril.mythril import MythrilDisassembler, MythrilAnalyzer
from echidna import Echidna
from manticore.ethereum import ManticoreEVM
from crytic_compile import CryticCompile
from ape import networks, accounts
from brownie import network, Contract
from tenderly import TenderlyAPI

from ..utils.config import config
from ..utils.logger import logger
from .vulnerability_scanner import VulnerabilityScanner
from .exploit_development import ExploitDeveloper

@dataclass
class ExecutionStage:
    stage_id: str
    tool_requirements: List[str]
    execution_steps: List[Dict]
    validation_checks: List[str]
    dependencies: List[str]
    estimated_gas: int
    tool_configs: Dict[str, Dict]

@dataclass
class ExecutionResult:
    success: bool
    stages_completed: List[str]
    gas_used: int
    state_changes: Dict
    errors: List[Dict]
    tool_reports: Dict[str, Dict]

class MultiStageExecutor:
    def __init__(self):
        # Initialize all tools
        self.foundry = Foundry()
        self.hardhat = HardhatRuntime()
        self.mythril = MythrilAnalyzer()
        self.manticore = ManticoreEVM()
        self.echidna = Echidna()
        self.tenderly = TenderlyAPI(config.tenderly_api_key)
        
        # Initialize frameworks
        self._initialize_frameworks()
        
    def _initialize_frameworks(self):
        """Initialize all development frameworks"""
        # Initialize Brownie
        network.connect('mainnet-fork')
        
        # Initialize Ape
        networks.active_provider = networks.ethereum.mainnet_fork
        
        # Initialize Foundry fork
        self.anvil_fork = self.foundry.create_fork(
            config.rpc_url,
            self.web3.eth.block_number
        )
        
        # Initialize Hardhat
        self.hardhat.initialize_network('hardhat')

    async def execute_stages(self,
                           stages: List[ExecutionStage],
                           chain_id: int) -> ExecutionResult:
        """Execute multiple stages using all available tools"""
        try:
            results = ExecutionResult(
                success=True,
                stages_completed=[],
                gas_used=0,
                state_changes={},
                errors=[],
                tool_reports={}
            )
            
            # Create execution environment
            env = await self._setup_execution_environment(chain_id)
            
            # Execute each stage
            for stage in stages:
                # Verify dependencies
                if not self._verify_stage_dependencies(stage, results):
                    results.errors.append({
                        'stage': stage.stage_id,
                        'error': 'Dependencies not met'
                    })
                    results.success = False
                    break
                
                # Execute stage with all required tools
                stage_result = await self._execute_stage(stage, env, chain_id)
                
                # Process stage result
                if stage_result['success']:
                    results.stages_completed.append(stage.stage_id)
                    results.gas_used += stage_result['gas_used']
                    results.state_changes.update(stage_result['state_changes'])
                    results.tool_reports.update(stage_result['tool_reports'])
                else:
                    results.errors.append({
                        'stage': stage.stage_id,
                        'error': stage_result['error']
                    })
                    results.success = False
                    break
            
            return results
            
        except Exception as e:
            logger.error(f"Stage execution error: {str(e)}")
            return ExecutionResult(
                success=False,
                stages_completed=[],
                gas_used=0,
                state_changes={},
                errors=[{'error': str(e)}],
                tool_reports={}
            )

    async def _setup_execution_environment(self, chain_id: int) -> Dict:
        """Setup execution environment using all tools"""
        env = {}
        
        # Setup Foundry environment
        env['foundry'] = await self._setup_foundry_env(chain_id)
        
        # Setup Hardhat environment
        env['hardhat'] = await self._setup_hardhat_env(chain_id)
        
        # Setup other tool environments
        env['mythril'] = await self._setup_mythril_env(chain_id)
        env['manticore'] = await self._setup_manticore_env(chain_id)
        env['echidna'] = await self._setup_echidna_env(chain_id)
        
        return env

    async def _execute_stage(self,
                           stage: ExecutionStage,
                           env: Dict,
                           chain_id: int) -> Dict:
        """Execute single stage using required tools"""
        results = {
            'success': True,
            'gas_used': 0,
            'state_changes': {},
            'tool_reports': {},
            'error': None
        }
        
        # Execute with each required tool
        for tool in stage.tool_requirements:
            tool_result = await self._execute_with_tool(
                tool,
                stage,
                env[tool],
                chain_id
            )
            
            if not tool_result['success']:
                results['success'] = False
                results['error'] = tool_result['error']
                break
                
            results['gas_used'] += tool_result['gas_used']
            results['state_changes'].update(tool_result['state_changes'])
            results['tool_reports'][tool] = tool_result['report']
        
        return results

    async def _execute_with_tool(self,
                               tool: str,
                               stage: ExecutionStage,
                               env: Dict,
                               chain_id: int) -> Dict:
        """Execute stage steps with specific tool"""
        if tool == 'foundry':
            return await self._execute_with_foundry(stage, env, chain_id)
        elif tool == 'hardhat':
            return await self._execute_with_hardhat(stage, env, chain_id)
        elif tool == 'mythril':
            return await self._execute_with_mythril(stage, env)
        elif tool == 'manticore':
            return await self._execute_with_manticore(stage, env)
        elif tool == 'echidna':
            return await self._execute_with_echidna(stage, env)
        else:
            return {
                'success': False,
                'error': f'Unsupported tool: {tool}'
            }

    def _verify_stage_dependencies(self,
                                 stage: ExecutionStage,
                                 results: ExecutionResult) -> bool:
        """Verify stage dependencies are met"""
        return all(dep in results.stages_completed for dep in stage.dependencies)

    async def _setup_foundry_env(self, chain_id: int) -> Dict:
        """Setup Foundry execution environment"""
        try:
            # Create fork
            fork = await self.foundry.create_fork(
                config.get_chain_config(chain_id).rpc_url
            )
            
            # Setup test environment
            test_env = await self.foundry.setup_test_environment(fork)
            
            return {
                'fork': fork,
                'test_env': test_env,
                'contracts': {}
            }
            
        except Exception as e:
            logger.error(f"Foundry setup error: {str(e)}")
            return {}

    async def _setup_hardhat_env(self, chain_id: int) -> Dict:
        """Setup Hardhat execution environment"""
        try:
            # Initialize network
            network = await self.hardhat.init_network(chain_id)
            
            # Setup test environment
            test_env = await self.hardhat.setup_test_environment()
            
            return {
                'network': network,
                'test_env': test_env,
                'contracts': {}
            }
            
        except Exception as e:
            logger.error(f"Hardhat setup error: {str(e)}")
            return {}

    async def _setup_mythril_env(self, chain_id: int) -> Dict:
        """Setup Mythril execution environment"""
        try:
            # Initialize analyzer
            analyzer = MythrilDisassembler()
            
            return {
                'analyzer': analyzer,
                'chain_id': chain_id
            }
            
        except Exception as e:
            logger.error(f"Mythril setup error: {str(e)}")
            return {}

    async def _setup_manticore_env(self, chain_id: int) -> Dict:
        """Setup Manticore execution environment"""
        try:
            # Initialize EVM
            evm = ManticoreEVM()
            
            return {
                'evm': evm,
                'chain_id': chain_id
            }
            
        except Exception as e:
            logger.error(f"Manticore setup error: {str(e)}")
            return {}

    async def _setup_echidna_env(self, chain_id: int) -> Dict:
        """Setup Echidna execution environment"""
        try:
            # Initialize Echidna
            config = self.echidna.create_config()
            
            return {
                'config': config,
                'chain_id': chain_id
            }
            
        except Exception as e:
            logger.error(f"Echidna setup error: {str(e)}")
            return {}

    async def _execute_with_foundry(self,
                                  stage: ExecutionStage,
                                  env: Dict,
                                  chain_id: int) -> Dict:
        """Execute stage with Foundry"""
        try:
            results = {
                'success': True,
                'gas_used': 0,
                'state_changes': {},
                'report': {},
                'error': None
            }
            
            # Execute each step
            for step in stage.execution_steps:
                step_result = await self.foundry.execute_step(
                    step,
                    env['fork'],
                    env['test_env']
                )
                
                if not step_result['success']:
                    results['success'] = False
                    results['error'] = step_result['error']
                    break
                
                results['gas_used'] += step_result['gas_used']
                results['state_changes'].update(step_result['state_changes'])
            
            # Generate report
            if results['success']:
                results['report'] = await self.foundry.generate_report(
                    env['fork'],
                    stage.stage_id
                )
            
            return results
            
        except Exception as e:
            return {
                'success': False,
                'gas_used': 0,
                'state_changes': {},
                'report': {},
                'error': str(e)
            }

    async def _execute_with_hardhat(self,
                                  stage: ExecutionStage,
                                  env: Dict,
                                  chain_id: int) -> Dict:
        """Execute stage with Hardhat"""
        try:
            results = {
                'success': True,
                'gas_used': 0,
                'state_changes': {},
                'report': {},
                'error': None
            }
            
            # Execute each step
            for step in stage.execution_steps:
                step_result = await self.hardhat.execute_step(
                    step,
                    env['network'],
                    env['test_env']
                )
                
                if not step_result['success']:
                    results['success'] = False
                    results['error'] = step_result['error']
                    break
                
                results['gas_used'] += step_result['gas_used']
                results['state_changes'].update(step_result['state_changes'])
            
            # Generate report
            if results['success']:
                results['report'] = await self.hardhat.generate_report(
                    env['network'],
                    stage.stage_id
                )
            
            return results
            
        except Exception as e:
            return {
                'success': False,
                'gas_used': 0,
                'state_changes': {},
                'report': {},
                'error': str(e)
            }

    async def _execute_with_mythril(self,
                                  stage: ExecutionStage,
                                  env: Dict) -> Dict:
        """Execute stage with Mythril"""
        try:
            results = {
                'success': True,
                'gas_used': 0,
                'state_changes': {},
                'report': {},
                'error': None
            }
            
            # Analyze each step
            for step in stage.execution_steps:
                step_result = await self.mythril.analyze_step(
                    step,
                    env['analyzer']
                )
                
                if not step_result['success']:
                    results['success'] = False
                    results['error'] = step_result['error']
                    break
                
                results['state_changes'].update(step_result['state_changes'])
            
            # Generate report
            if results['success']:
                results['report'] = await self.mythril.generate_report(
                    env['analyzer'],
                    stage.stage_id
                )
            
            return results
            
        except Exception as e:
            return {
                'success': False,
                'gas_used': 0,
                'state_changes': {},
                'report': {},
                'error': str(e)
            }

    async def _execute_with_manticore(self,
                                    stage: ExecutionStage,
                                    env: Dict) -> Dict:
        """Execute stage with Manticore"""
        try:
            results = {
                'success': True,
                'gas_used': 0,
                'state_changes': {},
                'report': {},
                'error': None
            }
            
            # Execute each step
            for step in stage.execution_steps:
                step_result = await self.manticore.execute_step(
                    step,
                    env['evm']
                )
                
                if not step_result['success']:
                    results['success'] = False
                    results['error'] = step_result['error']
                    break
                
                results['state_changes'].update(step_result['state_changes'])
            
            # Generate report
            if results['success']:
                results['report'] = await self.manticore.generate_report(
                    env['evm'],
                    stage.stage_id
                )
            
            return results
            
        except Exception as e:
            return {
                'success': False,
                'gas_used': 0,
                'state_changes': {},
                'report': {},
                'error': str(e)
            }

    async def _execute_with_echidna(self,
                                  stage: ExecutionStage,
                                  env: Dict) -> Dict:
        """Execute stage with Echidna"""
        try:
            results = {
                'success': True,
                'gas_used': 0,
                'state_changes': {},
                'report': {},
                'error': None
            }
            
            # Execute each step
            for step in stage.execution_steps:
                step_result = await self.echidna.execute_step(
                    step,
                    env['config']
                )
                
                if not step_result['success']:
                    results['success'] = False
                    results['error'] = step_result['error']
                    break
                
                results['state_changes'].update(step_result['state_changes'])
            
            # Generate report
            if results['success']:
                results['report'] = await self.echidna.generate_report(
                    env['config'],
                    stage.stage_id
                )
            
            return results
            
        except Exception as e:
            return {
                'success': False,
                'gas_used': 0,
                'state_changes': {},
                'report': {},
                'error': str(e)
            }