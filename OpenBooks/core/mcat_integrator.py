#!/usr/bin/env python3
"""
mcat_integrator.py - Integrate MCAT requirements with subtopic contexts

This module ensures MCAT-relevant disciplines include appropriate medical education
context and alignment with MCAT content specifications at the subtopic level.
"""

import logging
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from collections import defaultdict

from .data_models import SubtopicEntry, EducationalLevel, BloomLevel, QuestionType

logger = logging.getLogger(__name__)


@dataclass
class MCATContentSpecification:
    """
    MCAT content specification with detailed requirements.
    """
    topic_category: str
    skill_level: str  # Foundational, Content, Scientific Reasoning
    content_description: str
    mcat_sections: List[str]  # Which MCAT sections test this
    prerequisite_concepts: List[str]
    typical_question_types: List[str]
    interdisciplinary_connections: List[str]
    
    def to_dict(self) -> Dict:
        return {
            'topic_category': self.topic_category,
            'skill_level': self.skill_level,
            'content_description': self.content_description,
            'mcat_sections': self.mcat_sections,
            'prerequisite_concepts': self.prerequisite_concepts,
            'typical_question_types': self.typical_question_types,
            'interdisciplinary_connections': self.interdisciplinary_connections
        }


@dataclass
class MCATEnhancedSubtopic:
    """
    Subtopic enhanced with MCAT-specific context and connections.
    """
    base_subtopic: SubtopicEntry
    mcat_relevance_score: float  # 0-1 scale
    mcat_content_specs: List[MCATContentSpecification]
    medical_applications: List[str]
    interdisciplinary_mcat_links: Dict[str, List[str]]  # Links to other MCAT disciplines
    clinical_contexts: List[str]
    typical_mcat_question_formats: List[str]
    
    def to_dict(self) -> Dict:
        return {
            'base_subtopic': self.base_subtopic.__dict__,
            'mcat_relevance_score': self.mcat_relevance_score,
            'mcat_content_specs': [spec.to_dict() for spec in self.mcat_content_specs],
            'medical_applications': self.medical_applications,
            'interdisciplinary_mcat_links': self.interdisciplinary_mcat_links,
            'clinical_contexts': self.clinical_contexts,
            'typical_mcat_question_formats': self.typical_mcat_question_formats
        }


class MCATIntegrator:
    """
    Integrate MCAT requirements with curriculum subtopics.
    
    Ensures MCAT-relevant disciplines (Physics, Chemistry, Biology, Psychology, 
    Sociology, Medicine) include appropriate medical education context.
    """
    
    def __init__(self):
        self.mcat_disciplines = {
            'Physics', 'Chemistry', 'Biology', 'Psychology', 'Sociology', 'Medicine'
        }
        self.mcat_content_specifications = self._load_mcat_content_specifications()
        self.medical_application_mappings = self._load_medical_application_mappings()
        self.interdisciplinary_mcat_connections = self._load_interdisciplinary_connections()
        self.clinical_context_templates = self._load_clinical_context_templates()
        
    def integrate_mcat_requirements(self, curriculum_by_discipline: Dict[str, List[SubtopicEntry]]) -> Dict[str, List[MCATEnhancedSubtopic]]:
        """
        Integrate MCAT requirements into relevant discipline curricula.
        
        Enhances subtopics with MCAT-specific context, medical applications,
        and interdisciplinary connections for medical education relevance.
        """
        logger.info("Starting MCAT integration for relevant disciplines")
        
        mcat_enhanced_curricula = {}
        
        for discipline, curriculum in curriculum_by_discipline.items():
            if discipline in self.mcat_disciplines:
                logger.info(f"Enhancing {discipline} curriculum with MCAT integration ({len(curriculum)} subtopics)")
                
                enhanced_subtopics = []
                for subtopic in curriculum:
                    enhanced_subtopic = self._enhance_subtopic_with_mcat(subtopic, discipline)
                    enhanced_subtopics.append(enhanced_subtopic)
                
                # Ensure comprehensive MCAT coverage
                enhanced_subtopics = self._ensure_comprehensive_mcat_coverage(enhanced_subtopics, discipline)
                
                # Add MCAT-specific ordering considerations
                enhanced_subtopics = self._apply_mcat_educational_ordering(enhanced_subtopics, discipline)
                
                mcat_enhanced_curricula[discipline] = enhanced_subtopics
                
                logger.info(f"{discipline}: {len(enhanced_subtopics)} subtopics enhanced with MCAT integration")
            else:
                # Convert non-MCAT disciplines to enhanced format for consistency
                enhanced_subtopics = [
                    MCATEnhancedSubtopic(
                        base_subtopic=subtopic,
                        mcat_relevance_score=0.0,
                        mcat_content_specs=[],
                        medical_applications=[],
                        interdisciplinary_mcat_links={},
                        clinical_contexts=[],
                        typical_mcat_question_formats=[]
                    ) for subtopic in curriculum
                ]
                mcat_enhanced_curricula[discipline] = enhanced_subtopics
        
        # Add interdisciplinary MCAT connections
        self._add_interdisciplinary_mcat_connections(mcat_enhanced_curricula)
        
        logger.info(f"MCAT integration complete for {len(mcat_enhanced_curricula)} disciplines")
        return mcat_enhanced_curricula
    
    def _enhance_subtopic_with_mcat(self, subtopic: SubtopicEntry, discipline: str) -> MCATEnhancedSubtopic:
        """Enhance individual subtopic with MCAT-specific context."""
        
        # Calculate MCAT relevance score
        mcat_relevance = self._calculate_mcat_relevance(subtopic, discipline)
        
        # Find matching MCAT content specifications
        matching_specs = self._find_matching_mcat_specs(subtopic, discipline)
        
        # Generate medical applications
        medical_applications = self._generate_medical_applications(subtopic, discipline)
        
        # Generate clinical contexts
        clinical_contexts = self._generate_clinical_contexts(subtopic, discipline)
        
        # Determine typical MCAT question formats
        question_formats = self._determine_mcat_question_formats(subtopic, discipline)
        
        # Find interdisciplinary MCAT links
        interdisciplinary_links = self._find_interdisciplinary_mcat_links(subtopic, discipline)
        
        return MCATEnhancedSubtopic(
            base_subtopic=subtopic,
            mcat_relevance_score=mcat_relevance,
            mcat_content_specs=matching_specs,
            medical_applications=medical_applications,
            interdisciplinary_mcat_links=interdisciplinary_links,
            clinical_contexts=clinical_contexts,
            typical_mcat_question_formats=question_formats
        )
    
    def _calculate_mcat_relevance(self, subtopic: SubtopicEntry, discipline: str) -> float:
        """Calculate how relevant a subtopic is to MCAT preparation."""
        relevance_score = 0.0
        
        subtopic_text = f"{subtopic.subtopic} {subtopic.discipline_specific_context}".lower()
        
        # Check against MCAT content specifications
        for spec in self.mcat_content_specifications.get(discipline, []):
            if any(keyword.lower() in subtopic_text for keyword in spec.content_description.split()):
                relevance_score += 0.3
        
        # Check medical application potential
        medical_keywords = [
            'medical', 'clinical', 'health', 'disease', 'therapy', 'diagnosis',
            'physiology', 'anatomy', 'pathology', 'pharmacology', 'metabolism'
        ]
        
        medical_matches = sum(1 for keyword in medical_keywords if keyword in subtopic_text)
        relevance_score += min(0.4, medical_matches * 0.1)
        
        # Check for prerequisite concepts commonly tested on MCAT
        mcat_prerequisite_concepts = self._get_mcat_prerequisite_concepts(discipline)
        prereq_matches = sum(1 for concept in mcat_prerequisite_concepts 
                           if concept.lower() in subtopic_text)
        relevance_score += min(0.3, prereq_matches * 0.1)
        
        # IMPORTANT: Advanced topics beyond MCAT scope (graduate level, research topics, 
        # specialized applications) receive a base relevance score to ensure they are
        # preserved in the curriculum even if not directly MCAT-relevant
        if subtopic.level in [EducationalLevel.GRAD_INTRO, EducationalLevel.GRAD_ADV]:
            relevance_score = max(relevance_score, 0.2)  # Ensure advanced topics are preserved
        
        return min(1.0, relevance_score)
    
    def _find_matching_mcat_specs(self, subtopic: SubtopicEntry, discipline: str) -> List[MCATContentSpecification]:
        """Find MCAT content specifications that match this subtopic."""
        matching_specs = []
        
        subtopic_text = f"{subtopic.subtopic} {subtopic.discipline_specific_context}".lower()
        
        for spec in self.mcat_content_specifications.get(discipline, []):
            # Check for keyword matches in content description
            spec_keywords = spec.content_description.lower().split()
            
            # Calculate overlap
            subtopic_words = set(subtopic_text.split())
            spec_words = set(spec_keywords)
            
            overlap = len(subtopic_words.intersection(spec_words))
            
            if overlap >= 2:  # Require at least 2 word overlap
                matching_specs.append(spec)
        
        return matching_specs
    
    def _generate_medical_applications(self, subtopic: SubtopicEntry, discipline: str) -> List[str]:
        """Generate medical applications for the subtopic."""
        applications = []
        
        application_mappings = self.medical_application_mappings.get(discipline, {})
        
        subtopic_lower = subtopic.subtopic.lower()
        
        # Direct mappings
        for topic_pattern, app_list in application_mappings.items():
            if topic_pattern.lower() in subtopic_lower:
                applications.extend(app_list)
        
        # Generic applications based on discipline
        generic_applications = {
            'Physics': [
                'Medical imaging and radiation therapy',
                'Biomechanics and prosthetics',
                'Medical device physics'
            ],
            'Chemistry': [
                'Drug design and pharmacokinetics',
                'Biochemical pathways and metabolism',
                'Diagnostic chemistry and biomarkers'
            ],
            'Biology': [
                'Disease mechanisms and pathophysiology',
                'Genetic disorders and gene therapy',
                'Immune system function and dysfunction'
            ],
            'Psychology': [
                'Mental health diagnosis and treatment',
                'Patient behavior and compliance',
                'Cognitive assessment and rehabilitation'
            ],
            'Sociology': [
                'Healthcare disparities and access',
                'Patient-provider communication',
                'Health policy and public health'
            ]
        }
        
        # Add generic applications if no specific ones found
        if not applications and discipline in generic_applications:
            applications.extend(generic_applications[discipline][:2])  # Add 2 generic applications
        
        return applications[:3]  # Limit to 3 applications
    
    def _generate_clinical_contexts(self, subtopic: SubtopicEntry, discipline: str) -> List[str]:
        """Generate clinical contexts for the subtopic."""
        contexts = []
        
        context_templates = self.clinical_context_templates.get(discipline, [])
        
        # Generate contexts based on templates
        for template in context_templates:
            if any(keyword.lower() in subtopic.subtopic.lower() 
                   for keyword in template.get('keywords', [])):
                context = template['context_template'].format(topic=subtopic.subtopic)
                contexts.append(context)
        
        return contexts[:2]  # Limit to 2 contexts
    
    def _determine_mcat_question_formats(self, subtopic: SubtopicEntry, discipline: str) -> List[str]:
        """Determine typical MCAT question formats for this subtopic."""
        formats = []
        
        # Question format mappings by discipline and content type
        format_mappings = {
            'Physics': {
                'calculation': ['Multiple choice calculations', 'Data interpretation'],
                'conceptual': ['Passage-based reasoning', 'Graph analysis'],
                'experimental': ['Experimental design', 'Data analysis']
            },
            'Chemistry': {
                'reaction': ['Mechanism analysis', 'Product prediction'],
                'structure': ['Structure-function relationships', 'Stereochemistry'],
                'thermodynamics': ['Energy calculations', 'Equilibrium analysis']
            },
            'Biology': {
                'molecular': ['Pathway analysis', 'Genetic crosses'],
                'cellular': ['Process diagrams', 'Function prediction'],
                'organismal': ['Physiological reasoning', 'System integration']
            },
            'Psychology': {
                'cognitive': ['Case study analysis', 'Theory application'],
                'social': ['Scenario-based reasoning', 'Research interpretation'],
                'developmental': ['Stage identification', 'Process explanation']
            }
        }
        
        discipline_formats = format_mappings.get(discipline, {})
        subtopic_lower = subtopic.subtopic.lower()
        
        # Match subtopic to question format categories
        for category, category_formats in discipline_formats.items():
            if category in subtopic_lower:
                formats.extend(category_formats)
        
        # Default formats if no specific matches
        if not formats:
            default_formats = [
                'Passage-based multiple choice',
                'Conceptual reasoning questions',
                'Application scenarios'
            ]
            formats.extend(default_formats[:2])
        
        return formats[:3]  # Limit to 3 formats
    
    def _find_interdisciplinary_mcat_links(self, subtopic: SubtopicEntry, discipline: str) -> Dict[str, List[str]]:
        """Find interdisciplinary MCAT connections for this subtopic."""
        links = {}
        
        connections = self.interdisciplinary_mcat_connections.get(discipline, {})
        
        subtopic_lower = subtopic.subtopic.lower()
        
        for other_discipline, connection_mappings in connections.items():
            discipline_links = []
            
            for topic_pattern, linked_topics in connection_mappings.items():
                if topic_pattern.lower() in subtopic_lower:
                    discipline_links.extend(linked_topics)
            
            if discipline_links:
                links[other_discipline] = discipline_links[:3]  # Limit to 3 links
        
        return links
    
    def _ensure_comprehensive_mcat_coverage(self, enhanced_subtopics: List[MCATEnhancedSubtopic], 
                                          discipline: str) -> List[MCATEnhancedSubtopic]:
        """Ensure comprehensive coverage of MCAT content specifications."""
        
        # Check which MCAT specs are covered
        covered_specs = set()
        for subtopic in enhanced_subtopics:
            for spec in subtopic.mcat_content_specs:
                covered_specs.add(spec.topic_category)
        
        # Find missing MCAT specs
        all_specs = set(spec.topic_category for spec in self.mcat_content_specifications.get(discipline, []))
        missing_specs = all_specs - covered_specs
        
        # Add subtopics for missing MCAT content
        for missing_spec_category in missing_specs:
            missing_spec = next((spec for spec in self.mcat_content_specifications.get(discipline, [])
                               if spec.topic_category == missing_spec_category), None)
            
            if missing_spec:
                # Create new subtopic for missing MCAT content
                new_subtopic = self._create_mcat_specific_subtopic(missing_spec, discipline)
                enhanced_new_subtopic = self._enhance_subtopic_with_mcat(new_subtopic, discipline)
                enhanced_subtopics.append(enhanced_new_subtopic)
                
                logger.info(f"Added MCAT-specific subtopic for {discipline}: {missing_spec_category}")
        
        return enhanced_subtopics
    
    def _create_mcat_specific_subtopic(self, mcat_spec: MCATContentSpecification, 
                                     discipline: str) -> SubtopicEntry:
        """Create a new subtopic specifically for MCAT content coverage."""
        from .data_models import create_subtopic_id
        
        return SubtopicEntry(
            id=create_subtopic_id(discipline, "MCAT", mcat_spec.topic_category),
            discipline=discipline,
            category="MCAT",
            subtopic=mcat_spec.topic_category,
            level=EducationalLevel.UG_ADV,  # MCAT is typically post-undergraduate
            bloom=BloomLevel.APPLY,
            standards_links=["MCAT"],
            prerequisites=mcat_spec.prerequisite_concepts,
            learning_objectives=[f"Master {mcat_spec.topic_category} for MCAT preparation"],
            textbook_references=[],
            question_types=[QuestionType.CONCEPTUAL],
            hierarchy_level=3,
            parent_topics=[],
            child_topics=[],
            discipline_specific_context=f"MCAT-focused coverage of {mcat_spec.content_description}",
            discipline_specific_learning_objectives=[
                f"Apply {mcat_spec.topic_category} concepts in medical contexts",
                f"Analyze {mcat_spec.topic_category} in interdisciplinary scenarios"
            ],
            discipline_specific_applications=[],
            discipline_specific_prerequisites=[],
            scientific_principles_validated=True,
            authority_source="MCAT Content Specifications",
            authority_confidence=0.9,
            scientific_principle_conflicts=[],
            cross_disciplinary_links={},
            conceptual_consistency_validated=True,
            common_misconceptions=[],
            key_equations=[],
            typical_examples=[],
            experimental_methods=[],
            mcat_relevance=True
        )
    
    def _apply_mcat_educational_ordering(self, enhanced_subtopics: List[MCATEnhancedSubtopic], 
                                       discipline: str) -> List[MCATEnhancedSubtopic]:
        """Apply MCAT-appropriate educational ordering."""
        
        # Sort by MCAT relevance and educational progression
        def mcat_ordering_key(subtopic):
            base = subtopic.base_subtopic
            
            # Primary sort: Educational level
            level_order = {
                EducationalLevel.HS_FOUND: 1,
                EducationalLevel.HS_ADV: 2,
                EducationalLevel.UG_INTRO: 3,
                EducationalLevel.UG_ADV: 4,
                EducationalLevel.GRAD_INTRO: 5,
                EducationalLevel.GRAD_ADV: 6
            }
            
            level_priority = level_order.get(base.level, 5)
            
            # Secondary sort: MCAT relevance (higher first within same level)
            mcat_priority = 1.0 - subtopic.mcat_relevance_score
            
            # Tertiary sort: Prerequisites (topics with fewer prereqs first)
            prereq_priority = len(base.prerequisites)
            
            # Quaternary sort: Alphabetical
            alpha_priority = base.subtopic
            
            return (level_priority, mcat_priority, prereq_priority, alpha_priority)
        
        return sorted(enhanced_subtopics, key=mcat_ordering_key)
    
    def _add_interdisciplinary_mcat_connections(self, mcat_enhanced_curricula: Dict[str, List[MCATEnhancedSubtopic]]):
        """Add bidirectional interdisciplinary MCAT connections."""
        
        # Create cross-references between disciplines
        for discipline1, curriculum1 in mcat_enhanced_curricula.items():
            if discipline1 not in self.mcat_disciplines:
                continue
                
            for subtopic1 in curriculum1:
                for discipline2, curriculum2 in mcat_enhanced_curricula.items():
                    if discipline2 != discipline1 and discipline2 in self.mcat_disciplines:
                        
                        # Find related topics in other disciplines
                        related_topics = self._find_related_topics_across_disciplines(
                            subtopic1, discipline1, curriculum2, discipline2
                        )
                        
                        if related_topics:
                            if discipline2 not in subtopic1.interdisciplinary_mcat_links:
                                subtopic1.interdisciplinary_mcat_links[discipline2] = []
                            subtopic1.interdisciplinary_mcat_links[discipline2].extend(related_topics)
                            
                            # Keep only unique links and limit to 3
                            subtopic1.interdisciplinary_mcat_links[discipline2] = list(set(
                                subtopic1.interdisciplinary_mcat_links[discipline2]
                            ))[:3]
    
    def _find_related_topics_across_disciplines(self, source_subtopic: MCATEnhancedSubtopic, 
                                              source_discipline: str,
                                              target_curriculum: List[MCATEnhancedSubtopic], 
                                              target_discipline: str) -> List[str]:
        """Find related topics across disciplines for MCAT integration."""
        related_topics = []
        
        source_text = source_subtopic.base_subtopic.subtopic.lower()
        source_keywords = set(source_text.split())
        
        # Predefined cross-disciplinary connections
        cross_connections = {
            ('Physics', 'Chemistry'): ['energy', 'thermodynamics', 'kinetics', 'spectroscopy'],
            ('Physics', 'Biology'): ['mechanics', 'fluid', 'pressure', 'electrical'],
            ('Chemistry', 'Biology'): ['metabolism', 'enzyme', 'molecular', 'structure'],
            ('Biology', 'Psychology'): ['neuron', 'brain', 'behavior', 'hormone'],
            ('Psychology', 'Sociology'): ['behavior', 'social', 'group', 'culture']
        }
        
        connection_key = (source_discipline, target_discipline)
        relevant_keywords = cross_connections.get(connection_key, [])
        
        # Find matching topics in target discipline
        for target_subtopic in target_curriculum:
            target_text = target_subtopic.base_subtopic.subtopic.lower()
            target_keywords = set(target_text.split())
            
            # Check for keyword overlap
            keyword_overlap = len(source_keywords.intersection(target_keywords))
            
            # Check for predefined cross-connections
            has_cross_connection = any(keyword in source_text and keyword in target_text 
                                     for keyword in relevant_keywords)
            
            if keyword_overlap >= 2 or has_cross_connection:
                related_topics.append(target_subtopic.base_subtopic.subtopic)
        
        return related_topics[:3]  # Limit to 3 related topics
    
    def generate_mcat_integration_report(self, mcat_enhanced_curricula: Dict[str, List[MCATEnhancedSubtopic]]) -> Dict:
        """Generate comprehensive MCAT integration report."""
        
        mcat_disciplines_analyzed = [d for d in mcat_enhanced_curricula.keys() if d in self.mcat_disciplines]
        
        # Calculate coverage statistics
        coverage_stats = {}
        for discipline in mcat_disciplines_analyzed:
            curriculum = mcat_enhanced_curricula[discipline]
            
            high_relevance = len([s for s in curriculum if s.mcat_relevance_score >= 0.7])
            medium_relevance = len([s for s in curriculum if 0.4 <= s.mcat_relevance_score < 0.7])
            
            total_medical_apps = sum(len(s.medical_applications) for s in curriculum)
            total_clinical_contexts = sum(len(s.clinical_contexts) for s in curriculum)
            total_interdisciplinary_links = sum(len(s.interdisciplinary_mcat_links) for s in curriculum)
            
            coverage_stats[discipline] = {
                'total_subtopics': len(curriculum),
                'high_mcat_relevance': high_relevance,
                'medium_mcat_relevance': medium_relevance,
                'average_mcat_relevance': sum(s.mcat_relevance_score for s in curriculum) / len(curriculum) if curriculum else 0,
                'total_medical_applications': total_medical_apps,
                'total_clinical_contexts': total_clinical_contexts,
                'total_interdisciplinary_links': total_interdisciplinary_links
            }
        
        # Interdisciplinary connections matrix
        connection_matrix = {}
        for discipline1 in mcat_disciplines_analyzed:
            connection_matrix[discipline1] = {}
            curriculum1 = mcat_enhanced_curricula[discipline1]
            
            for discipline2 in mcat_disciplines_analyzed:
                if discipline1 != discipline2:
                    connections = 0
                    for subtopic in curriculum1:
                        if discipline2 in subtopic.interdisciplinary_mcat_links:
                            connections += len(subtopic.interdisciplinary_mcat_links[discipline2])
                    connection_matrix[discipline1][discipline2] = connections
        
        return {
            'mcat_disciplines_analyzed': mcat_disciplines_analyzed,
            'coverage_statistics': coverage_stats,
            'interdisciplinary_connection_matrix': connection_matrix,
            'total_enhanced_subtopics': sum(len(curriculum) for curriculum in mcat_enhanced_curricula.values()),
            'overall_mcat_integration_quality': self._calculate_overall_mcat_quality(coverage_stats)
        }
    
    def _calculate_overall_mcat_quality(self, coverage_stats: Dict) -> float:
        """Calculate overall MCAT integration quality score."""
        if not coverage_stats:
            return 0.0
        
        total_scores = []
        for discipline_stats in coverage_stats.values():
            # Weight different factors
            relevance_score = discipline_stats['average_mcat_relevance'] * 0.4
            coverage_score = min(1.0, (discipline_stats['high_mcat_relevance'] + 
                                     discipline_stats['medium_mcat_relevance']) / 
                                discipline_stats['total_subtopics']) * 0.3
            application_score = min(1.0, discipline_stats['total_medical_applications'] / 
                                  discipline_stats['total_subtopics']) * 0.3
            
            total_score = relevance_score + coverage_score + application_score
            total_scores.append(total_score)
        
        return sum(total_scores) / len(total_scores) if total_scores else 0.0
    
    def _get_mcat_prerequisite_concepts(self, discipline: str) -> List[str]:
        """Get prerequisite concepts commonly tested on MCAT for this discipline."""
        prerequisites = {
            'Physics': [
                'mechanics', 'thermodynamics', 'waves', 'electricity', 'magnetism',
                'optics', 'atomic physics', 'fluids'
            ],
            'Chemistry': [
                'atomic structure', 'bonding', 'thermochemistry', 'kinetics', 'equilibrium',
                'acids', 'bases', 'electrochemistry', 'organic chemistry'
            ],
            'Biology': [
                'cell biology', 'genetics', 'evolution', 'anatomy', 'physiology',
                'molecular biology', 'ecology', 'biochemistry'
            ],
            'Psychology': [
                'learning', 'memory', 'cognition', 'development', 'personality',
                'abnormal psychology', 'social psychology', 'research methods'
            ],
            'Sociology': [
                'social structure', 'demographics', 'social inequality', 'social institutions',
                'social change', 'research methods', 'culture', 'socialization'
            ]
        }
        
        return prerequisites.get(discipline, [])
    
    def _load_mcat_content_specifications(self) -> Dict[str, List[MCATContentSpecification]]:
        """Load MCAT content specifications for each discipline."""
        return {
            'Physics': [
                MCATContentSpecification(
                    topic_category="Mechanics",
                    skill_level="Foundational",
                    content_description="Forces, motion, energy, momentum",
                    mcat_sections=["Chemical and Physical Foundations"],
                    prerequisite_concepts=["kinematics", "dynamics", "energy"],
                    typical_question_types=["calculation", "conceptual"],
                    interdisciplinary_connections=["Biology", "Chemistry"]
                ),
                MCATContentSpecification(
                    topic_category="Thermodynamics",
                    skill_level="Content",
                    content_description="Heat, temperature, entropy, phase changes",
                    mcat_sections=["Chemical and Physical Foundations"],
                    prerequisite_concepts=["energy", "kinetic theory"],
                    typical_question_types=["calculation", "graph analysis"],
                    interdisciplinary_connections=["Chemistry", "Biology"]
                ),
                MCATContentSpecification(
                    topic_category="Electromagnetism",
                    skill_level="Content",
                    content_description="Electric fields, magnetic fields, circuits",
                    mcat_sections=["Chemical and Physical Foundations"],
                    prerequisite_concepts=["electricity", "magnetism"],
                    typical_question_types=["circuit analysis", "field calculations"],
                    interdisciplinary_connections=["Biology", "Chemistry"]
                )
            ],
            'Chemistry': [
                MCATContentSpecification(
                    topic_category="Atomic Structure",
                    skill_level="Foundational",
                    content_description="Electronic structure, periodic trends",
                    mcat_sections=["Chemical and Physical Foundations"],
                    prerequisite_concepts=["atoms", "electrons", "periodic table"],
                    typical_question_types=["structure prediction", "trend analysis"],
                    interdisciplinary_connections=["Physics", "Biology"]
                ),
                MCATContentSpecification(
                    topic_category="Chemical Bonding",
                    skill_level="Content",
                    content_description="Ionic, covalent, intermolecular forces",
                    mcat_sections=["Chemical and Physical Foundations"],
                    prerequisite_concepts=["atomic structure", "electronegativity"],
                    typical_question_types=["structure-property", "bonding prediction"],
                    interdisciplinary_connections=["Biology", "Physics"]
                ),
                MCATContentSpecification(
                    topic_category="Biochemistry",
                    skill_level="Scientific Reasoning",
                    content_description="Metabolism, enzymes, macromolecules",
                    mcat_sections=["Biological and Biochemical Foundations"],
                    prerequisite_concepts=["organic chemistry", "thermodynamics"],
                    typical_question_types=["pathway analysis", "enzyme kinetics"],
                    interdisciplinary_connections=["Biology", "Physics"]
                )
            ],
            'Biology': [
                MCATContentSpecification(
                    topic_category="Cell Biology",
                    skill_level="Foundational",
                    content_description="Cell structure, membrane transport, organelles",
                    mcat_sections=["Biological and Biochemical Foundations"],
                    prerequisite_concepts=["chemistry", "molecular biology"],
                    typical_question_types=["process analysis", "structure-function"],
                    interdisciplinary_connections=["Chemistry", "Physics"]
                ),
                MCATContentSpecification(
                    topic_category="Genetics",
                    skill_level="Content",
                    content_description="Inheritance, molecular genetics, gene expression",
                    mcat_sections=["Biological and Biochemical Foundations"],
                    prerequisite_concepts=["DNA", "proteins", "cell division"],
                    typical_question_types=["genetic crosses", "molecular mechanisms"],
                    interdisciplinary_connections=["Chemistry", "Psychology"]
                ),
                MCATContentSpecification(
                    topic_category="Physiology",
                    skill_level="Scientific Reasoning",
                    content_description="Organ systems, homeostasis, regulation",
                    mcat_sections=["Biological and Biochemical Foundations"],
                    prerequisite_concepts=["anatomy", "biochemistry", "physics"],
                    typical_question_types=["system integration", "regulation analysis"],
                    interdisciplinary_connections=["Physics", "Chemistry", "Psychology"]
                )
            ],
            'Psychology': [
                MCATContentSpecification(
                    topic_category="Learning and Memory",
                    skill_level="Foundational",
                    content_description="Classical conditioning, memory processes",
                    mcat_sections=["Psychological, Social, and Biological Foundations"],
                    prerequisite_concepts=["neuroscience", "cognition"],
                    typical_question_types=["theory application", "case analysis"],
                    interdisciplinary_connections=["Biology", "Sociology"]
                ),
                MCATContentSpecification(
                    topic_category="Cognition",
                    skill_level="Content",
                    content_description="Thinking, problem solving, language",
                    mcat_sections=["Psychological, Social, and Biological Foundations"],
                    prerequisite_concepts=["memory", "perception"],
                    typical_question_types=["cognitive processes", "research interpretation"],
                    interdisciplinary_connections=["Biology", "Sociology"]
                )
            ],
            'Sociology': [
                MCATContentSpecification(
                    topic_category="Social Structure",
                    skill_level="Foundational",
                    content_description="Social institutions, stratification, demographics",
                    mcat_sections=["Psychological, Social, and Biological Foundations"],
                    prerequisite_concepts=["social theory", "research methods"],
                    typical_question_types=["theory application", "data interpretation"],
                    interdisciplinary_connections=["Psychology"]
                ),
                MCATContentSpecification(
                    topic_category="Health and Medicine",
                    skill_level="Scientific Reasoning",
                    content_description="Healthcare systems, health disparities",
                    mcat_sections=["Psychological, Social, and Biological Foundations"],
                    prerequisite_concepts=["social structure", "demographics"],
                    typical_question_types=["policy analysis", "disparity assessment"],
                    interdisciplinary_connections=["Psychology", "Biology"]
                )
            ]
        }
    
    def _load_medical_application_mappings(self) -> Dict[str, Dict[str, List[str]]]:
        """Load medical application mappings for each discipline."""
        return {
            'Physics': {
                'mechanics': ['Biomechanics in physical therapy', 'Orthopedic implant design'],
                'thermodynamics': ['Metabolic rate calculations', 'Hypothermia treatment'],
                'electricity': ['ECG and EEG interpretation', 'Defibrillation physics'],
                'optics': ['Vision correction', 'Microscopy in diagnostics'],
                'waves': ['Ultrasound imaging', 'MRI physics'],
                'radiation': ['Radiation therapy', 'Medical imaging']
            },
            'Chemistry': {
                'bonding': ['Drug-receptor interactions', 'Enzyme active sites'],
                'kinetics': ['Pharmacokinetics', 'Enzyme kinetics in metabolism'],
                'equilibrium': ['Acid-base balance', 'Oxygen transport'],
                'organic': ['Drug design', 'Metabolic pathways'],
                'thermodynamics': ['Metabolic energy calculations', 'Protein folding']
            },
            'Biology': {
                'cell': ['Cancer biology', 'Stem cell therapy'],
                'genetics': ['Genetic counseling', 'Gene therapy'],
                'physiology': ['Disease pathophysiology', 'Drug effects'],
                'evolution': ['Antibiotic resistance', 'Vaccine development'],
                'ecology': ['Epidemiology', 'Public health']
            },
            'Psychology': {
                'learning': ['Therapy techniques', 'Patient education'],
                'memory': ['Alzheimer\'s disease', 'Amnesia treatment'],
                'development': ['Pediatric psychology', 'Geriatric care'],
                'abnormal': ['Mental health diagnosis', 'Treatment planning'],
                'social': ['Healthcare communication', 'Patient compliance']
            },
            'Sociology': {
                'inequality': ['Health disparities', 'Access to care'],
                'institutions': ['Healthcare systems', 'Medical education'],
                'demographics': ['Epidemiological patterns', 'Public health policy'],
                'culture': ['Cultural competency', 'Traditional medicine']
            }
        }
    
    def _load_interdisciplinary_connections(self) -> Dict[str, Dict[str, Dict[str, List[str]]]]:
        """Load interdisciplinary MCAT connections."""
        return {
            'Physics': {
                'Chemistry': {
                    'thermodynamics': ['Chemical thermodynamics', 'Reaction energetics'],
                    'mechanics': ['Molecular motion', 'Reaction kinetics'],
                    'electricity': ['Electrochemistry', 'Ion transport']
                },
                'Biology': {
                    'mechanics': ['Biomechanics', 'Muscle contraction'],
                    'fluid': ['Blood flow', 'Respiratory mechanics'],
                    'electricity': ['Nerve conduction', 'Membrane potential']
                }
            },
            'Chemistry': {
                'Biology': {
                    'metabolism': ['Biochemical pathways', 'Energy production'],
                    'structure': ['Protein structure', 'DNA chemistry'],
                    'regulation': ['Enzyme regulation', 'Hormone chemistry']
                },
                'Physics': {
                    'kinetics': ['Reaction rates', 'Molecular motion'],
                    'thermodynamics': ['Energy changes', 'Equilibrium']
                }
            },
            'Biology': {
                'Psychology': {
                    'neuroscience': ['Brain function', 'Neurotransmitters'],
                    'behavior': ['Biological basis of behavior', 'Hormones'],
                    'development': ['Neural development', 'Cognitive development']
                },
                'Chemistry': {
                    'biochemistry': ['Metabolic pathways', 'Molecular biology'],
                    'physiology': ['Chemical signaling', 'Homeostasis']
                }
            },
            'Psychology': {
                'Biology': {
                    'neuroscience': ['Brain structure', 'Neural mechanisms'],
                    'behavior': ['Evolutionary psychology', 'Biological drives']
                },
                'Sociology': {
                    'social': ['Group behavior', 'Social influence'],
                    'development': ['Socialization', 'Cultural development']
                }
            },
            'Sociology': {
                'Psychology': {
                    'social': ['Social psychology', 'Group dynamics'],
                    'culture': ['Cultural psychology', 'Social cognition']
                }
            }
        }
    
    def _load_clinical_context_templates(self) -> Dict[str, List[Dict]]:
        """Load clinical context templates for each discipline."""
        return {
            'Physics': [
                {
                    'keywords': ['force', 'pressure', 'mechanics'],
                    'context_template': 'In clinical practice, {topic} is relevant for understanding biomechanical forces in the human body, such as joint mechanics and muscle function.'
                },
                {
                    'keywords': ['radiation', 'electromagnetic'],
                    'context_template': 'Medical applications of {topic} include diagnostic imaging techniques and radiation therapy for cancer treatment.'
                }
            ],
            'Chemistry': [
                {
                    'keywords': ['reaction', 'kinetics', 'equilibrium'],
                    'context_template': 'Understanding {topic} is essential for pharmacokinetics and drug metabolism in clinical medicine.'
                },
                {
                    'keywords': ['structure', 'bonding', 'molecular'],
                    'context_template': 'Knowledge of {topic} helps in understanding drug-receptor interactions and enzyme function in disease states.'
                }
            ],
            'Biology': [
                {
                    'keywords': ['cell', 'molecular', 'genetics'],
                    'context_template': 'Clinical relevance of {topic} includes understanding disease mechanisms at the cellular and molecular level.'
                },
                {
                    'keywords': ['physiology', 'anatomy', 'system'],
                    'context_template': '{topic} knowledge is fundamental for understanding normal body function and pathophysiology of diseases.'
                }
            ],
            'Psychology': [
                {
                    'keywords': ['cognitive', 'memory', 'learning'],
                    'context_template': 'Clinical applications of {topic} include cognitive assessment, rehabilitation, and understanding learning disabilities.'
                },
                {
                    'keywords': ['social', 'behavior', 'development'],
                    'context_template': 'Understanding {topic} is important for patient communication, therapy techniques, and developmental assessments.'
                }
            ],
            'Sociology': [
                {
                    'keywords': ['inequality', 'access', 'demographics'],
                    'context_template': 'Knowledge of {topic} is crucial for understanding health disparities and developing equitable healthcare policies.'
                },
                {
                    'keywords': ['culture', 'social', 'community'],
                    'context_template': '{topic} understanding helps healthcare providers deliver culturally competent care and engage communities effectively.'
                }
            ]
        }