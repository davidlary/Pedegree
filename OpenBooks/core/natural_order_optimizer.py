#!/usr/bin/env python3
"""
natural_order_optimizer.py - Optimize subtopic ordering for natural educational progression

This module ensures subtopics follow natural educational progression that matches
how concepts build upon each other, creating optimal learning sequences.
"""

import logging
import networkx as nx
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from collections import defaultdict
import re

from .data_models import SubtopicEntry, EducationalLevel, BloomLevel

logger = logging.getLogger(__name__)


@dataclass
class ConceptDependency:
    """Represents a prerequisite relationship between concepts."""
    prerequisite_concept: str
    dependent_concept: str
    dependency_strength: float  # 0-1, how critical this prerequisite is
    dependency_type: str  # 'foundational', 'supportive', 'enriching'
    
    def to_dict(self) -> Dict:
        return {
            'prerequisite_concept': self.prerequisite_concept,
            'dependent_concept': self.dependent_concept,
            'dependency_strength': self.dependency_strength,
            'dependency_type': self.dependency_type
        }


@dataclass
class NaturalOrderingResult:
    """Results of natural ordering optimization."""
    ordered_subtopics: List[SubtopicEntry]
    dependency_graph: nx.DiGraph
    ordering_quality_score: float
    identified_issues: List[str]
    optimization_notes: List[str]
    
    def to_dict(self) -> Dict:
        return {
            'total_subtopics': len(self.ordered_subtopics),
            'ordering_quality_score': self.ordering_quality_score,
            'identified_issues': self.identified_issues,
            'optimization_notes': self.optimization_notes,
            'subtopic_order': [s.subtopic for s in self.ordered_subtopics]
        }


class NaturalOrderOptimizer:
    """
    Optimizes subtopic ordering for natural educational progression.
    
    Ensures subtopics follow the natural concept progression that builds
    knowledge systematically for optimal learning and question generation.
    """
    
    def __init__(self):
        # Load comprehensive discipline knowledge for data-driven ordering
        self.concept_dependencies = self._load_comprehensive_concept_dependencies()
        self.educational_progressions = self._load_comprehensive_educational_progressions()
        self.granularity_patterns = self._load_granularity_patterns()
        self.toc_dependency_cache = {}  # Cache TOC-derived dependencies
        
    def optimize_natural_ordering(self, subtopics: List[SubtopicEntry], 
                                discipline: str, toc_entries: Optional[List] = None) -> NaturalOrderingResult:
        """
        CORE GOAL: Merge multiple TOCs into unified outline of ~1000 fine-grained subtopics.
        
        Creates comprehensive curriculum from high school to advanced graduate level
        in the most effective educational order where prerequisites come first.
        Uses data-driven approach based on TOC order and discipline knowledge.
        """
        logger.info(f"Creating unified curriculum outline for {discipline} from {len(subtopics)} subtopics")
        
        # Step 0: Extract and merge ordering from multiple TOC sources
        if toc_entries:
            logger.info(f"Extracting educational progression from {len(toc_entries)} TOC entries")
            self._extract_and_merge_multi_level_tocs(toc_entries, discipline)
        
        # Step 1: Build comprehensive dependency graph from merged TOC data
        dependency_graph = self._build_unified_curriculum_graph(subtopics, discipline)
        
        # Step 2: Apply educational level progression
        level_ordered_subtopics = self._apply_educational_level_ordering(subtopics)
        
        # Step 3: Apply data-driven concept dependency ordering within levels
        concept_ordered_subtopics = self._apply_concept_dependency_ordering(
            level_ordered_subtopics, dependency_graph, discipline
        )
        
        # Step 4: Optimize for question generation granularity
        optimized_subtopics = self._optimize_question_granularity(
            concept_ordered_subtopics, discipline
        )
        
        # Step 5: Validate and refine ordering
        final_subtopics, quality_score, issues, notes = self._validate_and_refine_ordering(
            optimized_subtopics, dependency_graph, discipline
        )
        
        logger.info(f"Natural ordering optimization complete: quality score {quality_score:.2f}")
        
        return NaturalOrderingResult(
            ordered_subtopics=final_subtopics,
            dependency_graph=dependency_graph,
            ordering_quality_score=quality_score,
            identified_issues=issues,
            optimization_notes=notes
        )
    
    def _extract_and_merge_multi_level_tocs(self, toc_entries: List, discipline: str):
        """
        CORE METHOD: Extract and merge multiple TOCs into unified educational progression.
        
        Merges TOCs from different books/levels into one comprehensive curriculum outline
        that progresses from foundational to advanced topics in optimal educational order.
        """
        if discipline not in self.toc_dependency_cache:
            self.toc_dependency_cache[discipline] = {
                'unified_outline': [],
                'prerequisites': {},
                'educational_levels': {},
                'topic_coverage': set()
            }
        
        # Group TOC entries by educational level and book source
        toc_by_level = defaultdict(list)
        toc_by_book = defaultdict(list)
        
        for entry in toc_entries:
            if not hasattr(entry, 'title') or not entry.title:
                continue
            
            # Determine educational level from book source or content analysis
            edu_level = self._determine_educational_level_from_toc(entry, discipline)
            toc_by_level[edu_level].append(entry)
            
            book_source = getattr(entry, 'book_source', 'unknown')
            toc_by_book[book_source].append(entry)
        
        # Create unified progression by merging across levels
        unified_outline = self._merge_tocs_across_levels(toc_by_level, discipline)
        
        # Extract fine-grained subtopics to reach ~1000 target
        detailed_subtopics = self._extract_fine_grained_subtopics(unified_outline, discipline)
        
        # Build prerequisite relationships from natural progression
        self._build_prerequisite_graph_from_progression(detailed_subtopics, discipline)
        
        # Store unified curriculum
        self.toc_dependency_cache[discipline]['unified_outline'] = detailed_subtopics
        
        logger.info(f"Created unified {discipline} outline with {len(detailed_subtopics)} subtopics "
                   f"across {len(toc_by_level)} educational levels from {len(toc_by_book)} books")
    
    def _determine_educational_level_from_toc(self, toc_entry, discipline: str) -> str:
        """Determine educational level from TOC entry context."""
        book_source = getattr(toc_entry, 'book_source', '').lower()
        title = getattr(toc_entry, 'title', '').lower()
        
        # Analyze book source for level indicators
        if any(indicator in book_source for indicator in ['high school', 'introductory', 'basics', 'principles']):
            return 'high_school'
        elif any(indicator in book_source for indicator in ['undergraduate', 'college', 'university']):
            if any(adv in book_source for adv in ['advanced', 'upper', 'senior']):
                return 'undergraduate_advanced'
            return 'undergraduate_intro'
        elif any(indicator in book_source for indicator in ['graduate', 'masters', 'doctoral', 'phd']):
            return 'graduate'
        elif any(indicator in book_source for indicator in ['research', 'handbook', 'advanced', 'specialized']):
            return 'research'
        
        # Analyze title complexity and content
        complex_terms = ['quantum', 'relativistic', 'advanced', 'nonlinear', 'statistical', 'computational']
        if any(term in title for term in complex_terms):
            return 'graduate'
        
        basic_terms = ['introduction', 'fundamentals', 'basics', 'elementary']
        if any(term in title for term in basic_terms):
            return 'undergraduate_intro'
        
        return 'undergraduate_intro'  # Default level
    
    def _merge_tocs_across_levels(self, toc_by_level: Dict, discipline: str) -> List:
        """Merge TOCs from different educational levels into unified progression."""
        merged_outline = []
        
        # Define progression order
        level_order = [
            'high_school', 'undergraduate_intro', 'undergraduate_advanced', 
            'graduate', 'research'
        ]
        
        # Track concepts already covered to avoid duplication
        covered_concepts = set()
        
        for level in level_order:
            if level not in toc_by_level:
                continue
            
            logger.info(f"Processing {level} level for {discipline}")
            
            # Extract and organize concepts from this level
            level_concepts = self._extract_concepts_from_level(toc_by_level[level], level, covered_concepts)
            
            # Add to unified outline with level annotation
            for concept in level_concepts:
                concept['educational_level'] = level
                merged_outline.append(concept)
                covered_concepts.add(concept['normalized_name'])
        
        return merged_outline
    
    def _extract_concepts_from_level(self, toc_entries: List, level: str, covered_concepts: set) -> List:
        """Extract and organize concepts from TOC entries at a specific educational level."""
        concepts = []
        
        for entry in toc_entries:
            normalized_name = self._normalize_concept_name(entry.title)
            
            # Skip if already covered at previous level (avoid duplication)
            if normalized_name in covered_concepts:
                continue
            
            concept = {
                'title': entry.title,
                'normalized_name': normalized_name,
                'level': getattr(entry, 'level', 0),
                'book_source': getattr(entry, 'book_source', ''),
                'page_number': getattr(entry, 'page_number', None),
                'parent': getattr(entry, 'parent', None),
                'children': getattr(entry, 'children', []),
                'toc_order': len(concepts)  # Track original order
            }
            
            concepts.append(concept)
        
        # Sort by TOC hierarchy and order
        concepts.sort(key=lambda x: (x['level'], x['toc_order']))
        
        return concepts
    
    def _extract_fine_grained_subtopics(self, unified_outline: List, discipline: str) -> List:
        """Extract fine-grained subtopics from unified outline to reach ~1000 target."""
        fine_grained_subtopics = []
        target_count = 1000
        
        # If we have fewer concepts than target, expand each concept
        if len(unified_outline) < target_count:
            expansion_factor = target_count // len(unified_outline) if unified_outline else 1
            
            for concept in unified_outline:
                # Create base subtopic
                fine_grained_subtopics.append(concept)
                
                # Generate expanded subtopics based on discipline knowledge
                expanded = self._generate_expanded_subtopics(concept, discipline, expansion_factor - 1)
                fine_grained_subtopics.extend(expanded)
        else:
            # We have enough concepts, just use them directly
            fine_grained_subtopics = unified_outline[:target_count]
        
        logger.info(f"Generated {len(fine_grained_subtopics)} fine-grained subtopics for {discipline}")
        return fine_grained_subtopics
    
    def _generate_expanded_subtopics(self, base_concept: Dict, discipline: str, count: int) -> List:
        """Generate expanded subtopics from a base concept using discipline knowledge."""
        expanded_subtopics = []
        
        concept_name = base_concept['normalized_name']
        
        # Use discipline-specific expansion patterns
        expansion_patterns = self._get_discipline_expansion_patterns(discipline)
        
        # Find matching expansion pattern
        for pattern, subtopic_types in expansion_patterns.items():
            if pattern in concept_name:
                for i, subtopic_type in enumerate(subtopic_types[:count]):
                    expanded_concept = base_concept.copy()
                    expanded_concept['title'] = f"{base_concept['title']}: {subtopic_type}"
                    expanded_concept['normalized_name'] = f"{concept_name}_{subtopic_type.lower().replace(' ', '_')}"
                    expanded_concept['expansion_type'] = subtopic_type
                    expanded_concept['parent_concept'] = concept_name
                    expanded_subtopics.append(expanded_concept)
                break
        
        # If no pattern matched, use generic expansion
        if not expanded_subtopics and count > 0:
            generic_types = ['Fundamentals', 'Theory', 'Applications', 'Advanced Topics', 'Problem Solving']
            for i, subtopic_type in enumerate(generic_types[:count]):
                expanded_concept = base_concept.copy()
                expanded_concept['title'] = f"{base_concept['title']}: {subtopic_type}"
                expanded_concept['normalized_name'] = f"{concept_name}_{subtopic_type.lower().replace(' ', '_')}"
                expanded_concept['expansion_type'] = subtopic_type
                expanded_concept['parent_concept'] = concept_name
                expanded_subtopics.append(expanded_concept)
        
        return expanded_subtopics
    
    def _build_prerequisite_graph_from_progression(self, detailed_subtopics: List, discipline: str):
        """Build prerequisite relationships from natural educational progression."""
        cache = self.toc_dependency_cache[discipline]
        
        for i, subtopic in enumerate(detailed_subtopics):
            concept_name = subtopic['normalized_name']
            
            if concept_name not in cache['prerequisites']:
                cache['prerequisites'][concept_name] = []
            
            # Add sequential prerequisites (previous concepts at same or lower level)
            for j in range(max(0, i-5), i):  # Look at up to 5 previous concepts
                prev_subtopic = detailed_subtopics[j]
                prev_name = prev_subtopic['normalized_name']
                
                # Determine dependency strength based on educational progression
                strength = self._calculate_progression_dependency_strength(
                    prev_subtopic, subtopic, i - j
                )
                
                if strength > 0.3:  # Only add meaningful dependencies
                    cache['prerequisites'][concept_name].append({
                        'prerequisite': prev_name,
                        'strength': strength,
                        'source': 'educational_progression'
                    })
            
            # Add hierarchical prerequisites (parent concepts)
            if 'parent_concept' in subtopic:
                parent_name = subtopic['parent_concept']
                cache['prerequisites'][concept_name].append({
                    'prerequisite': parent_name,
                    'strength': 0.9,
                    'source': 'hierarchical'
                })
    
    def _calculate_progression_dependency_strength(self, prev_subtopic: Dict, 
                                                 current_subtopic: Dict, distance: int) -> float:
        """Calculate dependency strength based on educational progression."""
        base_strength = max(0, 1.0 - (distance * 0.1))  # Closer concepts have higher strength
        
        # Same educational level: moderate dependency
        if prev_subtopic.get('educational_level') == current_subtopic.get('educational_level'):
            return base_strength * 0.6
        
        # Previous level: strong foundational dependency
        level_order = ['high_school', 'undergraduate_intro', 'undergraduate_advanced', 'graduate', 'research']
        prev_idx = level_order.index(prev_subtopic.get('educational_level', 'undergraduate_intro'))
        curr_idx = level_order.index(current_subtopic.get('educational_level', 'undergraduate_intro'))
        
        if prev_idx < curr_idx:
            return base_strength * 0.8  # Strong prerequisite relationship
        elif prev_idx > curr_idx:
            return 0.0  # Advanced topic can't be prerequisite for basic topic
        
        return base_strength * 0.5  # Same level, moderate relationship
    
    def _add_toc_dependency(self, prereq: str, dependent: str, strength: float, discipline: str):
        """Add a TOC-derived dependency relationship."""
        if prereq not in self.toc_dependency_cache[discipline]:
            self.toc_dependency_cache[discipline][prereq] = []
        
        self.toc_dependency_cache[discipline][prereq].append({
            'dependent': dependent,
            'strength': strength,
            'source': 'toc_order'
        })
    
    def _normalize_concept_name(self, title: str) -> str:
        """Normalize concept names for consistent matching."""
        import re
        # Remove common prefixes/suffixes, numbers, and normalize to lowercase
        normalized = re.sub(r'^(chapter|section|part|unit)\s*\d*:?\s*', '', title.lower())
        normalized = re.sub(r'\s*\(.*?\)\s*', '', normalized)  # Remove parenthetical content
        normalized = re.sub(r'\s+', '_', normalized.strip())  # Replace spaces with underscores
        return normalized
    
    def _get_discipline_expansion_patterns(self, discipline: str) -> Dict[str, List[str]]:
        """Get discipline-specific patterns for expanding concepts into fine-grained subtopics."""
        return {
            'Physics': {
                'mechanics': ['Kinematics', 'Dynamics', 'Statics', 'Rotational Motion', 'Oscillations', 'Waves'],
                'thermodynamics': ['First Law', 'Second Law', 'Heat Engines', 'Entropy', 'Phase Transitions', 'Statistical Mechanics'],
                'electromagnetism': ['Electric Fields', 'Magnetic Fields', 'Electromagnetic Induction', 'Maxwell Equations', 'AC Circuits', 'Electromagnetic Waves'],
                'quantum': ['Wave-Particle Duality', 'Schrödinger Equation', 'Quantum States', 'Operators', 'Spin', 'Entanglement'],
                'relativity': ['Special Relativity', 'General Relativity', 'Spacetime', 'Black Holes', 'Cosmology'],
                'optics': ['Geometric Optics', 'Wave Optics', 'Interference', 'Diffraction', 'Polarization', 'Laser Physics']
            },
            'Chemistry': {
                'atomic_structure': ['Electron Configuration', 'Periodic Trends', 'Atomic Orbitals', 'Nuclear Chemistry'],
                'bonding': ['Ionic Bonding', 'Covalent Bonding', 'Metallic Bonding', 'Intermolecular Forces', 'VSEPR Theory'],
                'thermochemistry': ['Enthalpy', 'Entropy', 'Gibbs Free Energy', 'Calorimetry', 'Phase Diagrams'],
                'kinetics': ['Rate Laws', 'Reaction Mechanisms', 'Catalysis', 'Temperature Effects', 'Collision Theory'],
                'equilibrium': ['Le Chatelier Principle', 'Equilibrium Constants', 'Acid-Base Equilibria', 'Solubility'],
                'organic': ['Alkanes', 'Alkenes', 'Aromatics', 'Functional Groups', 'Reaction Mechanisms', 'Stereochemistry'],
                'analytical': ['Spectroscopy', 'Chromatography', 'Mass Spectrometry', 'Electrochemistry']
            },
            'Biology': {
                'cell': ['Cell Structure', 'Membrane Transport', 'Metabolism', 'Cell Division', 'Cell Signaling'],
                'genetics': ['Mendelian Genetics', 'Molecular Genetics', 'Gene Expression', 'Mutation', 'Population Genetics'],
                'evolution': ['Natural Selection', 'Speciation', 'Phylogeny', 'Evolutionary Evidence', 'Coevolution'],
                'ecology': ['Population Ecology', 'Community Ecology', 'Ecosystem Ecology', 'Conservation', 'Biogeochemical Cycles'],
                'physiology': ['Circulatory System', 'Respiratory System', 'Nervous System', 'Endocrine System', 'Immune System'],
                'molecular': ['DNA Replication', 'Transcription', 'Translation', 'Protein Structure', 'Enzyme Function']
            },
            'Mathematics': {
                'calculus': ['Limits', 'Derivatives', 'Integrals', 'Series', 'Multivariable', 'Differential Equations'],
                'algebra': ['Linear Equations', 'Quadratic Equations', 'Polynomials', 'Matrices', 'Vector Spaces'],
                'geometry': ['Euclidean Geometry', 'Analytic Geometry', 'Trigonometry', 'Coordinate Systems'],
                'statistics': ['Descriptive Statistics', 'Probability', 'Hypothesis Testing', 'Regression', 'ANOVA'],
                'discrete': ['Set Theory', 'Logic', 'Graph Theory', 'Combinatorics', 'Number Theory']
            }
        }.get(discipline, {
            'fundamentals': ['Basic Concepts', 'Theory', 'Applications', 'Problem Solving', 'Advanced Topics']
        })
    
    def _build_unified_curriculum_graph(self, subtopics: List[SubtopicEntry], 
                                      discipline: str) -> nx.DiGraph:
        """Build unified curriculum dependency graph using TOC data and discipline knowledge."""
        graph = nx.DiGraph()
        
        # Add nodes for each subtopic
        for subtopic in subtopics:
            graph.add_node(subtopic.id, subtopic=subtopic)
        
        # Use TOC-derived dependencies if available
        toc_dependencies = self.toc_dependency_cache.get(discipline, {}).get('prerequisites', {})
        
        # Add edges based on explicit prerequisites
        for subtopic in subtopics:
            # Use explicit prerequisites from subtopic
            for prereq in subtopic.prerequisites:
                prereq_subtopic = self._find_subtopic_by_name(prereq, subtopics)
                if prereq_subtopic:
                    graph.add_edge(prereq_subtopic.id, subtopic.id, 
                                 weight=1.0, type='explicit')
            
            # Use TOC-derived dependencies
            subtopic_normalized = self._normalize_concept_name(subtopic.subtopic)
            if subtopic_normalized in toc_dependencies:
                for dep_info in toc_dependencies[subtopic_normalized]:
                    prereq_name = dep_info['prerequisite']
                    strength = dep_info['strength']
                    
                    # Find matching subtopic
                    prereq_subtopic = self._find_subtopic_with_normalized_name(prereq_name, subtopics)
                    if prereq_subtopic and prereq_subtopic.id != subtopic.id:
                        if not graph.has_edge(prereq_subtopic.id, subtopic.id):
                            graph.add_edge(prereq_subtopic.id, subtopic.id,
                                         weight=strength, type='toc_derived')
            
            # Use discipline knowledge dependencies
            subtopic_concepts = self._extract_concepts(subtopic.subtopic)
            dependencies = self.concept_dependencies.get(discipline, {})
            
            for concept in subtopic_concepts:
                if concept in dependencies:
                    for prereq_concept in dependencies[concept]:
                        prereq_subtopic = self._find_subtopic_with_concept(prereq_concept, subtopics)
                        if prereq_subtopic and prereq_subtopic.id != subtopic.id:
                            if not graph.has_edge(prereq_subtopic.id, subtopic.id):
                                strength = self._calculate_dependency_strength(
                                    prereq_concept, concept, discipline
                                )
                                graph.add_edge(prereq_subtopic.id, subtopic.id,
                                             weight=strength, type='knowledge_based')
        
        # Remove cycles while preserving important dependencies
        if not nx.is_directed_acyclic_graph(graph):
            graph = self._remove_cycles_preserving_structure(graph)
        
        return graph
    
    def _find_subtopic_with_normalized_name(self, normalized_name: str, 
                                          subtopics: List[SubtopicEntry]) -> Optional[SubtopicEntry]:
        """Find subtopic by normalized name."""
        for subtopic in subtopics:
            if self._normalize_concept_name(subtopic.subtopic) == normalized_name:
                return subtopic
        return None
        for subtopic in subtopics:
            graph.add_node(subtopic.id, subtopic=subtopic)
        
        # Add edges based on dependencies
        dependencies = self.concept_dependencies.get(discipline, {})
        
        for subtopic in subtopics:
            # Check explicit prerequisites
            for prereq in subtopic.prerequisites:
                prereq_subtopic = self._find_subtopic_by_name(prereq, subtopics)
                if prereq_subtopic:
                    graph.add_edge(prereq_subtopic.id, subtopic.id, 
                                 weight=1.0, type='explicit')
            
            # Check concept-based dependencies
            subtopic_concepts = self._extract_concepts(subtopic.subtopic)
            
            for concept in subtopic_concepts:
                if concept in dependencies:
                    for prereq_concept in dependencies[concept]:
                        prereq_subtopic = self._find_subtopic_with_concept(
                            prereq_concept, subtopics
                        )
                        if prereq_subtopic and prereq_subtopic.id != subtopic.id:
                            # Don't add edge if it already exists
                            if not graph.has_edge(prereq_subtopic.id, subtopic.id):
                                strength = self._calculate_dependency_strength(
                                    prereq_concept, concept, discipline
                                )
                                graph.add_edge(prereq_subtopic.id, subtopic.id,
                                             weight=strength, type='conceptual')
        
        # Remove cycles while preserving important dependencies
        if not nx.is_directed_acyclic_graph(graph):
            graph = self._remove_cycles_preserving_structure(graph)
        
        return graph
    
    def _apply_educational_level_ordering(self, subtopics: List[SubtopicEntry]) -> List[SubtopicEntry]:
        """Apply educational level progression ordering."""
        
        # Define level ordering
        level_order = [
            EducationalLevel.HS_FOUND,
            EducationalLevel.HS_ADV,
            EducationalLevel.UG_INTRO,
            EducationalLevel.UG_ADV,
            EducationalLevel.GRAD_INTRO,
            EducationalLevel.GRAD_ADV
        ]
        
        # Group by level
        by_level = defaultdict(list)
        for subtopic in subtopics:
            by_level[subtopic.level].append(subtopic)
        
        # Order within each level by difficulty and prerequisites
        ordered_subtopics = []
        for level in level_order:
            level_subtopics = by_level[level]
            if level_subtopics:
                # Sort by difficulty score and prerequisite count
                level_subtopics.sort(key=lambda x: (
                    len(x.prerequisites),
                    getattr(x, 'difficulty_score', 0.5),  # Default difficulty if not present
                    x.subtopic
                ))
                ordered_subtopics.extend(level_subtopics)
        
        return ordered_subtopics
    
    def _apply_concept_dependency_ordering(self, subtopics: List[SubtopicEntry], 
                                         dependency_graph: nx.DiGraph, 
                                         discipline: str) -> List[SubtopicEntry]:
        """Apply concept dependency ordering within educational levels."""
        
        # Group by educational level
        by_level = defaultdict(list)
        for subtopic in subtopics:
            by_level[subtopic.level].append(subtopic)
        
        ordered_subtopics = []
        
        for level, level_subtopics in by_level.items():
            if not level_subtopics:
                continue
                
            # Create subgraph for this level
            level_ids = [s.id for s in level_subtopics]
            level_subgraph = dependency_graph.subgraph(level_ids)
            
            try:
                # Topological sort within level
                topo_order = list(nx.topological_sort(level_subgraph))
                
                # Convert back to subtopics
                id_to_subtopic = {s.id: s for s in level_subtopics}
                level_ordered = [id_to_subtopic[node_id] for node_id in topo_order 
                               if node_id in id_to_subtopic]
                
                # Add any subtopics not in the graph
                missing = [s for s in level_subtopics if s.id not in topo_order]
                level_ordered.extend(missing)
                
                ordered_subtopics.extend(level_ordered)
                
            except (nx.NetworkXError, nx.NetworkXUnfeasible):
                # Fallback to difficulty-based ordering if cycles exist
                level_subtopics.sort(key=lambda x: (getattr(x, 'difficulty_score', 0.5), x.subtopic))
                ordered_subtopics.extend(level_subtopics)
        
        return ordered_subtopics
    
    def _optimize_question_granularity(self, subtopics: List[SubtopicEntry], 
                                     discipline: str) -> List[SubtopicEntry]:
        """Optimize subtopic granularity for effective question generation."""
        
        optimized_subtopics = []
        granularity_patterns = self.granularity_patterns.get(discipline, {})
        
        for subtopic in subtopics:
            # Check if subtopic is at appropriate granularity
            granularity_score = self._assess_question_granularity(subtopic, discipline)
            
            if granularity_score >= 0.7:
                # Good granularity, keep as is
                optimized_subtopics.append(subtopic)
            elif granularity_score < 0.4:
                # Too broad, split into more specific subtopics
                split_subtopics = self._split_broad_subtopic(subtopic, discipline)
                optimized_subtopics.extend(split_subtopics)
            else:
                # Moderate granularity, enhance for better question generation
                enhanced_subtopic = self._enhance_subtopic_for_questions(subtopic, discipline)
                optimized_subtopics.append(enhanced_subtopic)
        
        return optimized_subtopics
    
    def _assess_question_granularity(self, subtopic: SubtopicEntry, discipline: str) -> float:
        """Assess how well-suited a subtopic is for question generation."""
        score = 0.5  # Base score
        
        # Title specificity
        title_words = subtopic.subtopic.split()
        if len(title_words) >= 2 and len(title_words) <= 6:
            score += 0.2  # Good title length
        
        # Concept specificity
        vague_terms = ['introduction', 'overview', 'general', 'basic', 'advanced']
        if not any(term.lower() in subtopic.subtopic.lower() for term in vague_terms):
            score += 0.2  # Specific concept
        
        # Learning objectives clarity
        if subtopic.learning_objectives:
            clear_objectives = sum(1 for obj in subtopic.learning_objectives 
                                 if len(obj.split()) >= 5)  # Detailed objectives
            score += min(0.2, clear_objectives * 0.1)
        
        # Discipline-specific context
        if subtopic.discipline_specific_context and len(subtopic.discipline_specific_context) > 50:
            score += 0.1  # Has substantial context
        
        # Question-friendly patterns
        question_friendly_terms = [
            'calculate', 'analyze', 'compare', 'predict', 'explain', 'determine',
            'evaluate', 'apply', 'solve', 'identify'
        ]
        
        text = f"{subtopic.subtopic} {' '.join(subtopic.learning_objectives)}".lower()
        friendly_matches = sum(1 for term in question_friendly_terms if term in text)
        score += min(0.2, friendly_matches * 0.05)
        
        return min(1.0, score)
    
    def _split_broad_subtopic(self, subtopic: SubtopicEntry, discipline: str) -> List[SubtopicEntry]:
        """Split overly broad subtopic into more specific ones."""
        split_subtopics = []
        
        # Get splitting patterns for this discipline
        splitting_patterns = self._get_splitting_patterns(discipline)
        
        subtopic_lower = subtopic.subtopic.lower()
        
        # Find applicable splitting pattern
        for pattern, sub_areas in splitting_patterns.items():
            if pattern in subtopic_lower:
                # Create subtopics for each sub-area
                for i, sub_area in enumerate(sub_areas):
                    split_subtopic = self._create_split_subtopic(
                        subtopic, sub_area, i, discipline
                    )
                    split_subtopics.append(split_subtopic)
                break
        
        # If no pattern matched, create default splits
        if not split_subtopics:
            default_splits = ['Fundamentals', 'Applications', 'Advanced Concepts']
            for i, split_name in enumerate(default_splits):
                split_subtopic = self._create_split_subtopic(
                    subtopic, split_name, i, discipline
                )
                split_subtopics.append(split_subtopic)
        
        return split_subtopics
    
    def _create_split_subtopic(self, original: SubtopicEntry, sub_area: str, 
                             index: int, discipline: str) -> SubtopicEntry:
        """Create a new subtopic from splitting a broader one."""
        from .data_models import create_subtopic_id
        
        new_title = f"{original.subtopic}: {sub_area}"
        
        # Use a base difficulty score since SubtopicEntry doesn't have difficulty_score field
        new_difficulty = 0.5 + (index * 0.05)
        new_difficulty = min(1.0, new_difficulty)
        
        return SubtopicEntry(
            id=create_subtopic_id(discipline, original.category or "General", sub_area),
            discipline=discipline,
            category=original.category or "General",
            subtopic=new_title,
            level=original.level,
            bloom=original.bloom,
            standards_links=original.standards_links,
            prerequisites=original.prerequisites,
            learning_objectives=[f"Master {sub_area} concepts in {original.subtopic}"],
            textbook_references=original.textbook_references,
            question_types=original.question_types if hasattr(original, 'question_types') else [],
            hierarchy_level=original.hierarchy_level if hasattr(original, 'hierarchy_level') else 3,
            parent_topics=original.parent_topics if hasattr(original, 'parent_topics') else [],
            child_topics=original.child_topics if hasattr(original, 'child_topics') else [],
            discipline_specific_context=f"Focused study of {sub_area} within {original.subtopic}",
            discipline_specific_learning_objectives=[
                f"Apply {sub_area} principles in {discipline} contexts"
            ],
            discipline_specific_applications=original.discipline_specific_applications if hasattr(original, 'discipline_specific_applications') else [],
            discipline_specific_prerequisites=original.discipline_specific_prerequisites if hasattr(original, 'discipline_specific_prerequisites') else [],
            scientific_principles_validated=original.scientific_principles_validated,
            authority_source=original.authority_source,
            authority_confidence=original.authority_confidence,
            scientific_principle_conflicts=original.scientific_principle_conflicts,
            cross_disciplinary_links=original.cross_disciplinary_links,
            conceptual_consistency_validated=original.conceptual_consistency_validated,
            common_misconceptions=original.common_misconceptions,
            key_equations=original.key_equations,
            typical_examples=original.typical_examples,
            experimental_methods=original.experimental_methods,
            mcat_relevance=original.mcat_relevance if hasattr(original, 'mcat_relevance') else False
        )
    
    def _enhance_subtopic_for_questions(self, subtopic: SubtopicEntry, discipline: str) -> SubtopicEntry:
        """Enhance subtopic to be more suitable for question generation."""
        enhanced = subtopic
        
        # Enhance learning objectives with more specific, measurable outcomes
        if len(subtopic.learning_objectives) < 3:
            enhanced.learning_objectives = self._generate_enhanced_objectives(subtopic, discipline)
        
        # Add typical examples if missing
        if not subtopic.typical_examples:
            enhanced.typical_examples = self._generate_typical_examples(subtopic, discipline)
        
        # Enhance discipline-specific context
        if len(subtopic.discipline_specific_context) < 100:
            enhanced.discipline_specific_context = self._enhance_context_for_questions(
                subtopic, discipline
            )
        
        return enhanced
    
    def _generate_enhanced_objectives(self, subtopic: SubtopicEntry, discipline: str) -> List[str]:
        """Generate enhanced learning objectives suitable for question generation."""
        base_objectives = subtopic.learning_objectives.copy()
        
        # Add Bloom's taxonomy progression
        bloom_verbs = {
            BloomLevel.REMEMBER: ['identify', 'list', 'define', 'recall'],
            BloomLevel.UNDERSTAND: ['explain', 'describe', 'interpret', 'summarize'],
            BloomLevel.APPLY: ['calculate', 'solve', 'demonstrate', 'use'],
            BloomLevel.ANALYZE: ['compare', 'contrast', 'examine', 'investigate'],
            BloomLevel.EVALUATE: ['assess', 'critique', 'judge', 'justify'],
            BloomLevel.CREATE: ['design', 'construct', 'develop', 'formulate']
        }
        
        verbs = bloom_verbs.get(subtopic.bloom, ['understand'])
        
        enhanced_objectives = base_objectives
        topic = subtopic.subtopic.lower()
        
        # Add specific measurable objectives
        if len(enhanced_objectives) < 3:
            enhanced_objectives.extend([
                f"{verbs[0].title()} key concepts in {topic}",
                f"{verbs[1] if len(verbs) > 1 else verbs[0]} applications of {topic}",
                f"Solve problems involving {topic}"
            ])
        
        return enhanced_objectives[:5]  # Limit to 5 objectives
    
    def _generate_typical_examples(self, subtopic: SubtopicEntry, discipline: str) -> List[str]:
        """Generate typical examples for the subtopic."""
        examples = []
        
        # Discipline-specific example patterns
        example_patterns = {
            'Physics': [
                f"Calculating {subtopic.subtopic.lower()} in physical systems",
                f"Real-world applications of {subtopic.subtopic.lower()}",
                f"Problem-solving with {subtopic.subtopic.lower()}"
            ],
            'Chemistry': [
                f"Chemical reactions involving {subtopic.subtopic.lower()}",
                f"Laboratory synthesis using {subtopic.subtopic.lower()}",
                f"Industrial applications of {subtopic.subtopic.lower()}"
            ],
            'Biology': [
                f"Biological processes related to {subtopic.subtopic.lower()}",
                f"Medical applications of {subtopic.subtopic.lower()}",
                f"Evolutionary significance of {subtopic.subtopic.lower()}"
            ]
        }
        
        patterns = example_patterns.get(discipline, [
            f"Practical applications of {subtopic.subtopic.lower()}",
            f"Problem examples with {subtopic.subtopic.lower()}"
        ])
        
        return patterns[:3]
    
    def _enhance_context_for_questions(self, subtopic: SubtopicEntry, discipline: str) -> str:
        """Enhance discipline-specific context for better question generation."""
        base_context = subtopic.discipline_specific_context
        
        enhanced_context = base_context if base_context else ""
        
        # Add question-generation friendly context
        topic = subtopic.subtopic
        
        question_context = (
            f"This topic enables students to solve problems involving {topic.lower()}, "
            f"analyze real-world applications, and connect concepts to broader {discipline} principles. "
            f"Students should be able to calculate, predict, and explain phenomena related to {topic.lower()}."
        )
        
        if enhanced_context:
            enhanced_context += " " + question_context
        else:
            enhanced_context = question_context
        
        return enhanced_context
    
    def _validate_and_refine_ordering(self, subtopics: List[SubtopicEntry], 
                                    dependency_graph: nx.DiGraph, 
                                    discipline: str) -> Tuple[List[SubtopicEntry], float, List[str], List[str]]:
        """Validate and refine the final ordering."""
        issues = []
        notes = []
        
        # Check for prerequisite violations
        for i, subtopic in enumerate(subtopics):
            for prereq in subtopic.prerequisites:
                prereq_indices = [j for j, s in enumerate(subtopics) 
                                if prereq.lower() in s.subtopic.lower()]
                
                if prereq_indices and all(idx > i for idx in prereq_indices):
                    issues.append(f"Prerequisite '{prereq}' appears after '{subtopic.subtopic}'")
        
        # Check educational level progression
        level_order_map = {
            EducationalLevel.HS_FOUND: 1,
            EducationalLevel.HS_ADV: 2,
            EducationalLevel.UG_INTRO: 3,
            EducationalLevel.UG_ADV: 4,
            EducationalLevel.GRAD_INTRO: 5,
            EducationalLevel.GRAD_ADV: 6
        }
        
        prev_level_value = 0
        for subtopic in subtopics:
            current_level_value = level_order_map.get(subtopic.level, 1)
            if current_level_value < prev_level_value - 1:  # Allow some flexibility
                issues.append(f"Educational level regression at '{subtopic.subtopic}'")
            prev_level_value = current_level_value
        
        # Calculate quality score
        quality_score = self._calculate_ordering_quality(subtopics, dependency_graph, issues)
        
        # Add optimization notes
        notes.append(f"Optimized {len(subtopics)} subtopics for natural progression")
        notes.append(f"Average granularity score: {self._calculate_average_granularity(subtopics, discipline):.2f}")
        
        if quality_score > 0.8:
            notes.append("High-quality ordering achieved")
        elif quality_score > 0.6:
            notes.append("Moderate-quality ordering, some improvements possible")
        else:
            notes.append("Low-quality ordering, significant improvements needed")
        
        return subtopics, quality_score, issues, notes
    
    def _calculate_ordering_quality(self, subtopics: List[SubtopicEntry], 
                                  dependency_graph: nx.DiGraph, issues: List[str]) -> float:
        """Calculate overall quality score for the ordering."""
        
        # Base score
        quality_score = 1.0
        
        # Penalize for issues
        quality_score -= len(issues) * 0.1
        
        # Check prerequisite satisfaction
        prereq_satisfaction = 0
        total_prereqs = 0
        
        for i, subtopic in enumerate(subtopics):
            for prereq in subtopic.prerequisites:
                total_prereqs += 1
                # Check if prerequisite appears before this subtopic
                for j, other_subtopic in enumerate(subtopics[:i]):
                    if prereq.lower() in other_subtopic.subtopic.lower():
                        prereq_satisfaction += 1
                        break
        
        if total_prereqs > 0:
            prereq_score = prereq_satisfaction / total_prereqs
            quality_score = quality_score * 0.7 + prereq_score * 0.3
        
        # Check difficulty progression
        difficulty_progression = 0
        for i in range(1, len(subtopics)):
            current_difficulty = getattr(subtopics[i], 'difficulty_score', 0.5)
            prev_difficulty = getattr(subtopics[i-1], 'difficulty_score', 0.5)
            if current_difficulty >= prev_difficulty - 0.1:  # Allow small decreases
                difficulty_progression += 1
        
        if len(subtopics) > 1:
            difficulty_score = difficulty_progression / (len(subtopics) - 1)
            quality_score = quality_score * 0.8 + difficulty_score * 0.2
        
        return max(0.0, min(1.0, quality_score))
    
    def _calculate_average_granularity(self, subtopics: List[SubtopicEntry], discipline: str) -> float:
        """Calculate average granularity score for question generation."""
        if not subtopics:
            return 0.0
        
        granularity_scores = [self._assess_question_granularity(subtopic, discipline) 
                            for subtopic in subtopics]
        
        return sum(granularity_scores) / len(granularity_scores)
    
    # Helper methods
    def _extract_concepts(self, subtopic_title: str) -> List[str]:
        """Extract key concepts from subtopic title."""
        # Remove common words and extract meaningful concepts
        stop_words = {'the', 'and', 'or', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        
        words = re.findall(r'\b\w+\b', subtopic_title.lower())
        concepts = [word for word in words if word not in stop_words and len(word) > 2]
        
        return concepts
    
    def _find_subtopic_by_name(self, name: str, subtopics: List[SubtopicEntry]) -> Optional[SubtopicEntry]:
        """Find subtopic by name or partial match."""
        name_lower = name.lower()
        
        # Exact match first
        for subtopic in subtopics:
            if subtopic.subtopic.lower() == name_lower:
                return subtopic
        
        # Partial match
        for subtopic in subtopics:
            if name_lower in subtopic.subtopic.lower():
                return subtopic
        
        return None
    
    def _find_subtopic_with_concept(self, concept: str, subtopics: List[SubtopicEntry]) -> Optional[SubtopicEntry]:
        """Find subtopic that contains a specific concept."""
        concept_lower = concept.lower()
        
        for subtopic in subtopics:
            if concept_lower in subtopic.subtopic.lower():
                return subtopic
        
        return None
    
    def _calculate_dependency_strength(self, prereq_concept: str, concept: str, discipline: str) -> float:
        """Calculate strength of dependency between concepts."""
        # This would be enhanced with domain knowledge
        # For now, use simple heuristics
        
        dependency_weights = {
            'foundational': 0.9,
            'supportive': 0.7,
            'enriching': 0.5
        }
        
        # Default strength
        return 0.6
    
    def _remove_cycles_preserving_structure(self, graph: nx.DiGraph) -> nx.DiGraph:
        """Remove cycles while preserving important dependency structure."""
        try:
            cycles = list(nx.simple_cycles(graph))
            for cycle in cycles:
                if len(cycle) >= 2:
                    # Remove edge with lowest weight
                    edges_in_cycle = [(cycle[i], cycle[(i+1) % len(cycle)]) 
                                    for i in range(len(cycle))]
                    
                    # Find edge with minimum weight
                    min_weight = float('inf')
                    min_edge = None
                    
                    for edge in edges_in_cycle:
                        if graph.has_edge(edge[0], edge[1]):
                            weight = graph[edge[0]][edge[1]].get('weight', 0.5)
                            if weight < min_weight:
                                min_weight = weight
                                min_edge = edge
                    
                    if min_edge:
                        graph.remove_edge(min_edge[0], min_edge[1])
        
        except Exception as e:
            logger.warning(f"Error removing cycles: {e}")
        
        return graph
    
    def _get_splitting_patterns(self, discipline: str) -> Dict[str, List[str]]:
        """Get patterns for splitting broad subtopics."""
        return {
            'Physics': {
                'mechanics': ['Kinematics', 'Dynamics', 'Energy and Work', 'Momentum'],
                'thermodynamics': ['First Law', 'Second Law', 'Heat Engines', 'Statistical Mechanics'],
                'electromagnetism': ['Electric Fields', 'Magnetic Fields', 'Electromagnetic Induction', 'Maxwell Equations'],
                'quantum': ['Wave-Particle Duality', 'Schrödinger Equation', 'Quantum States', 'Applications']
            },
            'Chemistry': {
                'bonding': ['Ionic Bonding', 'Covalent Bonding', 'Metallic Bonding', 'Intermolecular Forces'],
                'kinetics': ['Rate Laws', 'Reaction Mechanisms', 'Catalysis', 'Temperature Effects'],
                'equilibrium': ['Dynamic Equilibrium', 'Le Chatelier Principle', 'Equilibrium Constants', 'Applications'],
                'organic': ['Alkanes', 'Alkenes', 'Aromatic Compounds', 'Functional Groups']
            },
            'Biology': {
                'genetics': ['Mendelian Genetics', 'Molecular Genetics', 'Population Genetics', 'Gene Expression'],
                'evolution': ['Natural Selection', 'Speciation', 'Phylogeny', 'Evolutionary Evidence'],
                'ecology': ['Population Ecology', 'Community Ecology', 'Ecosystem Ecology', 'Conservation'],
                'cell': ['Cell Structure', 'Membrane Transport', 'Metabolism', 'Cell Division']
            }
        }
    
    def _load_comprehensive_concept_dependencies(self) -> Dict[str, Dict[str, List[str]]]:
        """Load concept dependency mappings."""
        return {
            'Physics': {
                'dynamics': ['kinematics', 'vectors'],
                'energy': ['mechanics', 'calculus'],
                'waves': ['oscillations', 'mathematics'],
                'electromagnetism': ['vectors', 'calculus', 'fields'],
                'quantum': ['waves', 'linear algebra', 'probability']
            },
            'Chemistry': {
                'bonding': ['atomic structure', 'periodic table'],
                'kinetics': ['mathematics', 'equilibrium concepts'],
                'thermodynamics': ['energy concepts', 'mathematics'],
                'organic': ['bonding', 'structure'],
                'equilibrium': ['kinetics', 'mathematics']
            },
            'Biology': {
                'genetics': ['cell biology', 'molecular biology'],
                'evolution': ['genetics', 'ecology'],
                'physiology': ['anatomy', 'chemistry'],
                'ecology': ['evolution', 'statistics'],
                'molecular biology': ['chemistry', 'cell biology']
            }
        }
    
    def _load_comprehensive_educational_progressions(self) -> Dict[str, List[str]]:
        """Load standard educational progressions by discipline."""
        return {
            'Physics': [
                'Basic Mathematics', 'Mechanics', 'Thermodynamics', 'Waves and Sound',
                'Electricity and Magnetism', 'Optics', 'Modern Physics', 'Quantum Mechanics'
            ],
            'Chemistry': [
                'Atomic Structure', 'Periodic Table', 'Chemical Bonding', 'Stoichiometry',
                'Thermochemistry', 'Kinetics', 'Equilibrium', 'Acids and Bases',
                'Electrochemistry', 'Organic Chemistry'
            ],
            'Biology': [
                'Cell Biology', 'Molecular Biology', 'Genetics', 'Evolution',
                'Anatomy and Physiology', 'Ecology', 'Biotechnology'
            ]
        }
    
    def _load_granularity_patterns(self) -> Dict[str, Dict[str, float]]:
        """Load granularity assessment patterns."""
        return {
            'Physics': {
                'calculation_focus': 0.9,
                'concept_application': 0.8,
                'theory_explanation': 0.7,
                'broad_overview': 0.3
            },
            'Chemistry': {
                'reaction_mechanism': 0.9,
                'calculation_method': 0.8,
                'concept_application': 0.7,
                'general_principle': 0.4
            },
            'Biology': {
                'process_mechanism': 0.9,
                'system_function': 0.8,
                'concept_application': 0.7,
                'broad_survey': 0.3
            }
        }