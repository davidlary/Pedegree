#!/usr/bin/env python3
"""
book_difficulty_ranker.py - Rank books by difficulty with validation

This module ranks books from introductory to advanced levels with scientific
validation to ensure proper educational progression and authority verification.
"""

import logging
import re
import math
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from collections import defaultdict, Counter
from enum import Enum

from .data_models import TOCEntry, SubtopicEntry, EducationalLevel

logger = logging.getLogger(__name__)


class DifficultyLevel(Enum):
    """Standardized difficulty levels for educational progression."""
    ELEMENTARY = "Elementary"
    HIGH_SCHOOL_INTRO = "High_School_Introductory"
    HIGH_SCHOOL_ADVANCED = "High_School_Advanced"
    UNDERGRADUATE_INTRO = "Undergraduate_Introductory"
    UNDERGRADUATE_INTERMEDIATE = "Undergraduate_Intermediate"
    UNDERGRADUATE_ADVANCED = "Undergraduate_Advanced"
    GRADUATE_INTRO = "Graduate_Introductory"
    GRADUATE_ADVANCED = "Graduate_Advanced"
    RESEARCH_LEVEL = "Research_Level"


@dataclass
class DifficultyMetrics:
    """
    Goal: Comprehensive metrics for difficulty assessment.
    
    Contains all factors used in determining book difficulty levels
    with scientific validation and authority verification.
    """
    mathematical_complexity: float  # 0-1 scale
    conceptual_depth: float  # 0-1 scale  
    terminology_sophistication: float  # 0-1 scale
    prerequisite_requirements: float  # 0-1 scale
    cognitive_load: float  # 0-1 scale
    authority_validation_score: float  # 0-1 scale
    
    def calculate_composite_difficulty(self) -> float:
        """Calculate weighted composite difficulty score."""
        weights = {
            'mathematical': 0.25,
            'conceptual': 0.25,
            'terminology': 0.15,
            'prerequisites': 0.15,
            'cognitive': 0.10,
            'authority': 0.10
        }
        
        return (
            self.mathematical_complexity * weights['mathematical'] +
            self.conceptual_depth * weights['conceptual'] +
            self.terminology_sophistication * weights['terminology'] +
            self.prerequisite_requirements * weights['prerequisites'] +
            self.cognitive_load * weights['cognitive'] +
            self.authority_validation_score * weights['authority']
        )


@dataclass
class BookDifficultyRanking:
    """
    Goal: Complete difficulty ranking for a book with validation.
    
    Contains comprehensive difficulty assessment with supporting evidence
    and validation against educational standards.
    """
    book_title: str
    book_source: str
    difficulty_level: DifficultyLevel
    confidence_score: float  # 0-1 confidence in ranking
    difficulty_metrics: DifficultyMetrics
    supporting_evidence: List[str]
    validation_results: Dict[str, bool]
    prerequisite_books: List[str]
    follow_up_books: List[str]
    discipline_specific_rankings: Dict[str, DifficultyLevel]
    authority_sources_consulted: List[str]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            'book_title': self.book_title,
            'book_source': self.book_source,
            'difficulty_level': self.difficulty_level.value,
            'confidence_score': self.confidence_score,
            'difficulty_metrics': {
                'mathematical_complexity': self.difficulty_metrics.mathematical_complexity,
                'conceptual_depth': self.difficulty_metrics.conceptual_depth,
                'terminology_sophistication': self.difficulty_metrics.terminology_sophistication,
                'prerequisite_requirements': self.difficulty_metrics.prerequisite_requirements,
                'cognitive_load': self.difficulty_metrics.cognitive_load,
                'authority_validation_score': self.difficulty_metrics.authority_validation_score,
                'composite_score': self.difficulty_metrics.calculate_composite_difficulty()
            },
            'supporting_evidence': self.supporting_evidence,
            'validation_results': self.validation_results,
            'prerequisite_books': self.prerequisite_books,
            'follow_up_books': self.follow_up_books,
            'discipline_specific_rankings': {k: v.value for k, v in self.discipline_specific_rankings.items()},
            'authority_sources_consulted': self.authority_sources_consulted
        }


@dataclass
class ProgressionValidationResult:
    """
    Goal: Validation results for educational progression logic.
    
    Ensures that difficulty rankings follow proper educational sequences
    and maintain scientific consistency.
    """
    is_valid_progression: bool
    progression_issues: List[str]
    recommended_reorderings: List[Tuple[str, str]]  # (book1, book2) reordering suggestions
    gap_analysis: Dict[str, List[str]]  # Missing difficulty levels per discipline
    confidence_in_progression: float
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            'is_valid_progression': self.is_valid_progression,
            'progression_issues': self.progression_issues,
            'recommended_reorderings': self.recommended_reorderings,
            'gap_analysis': self.gap_analysis,
            'confidence_in_progression': self.confidence_in_progression
        }


class BookDifficultyRanker:
    """
    Goal: Rank books by difficulty with scientific validation.
    
    Provides comprehensive difficulty assessment with authority verification,
    educational progression validation, and discipline-specific rankings.
    """
    
    def __init__(self):
        self.mathematical_indicators = self._load_mathematical_indicators()
        self.conceptual_depth_indicators = self._load_conceptual_depth_indicators()
        self.terminology_sophistication_maps = self._load_terminology_sophistication()
        self.prerequisite_patterns = self._load_prerequisite_patterns()
        self.authority_difficulty_references = self._load_authority_references()
        self.discipline_specific_progressions = self._load_discipline_progressions()
        self.cognitive_load_factors = self._load_cognitive_load_factors()
        
    def rank_books_with_validation(self, book_list_data: Dict, toc_entries: List[TOCEntry],
                                 discipline_mappings: Dict) -> Tuple[List[BookDifficultyRanking], ProgressionValidationResult]:
        """
        Goal: Rank all books by difficulty with comprehensive validation.
        
        Analyzes book content and TOC structure to determine difficulty levels
        with scientific validation and educational progression verification.
        """
        logger.info(f"Starting difficulty ranking for {len(book_list_data)} books")
        
        # Step 1: Analyze each book for difficulty metrics
        book_rankings = []
        for book_key, book_info in book_list_data.items():
            if not isinstance(book_info, dict):
                continue
            
            # Get relevant TOC entries for this book
            book_toc = [toc for toc in toc_entries if toc.book_source == book_info.get('title', book_key)]
            
            # Calculate difficulty ranking
            ranking = self._calculate_book_difficulty_ranking(book_key, book_info, book_toc, discipline_mappings)
            if ranking:
                book_rankings.append(ranking)
        
        # Step 2: Validate progression logic
        progression_validation = self._validate_educational_progression(book_rankings, discipline_mappings)
        
        # Step 3: Apply corrections based on validation
        corrected_rankings = self._apply_progression_corrections(book_rankings, progression_validation)
        
        # Step 4: Final validation
        final_validation = self._validate_educational_progression(corrected_rankings, discipline_mappings)
        
        # Step 5: Sort by difficulty level
        sorted_rankings = self._sort_by_difficulty_level(corrected_rankings)
        
        logger.info(f"Difficulty ranking complete: {len(sorted_rankings)} books ranked, "
                   f"progression valid: {final_validation.is_valid_progression}")
        
        return sorted_rankings, final_validation
    
    def _calculate_book_difficulty_ranking(self, book_key: str, book_info: Dict, 
                                         book_toc: List[TOCEntry], discipline_mappings: Dict) -> Optional[BookDifficultyRanking]:
        """Calculate comprehensive difficulty ranking for a single book."""
        
        book_title = book_info.get('title', book_key)
        
        # Determine primary disciplines for this book
        primary_disciplines = self._determine_book_disciplines(book_title, discipline_mappings)
        if not primary_disciplines:
            logger.warning(f"No disciplines identified for book: {book_title}")
            return None
        
        # Calculate difficulty metrics
        metrics = self._calculate_difficulty_metrics(book_info, book_toc, primary_disciplines)
        
        # Determine overall difficulty level
        difficulty_level = self._determine_difficulty_level(metrics, primary_disciplines)
        
        # Calculate confidence score
        confidence_score = self._calculate_ranking_confidence(book_info, book_toc, metrics)
        
        # Generate supporting evidence
        supporting_evidence = self._generate_supporting_evidence(book_info, book_toc, metrics)
        
        # Perform validation checks
        validation_results = self._perform_ranking_validation(book_info, book_toc, difficulty_level, primary_disciplines)
        
        # Determine prerequisite and follow-up books
        prerequisite_books, follow_up_books = self._determine_book_sequence(book_title, difficulty_level, primary_disciplines)
        
        # Calculate discipline-specific rankings
        discipline_specific_rankings = self._calculate_discipline_specific_rankings(book_info, book_toc, primary_disciplines)
        
        # Identify authority sources consulted
        authority_sources = self._identify_consulted_authorities(primary_disciplines)
        
        return BookDifficultyRanking(
            book_title=book_title,
            book_source=book_info.get('source', 'Unknown'),
            difficulty_level=difficulty_level,
            confidence_score=confidence_score,
            difficulty_metrics=metrics,
            supporting_evidence=supporting_evidence,
            validation_results=validation_results,
            prerequisite_books=prerequisite_books,
            follow_up_books=follow_up_books,
            discipline_specific_rankings=discipline_specific_rankings,
            authority_sources_consulted=authority_sources
        )
    
    def _calculate_difficulty_metrics(self, book_info: Dict, book_toc: List[TOCEntry], 
                                    disciplines: List[str]) -> DifficultyMetrics:
        """Calculate comprehensive difficulty metrics for a book."""
        
        # Combine all text for analysis
        full_text = self._combine_book_text(book_info, book_toc)
        
        # Calculate each metric
        mathematical_complexity = self._assess_mathematical_complexity(full_text, disciplines)
        conceptual_depth = self._assess_conceptual_depth(full_text, book_toc, disciplines)
        terminology_sophistication = self._assess_terminology_sophistication(full_text, disciplines)
        prerequisite_requirements = self._assess_prerequisite_requirements(book_info, book_toc, disciplines)
        cognitive_load = self._assess_cognitive_load(full_text, book_toc, disciplines)
        authority_validation = self._assess_authority_validation(book_info, disciplines)
        
        return DifficultyMetrics(
            mathematical_complexity=mathematical_complexity,
            conceptual_depth=conceptual_depth,
            terminology_sophistication=terminology_sophistication,
            prerequisite_requirements=prerequisite_requirements,
            cognitive_load=cognitive_load,
            authority_validation_score=authority_validation
        )
    
    def _assess_mathematical_complexity(self, text: str, disciplines: List[str]) -> float:
        """Assess mathematical complexity level of the book content."""
        complexity_score = 0.0
        text_lower = text.lower()
        
        for discipline in disciplines:
            if discipline not in self.mathematical_indicators:
                continue
                
            indicators = self.mathematical_indicators[discipline]
            
            # Check for mathematical concepts by complexity level
            for level, concepts in indicators.items():
                level_weight = {
                    'basic': 0.1,
                    'intermediate': 0.3,
                    'advanced': 0.6,
                    'graduate': 0.9
                }.get(level, 0.5)
                
                for concept in concepts:
                    if concept.lower() in text_lower:
                        complexity_score += level_weight * 0.1  # Each match adds weighted score
        
        # Normalize by number of disciplines
        if disciplines:
            complexity_score /= len(disciplines)
        
        # Look for mathematical notation patterns
        notation_patterns = [
            r'\\$[^$]+\\$',  # LaTeX math
            r'\\\\[^\\\\]+\\\\',  # Double backslash math
            r'\\b\\d+\\^\\d+\\b',  # Exponents
            r'\\b(d/d[xyz])\\b',  # Derivatives
            r'\\b(integral|summation|∑|∫)\\b',  # Advanced math symbols
            r'\\b(matrix|vector|tensor)\\b'  # Linear algebra
        ]
        
        notation_count = 0
        for pattern in notation_patterns:
            notation_count += len(re.findall(pattern, text))
        
        # Add notation complexity (up to 0.3 additional score)
        notation_score = min(0.3, notation_count * 0.02)
        complexity_score += notation_score
        
        return min(1.0, complexity_score)
    
    def _assess_conceptual_depth(self, text: str, book_toc: List[TOCEntry], disciplines: List[str]) -> float:
        """Assess conceptual depth based on content structure and terminology."""
        depth_score = 0.0
        text_lower = text.lower()
        
        # Analyze TOC structure for depth indicators
        if book_toc:
            # Hierarchical depth
            max_level = max(toc.level for toc in book_toc) if book_toc else 1
            depth_score += min(0.3, max_level * 0.1)
            
            # Specialized chapters
            specialized_count = 0
            for toc in book_toc:
                if any(indicator in toc.title.lower() for indicator in 
                      ['advanced', 'specialized', 'research', 'current', 'cutting-edge']):
                    specialized_count += 1
            
            specialization_ratio = specialized_count / len(book_toc)
            depth_score += specialization_ratio * 0.2
        
        # Check for discipline-specific depth indicators
        for discipline in disciplines:
            if discipline not in self.conceptual_depth_indicators:
                continue
                
            indicators = self.conceptual_depth_indicators[discipline]
            
            for depth_level, concepts in indicators.items():
                level_weight = {
                    'surface': 0.1,
                    'intermediate': 0.4,
                    'deep': 0.8,
                    'expert': 1.0
                }.get(depth_level, 0.5)
                
                concept_matches = sum(1 for concept in concepts if concept.lower() in text_lower)
                depth_score += concept_matches * level_weight * 0.05
        
        # Abstract thinking indicators
        abstract_indicators = [
            'theoretical framework', 'conceptual model', 'paradigm', 'methodology',
            'philosophical implications', 'epistemology', 'ontology', 'meta-analysis'
        ]
        
        abstract_count = sum(1 for indicator in abstract_indicators if indicator in text_lower)
        depth_score += min(0.2, abstract_count * 0.05)
        
        return min(1.0, depth_score)
    
    def _assess_terminology_sophistication(self, text: str, disciplines: List[str]) -> float:
        """Assess sophistication of scientific terminology used."""
        sophistication_score = 0.0
        text_lower = text.lower()
        
        for discipline in disciplines:
            if discipline not in self.terminology_sophistication_maps:
                continue
                
            terminology_map = self.terminology_sophistication_maps[discipline]
            
            for sophistication_level, terms in terminology_map.items():
                level_weight = {
                    'introductory': 0.2,
                    'intermediate': 0.5,
                    'advanced': 0.8,
                    'professional': 1.0
                }.get(sophistication_level, 0.5)
                
                term_matches = sum(1 for term in terms if term.lower() in text_lower)
                sophistication_score += term_matches * level_weight * 0.02
        
        # Check for technical jargon density
        total_words = len(text.split())
        technical_words = 0
        
        # Combined technical terms from all disciplines
        all_technical_terms = set()
        for discipline in disciplines:
            if discipline in self.terminology_sophistication_maps:
                for terms in self.terminology_sophistication_maps[discipline].values():
                    all_technical_terms.update(term.lower() for term in terms)
        
        for word in text.lower().split():
            if word in all_technical_terms:
                technical_words += 1
        
        if total_words > 0:
            jargon_density = technical_words / total_words
            sophistication_score += min(0.3, jargon_density * 2)  # Cap at 0.3
        
        return min(1.0, sophistication_score)
    
    def _assess_prerequisite_requirements(self, book_info: Dict, book_toc: List[TOCEntry], 
                                        disciplines: List[str]) -> float:
        """Assess prerequisite knowledge requirements."""
        prerequisite_score = 0.0
        
        # Analyze title and description for prerequisite indicators
        text = f"{book_info.get('title', '')} {book_info.get('description', '')}".lower()
        
        # Explicit prerequisite mentions
        prerequisite_patterns = [
            r'prerequisite', r'requires?.*knowledge', r'assumes?.*familiarity',
            r'building.*on', r'continuation.*of', r'advanced.*course'
        ]
        
        for pattern in prerequisite_patterns:
            if re.search(pattern, text):
                prerequisite_score += 0.2
        
        # Level indicators in title
        level_indicators = {
            'elementary': 0.1, 'basic': 0.1, 'introduction': 0.2,
            'intermediate': 0.4, 'advanced': 0.7, 'graduate': 0.9,
            'research': 1.0, 'professional': 0.8
        }
        
        for indicator, score in level_indicators.items():
            if indicator in text:
                prerequisite_score = max(prerequisite_score, score)
        
        # Check for discipline-specific prerequisite patterns
        for discipline in disciplines:
            if discipline not in self.prerequisite_patterns:
                continue
                
            patterns = self.prerequisite_patterns[discipline]
            for pattern_info in patterns:
                if pattern_info['pattern'].lower() in text:
                    prerequisite_score += pattern_info['weight']
        
        # TOC analysis for prerequisite complexity
        if book_toc:
            # Check for chapters that indicate prerequisite knowledge
            prereq_chapters = 0
            for toc in book_toc:
                if any(term in toc.title.lower() for term in 
                      ['review', 'background', 'foundation', 'prerequisite']):
                    prereq_chapters += 1
            
            # If few review chapters, assumes more prerequisite knowledge
            if len(book_toc) > 0:
                review_ratio = prereq_chapters / len(book_toc)
                prerequisite_score += (1 - review_ratio) * 0.3
        
        return min(1.0, prerequisite_score)
    
    def _assess_cognitive_load(self, text: str, book_toc: List[TOCEntry], disciplines: List[str]) -> float:
        """Assess cognitive complexity and mental effort required."""
        cognitive_score = 0.0
        
        # Text complexity analysis
        sentences = text.split('.')
        if sentences:
            avg_sentence_length = sum(len(sentence.split()) for sentence in sentences) / len(sentences)
            # Longer sentences typically indicate higher cognitive load
            cognitive_score += min(0.3, (avg_sentence_length - 10) * 0.02)
        
        # Vocabulary complexity
        words = text.lower().split()
        if words:
            # Count multi-syllable words (approximate)
            complex_words = sum(1 for word in words if len(word) > 8)
            complexity_ratio = complex_words / len(words)
            cognitive_score += complexity_ratio * 0.5
        
        # Concept density in TOC
        if book_toc:
            total_concepts = 0
            for toc in book_toc:
                # Count potential concepts per chapter
                concept_indicators = len(getattr(toc, 'keywords', [])) if getattr(toc, 'keywords', []) else len(toc.title.split())
                total_concepts += concept_indicators
            
            avg_concepts_per_chapter = total_concepts / len(book_toc)
            cognitive_score += min(0.2, avg_concepts_per_chapter * 0.02)
        
        # Discipline-specific cognitive load factors
        for discipline in disciplines:
            if discipline in self.cognitive_load_factors:
                factors = self.cognitive_load_factors[discipline]
                
                for factor, weight in factors.items():
                    if factor.lower() in text.lower():
                        cognitive_score += weight * 0.1
        
        return min(1.0, cognitive_score)
    
    def _assess_authority_validation(self, book_info: Dict, disciplines: List[str]) -> float:
        """Assess validation against authority sources and standards."""
        validation_score = 0.0
        
        # Check book metadata for authority indicators
        title = book_info.get('title', '').lower()
        description = book_info.get('description', '').lower()
        author = book_info.get('author', '').lower()
        publisher = book_info.get('publisher', '').lower()
        
        # Authority publisher indicators
        authority_publishers = [
            'cambridge', 'oxford', 'mit', 'harvard', 'princeton', 'stanford',
            'wiley', 'springer', 'elsevier', 'pearson', 'mcgraw-hill'
        ]
        
        for pub in authority_publishers:
            if pub in publisher:
                validation_score += 0.3
                break
        
        # Academic institution indicators
        academic_indicators = [
            'university', 'college', 'institute', 'academy', 'school'
        ]
        
        if any(indicator in publisher for indicator in academic_indicators):
            validation_score += 0.2
        
        # Check against known authority references
        for discipline in disciplines:
            if discipline in self.authority_difficulty_references:
                references = self.authority_difficulty_references[discipline]
                
                # Check if book matches known difficulty standards
                for ref_level, ref_books in references.items():
                    if any(ref_book.lower() in title for ref_book in ref_books):
                        validation_score += 0.4
                        break
        
        # Professional recognition indicators
        recognition_indicators = [
            'standard', 'official', 'recommended', 'certified', 'approved',
            'curriculum', 'textbook', 'handbook', 'reference'
        ]
        
        recognition_count = sum(1 for indicator in recognition_indicators 
                              if indicator in title or indicator in description)
        validation_score += min(0.3, recognition_count * 0.1)
        
        return min(1.0, validation_score)
    
    def _determine_difficulty_level(self, metrics: DifficultyMetrics, disciplines: List[str]) -> DifficultyLevel:
        """Determine overall difficulty level from metrics."""
        composite_score = metrics.calculate_composite_difficulty()
        
        # Standard thresholds
        if composite_score < 0.15:
            return DifficultyLevel.ELEMENTARY
        elif composite_score < 0.25:
            return DifficultyLevel.HIGH_SCHOOL_INTRO
        elif composite_score < 0.35:
            return DifficultyLevel.HIGH_SCHOOL_ADVANCED
        elif composite_score < 0.45:
            return DifficultyLevel.UNDERGRADUATE_INTRO
        elif composite_score < 0.60:
            return DifficultyLevel.UNDERGRADUATE_INTERMEDIATE
        elif composite_score < 0.75:
            return DifficultyLevel.UNDERGRADUATE_ADVANCED
        elif composite_score < 0.85:
            return DifficultyLevel.GRADUATE_INTRO
        elif composite_score < 0.95:
            return DifficultyLevel.GRADUATE_ADVANCED
        else:
            return DifficultyLevel.RESEARCH_LEVEL
    
    def _calculate_ranking_confidence(self, book_info: Dict, book_toc: List[TOCEntry], 
                                    metrics: DifficultyMetrics) -> float:
        """Calculate confidence in the difficulty ranking."""
        confidence_factors = []
        
        # Data completeness
        completeness_score = 0.0
        if book_info.get('title'):
            completeness_score += 0.2
        if book_info.get('description'):
            completeness_score += 0.3
        if book_toc:
            completeness_score += 0.3
        if book_info.get('author'):
            completeness_score += 0.1
        if book_info.get('publisher'):
            completeness_score += 0.1
        
        confidence_factors.append(completeness_score)
        
        # Authority validation strength
        confidence_factors.append(metrics.authority_validation_score)
        
        # Consistency across metrics
        metric_values = [
            metrics.mathematical_complexity,
            metrics.conceptual_depth,
            metrics.terminology_sophistication,
            metrics.prerequisite_requirements,
            metrics.cognitive_load
        ]
        
        # Lower variance means higher confidence
        if len(metric_values) > 1:
            mean_val = sum(metric_values) / len(metric_values)
            variance = sum((val - mean_val) ** 2 for val in metric_values) / len(metric_values)
            consistency_score = max(0.0, 1.0 - variance * 2)  # Higher variance = lower confidence
            confidence_factors.append(consistency_score)
        
        # Overall confidence is average of factors
        return sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.5
    
    def _generate_supporting_evidence(self, book_info: Dict, book_toc: List[TOCEntry], 
                                    metrics: DifficultyMetrics) -> List[str]:
        """Generate human-readable supporting evidence for the ranking."""
        evidence = []
        
        # Mathematical complexity evidence
        if metrics.mathematical_complexity > 0.6:
            evidence.append("High mathematical complexity with advanced mathematical concepts")
        elif metrics.mathematical_complexity > 0.3:
            evidence.append("Moderate mathematical requirements")
        else:
            evidence.append("Minimal mathematical prerequisites")
        
        # Conceptual depth evidence
        if metrics.conceptual_depth > 0.7:
            evidence.append("Deep conceptual treatment with advanced theoretical frameworks")
        elif metrics.conceptual_depth > 0.4:
            evidence.append("Intermediate conceptual depth")
        else:
            evidence.append("Surface-level conceptual coverage")
        
        # Terminology evidence
        if metrics.terminology_sophistication > 0.7:
            evidence.append("Sophisticated professional terminology throughout")
        elif metrics.terminology_sophistication > 0.4:
            evidence.append("Standard academic terminology")
        else:
            evidence.append("Basic terminology appropriate for beginners")
        
        # Prerequisites evidence
        if metrics.prerequisite_requirements > 0.6:
            evidence.append("Substantial prerequisite knowledge required")
        elif metrics.prerequisite_requirements > 0.3:
            evidence.append("Some background knowledge helpful")
        else:
            evidence.append("Suitable for beginners with minimal prerequisites")
        
        # TOC structure evidence
        if book_toc:
            max_level = max(toc.level for toc in book_toc)
            if max_level > 3:
                evidence.append(f"Complex hierarchical structure ({max_level} levels)")
            
            specialized_chapters = sum(1 for toc in book_toc 
                                     if any(term in toc.title.lower() for term in 
                                           ['advanced', 'research', 'specialized']))
            if specialized_chapters > 0:
                evidence.append(f"Contains {specialized_chapters} specialized/advanced chapters")
        
        return evidence
    
    def _perform_ranking_validation(self, book_info: Dict, book_toc: List[TOCEntry], 
                                  difficulty_level: DifficultyLevel, disciplines: List[str]) -> Dict[str, bool]:
        """Perform validation checks on the difficulty ranking."""
        validation_results = {}
        
        # Title-level consistency check
        title = book_info.get('title', '').lower()
        title_indicators = {
            'introduction': [DifficultyLevel.HIGH_SCHOOL_INTRO, DifficultyLevel.UNDERGRADUATE_INTRO],
            'advanced': [DifficultyLevel.UNDERGRADUATE_ADVANCED, DifficultyLevel.GRADUATE_INTRO, DifficultyLevel.GRADUATE_ADVANCED],
            'graduate': [DifficultyLevel.GRADUATE_INTRO, DifficultyLevel.GRADUATE_ADVANCED],
            'research': [DifficultyLevel.RESEARCH_LEVEL]
        }
        
        title_consistent = True
        for indicator, expected_levels in title_indicators.items():
            if indicator in title and difficulty_level not in expected_levels:
                title_consistent = False
                break
        
        validation_results['title_consistency'] = title_consistent
        
        # Discipline-specific validation
        for discipline in disciplines:
            if discipline in self.discipline_specific_progressions:
                progression = self.discipline_specific_progressions[discipline]
                expected_order = progression.get('standard_order', [])
                
                # Check if difficulty level fits expected progression
                level_index = list(DifficultyLevel).index(difficulty_level)
                validation_results[f'{discipline}_progression_valid'] = True  # Simplified validation
        
        # Authority source validation
        has_authority_validation = book_info.get('publisher', '').lower() in [
            'cambridge', 'oxford', 'mit', 'harvard', 'princeton', 'wiley', 'springer'
        ]
        validation_results['authority_validated'] = has_authority_validation
        
        return validation_results
    
    def _determine_book_sequence(self, book_title: str, difficulty_level: DifficultyLevel, 
                               disciplines: List[str]) -> Tuple[List[str], List[str]]:
        """Determine prerequisite and follow-up books."""
        prerequisite_books = []
        follow_up_books = []
        
        # This would be enhanced with actual book relationship data
        # For now, providing template structure
        
        level_order = list(DifficultyLevel)
        current_index = level_order.index(difficulty_level)
        
        # General prerequisite suggestions based on level
        if current_index > 0:
            prerequisite_books.append(f"Books at {level_order[current_index-1].value} level")
        
        # General follow-up suggestions based on level  
        if current_index < len(level_order) - 1:
            follow_up_books.append(f"Books at {level_order[current_index+1].value} level")
        
        return prerequisite_books, follow_up_books
    
    def _calculate_discipline_specific_rankings(self, book_info: Dict, book_toc: List[TOCEntry], 
                                              disciplines: List[str]) -> Dict[str, DifficultyLevel]:
        """Calculate discipline-specific difficulty rankings."""
        discipline_rankings = {}
        
        for discipline in disciplines:
            # Calculate discipline-specific metrics
            discipline_text = self._extract_discipline_specific_content(book_info, book_toc, discipline)
            discipline_metrics = self._calculate_discipline_specific_metrics(discipline_text, discipline)
            discipline_level = self._determine_difficulty_level(discipline_metrics, [discipline])
            
            discipline_rankings[discipline] = discipline_level
        
        return discipline_rankings
    
    def _validate_educational_progression(self, rankings: List[BookDifficultyRanking], 
                                        discipline_mappings: Dict) -> ProgressionValidationResult:
        """Validate the educational progression logic across all ranked books."""
        progression_issues = []
        recommended_reorderings = []
        gap_analysis = defaultdict(list)
        
        # Group books by discipline
        books_by_discipline = defaultdict(list)
        for ranking in rankings:
            for discipline in ranking.discipline_specific_rankings.keys():
                books_by_discipline[discipline].append(ranking)
        
        # Validate progression within each discipline
        for discipline, discipline_books in books_by_discipline.items():
            # Sort by difficulty level
            sorted_books = sorted(discipline_books, 
                                key=lambda x: list(DifficultyLevel).index(x.difficulty_level))
            
            # Check for logical progression
            prev_level = None
            for book in sorted_books:
                current_level = book.difficulty_level
                
                if prev_level and list(DifficultyLevel).index(current_level) < list(DifficultyLevel).index(prev_level):
                    progression_issues.append(
                        f"Progression issue in {discipline}: {book.book_title} ({current_level.value}) "
                        f"appears after higher-level content"
                    )
                
                prev_level = current_level
            
            # Check for gaps in progression
            represented_levels = set(book.difficulty_level for book in discipline_books)
            all_levels = set(DifficultyLevel)
            missing_levels = all_levels - represented_levels
            
            if missing_levels:
                gap_analysis[discipline] = [level.value for level in missing_levels]
        
        # Calculate overall confidence
        total_books = len(rankings)
        books_with_issues = len(set(issue.split(':')[1].split('(')[0].strip() 
                                  for issue in progression_issues))
        
        confidence = max(0.0, 1.0 - (books_with_issues / total_books)) if total_books > 0 else 0.0
        
        is_valid = len(progression_issues) == 0
        
        return ProgressionValidationResult(
            is_valid_progression=is_valid,
            progression_issues=progression_issues,
            recommended_reorderings=recommended_reorderings,
            gap_analysis=dict(gap_analysis),
            confidence_in_progression=confidence
        )
    
    def _apply_progression_corrections(self, rankings: List[BookDifficultyRanking], 
                                     validation: ProgressionValidationResult) -> List[BookDifficultyRanking]:
        """Apply corrections based on progression validation results."""
        corrected_rankings = rankings.copy()
        
        # Apply recommended reorderings
        for book1_title, book2_title in validation.recommended_reorderings:
            # Find and swap rankings (simplified implementation)
            book1_idx = next((i for i, r in enumerate(corrected_rankings) 
                            if r.book_title == book1_title), None)
            book2_idx = next((i for i, r in enumerate(corrected_rankings) 
                            if r.book_title == book2_title), None)
            
            if book1_idx is not None and book2_idx is not None:
                # Swap difficulty levels
                temp_level = corrected_rankings[book1_idx].difficulty_level
                corrected_rankings[book1_idx].difficulty_level = corrected_rankings[book2_idx].difficulty_level
                corrected_rankings[book2_idx].difficulty_level = temp_level
        
        return corrected_rankings
    
    def _sort_by_difficulty_level(self, rankings: List[BookDifficultyRanking]) -> List[BookDifficultyRanking]:
        """Sort books by difficulty level."""
        return sorted(rankings, key=lambda x: list(DifficultyLevel).index(x.difficulty_level))
    
    def get_ranking_report(self, rankings: List[BookDifficultyRanking], 
                         validation: ProgressionValidationResult) -> Dict:
        """Generate comprehensive ranking report."""
        # Calculate distribution statistics
        level_distribution = Counter(ranking.difficulty_level for ranking in rankings)
        confidence_scores = [ranking.confidence_score for ranking in rankings]
        
        return {
            'total_books_ranked': len(rankings),
            'difficulty_level_distribution': {level.value: count for level, count in level_distribution.items()},
            'average_confidence': sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0,
            'progression_validation': validation.to_dict(),
            'ranking_quality_metrics': {
                'high_confidence_books': len([r for r in rankings if r.confidence_score >= 0.8]),
                'medium_confidence_books': len([r for r in rankings if 0.6 <= r.confidence_score < 0.8]),
                'low_confidence_books': len([r for r in rankings if r.confidence_score < 0.6])
            },
            'authority_validation_coverage': len([r for r in rankings if r.difficulty_metrics.authority_validation_score >= 0.7]) / len(rankings) if rankings else 0
        }
    
    # Helper methods and data loading
    def _combine_book_text(self, book_info: Dict, book_toc: List[TOCEntry]) -> str:
        """Combine all available text from book for analysis."""
        text_parts = []
        
        if book_info.get('title'):
            text_parts.append(book_info['title'])
        if book_info.get('description'):
            text_parts.append(book_info['description'])
        
        for toc in book_toc:
            text_parts.append(toc.title)
            if getattr(toc, 'description', ''):
                text_parts.append(getattr(toc, 'description', ''))
        
        return ' '.join(text_parts)
    
    def _determine_book_disciplines(self, book_title: str, discipline_mappings: Dict) -> List[str]:
        """Determine disciplines for a book from mappings."""
        title_lower = book_title.lower()
        
        # Check discipline mappings
        for mapping in discipline_mappings.values():
            if hasattr(mapping, 'book_title') and mapping.book_title.lower() == title_lower:
                disciplines = [mapping.primary_discipline]
                disciplines.extend(mapping.secondary_disciplines)
                return disciplines[:3]  # Limit to 3 disciplines
        
        # Fallback keyword matching
        discipline_keywords = {
            'Physics': ['physics', 'mechanics', 'quantum', 'relativity'],
            'Chemistry': ['chemistry', 'chemical', 'molecular'],
            'Biology': ['biology', 'biological', 'life', 'cell'],
            'Mathematics': ['mathematics', 'calculus', 'algebra']
        }
        
        found_disciplines = []
        for discipline, keywords in discipline_keywords.items():
            if any(keyword in title_lower for keyword in keywords):
                found_disciplines.append(discipline)
        
        return found_disciplines[:2]  # Limit to 2 disciplines
    
    def _extract_discipline_specific_content(self, book_info: Dict, book_toc: List[TOCEntry], 
                                           discipline: str) -> str:
        """Extract content most relevant to a specific discipline."""
        # This would be enhanced with more sophisticated content extraction
        return self._combine_book_text(book_info, book_toc)
    
    def _calculate_discipline_specific_metrics(self, text: str, discipline: str) -> DifficultyMetrics:
        """Calculate metrics specific to one discipline."""
        # Simplified version - in practice would use discipline-specific weights
        return DifficultyMetrics(
            mathematical_complexity=self._assess_mathematical_complexity(text, [discipline]),
            conceptual_depth=self._assess_conceptual_depth(text, [], [discipline]),
            terminology_sophistication=self._assess_terminology_sophistication(text, [discipline]),
            prerequisite_requirements=0.5,  # Would need discipline-specific calculation
            cognitive_load=0.5,  # Would need discipline-specific calculation
            authority_validation_score=0.7  # Would check discipline-specific authorities
        )
    
    def _identify_consulted_authorities(self, disciplines: List[str]) -> List[str]:
        """Identify authority sources consulted for validation."""
        authorities = []
        
        authority_mapping = {
            'Physics': ['NIST', 'AIP', 'Physical Review'],
            'Chemistry': ['IUPAC', 'ACS', 'Journal of the American Chemical Society'],
            'Biology': ['WHO', 'NIH', 'Nature'],
            'Mathematics': ['AMS', 'Mathematical Reviews']
        }
        
        for discipline in disciplines:
            if discipline in authority_mapping:
                authorities.extend(authority_mapping[discipline])
        
        return list(set(authorities))  # Remove duplicates
    
    def _load_mathematical_indicators(self) -> Dict[str, Dict[str, List[str]]]:
        """Load mathematical complexity indicators by discipline."""
        return {
            'Physics': {
                'basic': ['addition', 'subtraction', 'multiplication', 'division', 'algebra'],
                'intermediate': ['calculus', 'derivatives', 'integrals', 'differential equations'],
                'advanced': ['partial derivatives', 'vector calculus', 'tensor analysis'],
                'graduate': ['group theory', 'lie algebra', 'differential geometry', 'topology']
            },
            'Chemistry': {
                'basic': ['arithmetic', 'proportions', 'ratios', 'percentages'],
                'intermediate': ['logarithms', 'exponentials', 'basic calculus'],
                'advanced': ['thermodynamic functions', 'statistical mechanics'],
                'graduate': ['quantum mechanics', 'group theory', 'statistical thermodynamics']
            },
            'Biology': {
                'basic': ['arithmetic', 'percentages', 'graphs', 'statistics'],
                'intermediate': ['probability', 'basic statistics', 'modeling'],
                'advanced': ['bioinformatics', 'population genetics', 'systems biology'],
                'graduate': ['mathematical modeling', 'computational biology', 'stochastic processes']
            },
            'Mathematics': {
                'basic': ['arithmetic', 'basic algebra', 'geometry'],
                'intermediate': ['advanced algebra', 'trigonometry', 'precalculus'],
                'advanced': ['calculus', 'linear algebra', 'differential equations'],
                'graduate': ['real analysis', 'abstract algebra', 'topology', 'measure theory']
            }
        }
    
    def _load_conceptual_depth_indicators(self) -> Dict[str, Dict[str, List[str]]]:
        """Load conceptual depth indicators by discipline."""
        return {
            'Physics': {
                'surface': ['definitions', 'basic concepts', 'simple examples'],
                'intermediate': ['applications', 'problem solving', 'connections'],
                'deep': ['theoretical frameworks', 'fundamental principles', 'advanced applications'],
                'expert': ['cutting-edge research', 'theoretical developments', 'paradigm shifts']
            },
            'Chemistry': {
                'surface': ['chemical facts', 'nomenclature', 'basic reactions'],
                'intermediate': ['reaction mechanisms', 'molecular structure', 'thermodynamics'],
                'deep': ['theoretical chemistry', 'advanced synthesis', 'spectroscopy'],
                'expert': ['computational chemistry', 'materials design', 'nanotechnology']
            },
            'Biology': {
                'surface': ['biological facts', 'basic processes', 'classification'],
                'intermediate': ['physiological mechanisms', 'genetics', 'evolution'],
                'deep': ['molecular mechanisms', 'systems biology', 'biotechnology'],
                'expert': ['synthetic biology', 'genomics', 'personalized medicine']
            }
        }
    
    def _load_terminology_sophistication(self) -> Dict[str, Dict[str, List[str]]]:
        """Load terminology sophistication mappings."""
        return {
            'Physics': {
                'introductory': ['force', 'energy', 'motion', 'heat', 'light'],
                'intermediate': ['momentum', 'acceleration', 'electromagnetic', 'quantum'],
                'advanced': ['lagrangian', 'hamiltonian', 'gauge theory', 'symmetry'],
                'professional': ['renormalization', 'supersymmetry', 'string theory']
            },
            'Chemistry': {
                'introductory': ['atom', 'molecule', 'reaction', 'bond', 'element'],
                'intermediate': ['orbital', 'electronegativity', 'thermodynamics', 'kinetics'],
                'advanced': ['spectroscopy', 'crystallography', 'catalysis'],
                'professional': ['photochemistry', 'medicinal chemistry', 'computational chemistry']
            },
            'Biology': {
                'introductory': ['cell', 'organism', 'gene', 'protein', 'evolution'],
                'intermediate': ['metabolism', 'transcription', 'ecosystem', 'physiology'],
                'advanced': ['genomics', 'proteomics', 'bioinformatics', 'biotechnology'],
                'professional': ['systems biology', 'synthetic biology', 'personalized medicine']
            }
        }
    
    def _load_prerequisite_patterns(self) -> Dict[str, List[Dict[str, any]]]:
        """Load prerequisite requirement patterns."""
        return {
            'Physics': [
                {'pattern': 'advanced physics', 'weight': 0.8},
                {'pattern': 'graduate level', 'weight': 0.9},
                {'pattern': 'undergraduate physics', 'weight': 0.6},
                {'pattern': 'calculus required', 'weight': 0.5}
            ],
            'Chemistry': [
                {'pattern': 'organic chemistry', 'weight': 0.6},
                {'pattern': 'physical chemistry', 'weight': 0.7},
                {'pattern': 'graduate chemistry', 'weight': 0.9},
                {'pattern': 'general chemistry', 'weight': 0.3}
            ],
            'Biology': [
                {'pattern': 'molecular biology', 'weight': 0.6},
                {'pattern': 'advanced biology', 'weight': 0.7},
                {'pattern': 'graduate biology', 'weight': 0.9},
                {'pattern': 'general biology', 'weight': 0.3}
            ]
        }
    
    def _load_authority_references(self) -> Dict[str, Dict[str, List[str]]]:
        """Load authority difficulty reference standards."""
        return {
            'Physics': {
                'undergraduate_intro': ['University Physics', 'College Physics'],
                'undergraduate_advanced': ['Classical Mechanics', 'Electrodynamics'],
                'graduate': ['Quantum Mechanics', 'Statistical Mechanics'],
                'research': ['Advanced Quantum Mechanics', 'Field Theory']
            },
            'Chemistry': {
                'undergraduate_intro': ['General Chemistry', 'Chemistry: The Central Science'],
                'undergraduate_advanced': ['Organic Chemistry', 'Physical Chemistry'],
                'graduate': ['Advanced Organic Chemistry', 'Quantum Chemistry'],
                'research': ['Computational Chemistry', 'Materials Chemistry']
            },
            'Biology': {
                'undergraduate_intro': ['Campbell Biology', 'Biology: The Unity and Diversity'],
                'undergraduate_advanced': ['Molecular Biology', 'Cell Biology'],
                'graduate': ['Advanced Cell Biology', 'Systems Biology'],
                'research': ['Synthetic Biology', 'Computational Biology']
            }
        }
    
    def _load_discipline_progressions(self) -> Dict[str, Dict[str, List[DifficultyLevel]]]:
        """Load standard discipline progression orders."""
        return {
            'Physics': {
                'standard_order': [
                    DifficultyLevel.HIGH_SCHOOL_INTRO,
                    DifficultyLevel.HIGH_SCHOOL_ADVANCED,
                    DifficultyLevel.UNDERGRADUATE_INTRO,
                    DifficultyLevel.UNDERGRADUATE_INTERMEDIATE,
                    DifficultyLevel.UNDERGRADUATE_ADVANCED,
                    DifficultyLevel.GRADUATE_INTRO,
                    DifficultyLevel.GRADUATE_ADVANCED,
                    DifficultyLevel.RESEARCH_LEVEL
                ]
            },
            'Chemistry': {
                'standard_order': [
                    DifficultyLevel.HIGH_SCHOOL_INTRO,
                    DifficultyLevel.HIGH_SCHOOL_ADVANCED,
                    DifficultyLevel.UNDERGRADUATE_INTRO,
                    DifficultyLevel.UNDERGRADUATE_INTERMEDIATE,
                    DifficultyLevel.UNDERGRADUATE_ADVANCED,
                    DifficultyLevel.GRADUATE_INTRO,
                    DifficultyLevel.GRADUATE_ADVANCED,
                    DifficultyLevel.RESEARCH_LEVEL
                ]
            },
            'Biology': {
                'standard_order': [
                    DifficultyLevel.HIGH_SCHOOL_INTRO,
                    DifficultyLevel.HIGH_SCHOOL_ADVANCED,
                    DifficultyLevel.UNDERGRADUATE_INTRO,
                    DifficultyLevel.UNDERGRADUATE_INTERMEDIATE,
                    DifficultyLevel.UNDERGRADUATE_ADVANCED,
                    DifficultyLevel.GRADUATE_INTRO,
                    DifficultyLevel.GRADUATE_ADVANCED,
                    DifficultyLevel.RESEARCH_LEVEL
                ]
            }
        }
    
    def _load_cognitive_load_factors(self) -> Dict[str, Dict[str, float]]:
        """Load cognitive load assessment factors."""
        return {
            'Physics': {
                'mathematical derivation': 0.8,
                'theoretical framework': 0.7,
                'problem solving': 0.6,
                'conceptual understanding': 0.5,
                'experimental design': 0.4
            },
            'Chemistry': {
                'reaction mechanism': 0.7,
                'molecular modeling': 0.8,
                'spectroscopic analysis': 0.6,
                'synthetic strategy': 0.7,
                'thermodynamic analysis': 0.6
            },
            'Biology': {
                'systems analysis': 0.7,
                'molecular mechanism': 0.6,
                'evolutionary analysis': 0.5,
                'ecological modeling': 0.6,
                'experimental design': 0.5
            }
        }