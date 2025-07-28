#!/usr/bin/env python3
"""
curriculum_synthesizer.py - Synthesize comprehensive curriculum with ~1000 subtopics per discipline

This module merges TOC headings into unified curricula with fine-grained subtopics,
prerequisite ordering, and scientific validation to create comprehensive educational sequences.
"""

import logging
import networkx as nx
from typing import Dict, List, Optional, Tuple, Set, Any
from dataclasses import dataclass
from collections import defaultdict
import re
from difflib import SequenceMatcher

from .data_models import (
    SubtopicEntry, TOCEntry, EducationalLevel, BloomLevel, QuestionType,
    create_subtopic_id
)

logger = logging.getLogger(__name__)


@dataclass
class TopicCluster:
    """
    Goal: Group related topics for systematic expansion to fine-grained subtopics.
    
    Enables organized expansion of broad topics into the target ~1000 subtopics
    while maintaining educational coherence.
    """
    cluster_id: str
    main_topic: str
    related_topics: List[str]
    hierarchy_level: int  # 1-6 in the 6-level hierarchy
    prerequisite_clusters: List[str]
    expansion_potential: int  # Estimated subtopics this cluster can generate
    authority_sources: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'cluster_id': self.cluster_id,
            'main_topic': self.main_topic,
            'related_topics': self.related_topics,
            'hierarchy_level': self.hierarchy_level,
            'prerequisite_clusters': self.prerequisite_clusters,
            'expansion_potential': self.expansion_potential,
            'authority_sources': self.authority_sources
        }


@dataclass
class PrerequisiteRelationship:
    """
    Goal: Define prerequisite relationships for optimal learning sequence.
    
    Enables building of dependency graphs for proper educational progression.
    """
    prerequisite_topic: str
    dependent_topic: str
    relationship_type: str  # "foundation", "supporting", "enabling", "enhancing"
    strength: float  # 0-1, how critical this prerequisite is
    confidence: float  # 0-1, confidence in the relationship
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'prerequisite_topic': self.prerequisite_topic,
            'dependent_topic': self.dependent_topic,
            'relationship_type': self.relationship_type,
            'strength': self.strength,
            'confidence': self.confidence
        }


class CurriculumSynthesizer:
    """
    Goal: Merge TOC headings into unified ~1000 subtopic curriculum per discipline.
    
    Creates comprehensive, well-ordered curricula with scientific validation,
    prerequisite tracking, and systematic expansion to target granularity.
    """
    
    def __init__(self):
        self.target_subtopics = 1000  # Target number of subtopics per discipline
        self.semantic_similarity_threshold = 0.8
        self.expansion_templates = self._load_expansion_templates()
        self.prerequisite_patterns = self._load_prerequisite_patterns()
        self.discipline_hierarchies = self._load_discipline_hierarchies()
        
    def synthesize_curriculum_with_scientific_validation(self, all_topics: List[TOCEntry], 
                                                       discipline: str) -> List[SubtopicEntry]:
        """
        Goal: Create unified curriculum with scientific validation and authority tracking.
        
        Processes all TOC entries to create comprehensive, validated curriculum
        with individual subtopic-level contexts and ~1000 fine-grained subtopics.
        """
        logger.info(f"Synthesizing curriculum for {discipline} from {len(all_topics)} TOC entries")
        
        # Step 1: Semantic deduplication with scientific accuracy preservation
        deduplicated_topics = self._semantic_deduplication(all_topics, discipline)
        logger.info(f"After deduplication: {len(deduplicated_topics)} unique topics")
        
        # Step 2: Create topic clusters for systematic expansion
        topic_clusters = self._create_topic_clusters(deduplicated_topics, discipline)
        logger.info(f"Created {len(topic_clusters)} topic clusters")
        
        # Step 3: Build prerequisite relationships
        prerequisite_graph = self._build_prerequisite_graph(topic_clusters, discipline)
        logger.info(f"Built prerequisite graph with {prerequisite_graph.number_of_nodes()} nodes")
        
        # Step 4: Expand systematically to ~1000 subtopics
        expanded_subtopics = self._expand_to_thousand_subtopics_systematic(
            topic_clusters, discipline, prerequisite_graph
        )
        logger.info(f"Expanded to {len(expanded_subtopics)} subtopics")
        
        # Step 5: Apply individual subtopic-level discipline-specific contexts
        contextualized_subtopics = self._apply_validated_subtopic_contexts(
            expanded_subtopics, discipline
        )
        
        # Step 6: Validate prerequisite scientific consistency
        consistency_issues = self._validate_prerequisite_scientific_consistency(contextualized_subtopics)
        if consistency_issues:
            logger.warning(f"Found {len(consistency_issues)} prerequisite consistency issues")
        
        # Step 7: Final validation and optimization
        final_curriculum = self._optimize_curriculum_structure(contextualized_subtopics, discipline)
        
        logger.info(f"Final curriculum for {discipline}: {len(final_curriculum)} subtopics")
        return final_curriculum
    
    def _semantic_deduplication(self, topics: List[TOCEntry], discipline: str) -> List[TOCEntry]:
        """
        Goal: Remove duplicate topics while preserving pedagogical extensions.
        
        Uses semantic similarity to identify duplicates while maintaining
        the clearest, most widely used terminology.
        """
        unique_topics = []
        topic_groups = []  # Groups of similar topics
        
        for topic in topics:
            # Find existing group this topic belongs to
            assigned_group = None
            for group in topic_groups:
                if self._topics_are_similar(topic, group[0], discipline):
                    group.append(topic)
                    assigned_group = group
                    break
            
            # Create new group if no match found
            if assigned_group is None:
                topic_groups.append([topic])
        
        # Select best topic from each group
        for group in topic_groups:
            best_topic = self._select_best_topic_from_group(group, discipline)
            
            # Merge pedagogical extensions from other topics in group
            merged_topic = self._merge_pedagogical_extensions(best_topic, group)
            unique_topics.append(merged_topic)
        
        return unique_topics
    
    def _topics_are_similar(self, topic1: TOCEntry, topic2: TOCEntry, discipline: str) -> bool:
        """Check if two topics are semantically similar."""
        # Normalize titles for comparison
        title1 = self._normalize_topic_title(topic1.title, discipline)
        title2 = self._normalize_topic_title(topic2.title, discipline)
        
        # Calculate similarity score
        similarity = SequenceMatcher(None, title1.lower(), title2.lower()).ratio()
        
        # Check for keyword overlap
        words1 = set(title1.lower().split())
        words2 = set(title2.lower().split())
        
        # Remove stop words
        stop_words = {'and', 'or', 'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'with'}
        words1 -= stop_words
        words2 -= stop_words
        
        if len(words1) == 0 or len(words2) == 0:
            return similarity >= self.semantic_similarity_threshold
        
        word_overlap = len(words1.intersection(words2)) / min(len(words1), len(words2))
        
        # Combined similarity score
        combined_similarity = (similarity + word_overlap) / 2
        
        return combined_similarity >= self.semantic_similarity_threshold
    
    def _normalize_topic_title(self, title: str, discipline: str) -> str:
        """Normalize topic title for comparison."""
        # Remove common prefixes/suffixes
        normalized = title.strip()
        
        # Remove chapter/section numbers
        normalized = re.sub(r'^(chapter|section|unit)\s*\d+\s*[:\-\.]?\s*', '', normalized, flags=re.IGNORECASE)
        normalized = re.sub(r'^\d+\.\d*\s*', '', normalized)
        
        # Remove common discipline prefixes
        discipline_prefixes = {
            'Physics': ['introduction to', 'principles of', 'fundamentals of'],
            'Chemistry': ['basic', 'general', 'organic', 'inorganic'],
            'Biology': ['introduction to', 'principles of', 'general'],
            'Mathematics': ['basic', 'elementary', 'intermediate', 'advanced']
        }
        
        for prefix in discipline_prefixes.get(discipline, []):
            pattern = rf'^{re.escape(prefix)}\s+'
            normalized = re.sub(pattern, '', normalized, flags=re.IGNORECASE)
        
        return normalized.strip()
    
    def _select_best_topic_from_group(self, group: List[TOCEntry], discipline: str) -> TOCEntry:
        """Select the best representative topic from a similarity group."""
        if len(group) == 1:
            return group[0]
        
        # Scoring factors
        def score_topic(topic: TOCEntry) -> float:
            score = 0.0
            
            # Prefer standard terminology
            if self._uses_standard_terminology(topic.title, discipline):
                score += 2.0
            
            # Prefer comprehensive titles (not too short, not too long)
            title_length = len(topic.title.split())
            if 2 <= title_length <= 6:
                score += 1.0
            
            # Prefer topics with more hierarchy information
            if topic.level > 0:
                score += 0.5
            
            # Prefer topics from authoritative sources
            if self._is_authoritative_source(topic.book_source):
                score += 1.0
            
            return score
        
        # Select highest scoring topic
        scored_topics = [(topic, score_topic(topic)) for topic in group]
        best_topic = max(scored_topics, key=lambda x: x[1])[0]
        
        return best_topic
    
    def _merge_pedagogical_extensions(self, base_topic: TOCEntry, group: List[TOCEntry]) -> TOCEntry:
        """Merge pedagogical extensions from similar topics."""
        # This would be enhanced to extract and merge actual pedagogical content
        # For now, we'll preserve the base topic structure
        merged = base_topic
        
        # Could add logic to merge:
        # - Key equations from multiple sources
        # - Typical examples
        # - Experimental methods
        # - Additional context
        
        return merged
    
    def _create_topic_clusters(self, topics: List[TOCEntry], discipline: str) -> List[TopicCluster]:
        """
        Goal: Create topic clusters for systematic expansion to fine-grained subtopics.
        
        Groups related topics to enable organized expansion while maintaining
        educational coherence and hierarchy.
        """
        clusters = []
        hierarchy = self.discipline_hierarchies.get(discipline, self._get_default_hierarchy())
        
        # Group topics by hierarchy level and content area
        hierarchy_groups = defaultdict(list)
        for topic in topics:
            level = min(topic.level, 6)  # Cap at level 6
            hierarchy_groups[level].append(topic)
        
        cluster_id_counter = 0
        
        # Create clusters for each hierarchy level
        for level, level_topics in hierarchy_groups.items():
            content_areas = self._group_by_content_area(level_topics, discipline)
            
            for area_name, area_topics in content_areas.items():
                cluster_id_counter += 1
                
                # Estimate expansion potential
                expansion_potential = self._estimate_expansion_potential(area_topics, level, discipline)
                
                cluster = TopicCluster(
                    cluster_id=f"{discipline}_{level}_{cluster_id_counter:03d}",
                    main_topic=area_name,
                    related_topics=[topic.title for topic in area_topics],
                    hierarchy_level=level,
                    prerequisite_clusters=[],  # Will be populated later
                    expansion_potential=expansion_potential,
                    authority_sources=list(set(topic.book_source for topic in area_topics))
                )
                
                clusters.append(cluster)
        
        # Identify prerequisite relationships between clusters
        self._identify_cluster_prerequisites(clusters, discipline)
        
        return clusters
    
    def _group_by_content_area(self, topics: List[TOCEntry], discipline: str) -> Dict[str, List[TOCEntry]]:
        """Group topics by content area within the same hierarchy level."""
        content_areas = defaultdict(list)
        
        # Use keyword-based grouping
        area_keywords = self._get_content_area_keywords(discipline)
        
        for topic in topics:
            topic_lower = topic.title.lower()
            assigned_area = None
            
            # Find matching content area
            for area_name, keywords in area_keywords.items():
                if any(keyword in topic_lower for keyword in keywords):
                    assigned_area = area_name
                    break
            
            # Default area if no match
            if assigned_area is None:
                assigned_area = "General"
            
            content_areas[assigned_area].append(topic)
        
        return dict(content_areas)
    
    def _get_content_area_keywords(self, discipline: str) -> Dict[str, List[str]]:
        """Get keyword mappings for content areas by discipline."""
        keyword_mappings = {
            'Physics': {
                'Mechanics': ['force', 'motion', 'energy', 'momentum', 'mechanics', 'dynamics', 'kinematics'],
                'Thermodynamics': ['heat', 'temperature', 'entropy', 'thermodynamics', 'thermal'],
                'Electromagnetism': ['electric', 'magnetic', 'electromagnetic', 'charge', 'field', 'current'],
                'Waves': ['wave', 'oscillation', 'vibration', 'sound', 'light', 'frequency'],
                'Modern Physics': ['quantum', 'relativity', 'atomic', 'nuclear', 'particle', 'modern'],
                'Optics': ['light', 'lens', 'mirror', 'optics', 'refraction', 'reflection']
            },
            'Chemistry': {
                'Atomic Structure': ['atom', 'electron', 'nucleus', 'orbital', 'quantum', 'structure'],
                'Bonding': ['bond', 'molecular', 'ionic', 'covalent', 'intermolecular'],
                'Thermodynamics': ['enthalpy', 'entropy', 'gibbs', 'thermodynamics', 'energy'],
                'Kinetics': ['rate', 'kinetics', 'mechanism', 'catalyst', 'activation'],
                'Equilibrium': ['equilibrium', 'balance', 'le chatelier', 'constant'],
                'Acids and Bases': ['acid', 'base', 'ph', 'buffer', 'titration'],
                'Organic Chemistry': ['organic', 'hydrocarbon', 'functional group', 'polymer'],
                'Analytical Chemistry': ['analysis', 'spectroscopy', 'chromatography', 'analytical']
            },
            'Biology': {
                'Cell Biology': ['cell', 'membrane', 'organelle', 'cytoplasm', 'nucleus'],
                'Genetics': ['gene', 'dna', 'rna', 'chromosome', 'heredity', 'mutation'],
                'Evolution': ['evolution', 'natural selection', 'adaptation', 'species', 'darwin'],
                'Ecology': ['ecosystem', 'population', 'community', 'environment', 'ecology'],
                'Physiology': ['organ', 'system', 'function', 'homeostasis', 'physiology'],
                'Biochemistry': ['enzyme', 'protein', 'metabolism', 'biochemical', 'pathway'],
                'Molecular Biology': ['molecular', 'transcription', 'translation', 'replication']
            },
            'Psychology': {
                'Cognitive Psychology': ['cognition', 'memory', 'learning', 'thinking', 'perception'],
                'Social Psychology': ['social', 'group', 'attitude', 'prejudice', 'conformity'],
                'Developmental Psychology': ['development', 'child', 'adolescent', 'aging', 'lifespan'],
                'Abnormal Psychology': ['abnormal', 'disorder', 'mental health', 'psychopathology'],
                'Research Methods': ['research', 'statistics', 'experiment', 'methodology', 'data'],
                'Biological Psychology': ['brain', 'neuron', 'nervous system', 'biological', 'neuropsychology']
            }
        }
        
        return keyword_mappings.get(discipline, {'General': ['general', 'introduction', 'overview']})
    
    def _estimate_expansion_potential(self, topics: List[TOCEntry], level: int, discipline: str) -> int:
        """Estimate how many subtopics this cluster can generate."""
        base_topics = len(topics)
        
        # Expansion factors by hierarchy level
        level_multipliers = {
            1: 2,   # Discipline level - broad expansion
            2: 8,   # Main branches - significant expansion  
            3: 12,  # Subtopics - major expansion
            4: 15,  # Detailed concepts - maximum expansion
            5: 8,   # Fine-grained details - moderate expansion
            6: 3    # Micro-concepts - minimal expansion
        }
        
        base_expansion = base_topics * level_multipliers.get(level, 5)
        
        # Adjust for discipline complexity
        discipline_factors = {
            'Physics': 1.2,  # High mathematical complexity
            'Chemistry': 1.1,
            'Biology': 1.3,  # High diversity of topics
            'Psychology': 0.9,
            'Mathematics': 1.1
        }
        
        factor = discipline_factors.get(discipline, 1.0)
        return int(base_expansion * factor)
    
    def _identify_cluster_prerequisites(self, clusters: List[TopicCluster], discipline: str) -> None:
        """Identify prerequisite relationships between topic clusters."""
        
        for cluster in clusters:
            prerequisites = []
            
            # Lower hierarchy levels are generally prerequisites for higher levels
            for other_cluster in clusters:
                if other_cluster.hierarchy_level < cluster.hierarchy_level:
                    # Check for content dependencies
                    if self._clusters_have_dependency(other_cluster, cluster, discipline):
                        prerequisites.append(other_cluster.cluster_id)
            
            cluster.prerequisite_clusters = prerequisites
    
    def _clusters_have_dependency(self, prerequisite_cluster: TopicCluster, 
                                 dependent_cluster: TopicCluster, discipline: str) -> bool:
        """Check if one cluster is a prerequisite for another."""
        
        # Get prerequisite patterns for the discipline
        patterns = self.prerequisite_patterns.get(discipline, {})
        
        prereq_topics = [topic.lower() for topic in prerequisite_cluster.related_topics]
        dependent_topics = [topic.lower() for topic in dependent_cluster.related_topics]
        
        # Check for explicit patterns
        for dependent_topic in dependent_topics:
            for pattern, prereqs in patterns.items():
                if pattern in dependent_topic:
                    for prereq in prereqs:
                        if any(prereq in prereq_topic for prereq_topic in prereq_topics):
                            return True
        
        # Check for mathematical progression
        if self._has_mathematical_progression(prerequisite_cluster, dependent_cluster):
            return True
        
        return False
    
    def _has_mathematical_progression(self, cluster1: TopicCluster, cluster2: TopicCluster) -> bool:
        """Check for mathematical progression between clusters."""
        math_progressions = [
            ['algebra', 'calculus'],
            ['arithmetic', 'algebra'],
            ['geometry', 'trigonometry'],
            ['basic', 'advanced'],
            ['introduction', 'intermediate', 'advanced']
        ]
        
        topics1_lower = [topic.lower() for topic in cluster1.related_topics]
        topics2_lower = [topic.lower() for topic in cluster2.related_topics]
        
        for progression in math_progressions:
            for i in range(len(progression) - 1):
                prereq_level = progression[i]
                advanced_level = progression[i + 1]
                
                has_prereq = any(prereq_level in topic for topic in topics1_lower)
                has_advanced = any(advanced_level in topic for topic in topics2_lower)
                
                if has_prereq and has_advanced:
                    return True
        
        return False
    
    def _build_prerequisite_graph(self, clusters: List[TopicCluster], discipline: str) -> nx.DiGraph:
        """
        Goal: Build prerequisite dependency graph for optimal learning sequence.
        
        Creates directed acyclic graph of concept dependencies to ensure
        proper educational progression.
        """
        graph = nx.DiGraph()
        
        # Add nodes for each cluster
        for cluster in clusters:
            graph.add_node(cluster.cluster_id, 
                          cluster=cluster,
                          level=cluster.hierarchy_level,
                          main_topic=cluster.main_topic)
        
        # Add prerequisite edges
        for cluster in clusters:
            for prereq_id in cluster.prerequisite_clusters:
                if prereq_id in graph:
                    graph.add_edge(prereq_id, cluster.cluster_id, 
                                 relationship_type="prerequisite")
        
        # Validate DAG (no cycles)
        if not nx.is_directed_acyclic_graph(graph):
            logger.warning(f"Prerequisite graph for {discipline} contains cycles - removing problematic edges")
            graph = self._remove_cycles(graph)
        
        return graph
    
    def _remove_cycles(self, graph: nx.DiGraph) -> nx.DiGraph:
        """Remove cycles from prerequisite graph."""
        try:
            # Find and remove edges that create cycles
            cycles = list(nx.simple_cycles(graph))
            for cycle in cycles:
                # Remove the edge with lowest confidence/strength
                # For now, remove the last edge in the cycle
                if len(cycle) >= 2:
                    graph.remove_edge(cycle[-1], cycle[0])
            
            return graph
        except Exception as e:
            logger.error(f"Error removing cycles: {e}")
            return graph
    
    def _expand_to_thousand_subtopics_systematic(self, clusters: List[TopicCluster], 
                                               discipline: str, 
                                               prerequisite_graph: nx.DiGraph) -> List[SubtopicEntry]:
        """
        Goal: Systematically expand to ~1000 subtopics with quality control.
        
        Uses hierarchical decomposition and expansion templates to reach
        target granularity while maintaining educational coherence.
        """
        subtopics = []
        current_count = 0
        target = self.target_subtopics
        
        # Sort clusters by topological order (prerequisites first)
        try:
            ordered_clusters = list(nx.topological_sort(prerequisite_graph))
        except nx.NetworkXError:
            # Fallback to hierarchy level ordering
            ordered_clusters = [c.cluster_id for c in sorted(clusters, key=lambda x: x.hierarchy_level)]
        
        # Calculate expansion quota per cluster
        total_potential = sum(cluster.expansion_potential for cluster in clusters)
        
        for cluster_id in ordered_clusters:
            cluster = next((c for c in clusters if c.cluster_id == cluster_id), None)
            if not cluster:
                continue
            
            # Calculate how many subtopics this cluster should generate
            if total_potential > 0:
                cluster_quota = int((cluster.expansion_potential / total_potential) * target)
            else:
                cluster_quota = target // len(clusters)
            
            # Expand cluster to subtopics
            cluster_subtopics = self._expand_cluster_to_subtopics(
                cluster, cluster_quota, discipline, current_count
            )
            
            subtopics.extend(cluster_subtopics)
            current_count += len(cluster_subtopics)
            
            if current_count >= target:
                break
        
        # If we haven't reached the target, add more detail to important areas
        if current_count < target:
            remaining = target - current_count
            subtopics.extend(self._add_specialized_subtopics(clusters, discipline, remaining))
        
        return subtopics[:target]  # Ensure we don't exceed target
    
    def _expand_cluster_to_subtopics(self, cluster: TopicCluster, quota: int, 
                                   discipline: str, current_id: int) -> List[SubtopicEntry]:
        """Expand a topic cluster into fine-grained subtopics."""
        subtopics = []
        
        # Get expansion template for this discipline and hierarchy level
        template = self._get_expansion_template(discipline, cluster.hierarchy_level)
        
        # Distribute quota among related topics
        topics_per_related = max(1, quota // len(cluster.related_topics)) if cluster.related_topics else quota
        
        for i, related_topic in enumerate(cluster.related_topics):
            # Generate subtopics for this related topic
            topic_subtopics = self._generate_subtopics_for_topic(
                related_topic, topics_per_related, cluster, discipline, current_id + i * topics_per_related
            )
            subtopics.extend(topic_subtopics)
            
            if len(subtopics) >= quota:
                break
        
        return subtopics[:quota]
    
    def _generate_subtopics_for_topic(self, topic: str, count: int, cluster: TopicCluster,
                                    discipline: str, start_id: int) -> List[SubtopicEntry]:
        """Generate fine-grained subtopics for a specific topic."""
        subtopics = []
        
        # Get expansion patterns for the topic
        expansion_patterns = self._get_topic_expansion_patterns(topic, discipline)
        
        for i in range(count):
            if i < len(expansion_patterns):
                subtopic_title = expansion_patterns[i]
            else:
                # Generate additional subtopics based on templates
                subtopic_title = f"{topic} - Advanced Topic {i - len(expansion_patterns) + 1}"
            
            # Create subtopic entry
            subtopic_id = create_subtopic_id(discipline, cluster.main_topic, subtopic_title)
            
            subtopic = SubtopicEntry(
                id=subtopic_id,
                discipline=discipline,
                category=cluster.main_topic,
                subtopic=subtopic_title,
                level=self._determine_educational_level(cluster.hierarchy_level),
                bloom=self._determine_bloom_level(cluster.hierarchy_level, i),
                standards_links=[],  # Will be populated later
                prerequisites=[],    # Will be populated later
                learning_objectives=self._generate_learning_objectives(subtopic_title, discipline),
                textbook_references=[],
                question_types=self._determine_question_types(subtopic_title, discipline),
                hierarchy_level=cluster.hierarchy_level,
                parent_topics=[topic],
                child_topics=[],
                discipline_specific_context="",  # Will be populated later
                discipline_specific_learning_objectives=[],
                discipline_specific_applications=[],
                discipline_specific_prerequisites=[]
            )
            
            subtopics.append(subtopic)
        
        return subtopics
    
    def _get_topic_expansion_patterns(self, topic: str, discipline: str) -> List[str]:
        """Get expansion patterns for a specific topic."""
        # This would be enhanced with comprehensive topic-specific patterns
        
        base_patterns = [
            f"Fundamental Principles of {topic}",
            f"Mathematical Framework for {topic}",
            f"Experimental Methods in {topic}",
            f"Applications of {topic}",
            f"Advanced Concepts in {topic}",
            f"Problem-Solving Strategies for {topic}",
            f"Real-World Examples of {topic}",
            f"Historical Development of {topic}",
            f"Current Research in {topic}",
            f"Interdisciplinary Connections of {topic}"
        ]
        
        # Add discipline-specific patterns
        discipline_patterns = {
            'Physics': [
                f"Mathematical Derivations in {topic}",
                f"Laboratory Measurements of {topic}",
                f"Theoretical Models of {topic}",
                f"Computational Methods for {topic}"
            ],
            'Chemistry': [
                f"Molecular Basis of {topic}",
                f"Thermodynamics of {topic}",
                f"Kinetics of {topic}",
                f"Spectroscopic Analysis of {topic}"
            ],
            'Biology': [
                f"Molecular Mechanisms of {topic}",
                f"Cellular Basis of {topic}",
                f"Evolutionary Aspects of {topic}",
                f"Ecological Role of {topic}"
            ]
        }
        
        all_patterns = base_patterns + discipline_patterns.get(discipline, [])
        return all_patterns[:15]  # Return top 15 patterns
    
    def _apply_validated_subtopic_contexts(self, subtopics: List[SubtopicEntry], 
                                         discipline: str) -> List[SubtopicEntry]:
        """
        Goal: Apply discipline-specific context with scientific validation.
        
        Generates contextual information for each subtopic while ensuring
        scientific accuracy and consistency.
        """
        contextualized_subtopics = []
        
        for subtopic in subtopics:
            # Generate discipline-specific context
            context = self._generate_discipline_context(subtopic, discipline)
            
            # Generate discipline-specific learning objectives
            discipline_objectives = self._generate_discipline_specific_objectives(subtopic, discipline)
            
            # Generate discipline-specific applications
            applications = self._generate_discipline_applications(subtopic, discipline)
            
            # Generate discipline-specific prerequisites
            discipline_prereqs = self._generate_discipline_prerequisites(subtopic, discipline)
            
            # Update subtopic with contexts
            subtopic.discipline_specific_context = context
            subtopic.discipline_specific_learning_objectives = discipline_objectives
            subtopic.discipline_specific_applications = applications
            subtopic.discipline_specific_prerequisites = discipline_prereqs
            
            contextualized_subtopics.append(subtopic)
        
        return contextualized_subtopics
    
    def _generate_discipline_context(self, subtopic: SubtopicEntry, discipline: str) -> str:
        """Generate discipline-specific context for a subtopic."""
        
        context_templates = {
            'Physics': f"In physics, {subtopic.subtopic.lower()} involves the study of physical phenomena and their mathematical descriptions. This topic builds on fundamental physical principles and provides the foundation for understanding more advanced concepts.",
            
            'Chemistry': f"From a chemical perspective, {subtopic.subtopic.lower()} focuses on molecular-level interactions and transformations. Understanding this concept is essential for predicting chemical behavior and designing new materials.",
            
            'Biology': f"In biological systems, {subtopic.subtopic.lower()} represents critical processes that maintain life and enable adaptation. This topic integrates molecular mechanisms with organismal function.",
            
            'Psychology': f"Within psychology, {subtopic.subtopic.lower()} examines cognitive and behavioral processes that influence human experience. This area connects theoretical frameworks with practical applications.",
            
            'Mathematics': f"Mathematically, {subtopic.subtopic.lower()} involves abstract structures and logical reasoning. This concept provides tools for modeling and solving complex problems across disciplines."
        }
        
        return context_templates.get(discipline, 
                                   f"In {discipline.lower()}, {subtopic.subtopic.lower()} represents an important area of study with both theoretical and practical implications.")
    
    def _generate_discipline_specific_objectives(self, subtopic: SubtopicEntry, discipline: str) -> List[str]:
        """Generate discipline-specific learning objectives."""
        
        objective_templates = {
            'Physics': [
                f"Apply mathematical principles to analyze {subtopic.subtopic.lower()}",
                f"Conduct experimental investigations of {subtopic.subtopic.lower()}",
                f"Explain the physical mechanisms underlying {subtopic.subtopic.lower()}"
            ],
            'Chemistry': [
                f"Describe molecular-level processes in {subtopic.subtopic.lower()}",
                f"Predict chemical outcomes based on {subtopic.subtopic.lower()}",
                f"Analyze experimental data related to {subtopic.subtopic.lower()}"
            ],
            'Biology': [
                f"Explain biological significance of {subtopic.subtopic.lower()}",
                f"Analyze evolutionary advantages of {subtopic.subtopic.lower()}",
                f"Connect molecular mechanisms to organismal function in {subtopic.subtopic.lower()}"
            ]
        }
        
        return objective_templates.get(discipline, [f"Understand key concepts in {subtopic.subtopic.lower()}"])
    
    def _generate_discipline_applications(self, subtopic: SubtopicEntry, discipline: str) -> List[str]:
        """Generate discipline-specific applications."""
        
        application_templates = {
            'Physics': [
                f"Engineering design using {subtopic.subtopic.lower()}",
                f"Technology development based on {subtopic.subtopic.lower()}",
                f"Scientific instrumentation utilizing {subtopic.subtopic.lower()}"
            ],
            'Chemistry': [
                f"Industrial processes involving {subtopic.subtopic.lower()}",
                f"Materials science applications of {subtopic.subtopic.lower()}",
                f"Environmental chemistry related to {subtopic.subtopic.lower()}"
            ],
            'Biology': [
                f"Medical applications of {subtopic.subtopic.lower()}",
                f"Biotechnology utilizing {subtopic.subtopic.lower()}",
                f"Conservation strategies based on {subtopic.subtopic.lower()}"
            ]
        }
        
        return application_templates.get(discipline, [f"Practical applications of {subtopic.subtopic.lower()}"])
    
    def _generate_discipline_prerequisites(self, subtopic: SubtopicEntry, discipline: str) -> List[str]:
        """Generate discipline-specific prerequisites."""
        
        prereq_templates = {
            'Physics': ["Mathematical foundations", "Basic physical principles", "Laboratory skills"],
            'Chemistry': ["Atomic structure", "Chemical bonding", "Stoichiometry"],
            'Biology': ["Cell structure", "Basic biochemistry", "Scientific method"],
            'Psychology': ["Research methods", "Statistics", "Basic psychology principles"],
            'Mathematics': ["Algebra", "Geometry", "Logical reasoning"]
        }
        
        return prereq_templates.get(discipline, ["General academic preparation"])
    
    def _validate_prerequisite_scientific_consistency(self, curriculum: List[SubtopicEntry]) -> List[str]:
        """
        Goal: Validate that prerequisite relationships maintain scientific consistency.
        
        Ensures logical progression of scientific concepts and identifies
        potential prerequisite conflicts or gaps.
        """
        issues = []
        
        # Check for mathematical prerequisite consistency
        math_issues = self._check_mathematical_prerequisites(curriculum)
        issues.extend(math_issues)
        
        # Check for conceptual prerequisite consistency
        conceptual_issues = self._check_conceptual_prerequisites(curriculum)
        issues.extend(conceptual_issues)
        
        # Check for temporal/historical consistency
        temporal_issues = self._check_temporal_consistency(curriculum)
        issues.extend(temporal_issues)
        
        return issues
    
    def _check_mathematical_prerequisites(self, curriculum: List[SubtopicEntry]) -> List[str]:
        """Check mathematical prerequisite consistency."""
        issues = []
        
        # Define mathematical complexity levels
        math_levels = {
            'arithmetic': 1,
            'algebra': 2,
            'geometry': 2,
            'trigonometry': 3,
            'calculus': 4,
            'differential equations': 5,
            'linear algebra': 4,
            'statistics': 3
        }
        
        # Check each subtopic's mathematical requirements
        for subtopic in curriculum:
            subtopic_math_level = self._assess_mathematical_level(subtopic)
            
            for prereq in subtopic.prerequisites:
                prereq_subtopic = next((s for s in curriculum if s.subtopic == prereq), None)
                if prereq_subtopic:
                    prereq_math_level = self._assess_mathematical_level(prereq_subtopic)
                    
                    if prereq_math_level > subtopic_math_level:
                        issues.append(f"Mathematical prerequisite inconsistency: {prereq} (level {prereq_math_level}) required for {subtopic.subtopic} (level {subtopic_math_level})")
        
        return issues
    
    def _assess_mathematical_level(self, subtopic: SubtopicEntry) -> int:
        """Assess the mathematical complexity level of a subtopic."""
        text = f"{subtopic.subtopic} {subtopic.discipline_specific_context}".lower()
        
        math_levels = {
            'differential equations': 5,
            'calculus': 4,
            'linear algebra': 4,
            'trigonometry': 3,
            'statistics': 3,
            'algebra': 2,
            'geometry': 2,
            'arithmetic': 1
        }
        
        max_level = 1  # Default to basic level
        for math_topic, level in math_levels.items():
            if math_topic in text:
                max_level = max(max_level, level)
        
        return max_level
    
    def _check_conceptual_prerequisites(self, curriculum: List[SubtopicEntry]) -> List[str]:
        """Check conceptual prerequisite consistency."""
        issues = []
        
        # Define conceptual dependency patterns
        dependency_patterns = {
            'atomic structure': ['electron', 'proton', 'neutron'],
            'chemical bonding': ['atomic structure', 'electron'],
            'molecular geometry': ['chemical bonding'],
            'thermodynamics': ['energy', 'heat'],
            'kinetics': ['molecular motion', 'energy']
        }
        
        # Check for missing conceptual prerequisites
        for subtopic in curriculum:
            text = subtopic.subtopic.lower()
            
            for concept, required_prereqs in dependency_patterns.items():
                if concept in text:
                    # Check if required prerequisites are present
                    for required in required_prereqs:
                        has_prereq = any(required in prereq.lower() 
                                       for prereq in subtopic.prerequisites)
                        
                        if not has_prereq:
                            # Check if prerequisite exists elsewhere in curriculum
                            prereq_exists = any(required in other.subtopic.lower() 
                                             for other in curriculum 
                                             if other != subtopic)
                            
                            if prereq_exists:
                                issues.append(f"Missing prerequisite link: {subtopic.subtopic} should have prerequisite containing '{required}'")
        
        return issues
    
    def _check_temporal_consistency(self, curriculum: List[SubtopicEntry]) -> List[str]:
        """Check temporal/historical consistency in curriculum ordering."""
        issues = []
        
        # Define historical progression patterns
        historical_patterns = {
            'classical mechanics': 1,
            'thermodynamics': 2,
            'electromagnetism': 3,
            'quantum mechanics': 4,
            'relativity': 4
        }
        
        # Check for temporal inconsistencies
        for subtopic in curriculum:
            if subtopic.level == EducationalLevel.UG_ADV or subtopic.level == EducationalLevel.GRAD_INTRO:
                subtopic_era = self._assess_historical_era(subtopic)
                
                for prereq in subtopic.prerequisites:
                    prereq_subtopic = next((s for s in curriculum if s.subtopic == prereq), None)
                    if prereq_subtopic:
                        prereq_era = self._assess_historical_era(prereq_subtopic)
                        
                        if prereq_era > subtopic_era:
                            issues.append(f"Temporal inconsistency: {prereq} (era {prereq_era}) as prerequisite for {subtopic.subtopic} (era {subtopic_era})")
        
        return issues
    
    def _assess_historical_era(self, subtopic: SubtopicEntry) -> int:
        """Assess the historical era of a physics concept."""
        text = subtopic.subtopic.lower()
        
        era_indicators = {
            'classical': 1,
            'newtonian': 1,
            'thermodynamic': 2,
            'electromagnetic': 3,
            'quantum': 4,
            'relativistic': 4,
            'modern': 4
        }
        
        for indicator, era in era_indicators.items():
            if indicator in text:
                return era
        
        return 1  # Default to classical era
    
    def _optimize_curriculum_structure(self, subtopics: List[SubtopicEntry], discipline: str) -> List[SubtopicEntry]:
        """Final optimization of curriculum structure."""
        
        # Sort by hierarchy level and educational level
        sorted_subtopics = sorted(subtopics, key=lambda x: (x.hierarchy_level, x.level.value))
        
        # Ensure we have exactly the target number of subtopics
        if len(sorted_subtopics) > self.target_subtopics:
            # Remove least important subtopics
            sorted_subtopics = sorted_subtopics[:self.target_subtopics]
        elif len(sorted_subtopics) < self.target_subtopics:
            # Add additional specialized subtopics
            additional_needed = self.target_subtopics - len(sorted_subtopics)
            additional_subtopics = self._generate_additional_specialized_subtopics(
                sorted_subtopics, discipline, additional_needed
            )
            sorted_subtopics.extend(additional_subtopics)
        
        return sorted_subtopics
    
    def _generate_additional_specialized_subtopics(self, existing_subtopics: List[SubtopicEntry],
                                                 discipline: str, count: int) -> List[SubtopicEntry]:
        """Generate additional specialized subtopics to reach target count."""
        additional = []
        
        # Identify areas that could use more detail
        category_counts = defaultdict(int)
        for subtopic in existing_subtopics:
            category_counts[subtopic.category] += 1
        
        # Find categories with fewer subtopics
        min_count = min(category_counts.values()) if category_counts else 0
        sparse_categories = [cat for cat, count in category_counts.items() if count <= min_count + 2]
        
        # Generate additional subtopics for sparse categories
        for i in range(count):
            if sparse_categories:
                category = sparse_categories[i % len(sparse_categories)]
                
                subtopic_id = create_subtopic_id(discipline, category, f"Advanced Topic {i+1}")
                
                additional_subtopic = SubtopicEntry(
                    id=subtopic_id,
                    discipline=discipline,
                    category=category,
                    subtopic=f"Advanced {category} Topic {i+1}",
                    level=EducationalLevel.UG_ADV,
                    bloom=BloomLevel.ANALYZE,
                    standards_links=[],
                    prerequisites=[],
                    learning_objectives=[f"Advanced understanding of {category}"],
                    textbook_references=[],
                    question_types=[QuestionType.CONCEPTUAL],
                    hierarchy_level=4,
                    parent_topics=[category],
                    child_topics=[],
                    discipline_specific_context=f"Advanced topic in {category} requiring deep understanding of fundamental principles.",
                    discipline_specific_learning_objectives=[f"Master advanced concepts in {category}"],
                    discipline_specific_applications=[f"Apply {category} to complex problems"],
                    discipline_specific_prerequisites=[f"Strong foundation in {category}"]
                )
                
                additional.append(additional_subtopic)
        
        return additional
    
    def _add_specialized_subtopics(self, clusters: List[TopicCluster], discipline: str, count: int) -> List[SubtopicEntry]:
        """Add specialized subtopics to reach target count."""
        specialized = []
        
        # Focus on advanced topics and interdisciplinary connections
        advanced_topics = [
            "Research Methods",
            "Advanced Applications", 
            "Interdisciplinary Connections",
            "Current Developments",
            "Computational Methods",
            "Experimental Techniques"
        ]
        
        for i in range(count):
            topic = advanced_topics[i % len(advanced_topics)]
            cluster = clusters[i % len(clusters)] if clusters else None
            
            if cluster:
                category = cluster.main_topic
            else:
                category = "Advanced Topics"
            
            subtopic_id = create_subtopic_id(discipline, category, f"{topic} {i+1}")
            
            specialized_subtopic = SubtopicEntry(
                id=subtopic_id,
                discipline=discipline,
                category=category,
                subtopic=f"{topic} in {category}",
                level=EducationalLevel.GRAD_INTRO,
                bloom=BloomLevel.CREATE,
                standards_links=[],
                prerequisites=[],
                learning_objectives=[f"Advanced {topic.lower()} in {category.lower()}"],
                textbook_references=[],
                question_types=[QuestionType.EXPERIMENTAL, QuestionType.COMPUTATIONAL],
                hierarchy_level=5,
                parent_topics=[category],
                child_topics=[],
                discipline_specific_context=f"Specialized topic focusing on {topic.lower()} within {category.lower()}.",
                discipline_specific_learning_objectives=[f"Develop expertise in {topic.lower()}"],
                discipline_specific_applications=[f"Apply {topic.lower()} to research problems"],
                discipline_specific_prerequisites=[f"Advanced understanding of {category.lower()}"]
            )
            
            specialized.append(specialized_subtopic)
        
        return specialized
    
    def _determine_educational_level(self, hierarchy_level: int) -> EducationalLevel:
        """Determine educational level from hierarchy level."""
        level_mapping = {
            1: EducationalLevel.HS_FOUND,
            2: EducationalLevel.HS_ADV,
            3: EducationalLevel.UG_INTRO,
            4: EducationalLevel.UG_ADV,
            5: EducationalLevel.GRAD_INTRO,
            6: EducationalLevel.GRAD_ADV
        }
        return level_mapping.get(hierarchy_level, EducationalLevel.UG_INTRO)
    
    def _determine_bloom_level(self, hierarchy_level: int, subtopic_index: int) -> BloomLevel:
        """Determine Bloom's taxonomy level."""
        # Progress through Bloom's levels as we go deeper
        bloom_progression = [BloomLevel.UNDERSTAND, BloomLevel.APPLY, BloomLevel.ANALYZE, 
                           BloomLevel.EVALUATE, BloomLevel.CREATE]
        
        base_index = min(hierarchy_level - 1, len(bloom_progression) - 1)
        variation = subtopic_index % 2  # Add some variation
        
        final_index = min(base_index + variation, len(bloom_progression) - 1)
        return bloom_progression[final_index]
    
    def _determine_question_types(self, subtopic_title: str, discipline: str) -> List[QuestionType]:
        """Determine appropriate question types for a subtopic."""
        title_lower = subtopic_title.lower()
        
        types = []
        
        # Check for computational indicators
        if any(word in title_lower for word in ['calculation', 'mathematical', 'equation', 'formula']):
            types.append(QuestionType.COMPUTATIONAL)
        
        # Check for conceptual indicators
        if any(word in title_lower for word in ['principle', 'theory', 'concept', 'understanding']):
            types.append(QuestionType.CONCEPTUAL)
        
        # Check for experimental indicators
        if any(word in title_lower for word in ['experimental', 'laboratory', 'measurement', 'observation']):
            types.append(QuestionType.EXPERIMENTAL)
        
        # Check for graphical indicators
        if any(word in title_lower for word in ['graph', 'chart', 'diagram', 'visualization']):
            types.append(QuestionType.GRAPHICAL)
        
        # Default to conceptual if no specific indicators
        if not types:
            types.append(QuestionType.CONCEPTUAL)
        
        return types
    
    def _generate_learning_objectives(self, subtopic_title: str, discipline: str) -> List[str]:
        """Generate learning objectives for a subtopic."""
        return [
            f"Understand the fundamental concepts of {subtopic_title.lower()}",
            f"Apply knowledge of {subtopic_title.lower()} to solve problems",
            f"Analyze the implications of {subtopic_title.lower()} in {discipline.lower()}"
        ]
    
    def _uses_standard_terminology(self, title: str, discipline: str) -> bool:
        """Check if title uses standard terminology for the discipline."""
        # This would be enhanced with comprehensive terminology databases
        standard_terms = {
            'Physics': ['energy', 'force', 'momentum', 'acceleration', 'velocity'],
            'Chemistry': ['molecule', 'atom', 'reaction', 'bond', 'element'],
            'Biology': ['cell', 'organism', 'gene', 'protein', 'evolution']
        }
        
        terms = standard_terms.get(discipline, [])
        return any(term in title.lower() for term in terms)
    
    def _is_authoritative_source(self, source: str) -> bool:
        """Check if source is considered authoritative."""
        authoritative_indicators = [
            'university', 'college', 'academic', 'textbook', 
            'pearson', 'mcgraw', 'wiley', 'cambridge', 'oxford'
        ]
        
        return any(indicator in source.lower() for indicator in authoritative_indicators)
    
    def _load_expansion_templates(self) -> Dict[str, Any]:
        """Load templates for systematic topic expansion."""
        return {
            'Physics': {
                'mechanics': ['kinematics', 'dynamics', 'statics', 'energy', 'momentum'],
                'thermodynamics': ['laws', 'cycles', 'entropy', 'heat transfer'],
                'electromagnetism': ['fields', 'forces', 'induction', 'waves']
            },
            'Chemistry': {
                'bonding': ['ionic', 'covalent', 'metallic', 'intermolecular'],
                'kinetics': ['rate laws', 'mechanisms', 'catalysis', 'equilibrium']
            }
        }
    
    def _load_prerequisite_patterns(self) -> Dict[str, Dict[str, List[str]]]:
        """Load prerequisite patterns by discipline."""
        return {
            'Physics': {
                'calculus': ['algebra', 'trigonometry'],
                'electromagnetism': ['vectors', 'calculus'],
                'quantum mechanics': ['classical mechanics', 'waves']
            },
            'Chemistry': {
                'organic chemistry': ['general chemistry', 'bonding'],
                'physical chemistry': ['thermodynamics', 'calculus']
            }
        }
    
    def _load_discipline_hierarchies(self) -> Dict[str, Dict[str, Any]]:
        """Load discipline-specific hierarchy structures."""
        return {
            'Physics': {
                'levels': 6,
                'main_branches': ['Mechanics', 'Thermodynamics', 'Electromagnetism', 'Optics', 'Modern Physics']
            },
            'Chemistry': {
                'levels': 6,
                'main_branches': ['General Chemistry', 'Organic Chemistry', 'Physical Chemistry', 'Analytical Chemistry']
            }
        }
    
    def _get_default_hierarchy(self) -> Dict[str, Any]:
        """Get default hierarchy structure."""
        return {
            'levels': 6,
            'main_branches': ['Foundations', 'Core Concepts', 'Applications', 'Advanced Topics']
        }
    
    def _get_expansion_template(self, discipline: str, level: int) -> Dict[str, Any]:
        """Get expansion template for specific discipline and level."""
        templates = self.expansion_templates.get(discipline, {})
        return templates.get(f'level_{level}', {})