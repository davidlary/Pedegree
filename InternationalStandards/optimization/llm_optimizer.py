#!/usr/bin/env python3
"""
LLM Usage and Cost-Quality Balance Optimization System

Comprehensive optimization system that dynamically balances LLM usage costs
with quality requirements across all 19 OpenAlex disciplines. Provides
intelligent model selection, token usage optimization, and cost management.

Author: Autonomous AI Development System
"""

import json
import logging
import statistics
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import hashlib
from collections import defaultdict, deque

# Add parent directory to path for imports
import sys
sys.path.append(str(Path(__file__).parent.parent))

from data.database_manager import DatabaseManager

class OptimizationStrategy(Enum):
    """LLM optimization strategies"""
    COST_FOCUSED = "cost_focused"
    QUALITY_FOCUSED = "quality_focused"
    BALANCED = "balanced"
    SPEED_FOCUSED = "speed_focused"
    DISCIPLINE_ADAPTIVE = "discipline_adaptive"

class TaskComplexity(Enum):
    """Task complexity levels"""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    EXPERT = "expert"

@dataclass
class LLMUsageRecord:
    """Record of LLM usage"""
    usage_id: str
    model_name: str
    task_type: str
    discipline_id: Optional[int]
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost_usd: float
    response_time_ms: int
    quality_score: Optional[float]
    task_complexity: TaskComplexity
    optimization_applied: Optional[str]
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class ModelPerformanceProfile:
    """Performance profile for an LLM model"""
    model_name: str
    avg_cost_per_1k_tokens: float
    avg_response_time_ms: int
    avg_quality_score: float
    reliability_score: float
    best_use_cases: List[str]
    discipline_performance: Dict[int, Dict[str, float]]
    token_efficiency: float
    last_updated: datetime

@dataclass
class OptimizationRule:
    """LLM optimization rule"""
    rule_id: str
    name: str
    description: str
    conditions: Dict[str, Any]
    actions: Dict[str, Any]
    priority: int
    discipline_specific: bool
    enabled: bool
    success_rate: float = 0.0
    applications: int = 0

class LLMOptimizer:
    """Comprehensive LLM usage and cost optimization system"""
    
    def __init__(self, database_manager: DatabaseManager,
                 llm_integration: Optional[Any] = None):
        """Initialize LLM optimizer
        
        Args:
            database_manager: Database manager instance
            llm_integration: LLM integration instance (from core)
        """
        self.db = database_manager
        self.llm_integration = llm_integration
        self.logger = logging.getLogger(__name__)
        
        # Optimization state
        self.current_strategy = OptimizationStrategy.BALANCED
        self.usage_history = deque(maxlen=10000)
        self.model_profiles = {}
        self.optimization_rules = []
        
        # Cost and quality targets
        self.cost_targets = {
            'daily_budget_usd': 100.0,
            'cost_per_standard_target': 0.05,
            'max_cost_per_request': 2.0
        }
        
        self.quality_targets = {
            'min_quality_score': 0.7,
            'target_quality_score': 0.85,
            'consistency_threshold': 0.1
        }
        
        # Performance tracking
        self.optimization_stats = {
            'total_optimizations': 0,
            'cost_savings_usd': 0.0,
            'quality_improvements': 0,
            'model_switches': 0,
            'avg_optimization_time_ms': 0.0
        }
        
        # Threading for background optimization
        self.optimization_lock = threading.Lock()
        
        # Initialize components
        self._initialize_model_profiles()
        self._initialize_optimization_rules()
        
        self.logger.info("LLM optimizer initialized")
    
    def _initialize_model_profiles(self):
        """Initialize model performance profiles"""
        # Default model profiles (would be loaded from actual usage data)
        default_profiles = {
            'gpt-4o': {
                'avg_cost_per_1k_tokens': 0.03,
                'avg_response_time_ms': 2500,
                'avg_quality_score': 0.92,
                'reliability_score': 0.98,
                'best_use_cases': ['complex_analysis', 'creative_writing', 'expert_reasoning'],
                'token_efficiency': 0.85
            },
            'gpt-4o-mini': {
                'avg_cost_per_1k_tokens': 0.0015,
                'avg_response_time_ms': 1200,
                'avg_quality_score': 0.85,
                'reliability_score': 0.95,
                'best_use_cases': ['classification', 'simple_extraction', 'formatting'],
                'token_efficiency': 0.90
            },
            'claude-3-5-sonnet': {
                'avg_cost_per_1k_tokens': 0.015,
                'avg_response_time_ms': 1800,
                'avg_quality_score': 0.89,
                'reliability_score': 0.96,
                'best_use_cases': ['analysis', 'structured_output', 'reasoning'],
                'token_efficiency': 0.88
            },
            'claude-3-haiku': {
                'avg_cost_per_1k_tokens': 0.0008,
                'avg_response_time_ms': 800,
                'avg_quality_score': 0.78,
                'reliability_score': 0.94,
                'best_use_cases': ['simple_tasks', 'classification', 'quick_extraction'],
                'token_efficiency': 0.92
            }
        }
        
        for model_name, profile_data in default_profiles.items():
            profile = ModelPerformanceProfile(
                model_name=model_name,
                avg_cost_per_1k_tokens=profile_data['avg_cost_per_1k_tokens'],
                avg_response_time_ms=profile_data['avg_response_time_ms'],
                avg_quality_score=profile_data['avg_quality_score'],
                reliability_score=profile_data['reliability_score'],
                best_use_cases=profile_data['best_use_cases'],
                discipline_performance={},
                token_efficiency=profile_data['token_efficiency'],
                last_updated=datetime.now()
            )
            self.model_profiles[model_name] = profile
        
        self.logger.info(f"Initialized {len(self.model_profiles)} model profiles")
    
    def _initialize_optimization_rules(self):
        """Initialize optimization rules"""
        rules = [
            # Cost optimization rules
            OptimizationRule(
                rule_id="cost_budget_exceeded",
                name="Daily Budget Exceeded",
                description="Switch to cheaper models when daily budget is exceeded",
                conditions={'daily_cost_ratio': '> 0.9'},
                actions={'model_tier': 'downgrade', 'urgency': 'high'},
                priority=10,
                discipline_specific=False,
                enabled=True
            ),
            
            OptimizationRule(
                rule_id="simple_task_cost_optimization",
                name="Simple Task Cost Optimization",
                description="Use cheaper models for simple classification and extraction tasks",
                conditions={'task_complexity': 'simple', 'quality_requirement': '< 0.8'},
                actions={'model_selection': 'cost_optimized'},
                priority=5,
                discipline_specific=False,
                enabled=True
            ),
            
            # Quality optimization rules
            OptimizationRule(
                rule_id="quality_threshold_not_met",
                name="Quality Threshold Not Met",
                description="Upgrade model when quality consistently falls below threshold",
                conditions={'quality_score': '< min_threshold', 'consistency': 'poor'},
                actions={'model_tier': 'upgrade', 'review_required': True},
                priority=8,
                discipline_specific=False,
                enabled=True
            ),
            
            # Discipline-specific rules
            OptimizationRule(
                rule_id="stem_precision_requirement",
                name="STEM Precision Requirement",
                description="Use high-precision models for STEM disciplines requiring exact calculations",
                conditions={'discipline_type': 'stem', 'task_type': 'calculation'},
                actions={'model_selection': 'precision_focused'},
                priority=7,
                discipline_specific=True,
                enabled=True
            ),
            
            OptimizationRule(
                rule_id="humanities_creativity_optimization",
                name="Humanities Creativity Optimization",
                description="Use creative models for humanities tasks requiring interpretation",
                conditions={'discipline_type': 'humanities', 'task_type': 'interpretation'},
                actions={'model_selection': 'creativity_focused'},
                priority=6,
                discipline_specific=True,
                enabled=True
            ),
            
            # Performance optimization rules
            OptimizationRule(
                rule_id="high_volume_efficiency",
                name="High Volume Efficiency",
                description="Optimize for speed and efficiency during high-volume processing",
                conditions={'request_volume': '> high_threshold', 'time_constraint': 'strict'},
                actions={'model_selection': 'speed_optimized', 'batch_processing': True},
                priority=4,
                discipline_specific=False,
                enabled=True
            )
        ]
        
        self.optimization_rules = rules
        self.logger.info(f"Initialized {len(self.optimization_rules)} optimization rules")
    
    def optimize_model_selection(self, task_type: str, discipline_id: Optional[int] = None,
                                 quality_requirement: float = 0.8,
                                 cost_constraint: Optional[float] = None,
                                 speed_requirement: Optional[int] = None,
                                 context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Optimize model selection for a specific task
        
        Args:
            task_type: Type of task to perform
            discipline_id: Target discipline ID
            quality_requirement: Minimum quality score required
            cost_constraint: Maximum cost per request
            speed_requirement: Maximum response time in ms
            context: Additional context for optimization
            
        Returns:
            Optimization recommendation
        """
        optimization_start = datetime.now()
        
        try:
            with self.optimization_lock:
                # Analyze current situation
                task_complexity = self._assess_task_complexity(task_type, context)
                discipline_profile = self._get_discipline_profile(discipline_id)
                
                # Apply optimization strategy
                candidates = self._get_model_candidates(
                    task_type, discipline_id, task_complexity
                )
                
                # Score and rank candidates
                scored_candidates = self._score_model_candidates(
                    candidates, task_type, discipline_id, quality_requirement,
                    cost_constraint, speed_requirement, context
                )
                
                # Select optimal model
                optimal_model = self._select_optimal_model(scored_candidates)
                
                # Apply optimization rules
                optimization_adjustments = self._apply_optimization_rules(
                    optimal_model, task_type, discipline_id, context
                )
                
                # Generate recommendation
                recommendation = self._generate_optimization_recommendation(
                    optimal_model, optimization_adjustments, scored_candidates
                )
                
                # Update statistics
                optimization_time = (datetime.now() - optimization_start).total_seconds() * 1000
                self._update_optimization_stats(optimization_time, True)
                
                return recommendation
        
        except Exception as e:
            optimization_time = (datetime.now() - optimization_start).total_seconds() * 1000
            self._update_optimization_stats(optimization_time, False)
            self.logger.error(f"Error in model selection optimization: {e}")
            
            # Return fallback recommendation
            return {
                'success': False,
                'error': str(e),
                'fallback_model': self._get_fallback_model(),
                'timestamp': datetime.now().isoformat()
            }
    
    def _assess_task_complexity(self, task_type: str, 
                               context: Optional[Dict[str, Any]]) -> TaskComplexity:
        """Assess the complexity of a task"""
        # Simple heuristics for task complexity
        simple_tasks = ['classification', 'extraction', 'formatting', 'simple_qa']
        moderate_tasks = ['summarization', 'translation', 'basic_analysis']
        complex_tasks = ['deep_analysis', 'reasoning', 'creative_writing', 'problem_solving']
        expert_tasks = ['research', 'expert_analysis', 'complex_reasoning', 'scientific_modeling']
        
        if task_type in simple_tasks:
            return TaskComplexity.SIMPLE
        elif task_type in moderate_tasks:
            return TaskComplexity.MODERATE
        elif task_type in complex_tasks:
            return TaskComplexity.COMPLEX
        elif task_type in expert_tasks:
            return TaskComplexity.EXPERT
        
        # Default based on context analysis
        if context:
            # Check for complexity indicators
            input_length = context.get('input_length', 0)
            if input_length > 5000:
                return TaskComplexity.COMPLEX
            elif input_length > 2000:
                return TaskComplexity.MODERATE
        
        return TaskComplexity.MODERATE
    
    def _get_discipline_profile(self, discipline_id: Optional[int]) -> Dict[str, Any]:
        """Get performance profile for a discipline"""
        if not discipline_id:
            return {'type': 'general', 'requirements': {}}
        
        # Get discipline information from database
        try:
            disciplines = self.db.get_all_disciplines()
            discipline = next((d for d in disciplines if d['discipline_id'] == discipline_id), None)
            
            if discipline:
                discipline_name = discipline['discipline_name'].lower()
                
                # Categorize discipline
                stem_disciplines = ['mathematics', 'physics', 'chemistry', 'biology', 'computer_science', 'engineering']
                humanities_disciplines = ['literature', 'history', 'philosophy', 'art', 'languages']
                social_sciences = ['psychology', 'sociology', 'economics', 'political_science']
                
                if discipline_name in stem_disciplines:
                    return {
                        'type': 'stem',
                        'requirements': {
                            'precision': 'high',
                            'factual_accuracy': 'critical',
                            'logical_reasoning': 'important'
                        }
                    }
                elif discipline_name in humanities_disciplines:
                    return {
                        'type': 'humanities',
                        'requirements': {
                            'creativity': 'important',
                            'interpretation': 'high',
                            'cultural_awareness': 'important'
                        }
                    }
                elif discipline_name in social_sciences:
                    return {
                        'type': 'social_science',
                        'requirements': {
                            'analytical_thinking': 'high',
                            'context_awareness': 'important',
                            'nuanced_reasoning': 'important'
                        }
                    }
        
        except Exception as e:
            self.logger.error(f"Error getting discipline profile: {e}")
        
        return {'type': 'general', 'requirements': {}}
    
    def _get_model_candidates(self, task_type: str, discipline_id: Optional[int],
                             task_complexity: TaskComplexity) -> List[str]:
        """Get candidate models for the task"""
        candidates = list(self.model_profiles.keys())
        
        # Filter based on task complexity
        if task_complexity == TaskComplexity.SIMPLE:
            # Prefer efficient, cost-effective models
            priority_models = ['gpt-4o-mini', 'claude-3-haiku']
            candidates = [m for m in candidates if m in priority_models] + \
                        [m for m in candidates if m not in priority_models]
        
        elif task_complexity == TaskComplexity.EXPERT:
            # Prefer high-capability models
            priority_models = ['gpt-4o', 'claude-3-5-sonnet']
            candidates = [m for m in candidates if m in priority_models] + \
                        [m for m in candidates if m not in priority_models]
        
        return candidates[:5]  # Limit to top 5 candidates
    
    def _score_model_candidates(self, candidates: List[str], task_type: str,
                               discipline_id: Optional[int], quality_requirement: float,
                               cost_constraint: Optional[float],
                               speed_requirement: Optional[int],
                               context: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Score model candidates based on requirements"""
        scored_candidates = []
        
        for model_name in candidates:
            profile = self.model_profiles.get(model_name)
            if not profile:
                continue
            
            # Base scores
            quality_score = profile.avg_quality_score
            cost_score = 1.0 / (profile.avg_cost_per_1k_tokens * 1000 + 0.001)  # Inverse cost
            speed_score = 1.0 / (profile.avg_response_time_ms + 1)  # Inverse time
            reliability_score = profile.reliability_score
            
            # Requirement compliance
            quality_compliance = 1.0 if quality_score >= quality_requirement else quality_score / quality_requirement
            cost_compliance = 1.0
            speed_compliance = 1.0
            
            if cost_constraint:
                estimated_cost = profile.avg_cost_per_1k_tokens * 2  # Rough estimate
                cost_compliance = 1.0 if estimated_cost <= cost_constraint else cost_constraint / estimated_cost
            
            if speed_requirement:
                speed_compliance = 1.0 if profile.avg_response_time_ms <= speed_requirement else speed_requirement / profile.avg_response_time_ms
            
            # Use case suitability
            use_case_score = 1.0 if task_type in profile.best_use_cases else 0.7
            
            # Discipline-specific performance
            discipline_score = 1.0
            if discipline_id and discipline_id in profile.discipline_performance:
                discipline_performance = profile.discipline_performance[discipline_id]
                discipline_score = discipline_performance.get('avg_score', 0.8)
            
            # Calculate weighted total score based on current strategy
            weights = self._get_strategy_weights()
            
            total_score = (
                quality_score * weights['quality'] * quality_compliance +
                cost_score * weights['cost'] * cost_compliance +
                speed_score * weights['speed'] * speed_compliance +
                reliability_score * weights['reliability'] +
                use_case_score * weights['use_case'] +
                discipline_score * weights['discipline'] +
                profile.token_efficiency * weights['efficiency']
            )
            
            scored_candidates.append({
                'model_name': model_name,
                'total_score': total_score,
                'quality_score': quality_score,
                'cost_score': cost_score,
                'speed_score': speed_score,
                'reliability_score': reliability_score,
                'use_case_score': use_case_score,
                'discipline_score': discipline_score,
                'quality_compliance': quality_compliance,
                'cost_compliance': cost_compliance,
                'speed_compliance': speed_compliance,
                'profile': profile
            })
        
        # Sort by total score descending
        scored_candidates.sort(key=lambda x: x['total_score'], reverse=True)
        
        return scored_candidates
    
    def _get_strategy_weights(self) -> Dict[str, float]:
        """Get scoring weights based on current optimization strategy"""
        if self.current_strategy == OptimizationStrategy.COST_FOCUSED:
            return {
                'quality': 0.15,
                'cost': 0.35,
                'speed': 0.15,
                'reliability': 0.10,
                'use_case': 0.10,
                'discipline': 0.10,
                'efficiency': 0.05
            }
        elif self.current_strategy == OptimizationStrategy.QUALITY_FOCUSED:
            return {
                'quality': 0.40,
                'cost': 0.10,
                'speed': 0.10,
                'reliability': 0.15,
                'use_case': 0.15,
                'discipline': 0.10,
                'efficiency': 0.00
            }
        elif self.current_strategy == OptimizationStrategy.SPEED_FOCUSED:
            return {
                'quality': 0.15,
                'cost': 0.15,
                'speed': 0.35,
                'reliability': 0.10,
                'use_case': 0.10,
                'discipline': 0.10,
                'efficiency': 0.05
            }
        else:  # BALANCED
            return {
                'quality': 0.25,
                'cost': 0.20,
                'speed': 0.15,
                'reliability': 0.15,
                'use_case': 0.15,
                'discipline': 0.10,
                'efficiency': 0.00
            }
    
    def _select_optimal_model(self, scored_candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Select the optimal model from scored candidates"""
        if not scored_candidates:
            return {'model_name': self._get_fallback_model(), 'score': 0.5}
        
        return scored_candidates[0]
    
    def _apply_optimization_rules(self, selected_model: Dict[str, Any],
                                 task_type: str, discipline_id: Optional[int],
                                 context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Apply optimization rules to the selected model"""
        adjustments = {}
        applied_rules = []
        
        for rule in self.optimization_rules:
            if not rule.enabled:
                continue
            
            # Check if rule conditions are met
            if self._evaluate_rule_conditions(rule, selected_model, task_type, discipline_id, context):
                # Apply rule actions
                rule_adjustments = self._apply_rule_actions(rule, selected_model, context)
                adjustments.update(rule_adjustments)
                applied_rules.append(rule.rule_id)
                
                # Update rule statistics
                rule.applications += 1
        
        return {
            'adjustments': adjustments,
            'applied_rules': applied_rules
        }
    
    def _evaluate_rule_conditions(self, rule: OptimizationRule,
                                 selected_model: Dict[str, Any],
                                 task_type: str, discipline_id: Optional[int],
                                 context: Optional[Dict[str, Any]]) -> bool:
        """Evaluate if rule conditions are met"""
        # Simplified rule condition evaluation
        conditions = rule.conditions
        
        # Check daily cost ratio
        if 'daily_cost_ratio' in conditions:
            daily_cost = self._get_daily_cost()
            daily_budget = self.cost_targets['daily_budget_usd']
            cost_ratio = daily_cost / daily_budget if daily_budget > 0 else 0
            
            condition = conditions['daily_cost_ratio']
            if condition.startswith('> '):
                threshold = float(condition[2:])
                if cost_ratio <= threshold:
                    return False
        
        # Check task complexity
        if 'task_complexity' in conditions:
            expected_complexity = conditions['task_complexity']
            actual_complexity = self._assess_task_complexity(task_type, context)
            if expected_complexity != actual_complexity.value:
                return False
        
        # Check quality requirements
        if 'quality_requirement' in conditions:
            condition = conditions['quality_requirement']
            if condition.startswith('< '):
                threshold = float(condition[2:])
                if context and context.get('quality_requirement', 0.8) >= threshold:
                    return False
        
        # Check discipline type
        if 'discipline_type' in conditions:
            expected_type = conditions['discipline_type']
            discipline_profile = self._get_discipline_profile(discipline_id)
            if discipline_profile.get('type') != expected_type:
                return False
        
        return True
    
    def _apply_rule_actions(self, rule: OptimizationRule,
                           selected_model: Dict[str, Any],
                           context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Apply rule actions"""
        adjustments = {}
        actions = rule.actions
        
        # Model tier adjustments
        if 'model_tier' in actions:
            action = actions['model_tier']
            current_model = selected_model['model_name']
            
            if action == 'upgrade':
                upgraded_model = self._get_upgraded_model(current_model)
                if upgraded_model != current_model:
                    adjustments['model_override'] = upgraded_model
                    adjustments['reason'] = f"Upgraded due to rule: {rule.name}"
            
            elif action == 'downgrade':
                downgraded_model = self._get_downgraded_model(current_model)
                if downgraded_model != current_model:
                    adjustments['model_override'] = downgraded_model
                    adjustments['reason'] = f"Downgraded due to rule: {rule.name}"
        
        # Model selection type
        if 'model_selection' in actions:
            selection_type = actions['model_selection']
            optimized_model = self._get_model_by_optimization_type(selection_type)
            if optimized_model:
                adjustments['model_override'] = optimized_model
                adjustments['reason'] = f"Selected {selection_type} model due to rule: {rule.name}"
        
        # Additional adjustments
        if 'batch_processing' in actions and actions['batch_processing']:
            adjustments['batch_processing'] = True
        
        if 'urgency' in actions:
            adjustments['urgency'] = actions['urgency']
        
        return adjustments
    
    def _get_upgraded_model(self, current_model: str) -> str:
        """Get an upgraded model"""
        upgrade_map = {
            'gpt-4o-mini': 'gpt-4o',
            'claude-3-haiku': 'claude-3-5-sonnet',
        }
        return upgrade_map.get(current_model, current_model)
    
    def _get_downgraded_model(self, current_model: str) -> str:
        """Get a downgraded model"""
        downgrade_map = {
            'gpt-4o': 'gpt-4o-mini',
            'claude-3-5-sonnet': 'claude-3-haiku',
        }
        return downgrade_map.get(current_model, current_model)
    
    def _get_model_by_optimization_type(self, optimization_type: str) -> Optional[str]:
        """Get model by optimization type"""
        optimization_models = {
            'cost_optimized': 'gpt-4o-mini',
            'quality_optimized': 'gpt-4o',
            'speed_optimized': 'claude-3-haiku',
            'precision_focused': 'gpt-4o',
            'creativity_focused': 'claude-3-5-sonnet'
        }
        return optimization_models.get(optimization_type)
    
    def _generate_optimization_recommendation(self, optimal_model: Dict[str, Any],
                                            optimization_adjustments: Dict[str, Any],
                                            all_candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate final optimization recommendation"""
        # Apply any adjustments
        final_model = optimization_adjustments.get('adjustments', {}).get('model_override', 
                                                                          optimal_model['model_name'])
        
        # Get final model profile
        final_profile = self.model_profiles.get(final_model)
        
        recommendation = {
            'success': True,
            'recommended_model': final_model,
            'confidence': min(1.0, optimal_model['total_score'] / 5.0),
            'optimization_score': optimal_model['total_score'],
            'estimated_cost_per_1k_tokens': final_profile.avg_cost_per_1k_tokens if final_profile else 0.01,
            'estimated_response_time_ms': final_profile.avg_response_time_ms if final_profile else 2000,
            'expected_quality_score': final_profile.avg_quality_score if final_profile else 0.8,
            'optimization_strategy': self.current_strategy.value,
            'applied_rules': optimization_adjustments.get('applied_rules', []),
            'adjustment_reason': optimization_adjustments.get('adjustments', {}).get('reason'),
            'alternatives': [
                {
                    'model': candidate['model_name'],
                    'score': candidate['total_score'],
                    'cost_per_1k': candidate['profile'].avg_cost_per_1k_tokens,
                    'quality': candidate['quality_score']
                }
                for candidate in all_candidates[1:4]  # Top 3 alternatives
            ],
            'timestamp': datetime.now().isoformat()
        }
        
        return recommendation
    
    def record_usage(self, usage_record: LLMUsageRecord):
        """Record LLM usage for optimization learning"""
        self.usage_history.append(usage_record)
        
        # Update model profile with actual performance
        self._update_model_profile(usage_record)
        
        # Check for optimization opportunities
        self._check_optimization_opportunities(usage_record)
    
    def _update_model_profile(self, usage_record: LLMUsageRecord):
        """Update model profile based on actual usage"""
        model_name = usage_record.model_name
        if model_name not in self.model_profiles:
            return
        
        profile = self.model_profiles[model_name]
        
        # Update averages with exponential moving average
        alpha = 0.1  # Learning rate
        
        # Update cost (if available)
        if usage_record.cost_usd > 0 and usage_record.total_tokens > 0:
            actual_cost_per_1k = (usage_record.cost_usd / usage_record.total_tokens) * 1000
            profile.avg_cost_per_1k_tokens = (
                (1 - alpha) * profile.avg_cost_per_1k_tokens + 
                alpha * actual_cost_per_1k
            )
        
        # Update response time
        profile.avg_response_time_ms = (
            (1 - alpha) * profile.avg_response_time_ms + 
            alpha * usage_record.response_time_ms
        )
        
        # Update quality score
        if usage_record.quality_score is not None:
            profile.avg_quality_score = (
                (1 - alpha) * profile.avg_quality_score + 
                alpha * usage_record.quality_score
            )
        
        # Update discipline-specific performance
        if usage_record.discipline_id:
            discipline_id = usage_record.discipline_id
            if discipline_id not in profile.discipline_performance:
                profile.discipline_performance[discipline_id] = {
                    'avg_score': usage_record.quality_score or 0.8,
                    'usage_count': 1
                }
            else:
                discipline_perf = profile.discipline_performance[discipline_id]
                discipline_perf['usage_count'] += 1
                if usage_record.quality_score is not None:
                    discipline_perf['avg_score'] = (
                        (1 - alpha) * discipline_perf['avg_score'] + 
                        alpha * usage_record.quality_score
                    )
        
        profile.last_updated = datetime.now()
    
    def _check_optimization_opportunities(self, usage_record: LLMUsageRecord):
        """Check for optimization opportunities based on usage"""
        # Check if cost is too high for the quality received
        if (usage_record.cost_usd > self.cost_targets['cost_per_standard_target'] and 
            usage_record.quality_score and usage_record.quality_score < 0.9):
            self._suggest_cost_optimization(usage_record)
        
        # Check if quality is below threshold
        if (usage_record.quality_score and 
            usage_record.quality_score < self.quality_targets['min_quality_score']):
            self._suggest_quality_optimization(usage_record)
    
    def _suggest_cost_optimization(self, usage_record: LLMUsageRecord):
        """Suggest cost optimization based on usage"""
        # This would trigger automatic optimization or alert
        self.logger.info(f"Cost optimization opportunity detected for {usage_record.model_name}")
        
    def _suggest_quality_optimization(self, usage_record: LLMUsageRecord):
        """Suggest quality optimization based on usage"""
        # This would trigger automatic optimization or alert
        self.logger.info(f"Quality optimization opportunity detected for {usage_record.model_name}")
    
    def _get_daily_cost(self) -> float:
        """Get total cost for today"""
        today = datetime.now().date()
        daily_usage = [record for record in self.usage_history 
                      if record.timestamp.date() == today]
        return sum(record.cost_usd for record in daily_usage)
    
    def _get_fallback_model(self) -> str:
        """Get fallback model when optimization fails"""
        return 'gpt-4o-mini'  # Safe, cost-effective default
    
    def _update_optimization_stats(self, optimization_time_ms: float, success: bool):
        """Update optimization statistics"""
        self.optimization_stats['total_optimizations'] += 1
        
        if success:
            # Update average optimization time
            current_avg = self.optimization_stats['avg_optimization_time_ms']
            total_opts = self.optimization_stats['total_optimizations']
            self.optimization_stats['avg_optimization_time_ms'] = (
                (current_avg * (total_opts - 1) + optimization_time_ms) / total_opts
            )
    
    def set_optimization_strategy(self, strategy: OptimizationStrategy):
        """Set the optimization strategy"""
        self.current_strategy = strategy
        self.logger.info(f"Optimization strategy set to: {strategy.value}")
    
    def get_cost_analysis(self, days: int = 7) -> Dict[str, Any]:
        """Get cost analysis for specified period"""
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_usage = [record for record in self.usage_history 
                       if record.timestamp >= cutoff_date]
        
        if not recent_usage:
            return {'message': 'No usage data available for the specified period'}
        
        # Calculate statistics
        total_cost = sum(record.cost_usd for record in recent_usage)
        total_tokens = sum(record.total_tokens for record in recent_usage)
        avg_cost_per_1k = (total_cost / total_tokens * 1000) if total_tokens > 0 else 0
        
        # Cost by model
        cost_by_model = defaultdict(float)
        tokens_by_model = defaultdict(int)
        
        for record in recent_usage:
            cost_by_model[record.model_name] += record.cost_usd
            tokens_by_model[record.model_name] += record.total_tokens
        
        # Daily costs
        daily_costs = defaultdict(float)
        for record in recent_usage:
            date_key = record.timestamp.date().isoformat()
            daily_costs[date_key] += record.cost_usd
        
        return {
            'period_days': days,
            'total_cost_usd': round(total_cost, 4),
            'total_tokens': total_tokens,
            'avg_cost_per_1k_tokens': round(avg_cost_per_1k, 4),
            'daily_average_cost': round(total_cost / days, 4),
            'cost_by_model': dict(cost_by_model),
            'tokens_by_model': dict(tokens_by_model),
            'daily_costs': dict(daily_costs),
            'budget_utilization': (total_cost / days) / self.cost_targets['daily_budget_usd'],
            'optimization_savings': self.optimization_stats['cost_savings_usd']
        }
    
    def get_optimization_statistics(self) -> Dict[str, Any]:
        """Get optimization statistics"""
        stats = self.optimization_stats.copy()
        
        # Add current strategy
        stats['current_strategy'] = self.current_strategy.value
        
        # Add rule statistics
        stats['optimization_rules'] = {
            'total_rules': len(self.optimization_rules),
            'enabled_rules': len([r for r in self.optimization_rules if r.enabled]),
            'rule_applications': sum(r.applications for r in self.optimization_rules)
        }
        
        # Add model profile statistics
        stats['model_profiles'] = {
            'total_models': len(self.model_profiles),
            'last_updated': max(p.last_updated for p in self.model_profiles.values()).isoformat() if self.model_profiles else None
        }
        
        return stats
    
    def generate_optimization_report(self) -> Dict[str, Any]:
        """Generate comprehensive optimization report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'optimization_strategy': self.current_strategy.value,
            'cost_analysis': self.get_cost_analysis(),
            'optimization_statistics': self.get_optimization_statistics(),
            'model_performance': {},
            'recommendations': []
        }
        
        # Model performance summary
        for model_name, profile in self.model_profiles.items():
            report['model_performance'][model_name] = {
                'avg_cost_per_1k_tokens': profile.avg_cost_per_1k_tokens,
                'avg_response_time_ms': profile.avg_response_time_ms,
                'avg_quality_score': profile.avg_quality_score,
                'reliability_score': profile.reliability_score,
                'token_efficiency': profile.token_efficiency,
                'discipline_count': len(profile.discipline_performance)
            }
        
        # Generate recommendations
        report['recommendations'] = self._generate_strategic_recommendations()
        
        return report
    
    def _generate_strategic_recommendations(self) -> List[Dict[str, Any]]:
        """Generate strategic optimization recommendations"""
        recommendations = []
        
        # Cost optimization recommendations
        daily_cost = self._get_daily_cost()
        daily_budget = self.cost_targets['daily_budget_usd']
        
        if daily_cost > daily_budget * 0.8:
            recommendations.append({
                'type': 'cost_optimization',
                'priority': 'high',
                'title': 'Daily budget approaching limit',
                'description': f'Current daily cost (${daily_cost:.2f}) is approaching budget limit (${daily_budget:.2f})',
                'suggested_action': 'Consider switching to cost-optimized strategy or reviewing high-cost operations'
            })
        
        # Quality optimization recommendations
        recent_usage = list(self.usage_history)[-100:]  # Last 100 operations
        if recent_usage:
            avg_quality = statistics.mean(
                record.quality_score for record in recent_usage 
                if record.quality_score is not None
            )
            
            if avg_quality < self.quality_targets['min_quality_score']:
                recommendations.append({
                    'type': 'quality_optimization',
                    'priority': 'high',
                    'title': 'Quality below threshold',
                    'description': f'Average quality score ({avg_quality:.2f}) is below minimum threshold ({self.quality_targets["min_quality_score"]})',
                    'suggested_action': 'Consider upgrading to higher-quality models for critical tasks'
                })
        
        return recommendations

# Factory function for easy initialization
def create_llm_optimizer(database_manager: DatabaseManager,
                        llm_integration: Optional[Any] = None,
                        optimization_strategy: OptimizationStrategy = OptimizationStrategy.BALANCED) -> LLMOptimizer:
    """Create and configure LLM optimizer
    
    Args:
        database_manager: Database manager instance
        llm_integration: LLM integration instance
        optimization_strategy: Initial optimization strategy
        
    Returns:
        Configured LLMOptimizer instance
    """
    optimizer = LLMOptimizer(database_manager, llm_integration)
    optimizer.set_optimization_strategy(optimization_strategy)
    return optimizer