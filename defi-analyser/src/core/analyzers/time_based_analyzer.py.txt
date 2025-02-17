# src/core/analyzers/time_based_analyzer.py

import asyncio
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from datetime import datetime, timedelta
from ...utils.config import config
from ...utils.logger import logger
from ...utils.state.state_manager import StateManager

@dataclass
class TimeWindow:
    start_time: int
    end_time: int
    block_range: tuple
    metrics: Dict
    events: List[Dict]
    patterns: List[Dict]

@dataclass
class TimeBasedAnalysis:
    protocol_address: str
    chain_id: int
    windows: List[TimeWindow]
    temporal_patterns: List[Dict]
    recurring_events: List[Dict]
    opportunity_windows: List[Dict]
    risk_periods: List[Dict]
    timestamp: float

class TimeBasedAnalyzer:
    def __init__(self):
        self.state_manager = StateManager()
        self.analyzed_windows: Dict[str, Set[int]] = {}
        self.pattern_history: Dict[str, List[Dict]] = {}
        
    async def analyze_time_patterns(self,
                                  protocol_address: str,
                                  chain_id: int,
                                  options: Optional[Dict] = None) -> Optional[TimeBasedAnalysis]:
        """Analyze time-based patterns and opportunities"""
        try:
            start_time = asyncio.get_event_loop().time()
            options = options or {}
            
            # Get protocol state
            state = await self.state_manager.get_state(chain_id)
            protocol_state = state.protocol_states.get(protocol_address, {})
            
            # Generate time windows
            windows = await self._generate_time_windows(
                protocol_address,
                chain_id,
                options
            )
            
            # Analyze temporal patterns
            temporal_patterns = await self._analyze_temporal_patterns(
                windows,
                protocol_address,
                chain_id
            )
            
            # Identify recurring events
            recurring_events = await self._identify_recurring_events(
                windows,
                protocol_address,
                chain_id
            )
            
            # Find opportunity windows
            opportunity_windows = await self._find_opportunity_windows(
                windows,
                temporal_patterns,
                recurring_events,
                chain_id
            )
            
            # Identify risk periods
            risk_periods = await self._identify_risk_periods(
                windows,
                temporal_patterns,
                recurring_events,
                chain_id
            )
            
            analysis = TimeBasedAnalysis(
                protocol_address=protocol_address,
                chain_id=chain_id,
                windows=windows,
                temporal_patterns=temporal_patterns,
                recurring_events=recurring_events,
                opportunity_windows=opportunity_windows,
                risk_periods=risk_periods,
                timestamp=start_time
            )
            
            # Update pattern history
            self._update_pattern_history(analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing time patterns: {str(e)}")
            return None

    async def _generate_time_windows(self,
                                   protocol_address: str,
                                   chain_id: int,
                                   options: Dict) -> List[TimeWindow]:
        """Generate analysis time windows"""
        try:
            windows = []
            window_size = options.get('window_size', 3600)  # 1 hour default
            lookback_period = options.get('lookback_period', 86400)  # 24 hours default
            
            current_time = int(datetime.now().timestamp())
            start_time = current_time - lookback_period
            
            while start_time < current_time:
                end_time = min(start_time + window_size, current_time)
                
                # Get block range for window
                start_block = await self._get_block_by_timestamp(
                    start_time,
                    chain_id
                )
                end_block = await self._get_block_by_timestamp(
                    end_time,
                    chain_id
                )
                
                # Get window metrics
                metrics = await self._get_window_metrics(
                    protocol_address,
                    chain_id,
                    start_time,
                    end_time
                )
                
                # Get window events
                events = await self._get_window_events(
                    protocol_address,
                    chain_id,
                    start_block,
                    end_block
                )
                
                # Get window patterns
                patterns = await self._get_window_patterns(
                    protocol_address,
                    chain_id,
                    start_time,
                    end_time
                )
                
                windows.append(TimeWindow(
                    start_time=start_time,
                    end_time=end_time,
                    block_range=(start_block, end_block),
                    metrics=metrics,
                    events=events,
                    patterns=patterns
                ))
                
                start_time = end_time
                
            return windows
            
        except Exception as e:
            logger.error(f"Error generating time windows: {str(e)}")
            return []

    async def _analyze_temporal_patterns(self,
                                       windows: List[TimeWindow],
                                       protocol_address: str,
                                       chain_id: int) -> List[Dict]:
        """Analyze temporal patterns across windows"""
        try:
            patterns = []
            
            # Analyze volume patterns
            volume_patterns = self._analyze_volume_patterns(windows)
            patterns.extend(volume_patterns)
            
            # Analyze price patterns
            price_patterns = self._analyze_price_patterns(windows)
            patterns.extend(price_patterns)
            
            # Analyze liquidity patterns
            liquidity_patterns = self._analyze_liquidity_patterns(windows)
            patterns.extend(liquidity_patterns)
            
            # Analyze user behavior patterns
            user_patterns = await self._analyze_user_patterns(
                windows,
                protocol_address,
                chain_id
            )
            patterns.extend(user_patterns)
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error analyzing temporal patterns: {str(e)}")
            return []

    async def _identify_recurring_events(self,
                                       windows: List[TimeWindow],
                                       protocol_address: str,
                                       chain_id: int) -> List[Dict]:
        """Identify recurring events and their patterns"""
        try:
            recurring_events = []
            
            # Group events by type
            event_groups = self._group_events_by_type(windows)
            
            for event_type, events in event_groups.items():
                # Analyze event timing
                timing_pattern = self._analyze_event_timing(events)
                
                if timing_pattern['is_recurring']:
                    recurring_events.append({
                        'event_type': event_type,
                        'frequency': timing_pattern['frequency'],
                        'confidence': timing_pattern['confidence'],
                        'next_expected': timing_pattern['next_expected'],
                        'impact_analysis': await self._analyze_event_impact(
                            events,
                            protocol_address,
                            chain_id
                        )
                    })
                    
            return recurring_events
            
        except Exception as e:
            logger.error(f"Error identifying recurring events: {str(e)}")
            return []

    async def _find_opportunity_windows(self,
                                      windows: List[TimeWindow],
                                      patterns: List[Dict],
                                      recurring_events: List[Dict],
                                      chain_id: int) -> List[Dict]:
        """Find windows of opportunity based on patterns"""
        try:
            opportunities = []
            
            for pattern in patterns:
                if pattern['type'] == 'volume_spike':
                    opps = self._find_volume_opportunities(
                        pattern,
                        windows
                    )
                    opportunities.extend(opps)
                    
                elif pattern['type'] == 'price_movement':
                    opps = self._find_price_opportunities(
                        pattern,
                        windows
                    )
                    opportunities.extend(opps)
                    
                elif pattern['type'] == 'liquidity_change':
                    opps = self._find_liquidity_opportunities(
                        pattern,
                        windows
                    )
                    opportunities.extend(opps)
                    
            # Add recurring event opportunities
            for event in recurring_events:
                if event['impact_analysis']['creates_opportunity']:
                    opportunities.append({
                        'type': 'recurring_event',
                        'event_type': event['event_type'],
                        'expected_time': event['next_expected'],
                        'confidence': event['confidence'],
                        'estimated_profit': event['impact_analysis']['potential_profit']
                    })
                    
            return opportunities
            
        except Exception as e:
            logger.error(f"Error finding opportunity windows: {str(e)}")
            return []

    def _update_pattern_history(self, analysis: TimeBasedAnalysis):
        """Update pattern history"""
        try:
            key = f"{analysis.protocol_address}_{analysis.chain_id}"
            
            if key not in self.pattern_history:
                self.pattern_history[key] = []
                
            # Add new patterns
            self.pattern_history[key].extend(analysis.temporal_patterns)
            
            # Limit history size
            if len(self.pattern_history[key]) > 1000:
                self.pattern_history[key] = self.pattern_history[key][-1000:]
                
        except Exception as e:
            logger.error(f"Error updating pattern history: {str(e)}")
