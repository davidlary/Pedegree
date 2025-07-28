#!/usr/bin/env python3
"""
comprehensive_gap_analyzer.py - Identify curriculum gaps with dual-priority alerts

This module performs comprehensive gap analysis to ensure ~1000 subtopics per discipline
cover the entire discipline comprehensively with natural educational progression.
"""

import logging
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from collections import defaultdict, Counter
import math

from .data_models import SubtopicEntry, DualPriorityAlert, AlertSeverity, StandardsFramework
from .dual_priority_alert_system import DualPriorityAlertSystem

logger = logging.getLogger(__name__)


@dataclass
class CurriculumGap:
    """
    Goal: Represent identified gaps in curriculum coverage.
    
    Tracks missing topics and their importance for comprehensive discipline coverage.
    """
    gap_id: str
    discipline: str
    missing_topic: str
    importance_score: float  # 0-1 scale
    standards_impact: List[str]  # Which standards are affected
    educational_level: str
    prerequisite_topics: List[str]
    follow_up_topics: List[str]
    recommended_sources: List[str]
    urgency_level: AlertSeverity
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            'gap_id': self.gap_id,
            'discipline': self.discipline,
            'missing_topic': self.missing_topic,
            'importance_score': self.importance_score,
            'standards_impact': self.standards_impact,
            'educational_level': self.educational_level,
            'prerequisite_topics': self.prerequisite_topics,
            'follow_up_topics': self.follow_up_topics,
            'recommended_sources': self.recommended_sources,
            'urgency_level': self.urgency_level.value if hasattr(self.urgency_level, 'value') else str(self.urgency_level)
        }


@dataclass
class ComprehensiveAnalysisResult:
    """
    Goal: Complete gap analysis results for curriculum completeness.
    
    Contains comprehensive analysis of curriculum gaps, coverage statistics,
    and recommendations for achieving ~1000 subtopics per discipline.
    """
    discipline: str
    total_subtopics_found: int
    target_subtopics: int
    coverage_percentage: float
    identified_gaps: List[CurriculumGap]
    coverage_by_level: Dict[str, int]
    natural_order_issues: List[str]
    comprehensive_coverage_score: float
    priority_alerts: List[DualPriorityAlert]
    expansion_recommendations: List[str]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            'discipline': self.discipline,
            'total_subtopics_found': self.total_subtopics_found,
            'target_subtopics': self.target_subtopics,
            'coverage_percentage': self.coverage_percentage,
            'identified_gaps': [gap.to_dict() for gap in self.identified_gaps],
            'coverage_by_level': self.coverage_by_level,
            'natural_order_issues': self.natural_order_issues,
            'comprehensive_coverage_score': self.comprehensive_coverage_score,
            'priority_alerts': [alert.__dict__ for alert in self.priority_alerts],
            'expansion_recommendations': self.expansion_recommendations
        }


class ComprehensiveGapAnalyzer:
    """
    Goal: Identify gaps to ensure comprehensive ~1000 subtopics per discipline.
    
    Analyzes curriculum completeness, identifies missing topics, and generates
    recommendations to achieve comprehensive discipline coverage in natural order.
    """
    
    def __init__(self):
        self.target_subtopics_per_discipline = 1000
        self.alert_system = DualPriorityAlertSystem()
        self.discipline_scope_maps = self._load_discipline_scope_maps()
        self.natural_progression_templates = self._load_natural_progression_templates()
        self.comprehensive_coverage_standards = self._load_comprehensive_coverage_standards()
        self.topic_importance_weights = self._load_topic_importance_weights()
        
    def analyze_comprehensive_coverage(self, curriculum_by_discipline: Dict[str, List[SubtopicEntry]],
                                     standards_frameworks: Dict[str, List[StandardsFramework]]) -> Dict[str, ComprehensiveAnalysisResult]:
        """
        Goal: Analyze comprehensive coverage to achieve ~1000 subtopics per discipline.
        
        Performs complete gap analysis to ensure each discipline has comprehensive
        coverage with natural educational progression to the target count.
        """
        logger.info(f"Starting comprehensive gap analysis for {len(curriculum_by_discipline)} disciplines")
        
        analysis_results = {}
        
        for discipline, curriculum in curriculum_by_discipline.items():
            logger.info(f"Analyzing {discipline}: {len(curriculum)} current subtopics")
            
            # Analyze current coverage
            coverage_analysis = self._analyze_current_coverage(discipline, curriculum)
            
            # Identify missing topics for comprehensive coverage
            missing_topics = self._identify_missing_comprehensive_topics(discipline, curriculum)
            
            # Analyze natural order progression
            order_issues = self._analyze_natural_order_progression(discipline, curriculum)
            
            # Calculate comprehensive coverage score
            coverage_score = self._calculate_comprehensive_coverage_score(discipline, curriculum, missing_topics)
            
            # Generate priority alerts
            priority_alerts = self._generate_priority_alerts(discipline, curriculum, missing_topics, standards_frameworks.get(discipline, []))
            
            # Generate expansion recommendations
            expansion_recommendations = self._generate_expansion_recommendations(discipline, curriculum, missing_topics)
            
            # Calculate coverage percentage toward target
            coverage_percentage = len(curriculum) / self.target_subtopics_per_discipline
            
            # Create comprehensive analysis result
            result = ComprehensiveAnalysisResult(
                discipline=discipline,
                total_subtopics_found=len(curriculum),
                target_subtopics=self.target_subtopics_per_discipline,
                coverage_percentage=coverage_percentage,
                identified_gaps=missing_topics,
                coverage_by_level=coverage_analysis,
                natural_order_issues=order_issues,
                comprehensive_coverage_score=coverage_score,
                priority_alerts=priority_alerts,
                expansion_recommendations=expansion_recommendations
            )
            
            analysis_results[discipline] = result
            
            logger.info(f"{discipline} analysis complete: {coverage_percentage:.1%} coverage, "
                       f"{len(missing_topics)} gaps identified, "
                       f"{coverage_score:.2f} comprehensiveness score")
        
        return analysis_results
    
    def _analyze_current_coverage(self, discipline: str, curriculum: List[SubtopicEntry]) -> Dict[str, int]:
        """Analyze current curriculum coverage by educational level."""
        coverage_by_level = defaultdict(int)
        
        for subtopic in curriculum:
            level = subtopic.level.value if hasattr(subtopic.level, 'value') else str(subtopic.level)
            coverage_by_level[level] += 1
        
        return dict(coverage_by_level)
    
    def _identify_missing_comprehensive_topics(self, discipline: str, curriculum: List[SubtopicEntry]) -> List[CurriculumGap]:
        """Identify missing topics for comprehensive discipline coverage."""
        missing_gaps = []
        
        # Get comprehensive scope map for discipline
        scope_map = self.discipline_scope_maps.get(discipline, {})
        if not scope_map:
            logger.warning(f"No scope map found for discipline: {discipline}")
            return missing_gaps
        
        # Get current topics covered
        current_topics = set(subtopic.subtopic.lower() for subtopic in curriculum)
        
        gap_id_counter = 0
        
        # Check each area in the scope map
        for area_name, area_info in scope_map.items():
            essential_topics = area_info.get('essential_topics', [])
            recommended_topics = area_info.get('recommended_topics', [])
            advanced_topics = area_info.get('advanced_topics', [])
            
            # Check essential topics (high importance)
            for topic in essential_topics:
                if not self._topic_is_covered(topic, current_topics):
                    gap_id_counter += 1
                    gap = CurriculumGap(
                        gap_id=f"{discipline}_gap_{gap_id_counter:04d}",
                        discipline=discipline,
                        missing_topic=topic,
                        importance_score=0.9,  # Essential topics are high importance
                        standards_impact=area_info.get('standards_impact', []),
                        educational_level=area_info.get('typical_level', 'Undergraduate'),
                        prerequisite_topics=area_info.get('prerequisites', []),
                        follow_up_topics=area_info.get('follow_ups', []),
                        recommended_sources=area_info.get('recommended_sources', []),
                        urgency_level=AlertSeverity.HIGH
                    )
                    missing_gaps.append(gap)
            
            # Check recommended topics (medium importance)
            for topic in recommended_topics:
                if not self._topic_is_covered(topic, current_topics):
                    gap_id_counter += 1
                    gap = CurriculumGap(
                        gap_id=f"{discipline}_gap_{gap_id_counter:04d}",
                        discipline=discipline,
                        missing_topic=topic,
                        importance_score=0.7,  # Recommended topics are medium importance
                        standards_impact=area_info.get('standards_impact', []),
                        educational_level=area_info.get('typical_level', 'Undergraduate'),
                        prerequisite_topics=area_info.get('prerequisites', []),
                        follow_up_topics=area_info.get('follow_ups', []),
                        recommended_sources=area_info.get('recommended_sources', []),
                        urgency_level=AlertSeverity.MEDIUM
                    )
                    missing_gaps.append(gap)
            
            # Check advanced topics (lower importance but needed for comprehensiveness)
            for topic in advanced_topics:
                if not self._topic_is_covered(topic, current_topics):
                    gap_id_counter += 1
                    gap = CurriculumGap(
                        gap_id=f"{discipline}_gap_{gap_id_counter:04d}",
                        discipline=discipline,
                        missing_topic=topic,
                        importance_score=0.5,  # Advanced topics are lower importance
                        standards_impact=area_info.get('standards_impact', []),
                        educational_level=area_info.get('typical_level', 'Graduate'),
                        prerequisite_topics=area_info.get('prerequisites', []),
                        follow_up_topics=area_info.get('follow_ups', []),
                        recommended_sources=area_info.get('recommended_sources', []),
                        urgency_level=AlertSeverity.MEDIUM
                    )
                    missing_gaps.append(gap)
        
        # Sort gaps by importance score (highest first)
        missing_gaps.sort(key=lambda x: x.importance_score, reverse=True)
        
        return missing_gaps
    
    def _topic_is_covered(self, target_topic: str, current_topics: Set[str]) -> bool:
        """Check if a target topic is covered by current curriculum."""
        target_lower = target_topic.lower()
        
        # Direct match
        if target_lower in current_topics:
            return True
        
        # Check for partial matches (topic is contained in current topics)
        target_words = set(target_lower.split())
        for current_topic in current_topics:
            current_words = set(current_topic.split())
            
            # If most target words are in current topic, consider it covered
            overlap = len(target_words.intersection(current_words))
            if overlap >= len(target_words) * 0.7:  # 70% word overlap
                return True
        
        return False
    
    def _analyze_natural_order_progression(self, discipline: str, curriculum: List[SubtopicEntry]) -> List[str]:
        """Analyze natural order progression issues in curriculum."""
        order_issues = []
        
        # Get natural progression template for discipline
        progression_template = self.natural_progression_templates.get(discipline, {})
        if not progression_template:
            return order_issues
        
        # Check if curriculum follows natural progression
        expected_order = progression_template.get('progression_order', [])
        prerequisite_rules = progression_template.get('prerequisite_rules', {})
        
        # Create topic to index mapping for current curriculum
        current_topics = {subtopic.subtopic.lower(): i for i, subtopic in enumerate(curriculum)}
        
        # Check prerequisite violations
        for topic, prerequisites in prerequisite_rules.items():
            if topic.lower() in current_topics:
                topic_index = current_topics[topic.lower()]
                
                for prereq in prerequisites:
                    if prereq.lower() in current_topics:
                        prereq_index = current_topics[prereq.lower()]
                        
                        if prereq_index > topic_index:
                            order_issues.append(
                                f"Prerequisite violation: '{prereq}' should come before '{topic}'"
                            )
        
        # Check for missing foundational topics
        foundational_topics = progression_template.get('foundational_topics', [])
        for foundational in foundational_topics:
            if not any(foundational.lower() in topic.lower() for topic in current_topics.keys()):
                order_issues.append(f"Missing foundational topic: '{foundational}'")
        
        return order_issues
    
    def _calculate_comprehensive_coverage_score(self, discipline: str, curriculum: List[SubtopicEntry], 
                                              missing_gaps: List[CurriculumGap]) -> float:
        """Calculate comprehensive coverage score for the discipline."""
        
        # Base score from current subtopic count
        current_count = len(curriculum)
        target_count = self.target_subtopics_per_discipline
        quantity_score = min(1.0, current_count / target_count)
        
        # Quality score from gap analysis
        total_importance = sum(gap.importance_score for gap in missing_gaps)
        max_possible_importance = len(missing_gaps) * 1.0  # If all gaps were max importance
        
        if max_possible_importance > 0:
            quality_score = 1.0 - (total_importance / max_possible_importance)
        else:
            quality_score = 1.0  # No gaps means perfect quality
        
        # Coverage distribution score
        coverage_standards = self.comprehensive_coverage_standards.get(discipline, {})
        expected_distribution = coverage_standards.get('level_distribution', {})
        
        actual_distribution = defaultdict(int)
        for subtopic in curriculum:
            level = subtopic.level.value if hasattr(subtopic.level, 'value') else str(subtopic.level)
            actual_distribution[level] += 1
        
        distribution_score = 1.0
        if expected_distribution:
            distribution_differences = []
            for level, expected_ratio in expected_distribution.items():
                expected_count = expected_ratio * current_count
                actual_count = actual_distribution.get(level, 0)
                if expected_count > 0:
                    difference = abs(actual_count - expected_count) / expected_count
                    distribution_differences.append(difference)
            
            if distribution_differences:
                avg_difference = sum(distribution_differences) / len(distribution_differences)
                distribution_score = max(0.0, 1.0 - avg_difference)
        
        # Weighted composite score
        composite_score = (
            quantity_score * 0.4 +  # 40% weight on quantity
            quality_score * 0.4 +   # 40% weight on quality (gap coverage)
            distribution_score * 0.2  # 20% weight on proper distribution
        )
        
        return composite_score
    
    def _generate_priority_alerts(self, discipline: str, curriculum: List[SubtopicEntry],
                                missing_gaps: List[CurriculumGap], 
                                standards_frameworks: List[StandardsFramework]) -> List[DualPriorityAlert]:
        """Generate priority alerts for curriculum gaps."""
        
        # Convert gaps to validation reports format for alert system
        validation_reports = {
            discipline: type('ValidationReport', (), {
                'discipline': discipline,
                'total_subtopics': len(curriculum),
                'coverage_results': {'comprehensive_coverage': len(curriculum) / self.target_subtopics_per_discipline},
                'scientific_violations': [],
                'consistency_results': [],
                'dual_priority_alerts': [],
                'overall_completeness_score': len(curriculum) / self.target_subtopics_per_discipline
            })()
        }
        
        # Generate alerts using the dual priority system
        priority_alerts = self.alert_system.generate_prioritized_alerts(
            validation_reports, [], {}
        )
        
        # Add gap-specific alerts
        for gap in missing_gaps[:20]:  # Top 20 most important gaps
            alert = DualPriorityAlert(
                discipline=discipline,
                alert_type="Comprehensive_Coverage_Gap",
                standards_importance_score=gap.importance_score,
                missing_topics_count=1,
                composite_priority_score=gap.importance_score,
                severity=gap.urgency_level,
                recommendations=[
                    f"Add missing topic: {gap.missing_topic}",
                    f"Level: {gap.educational_level}",
                    f"Prerequisites: {', '.join(gap.prerequisite_topics)}"
                ],
                affected_standards=gap.standards_impact,
                specific_missing_topics=[gap.missing_topic],
                textbook_recommendations=gap.recommended_sources
            )
            priority_alerts.append(alert)
        
        return priority_alerts
    
    def _generate_expansion_recommendations(self, discipline: str, curriculum: List[SubtopicEntry],
                                          missing_gaps: List[CurriculumGap]) -> List[str]:
        """Generate specific recommendations for expanding curriculum to ~1000 subtopics."""
        recommendations = []
        
        current_count = len(curriculum)
        target_count = self.target_subtopics_per_discipline
        needed_count = target_count - current_count
        
        if needed_count <= 0:
            recommendations.append(f"Curriculum already meets target with {current_count} subtopics")
            return recommendations
        
        recommendations.append(f"Need to add {needed_count} subtopics to reach target of {target_count}")
        
        # Prioritize by gap importance
        high_priority_gaps = [gap for gap in missing_gaps if gap.importance_score >= 0.8]
        medium_priority_gaps = [gap for gap in missing_gaps if 0.5 <= gap.importance_score < 0.8]
        
        if high_priority_gaps:
            recommendations.append(f"Priority 1: Add {len(high_priority_gaps)} essential topics")
            for gap in high_priority_gaps[:5]:  # Show top 5
                recommendations.append(f"  - {gap.missing_topic} ({gap.educational_level})")
        
        if medium_priority_gaps and needed_count > len(high_priority_gaps):
            remaining_needed = needed_count - len(high_priority_gaps)
            recommended_medium = min(remaining_needed, len(medium_priority_gaps))
            recommendations.append(f"Priority 2: Add {recommended_medium} recommended topics")
            for gap in medium_priority_gaps[:3]:  # Show top 3
                recommendations.append(f"  - {gap.missing_topic} ({gap.educational_level})")
        
        # Level-specific recommendations
        coverage_standards = self.comprehensive_coverage_standards.get(discipline, {})
        expected_distribution = coverage_standards.get('level_distribution', {})
        
        if expected_distribution:
            recommendations.append("Level distribution recommendations:")
            for level, expected_ratio in expected_distribution.items():
                expected_count = int(expected_ratio * target_count)
                current_level_count = sum(1 for s in curriculum 
                                        if str(s.educational_level) == level)
                needed_for_level = max(0, expected_count - current_level_count)
                
                if needed_for_level > 0:
                    recommendations.append(f"  - Add {needed_for_level} subtopics at {level} level")
        
        # Source recommendations
        source_counter = Counter()
        for gap in missing_gaps:
            source_counter.update(gap.recommended_sources)
        
        if source_counter:
            recommendations.append("Recommended sources for expansion:")
            for source, count in source_counter.most_common(3):
                recommendations.append(f"  - {source} (covers {count} missing topics)")
        
        return recommendations
    
    def generate_comprehensive_report(self, analysis_results: Dict[str, ComprehensiveAnalysisResult]) -> Dict:
        """Generate comprehensive gap analysis report across all disciplines."""
        
        total_subtopics = sum(result.total_subtopics_found for result in analysis_results.values())
        total_target = len(analysis_results) * self.target_subtopics_per_discipline
        overall_coverage = total_subtopics / total_target if total_target > 0 else 0.0
        
        # Summary statistics
        coverage_stats = {
            'total_disciplines_analyzed': len(analysis_results),
            'total_subtopics_found': total_subtopics,
            'total_target_subtopics': total_target,
            'overall_coverage_percentage': overall_coverage,
            'disciplines_meeting_target': len([r for r in analysis_results.values() 
                                             if r.total_subtopics_found >= self.target_subtopics_per_discipline]),
            'average_comprehensiveness_score': sum(r.comprehensive_coverage_score for r in analysis_results.values()) / len(analysis_results) if analysis_results else 0.0
        }
        
        # Priority gaps across all disciplines
        all_gaps = []
        for result in analysis_results.values():
            all_gaps.extend(result.identified_gaps)
        
        # Sort by importance and select top gaps
        top_gaps = sorted(all_gaps, key=lambda x: x.importance_score, reverse=True)[:50]
        
        # Natural order issues summary
        total_order_issues = sum(len(result.natural_order_issues) for result in analysis_results.values())
        
        return {
            'summary_statistics': coverage_stats,
            'discipline_results': {discipline: result.to_dict() for discipline, result in analysis_results.items()},
            'top_priority_gaps': [gap.to_dict() for gap in top_gaps],
            'natural_order_analysis': {
                'total_order_issues': total_order_issues,
                'disciplines_with_issues': len([r for r in analysis_results.values() if r.natural_order_issues])
            },
            'expansion_summary': self._generate_expansion_summary(analysis_results),
            'recommendations': self._generate_overall_recommendations(analysis_results)
        }
    
    def _generate_expansion_summary(self, analysis_results: Dict[str, ComprehensiveAnalysisResult]) -> Dict:
        """Generate summary of expansion needs across disciplines."""
        
        expansion_needs = {}
        for discipline, result in analysis_results.items():
            needed = self.target_subtopics_per_discipline - result.total_subtopics_found
            expansion_needs[discipline] = {
                'current_count': result.total_subtopics_found,
                'target_count': self.target_subtopics_per_discipline,
                'needed_count': max(0, needed),
                'coverage_percentage': result.coverage_percentage,
                'priority_gaps': len([gap for gap in result.identified_gaps if gap.importance_score >= 0.8])
            }
        
        return expansion_needs
    
    def _generate_overall_recommendations(self, analysis_results: Dict[str, ComprehensiveAnalysisResult]) -> List[str]:
        """Generate overall recommendations for achieving comprehensive coverage."""
        recommendations = []
        
        # Identify disciplines needing most attention
        disciplines_by_need = sorted(analysis_results.items(), 
                                   key=lambda x: x[1].comprehensive_coverage_score)
        
        lowest_coverage = disciplines_by_need[0] if disciplines_by_need else None
        if lowest_coverage and lowest_coverage[1].comprehensive_coverage_score < 0.7:
            recommendations.append(f"Priority focus: {lowest_coverage[0]} has lowest comprehensiveness score ({lowest_coverage[1].comprehensive_coverage_score:.2f})")
        
        # Overall expansion recommendations
        total_needed = sum(max(0, self.target_subtopics_per_discipline - result.total_subtopics_found) 
                         for result in analysis_results.values())
        
        if total_needed > 0:
            recommendations.append(f"Total expansion needed: {total_needed} subtopics across all disciplines")
        
        # Natural order recommendations
        disciplines_with_order_issues = [discipline for discipline, result in analysis_results.items() 
                                       if result.natural_order_issues]
        
        if disciplines_with_order_issues:
            recommendations.append(f"Address prerequisite order issues in: {', '.join(disciplines_with_order_issues)}")
        
        # Standards coverage recommendations
        disciplines_needing_standards_work = [discipline for discipline, result in analysis_results.items()
                                            if len(result.identified_gaps) > 50]
        
        if disciplines_needing_standards_work:
            recommendations.append(f"Enhance standards coverage in: {', '.join(disciplines_needing_standards_work)}")
        
        return recommendations
    
    def _load_discipline_scope_maps(self) -> Dict[str, Dict[str, Dict]]:
        """Load comprehensive scope maps defining what each discipline should cover."""
        return {
            'Physics': {
                'Classical_Mechanics': {
                    'essential_topics': [
                        'Kinematics', 'Newton\'s Laws', 'Work and Energy', 'Momentum Conservation',
                        'Rotational Motion', 'Angular Momentum', 'Oscillations', 'Waves'
                    ],
                    'recommended_topics': [
                        'Lagrangian Mechanics', 'Hamiltonian Mechanics', 'Central Force Motion',
                        'Rigid Body Dynamics', 'Coupled Oscillators', 'Wave Equations'
                    ],
                    'advanced_topics': [
                        'Chaos Theory', 'Nonlinear Dynamics', 'Continuum Mechanics',
                        'Fluid Dynamics', 'Elasticity Theory'
                    ],
                    'typical_level': 'Undergraduate',
                    'standards_impact': ['AP_Physics', 'IB_Physics'],
                    'prerequisites': ['Calculus', 'Vector Analysis'],
                    'recommended_sources': ['Goldstein Classical Mechanics', 'Taylor Classical Mechanics']
                },
                'Electromagnetism': {
                    'essential_topics': [
                        'Electric Fields', 'Magnetic Fields', 'Gauss\'s Law', 'Ampere\'s Law',
                        'Faraday\'s Law', 'Maxwell Equations', 'Electromagnetic Waves'
                    ],
                    'recommended_topics': [
                        'Multipole Expansion', 'Electromagnetic Radiation', 'Waveguides',
                        'Antenna Theory', 'Plasma Physics'
                    ],
                    'advanced_topics': [
                        'Relativistic Electromagnetism', 'Gauge Theory', 'Quantum Electrodynamics',
                        'Nonlinear Optics'
                    ],
                    'typical_level': 'Undergraduate',
                    'standards_impact': ['AP_Physics', 'IB_Physics'],
                    'prerequisites': ['Vector Calculus', 'Classical Mechanics'],
                    'recommended_sources': ['Griffiths Electrodynamics', 'Jackson Classical Electrodynamics']
                },
                'Quantum_Mechanics': {
                    'essential_topics': [
                        'Wave-Particle Duality', 'Schrödinger Equation', 'Quantum States',
                        'Operators', 'Angular Momentum', 'Hydrogen Atom', 'Spin'
                    ],
                    'recommended_topics': [
                        'Perturbation Theory', 'Variational Methods', 'Scattering Theory',
                        'Identical Particles', 'Quantum Statistics'
                    ],
                    'advanced_topics': [
                        'Quantum Field Theory', 'Many-Body Theory', 'Quantum Information',
                        'Decoherence', 'Quantum Computing'
                    ],
                    'typical_level': 'Advanced Undergraduate',
                    'standards_impact': ['Advanced Physics'],
                    'prerequisites': ['Linear Algebra', 'Classical Mechanics', 'Electromagnetism'],
                    'recommended_sources': ['Griffiths Quantum Mechanics', 'Shankar Quantum Mechanics']
                },
                'Thermodynamics': {
                    'essential_topics': [
                        'Laws of Thermodynamics', 'Heat Engines', 'Entropy', 'Phase Transitions',
                        'Statistical Mechanics', 'Kinetic Theory'
                    ],
                    'recommended_topics': [
                        'Ensemble Theory', 'Partition Functions', 'Critical Phenomena',
                        'Transport Phenomena', 'Irreversible Thermodynamics'
                    ],
                    'advanced_topics': [
                        'Renormalization Group', 'Non-equilibrium Statistical Mechanics',
                        'Information Theory', 'Maximum Entropy Methods'
                    ],
                    'typical_level': 'Undergraduate',
                    'standards_impact': ['AP_Physics', 'IB_Physics'],
                    'prerequisites': ['Calculus', 'Classical Mechanics'],
                    'recommended_sources': ['Schroeder Thermal Physics', 'Callen Thermodynamics']
                },
                'Modern_Physics': {
                    'essential_topics': [
                        'Special Relativity', 'General Relativity', 'Particle Physics',
                        'Nuclear Physics', 'Atomic Physics', 'Solid State Physics'
                    ],
                    'recommended_topics': [
                        'Cosmology', 'Astrophysics', 'Accelerator Physics',
                        'Detector Physics', 'Medical Physics'
                    ],
                    'advanced_topics': [
                        'String Theory', 'Dark Matter', 'Dark Energy',
                        'Quantum Gravity', 'Extra Dimensions'
                    ],
                    'typical_level': 'Advanced Undergraduate',
                    'standards_impact': ['Advanced Physics'],
                    'prerequisites': ['Quantum Mechanics', 'Electromagnetism'],
                    'recommended_sources': ['Beiser Modern Physics', 'Griffiths Particle Physics']
                }
            },
            'Chemistry': {
                'General_Chemistry': {
                    'essential_topics': [
                        'Atomic Structure', 'Periodic Table', 'Chemical Bonding', 'Molecular Geometry',
                        'Stoichiometry', 'Chemical Reactions', 'Thermochemistry', 'Kinetics'
                    ],
                    'recommended_topics': [
                        'Quantum Chemistry', 'Group Theory', 'Crystallography',
                        'Surface Chemistry', 'Electrochemistry'
                    ],
                    'advanced_topics': [
                        'Computational Chemistry', 'Materials Chemistry', 'Nanotechnology',
                        'Green Chemistry', 'Chemical Biology'
                    ],
                    'typical_level': 'Undergraduate',
                    'standards_impact': ['AP_Chemistry', 'IB_Chemistry'],
                    'prerequisites': ['Mathematics', 'Basic Physics'],
                    'recommended_sources': ['Atkins Physical Chemistry', 'Brown Chemistry']
                },
                'Organic_Chemistry': {
                    'essential_topics': [
                        'Alkanes', 'Alkenes', 'Alkynes', 'Aromatic Compounds', 'Functional Groups',
                        'Stereochemistry', 'Reaction Mechanisms', 'Synthesis'
                    ],
                    'recommended_topics': [
                        'Organometallic Chemistry', 'Polymer Chemistry', 'Natural Products',
                        'Drug Design', 'Catalysis'
                    ],
                    'advanced_topics': [
                        'Total Synthesis', 'Asymmetric Synthesis', 'Chemical Biology',
                        'Medicinal Chemistry', 'Materials Science'
                    ],
                    'typical_level': 'Undergraduate',
                    'standards_impact': ['AP_Chemistry', 'ACS_Organic'],
                    'prerequisites': ['General Chemistry'],
                    'recommended_sources': ['Clayden Organic Chemistry', 'Smith Organic Chemistry']
                },
                'Physical_Chemistry': {
                    'essential_topics': [
                        'Thermodynamics', 'Kinetics', 'Quantum Chemistry', 'Statistical Mechanics',
                        'Spectroscopy', 'Electrochemistry', 'Surface Chemistry'
                    ],
                    'recommended_topics': [
                        'Molecular Dynamics', 'Computational Methods', 'Photochemistry',
                        'Laser Chemistry', 'Single Molecule Studies'
                    ],
                    'advanced_topics': [
                        'Quantum Information', 'Femtochemistry', 'Ultracold Chemistry',
                        'Chemical Dynamics', 'Reaction Control'
                    ],
                    'typical_level': 'Advanced Undergraduate',
                    'standards_impact': ['ACS_Physical'],
                    'prerequisites': ['Calculus', 'Physics', 'General Chemistry'],
                    'recommended_sources': ['Atkins Physical Chemistry', 'McQuarrie Physical Chemistry']
                }
            },
            'Biology': {
                'Cell_Biology': {
                    'essential_topics': [
                        'Cell Structure', 'Membrane Biology', 'Organelles', 'Cell Division',
                        'Signal Transduction', 'Metabolism', 'Gene Expression', 'Protein Synthesis'
                    ],
                    'recommended_topics': [
                        'Stem Cells', 'Cell Death', 'Cell Motility', 'Cell Adhesion',
                        'Tissue Engineering', 'Regenerative Medicine'
                    ],
                    'advanced_topics': [
                        'Single Cell Analysis', 'Synthetic Biology', 'Cell Reprogramming',
                        'Organoids', 'CRISPR Technology'
                    ],
                    'typical_level': 'Undergraduate',
                    'standards_impact': ['AP_Biology', 'IB_Biology'],
                    'prerequisites': ['General Biology', 'Chemistry'],
                    'recommended_sources': ['Alberts Cell Biology', 'Lodish Molecular Cell Biology']
                },
                'Genetics': {
                    'essential_topics': [
                        'Mendelian Genetics', 'DNA Structure', 'Replication', 'Transcription',
                        'Translation', 'Mutation', 'Population Genetics', 'Evolution'
                    ],
                    'recommended_topics': [
                        'Genomics', 'Epigenetics', 'Gene Regulation', 'Developmental Genetics',
                        'Medical Genetics', 'Pharmacogenomics'
                    ],
                    'advanced_topics': [
                        'CRISPR', 'Gene Therapy', 'Personalized Medicine', 'Synthetic Biology',
                        'Ancient DNA', 'Metagenomics'
                    ],
                    'typical_level': 'Undergraduate',
                    'standards_impact': ['AP_Biology', 'IB_Biology'],
                    'prerequisites': ['Cell Biology', 'Chemistry'],
                    'recommended_sources': ['Hartwell Genetics', 'Griffiths Genetic Analysis']
                },
                'Ecology': {
                    'essential_topics': [
                        'Population Ecology', 'Community Ecology', 'Ecosystem Ecology',
                        'Biogeochemical Cycles', 'Biodiversity', 'Conservation Biology'
                    ],
                    'recommended_topics': [
                        'Landscape Ecology', 'Marine Ecology', 'Climate Change Biology',
                        'Restoration Ecology', 'Urban Ecology'
                    ],
                    'advanced_topics': [
                        'Global Change Biology', 'Extinction Biology', 'Invasion Biology',
                        'Ecosystem Services', 'Environmental Genomics'
                    ],
                    'typical_level': 'Undergraduate',
                    'standards_impact': ['AP_Biology', 'Environmental Science'],
                    'prerequisites': ['General Biology', 'Statistics'],
                    'recommended_sources': ['Begon Ecology', 'Ricklefs Economy of Nature']
                }
            }
        }
    
    def _load_natural_progression_templates(self) -> Dict[str, Dict]:
        """Load natural progression templates for each discipline."""
        return {
            'Physics': {
                'progression_order': [
                    'Basic Mathematics', 'Mechanics', 'Thermodynamics', 'Waves',
                    'Electromagnetism', 'Modern Physics', 'Quantum Mechanics'
                ],
                'foundational_topics': [
                    'Vector Analysis', 'Calculus', 'Newton\'s Laws', 'Energy Conservation'
                ],
                'prerequisite_rules': {
                    'Electromagnetism': ['Vector Calculus', 'Classical Mechanics'],
                    'Quantum Mechanics': ['Linear Algebra', 'Classical Mechanics', 'Electromagnetism'],
                    'Statistical Mechanics': ['Thermodynamics', 'Probability Theory'],
                    'General Relativity': ['Special Relativity', 'Tensor Analysis']
                }
            },
            'Chemistry': {
                'progression_order': [
                    'Atomic Structure', 'Chemical Bonding', 'Molecular Geometry',
                    'Thermochemistry', 'Kinetics', 'Equilibrium', 'Organic Chemistry'
                ],
                'foundational_topics': [
                    'Atomic Theory', 'Periodic Table', 'Chemical Bonding', 'Stoichiometry'
                ],
                'prerequisite_rules': {
                    'Organic Chemistry': ['General Chemistry', 'Chemical Bonding'],
                    'Physical Chemistry': ['Calculus', 'General Chemistry', 'Physics'],
                    'Biochemistry': ['Organic Chemistry', 'Biology'],
                    'Quantum Chemistry': ['Physical Chemistry', 'Linear Algebra']
                }
            },
            'Biology': {
                'progression_order': [
                    'Cell Biology', 'Genetics', 'Molecular Biology', 'Physiology',
                    'Evolution', 'Ecology', 'Systems Biology'
                ],
                'foundational_topics': [
                    'Cell Structure', 'DNA Structure', 'Protein Synthesis', 'Metabolism'
                ],
                'prerequisite_rules': {
                    'Genetics': ['Cell Biology', 'DNA Structure'],
                    'Molecular Biology': ['Cell Biology', 'Genetics'],
                    'Biochemistry': ['Cell Biology', 'Chemistry'],
                    'Systems Biology': ['Molecular Biology', 'Mathematics']
                }
            }
        }
    
    def _load_comprehensive_coverage_standards(self) -> Dict[str, Dict]:
        """Load standards for comprehensive coverage expectations."""
        return {
            'Physics': {
                'level_distribution': {
                    'High_School_Introductory': 0.15,
                    'High_School_Advanced': 0.20,
                    'Undergraduate_Introductory': 0.25,
                    'Undergraduate_Advanced': 0.25,
                    'Graduate_Introductory': 0.10,
                    'Graduate_Advanced': 0.05
                },
                'minimum_areas_covered': 15,
                'comprehensiveness_threshold': 0.85
            },
            'Chemistry': {
                'level_distribution': {
                    'High_School_Introductory': 0.20,
                    'High_School_Advanced': 0.25,
                    'Undergraduate_Introductory': 0.30,
                    'Undergraduate_Advanced': 0.20,
                    'Graduate_Introductory': 0.05
                },
                'minimum_areas_covered': 12,
                'comprehensiveness_threshold': 0.80
            },
            'Biology': {
                'level_distribution': {
                    'High_School_Introductory': 0.25,
                    'High_School_Advanced': 0.30,
                    'Undergraduate_Introductory': 0.25,
                    'Undergraduate_Advanced': 0.15,
                    'Graduate_Introductory': 0.05
                },
                'minimum_areas_covered': 18,
                'comprehensiveness_threshold': 0.75
            }
        }
    
    def _load_topic_importance_weights(self) -> Dict[str, Dict[str, float]]:
        """Load importance weights for different types of topics."""
        return {
            'Physics': {
                'foundational': 1.0,
                'core_theory': 0.9,
                'applications': 0.7,
                'advanced_theory': 0.6,
                'research_frontiers': 0.4
            },
            'Chemistry': {
                'fundamental_concepts': 1.0,
                'core_reactions': 0.9,
                'mechanisms': 0.8,
                'applications': 0.7,
                'research_areas': 0.5
            },
            'Biology': {
                'basic_principles': 1.0,
                'cellular_processes': 0.9,
                'organismal_biology': 0.8,
                'ecological_concepts': 0.7,
                'biotechnology': 0.6
            }
        }