#!/usr/bin/env python3
"""
dual_priority_alert_system.py - Prioritize alerts by both standards importance and missing topic count

This module generates and prioritizes alerts using both the importance of affected
standards frameworks and the number of missing topics to provide actionable insights.
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import json

from .data_models import (
    DualPriorityAlert, AlertSeverity, SubtopicEntry, ScientificViolation,
    StandardsFramework, ValidationReport, ConsistencyValidationResult,
    calculate_composite_priority, determine_alert_severity
)

logger = logging.getLogger(__name__)


class AlertType(Enum):
    """Types of alerts that can be generated."""
    COVERAGE_GAP = "Coverage_Gap"
    STANDARDS_VIOLATION = "Standards_Violation"
    SCIENTIFIC_VIOLATION = "Scientific_Violation"
    CONSISTENCY_CONFLICT = "Consistency_Conflict"
    COMPLETENESS_ISSUE = "Completeness_Issue"
    TEXTBOOK_GAP = "Textbook_Gap"


@dataclass
class AlertMetrics:
    """
    Goal: Track metrics for alert prioritization calculations.
    
    Contains all factors used in dual-priority alert generation and ranking.
    """
    standards_importance_score: float
    missing_topics_count: int
    affected_frameworks: List[str]
    severity_factors: Dict[str, float]
    textbook_coverage_gap: float = 0.0
    student_impact_score: float = 0.0
    urgency_multiplier: float = 1.0
    
    def calculate_composite_score(self, standards_weight: float = 0.7, 
                                count_weight: float = 0.3) -> float:
        """Calculate weighted composite priority score."""
        return calculate_composite_priority(
            self.standards_importance_score, 
            self.missing_topics_count,
            standards_weight, 
            count_weight
        ) * self.urgency_multiplier


@dataclass
class AlertRecommendation:
    """
    Goal: Provide specific, actionable recommendations for addressing alerts.
    
    Contains detailed guidance for resolving identified issues.
    """
    recommendation_type: str  # Immediate, Short_Term, Long_Term
    action: str
    priority: int  # 1-5, 1 being highest
    estimated_effort: str  # Low, Medium, High
    expected_impact: str  # Low, Medium, High
    resources_needed: List[str]
    timeline: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'recommendation_type': self.recommendation_type,
            'action': self.action,
            'priority': self.priority,
            'estimated_effort': self.estimated_effort,
            'expected_impact': self.expected_impact,
            'resources_needed': self.resources_needed,
            'timeline': self.timeline
        }


class DualPriorityAlertSystem:
    """
    Goal: Generate and prioritize alerts using both standards importance and missing topic count.
    
    Creates actionable, prioritized alerts that consider both the criticality of
    affected standards and the scope of missing content.
    """
    
    def __init__(self):
        self.standards_importance_weights = self._load_standards_weights()
        self.topic_count_weights = self._define_topic_count_weights()
        self.alert_history: List[DualPriorityAlert] = []
        self.recommendation_templates = self._load_recommendation_templates()
        
    def generate_prioritized_alerts(self, validation_reports: Dict[str, ValidationReport], 
                                   consistency_results: List[ConsistencyValidationResult],
                                   scientific_violations: Dict[str, List[ScientificViolation]]) -> List[DualPriorityAlert]:
        """
        Goal: Generate comprehensive prioritized alerts from all validation results.
        
        Combines coverage gaps, scientific violations, and consistency issues into
        unified alert list ranked by composite priority scores.
        """
        all_alerts = []
        
        logger.info(f"Generating alerts for {len(validation_reports)} disciplines")
        
        # Generate coverage gap alerts
        for discipline, report in validation_reports.items():
            coverage_alerts = self._generate_coverage_alerts(discipline, report)
            all_alerts.extend(coverage_alerts)
        
        # Generate scientific violation alerts
        for discipline, violations in scientific_violations.items():
            violation_alerts = self._generate_scientific_violation_alerts(discipline, violations)
            all_alerts.extend(violation_alerts)
        
        # Generate consistency conflict alerts
        consistency_alerts = self._generate_consistency_alerts(consistency_results)
        all_alerts.extend(consistency_alerts)
        
        # Generate completeness alerts
        completeness_alerts = self._generate_completeness_alerts(validation_reports)
        all_alerts.extend(completeness_alerts)
        
        # Calculate composite priority scores and sort
        for alert in all_alerts:
            alert.composite_priority_score = self._calculate_alert_priority(alert)
            alert.severity = determine_alert_severity(alert.composite_priority_score)
        
        # Sort by priority (highest first)
        prioritized_alerts = sorted(all_alerts, key=lambda x: x.composite_priority_score, reverse=True)
        
        # Add recommendations
        for alert in prioritized_alerts:
            alert.recommendations = self._generate_recommendations(alert)
        
        self.alert_history.extend(prioritized_alerts)
        
        logger.info(f"Generated {len(prioritized_alerts)} prioritized alerts")
        return prioritized_alerts
    
    def _generate_coverage_alerts(self, discipline: str, report: ValidationReport) -> List[DualPriorityAlert]:
        """Generate alerts for coverage gaps below thresholds."""
        alerts = []
        
        for framework, coverage in report.coverage_results.items():
            threshold = self._get_framework_threshold(framework)
            
            if coverage < threshold:
                # Calculate missing topics count
                missing_count = self._estimate_missing_topics_count(discipline, framework, coverage, threshold)
                
                # Calculate standards importance
                standards_importance = self.standards_importance_weights.get(framework, 0.5)
                
                alert = DualPriorityAlert(
                    discipline=discipline,
                    alert_type=AlertType.COVERAGE_GAP.value,
                    standards_importance_score=standards_importance,
                    missing_topics_count=missing_count,
                    composite_priority_score=0.0,  # Will be calculated
                    severity=AlertSeverity.MEDIUM,  # Will be updated
                    recommendations=[],  # Will be generated
                    affected_standards=[framework],
                    specific_missing_topics=self._identify_missing_topics(discipline, framework),
                    textbook_recommendations=self._generate_textbook_recommendations(discipline, framework)
                )
                
                alerts.append(alert)
        
        return alerts
    
    def _generate_scientific_violation_alerts(self, discipline: str, 
                                            violations: List[ScientificViolation]) -> List[DualPriorityAlert]:
        """Generate alerts for scientific principle violations."""
        alerts = []
        
        if not violations:
            return alerts
        
        # Group violations by severity
        violations_by_severity = {}
        for violation in violations:
            severity = violation.severity
            if severity not in violations_by_severity:
                violations_by_severity[severity] = []
            violations_by_severity[severity].append(violation)
        
        # Create alerts for each severity group
        for severity, violation_group in violations_by_severity.items():
            # Calculate standards importance (scientific accuracy is always high)
            standards_importance = 0.9  # High importance for scientific accuracy
            
            alert = DualPriorityAlert(
                discipline=discipline,
                alert_type=AlertType.SCIENTIFIC_VIOLATION.value,
                standards_importance_score=standards_importance,
                missing_topics_count=len(violation_group),
                composite_priority_score=0.0,
                severity=severity,
                recommendations=[],
                affected_standards=["Scientific_Accuracy"],
                specific_missing_topics=[v.description for v in violation_group],
                textbook_recommendations=[]
            )
            
            alerts.append(alert)
        
        return alerts
    
    def _generate_consistency_alerts(self, consistency_results: List[ConsistencyValidationResult]) -> List[DualPriorityAlert]:
        """Generate alerts for cross-disciplinary consistency issues."""
        alerts = []
        
        failed_validations = [r for r in consistency_results if not r.validation_passed]
        
        if not failed_validations:
            return alerts
        
        # Group by disciplines involved
        discipline_groups = {}
        for result in failed_validations:
            key = "|".join(sorted(result.disciplines))
            if key not in discipline_groups:
                discipline_groups[key] = []
            discipline_groups[key].append(result)
        
        # Create alerts for each discipline group
        for disciplines_key, results in discipline_groups.items():
            disciplines = disciplines_key.split("|")
            
            # Calculate importance based on disciplines involved
            standards_importance = self._calculate_cross_disciplinary_importance(disciplines)
            
            alert = DualPriorityAlert(
                discipline=disciplines_key,
                alert_type=AlertType.CONSISTENCY_CONFLICT.value,
                standards_importance_score=standards_importance,
                missing_topics_count=len(results),
                composite_priority_score=0.0,
                severity=AlertSeverity.MEDIUM,
                recommendations=[],
                affected_standards=[f"Cross_Disciplinary_Consistency_{d}" for d in disciplines],
                specific_missing_topics=[f"{r.topic}: {', '.join(r.conflicts_detected)}" for r in results],
                textbook_recommendations=[]
            )
            
            alerts.append(alert)
        
        return alerts
    
    def _generate_completeness_alerts(self, validation_reports: Dict[str, ValidationReport]) -> List[DualPriorityAlert]:
        """Generate alerts for overall curriculum completeness issues."""
        alerts = []
        
        for discipline, report in validation_reports.items():
            if report.overall_completeness_score < 0.9:  # Below 90% completeness
                
                # Calculate missing topics estimate
                expected_topics = 1000  # Target ~1000 subtopics per discipline
                missing_count = max(0, expected_topics - report.total_subtopics)
                
                alert = DualPriorityAlert(
                    discipline=discipline,
                    alert_type=AlertType.COMPLETENESS_ISSUE.value,
                    standards_importance_score=0.7,  # Medium-high importance
                    missing_topics_count=missing_count,
                    composite_priority_score=0.0,
                    severity=AlertSeverity.MEDIUM,
                    recommendations=[],
                    affected_standards=[f"{discipline}_Completeness"],
                    specific_missing_topics=[f"Overall completeness: {report.overall_completeness_score:.1%}"],
                    textbook_recommendations=self._generate_completeness_textbook_recommendations(discipline)
                )
                
                alerts.append(alert)
        
        return alerts
    
    def _calculate_alert_priority(self, alert: DualPriorityAlert) -> float:
        """
        Goal: Calculate composite priority score for alert ranking.
        
        Combines standards importance and missing topic count into unified score
        for actionable prioritization.
        """
        # Base composite calculation
        base_score = calculate_composite_priority(
            alert.standards_importance_score,
            alert.missing_topics_count
        )
        
        # Apply alert type multipliers
        type_multipliers = {
            AlertType.SCIENTIFIC_VIOLATION.value: 1.2,  # Higher priority for scientific accuracy
            AlertType.COVERAGE_GAP.value: 1.0,
            AlertType.CONSISTENCY_CONFLICT.value: 0.9,
            AlertType.COMPLETENESS_ISSUE.value: 0.8,
            AlertType.TEXTBOOK_GAP.value: 0.7
        }
        
        multiplier = type_multipliers.get(alert.alert_type, 1.0)
        
        # Apply urgency factors
        urgency_factors = self._calculate_urgency_factors(alert)
        
        final_score = base_score * multiplier * urgency_factors
        return min(final_score, 1.0)  # Cap at 1.0
    
    def _calculate_urgency_factors(self, alert: DualPriorityAlert) -> float:
        """Calculate urgency multipliers based on various factors."""
        urgency = 1.0
        
        # High urgency for critical severity
        if alert.severity == AlertSeverity.CRITICAL:
            urgency *= 1.3
        elif alert.severity == AlertSeverity.HIGH:
            urgency *= 1.1
        
        # Higher urgency for MCAT-related gaps
        if any("MCAT" in standard for standard in alert.affected_standards):
            urgency *= 1.2
        
        # Higher urgency for scientific violations
        if alert.alert_type == AlertType.SCIENTIFIC_VIOLATION.value:
            urgency *= 1.15
        
        return urgency
    
    def _generate_recommendations(self, alert: DualPriorityAlert) -> List[str]:
        """
        Goal: Generate specific, actionable recommendations for alert resolution.
        
        Provides detailed guidance for addressing identified issues based on
        alert type and severity.
        """
        recommendations = []
        
        # Get base recommendations from templates
        template_recs = self.recommendation_templates.get(alert.alert_type, [])
        recommendations.extend(template_recs)
        
        # Add specific recommendations based on alert details
        if alert.alert_type == AlertType.COVERAGE_GAP.value:
            for framework in alert.affected_standards:
                recommendations.append(f"Review {framework} standards documentation for missing topics")
                recommendations.append(f"Identify authoritative textbooks covering {framework} requirements")
            
            if alert.missing_topics_count > 50:
                recommendations.append("Consider major curriculum restructuring to address extensive gaps")
            elif alert.missing_topics_count > 20:
                recommendations.append("Plan systematic topic addition over multiple iterations")
            else:
                recommendations.append("Targeted addition of specific missing topics")
        
        elif alert.alert_type == AlertType.SCIENTIFIC_VIOLATION.value:
            recommendations.append("Engage subject matter experts for content review")
            recommendations.append("Cross-reference with authoritative scientific sources")
            recommendations.append("Update content to align with current scientific consensus")
        
        elif alert.alert_type == AlertType.CONSISTENCY_CONFLICT.value:
            recommendations.append("Convene interdisciplinary expert panel for resolution")
            recommendations.append("Establish common terminology and conceptual framework")
            recommendations.append("Document discipline-specific contexts while maintaining consistency")
        
        # Add textbook recommendations if available
        if alert.textbook_recommendations:
            recommendations.append("Consider acquiring the following recommended textbooks:")
            recommendations.extend([f"  - {book}" for book in alert.textbook_recommendations])
        
        return recommendations
    
    def _load_standards_weights(self) -> Dict[str, float]:
        """
        Goal: Define importance weights for different standards frameworks.
        
        Higher weights indicate more critical standards that should receive
        priority in alert generation and resource allocation.
        """
        return {
            'MCAT': 1.0,  # Highest importance for medical education
            'NGSS': 0.9,  # High importance for K-12 science
            'AP_Physics': 0.85,
            'AP_Chemistry': 0.85,
            'AP_Biology': 0.85,
            'AP_Psychology': 0.8,
            'IB_Physics': 0.8,
            'IB_Chemistry': 0.8,
            'IB_Biology': 0.8,
            'ACS_Chemistry': 0.85,
            'AAPT_Physics': 0.8,
            'APA_Psychology': 0.85,
            'WHO_Health': 0.9,
            'Professional_Certifications': 0.75,
            'University_Standards': 0.7,
            'General_Education': 0.6
        }
    
    def _define_topic_count_weights(self) -> Dict[str, float]:
        """Define weighting factors for missing topic counts."""
        return {
            'few_topics': 0.3,      # < 10 missing topics
            'moderate_topics': 0.6,  # 10-50 missing topics
            'many_topics': 0.9,      # 50-100 missing topics
            'extensive_topics': 1.0  # > 100 missing topics
        }
    
    def _load_recommendation_templates(self) -> Dict[str, List[str]]:
        """Load template recommendations for different alert types."""
        return {
            AlertType.COVERAGE_GAP.value: [
                "Conduct gap analysis against standards framework",
                "Prioritize high-impact topics for immediate addition",
                "Develop implementation timeline for missing content"
            ],
            AlertType.SCIENTIFIC_VIOLATION.value: [
                "Review content with subject matter experts",
                "Verify against authoritative scientific sources",
                "Update to reflect current scientific consensus"
            ],
            AlertType.CONSISTENCY_CONFLICT.value: [
                "Establish interdisciplinary review committee",
                "Define common conceptual framework",
                "Maintain discipline-specific contexts within consistent framework"
            ],
            AlertType.COMPLETENESS_ISSUE.value: [
                "Assess curriculum scope against discipline standards",
                "Identify missing specialization areas",
                "Plan systematic curriculum expansion"
            ]
        }
    
    def _get_framework_threshold(self, framework: str) -> float:
        """Get coverage threshold for specific framework."""
        thresholds = {
            'MCAT': 0.98,
            'NGSS': 0.95,
            'AP_Physics': 0.90,
            'AP_Chemistry': 0.90,
            'AP_Biology': 0.90,
            'IB_Physics': 0.92,
            'IB_Chemistry': 0.92,
            'IB_Biology': 0.92,
            'default': 0.95
        }
        return thresholds.get(framework, thresholds['default'])
    
    def _estimate_missing_topics_count(self, discipline: str, framework: str, 
                                     current_coverage: float, threshold: float) -> int:
        """Estimate number of missing topics based on coverage gap."""
        coverage_gap = threshold - current_coverage
        
        # Estimate total topics needed for framework
        framework_topic_estimates = {
            'MCAT': 200,  # Approximate topics per MCAT subject
            'NGSS': 150,
            'AP_Physics': 120,
            'AP_Chemistry': 130,
            'AP_Biology': 140,
            'default': 100
        }
        
        total_topics = framework_topic_estimates.get(framework, framework_topic_estimates['default'])
        missing_count = int(coverage_gap * total_topics)
        
        return max(0, missing_count)
    
    def _identify_missing_topics(self, discipline: str, framework: str) -> List[str]:
        """Identify specific missing topics for framework (simplified implementation)."""
        # In a full implementation, this would do detailed gap analysis
        return [f"Missing {framework} topic in {discipline} (detailed analysis needed)"]
    
    def _generate_textbook_recommendations(self, discipline: str, framework: str) -> List[str]:
        """Generate textbook recommendations for covering gaps."""
        recommendations = {
            'Physics': {
                'MCAT': ["MCAT Physics Review", "Physics for Scientists and Engineers"],
                'AP_Physics': ["AP Physics Course and Exam Description", "College Physics"]
            },
            'Chemistry': {
                'MCAT': ["MCAT General Chemistry Review", "Chemical Principles"],
                'AP_Chemistry': ["AP Chemistry Course and Exam Description", "Chemistry: The Central Science"]
            },
            'Biology': {
                'MCAT': ["MCAT Biology Review", "Campbell Biology"],
                'AP_Biology': ["AP Biology Course and Exam Description", "Biology: The Unity and Diversity of Life"]
            }
        }
        
        return recommendations.get(discipline, {}).get(framework, [f"Standard {discipline} textbook for {framework}"])
    
    def _generate_completeness_textbook_recommendations(self, discipline: str) -> List[str]:
        """Generate textbook recommendations for overall completeness."""
        recommendations = {
            'Physics': ["University Physics", "Principles of Physics", "Modern Physics"],
            'Chemistry': ["Chemistry: The Central Science", "Organic Chemistry", "Physical Chemistry"],
            'Biology': ["Campbell Biology", "Molecular Biology of the Cell", "Genetics: Analysis and Principles"],
            'Psychology': ["Psychology: Science of Mind and Behaviour", "Cognitive Psychology", "Social Psychology"],
            'Mathematics': ["Calculus: Early Transcendentals", "Linear Algebra", "Statistics"]
        }
        
        return recommendations.get(discipline, [f"Comprehensive {discipline} textbooks"])
    
    def _calculate_cross_disciplinary_importance(self, disciplines: List[str]) -> float:
        """Calculate importance score for cross-disciplinary consistency."""
        # Higher importance for more disciplines involved
        base_importance = 0.6
        discipline_bonus = min(len(disciplines) * 0.1, 0.3)  # Max 0.3 bonus
        
        # Higher importance for critical discipline combinations
        critical_combinations = {
            ('Biology', 'Chemistry'): 0.1,
            ('Physics', 'Chemistry'): 0.1,
            ('Biology', 'Medicine'): 0.15,
            ('Psychology', 'Medicine'): 0.1
        }
        
        combination_bonus = 0.0
        for combo, bonus in critical_combinations.items():
            if all(d in disciplines for d in combo):
                combination_bonus = max(combination_bonus, bonus)
        
        return min(base_importance + discipline_bonus + combination_bonus, 1.0)
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """Generate summary of alert system performance and results."""
        if not self.alert_history:
            return {"message": "No alerts generated yet"}
        
        # Count alerts by type and severity
        by_type = {}
        by_severity = {}
        by_discipline = {}
        
        for alert in self.alert_history:
            # By type
            alert_type = alert.alert_type
            by_type[alert_type] = by_type.get(alert_type, 0) + 1
            
            # By severity
            severity = alert.severity.value if hasattr(alert.severity, 'value') else str(alert.severity)
            by_severity[severity] = by_severity.get(severity, 0) + 1
            
            # By discipline
            discipline = alert.discipline
            by_discipline[discipline] = by_discipline.get(discipline, 0) + 1
        
        # Calculate priority distribution
        priorities = [alert.composite_priority_score for alert in self.alert_history]
        
        return {
            'total_alerts': len(self.alert_history),
            'alerts_by_type': by_type,
            'alerts_by_severity': by_severity,
            'alerts_by_discipline': by_discipline,
            'priority_statistics': {
                'mean_priority': sum(priorities) / len(priorities) if priorities else 0,
                'max_priority': max(priorities) if priorities else 0,
                'min_priority': min(priorities) if priorities else 0,
                'high_priority_count': len([p for p in priorities if p >= 0.8]),
                'medium_priority_count': len([p for p in priorities if 0.5 <= p < 0.8]),
                'low_priority_count': len([p for p in priorities if p < 0.5])
            },
            'top_priority_alerts': sorted(self.alert_history, 
                                        key=lambda x: x.composite_priority_score, 
                                        reverse=True)[:5]
        }