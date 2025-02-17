# src/core/analysis_orchestrator.py

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
from .cross_protocol_analyzer import CrossProtocolAnalyzer
from .attack_optimizer import AttackOptimizer

@dataclass
class AnalysisResult:
    vulnerabilities: List[Dict]
    exploits: List[Dict]
    cross_protocol_vectors: List[Dict]
    optimized_attacks: List[Dict]
    chain_id: int
    timestamp: float
    tool_reports: Dict[str, Dict]
    risk_assessment: Dict
    confidence_score: float

class AnalysisOrchestrator:
    def __init__(self):
        # Initialize all tools
        self.foundry = Foundry()
        self.hardhat = HardhatRuntime()
        self.mythril = MythrilAnalyzer()
        self.manticore = ManticoreEVM()
        self.echidna = Echidna()
        self.tenderly = TenderlyAPI(config.tenderly_api_key)
        
        # Initialize analysis components
        self.vulnerability_scanner = VulnerabilityScanner()
        self.exploit_developer = ExploitDeveloper()
        self.cross_protocol_analyzer = CrossProtocolAnalyzer()
        self.attack_optimizer = AttackOptimizer()
        
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

    async def analyze_protocol(self,
                             contract_address: str,
                             chain_id: int,
                             options: Optional[Dict] = None) -> AnalysisResult:
        """
        Orchestrate complete protocol analysis using all tools
        """
        try:
            # Scan for vulnerabilities using all tools
            vulnerabilities = await self._scan_vulnerabilities(
                contract_address,
                chain_id
            )
            
            if not vulnerabilities:
                return self._create_empty_result(chain_id)
            
            # Develop exploits for vulnerabilities
            exploits = await self._develop_exploits(
                vulnerabilities,
                chain_id
            )
            
            # Analyze cross-protocol vectors
            cross_protocol = await self._analyze_cross_protocol(
                vulnerabilities,
                chain_id
            )
            
            # Optimize attack vectors
            optimized_attacks = await self._optimize_attacks(
                exploits,
                cross_protocol,
                chain_id
            )
            
            # Collect tool reports
            tool_reports = await self._collect_tool_reports(
                contract_address,
                chain_id
            )
            
            # Assess risks
            risk_assessment = self._assess_risks(
                vulnerabilities,
                exploits,
                cross_protocol
            )
            
            # Calculate confidence
            confidence_score = self._calculate_confidence(
                tool_reports,
                vulnerabilities,
                exploits
            )
            
            return AnalysisResult(
                vulnerabilities=vulnerabilities,
                exploits=exploits,
                cross_protocol_vectors=cross_protocol,
                optimized_attacks=optimized_attacks,
                chain_id=chain_id,
                timestamp=asyncio.get_event_loop().time(),
                tool_reports=tool_reports,
                risk_assessment=risk_assessment,
                confidence_score=confidence_score
            )
            
        except Exception as e:
            logger.error(f"Analysis orchestration error: {str(e)}")
            return self._create_empty_result(chain_id)

    async def _scan_vulnerabilities(self,
                                  contract_address: str,
                                  chain_id: int) -> List[Dict]:
        """
        Scan for vulnerabilities using all available tools
        """
        # Foundry scan
        foundry_results = await self._scan_with_foundry(
            contract_address,
            chain_id
        )
        
        # Hardhat scan
        hardhat_results = await self._scan_with_hardhat(
            contract_address,
            chain_id
        )
        
        # Mythril scan
        mythril_results = await self._scan_with_mythril(
            contract_address,
            chain_id
        )
        
        # Manticore scan
        manticore_results = await self._scan_with_manticore(
            contract_address,
            chain_id
        )
        
        # Echidna scan
        echidna_results = await self._scan_with_echidna(
            contract_address,
            chain_id
        )
        
        # Combine and deduplicate results
        all_results = []
        all_results.extend(foundry_results)
        all_results.extend(hardhat_results)
        all_results.extend(mythril_results)
        all_results.extend(manticore_results)
        all_results.extend(echidna_results)
        
        return self._deduplicate_vulnerabilities(all_results)

    async def _develop_exploits(self,
                              vulnerabilities: List[Dict],
                              chain_id: int) -> List[Dict]:
        """
        Develop exploits using all available tools
        """
        exploits = []
        
        for vuln in vulnerabilities:
            # Develop with Foundry
            foundry_exploit = await self._develop_with_foundry(
                vuln,
                chain_id
            )
            if foundry_exploit:
                exploits.append(foundry_exploit)
            
            # Develop with Hardhat
            hardhat_exploit = await self._develop_with_hardhat(
                vuln,
                chain_id
            )
            if hardhat_exploit:
                exploits.append(hardhat_exploit)
            
            # Develop with other tools
            other_exploits = await self._develop_with_other_tools(
                vuln,
                chain_id
            )
            exploits.extend(other_exploits)
        
        return self._deduplicate_exploits(exploits)

    async def _analyze_cross_protocol(self,
                                    vulnerabilities: List[Dict],
                                    chain_id: int) -> List[Dict]:
        """
        Analyze cross-protocol attack vectors using all tools
        """
        vectors = []
        
        # Analyze with each tool
        for vuln in vulnerabilities:
            tool_vectors = await self._analyze_with_all_tools(
                vuln,
                chain_id
            )
            vectors.extend(tool_vectors)
        
        return self._deduplicate_vectors(vectors)

    async def _optimize_attacks(self,
                              exploits: List[Dict],
                              cross_protocol: List[Dict],
                              chain_id: int) -> List[Dict]:
        """
        Optimize attack vectors using all available tools
        """
        optimized = []
        
        # Optimize with each tool
        for exploit in exploits:
            tool_optimizations = await self._optimize_with_all_tools(
                exploit,
                cross_protocol,
                chain_id
            )
            optimized.extend(tool_optimizations)
        
        return self._deduplicate_optimizations(optimized)

    async def _collect_tool_reports(self,
                                  contract_address: str,
                                  chain_id: int) -> Dict[str, Dict]:
        """
        Collect reports from all analysis tools
        """
        return {
            'foundry': await self._get_foundry_report(contract_address, chain_id),
            'hardhat': await self._get_hardhat_report(contract_address, chain_id),
            'mythril': await self._get_mythril_report(contract_address, chain_id),
            'manticore': await self._get_manticore_report(contract_address, chain_id),
            'echidna': await self._get_echidna_report(contract_address, chain_id),
            'slither': await self._get_slither_report(contract_address, chain_id),
            'crytic': await self._get_crytic_report(contract_address, chain_id),
            'ape': await self._get_ape_report(contract_address, chain_id),
            'brownie': await self._get_brownie_report(contract_address, chain_id),
            'tenderly': await self._get_tenderly_report(contract_address, chain_id)
        }

    def _assess_risks(self,
                     vulnerabilities: List[Dict],
                     exploits: List[Dict],
                     cross_protocol: List[Dict]) -> Dict:
        """
        Assess overall risks using all tool inputs
        """
        risk_scores = {
            'vulnerability_risk': self._calculate_vulnerability_risk(vulnerabilities),
            'exploit_risk': self._calculate_exploit_risk(exploits),
            'cross_protocol_risk': self._calculate_cross_protocol_risk(cross_protocol),
            'tool_specific_risks': self._calculate_tool_specific_risks(
                vulnerabilities,
                exploits,
                cross_protocol
            )
        }
        
        return {
            'risk_scores': risk_scores,
            'overall_risk': sum(risk_scores.values()) / len(risk_scores),
            'risk_factors': self._identify_risk_factors(risk_scores),
            'mitigation_suggestions': self._generate_mitigation_suggestions(risk_scores)
        }

    def _calculate_confidence(self,
                            tool_reports: Dict[str, Dict],
                            vulnerabilities: List[Dict],
                            exploits: List[Dict]) -> float:
        """
        Calculate confidence score based on all tool results
        """
        confidence_factors = []
        
        # Tool report confidence
        for tool, report in tool_reports.items():
            if report.get('success'):
                confidence_factors.append(0.1)
            if report.get('high_confidence_findings'):
                confidence_factors.append(0.2)
        
        # Vulnerability confidence
        if vulnerabilities:
            confidence_factors.append(
                sum(v.get('confidence', 0) for v in vulnerabilities) / len(vulnerabilities)
            )
        
        # Exploit confidence
        if exploits:
            confidence_factors.append(
                sum(e.get('success_probability', 0) for e in exploits) / len(exploits)
            )
        
        return min(sum(confidence_factors), 1.0)

    def _create_empty_result(self, chain_id: int) -> AnalysisResult:
        """Create empty result for failed analysis"""
        return AnalysisResult(
            vulnerabilities=[],
            exploits=[],
            cross_protocol_vectors=[],
            optimized_attacks=[],
            chain_id=chain_id,
            timestamp=asyncio.get_event_loop().time(),
            tool_reports={},
            risk_assessment={
                'risk_scores': {},
                'overall_risk': 0.0,
                'risk_factors': [],
                'mitigation_suggestions': []
            },
            confidence_score=0.0
        )

    def _deduplicate_vulnerabilities(self, vulnerabilities: List[Dict]) -> List[Dict]:
        """Deduplicate vulnerability findings"""
        seen = set()
        unique = []
        
        for vuln in vulnerabilities:
            key = f"{vuln['type']}_{vuln['location']}_{vuln['severity']}"
            if key not in seen:
                seen.add(key)
                unique.append(vuln)
        
        return unique

    def _deduplicate_exploits(self, exploits: List[Dict]) -> List[Dict]:
        """Deduplicate exploit findings"""
        seen = set()
        unique = []
        
        for exploit in exploits:
            key = f"{exploit['vulnerability_id']}_{exploit['type']}"
            if key not in seen:
                seen.add(key)
                unique.append(exploit)
        
        return unique

    def _deduplicate_vectors(self, vectors: List[Dict]) -> List[Dict]:
        """Deduplicate cross-protocol vectors"""
        seen = set()
        unique = []
        
        for vector in vectors:
            key = f"{vector['source']}_{vector['target']}_{vector['type']}"
            if key not in seen:
                seen.add(key)
                unique.append(vector)
        
        return unique

    def _deduplicate_optimizations(self, optimizations: List[Dict]) -> List[Dict]:
        """Deduplicate optimized attacks"""
        seen = set()
        unique = []
        
        for opt in optimizations:
            key = f"{opt['exploit_id']}_{opt['optimization_type']}"
            if key not in seen:
                seen.add(key)
                unique.append(opt)
        
        return unique

    def _calculate_vulnerability_risk(self, vulnerabilities: List[Dict]) -> float:
        """Calculate vulnerability risk score"""
        if not vulnerabilities:
            return 0.0
            
        total_risk = sum(
            v.get('severity_score', 0) * v.get('confidence', 0)
            for v in vulnerabilities
        )
        
        return total_risk / len(vulnerabilities)

    def _calculate_exploit_risk(self, exploits: List[Dict]) -> float:
        """Calculate exploit risk score"""
        if not exploits:
            return 0.0
            
        total_risk = sum(
            e.get('success_probability', 0) * e.get('impact_score', 0)
            for e in exploits
        )
        
        return total_risk / len(exploits)

    def _calculate_cross_protocol_risk(self, vectors: List[Dict]) -> float:
        """Calculate cross-protocol risk score"""
        if not vectors:
            return 0.0
            
        total_risk = sum(
            v.get('risk_score', 0) * v.get('confidence', 0)
            for v in vectors
        )
        
        return total_risk / len(vectors)

    def _calculate_tool_specific_risks(self,
                                     vulnerabilities: List[Dict],
                                     exploits: List[Dict],
                                     cross_protocol: List[Dict]) -> Dict[str, float]:
        """Calculate tool-specific risk scores"""
        return {
            'foundry_risk': self._calculate_foundry_risk(vulnerabilities, exploits),
            'hardhat_risk': self._calculate_hardhat_risk(vulnerabilities, exploits),
            'mythril_risk': self._calculate_mythril_risk(vulnerabilities),
            'manticore_risk': self._calculate_manticore_risk(vulnerabilities),
            'echidna_risk': self._calculate_echidna_risk(vulnerabilities, exploits),
            'slither_risk': self._calculate_slither_risk(vulnerabilities),
            'crytic_risk': self._calculate_crytic_risk(vulnerabilities, cross_protocol),
            'ape_risk': self._calculate_ape_risk(exploits),
            'brownie_risk': self._calculate_brownie_risk(exploits),
            'tenderly_risk': self._calculate_tenderly_risk(exploits, cross_protocol)
        }

    def _identify_risk_factors(self, risk_scores: Dict) -> List[Dict]:
        """Identify key risk factors"""
        factors = []
        
        for category, score in risk_scores.items():
            if score > 0.7:
                factors.append({
                    'category': category,
                    'risk_level': 'high',
                    'score': score,
                    'description': self._get_risk_description(category, score)
                })
            elif score > 0.4:
                factors.append({
                    'category': category,
                    'risk_level': 'medium',
                    'score': score,
                    'description': self._get_risk_description(category, score)
                })
        
        return factors

    def _generate_mitigation_suggestions(self, risk_scores: Dict) -> List[Dict]:
        """Generate mitigation suggestions based on risk scores"""
        suggestions = []
        
        for category, score in risk_scores.items():
            if score > 0.4:
                suggestions.extend(
                    self._get_mitigation_suggestions(category, score)
                )
        
        return suggestions

    def _get_risk_description(self, category: str, score: float) -> str:
        """Get description for risk category and score"""
        # Implementation for risk descriptions
        return f"Risk description for {category} with score {score}"

    def _get_mitigation_suggestions(self, category: str, score: float) -> List[Dict]:
        """Get mitigation suggestions for risk category"""
        # Implementation for mitigation suggestions
        return [{
            'category': category,
            'priority': 'high' if score > 0.7 else 'medium',
            'suggestion': f"Mitigation suggestion for {category}"
        }]