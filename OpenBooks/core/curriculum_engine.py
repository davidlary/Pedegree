"""
core/curriculum_engine.py - Reusable Curriculum Generation Engine

Goal: Provide a comprehensive, reusable curriculum generation engine that can be used
across different educational contexts and content sources.

This module encapsulates the core curriculum generation logic in a clean, modular way
that can be easily integrated into various educational applications.
"""

import asyncio
import logging
import re
from collections import defaultdict, Counter
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any, Union

import networkx as nx
import pandas as pd

from .educational_standards import EducationalStandardsManager
from .text_extractor import TextExtractor
from .search_indexer import SearchIndexer


@dataclass
class CurriculumConcept:
    """
    Represents a single curriculum concept with complete educational metadata.
    
    This is the fundamental building block of a curriculum, containing all necessary
    information for educational planning, sequencing, and assessment.
    """
    
    # Core identification
    concept_id: str
    title: str
    description: str
    category: str  # Main subject category (e.g., "Classical Mechanics")
    subtopic: str  # Specific subtopic area (e.g., "Newton's Laws")
    
    # Educational classification
    level: str  # HS-Found, HS-Adv, UG-Intro, UG-Adv, Grad-Intro, Grad-Adv
    bloom_taxonomy: str  # Understand, Apply, Analyze, Evaluate, Create
    standards: str  # Standards/exam codes (Intro-Core, Advanced-Core, MCAT, etc.)
    
    # Learning structure
    prerequisites: List[str] = field(default_factory=list)
    learning_objectives: List[str] = field(default_factory=list)
    difficulty_score: float = 0.0  # 0-10 scale
    estimated_hours: float = 1.0
    
    # Content references
    source_books: List[str] = field(default_factory=list)
    source_chapters: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for export and serialization."""
        data = {
            'concept_id': self.concept_id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'subtopic': self.subtopic,
            'level': self.level,
            'bloom_taxonomy': self.bloom_taxonomy,
            'standards': self.standards,
            'prerequisites': self.prerequisites,
            'learning_objectives': self.learning_objectives,
            'difficulty_score': self.difficulty_score,
            'estimated_hours': self.estimated_hours,
            'source_books': self.source_books,
            'source_chapters': self.source_chapters,
            'keywords': self.keywords,
            'created_at': self.created_at.isoformat()
        }
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CurriculumConcept':
        """Create concept from dictionary data."""
        data = data.copy()
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        return cls(**data)


@dataclass
class DisciplineCurriculum:
    """
    Complete curriculum for a discipline with all educational artifacts.
    
    Contains the full set of concepts, their relationships, and metadata
    needed for comprehensive curriculum delivery and analysis.
    """
    
    discipline: str
    concepts: List[CurriculumConcept] = field(default_factory=list)
    prerequisite_graph: nx.DiGraph = field(default_factory=nx.DiGraph)
    category_counts: Dict[str, Dict[str, int]] = field(default_factory=dict)
    exam_standards: Set[str] = field(default_factory=set)
    total_concepts: int = 0
    generation_time: datetime = field(default_factory=datetime.now)
    
    def add_concept(self, concept: CurriculumConcept):
        """Add a concept to the curriculum and update statistics."""
        self.concepts.append(concept)
        self.total_concepts += 1
        
        # Update category counts
        if concept.category not in self.category_counts:
            self.category_counts[concept.category] = defaultdict(int)
        self.category_counts[concept.category][concept.level] += 1
        
        # Track exam standards
        if concept.standards and concept.standards not in ['Intro-Core', 'Advanced-Core']:
            self.exam_standards.add(concept.standards)
    
    def get_concepts_by_category(self, category: str) -> List[CurriculumConcept]:
        """Get all concepts in a specific category."""
        return [c for c in self.concepts if c.category == category]
    
    def get_concepts_by_level(self, level: str) -> List[CurriculumConcept]:
        """Get all concepts at a specific educational level."""
        return [c for c in self.concepts if c.level == level]
    
    def get_prerequisite_tree(self, concept_id: str) -> List[str]:
        """Get all prerequisites for a concept (transitive closure)."""
        if concept_id not in self.prerequisite_graph:
            return []
        
        # Get all predecessors (prerequisites) in topological order
        try:
            subgraph = nx.ancestors(self.prerequisite_graph, concept_id)
            subgraph.add(concept_id)
            return list(nx.topological_sort(self.prerequisite_graph.subgraph(subgraph)))
        except nx.NetworkXError:
            return []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert curriculum to dictionary for export."""
        return {
            'discipline': self.discipline,
            'concepts': [c.to_dict() for c in self.concepts],
            'prerequisite_edges': list(self.prerequisite_graph.edges()),
            'category_counts': {cat: dict(counts) for cat, counts in self.category_counts.items()},
            'exam_standards': list(self.exam_standards),
            'total_concepts': self.total_concepts,
            'generation_time': self.generation_time.isoformat()
        }


class CurriculumEngine:
    """
    Core curriculum generation engine that transforms educational content into
    structured, pedagogically-sound curricula.
    
    This engine handles the complete pipeline from content discovery to curriculum
    delivery, with support for multiple disciplines and educational levels.
    """
    
    def __init__(self, 
                 text_extractor: Optional[TextExtractor] = None,
                 search_indexer: Optional[SearchIndexer] = None,
                 standards_manager: Optional[EducationalStandardsManager] = None,
                 logger: Optional[logging.Logger] = None):
        """
        Initialize the curriculum engine with optional dependencies.
        
        Args:
            text_extractor: Content extraction system
            search_indexer: Content search and analysis system
            standards_manager: Educational standards and assessment system
            logger: Logging system
        """
        
        self.text_extractor = text_extractor or TextExtractor()
        self.search_indexer = search_indexer or SearchIndexer()
        self.standards_manager = standards_manager or EducationalStandardsManager()
        self.logger = logger or logging.getLogger(__name__)
        
        # Educational level progression mapping
        self.level_progression = {
            'HighSchool': ['HS-Found', 'HS-Adv'],
            'University': ['UG-Intro', 'UG-Adv'], 
            'Graduate': ['Grad-Intro', 'Grad-Adv']
        }
        
        # Bloom's taxonomy mapping by educational level
        self.bloom_mapping = {
            'HS-Found': 'Understand',
            'HS-Adv': 'Apply', 
            'UG-Intro': 'Analyze',
            'UG-Adv': 'Evaluate',
            'Grad-Intro': 'Create',
            'Grad-Adv': 'Create'
        }
    
    async def generate_curriculum(self, 
                                discipline: str,
                                content_sources: List[Path],
                                target_size: int = 1000,
                                include_prerequisites: bool = True,
                                include_assessments: bool = True) -> DisciplineCurriculum:
        """
        Generate a complete curriculum for a discipline from content sources.
        
        Args:
            discipline: Name of the academic discipline
            content_sources: List of paths to educational content
            target_size: Target number of concepts in final curriculum
            include_prerequisites: Whether to build prerequisite relationships
            include_assessments: Whether to include assessment alignment
        
        Returns:
            Complete curriculum with concepts, prerequisites, and metadata
        """
        
        self.logger.info(f"Generating curriculum for {discipline} from {len(content_sources)} sources")
        
        # Step 1: Extract content from all sources
        extracted_content = await self._extract_content_from_sources(content_sources)
        
        # Step 2: Generate initial concepts from content
        initial_concepts = await self._generate_concepts_from_content(
            discipline, extracted_content
        )
        
        # Step 3: Augment with domain-specific concepts
        augmented_concepts = await self._augment_concepts_with_domain_knowledge(
            discipline, initial_concepts, target_size
        )
        
        # Step 4: Build prerequisite relationships
        prerequisite_graph = nx.DiGraph()
        if include_prerequisites:
            prerequisite_graph = self._build_prerequisite_graph(discipline, augmented_concepts)
        
        # Step 5: Sort concepts topologically
        sorted_concepts = self._sort_concepts_by_prerequisites(augmented_concepts, prerequisite_graph)
        
        # Step 6: Assign educational metadata
        final_concepts = self._assign_educational_metadata(
            discipline, sorted_concepts, include_assessments
        )
        
        # Step 7: Build final curriculum
        curriculum = DisciplineCurriculum(discipline=discipline)
        curriculum.prerequisite_graph = prerequisite_graph
        
        for concept in final_concepts:
            curriculum.add_concept(concept)
        
        self.logger.info(f"Generated curriculum with {curriculum.total_concepts} concepts")
        
        return curriculum
    
    async def _extract_content_from_sources(self, sources: List[Path]) -> Dict[str, Any]:
        """Extract structured content from multiple sources."""
        
        content = {
            'headings': [],
            'chapters': [],
            'sections': [],
            'metadata': []
        }
        
        for source_path in sources:
            if source_path.is_file():
                # Extract from individual file
                file_content = await self._extract_from_file(source_path)
                content['headings'].extend(file_content.get('headings', []))
                content['chapters'].extend(file_content.get('chapters', []))
                content['sections'].extend(file_content.get('sections', []))
                
            elif source_path.is_dir():
                # Extract from directory recursively
                dir_content = await self._extract_from_directory(source_path)
                content['headings'].extend(dir_content.get('headings', []))
                content['chapters'].extend(dir_content.get('chapters', []))
                content['sections'].extend(dir_content.get('sections', []))
        
        # Deduplicate content
        content = self._deduplicate_content(content)
        
        return content
    
    async def _extract_from_file(self, file_path: Path) -> Dict[str, Any]:
        """Extract content from a single file."""
        
        try:
            extracted = self.text_extractor.extract_content(str(file_path))
            
            if not extracted:
                return {'headings': [], 'chapters': [], 'sections': []}
            
            content = {'headings': [], 'chapters': [], 'sections': []}
            
            # Process chapters and sections
            if hasattr(extracted, 'chapters') and extracted.chapters:
                for chapter in extracted.chapters:
                    chapter_title = chapter.get('title', '')
                    if chapter_title:
                        content['chapters'].append(chapter_title)
                        content['headings'].append({
                            'title': chapter_title,
                            'level': 1,
                            'source': str(file_path)
                        })
                        
                        # Process sections within chapter
                        if 'sections' in chapter:
                            for section in chapter['sections']:
                                section_title = section.get('title', '')
                                if section_title:
                                    content['sections'].append(section_title)
                                    content['headings'].append({
                                        'title': section_title,
                                        'level': 2,
                                        'source': str(file_path)
                                    })
            
            return content
            
        except Exception as e:
            self.logger.warning(f"Could not extract from {file_path}: {e}")
            return {'headings': [], 'chapters': [], 'sections': []}
    
    async def _extract_from_directory(self, dir_path: Path) -> Dict[str, Any]:
        """Extract content from all files in a directory."""
        
        content = {'headings': [], 'chapters': [], 'sections': []}
        
        # Process all relevant files
        for file_path in dir_path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in ['.pdf', '.xml', '.cnxml', '.md', '.rst', '.tex']:
                file_content = await self._extract_from_file(file_path)
                content['headings'].extend(file_content.get('headings', []))
                content['chapters'].extend(file_content.get('chapters', []))
                content['sections'].extend(file_content.get('sections', []))
        
        return content
    
    def _deduplicate_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Remove duplicate content using fuzzy matching."""
        
        # Deduplicate headings by normalized title
        unique_headings = []
        seen_titles = set()
        
        for heading in content['headings']:
            title_normalized = re.sub(r'[^\w\s]', '', heading['title'].lower()).strip()
            if title_normalized and title_normalized not in seen_titles:
                seen_titles.add(title_normalized)
                unique_headings.append(heading)
        
        content['headings'] = unique_headings
        content['chapters'] = list(set(content['chapters']))
        content['sections'] = list(set(content['sections']))
        
        return content
    
    async def _generate_concepts_from_content(self, 
                                            discipline: str, 
                                            content: Dict[str, Any]) -> List[CurriculumConcept]:
        """Generate curriculum concepts from extracted content."""
        
        concepts = []
        concept_id = 1
        
        for heading in content['headings']:
            concept = CurriculumConcept(
                concept_id=f"{discipline.lower()}_{concept_id:04d}",
                title=heading['title'],
                description=f"Core concept in {discipline}: {heading['title']}",
                category=self._categorize_concept(discipline, heading['title']),
                subtopic=self._extract_subtopic(heading['title']),
                level='UG-Intro',  # Will be refined later
                bloom_taxonomy='',  # Will be assigned later
                standards='',  # Will be assigned later
                source_books=[heading.get('source', '')],
                keywords=self._extract_keywords(heading['title'])
            )
            concepts.append(concept)
            concept_id += 1
        
        return concepts
    
    def _categorize_concept(self, discipline: str, title: str) -> str:
        """Categorize a concept based on discipline and title content."""
        
        # Use the standards manager to get discipline-specific categorization
        return self.standards_manager.categorize_concept(discipline, title)
    
    def _extract_subtopic(self, title: str) -> str:
        """Extract specific subtopic from concept title."""
        
        # Remove common prefixes and suffixes
        cleaned = re.sub(r'^(chapter|section|lesson|topic|unit)\s*\d*[:\.\-\s]*', '', title, flags=re.IGNORECASE)
        cleaned = re.sub(r'\s*(introduction|intro|overview|summary|conclusion)$', '', cleaned, flags=re.IGNORECASE)
        
        return cleaned.strip() or title
    
    def _extract_keywords(self, title: str) -> List[str]:
        """Extract relevant keywords from concept title."""
        
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'introduction', 'chapter', 'section', 'lesson', 'topic', 'overview', 'summary'
        }
        
        words = re.findall(r'\w+', title.lower())
        keywords = [word for word in words if len(word) > 2 and word not in stop_words]
        
        return keywords[:5]  # Limit to top 5 keywords
    
    async def _augment_concepts_with_domain_knowledge(self, 
                                                    discipline: str,
                                                    concepts: List[CurriculumConcept],
                                                    target_size: int) -> List[CurriculumConcept]:
        """Augment concepts with essential domain knowledge to reach target size."""
        
        current_size = len(concepts)
        if current_size >= target_size:
            return concepts[:target_size]
        
        # Get essential concepts from standards manager
        essential_concepts = self.standards_manager.get_essential_concepts(discipline)
        
        # Filter out already covered concepts
        existing_titles = {c.title.lower() for c in concepts}
        new_concepts = []
        concept_id = current_size + 1
        
        for category, concept_list in essential_concepts.items():
            for concept_info in concept_list:
                if concept_info['title'].lower() not in existing_titles:
                    concept = CurriculumConcept(
                        concept_id=f"{discipline.lower()}_{concept_id:04d}",
                        title=concept_info['title'],
                        description=concept_info['description'],
                        category=category,
                        subtopic=concept_info['title'],
                        level=concept_info['level'],
                        difficulty_score=concept_info.get('difficulty', 5.0),
                        estimated_hours=concept_info.get('hours', 1.0),
                        keywords=concept_info.get('keywords', [])
                    )
                    new_concepts.append(concept)
                    concept_id += 1
                    
                    if len(concepts) + len(new_concepts) >= target_size:
                        break
            
            if len(concepts) + len(new_concepts) >= target_size:
                break
        
        return (concepts + new_concepts)[:target_size]
    
    def _build_prerequisite_graph(self, 
                                discipline: str, 
                                concepts: List[CurriculumConcept]) -> nx.DiGraph:
        """Build prerequisite graph using domain knowledge."""
        
        graph = nx.DiGraph()
        
        # Add all concepts as nodes
        for concept in concepts:
            graph.add_node(concept.concept_id, concept=concept)
        
        # Get prerequisite rules from standards manager
        prereq_rules = self.standards_manager.get_prerequisite_rules(discipline)
        
        # Build category mapping
        category_concepts = defaultdict(list)
        for concept in concepts:
            category_concepts[concept.category].append(concept)
        
        # Apply prerequisite rules between categories
        for category, prereq_categories in prereq_rules.items():
            if category in category_concepts:
                target_concepts = category_concepts[category]
                
                for prereq_category in prereq_categories:
                    if prereq_category in category_concepts:
                        prereq_concepts = category_concepts[prereq_category]
                        
                        # Add edges from prerequisites to targets
                        for prereq_concept in prereq_concepts:
                            for target_concept in target_concepts:
                                if self._level_order(prereq_concept.level) <= self._level_order(target_concept.level):
                                    graph.add_edge(prereq_concept.concept_id, target_concept.concept_id)
        
        # Add level-based prerequisites within categories
        for category_concept_list in category_concepts.values():
            sorted_concepts = sorted(category_concept_list, key=lambda c: self._level_order(c.level))
            
            for i in range(1, len(sorted_concepts)):
                prev_concept = sorted_concepts[i-1]
                current_concept = sorted_concepts[i]
                
                if not graph.has_edge(prev_concept.concept_id, current_concept.concept_id):
                    graph.add_edge(prev_concept.concept_id, current_concept.concept_id)
        
        return graph
    
    def _level_order(self, level: str) -> int:
        """Get numeric order for curriculum levels."""
        order_map = {
            'HS-Found': 1,
            'HS-Adv': 2,
            'UG-Intro': 3,
            'UG-Adv': 4,
            'Grad-Intro': 5,
            'Grad-Adv': 6
        }
        return order_map.get(level, 3)
    
    def _sort_concepts_by_prerequisites(self, 
                                      concepts: List[CurriculumConcept],
                                      graph: nx.DiGraph) -> List[CurriculumConcept]:
        """Sort concepts using topological ordering."""
        
        try:
            topo_order = list(nx.topological_sort(graph))
            concept_map = {c.concept_id: c for c in concepts}
            
            sorted_concepts = []
            for concept_id in topo_order:
                if concept_id in concept_map:
                    sorted_concepts.append(concept_map[concept_id])
            
            # Add any concepts not in graph
            for concept in concepts:
                if concept not in sorted_concepts:
                    sorted_concepts.append(concept)
            
            return sorted_concepts
            
        except nx.NetworkXError:
            # Fall back to level-based sorting if cycles exist
            return sorted(concepts, key=lambda c: (self._level_order(c.level), c.category, c.title))
    
    def _assign_educational_metadata(self, 
                                   discipline: str,
                                   concepts: List[CurriculumConcept],
                                   include_assessments: bool = True) -> List[CurriculumConcept]:
        """Assign Bloom's taxonomy, standards, and other educational metadata."""
        
        # Get exam standards for discipline
        exam_standards = self.standards_manager.get_exam_standards(discipline)
        primary_standard = next(iter(exam_standards)) if exam_standards else None
        
        for concept in concepts:
            # Assign Bloom's taxonomy based on level
            concept.bloom_taxonomy = self.bloom_mapping.get(concept.level, 'Understand')
            
            # Assign standards
            if include_assessments:
                if concept.level in ['HS-Found', 'UG-Intro']:
                    concept.standards = 'Intro-Core'
                elif concept.level in ['HS-Adv', 'UG-Adv']:
                    concept.standards = 'Advanced-Core'
                elif primary_standard and concept.level in ['Grad-Intro', 'Grad-Adv']:
                    concept.standards = primary_standard
                else:
                    concept.standards = 'Advanced-Core'
            
            # Refine level assignment based on content
            concept.level = self._refine_level_assignment(concept)
            
            # Update Bloom's taxonomy after level refinement
            concept.bloom_taxonomy = self.bloom_mapping.get(concept.level, concept.bloom_taxonomy)
        
        return concepts
    
    def _refine_level_assignment(self, concept: CurriculumConcept) -> str:
        """Refine level assignment based on concept characteristics."""
        
        title_lower = concept.title.lower()
        
        # Graduate-level indicators
        graduate_keywords = [
            'field theory', 'gauge', 'symmetry', 'topology', 'differential geometry',
            'many-body', 'renormalization', 'scattering theory', 'advanced', 'theoretical'
        ]
        
        # Advanced indicators
        advanced_keywords = [
            'quantum', 'relativistic', 'mathematical', 'nonlinear', 
            'multidimensional', 'stochastic', 'perturbation'
        ]
        
        if any(keyword in title_lower for keyword in graduate_keywords):
            if concept.level.startswith('UG'):
                return 'Grad-Intro'
            elif concept.level.startswith('HS'):
                return 'UG-Adv'
        elif any(keyword in title_lower for keyword in advanced_keywords):
            if concept.level == 'HS-Found':
                return 'HS-Adv'
            elif concept.level == 'UG-Intro':
                return 'UG-Adv'
        
        return concept.level
    
    def get_curriculum_statistics(self, curriculum: DisciplineCurriculum) -> Dict[str, Any]:
        """Generate comprehensive statistics for a curriculum."""
        
        stats = {
            'total_concepts': curriculum.total_concepts,
            'categories': len(curriculum.category_counts),
            'levels': len(set(c.level for c in curriculum.concepts)),
            'prerequisite_relationships': curriculum.prerequisite_graph.number_of_edges(),
            'exam_standards': len(curriculum.exam_standards),
            'average_difficulty': sum(c.difficulty_score for c in curriculum.concepts) / len(curriculum.concepts) if curriculum.concepts else 0,
            'total_hours': sum(c.estimated_hours for c in curriculum.concepts),
            'level_distribution': Counter(c.level for c in curriculum.concepts),
            'bloom_distribution': Counter(c.bloom_taxonomy for c in curriculum.concepts),
            'category_distribution': Counter(c.category for c in curriculum.concepts)
        }
        
        return stats
    
    def validate_curriculum(self, curriculum: DisciplineCurriculum) -> Dict[str, Any]:
        """Validate curriculum completeness and consistency."""
        
        validation = {
            'is_valid': True,
            'warnings': [],
            'errors': []
        }
        
        # Check for missing prerequisites
        try:
            nx.topological_sort(curriculum.prerequisite_graph)
        except nx.NetworkXError:
            validation['errors'].append("Circular dependencies detected in prerequisite graph")
            validation['is_valid'] = False
        
        # Check level progression
        for concept in curriculum.concepts:
            if not concept.level:
                validation['warnings'].append(f"Concept {concept.concept_id} missing level assignment")
            
            if not concept.bloom_taxonomy:
                validation['warnings'].append(f"Concept {concept.concept_id} missing Bloom's taxonomy")
        
        # Check category coverage
        if len(curriculum.category_counts) < 3:
            validation['warnings'].append("Curriculum has fewer than 3 categories - may lack breadth")
        
        # Check size appropriateness
        if curriculum.total_concepts < 100:
            validation['warnings'].append("Curriculum has fewer than 100 concepts - may be incomplete")
        elif curriculum.total_concepts > 2000:
            validation['warnings'].append("Curriculum has more than 2000 concepts - may be too detailed")
        
        return validation