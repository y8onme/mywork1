# src/core/cross_protocol_analyzer.py

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

@dataclass
class CrossProtocolVector:
    source_protocol: str
    target_protocol: str
    interaction_type: str
    required_conditions: List[Dict]
    estimated_impact: Dict
    execution_steps: List[Dict]
    tool_validations: Dict[str, Dict]

@dataclass
class AnalysisResult:
    vectors: List[CrossProtocolVector]
    risk_assessment: Dict
    tool_reports: Dict[str, Dict]
    confidence_score: float

class CrossProtocolAnalyzer:
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

    async def analyze_cross_protocol_vectors(self,
                                          protocols: List[str],
                                          chain_id: int) -> AnalysisResult:
        """Analyze cross-protocol attack vectors using all tools"""
        try:
            # Setup analysis environment
            env = await self._setup_analysis_environment(chain_id)
            
            # Find potential vectors
            vectors = []
            tool_reports = {}
            
            # Analyze with Foundry
            foundry_result = await self._analyze_with_foundry(
                protocols,
                env,
                chain_id
            )
            vectors.extend(foundry_result['vectors'])
            tool_reports['foundry'] = foundry_result['report']
            
            # Analyze with Hardhat
            hardhat_result = await self._analyze_with_hardhat(
                protocols,
                env,
                chain_id
            )
            vectors.extend(hardhat_result['vectors'])
            tool_reports['hardhat'] = hardhat_result['report']
            
            # Analyze with Mythril
            mythril_result = await self._analyze_with_mythril(
                protocols,
                env
            )
            vectors.extend(mythril_result['vectors'])
            tool_reports['mythril'] = mythril_result['report']
            
            # Analyze with Manticore
            manticore_result = await self._analyze_with_manticore(
                protocols,
                env
            )
            vectors.extend(manticore_result['vectors'])
            tool_reports['manticore'] = manticore_result['report']
            
            # Analyze with Echidna
            echidna_result = await self._analyze_with_echidna(
                protocols,
                env
            )
            vectors.extend(echidna_result['vectors'])
            tool_reports['echidna'] = echidna_result['report']
            
            # Deduplicate vectors
            unique_vectors = self._deduplicate_vectors(vectors)
            
            # Assess risks
            risk_assessment = self._assess_risks(
                unique_vectors,
                tool_reports
            )
            
            # Calculate confidence
            confidence_score = self._calculate_confidence(
                unique_vectors,
                tool_reports
            )
            
            return AnalysisResult(
                vectors=unique_vectors,
                risk_assessment=risk_assessment,
                tool_reports=tool_reports,
                confidence_score=confidence_score
            )
            
        except Exception as e:
            logger.error(f"Cross-protocol analysis error: {str(e)}")
            return AnalysisResult(
                vectors=[],
                risk_assessment={},
                tool_reports={},
                confidence_score=0.0
            )

    async def _setup_analysis_environment(self, chain_id: int) -> Dict:
        """Setup analysis environment using all tools"""
        env = {}
        
        # Setup Foundry environment
        env['foundry'] = await self._setup_foundry_env(chain_id)
        
        # Setup Hardhat environment
        env['hardhat'] = await self._setup_hardhat_env(chain_id)
        
        # Setup other tool environments
        env['mythril'] = await self._setup_mythril_env()
        env['manticore'] = await self._setup_manticore_env()
        env['echidna'] = await self._setup_echidna_env()
        
        return env

    async def _analyze_with_foundry(self,
                                  protocols: List[str],
                                  env: Dict,
                                  chain_id: int) -> Dict:
        """Analyze using Foundry"""
        try:
            vectors = []
            
            # Analyze protocol interactions
            for i, source in enumerate(protocols):
                for target in protocols[i+1:]:
                    vector = await self.foundry.analyze_interaction(
                        source,
                        target,
                        env['foundry']
                    )
                    if vector:
                        vectors.append(vector)
            
            # Generate analysis report
            report = await self.foundry.generate_analysis_report(
                vectors,
                env['foundry']
            )
            
            return {
                'vectors': vectors,
                'report': report
            }
            
        except Exception as e:
            logger.error(f"Foundry analysis error: {str(e)}")
            return {
                'vectors': [],
                'report': {'error': str(e)}
            }

    async def _analyze_with_hardhat(self,
                                  protocols: List[str],
                                  env: Dict,
                                  chain_id: int) -> Dict:
        """Analyze using Hardhat"""
        try:
            vectors = []
            
            # Analyze protocol interactions
            for i, source in enumerate(protocols):
                for target in protocols[i+1:]:
                    vector = await self.hardhat.analyze_interaction(
                        source,
                        target,
                        env['hardhat']
                    )
                    if vector:
                        vectors.append(vector)
            
            # Generate analysis report
            report = await self.hardhat.generate_analysis_report(
                vectors,
                env['hardhat']
            )
            
            return {
                'vectors': vectors,
                'report': report
            }
            
        except Exception as e:
            logger.error(f"Hardhat analysis error: {str(e)}")
            return {
                'vectors': [],
                'report': {'error': str(e)}
            }

    async def _analyze_with_mythril(self,
                                  protocols: List[str],
                                  env: Dict) -> Dict:
        """Analyze using Mythril"""
        try:
            vectors = []
            
            # Analyze protocol interactions
            for i, source in enumerate(protocols):
                for target in protocols[i+1:]:
                    vector = await self.mythril.analyze_interaction(
                        source,
                        target,
                        env['mythril']
                    )
                    if vector:
                        vectors.append(vector)
            
            # Generate analysis report
            report = await self.mythril.generate_analysis_report(
                vectors
            )
            
            return {
                'vectors': vectors,
                'report': report
            }
            
        except Exception as e:
            logger.error(f"Mythril analysis error: {str(e)}")
            return {
                'vectors': [],
                'report': {'error': str(e)}
            }

    async def _analyze_with_manticore(self,
                                    protocols: List[str],
                                    env: Dict) -> Dict:
        """Analyze using Manticore"""
        try:
            vectors = []
            
            # Analyze protocol interactions
            for i, source in enumerate(protocols):
                for target in protocols[i+1:]:
                    vector = await self.manticore.analyze_interaction(
                        source,
                        target,
                        env['manticore']
                    )
                    if vector:
                        vectors.append(vector)
            
            # Generate analysis report
            report = await self.manticore.generate_analysis_report(
                vectors
            )
            
            return {
                'vectors': vectors,
                'report': report
            }
            
        except Exception as e:
            logger.error(f"Manticore analysis error: {str(e)}")
            return {
                'vectors': [],
                'report': {'error': str(e)}
            }

    async def _analyze_with_echidna(self,
                                  protocols: List[str],
                                  env: Dict) -> Dict:
        """Analyze using Echidna"""
        try:
            vectors = []
            
            # Analyze protocol interactions
            for i, source in enumerate(protocols):
                for target in protocols[i+1:]:
                    vector = await self.echidna.analyze_interaction(
                        source,
                        target,
                        env['echidna']
                    )
                    if vector:
                        vectors.append(vector)
            
            # Generate analysis report
            report = await self.echidna.generate_analysis_report(
                vectors
            )
            
            return {
                'vectors': vectors,
                'report': report
            }
            
        except Exception as e:
            logger.error(f"Echidna analysis error: {str(e)}")
            return {
                'vectors': [],
                'report': {'error': str(e)}
            }

    def _deduplicate_vectors(self, vectors: List[CrossProtocolVector]) -> List[CrossProtocolVector]:
        """Deduplicate cross-protocol vectors"""
        seen = set()
        unique = []
        
        for vector in vectors:
            key = f"{vector.source_protocol}_{vector.target_protocol}_{vector.interaction_type}"
            if key not in seen:
                seen.add(key)
                unique.append(vector)
        
        return unique

    def _assess_risks(self,
                     vectors: List[CrossProtocolVector],
                     tool_reports: Dict[str, Dict]) -> Dict:
        """Assess risks from cross-protocol vectors"""
        assessment = {
            'risk_scores': {},
            'high_risk_vectors': [],
            'medium_risk_vectors': [],
            'low_risk_vectors': []
        }
        
        for vector in vectors:
            risk_score = self._calculate_vector_risk(vector, tool_reports)
            
            assessment['risk_scores'][f"{vector.source_protocol}_{vector.target_protocol}"] = risk_score
            
            if risk_score > 0.7:
                assessment['high_risk_vectors'].append(vector)
            elif risk_score > 0.4:
                assessment['medium_risk_vectors'].append(vector)
            else:
                assessment['low_risk_vectors'].append(vector)
        
        return assessment

    def _calculate_vector_risk(self,
                             vector: CrossProtocolVector,
                             tool_reports: Dict[str, Dict]) -> float:
        """Calculate risk score for vector"""
        base_risk = 0.5
        
        # Adjust based on impact
        if vector.estimated_impact.get('severity') == 'high':
            base_risk += 0.3
        elif vector.estimated_impact.get('severity') == 'medium':
            base_risk += 0.2
        
        # Adjust based on tool validations
        for tool, validation in vector.tool_validations.items():
            if validation.get('confirmed'):
                base_risk += 0.1
            if validation.get('high_confidence'):
                base_risk += 0.1
        
        return min(base_risk, 1.0)

    def _calculate_confidence(self,
                            vectors: List[CrossProtocolVector],
                            tool_reports: Dict[str, Dict]) -> float:
        """Calculate confidence score for analysis"""
        if not vectors:
            return 0.0
            
        confidence_scores = []
        
        for vector in vectors:
            vector_confidence = 0.5
            
            # Add confidence from tool validations
            for tool, validation in vector.tool_validations.items():
                if validation.get('confirmed'):
                    vector_confidence += 0.1
                if validation.get('high_confidence'):
                    vector_confidence += 0.1
            
            confidence_scores.append(min(vector_confidence, 1.0))
        
        return sum(confidence_scores) / len(confidence_scores)

    async def _setup_foundry_env(self, chain_id: int) -> Dict:
        """Setup Foundry environment"""
        # Implementation for Foundry environment setup
        return {}

    async def _setup_hardhat_env(self, chain_id: int) -> Dict:
        """Setup Hardhat environment"""
        # Implementation for Hardhat environment setup
        return {}

    async def _setup_mythril_env(self) -> Dict:
        """Setup Mythril environment"""
        # Implementation for Mythril environment setup
        return {}

    async def _setup_manticore_env(self) -> Dict:
        """Setup Manticore environment"""
        # Implementation for Manticore environment setup
        return {}

    async def _setup_echidna_env(self) -> Dict:
        """Setup Echidna environment"""
        # Implementation for Echidna environment setup
        return {}