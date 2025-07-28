#!/usr/bin/env python3
"""
curriculum_processor.py - Core processing engine for curriculum generation

Handles the detailed processing of textbook content, ontology integration,
and educational metadata enhancement for comprehensive curriculum creation.

Author: Claude Code
License: MIT
"""

import asyncio
import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Tuple
import xml.etree.ElementTree as ET

import networkx as nx
from loguru import logger


@dataclass
class BookReference:
    """Reference to a specific location in a textbook."""
    book_title: str
    book_path: str
    chapter: str
    section: Optional[str] = None
    module_id: Optional[str] = None
    page_range: Optional[str] = None


@dataclass
class LearningObjective:
    """Structured learning objective with Bloom's taxonomy classification."""
    description: str
    bloom_level: str
    cognitive_load: str  # low, medium, high
    assessment_type: str  # formative, summative
    time_estimate: float  # hours


@dataclass
class ConceptMapping:
    """Mapping between curriculum concepts and external ontologies."""
    source_concept_id: str
    target_ontology: str
    target_concept_id: str
    mapping_confidence: float
    mapping_type: str  # exact, broad, narrow, related


class TextbookContentExtractor:
    """Extracts and processes content from OpenStax textbooks."""
    
    def __init__(self, books_directory: Path):
        """Initialize with books directory path."""
        self.books_dir = books_directory
        self.module_cache: Dict[str, Dict[str, Any]] = {}
        
    def extract_discipline_content(self, discipline: str) -> Dict[str, Any]:
        """
        Extract comprehensive content structure for a discipline.
        
        Args:
            discipline: Name of the discipline (e.g., 'Physics', 'Biology')
            
        Returns:
            Structured content data including books, chapters, and modules
        """
        discipline_dir = self.books_dir / discipline / "University"
        if not discipline_dir.exists():
            logger.warning(f"No university-level books found for {discipline}")
            return {'books': [], 'total_modules': 0}
        
        content = {
            'discipline': discipline,
            'books': [],
            'total_modules': 0,
            'total_chapters': 0,
            'extraction_timestamp': datetime.now().isoformat()
        }
        
        # Process each book in the discipline
        for book_dir in discipline_dir.iterdir():
            if not book_dir.is_dir() or book_dir.name.startswith('.'):
                continue
                
            book_content = self._extract_book_content(book_dir)
            if book_content:
                content['books'].append(book_content)
                content['total_modules'] += book_content.get('module_count', 0)
                content['total_chapters'] += len(book_content.get('chapters', []))
        
        logger.info(f"Extracted content for {discipline}: {len(content['books'])} books, "
                   f"{content['total_chapters']} chapters, {content['total_modules']} modules")
        
        return content
    
    def _extract_book_content(self, book_dir: Path) -> Optional[Dict[str, Any]]:
        """Extract content from a single book directory."""
        try:
            # Find collection XML file
            collections_dir = book_dir / "collections"
            if not collections_dir.exists():
                return None
            
            collection_files = list(collections_dir.glob("*.collection.xml"))
            if not collection_files:
                return None
            
            # Parse the first collection file found
            collection_file = collection_files[0]
            return self._parse_collection_xml(collection_file, book_dir)
            
        except Exception as e:
            logger.error(f"Failed to extract content from {book_dir}: {e}")
            return None
    
    def _parse_collection_xml(self, xml_file: Path, book_dir: Path) -> Dict[str, Any]:
        """Parse OpenStax collection XML to extract book structure."""
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            # Extract book metadata
            title_elem = root.find('.//{http://cnx.rice.edu/mdml}title')
            title = title_elem.text if title_elem is not None else xml_file.stem
            
            uuid_elem = root.find('.//{http://cnx.rice.edu/mdml}uuid')
            book_uuid = uuid_elem.text if uuid_elem is not None else ""
            
            book_content = {
                'title': title,
                'uuid': book_uuid,
                'file_path': str(xml_file),
                'book_directory': str(book_dir),
                'chapters': [],
                'module_count': 0,
                'raw_modules': []  # Store individual modules not in chapters
            }
            
            # Extract chapters (subcollections)
            for subcollection in root.findall('.//{http://cnx.rice.edu/collxml}subcollection'):
                chapter = self._parse_chapter(subcollection)
                if chapter:
                    book_content['chapters'].append(chapter)
                    book_content['module_count'] += len(chapter['modules'])
            
            # Extract standalone modules (not in subcollections)
            content_elem = root.find('.//{http://cnx.rice.edu/collxml}content')
            if content_elem is not None:
                # Get all modules in subcollections first to track which ones to skip
                subcollection_modules = set()
                for subcollection in root.findall('.//{http://cnx.rice.edu/collxml}subcollection'):
                    for module_elem in subcollection.findall('.//{http://cnx.rice.edu/collxml}module'):
                        document_id = module_elem.get('document', '')
                        if document_id:
                            subcollection_modules.add(document_id)
                
                # Now process standalone modules (those not in subcollections)
                for module_elem in content_elem.findall('.//{http://cnx.rice.edu/collxml}module'):
                    document_id = module_elem.get('document', '')
                    # Skip modules that are already in subcollections
                    if document_id in subcollection_modules:
                        continue
                    
                    module_data = self._parse_module(module_elem)
                    if module_data:
                        book_content['raw_modules'].append(module_data)
                        book_content['module_count'] += 1
            
            return book_content
            
        except Exception as e:
            logger.error(f"Error parsing {xml_file}: {e}")
            return {}
    
    def _parse_chapter(self, subcollection_elem: ET.Element) -> Optional[Dict[str, Any]]:
        """Parse a chapter (subcollection) from XML."""
        title_elem = subcollection_elem.find('.//{http://cnx.rice.edu/mdml}title')
        chapter_title = title_elem.text if title_elem is not None else "Untitled Chapter"
        
        chapter = {
            'title': chapter_title,
            'modules': [],
            'subcollections': []  # For nested subcollections
        }
        
        # Extract modules in this chapter
        for module_elem in subcollection_elem.findall('.//{http://cnx.rice.edu/collxml}module'):
            module_data = self._parse_module(module_elem)
            if module_data:
                chapter['modules'].append(module_data)
        
        # Extract nested subcollections
        for nested_sub in subcollection_elem.findall('.//{http://cnx.rice.edu/collxml}subcollection'):
            if nested_sub != subcollection_elem:  # Avoid self-reference
                nested_chapter = self._parse_chapter(nested_sub)
                if nested_chapter:
                    chapter['subcollections'].append(nested_chapter)
        
        return chapter if chapter['modules'] or chapter['subcollections'] else None
    
    def _parse_module(self, module_elem: ET.Element) -> Optional[Dict[str, Any]]:
        """Parse a module from XML."""
        document_id = module_elem.get('document', '')
        if not document_id:
            return None
        
        # Try to get module title from the modules directory
        module_title = self._get_module_title(document_id)
        
        return {
            'document_id': document_id,
            'title': module_title,
            'type': 'module'
        }
    
    def _get_module_title(self, document_id: str) -> str:
        """Get module title by looking up the document ID."""
        # This is a simplified implementation
        # In a full implementation, you'd parse the actual module XML files
        # to get the real titles
        
        if document_id in self.module_cache:
            return self.module_cache[document_id].get('title', f"Module {document_id}")
        
        # Default title based on document ID
        return f"Module {document_id}"


class BloomTaxonomyClassifier:
    """Classifies learning content according to Bloom's Taxonomy."""
    
    # Keywords associated with each Bloom's level
    BLOOM_KEYWORDS = {
        'Remember': [
            'define', 'list', 'identify', 'name', 'state', 'describe', 'recall',
            'recognize', 'select', 'match', 'choose', 'label', 'find'
        ],
        'Understand': [
            'explain', 'interpret', 'summarize', 'classify', 'compare', 'contrast',
            'demonstrate', 'illustrate', 'translate', 'paraphrase', 'discuss'
        ],
        'Apply': [
            'apply', 'use', 'implement', 'execute', 'carry out', 'solve',
            'demonstrate', 'operate', 'calculate', 'compute', 'construct'
        ],
        'Analyze': [
            'analyze', 'examine', 'break down', 'differentiate', 'distinguish',
            'compare', 'contrast', 'investigate', 'categorize', 'organize'
        ],
        'Evaluate': [
            'evaluate', 'assess', 'judge', 'critique', 'justify', 'defend',
            'support', 'argue', 'decide', 'rate', 'recommend', 'prioritize'
        ],
        'Create': [
            'create', 'design', 'develop', 'compose', 'construct', 'generate',
            'produce', 'build', 'invent', 'plan', 'formulate', 'synthesize'
        ]
    }
    
    @classmethod
    def classify_content(cls, title: str, description: str, level: int) -> str:
        """
        Classify content according to Bloom's Taxonomy.
        
        Args:
            title: Content title
            description: Content description
            level: Hierarchical level (1-6)
            
        Returns:
            Bloom's taxonomy level
        """
        text = f"{title} {description}".lower()
        
        # Score each Bloom's level based on keyword presence
        scores = {}
        for bloom_level, keywords in cls.BLOOM_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in text)
            scores[bloom_level] = score
        
        # If no keywords found, assign based on hierarchical level
        if all(score == 0 for score in scores.values()):
            return cls._default_bloom_for_level(level)
        
        # Return the highest scoring Bloom's level
        return max(scores, key=scores.get)
    
    @classmethod
    def _default_bloom_for_level(cls, level: int) -> str:
        """Assign default Bloom's level based on hierarchical level."""
        defaults = {
            1: 'Remember',      # Discipline overview
            2: 'Understand',    # Main branches
            3: 'Apply',         # Subtopics
            4: 'Analyze',       # Detailed concepts
            5: 'Evaluate',      # Fine-grained details
            6: 'Create'         # Micro-concepts
        }
        return defaults.get(level, 'Apply')


class ConceptExpander:
    """Generates additional concepts to reach target curriculum size."""
    
    def __init__(self, target_size: int = 1000):
        """Initialize with target curriculum size."""
        self.target_size = target_size
        
        # Templates for generating additional concepts
        self.expansion_templates = {
            'mathematical': [
                'Mathematical formulation of {}',
                'Quantitative analysis of {}',
                'Computational methods for {}',
                'Statistical analysis of {}',
                'Modeling and simulation of {}'
            ],
            'experimental': [
                'Experimental investigation of {}',
                'Laboratory techniques for {}',
                'Measurement and instrumentation in {}',
                'Data collection methods for {}',
                'Error analysis in {}'
            ],
            'theoretical': [
                'Theoretical foundations of {}',
                'Historical development of {}',
                'Underlying principles of {}',
                'Conceptual framework for {}',
                'Theoretical models of {}'
            ],
            'applied': [
                'Practical applications of {}',
                'Industrial applications of {}',
                'Real-world examples of {}',
                'Case studies in {}',
                'Problem-solving with {}'
            ],
            'interdisciplinary': [
                'Connections between {} and other fields',
                'Interdisciplinary aspects of {}',
                'Cross-cutting themes in {}',
                'Integration of {} with technology',
                'Societal implications of {}'
            ]
        }
    
    def expand_curriculum(self, nodes: List, discipline: str) -> List:
        """
        Expand curriculum to reach target size.
        
        Args:
            nodes: Current curriculum nodes
            discipline: Discipline name
            
        Returns:
            Expanded list of curriculum nodes
        """
        current_size = len(nodes)
        
        if current_size >= self.target_size:
            logger.info(f"Curriculum already meets target size: {current_size} >= {self.target_size}")
            return nodes
        
        expansion_needed = self.target_size - current_size
        logger.info(f"Expanding {discipline} curriculum from {current_size} to {self.target_size} concepts")
        
        # Find nodes suitable for expansion (levels 4-5)
        expandable_nodes = [n for n in nodes if hasattr(n, 'level') and n.level in [4, 5]]
        
        if not expandable_nodes:
            logger.warning(f"No expandable nodes found for {discipline}")
            return nodes
        
        additional_nodes = []
        concepts_per_node = max(1, expansion_needed // len(expandable_nodes))
        
        for parent_node in expandable_nodes:
            if len(additional_nodes) >= expansion_needed:
                break
            
            # Generate additional concepts for this parent
            new_concepts = self._generate_additional_concepts(
                parent_node, concepts_per_node, discipline
            )
            additional_nodes.extend(new_concepts)
            
            # Update parent's children list
            if hasattr(parent_node, 'children_ids'):
                parent_node.children_ids.extend([concept.id for concept in new_concepts])
        
        logger.info(f"Generated {len(additional_nodes)} additional concepts for {discipline}")
        return nodes + additional_nodes
    
    def _generate_additional_concepts(self, parent_node, count: int, discipline: str) -> List:
        """Generate additional concepts for a parent node."""
        from curricula import CurriculumNode  # Import here to avoid circular import
        
        additional_concepts = []
        
        # Cycle through different expansion categories
        categories = list(self.expansion_templates.keys())
        
        for i in range(count):
            category = categories[i % len(categories)]
            templates = self.expansion_templates[category]
            template = templates[i % len(templates)]
            
            # Generate new concept
            concept_id = f"{parent_node.id}_expanded_{category}_{i:03d}"
            title = template.format(parent_node.title)
            
            new_concept = CurriculumNode(
                id=concept_id,
                title=title,
                description=f"Extended concept focusing on {category} aspects of {parent_node.title}",
                level=min(6, parent_node.level + 1),
                parent_id=parent_node.id,
                children_ids=[],
                bloom_level=self._get_bloom_for_category(category),
                difficulty=self._get_difficulty_for_category(category, parent_node.difficulty),
                question_types=self._get_question_types_for_category(category),
                prerequisites=[parent_node.id],
                learning_objectives=[f"Master {category} aspects of {parent_node.title}"],
                common_misconceptions=[f"Common misconception in {category} approach to {parent_node.title}"],
                textbook_references=parent_node.textbook_references.copy() if hasattr(parent_node, 'textbook_references') else [],
                ontology_mappings=[],
                estimated_hours=0.5,
                keywords=self._extract_keywords(title),
                related_concepts=[],
                created_at=datetime.now()
            )
            
            additional_concepts.append(new_concept)
        
        return additional_concepts
    
    def _get_bloom_for_category(self, category: str) -> str:
        """Get appropriate Bloom's level for expansion category."""
        bloom_mapping = {
            'mathematical': 'Apply',
            'experimental': 'Analyze',
            'theoretical': 'Understand',
            'applied': 'Apply',
            'interdisciplinary': 'Evaluate'
        }
        return bloom_mapping.get(category, 'Apply')
    
    def _get_difficulty_for_category(self, category: str, parent_difficulty: str) -> str:
        """Get difficulty level for expansion category."""
        if category in ['theoretical', 'interdisciplinary']:
            return 'advanced'
        elif category in ['mathematical', 'experimental']:
            return 'intermediate' if parent_difficulty == 'introductory' else 'advanced'
        else:
            return parent_difficulty
    
    def _get_question_types_for_category(self, category: str) -> List[str]:
        """Get question types for expansion category."""
        type_mapping = {
            'mathematical': ['computational', 'graphical'],
            'experimental': ['experimental', 'graphical'],
            'theoretical': ['conceptual'],
            'applied': ['computational', 'conceptual'],
            'interdisciplinary': ['conceptual']
        }
        return type_mapping.get(category, ['conceptual'])
    
    def _extract_keywords(self, title: str) -> List[str]:
        """Extract keywords from title."""
        # Remove common words and extract meaningful terms
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        words = re.findall(r'\b\w+\b', title.lower())
        return [w for w in words if w not in stop_words and len(w) > 2][:5]


class PrerequisiteTracker:
    """Manages prerequisite relationships and learning path optimization."""
    
    def __init__(self):
        """Initialize prerequisite tracker."""
        self.prerequisite_graph = nx.DiGraph()
        
    def build_prerequisite_graph(self, nodes: List) -> nx.DiGraph:
        """
        Build prerequisite dependency graph from curriculum nodes.
        
        Args:
            nodes: List of curriculum nodes
            
        Returns:
            NetworkX directed graph representing prerequisites
        """
        # Add all nodes to graph
        for node in nodes:
            self.prerequisite_graph.add_node(node.id, **{
                'title': node.title,
                'level': node.level,
                'bloom_level': node.bloom_level,
                'difficulty': node.difficulty
            })
        
        # Add prerequisite edges
        for node in nodes:
            if hasattr(node, 'prerequisites'):
                for prereq_id in node.prerequisites:
                    if self.prerequisite_graph.has_node(prereq_id):
                        self.prerequisite_graph.add_edge(prereq_id, node.id, relation='prerequisite')
            
            # Add hierarchical prerequisites (parent-child)
            if hasattr(node, 'parent_id') and node.parent_id:
                if self.prerequisite_graph.has_node(node.parent_id):
                    self.prerequisite_graph.add_edge(node.parent_id, node.id, relation='hierarchy')
        
        return self.prerequisite_graph
    
    def calculate_learning_paths(self, start_node_id: str, end_node_id: str) -> List[List[str]]:
        """
        Calculate optimal learning paths between two concepts.
        
        Args:
            start_node_id: Starting concept ID
            end_node_id: Target concept ID
            
        Returns:
            List of learning paths (each path is a list of node IDs)
        """
        try:
            # Find all simple paths between start and end
            paths = list(nx.all_simple_paths(self.prerequisite_graph, start_node_id, end_node_id))
            
            # Sort paths by length (shorter paths first)
            paths.sort(key=len)
            
            return paths[:5]  # Return top 5 paths
            
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return []
    
    def validate_prerequisite_consistency(self) -> Dict[str, List[str]]:
        """
        Validate prerequisite graph for consistency issues.
        
        Returns:
            Dictionary of validation issues
        """
        issues = {
            'cycles': [],
            'missing_prerequisites': [],
            'invalid_hierarchies': []
        }
        
        # Check for cycles
        try:
            cycles = list(nx.simple_cycles(self.prerequisite_graph))
            issues['cycles'] = cycles
        except:
            pass
        
        # Check for missing prerequisite nodes
        for node_id in self.prerequisite_graph.nodes():
            for successor in self.prerequisite_graph.successors(node_id):
                edge_data = self.prerequisite_graph.get_edge_data(node_id, successor)
                if edge_data and edge_data.get('relation') == 'prerequisite':
                    if not self.prerequisite_graph.has_node(successor):
                        issues['missing_prerequisites'].append(f"{node_id} -> {successor}")
        
        return issues
    
    def suggest_prerequisite_additions(self, nodes: List) -> List[Tuple[str, str, str]]:
        """
        Suggest additional prerequisite relationships.
        
        Args:
            nodes: List of curriculum nodes
            
        Returns:
            List of tuples (source_id, target_id, reason)
        """
        suggestions = []
        
        # Suggest prerequisites based on keyword similarity and level hierarchy
        for node in nodes:
            if hasattr(node, 'level') and node.level > 2:
                # Find potential prerequisites at lower levels
                for other_node in nodes:
                    if (hasattr(other_node, 'level') and 
                        other_node.level < node.level and 
                        other_node.id not in getattr(node, 'prerequisites', [])):
                        
                        # Check keyword overlap
                        node_keywords = set(getattr(node, 'keywords', []))
                        other_keywords = set(getattr(other_node, 'keywords', []))
                        
                        if len(node_keywords & other_keywords) >= 2:
                            suggestions.append((
                                other_node.id,
                                node.id,
                                f"Keyword overlap: {node_keywords & other_keywords}"
                            ))
        
        return suggestions[:20]  # Return top 20 suggestions


class MisconceptionGenerator:
    """Generates common misconceptions for educational content."""
    
    # Template misconceptions by discipline and concept type
    MISCONCEPTION_TEMPLATES = {
        'physics': [
            "Confusing {concept} with {related_concept}",
            "Believing {concept} always increases with {variable}",
            "Thinking {concept} is purely theoretical with no practical applications",
            "Assuming {concept} behaves linearly in all situations",
            "Confusing cause and effect in {concept} relationships"
        ],
        'biology': [
            "Thinking {concept} implies progression or improvement",
            "Believing {concept} is controlled by a single factor",
            "Assuming all {concept} variations are beneficial",
            "Confusing {concept} with similar but distinct processes",
            "Thinking {concept} occurs instantaneously"
        ],
        'chemistry': [
            "Visualizing {concept} using inappropriate physical models",
            "Assuming {concept} always follows simple patterns",
            "Confusing {concept} at molecular vs. macroscopic levels",
            "Thinking {concept} can be directly observed",
            "Believing {concept} violates conservation laws"
        ],
        'mathematics': [
            "Applying {concept} procedures without understanding meaning",
            "Thinking {concept} always has a unique solution",
            "Confusing {concept} with its inverse operation",
            "Assuming {concept} works the same in all number systems",
            "Believing {concept} relationships are always symmetric"
        ],
        'general': [
            "Oversimplifying complex {concept} relationships",
            "Thinking {concept} applies universally without exceptions",
            "Confusing correlation with causation in {concept}",
            "Assuming {concept} can be understood in isolation",
            "Believing {concept} has only one correct interpretation"
        ]
    }
    
    @classmethod
    def generate_misconceptions(cls, concept_title: str, discipline: str, level: int) -> List[str]:
        """
        Generate common misconceptions for a concept.
        
        Args:
            concept_title: Title of the concept
            discipline: Academic discipline
            level: Hierarchical level (1-6)
            
        Returns:
            List of common misconceptions
        """
        discipline_key = discipline.lower().replace(' ', '_')
        if discipline_key not in cls.MISCONCEPTION_TEMPLATES:
            discipline_key = 'general'
        
        templates = cls.MISCONCEPTION_TEMPLATES[discipline_key]
        misconceptions = []
        
        # Extract key terms from concept title
        key_terms = cls._extract_key_terms(concept_title)
        main_concept = key_terms[0] if key_terms else concept_title.lower()
        
        # Generate misconceptions from templates
        for i, template in enumerate(templates[:3]):  # Limit to 3 per concept
            if '{concept}' in template:
                misconception = template.replace('{concept}', main_concept)
                
                # Replace other placeholders
                if '{related_concept}' in misconception:
                    related = key_terms[1] if len(key_terms) > 1 else 'related concept'
                    misconception = misconception.replace('{related_concept}', related)
                
                if '{variable}' in misconception:
                    variables = ['time', 'temperature', 'pressure', 'size', 'complexity']
                    misconception = misconception.replace('{variable}', variables[i % len(variables)])
                
                misconceptions.append(misconception)
        
        # Add level-specific misconceptions
        level_misconceptions = cls._get_level_specific_misconceptions(level, main_concept)
        misconceptions.extend(level_misconceptions)
        
        return misconceptions[:3]  # Return max 3 misconceptions
    
    @classmethod
    def _extract_key_terms(cls, title: str) -> List[str]:
        """Extract key terms from concept title."""
        # Remove common words and extract meaningful terms
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        words = re.findall(r'\b\w+\b', title.lower())
        key_terms = [w for w in words if w not in stop_words and len(w) > 2]
        return key_terms[:3]  # Return top 3 key terms
    
    @classmethod
    def _get_level_specific_misconceptions(cls, level: int, concept: str) -> List[str]:
        """Get misconceptions specific to hierarchical level."""
        level_templates = {
            1: [f"Thinking {concept} is just memorization without understanding"],
            2: [f"Believing all aspects of {concept} are equally important"],
            3: [f"Assuming {concept} can be learned without prerequisite knowledge"],
            4: [f"Thinking {concept} analysis always yields definitive answers"],
            5: [f"Believing {concept} details are unnecessary for understanding"],
            6: [f"Assuming {concept} skills transfer automatically to new contexts"]
        }
        
        return level_templates.get(level, [])