#!/usr/bin/env python3
"""
test_curricula.py - Comprehensive unit tests for curriculum generation system

Tests all components of the curriculum generation system including
content extraction, hierarchy building, educational metadata, and export formats.

Author: Claude Code
License: MIT
"""

import asyncio
import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import xml.etree.ElementTree as ET

import networkx as nx
import pandas as pd
import pytest

# Import our modules to test
from curricula import CurriculumGenerator, CurriculumNode
from core.curriculum_processor import (
    TextbookContentExtractor, BloomTaxonomyClassifier, 
    ConceptExpander, PrerequisiteTracker, MisconceptionGenerator,
    BookReference, LearningObjective, ConceptMapping
)


class TestCurriculumNode(unittest.TestCase):
    """Test the CurriculumNode dataclass."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_node = CurriculumNode(
            id="test_node_001",
            title="Test Concept",
            description="A test concept for unit testing",
            level=3,
            parent_id="parent_001",
            children_ids=["child_001", "child_002"],
            bloom_level="Apply",
            difficulty="intermediate",
            question_types=["computational", "conceptual"],
            prerequisites=["prereq_001"],
            learning_objectives=["Understand test concepts"],
            common_misconceptions=["Common test misconception"],
            textbook_references=[{"book": "Test Book", "chapter": "Chapter 1"}],
            ontology_mappings=[{"ontology": "TestOnt", "concept_id": "TEST_001"}],
            estimated_hours=2.0,
            keywords=["test", "concept"],
            related_concepts=["related_001"],
            created_at=datetime.now()
        )
    
    def test_node_creation(self):
        """Test basic node creation and attributes."""
        self.assertEqual(self.sample_node.id, "test_node_001")
        self.assertEqual(self.sample_node.title, "Test Concept")
        self.assertEqual(self.sample_node.level, 3)
        self.assertEqual(self.sample_node.bloom_level, "Apply")
        self.assertEqual(len(self.sample_node.children_ids), 2)
    
    def test_node_to_dict(self):
        """Test conversion to dictionary."""
        node_dict = self.sample_node.to_dict()
        
        self.assertIsInstance(node_dict, dict)
        self.assertEqual(node_dict['id'], "test_node_001")
        self.assertEqual(node_dict['level'], 3)
        self.assertIn('created_at', node_dict)
        self.assertIsInstance(node_dict['created_at'], str)  # Should be ISO format
    
    def test_node_educational_metadata(self):
        """Test educational metadata attributes."""
        self.assertIn("computational", self.sample_node.question_types)
        self.assertEqual(len(self.sample_node.learning_objectives), 1)
        self.assertEqual(len(self.sample_node.common_misconceptions), 1)
        self.assertGreater(self.sample_node.estimated_hours, 0)


class TestTextbookContentExtractor(unittest.TestCase):
    """Test the TextbookContentExtractor class."""
    
    def setUp(self):
        """Set up test fixtures with temporary directories."""
        self.temp_dir = tempfile.mkdtemp()
        self.books_dir = Path(self.temp_dir)
        self.extractor = TextbookContentExtractor(self.books_dir)
        
        # Create mock book structure
        self._create_mock_book_structure()
    
    def _create_mock_book_structure(self):
        """Create a mock book directory structure for testing."""
        # Create discipline directory
        physics_dir = self.books_dir / "Physics" / "University" / "test-physics-book"
        physics_dir.mkdir(parents=True)
        
        # Create collections directory
        collections_dir = physics_dir / "collections"
        collections_dir.mkdir()
        
        # Create mock collection XML
        xml_content = '''<?xml version="1.0"?>
        <col:collection xmlns="http://cnx.rice.edu/collxml" 
                       xmlns:md="http://cnx.rice.edu/mdml" 
                       xmlns:col="http://cnx.rice.edu/collxml">
          <metadata xmlns:md="http://cnx.rice.edu/mdml">
            <md:title>Test Physics Book</md:title>
            <md:uuid>test-uuid-123</md:uuid>
          </metadata>
          <col:content>
            <col:subcollection>
              <md:title>Classical Mechanics</md:title>
              <col:content>
                <col:module document="m12345"/>
                <col:module document="m12346"/>
              </col:content>
            </col:subcollection>
            <col:subcollection>
              <md:title>Thermodynamics</md:title>
              <col:content>
                <col:module document="m12347"/>
              </col:content>
            </col:subcollection>
            <col:module document="m12348"/>
          </col:content>
        </col:collection>'''
        
        with open(collections_dir / "test-physics.collection.xml", "w") as f:
            f.write(xml_content)
    
    def test_extract_discipline_content(self):
        """Test extraction of discipline content."""
        content = self.extractor.extract_discipline_content("Physics")
        
        self.assertIsInstance(content, dict)
        self.assertEqual(content['discipline'], "Physics")
        self.assertGreater(len(content['books']), 0)
        self.assertGreater(content['total_modules'], 0)
        self.assertIn('extraction_timestamp', content)
    
    def test_parse_collection_xml(self):
        """Test parsing of collection XML files."""
        xml_file = self.books_dir / "Physics" / "University" / "test-physics-book" / "collections" / "test-physics.collection.xml"
        book_dir = xml_file.parent.parent
        
        book_content = self.extractor._parse_collection_xml(xml_file, book_dir)
        
        self.assertEqual(book_content['title'], "Test Physics Book")
        self.assertEqual(book_content['uuid'], "test-uuid-123")
        self.assertEqual(len(book_content['chapters']), 2)
        self.assertEqual(book_content['module_count'], 4)  # 3 in chapters + 1 standalone
    
    def test_parse_chapter(self):
        """Test parsing of individual chapters."""
        # Create a sample subcollection element
        xml_content = '''<col:subcollection xmlns:col="http://cnx.rice.edu/collxml" 
                                          xmlns:md="http://cnx.rice.edu/mdml">
          <md:title>Test Chapter</md:title>
          <col:content>
            <col:module document="m001"/>
            <col:module document="m002"/>
          </col:content>
        </col:subcollection>'''
        
        root = ET.fromstring(xml_content)
        chapter = self.extractor._parse_chapter(root)
        
        self.assertEqual(chapter['title'], "Test Chapter")
        self.assertEqual(len(chapter['modules']), 2)
        self.assertEqual(chapter['modules'][0]['document_id'], "m001")
    
    def test_empty_discipline_handling(self):
        """Test handling of non-existent disciplines."""
        content = self.extractor.extract_discipline_content("NonExistentSubject")
        
        self.assertEqual(content['books'], [])
        self.assertEqual(content['total_modules'], 0)


class TestBloomTaxonomyClassifier(unittest.TestCase):
    """Test the BloomTaxonomyClassifier."""
    
    def test_keyword_classification(self):
        """Test classification based on keywords."""
        # Test Remember level
        result = BloomTaxonomyClassifier.classify_content(
            "Define basic concepts", "List the fundamental principles", 1
        )
        self.assertEqual(result, "Remember")
        
        # Test Apply level
        result = BloomTaxonomyClassifier.classify_content(
            "Calculate force values", "Use Newton's laws to solve problems", 3
        )
        self.assertEqual(result, "Apply")
        
        # Test Create level
        result = BloomTaxonomyClassifier.classify_content(
            "Design experiment", "Create new solution method", 6
        )
        self.assertEqual(result, "Create")
    
    def test_default_classification_by_level(self):
        """Test default classification when no keywords match."""
        # Should fall back to level-based defaults
        result = BloomTaxonomyClassifier.classify_content(
            "Random title", "Random description", 1
        )
        self.assertEqual(result, "Remember")
        
        result = BloomTaxonomyClassifier.classify_content(
            "Random title", "Random description", 6
        )
        self.assertEqual(result, "Create")
    
    def test_all_bloom_levels_represented(self):
        """Test that all Bloom's levels have keywords."""
        for level in BloomTaxonomyClassifier.BLOOM_KEYWORDS:
            self.assertGreater(len(BloomTaxonomyClassifier.BLOOM_KEYWORDS[level]), 0)


class TestConceptExpander(unittest.TestCase):
    """Test the ConceptExpander class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.expander = ConceptExpander(target_size=100)
        
        # Create mock nodes
        self.mock_nodes = []
        for i in range(50):
            node = Mock()
            node.id = f"node_{i:03d}"
            node.title = f"Test Concept {i}"
            node.level = (i % 5) + 1  # Levels 1-5
            node.difficulty = "intermediate"
            node.textbook_references = []
            node.children_ids = []
            self.mock_nodes.append(node)
    
    def test_expansion_to_target_size(self):
        """Test expansion of curriculum to target size."""
        initial_size = len(self.mock_nodes)
        
        with patch('curricula.CurriculumNode') as mock_curriculum_node:
            # Configure the mock to return a proper mock object
            mock_curriculum_node.return_value = Mock()
            
            expanded_nodes = self.expander.expand_curriculum(
                self.mock_nodes, "Physics"
            )
            
            # Should expand to target size
            self.assertGreaterEqual(len(expanded_nodes), self.expander.target_size)
    
    def test_no_expansion_when_target_met(self):
        """Test that no expansion occurs when target is already met."""
        # Create nodes list that already meets target
        large_node_list = [Mock() for _ in range(150)]
        
        result = self.expander.expand_curriculum(large_node_list, "Physics")
        
        # Should return original list
        self.assertEqual(len(result), 150)
    
    def test_expansion_categories(self):
        """Test that different expansion categories are used."""
        categories = list(self.expander.expansion_templates.keys())
        
        for category in categories:
            self.assertIn(category, self.expander.expansion_templates)
            self.assertGreater(len(self.expander.expansion_templates[category]), 0)
    
    def test_bloom_level_assignment(self):
        """Test Bloom level assignment for different categories."""
        self.assertEqual(self.expander._get_bloom_for_category('mathematical'), 'Apply')
        self.assertEqual(self.expander._get_bloom_for_category('experimental'), 'Analyze')
        self.assertEqual(self.expander._get_bloom_for_category('theoretical'), 'Understand')


class TestPrerequisiteTracker(unittest.TestCase):
    """Test the PrerequisiteTracker class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tracker = PrerequisiteTracker()
        
        # Create mock nodes with prerequisite relationships
        self.mock_nodes = []
        for i in range(10):
            node = Mock()
            node.id = f"node_{i:03d}"
            node.title = f"Concept {i}"
            node.level = (i % 3) + 1
            node.bloom_level = "Apply"
            node.difficulty = "intermediate"
            node.parent_id = f"node_{max(0, i-1):03d}" if i > 0 else None
            node.prerequisites = [f"node_{max(0, i-2):03d}"] if i > 1 else []
            self.mock_nodes.append(node)
    
    def test_build_prerequisite_graph(self):
        """Test building of prerequisite dependency graph."""
        graph = self.tracker.build_prerequisite_graph(self.mock_nodes)
        
        self.assertIsInstance(graph, nx.DiGraph)
        self.assertEqual(len(graph.nodes()), len(self.mock_nodes))
        self.assertGreater(len(graph.edges()), 0)
    
    def test_learning_path_calculation(self):
        """Test calculation of learning paths."""
        self.tracker.build_prerequisite_graph(self.mock_nodes)
        
        paths = self.tracker.calculate_learning_paths("node_000", "node_005")
        
        self.assertIsInstance(paths, list)
        # Should find at least one path
        if paths:
            self.assertIsInstance(paths[0], list)
            self.assertEqual(paths[0][0], "node_000")
            self.assertEqual(paths[0][-1], "node_005")
    
    def test_prerequisite_validation(self):
        """Test validation of prerequisite consistency."""
        self.tracker.build_prerequisite_graph(self.mock_nodes)
        
        issues = self.tracker.validate_prerequisite_consistency()
        
        self.assertIsInstance(issues, dict)
        self.assertIn('cycles', issues)
        self.assertIn('missing_prerequisites', issues)
        self.assertIn('invalid_hierarchies', issues)
    
    def test_prerequisite_suggestions(self):
        """Test prerequisite relationship suggestions."""
        # Add keywords to mock nodes
        for i, node in enumerate(self.mock_nodes):
            node.keywords = [f"keyword_{i}", "common"]
        
        suggestions = self.tracker.suggest_prerequisite_additions(self.mock_nodes)
        
        self.assertIsInstance(suggestions, list)
        # Each suggestion should be a tuple with 3 elements
        for suggestion in suggestions:
            self.assertEqual(len(suggestion), 3)


class TestMisconceptionGenerator(unittest.TestCase):
    """Test the MisconceptionGenerator class."""
    
    def test_misconception_generation(self):
        """Test generation of misconceptions for different disciplines."""
        # Test Physics
        misconceptions = MisconceptionGenerator.generate_misconceptions(
            "Newton's Laws", "Physics", 3
        )
        
        self.assertIsInstance(misconceptions, list)
        self.assertGreater(len(misconceptions), 0)
        self.assertLessEqual(len(misconceptions), 3)
    
    def test_discipline_specific_templates(self):
        """Test that different disciplines use appropriate templates."""
        physics_misc = MisconceptionGenerator.generate_misconceptions(
            "Force and Motion", "Physics", 3
        )
        
        biology_misc = MisconceptionGenerator.generate_misconceptions(
            "Cell Division", "Biology", 3
        )
        
        # Should generate different misconceptions for different disciplines
        self.assertNotEqual(physics_misc, biology_misc)
    
    def test_level_specific_misconceptions(self):
        """Test level-specific misconception generation."""
        level_1_misc = MisconceptionGenerator._get_level_specific_misconceptions(1, "physics")
        level_6_misc = MisconceptionGenerator._get_level_specific_misconceptions(6, "physics")
        
        self.assertNotEqual(level_1_misc, level_6_misc)
    
    def test_key_term_extraction(self):
        """Test extraction of key terms from concept titles."""
        terms = MisconceptionGenerator._extract_key_terms("Newton's Laws of Motion")
        
        self.assertIsInstance(terms, list)
        self.assertIn("newton", terms)
        self.assertIn("laws", terms)
        self.assertNotIn("of", terms)  # Should filter stop words


class TestCurriculumGenerator(unittest.TestCase):
    """Test the main CurriculumGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        with patch('curricula.OpenBooksConfig'):
            self.generator = CurriculumGenerator()
        
        # Mock the UI and logger
        self.generator.ui = Mock()
        self.generator.logger = Mock()
    
    @patch('curricula.FederatedSystem')
    async def test_acorn_initialization(self, mock_federated_system):
        """Test ACORN system initialization."""
        mock_system = Mock()
        mock_federated_system.return_value = mock_system
        
        await self.generator._initialize_acorn_system()
        
        mock_federated_system.assert_called_once()
        mock_system.initialize_all_integrators.assert_called_once()
    
    def test_discipline_discovery(self):
        """Test discovery of available disciplines."""
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.iterdir') as mock_iterdir:
            
            # Mock directory structure
            mock_dirs = [
                Mock(is_dir=lambda: True, name="Physics"),
                Mock(is_dir=lambda: True, name="Biology"),
                Mock(is_dir=lambda: True, name="Uncategorized"),  # Should be filtered
            ]
            mock_iterdir.return_value = mock_dirs
            
            # Mock university subdirectories
            with patch('pathlib.Path.__truediv__') as mock_div:
                mock_uni_dir = Mock()
                mock_uni_dir.exists.return_value = True
                mock_uni_dir.__iter__ = Mock(return_value=iter([Mock()]))  # Has content
                mock_div.return_value = mock_uni_dir
                
                disciplines = self.generator._get_available_disciplines()
                
                self.assertIn("Physics", disciplines)
                self.assertIn("Biology", disciplines)
                self.assertNotIn("Uncategorized", disciplines)
    
    def test_curriculum_hierarchy_building(self):
        """Test building of 6-level curriculum hierarchy."""
        # Mock textbook content
        mock_content = {
            'books': [{
                'title': 'Test Physics Book',
                'chapters': [{
                    'title': 'Classical Mechanics',
                    'modules': [
                        {'title': 'Newton\'s Laws', 'document_id': 'm001'},
                        {'title': 'Kinematics', 'document_id': 'm002'}
                    ]
                }]
            }]
        }
        
        # Mock ontology mappings
        mock_mappings = {}
        
        nodes = self.generator._build_curriculum_hierarchy(
            "Physics", mock_content, mock_mappings
        )
        
        # Should create nodes at multiple levels
        levels = {node.level for node in nodes}
        self.assertIn(1, levels)  # Discipline level
        self.assertIn(2, levels)  # Branch level
        
        # Should have root discipline node
        root_nodes = [n for n in nodes if n.level == 1]
        self.assertEqual(len(root_nodes), 1)
        self.assertEqual(root_nodes[0].title, "Physics")
    
    def test_educational_metadata_enhancement(self):
        """Test enhancement of nodes with educational metadata."""
        # Create mock nodes
        mock_nodes = []
        for i in range(5):
            node = CurriculumNode(
                id=f"node_{i}",
                title=f"Concept {i}",
                description=f"Description {i}",
                level=i + 1,
                parent_id=f"node_{i-1}" if i > 0 else None,
                children_ids=[],
                bloom_level="Apply",
                difficulty="intermediate",
                question_types=["conceptual"],
                prerequisites=[],
                learning_objectives=[],
                common_misconceptions=[],
                textbook_references=[],
                ontology_mappings=[],
                estimated_hours=1.0,
                keywords=[f"keyword_{i}"],
                related_concepts=[],
                created_at=datetime.now()
            )
            mock_nodes.append(node)
        
        # Enhance with metadata
        self.generator._enhance_with_educational_metadata(mock_nodes)
        
        # Check that prerequisites were added
        for node in mock_nodes:
            if node.level > 1:
                self.assertGreater(len(node.prerequisites), 0)
            
            # Check that misconceptions were added
            self.assertGreater(len(node.common_misconceptions), 0)


class TestExportFormats(unittest.TestCase):
    """Test export functionality for different formats."""
    
    def setUp(self):
        """Set up test fixtures."""
        with patch('curricula.OpenBooksConfig'):
            self.generator = CurriculumGenerator()
        
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Create sample nodes
        self.sample_nodes = []
        for i in range(10):
            node = CurriculumNode(
                id=f"test_node_{i:03d}",
                title=f"Test Concept {i}",
                description=f"Test description {i}",
                level=(i % 6) + 1,
                parent_id=f"test_node_{max(0, i-1):03d}" if i > 0 else None,
                children_ids=[],
                bloom_level="Apply",
                difficulty="intermediate",
                question_types=["conceptual"],
                prerequisites=[],
                learning_objectives=[f"Learn concept {i}"],
                common_misconceptions=[f"Misconception about concept {i}"],
                textbook_references=[],
                ontology_mappings=[],
                estimated_hours=1.0,
                keywords=[f"keyword_{i}"],
                related_concepts=[],
                created_at=datetime.now()
            )
            self.sample_nodes.append(node)
    
    async def test_json_export(self):
        """Test JSON export format."""
        await self.generator._export_discipline_curriculum(
            "TestSubject", self.sample_nodes, self.temp_dir
        )
        
        json_file = self.temp_dir / "testsubject.json"
        self.assertTrue(json_file.exists())
        
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data['discipline'], "TestSubject")
        self.assertEqual(len(data['concepts']), len(self.sample_nodes))
        self.assertIn('metadata', data)
        self.assertIn('total_concepts', data['metadata'])
    
    def test_dot_format_generation(self):
        """Test DOT format generation for GraphViz."""
        # Create mock graph
        graph = nx.DiGraph()
        for node in self.sample_nodes:
            graph.add_node(node.id, title=node.title, level=node.level)
        
        dot_content = self.generator._generate_dot_format(
            "TestSubject", graph, self.sample_nodes
        )
        
        self.assertIn('digraph "TestSubject_Curriculum"', dot_content)
        self.assertIn('Test Concept 0', dot_content)
        self.assertIn('fillcolor=', dot_content)
    
    def test_markdown_generation(self):
        """Test Markdown format generation."""
        markdown_content = self.generator._generate_markdown_format(
            "TestSubject", self.sample_nodes
        )
        
        self.assertIn("# TestSubject Curriculum", markdown_content)
        self.assertIn("## Overview", markdown_content)
        self.assertIn("Total Concepts", markdown_content)
        self.assertIn("Level Breakdown", markdown_content)
    
    def test_tsv_export_compatibility(self):
        """Test TSV export data compatibility."""
        # Convert nodes to DataFrame
        df = pd.DataFrame([node.to_dict() for node in self.sample_nodes])
        
        # Should have all required columns
        required_columns = ['id', 'title', 'level', 'bloom_level', 'difficulty']
        for col in required_columns:
            self.assertIn(col, df.columns)
        
        # Should handle all data types properly
        self.assertEqual(len(df), len(self.sample_nodes))


class TestIntegrationWorkflow(unittest.IsolatedAsyncioTestCase):
    """Integration tests for the complete curriculum generation workflow."""
    
    async def test_complete_workflow_mock(self):
        """Test the complete workflow with mocked dependencies."""
        with patch('curricula.OpenBooksConfig'), \
             patch('curricula.FederatedSystem'), \
             patch.object(CurriculumGenerator, '_get_available_disciplines', return_value=['Physics']), \
             patch.object(CurriculumGenerator, '_extract_textbook_content'), \
             patch.object(CurriculumGenerator, '_get_ontology_mappings'), \
             patch.object(CurriculumGenerator, '_export_discipline_curriculum'):
            
            generator = CurriculumGenerator()
            generator.ui = Mock()
            generator.logger = Mock()
            
            # Mock the extraction methods
            generator._extract_textbook_content.return_value = {
                'books': [{'title': 'Test Book', 'chapters': []}]
            }
            generator._get_ontology_mappings.return_value = {}
            generator._export_discipline_curriculum.return_value = None
            
            # Run the workflow
            results = await generator.generate_all_curricula()
            
            # Verify results structure
            self.assertIsInstance(results, dict)
            self.assertIn('total_disciplines', results)
            self.assertIn('processing_time', results)


# Performance and stress tests
class TestPerformance(unittest.TestCase):
    """Performance tests for curriculum generation."""
    
    def test_large_curriculum_handling(self):
        """Test handling of large curriculum sizes."""
        # Create a large number of mock nodes
        large_node_count = 5000
        mock_nodes = []
        
        for i in range(large_node_count):
            node = Mock()
            node.id = f"node_{i:05d}"
            node.level = (i % 6) + 1
            mock_nodes.append(node)
        
        # Test that operations complete in reasonable time
        start_time = datetime.now()
        
        # Test node filtering by level
        level_1_nodes = [n for n in mock_nodes if n.level == 1]
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        # Should complete in under 1 second for 5000 nodes
        self.assertLess(processing_time, 1.0)
        self.assertGreater(len(level_1_nodes), 0)


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)