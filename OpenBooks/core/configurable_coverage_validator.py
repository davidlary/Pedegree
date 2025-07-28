#!/usr/bin/env python3
"""
configurable_coverage_validator.py - Validate curriculum coverage with configurable thresholds

This module implements framework-specific coverage validation with configurable
thresholds instead of uniform requirements, enabling tailored validation standards.
"""

import logging
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from datetime import datetime
import json

from .data_models import (
    SubtopicEntry, StandardsFramework, ValidationReport, DualPriorityAlert,
    AlertSeverity, ConfigurableCoverageThreshold
)

logger = logging.getLogger(__name__)


@dataclass
class CoverageAnalysis:
    """
    Goal: Detailed analysis of coverage for a specific standards framework.
    
    Contains comprehensive coverage metrics and gap identification for
    framework-specific validation.
    """
    framework_name: str
    total_outcomes: int
    covered_outcomes: int
    coverage_percentage: float
    threshold_requirement: float
    threshold_met: bool
    missing_outcomes: List[str]
    partially_covered_outcomes: List[str]
    confidence_score: float  # 0-1 confidence in coverage assessment
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'framework_name': self.framework_name,
            'total_outcomes': self.total_outcomes,
            'covered_outcomes': self.covered_outcomes,
            'coverage_percentage': self.coverage_percentage,
            'threshold_requirement': self.threshold_requirement,
            'threshold_met': self.threshold_met,
            'missing_outcomes': self.missing_outcomes,
            'partially_covered_outcomes': self.partially_covered_outcomes,
            'confidence_score': self.confidence_score
        }


@dataclass
class TextbookCoverageGap:
    """
    Goal: Identify specific textbook coverage gaps for targeted recommendations.
    
    Tracks which textbooks lack coverage of important topics to guide
    acquisition and curriculum development decisions.
    """
    topic: str
    missing_in_textbooks: List[str]
    coverage_percentage: float
    importance_score: float
    recommended_sources: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'topic': self.topic,
            'missing_in_textbooks': self.missing_in_textbooks,
            'coverage_percentage': self.coverage_percentage,
            'importance_score': self.importance_score,
            'recommended_sources': self.recommended_sources
        }


class ConfigurableCoverageValidator:
    """
    Goal: Validate curriculum coverage with framework-specific configurable thresholds.
    
    Provides detailed coverage analysis with different requirements for different
    standards frameworks, enabling tailored validation and targeted improvements.
    """
    
    def __init__(self, threshold_config: Optional[Dict[str, float]] = None):
        self.coverage_thresholds = threshold_config or self._load_default_thresholds()
        self.framework_priorities = self._load_framework_priorities()
        self.coverage_history: Dict[str, List[CoverageAnalysis]] = {}
        self.textbook_coverage_cache: Dict[str, Dict[str, float]] = {}
        
    def validate_with_configurable_thresholds(self, discipline: str, 
                                            curriculum: List[SubtopicEntry],
                                            standards_frameworks: List[StandardsFramework]) -> ValidationReport:
        """
        Goal: Validate curriculum coverage using framework-specific thresholds.
        
        Performs comprehensive coverage analysis with different requirements
        for each standards framework and generates detailed validation report.
        """
        logger.info(f"Validating coverage for {discipline} with {len(standards_frameworks)} frameworks")
        
        coverage_results = {}
        framework_analyses = {}
        
        # Analyze coverage for each framework
        for framework in standards_frameworks:
            analysis = self._analyze_framework_coverage(discipline, curriculum, framework)
            coverage_results[framework.name] = analysis.coverage_percentage
            framework_analyses[framework.name] = analysis
            
            logger.info(f"{framework.name}: {analysis.coverage_percentage:.1%} coverage "
                       f"(threshold: {analysis.threshold_requirement:.1%})")
        
        # Calculate overall completeness score
        overall_completeness = self._calculate_overall_completeness(coverage_results, standards_frameworks)
        
        # Generate textbook coverage gaps
        textbook_gaps = self._analyze_textbook_coverage_gaps(discipline, curriculum, standards_frameworks)
        
        # Store coverage history
        if discipline not in self.coverage_history:
            self.coverage_history[discipline] = []
        self.coverage_history[discipline].extend(framework_analyses.values())
        
        # Create validation report
        validation_report = ValidationReport(
            discipline=discipline,
            total_subtopics=len(curriculum),
            coverage_results=coverage_results,
            scientific_violations=[],  # Will be populated by other components
            consistency_results=[],     # Will be populated by other components
            dual_priority_alerts=[],   # Will be populated by other components
            overall_completeness_score=overall_completeness
        )
        
        logger.info(f"Validation complete for {discipline}: "
                   f"{overall_completeness:.1%} overall completeness")
        
        return validation_report
    
    def _analyze_framework_coverage(self, discipline: str, curriculum: List[SubtopicEntry],
                                   framework: StandardsFramework) -> CoverageAnalysis:
        """Analyze coverage for a specific standards framework."""
        
        # Get threshold for this framework
        threshold = self._get_framework_threshold(framework.name)
        
        # Map curriculum topics to framework outcomes
        topic_to_outcomes = self._map_topics_to_outcomes(curriculum, framework)
        
        # Calculate coverage
        total_outcomes = len(framework.outcomes)
        covered_outcomes = len([outcome for outcome in framework.outcomes 
                               if self._is_outcome_covered(outcome, topic_to_outcomes)])
        
        coverage_percentage = covered_outcomes / total_outcomes if total_outcomes > 0 else 0.0
        
        # Identify missing and partially covered outcomes
        missing_outcomes = []
        partially_covered_outcomes = []
        
        for outcome in framework.outcomes:
            coverage_level = self._assess_outcome_coverage(outcome, topic_to_outcomes)
            if coverage_level == 0.0:
                missing_outcomes.append(outcome)
            elif coverage_level < 0.8:  # Partially covered threshold
                partially_covered_outcomes.append(outcome)
        
        # Calculate confidence score
        confidence_score = self._calculate_coverage_confidence(framework, topic_to_outcomes)
        
        return CoverageAnalysis(
            framework_name=framework.name,
            total_outcomes=total_outcomes,
            covered_outcomes=covered_outcomes,
            coverage_percentage=coverage_percentage,
            threshold_requirement=threshold,
            threshold_met=coverage_percentage >= threshold,
            missing_outcomes=missing_outcomes,
            partially_covered_outcomes=partially_covered_outcomes,
            confidence_score=confidence_score
        )
    
    def _map_topics_to_outcomes(self, curriculum: List[SubtopicEntry], 
                               framework: StandardsFramework) -> Dict[str, List[str]]:
        """Map curriculum topics to framework outcomes."""
        topic_to_outcomes = {}
        
        for subtopic in curriculum:
            # Check standards links
            relevant_outcomes = []
            for standards_link in subtopic.standards_links:
                if framework.name in standards_link:
                    # Extract specific outcomes from the link
                    outcomes = self._extract_outcomes_from_link(standards_link, framework)
                    relevant_outcomes.extend(outcomes)
            
            # Also check by keyword matching
            keyword_outcomes = self._match_outcomes_by_keywords(subtopic, framework)
            relevant_outcomes.extend(keyword_outcomes)
            
            if relevant_outcomes:
                topic_to_outcomes[subtopic.subtopic] = list(set(relevant_outcomes))
        
        return topic_to_outcomes
    
    def _is_outcome_covered(self, outcome: str, topic_to_outcomes: Dict[str, List[str]]) -> bool:
        """Check if a specific outcome is covered by curriculum topics."""
        for topic, outcomes in topic_to_outcomes.items():
            if outcome in outcomes:
                return True
        return False
    
    def _assess_outcome_coverage(self, outcome: str, topic_to_outcomes: Dict[str, List[str]]) -> float:
        """Assess the level of coverage for a specific outcome (0.0 to 1.0)."""
        coverage_count = 0
        total_relevant_topics = 0
        
        # Count how many topics address this outcome
        for topic, outcomes in topic_to_outcomes.items():
            if any(self._outcomes_match(outcome, covered_outcome) for covered_outcome in outcomes):
                coverage_count += 1
            total_relevant_topics += 1
        
        if total_relevant_topics == 0:
            return 0.0
        
        # Simple coverage assessment - can be made more sophisticated
        if coverage_count >= 2:  # Multiple topics cover this outcome
            return 1.0
        elif coverage_count == 1:
            return 0.8  # Single topic coverage
        else:
            return 0.0
    
    def _outcomes_match(self, outcome1: str, outcome2: str) -> bool:
        """Check if two outcomes match (fuzzy matching)."""
        # Simple keyword-based matching - can be enhanced with NLP
        outcome1_lower = outcome1.lower()
        outcome2_lower = outcome2.lower()
        
        # Exact match
        if outcome1_lower == outcome2_lower:
            return True
        
        # Keyword overlap
        words1 = set(outcome1_lower.split())
        words2 = set(outcome2_lower.split())
        
        # Remove common words
        stop_words = {'and', 'or', 'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'with'}
        words1 -= stop_words
        words2 -= stop_words
        
        if len(words1) == 0 or len(words2) == 0:
            return False
        
        # Check for significant overlap
        overlap = len(words1.intersection(words2))
        min_words = min(len(words1), len(words2))
        
        return overlap / min_words >= 0.7  # 70% word overlap threshold
    
    def _extract_outcomes_from_link(self, standards_link: str, framework: StandardsFramework) -> List[str]:
        """Extract specific outcomes from a standards link."""
        # Simplified implementation - in practice would parse structured links
        matching_outcomes = []
        
        for outcome in framework.outcomes:
            if any(keyword.lower() in standards_link.lower() 
                   for keyword in outcome.split()[:3]):  # Check first 3 words
                matching_outcomes.append(outcome)
        
        return matching_outcomes
    
    def _match_outcomes_by_keywords(self, subtopic: SubtopicEntry, 
                                   framework: StandardsFramework) -> List[str]:
        """Match framework outcomes to subtopic by keyword analysis."""
        matching_outcomes = []
        
        # Combine subtopic text for analysis
        subtopic_text = " ".join([
            subtopic.subtopic,
            subtopic.discipline_specific_context,
            " ".join(subtopic.learning_objectives),
            " ".join(subtopic.discipline_specific_learning_objectives)
        ]).lower()
        
        for outcome in framework.outcomes:
            outcome_keywords = set(outcome.lower().split())
            subtopic_keywords = set(subtopic_text.split())
            
            # Remove stop words
            stop_words = {'and', 'or', 'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'with'}
            outcome_keywords -= stop_words
            subtopic_keywords -= stop_words
            
            if len(outcome_keywords) == 0:
                continue
            
            # Check for keyword overlap
            overlap = len(outcome_keywords.intersection(subtopic_keywords))
            if overlap / len(outcome_keywords) >= 0.5:  # 50% keyword overlap
                matching_outcomes.append(outcome)
        
        return matching_outcomes
    
    def _calculate_coverage_confidence(self, framework: StandardsFramework, 
                                     topic_to_outcomes: Dict[str, List[str]]) -> float:
        """Calculate confidence score for coverage assessment."""
        # Factors affecting confidence:
        # 1. Clarity of standards-to-topic mapping
        # 2. Number of topics mapped
        # 3. Quality of keyword matching
        
        total_mappings = sum(len(outcomes) for outcomes in topic_to_outcomes.values())
        total_topics = len(topic_to_outcomes)
        total_outcomes = len(framework.outcomes)
        
        if total_topics == 0 or total_outcomes == 0:
            return 0.0
        
        # Base confidence from mapping density
        mapping_density = total_mappings / (total_topics * total_outcomes)
        base_confidence = min(mapping_density * 2, 0.8)  # Cap at 0.8
        
        # Boost confidence if framework has clear structure
        if hasattr(framework, 'authority_score'):
            authority_boost = framework.authority_score * 0.2
            base_confidence += authority_boost
        
        return min(base_confidence, 1.0)
    
    def _calculate_overall_completeness(self, coverage_results: Dict[str, float],
                                      standards_frameworks: List[StandardsFramework]) -> float:
        """Calculate overall curriculum completeness score."""
        if not coverage_results:
            return 0.0
        
        # Weight by framework importance
        weighted_sum = 0.0
        total_weight = 0.0
        
        for framework in standards_frameworks:
            coverage = coverage_results.get(framework.name, 0.0)
            weight = self.framework_priorities.get(framework.name, 1.0)
            
            weighted_sum += coverage * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def _analyze_textbook_coverage_gaps(self, discipline: str, curriculum: List[SubtopicEntry],
                                      standards_frameworks: List[StandardsFramework]) -> List[TextbookCoverageGap]:
        """Analyze which textbooks lack coverage of important topics."""
        gaps = []
        
        # Group subtopics by textbook references
        textbook_coverage = {}
        all_textbooks = set()
        
        for subtopic in curriculum:
            for ref in subtopic.textbook_references:
                textbook = ref.get('title', 'Unknown')
                all_textbooks.add(textbook)
                
                if textbook not in textbook_coverage:
                    textbook_coverage[textbook] = []
                textbook_coverage[textbook].append(subtopic.subtopic)
        
        # Identify important topics from standards
        important_topics = set()
        for framework in standards_frameworks:
            for outcome in framework.outcomes:
                # Extract key concepts from outcomes
                key_concepts = self._extract_key_concepts(outcome)
                important_topics.update(key_concepts)
        
        # Find gaps for each important topic
        for topic in important_topics:
            missing_textbooks = []
            covered_textbooks = []
            
            for textbook in all_textbooks:
                covered_topics = textbook_coverage.get(textbook, [])
                if not any(self._topic_matches_concept(t, topic) for t in covered_topics):
                    missing_textbooks.append(textbook)
                else:
                    covered_textbooks.append(textbook)
            
            if missing_textbooks:
                coverage_percentage = len(covered_textbooks) / len(all_textbooks) if all_textbooks else 0.0
                importance_score = self._calculate_topic_importance(topic, standards_frameworks)
                
                gap = TextbookCoverageGap(
                    topic=topic,
                    missing_in_textbooks=missing_textbooks,
                    coverage_percentage=coverage_percentage,
                    importance_score=importance_score,
                    recommended_sources=self._recommend_sources_for_topic(topic, discipline)
                )
                gaps.append(gap)
        
        # Sort by importance and coverage gap
        gaps.sort(key=lambda x: (x.importance_score * (1 - x.coverage_percentage)), reverse=True)
        
        return gaps[:20]  # Return top 20 gaps
    
    def _extract_key_concepts(self, outcome: str) -> List[str]:
        """Extract key concepts from a standards outcome."""
        # Simple concept extraction - can be enhanced with NLP
        concepts = []
        
        # Look for noun phrases and key terms
        words = outcome.lower().split()
        for i, word in enumerate(words):
            # Skip articles and prepositions
            if word in ['the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'with']:
                continue
            
            # Single word concepts
            if len(word) > 3:  # Skip very short words
                concepts.append(word)
            
            # Two-word concepts
            if i < len(words) - 1:
                two_word = f"{word} {words[i+1]}"
                if len(two_word) > 8:  # Reasonable length
                    concepts.append(two_word)
        
        return concepts[:5]  # Return top 5 concepts
    
    def _topic_matches_concept(self, topic: str, concept: str) -> bool:
        """Check if a topic matches a key concept."""
        topic_lower = topic.lower()
        concept_lower = concept.lower()
        
        # Direct inclusion
        if concept_lower in topic_lower or topic_lower in concept_lower:
            return True
        
        # Word overlap
        topic_words = set(topic_lower.split())
        concept_words = set(concept_lower.split())
        
        overlap = len(topic_words.intersection(concept_words))
        min_words = min(len(topic_words), len(concept_words))
        
        return overlap / min_words >= 0.6 if min_words > 0 else False
    
    def _calculate_topic_importance(self, topic: str, standards_frameworks: List[StandardsFramework]) -> float:
        """Calculate importance score for a topic based on standards presence."""
        importance = 0.0
        
        for framework in standards_frameworks:
            framework_weight = self.framework_priorities.get(framework.name, 1.0)
            
            # Check how many outcomes mention this topic
            mentions = 0
            for outcome in framework.outcomes:
                if self._topic_matches_concept(outcome, topic):
                    mentions += 1
            
            # Add weighted importance
            if mentions > 0:
                framework_importance = min(mentions / len(framework.outcomes), 0.5) * framework_weight
                importance += framework_importance
        
        return min(importance, 1.0)
    
    def _recommend_sources_for_topic(self, topic: str, discipline: str) -> List[str]:
        """Recommend sources for covering a specific topic."""
        # Discipline-specific source recommendations
        source_recommendations = {
            'Physics': {
                'mechanics': ['Classical Mechanics by Taylor', 'University Physics by Young'],
                'electromagnetism': ['Griffiths Electrodynamics', 'Electricity and Magnetism by Purcell'],
                'thermodynamics': ['Thermal Physics by Schroeder', 'Heat and Thermodynamics by Zemansky'],
                'quantum': ['Quantum Mechanics by Griffiths', 'Modern Physics by Beiser']
            },
            'Chemistry': {
                'organic': ['Organic Chemistry by Clayden', 'Organic Chemistry by McMurry'],
                'physical': ['Physical Chemistry by Atkins', 'Physical Chemistry by McQuarrie'],
                'inorganic': ['Inorganic Chemistry by Housecroft', 'Advanced Inorganic Chemistry by Cotton'],
                'analytical': ['Analytical Chemistry by Skoog', 'Quantitative Chemical Analysis by Harris']
            },
            'Biology': {
                'molecular': ['Molecular Biology of the Cell by Alberts', 'Molecular Biology by Weaver'],
                'genetics': ['Genetics by Hartwell', 'Introduction to Genetic Analysis by Griffiths'],
                'ecology': ['Ecology by Begon', 'Community Ecology by Morin'],
                'evolution': ['Evolution by Futuyma', 'The Selfish Gene by Dawkins']
            }
        }
        
        recommendations = []
        discipline_sources = source_recommendations.get(discipline, {})
        
        # Find matching topic categories
        topic_lower = topic.lower()
        for category, sources in discipline_sources.items():
            if category in topic_lower or any(word in topic_lower for word in category.split()):
                recommendations.extend(sources)
        
        # Add general recommendations if no specific matches
        if not recommendations:
            general_sources = {
                'Physics': ['University Physics by Young', 'Principles of Physics by Halliday'],
                'Chemistry': ['Chemistry: The Central Science by Brown', 'General Chemistry by Petrucci'],
                'Biology': ['Campbell Biology', 'Biology by Raven'],
                'Psychology': ['Psychology by Myers', 'Cognitive Psychology by Sternberg'],
                'Mathematics': ['Calculus by Stewart', 'Linear Algebra by Strang']
            }
            recommendations = general_sources.get(discipline, [f'{discipline} textbook'])
        
        return recommendations[:3]  # Return top 3 recommendations
    
    def _load_default_thresholds(self) -> Dict[str, float]:
        """Load default coverage thresholds by framework."""
        return {
            'MCAT': 0.98,  # Very high threshold for medical education
            'NGSS': 0.95,  # High threshold for K-12 science standards
            'AP_Physics': 0.90,
            'AP_Chemistry': 0.90,
            'AP_Biology': 0.90,
            'AP_Psychology': 0.88,
            'IB_Physics': 0.92,
            'IB_Chemistry': 0.92,
            'IB_Biology': 0.92,
            'ACS_Chemistry': 0.93,
            'AAPT_Physics': 0.94,
            'APA_Psychology': 0.91,
            'WHO_Health': 0.96,
            'default': 0.95
        }
    
    def _load_framework_priorities(self) -> Dict[str, float]:
        """Load importance weights for different frameworks."""
        return {
            'MCAT': 1.0,  # Highest priority
            'NGSS': 0.9,
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
            'University_Standards': 0.7,
            'Professional_Certifications': 0.75
        }
    
    def _get_framework_threshold(self, framework_name: str) -> float:
        """Get coverage threshold for specific framework."""
        return self.coverage_thresholds.get(framework_name, self.coverage_thresholds.get('default', 0.95))
    
    def update_threshold(self, framework_name: str, new_threshold: float, justification: str = "") -> None:
        """Update coverage threshold for a framework."""
        self.coverage_thresholds[framework_name] = new_threshold
        logger.info(f"Updated threshold for {framework_name}: {new_threshold:.1%} - {justification}")
    
    def get_coverage_trends(self, discipline: str) -> Dict[str, Any]:
        """Get coverage trends over time for a discipline."""
        if discipline not in self.coverage_history:
            return {"message": f"No coverage history for {discipline}"}
        
        history = self.coverage_history[discipline]
        
        # Group by framework
        by_framework = {}
        for analysis in history:
            framework = analysis.framework_name
            if framework not in by_framework:
                by_framework[framework] = []
            by_framework[framework].append(analysis.coverage_percentage)
        
        # Calculate trends
        trends = {}
        for framework, percentages in by_framework.items():
            if len(percentages) >= 2:
                trend = "improving" if percentages[-1] > percentages[0] else "declining"
                change = percentages[-1] - percentages[0]
            else:
                trend = "stable"
                change = 0.0
            
            trends[framework] = {
                'trend': trend,
                'change': change,
                'current': percentages[-1] if percentages else 0.0,
                'history_length': len(percentages)
            }
        
        return trends
    
    def export_coverage_config(self) -> Dict[str, Any]:
        """Export current coverage configuration."""
        return {
            'thresholds': self.coverage_thresholds,
            'priorities': self.framework_priorities,
            'export_timestamp': datetime.now().isoformat()
        }
    
    def import_coverage_config(self, config: Dict[str, Any]) -> None:
        """Import coverage configuration."""
        if 'thresholds' in config:
            self.coverage_thresholds.update(config['thresholds'])
        if 'priorities' in config:
            self.framework_priorities.update(config['priorities'])
        
        logger.info("Imported coverage configuration successfully")