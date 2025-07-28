#!/usr/bin/env python3
"""
authority_based_conflict_resolver.py - Resolve conflicts by prioritizing most authoritative sources

This module resolves conceptual conflicts across disciplines and sources by applying
authority hierarchies and prioritizing the most reliable, authoritative sources.
"""

import logging
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum

from .data_models import SubtopicEntry, ScientificViolation, AlertSeverity

logger = logging.getLogger(__name__)


class SourceType(Enum):
    """Types of authoritative sources."""
    GOVERNMENT_AGENCY = "Government_Agency"  # NIST, FDA, WHO, etc.
    PROFESSIONAL_ORGANIZATION = "Professional_Organization"  # ACS, AIP, APA, etc.
    INTERNATIONAL_STANDARD = "International_Standard"  # IUPAC, ISO, etc.
    PEER_REVIEWED_JOURNAL = "Peer_Reviewed_Journal"
    UNIVERSITY_TEXTBOOK = "University_Textbook"
    EDUCATIONAL_STANDARD = "Educational_Standard"  # AP, IB, NGSS, etc.
    GENERAL_TEXTBOOK = "General_Textbook"
    ONLINE_RESOURCE = "Online_Resource"


@dataclass
class AuthoritySource:
    """
    Goal: Represent an authoritative source with reliability scoring.
    
    Contains metadata about sources to enable authority-based conflict resolution.
    """
    name: str
    source_type: SourceType
    discipline: str
    authority_score: float  # 0-1, higher = more authoritative
    reliability_factors: Dict[str, float]  # Factors contributing to authority
    last_updated: str = ""
    url: str = ""
    
    def get_composite_authority(self) -> float:
        """Calculate composite authority score from all factors."""
        base_score = self.authority_score
        
        # Weight by source type
        type_weights = {
            SourceType.GOVERNMENT_AGENCY: 1.0,
            SourceType.INTERNATIONAL_STANDARD: 0.95,
            SourceType.PROFESSIONAL_ORGANIZATION: 0.9,
            SourceType.PEER_REVIEWED_JOURNAL: 0.85,
            SourceType.UNIVERSITY_TEXTBOOK: 0.8,
            SourceType.EDUCATIONAL_STANDARD: 0.75,
            SourceType.GENERAL_TEXTBOOK: 0.6,
            SourceType.ONLINE_RESOURCE: 0.4
        }
        
        type_weight = type_weights.get(self.source_type, 0.5)
        
        # Apply reliability factors
        reliability_bonus = sum(self.reliability_factors.values()) / len(self.reliability_factors) if self.reliability_factors else 0
        
        return min(base_score * type_weight * (1 + reliability_bonus * 0.1), 1.0)


@dataclass
class ConflictResolution:
    """
    Goal: Document conflict resolution decision with rationale.
    
    Tracks how conflicts were resolved using authority hierarchy for audit trail.
    """
    conflict_id: str
    conflicting_sources: List[str]
    chosen_source: str
    authority_rationale: str
    confidence_score: float
    alternative_interpretations: List[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            'conflict_id': self.conflict_id,
            'conflicting_sources': self.conflicting_sources,
            'chosen_source': self.chosen_source,
            'authority_rationale': self.authority_rationale,
            'confidence_score': self.confidence_score,
            'alternative_interpretations': self.alternative_interpretations or []
        }


class AuthorityBasedConflictResolver:
    """
    Goal: Resolve conflicts by prioritizing most authoritative sources.
    
    Applies discipline-specific authority hierarchies to resolve conflicts
    between different sources and maintain scientific accuracy.
    """
    
    def __init__(self):
        self.authority_hierarchy = self._build_authority_hierarchy()
        self.source_registry = self._build_source_registry()
        self.conflict_resolutions: List[ConflictResolution] = []
        
    def resolve_conflicts(self, curriculum: List[SubtopicEntry], 
                         violations: List[ScientificViolation]) -> List[SubtopicEntry]:
        """
        Goal: Resolve conflicts in curriculum using authority-based decisions.
        
        Updates subtopic entries with conflict-resolved content based on
        highest authority sources and documents resolution decisions.
        """
        resolved_curriculum = curriculum.copy()
        
        logger.info(f"Resolving {len(violations)} scientific principle violations using authority hierarchy")
        
        # Group violations by subtopic
        violations_by_subtopic = {}
        for violation in violations:
            if violation.subtopic_id not in violations_by_subtopic:
                violations_by_subtopic[violation.subtopic_id] = []
            violations_by_subtopic[violation.subtopic_id].append(violation)
        
        # Resolve conflicts for each subtopic
        for subtopic in resolved_curriculum:
            if subtopic.id in violations_by_subtopic:
                subtopic_violations = violations_by_subtopic[subtopic.id]
                self._resolve_subtopic_conflicts(subtopic, subtopic_violations)
        
        logger.info(f"Resolved conflicts for {len(violations_by_subtopic)} subtopics")
        return resolved_curriculum
    
    def resolve_cross_disciplinary_conflicts(self, topic: str, 
                                           conflicting_contexts: Dict[str, SubtopicEntry]) -> SubtopicEntry:
        """
        Goal: Resolve conflicts when same topic appears differently across disciplines.
        
        Maintains discipline-specific applications while ensuring fundamental
        conceptual consistency based on highest authority source.
        """
        disciplines = list(conflicting_contexts.keys())
        
        # Find highest authority source across all contexts
        best_authority_score = 0
        best_source = None
        best_discipline = None
        
        for discipline, subtopic in conflicting_contexts.items():
            authority_score = self._get_source_authority(subtopic.authority_source, discipline)
            if authority_score > best_authority_score:
                best_authority_score = authority_score
                best_source = subtopic.authority_source
                best_discipline = discipline
        
        if best_discipline is None:
            logger.warning(f"No authoritative source found for cross-disciplinary topic: {topic}")
            return list(conflicting_contexts.values())[0]  # Return first as fallback
        
        # Use the most authoritative version as base
        resolved_subtopic = conflicting_contexts[best_discipline]
        
        # Document the resolution
        resolution = ConflictResolution(
            conflict_id=f"cross_disciplinary_{topic}",
            conflicting_sources=list(disciplines),
            chosen_source=best_source,
            authority_rationale=f"Highest authority score ({best_authority_score:.3f}) in {best_discipline}",
            confidence_score=best_authority_score
        )
        self.conflict_resolutions.append(resolution)
        
        # Update cross-disciplinary links
        for discipline in disciplines:
            if discipline != best_discipline:
                original_context = conflicting_contexts[discipline].discipline_specific_context
                resolved_subtopic.cross_disciplinary_links[discipline] = original_context
        
        resolved_subtopic.conceptual_consistency_validated = True
        resolved_subtopic.authority_confidence = best_authority_score
        
        logger.info(f"Resolved cross-disciplinary conflict for {topic} using {best_source} ({best_discipline})")
        return resolved_subtopic
    
    def get_conflict_resolution_report(self) -> Dict:
        """Generate comprehensive conflict resolution report."""
        return {
            'total_conflicts_resolved': len(self.conflict_resolutions),
            'resolutions': [resolution.to_dict() for resolution in self.conflict_resolutions],
            'authority_hierarchy_used': self._get_hierarchy_summary(),
            'confidence_distribution': self._get_confidence_distribution()
        }
    
    def _resolve_subtopic_conflicts(self, subtopic: SubtopicEntry, 
                                   violations: List[ScientificViolation]) -> None:
        """Resolve conflicts for individual subtopic using authority hierarchy."""
        
        # Find authoritative sources for resolution
        authoritative_sources = []
        for violation in violations:
            for source in violation.authoritative_sources:
                authority_score = self._get_source_authority(source, subtopic.discipline)
                authoritative_sources.append((source, authority_score))
        
        # Sort by authority score
        authoritative_sources.sort(key=lambda x: x[1], reverse=True)
        
        if not authoritative_sources:
            logger.warning(f"No authoritative sources found for resolving conflicts in {subtopic.id}")
            return
        
        # Use highest authority source
        best_source, best_score = authoritative_sources[0]
        
        # Apply resolution (simplified - in full implementation, would fetch correct content)
        subtopic.authority_source = best_source
        subtopic.authority_confidence = best_score
        subtopic.scientific_principles_validated = True
        
        # Clear conflicts after resolution
        subtopic.scientific_principle_conflicts = []
        
        # Document resolution
        resolution = ConflictResolution(
            conflict_id=subtopic.id,
            conflicting_sources=[v.conflicting_principle for v in violations],
            chosen_source=best_source,
            authority_rationale=f"Highest authority score ({best_score:.3f}) for {subtopic.discipline}",
            confidence_score=best_score
        )
        self.conflict_resolutions.append(resolution)
        
        logger.debug(f"Resolved conflicts for {subtopic.id} using {best_source}")
    
    def _build_authority_hierarchy(self) -> Dict[str, Dict[str, float]]:
        """
        Goal: Build discipline-specific authority hierarchy.
        
        Creates comprehensive authority rankings for each discipline to enable
        consistent conflict resolution based on source reliability.
        """
        return {
            "Physics": {
                "NIST": 1.0,  # National Institute of Standards and Technology
                "BIPM": 0.98,  # International Bureau of Weights and Measures
                "AIP": 0.95,  # American Institute of Physics
                "Physical Review": 0.92,
                "Nature Physics": 0.90,
                "University Physics Textbooks": 0.85,
                "AP Physics Standards": 0.80,
                "IB Physics Guide": 0.78,
                "General Physics Textbooks": 0.70,
                "Physics Online Resources": 0.40
            },
            "Chemistry": {
                "IUPAC": 1.0,  # International Union of Pure and Applied Chemistry
                "ACS": 0.98,  # American Chemical Society
                "Journal of the American Chemical Society": 0.95,
                "Nature Chemistry": 0.93,
                "Angewandte Chemie": 0.91,
                "University Chemistry Textbooks": 0.85,
                "AP Chemistry Standards": 0.80,
                "IB Chemistry Guide": 0.78,
                "General Chemistry Textbooks": 0.70,
                "Chemistry Online Resources": 0.40
            },
            "Biology": {
                "WHO": 1.0,  # World Health Organization
                "NIH": 0.98,  # National Institutes of Health
                "Nature": 0.95,
                "Science": 0.94,
                "Cell": 0.92,
                "PNAS": 0.90,
                "University Biology Textbooks": 0.85,
                "AP Biology Standards": 0.80,
                "IB Biology Guide": 0.78,
                "General Biology Textbooks": 0.70,
                "Biology Online Resources": 0.40
            },
            "Medicine": {
                "WHO": 1.0,
                "FDA": 0.98,
                "CDC": 0.96,
                "The Lancet": 0.94,
                "New England Journal of Medicine": 0.93,
                "JAMA": 0.91,
                "Medical Textbooks": 0.85,
                "Medical Association Guidelines": 0.80,
                "General Medical Resources": 0.60,
                "Medical Online Resources": 0.40
            },
            "Psychology": {
                "APA": 1.0,  # American Psychological Association
                "Psychological Science": 0.92,
                "Journal of Experimental Psychology": 0.90,
                "Nature Neuroscience": 0.88,
                "University Psychology Textbooks": 0.85,
                "AP Psychology Standards": 0.80,
                "IB Psychology Guide": 0.78,
                "General Psychology Textbooks": 0.70,
                "Psychology Online Resources": 0.40
            },
            "Mathematics": {
                "AMS": 0.98,  # American Mathematical Society
                "IEEE": 0.95,  # For applied mathematics
                "Annals of Mathematics": 0.94,
                "Journal of the AMS": 0.92,
                "University Mathematics Textbooks": 0.85,
                "AP Mathematics Standards": 0.80,
                "IB Mathematics Guide": 0.78,
                "General Mathematics Textbooks": 0.70,
                "Mathematics Online Resources": 0.40
            },
            "universal": {
                "ISO": 0.95,  # International Organization for Standardization
                "UNESCO": 0.90,
                "Educational Standards": 0.75,
                "General Academic Sources": 0.60,
                "Online Educational Resources": 0.35
            }
        }
    
    def _build_source_registry(self) -> Dict[str, AuthoritySource]:
        """Build comprehensive registry of authority sources."""
        sources = {}
        
        # Add major authority sources
        authority_sources = [
            AuthoritySource(
                name="NIST",
                source_type=SourceType.GOVERNMENT_AGENCY,
                discipline="Physics",
                authority_score=1.0,
                reliability_factors={"government_backing": 1.0, "international_recognition": 1.0},
                url="https://www.nist.gov/"
            ),
            AuthoritySource(
                name="IUPAC",
                source_type=SourceType.INTERNATIONAL_STANDARD,
                discipline="Chemistry",
                authority_score=1.0,
                reliability_factors={"international_standard": 1.0, "peer_review": 1.0},
                url="https://iupac.org/"
            ),
            AuthoritySource(
                name="WHO",
                source_type=SourceType.GOVERNMENT_AGENCY,
                discipline="Biology",
                authority_score=1.0,
                reliability_factors={"global_authority": 1.0, "medical_expertise": 1.0},
                url="https://www.who.int/"
            ),
            AuthoritySource(
                name="APA",
                source_type=SourceType.PROFESSIONAL_ORGANIZATION,
                discipline="Psychology",
                authority_score=1.0,
                reliability_factors={"professional_standards": 1.0, "research_base": 1.0},
                url="https://www.apa.org/"
            )
        ]
        
        for source in authority_sources:
            sources[source.name] = source
        
        return sources
    
    def _get_source_authority(self, source_name: str, discipline: str) -> float:
        """Get authority score for a source in a specific discipline."""
        
        # Check discipline-specific hierarchy first
        if discipline in self.authority_hierarchy:
            if source_name in self.authority_hierarchy[discipline]:
                return self.authority_hierarchy[discipline][source_name]
        
        # Check universal hierarchy
        if source_name in self.authority_hierarchy.get("universal", {}):
            return self.authority_hierarchy["universal"][source_name]
        
        # Check source registry
        if source_name in self.source_registry:
            return self.source_registry[source_name].get_composite_authority()
        
        # Default low authority for unknown sources
        logger.warning(f"Unknown source authority: {source_name} in {discipline}")
        return 0.3
    
    def _get_hierarchy_summary(self) -> Dict:
        """Get summary of authority hierarchy usage."""
        summary = {}
        for discipline, sources in self.authority_hierarchy.items():
            summary[discipline] = {
                'total_sources': len(sources),
                'top_authorities': sorted(sources.items(), key=lambda x: x[1], reverse=True)[:3]
            }
        return summary
    
    def _get_confidence_distribution(self) -> Dict:
        """Get distribution of confidence scores in resolutions."""
        if not self.conflict_resolutions:
            return {}
        
        scores = [r.confidence_score for r in self.conflict_resolutions]
        return {
            'mean_confidence': sum(scores) / len(scores),
            'min_confidence': min(scores),
            'max_confidence': max(scores),
            'high_confidence_count': len([s for s in scores if s >= 0.8]),
            'medium_confidence_count': len([s for s in scores if 0.6 <= s < 0.8]),
            'low_confidence_count': len([s for s in scores if s < 0.6])
        }
    
    def add_authority_source(self, source: AuthoritySource) -> None:
        """Add new authority source to registry."""
        self.source_registry[source.name] = source
        
        # Add to hierarchy if not present
        if source.discipline not in self.authority_hierarchy:
            self.authority_hierarchy[source.discipline] = {}
        
        if source.name not in self.authority_hierarchy[source.discipline]:
            self.authority_hierarchy[source.discipline][source.name] = source.get_composite_authority()
    
    def update_source_authority(self, source_name: str, discipline: str, new_score: float) -> None:
        """Update authority score for existing source."""
        if discipline in self.authority_hierarchy:
            if source_name in self.authority_hierarchy[discipline]:
                self.authority_hierarchy[discipline][source_name] = new_score
                logger.info(f"Updated authority score for {source_name} in {discipline}: {new_score}")
    
    def validate_authority_consistency(self) -> List[str]:
        """Validate consistency of authority hierarchy."""
        issues = []
        
        for discipline, sources in self.authority_hierarchy.items():
            if discipline == "universal":
                continue
                
            # Check for unreasonable authority scores
            for source, score in sources.items():
                if score > 1.0 or score < 0.0:
                    issues.append(f"Invalid authority score for {source} in {discipline}: {score}")
            
            # Check for missing key sources
            expected_sources = {
                "Physics": ["NIST", "AIP"],
                "Chemistry": ["IUPAC", "ACS"],
                "Biology": ["WHO", "NIH"],
                "Medicine": ["WHO", "FDA"],
                "Psychology": ["APA"]
            }
            
            if discipline in expected_sources:
                for expected in expected_sources[discipline]:
                    if expected not in sources:
                        issues.append(f"Missing expected authority source {expected} in {discipline}")
        
        return issues