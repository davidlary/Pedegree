"""
tests/test_curriculum_generation.py - Comprehensive Tests for Curriculum Generation System

Tests for the complete curriculum generation pipeline including:
- Curriculum engine functionality
- Educational standards management
- Visualization and export capabilities
- Integration with existing OpenBooks systems
"""

import asyncio
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import networkx as nx
import pandas as pd
import numpy as np

# Import modules to test
from core.curriculum_engine import (
    CurriculumConcept, DisciplineCurriculum, CurriculumEngine
)
from core.educational_standards import EducationalStandardsManager
from core.curriculum_viz import CurriculumVisualizer, CurriculumExporter


class TestCurriculumConcept(unittest.TestCase):
    """Test the CurriculumConcept dataclass."""
    
    def setUp(self):
        """Set up test data."""
        self.concept = CurriculumConcept(
            concept_id="physics_0001",
            title="Newton's First Law",
            description="An object at rest stays at rest",
            category="Classical Mechanics",
            subtopic="Laws of Motion",
            level="HS-Found",
            bloom_taxonomy="Understand",
            standards="Intro-Core",
            prerequisites=["Basic Kinematics"],
            learning_objectives=["Understand inertia"],
            difficulty_score=3.0,
            estimated_hours=2.0,
            source_books=["Physics Textbook"],
            keywords=["newton", "inertia", "motion"]
        )
    
    def test_concept_creation(self):
        """Test basic concept creation and attributes."""
        self.assertEqual(self.concept.concept_id, "physics_0001")
        self.assertEqual(self.concept.title, "Newton's First Law")
        self.assertEqual(self.concept.category, "Classical Mechanics")
        self.assertEqual(self.concept.level, "HS-Found")
        self.assertEqual(self.concept.difficulty_score, 3.0)
    
    def test_concept_to_dict(self):
        """Test conversion to dictionary."""
        concept_dict = self.concept.to_dict()
        
        self.assertIsInstance(concept_dict, dict)
        self.assertEqual(concept_dict['concept_id'], "physics_0001")
        self.assertEqual(concept_dict['title'], "Newton's First Law")
        self.assertIn('created_at', concept_dict)
        self.assertIsInstance(concept_dict['created_at'], str)
    
    def test_concept_from_dict(self):
        """Test creation from dictionary."""
        concept_dict = self.concept.to_dict()
        reconstructed = CurriculumConcept.from_dict(concept_dict)
        
        self.assertEqual(reconstructed.concept_id, self.concept.concept_id)
        self.assertEqual(reconstructed.title, self.concept.title)
        self.assertEqual(reconstructed.category, self.concept.category)
        self.assertEqual(reconstructed.difficulty_score, self.concept.difficulty_score)
    
    def test_concept_defaults(self):
        """Test concept creation with minimal parameters."""
        minimal_concept = CurriculumConcept(
            concept_id="test_001",
            title="Test Concept",
            description="Test Description",
            category="Test Category",
            subtopic="Test Subtopic",
            level="UG-Intro",
            bloom_taxonomy="Apply",
            standards="Test-Standard"
        )
        
        self.assertEqual(minimal_concept.prerequisites, [])
        self.assertEqual(minimal_concept.learning_objectives, [])
        self.assertEqual(minimal_concept.difficulty_score, 0.0)
        self.assertEqual(minimal_concept.estimated_hours, 1.0)


class TestDisciplineCurriculum(unittest.TestCase):
    """Test the DisciplineCurriculum dataclass."""
    
    def setUp(self):
        """Set up test data."""
        self.curriculum = DisciplineCurriculum(discipline="Physics")
        
        self.concept1 = CurriculumConcept(
            concept_id="physics_0001",
            title="Newton's First Law",
            description="Test description",
            category="Classical Mechanics",
            subtopic="Laws of Motion",
            level="HS-Found",
            bloom_taxonomy="Understand",
            standards="Intro-Core"
        )
        
        self.concept2 = CurriculumConcept(
            concept_id="physics_0002",
            title="Coulomb's Law",
            description="Test description",
            category="Electromagnetism",
            subtopic="Electric Force",
            level="HS-Adv",
            bloom_taxonomy="Apply",
            standards="AP-Physics"
        )
    
    def test_curriculum_creation(self):
        """Test basic curriculum creation."""
        self.assertEqual(self.curriculum.discipline, "Physics")
        self.assertEqual(self.curriculum.total_concepts, 0)
        self.assertEqual(len(self.curriculum.concepts), 0)
    
    def test_add_concept(self):
        """Test adding concepts to curriculum."""
        self.curriculum.add_concept(self.concept1)
        
        self.assertEqual(self.curriculum.total_concepts, 1)
        self.assertEqual(len(self.curriculum.concepts), 1)
        self.assertEqual(self.curriculum.concepts[0], self.concept1)
        
        # Check category counts
        self.assertIn("Classical Mechanics", self.curriculum.category_counts)
        self.assertEqual(self.curriculum.category_counts["Classical Mechanics"]["HS-Found"], 1)
    
    def test_add_multiple_concepts(self):
        """Test adding multiple concepts."""
        self.curriculum.add_concept(self.concept1)
        self.curriculum.add_concept(self.concept2)
        
        self.assertEqual(self.curriculum.total_concepts, 2)
        self.assertEqual(len(self.curriculum.category_counts), 2)
        self.assertIn("AP-Physics", self.curriculum.exam_standards)
    
    def test_get_concepts_by_category(self):
        """Test filtering concepts by category."""
        self.curriculum.add_concept(self.concept1)
        self.curriculum.add_concept(self.concept2)
        
        mechanics_concepts = self.curriculum.get_concepts_by_category("Classical Mechanics")
        self.assertEqual(len(mechanics_concepts), 1)
        self.assertEqual(mechanics_concepts[0], self.concept1)
    
    def test_get_concepts_by_level(self):
        """Test filtering concepts by level."""
        self.curriculum.add_concept(self.concept1)
        self.curriculum.add_concept(self.concept2)
        
        hs_found_concepts = self.curriculum.get_concepts_by_level("HS-Found")
        self.assertEqual(len(hs_found_concepts), 1)
        self.assertEqual(hs_found_concepts[0], self.concept1)
    
    def test_prerequisite_tree(self):
        """Test prerequisite tree functionality."""
        # Create a simple prerequisite graph
        graph = nx.DiGraph()
        graph.add_edge("physics_0001", "physics_0002")
        self.curriculum.prerequisite_graph = graph
        
        prereqs = self.curriculum.get_prerequisite_tree("physics_0002")
        self.assertIn("physics_0001", prereqs)
        self.assertIn("physics_0002", prereqs)
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        self.curriculum.add_concept(self.concept1)
        curriculum_dict = self.curriculum.to_dict()
        
        self.assertIsInstance(curriculum_dict, dict)
        self.assertEqual(curriculum_dict['discipline'], "Physics")
        self.assertEqual(curriculum_dict['total_concepts'], 1)
        self.assertIn('concepts', curriculum_dict)
        self.assertEqual(len(curriculum_dict['concepts']), 1)


class TestEducationalStandardsManager(unittest.TestCase):
    """Test the EducationalStandardsManager class."""
    
    def setUp(self):
        """Set up test data."""
        self.standards_manager = EducationalStandardsManager()
    
    def test_get_exam_standards(self):
        """Test getting exam standards for disciplines."""
        physics_standards = self.standards_manager.get_exam_standards("Physics")
        self.assertIsInstance(physics_standards, set)
        self.assertIn("AP-Physics", physics_standards)
        self.assertIn("GRE-Physics", physics_standards)
        
        # Test unknown discipline
        unknown_standards = self.standards_manager.get_exam_standards("Unknown")
        self.assertEqual(unknown_standards, set())
    
    def test_get_prerequisite_rules(self):
        """Test getting prerequisite rules."""
        physics_prereqs = self.standards_manager.get_prerequisite_rules("Physics")
        self.assertIsInstance(physics_prereqs, dict)
        
        # Check specific prerequisite relationships
        if "Quantum Mechanics" in physics_prereqs:
            quantum_prereqs = physics_prereqs["Quantum Mechanics"]
            self.assertIn("Classical Mechanics", quantum_prereqs)
            self.assertIn("Electromagnetism", quantum_prereqs)
    
    def test_get_essential_concepts(self):
        """Test getting essential concepts."""
        physics_concepts = self.standards_manager.get_essential_concepts("Physics")
        self.assertIsInstance(physics_concepts, dict)
        
        # Check that we have category-organized concepts
        if "Classical Mechanics" in physics_concepts:
            mechanics_concepts = physics_concepts["Classical Mechanics"]
            self.assertIsInstance(mechanics_concepts, list)
            
            if mechanics_concepts:
                first_concept = mechanics_concepts[0]
                self.assertIn('title', first_concept)
                self.assertIn('description', first_concept)
                self.assertIn('level', first_concept)
                self.assertIn('difficulty', first_concept)
    
    def test_categorize_concept(self):
        """Test concept categorization."""
        # Test physics categorization
        mechanics_title = "Newton's Laws of Motion"
        category = self.standards_manager.categorize_concept("Physics", mechanics_title)
        self.assertEqual(category, "Classical Mechanics")
        
        # Test electromagnetic categorization
        em_title = "Maxwell's Equations"
        category = self.standards_manager.categorize_concept("Physics", em_title)
        self.assertEqual(category, "Electromagnetism")
        
        # Test unknown concept
        unknown_title = "Unknown Physics Concept"
        category = self.standards_manager.categorize_concept("Physics", unknown_title)
        self.assertEqual(category, "General Physics")
    
    def test_detect_exam_alignment(self):
        """Test exam alignment detection."""
        concepts = [
            "Classical Mechanics",
            "Electromagnetism", 
            "Quantum Mechanics",
            "Thermodynamics"
        ]
        
        alignment_scores = self.standards_manager.detect_exam_alignment("Physics", concepts)
        self.assertIsInstance(alignment_scores, dict)
        
        # Scores should be between 0 and 1
        for exam, score in alignment_scores.items():
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 1.0)
    
    def test_suggest_missing_concepts(self):
        """Test missing concept suggestions."""
        current_concepts = ["Newton's First Law", "Coulomb's Law"]
        suggestions = self.standards_manager.suggest_missing_concepts("Physics", current_concepts)
        
        self.assertIsInstance(suggestions, list)
        
        # Check suggestion structure
        if suggestions:
            first_suggestion = suggestions[0]
            self.assertIn('title', first_suggestion)
            self.assertIn('category', first_suggestion)
            self.assertIn('importance', first_suggestion)
    
    def test_validate_prerequisite_chain(self):
        """Test prerequisite chain validation."""
        # Test valid sequence
        valid_sequence = ["Basic Algebra", "Calculus", "Advanced Calculus"]
        validation = self.standards_manager.validate_prerequisite_chain("Mathematics", valid_sequence)
        self.assertIsInstance(validation, dict)
        self.assertIn('is_valid', validation)
        self.assertIn('violations', validation)
        
        # Test invalid sequence
        invalid_sequence = ["Quantum Mechanics", "Classical Mechanics"]
        validation = self.standards_manager.validate_prerequisite_chain("Physics", invalid_sequence)
        self.assertIsInstance(validation, dict)


class TestCurriculumEngine(unittest.TestCase):
    """Test the CurriculumEngine class."""
    
    def setUp(self):
        """Set up test data."""
        # Mock dependencies
        self.mock_text_extractor = Mock()
        self.mock_search_indexer = Mock()
        self.mock_standards_manager = Mock()
        self.mock_logger = Mock()
        
        self.engine = CurriculumEngine(
            text_extractor=self.mock_text_extractor,
            search_indexer=self.mock_search_indexer,
            standards_manager=self.mock_standards_manager,
            logger=self.mock_logger
        )
    
    def test_engine_initialization(self):
        """Test engine initialization."""
        self.assertIsNotNone(self.engine.text_extractor)
        self.assertIsNotNone(self.engine.search_indexer)
        self.assertIsNotNone(self.engine.standards_manager)
        self.assertIsNotNone(self.engine.logger)
        
        # Test default initialization
        default_engine = CurriculumEngine()
        self.assertIsNotNone(default_engine.text_extractor)
        self.assertIsNotNone(default_engine.standards_manager)
    
    @patch('core.curriculum_engine.CurriculumEngine._extract_content_from_sources')
    @patch('core.curriculum_engine.CurriculumEngine._generate_concepts_from_content')
    @patch('core.curriculum_engine.CurriculumEngine._augment_concepts_with_domain_knowledge')
    async def test_generate_curriculum(self, mock_augment, mock_generate, mock_extract):
        """Test complete curriculum generation."""
        # Setup mocks
        mock_extract.return_value = {'headings': [{'title': 'Test Heading', 'source': 'test.pdf'}]}
        
        mock_concept = CurriculumConcept(
            concept_id="test_001",
            title="Test Concept",
            description="Test Description",
            category="Test Category",
            subtopic="Test Subtopic",
            level="UG-Intro",
            bloom_taxonomy="Apply",
            standards="Test-Standard"
        )
        
        mock_generate.return_value = [mock_concept]
        mock_augment.return_value = [mock_concept]
        
        # Test generation
        content_sources = [Path("/fake/path/test.pdf")]
        curriculum = await self.engine.generate_curriculum(
            discipline="Test",
            content_sources=content_sources,
            target_size=100
        )
        
        self.assertIsInstance(curriculum, DisciplineCurriculum)
        self.assertEqual(curriculum.discipline, "Test")
        self.assertEqual(curriculum.total_concepts, 1)
        
        # Verify mocks were called
        mock_extract.assert_called_once()
        mock_generate.assert_called_once()
        mock_augment.assert_called_once()
    
    def test_level_order(self):
        """Test educational level ordering."""
        self.assertEqual(self.engine._level_order("HS-Found"), 1)
        self.assertEqual(self.engine._level_order("HS-Adv"), 2)
        self.assertEqual(self.engine._level_order("UG-Intro"), 3)
        self.assertEqual(self.engine._level_order("UG-Adv"), 4)
        self.assertEqual(self.engine._level_order("Grad-Intro"), 5)
        self.assertEqual(self.engine._level_order("Grad-Adv"), 6)
        self.assertEqual(self.engine._level_order("Unknown"), 3)  # Default
    
    def test_extract_keywords(self):
        """Test keyword extraction."""
        title = "Introduction to Quantum Mechanics and Wave Functions"
        keywords = self.engine._extract_keywords(title)
        
        self.assertIsInstance(keywords, list)
        self.assertLessEqual(len(keywords), 5)  # Should limit to 5
        self.assertIn("quantum", keywords)
        self.assertIn("mechanics", keywords)
        self.assertIn("wave", keywords)
        self.assertIn("functions", keywords)
    
    def test_extract_subtopic(self):
        """Test subtopic extraction."""
        # Test with chapter prefix
        title_with_prefix = "Chapter 5: Newton's Laws of Motion"
        subtopic = self.engine._extract_subtopic(title_with_prefix)
        self.assertEqual(subtopic, "Newton's Laws of Motion")
        
        # Test with introduction suffix
        title_with_suffix = "Quantum Mechanics Introduction"
        subtopic = self.engine._extract_subtopic(title_with_suffix)
        self.assertEqual(subtopic, "Quantum Mechanics")
        
        # Test clean title
        clean_title = "Conservation of Energy"
        subtopic = self.engine._extract_subtopic(clean_title)
        self.assertEqual(subtopic, "Conservation of Energy")
    
    def test_refine_level_assignment(self):
        """Test level assignment refinement."""
        # Test graduate-level concept
        grad_concept = CurriculumConcept(
            concept_id="test_001",
            title="Quantum Field Theory",
            description="Advanced quantum mechanics",
            category="Quantum Mechanics",
            subtopic="Field Theory",
            level="UG-Intro",
            bloom_taxonomy="Apply",
            standards="Test-Standard"
        )
        
        refined_level = self.engine._refine_level_assignment(grad_concept)
        self.assertEqual(refined_level, "Grad-Intro")
        
        # Test advanced concept
        adv_concept = CurriculumConcept(
            concept_id="test_002",
            title="Advanced Quantum Mechanics",
            description="Advanced quantum concepts",
            category="Quantum Mechanics",
            subtopic="Advanced Topics",
            level="HS-Found",
            bloom_taxonomy="Apply",
            standards="Test-Standard"
        )
        
        refined_level = self.engine._refine_level_assignment(adv_concept)
        self.assertEqual(refined_level, "HS-Adv")
    
    def test_get_curriculum_statistics(self):
        """Test curriculum statistics generation."""
        curriculum = DisciplineCurriculum(discipline="Test")
        
        concept1 = CurriculumConcept(
            concept_id="test_001",
            title="Test Concept 1",
            description="Description 1",
            category="Category A",
            subtopic="Subtopic 1",
            level="UG-Intro",
            bloom_taxonomy="Apply",
            standards="Test-Standard",
            difficulty_score=5.0,
            estimated_hours=2.0
        )
        
        concept2 = CurriculumConcept(
            concept_id="test_002",
            title="Test Concept 2",
            description="Description 2",
            category="Category B",
            subtopic="Subtopic 2",
            level="UG-Adv",
            bloom_taxonomy="Analyze",
            standards="Test-Standard",
            difficulty_score=7.0,
            estimated_hours=3.0
        )
        
        curriculum.add_concept(concept1)
        curriculum.add_concept(concept2)
        
        stats = self.engine.get_curriculum_statistics(curriculum)
        
        self.assertEqual(stats['total_concepts'], 2)
        self.assertEqual(stats['categories'], 2)
        self.assertEqual(stats['levels'], 2)
        self.assertEqual(stats['average_difficulty'], 6.0)
        self.assertEqual(stats['total_hours'], 5.0)
        
        self.assertIn('level_distribution', stats)
        self.assertIn('bloom_distribution', stats)
        self.assertIn('category_distribution', stats)
    
    def test_validate_curriculum(self):
        """Test curriculum validation."""
        curriculum = DisciplineCurriculum(discipline="Test")
        
        # Add some test concepts
        for i in range(5):
            concept = CurriculumConcept(
                concept_id=f"test_{i:03d}",
                title=f"Test Concept {i}",
                description=f"Description {i}",
                category=f"Category {i % 2}",  # Two categories
                subtopic=f"Subtopic {i}",
                level="UG-Intro",
                bloom_taxonomy="Apply",
                standards="Test-Standard"
            )
            curriculum.add_concept(concept)
        
        validation = self.engine.validate_curriculum(curriculum)
        
        self.assertIsInstance(validation, dict)
        self.assertIn('is_valid', validation)
        self.assertIn('warnings', validation)
        self.assertIn('errors', validation)
        
        # Should have warnings about few concepts and categories
        self.assertGreater(len(validation['warnings']), 0)


class TestCurriculumVisualizer(unittest.TestCase):
    """Test the CurriculumVisualizer class."""
    
    def setUp(self):
        """Set up test data."""
        self.visualizer = CurriculumVisualizer()
        
        # Create test curriculum data
        self.test_concepts = [
            CurriculumConcept(
                concept_id="physics_001",
                title="Newton's First Law",
                description="Object at rest stays at rest",
                category="Classical Mechanics",
                subtopic="Laws of Motion",
                level="HS-Found",
                bloom_taxonomy="Understand",
                standards="Intro-Core",
                difficulty_score=3.0,
                estimated_hours=2.0
            ),
            CurriculumConcept(
                concept_id="physics_002",
                title="Coulomb's Law",
                description="Electric force between charges",
                category="Electromagnetism",
                subtopic="Electric Force",
                level="HS-Adv",
                bloom_taxonomy="Apply",
                standards="AP-Physics",
                difficulty_score=5.0,
                estimated_hours=3.0
            )
        ]
        
        self.test_curriculum_data = {
            'discipline': 'Physics',
            'concepts': self.test_concepts,
            'prerequisite_graph': nx.DiGraph(),
            'exam_standards': {'AP-Physics'}
        }
    
    def test_visualizer_initialization(self):
        """Test visualizer initialization."""
        self.assertIsNotNone(self.visualizer.level_colors)
        self.assertIsNotNone(self.visualizer.bloom_colors)
        self.assertIn('HS-Found', self.visualizer.level_colors)
        self.assertIn('Understand', self.visualizer.bloom_colors)
    
    def test_create_heatmap_matrix(self):
        """Test heatmap matrix creation."""
        categories = ['Classical Mechanics', 'Electromagnetism']
        levels = ['HS-Found', 'HS-Adv', 'UG-Intro']
        
        matrix = self.visualizer._create_heatmap_matrix(
            self.test_concepts, categories, levels, 'concept_count'
        )
        
        self.assertEqual(matrix.shape, (2, 3))
        self.assertEqual(matrix[0, 0], 1)  # Classical Mechanics, HS-Found
        self.assertEqual(matrix[1, 1], 1)  # Electromagnetism, HS-Adv
        self.assertEqual(matrix[0, 1], 0)  # Classical Mechanics, HS-Adv (empty)
        
        # Test difficulty metric
        difficulty_matrix = self.visualizer._create_heatmap_matrix(
            self.test_concepts, categories, levels, 'difficulty'
        )
        
        self.assertEqual(difficulty_matrix[0, 0], 3.0)  # Newton's law difficulty
        self.assertEqual(difficulty_matrix[1, 1], 5.0)  # Coulomb's law difficulty
    
    def test_normalize_matrix(self):
        """Test matrix normalization."""
        test_matrix = np.array([[1, 2, 3], [4, 5, 6]])
        normalized = self.visualizer._normalize_matrix(test_matrix)
        
        # Each row should be normalized to [0, 1]
        self.assertAlmostEqual(np.max(normalized[0, :]), 1.0)
        self.assertAlmostEqual(np.max(normalized[1, :]), 1.0)
        self.assertAlmostEqual(normalized[0, 0], 1/3)
        self.assertAlmostEqual(normalized[0, 1], 2/3)
    
    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.close')
    async def test_generate_prerequisite_graph(self, mock_close, mock_savefig):
        """Test prerequisite graph generation."""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            output_path = Path(tmp_file.name)
        
        # Add prerequisite relationship
        graph = nx.DiGraph()
        graph.add_edge("physics_001", "physics_002")
        self.test_curriculum_data['prerequisite_graph'] = graph
        
        success = await self.visualizer.generate_prerequisite_graph(
            self.test_curriculum_data, output_path
        )
        
        self.assertTrue(success)
        mock_savefig.assert_called_once()
        mock_close.assert_called_once()
    
    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.close')
    async def test_generate_curriculum_heatmap(self, mock_close, mock_savefig):
        """Test curriculum heatmap generation."""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            output_path = Path(tmp_file.name)
        
        success = await self.visualizer.generate_curriculum_heatmap(
            self.test_curriculum_data, output_path
        )
        
        self.assertTrue(success)
        mock_savefig.assert_called_once()
        mock_close.assert_called_once()
    
    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.close')
    async def test_generate_learning_progression_chart(self, mock_close, mock_savefig):
        """Test learning progression chart generation."""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            output_path = Path(tmp_file.name)
        
        success = await self.visualizer.generate_learning_progression_chart(
            self.test_curriculum_data, output_path
        )
        
        self.assertTrue(success)
        mock_savefig.assert_called_once()
        mock_close.assert_called_once()


class TestCurriculumExporter(unittest.TestCase):
    """Test the CurriculumExporter class."""
    
    def setUp(self):
        """Set up test data."""
        self.exporter = CurriculumExporter()
        
        # Create test curriculum data
        self.test_concepts = [
            CurriculumConcept(
                concept_id="physics_001",
                title="Newton's First Law",
                description="Object at rest stays at rest",
                category="Classical Mechanics",
                subtopic="Laws of Motion",
                level="HS-Found",
                bloom_taxonomy="Understand",
                standards="Intro-Core",
                difficulty_score=3.0,
                estimated_hours=2.0,
                keywords=["newton", "inertia"],
                prerequisites=["Basic Kinematics"]
            )
        ]
        
        self.test_curriculum_data = {
            'discipline': 'Physics',
            'concepts': self.test_concepts,
            'prerequisite_graph': nx.DiGraph(),
            'exam_standards': {'AP-Physics'},
            'generation_time': '2024-01-01T12:00:00'
        }
    
    def test_exporter_initialization(self):
        """Test exporter initialization."""
        self.assertIsNotNone(self.exporter.logger)
    
    async def test_export_master_curriculum_csv(self):
        """Test CSV export functionality."""
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as tmp_file:
            output_path = Path(tmp_file.name)
        
        success = await self.exporter.export_master_curriculum_csv(
            self.test_curriculum_data, output_path
        )
        
        self.assertTrue(success)
        self.assertTrue(output_path.exists())
        
        # Verify CSV content
        df = pd.read_csv(output_path)
        self.assertEqual(len(df), 1)
        self.assertIn('Title', df.columns)
        self.assertIn('Category', df.columns)
        self.assertIn('Level', df.columns)
        self.assertEqual(df['Title'].iloc[0], "Newton's First Law")
        
        # Cleanup
        output_path.unlink()
    
    async def test_export_curriculum_json(self):
        """Test JSON export functionality."""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp_file:
            output_path = Path(tmp_file.name)
        
        success = await self.exporter.export_curriculum_json(
            self.test_curriculum_data, output_path
        )
        
        self.assertTrue(success)
        self.assertTrue(output_path.exists())
        
        # Verify JSON content
        with open(output_path, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data['discipline'], 'Physics')
        self.assertEqual(data['total_concepts'], 1)
        self.assertIn('concepts', data)
        self.assertIn('statistics', data)
        self.assertEqual(len(data['concepts']), 1)
        
        # Cleanup
        output_path.unlink()
    
    async def test_export_interactive_table_html(self):
        """Test HTML export functionality."""
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as tmp_file:
            output_path = Path(tmp_file.name)
        
        success = await self.exporter.export_interactive_table_html(
            self.test_curriculum_data, output_path
        )
        
        self.assertTrue(success)
        self.assertTrue(output_path.exists())
        
        # Verify HTML content
        with open(output_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        self.assertIn('<!DOCTYPE html>', html_content)
        self.assertIn('Physics Curriculum', html_content)
        self.assertIn('Newton\'s First Law', html_content)
        self.assertIn('DataTables', html_content)
        
        # Cleanup
        output_path.unlink()
    
    async def test_export_executive_summary_md(self):
        """Test Markdown export functionality."""
        with tempfile.NamedTemporaryFile(suffix='.md', delete=False) as tmp_file:
            output_path = Path(tmp_file.name)
        
        success = await self.exporter.export_executive_summary_md(
            self.test_curriculum_data, output_path
        )
        
        self.assertTrue(success)
        self.assertTrue(output_path.exists())
        
        # Verify Markdown content
        with open(output_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        self.assertIn('# Physics Curriculum', md_content)
        self.assertIn('## Overview', md_content)
        self.assertIn('Total Concepts**: 1', md_content)
        self.assertIn('## Curriculum Statistics', md_content)
        
        # Cleanup
        output_path.unlink()
    
    def test_format_level_distribution(self):
        """Test level distribution formatting."""
        from collections import Counter
        level_counts = Counter({'HS-Found': 10, 'UG-Intro': 20, 'Grad-Adv': 5})
        total = 35
        
        formatted = self.exporter._format_level_distribution(level_counts, total)
        
        self.assertIn('HS-Found**: 10 concepts (28.6%)', formatted)
        self.assertIn('UG-Intro**: 20 concepts (57.1%)', formatted)
        self.assertIn('Grad-Adv**: 5 concepts (14.3%)', formatted)
    
    def test_format_bloom_distribution(self):
        """Test Bloom's taxonomy distribution formatting."""
        from collections import Counter
        bloom_counts = Counter({'Understand': 15, 'Apply': 10, 'Analyze': 5})
        total = 30
        
        formatted = self.exporter._format_bloom_distribution(bloom_counts, total)
        
        self.assertIn('Understand**: 15 concepts (50.0%)', formatted)
        self.assertIn('Apply**: 10 concepts (33.3%)', formatted)
        self.assertIn('Analyze**: 5 concepts (16.7%)', formatted)


class TestCurriculumIntegration(unittest.TestCase):
    """Integration tests for the complete curriculum generation system."""
    
    async def test_end_to_end_curriculum_generation(self):
        """Test complete end-to-end curriculum generation workflow."""
        # This is a simplified integration test
        # In a real scenario, you would test with actual content sources
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create mock content source
            mock_pdf = temp_path / "test_physics.pdf"
            mock_pdf.touch()
            
            # Initialize components
            standards_manager = EducationalStandardsManager()
            visualizer = CurriculumVisualizer()
            exporter = CurriculumExporter()
            
            # Test standards manager
            physics_standards = standards_manager.get_exam_standards("Physics")
            self.assertTrue(len(physics_standards) > 0)
            
            # Test essential concepts
            essential_concepts = standards_manager.get_essential_concepts("Physics")
            self.assertTrue(len(essential_concepts) > 0)
            
            # Create test curriculum
            curriculum = DisciplineCurriculum(discipline="Physics")
            
            # Add some test concepts
            for i, (category, concepts) in enumerate(essential_concepts.items()):
                if i >= 2:  # Limit to first 2 categories for test
                    break
                for j, concept_info in enumerate(concepts[:3]):  # First 3 concepts per category
                    concept = CurriculumConcept(
                        concept_id=f"physics_{i:02d}_{j:02d}",
                        title=concept_info['title'],
                        description=concept_info['description'],
                        category=category,
                        subtopic=concept_info['title'],
                        level=concept_info['level'],
                        bloom_taxonomy="Understand",
                        standards="Test-Standard",
                        difficulty_score=concept_info['difficulty'],
                        estimated_hours=concept_info['hours']
                    )
                    curriculum.add_concept(concept)
            
            # Test curriculum has concepts
            self.assertGreater(curriculum.total_concepts, 0)
            
            # Test export functionality
            curriculum_data = {
                'discipline': curriculum.discipline,
                'concepts': curriculum.concepts,
                'prerequisite_graph': curriculum.prerequisite_graph,
                'exam_standards': curriculum.exam_standards,
                'generation_time': '2024-01-01T12:00:00'
            }
            
            # Test CSV export
            csv_path = temp_path / "test_curriculum.csv"
            csv_success = await exporter.export_master_curriculum_csv(curriculum_data, csv_path)
            self.assertTrue(csv_success)
            self.assertTrue(csv_path.exists())
            
            # Test JSON export
            json_path = temp_path / "test_curriculum.json"
            json_success = await exporter.export_curriculum_json(curriculum_data, json_path)
            self.assertTrue(json_success)
            self.assertTrue(json_path.exists())
    
    def test_curriculum_validation_edge_cases(self):
        """Test curriculum validation with edge cases."""
        engine = CurriculumEngine()
        
        # Test empty curriculum
        empty_curriculum = DisciplineCurriculum(discipline="Empty")
        validation = engine.validate_curriculum(empty_curriculum)
        self.assertFalse(validation['is_valid'])
        self.assertGreater(len(validation['warnings']), 0)
        
        # Test curriculum with circular prerequisites
        circular_curriculum = DisciplineCurriculum(discipline="Circular")
        concept1 = CurriculumConcept(
            concept_id="circ_001", title="Concept A", description="Description A",
            category="Category A", subtopic="Subtopic A", level="UG-Intro",
            bloom_taxonomy="Apply", standards="Test"
        )
        concept2 = CurriculumConcept(
            concept_id="circ_002", title="Concept B", description="Description B",
            category="Category A", subtopic="Subtopic B", level="UG-Intro",
            bloom_taxonomy="Apply", standards="Test"
        )
        
        circular_curriculum.add_concept(concept1)
        circular_curriculum.add_concept(concept2)
        
        # Create circular dependency
        circular_curriculum.prerequisite_graph.add_edge("circ_001", "circ_002")
        circular_curriculum.prerequisite_graph.add_edge("circ_002", "circ_001")
        
        validation = engine.validate_curriculum(circular_curriculum)
        self.assertFalse(validation['is_valid'])
        self.assertGreater(len(validation['errors']), 0)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)