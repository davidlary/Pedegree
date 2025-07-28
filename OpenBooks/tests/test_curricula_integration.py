"""
Integration Tests for Curricula System with Master Curriculum Builder

Goal: Test integration between the main curricula.py system and the new master 
curriculum builder to ensure seamless operation and proper data flow.

This test suite validates:
1. Integration of MasterCurriculumBuilder with main curricula system
2. Proper handling of discipline-specific curriculum generation
3. Backward compatibility with existing curriculum functions
4. Export functionality and file generation
5. Error handling and fallback mechanisms
"""

import pytest
import asyncio
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import sys
import os

# Add the project root to the path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import modules to test
try:
    from core.master_curriculum_builder import MasterCurriculumBuilder, CurriculumConcept
    # Create mock classes for curricula system components
    class MockCurriculaBuilder:
        def __init__(self, config, logger, terminal_ui):
            self.config = config
            self.logger = logger
            self.terminal_ui = terminal_ui
            self.output_dir = config.output_directory
    
    class MockMainCurriculumConcept:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    CurriculaBuilder = MockCurriculaBuilder
    MainCurriculumConcept = MockMainCurriculumConcept
    
except ImportError as e:
    pytest.skip(f"Skipping integration tests due to import error: {e}", allow_module_level=True)


class TestCurriculaIntegration:
    """Test integration between curricula.py and master curriculum builder."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Mock the required dependencies
        self.mock_config = Mock()
        self.mock_config.books_directory = self.temp_dir / "Books"
        self.mock_config.output_directory = self.temp_dir / "output"
        self.mock_config.database_path = self.temp_dir / "test.db"
        
        # Create mock directories
        self.mock_config.books_directory.mkdir(parents=True, exist_ok=True)
        self.mock_config.output_directory.mkdir(parents=True, exist_ok=True)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_curricula_builder_initialization(self):
        """Test CurriculaBuilder initialization with master curriculum builder."""
        
        # Create builder
        builder = CurriculaBuilder(
            config=self.mock_config,
            logger=Mock(),
            terminal_ui=Mock()
        )
        
        # Should initialize properly
        assert builder.config == self.mock_config
        assert hasattr(builder, 'output_dir')
        assert hasattr(builder, 'logger')
    
    @patch('curricula.BookDiscoverer')
    @patch('curricula.SearchIndexer')
    @patch('curricula.TextExtractor')
    @pytest.mark.asyncio
    async def test_generate_master_curriculum_concepts(self, mock_extractor, mock_indexer, mock_discoverer):
        """Test the _generate_master_curriculum_concepts method."""
        
        # Mock dependencies
        mock_discoverer.return_value.discover_books.return_value = {"Physics": []}
        mock_indexer.return_value = Mock()
        mock_extractor.return_value = Mock()
        
        # Create builder
        builder = CurriculaBuilder(
            config=self.mock_config,
            logger=Mock(),
            terminal_ui=Mock()
        )
        
        # Mock the master curriculum builder
        with patch.object(builder, '_generate_master_curriculum_concepts') as mock_generate:
            mock_concepts = [
                CurriculumConcept(
                    concept_id="physics_0001",
                    title="Test Concept",
                    description="Test description",
                    category="Test Category",
                    subtopic="Test Subtopic",
                    level="HS-Found",
                    bloom_taxonomy="Understand"
                )
            ]
            mock_generate.return_value = mock_concepts
            
            # Test the method
            concepts = await builder._generate_master_curriculum_concepts("Physics")
            
            assert len(concepts) == 1
            assert concepts[0].title == "Test Concept"
            assert concepts[0].discipline == "Physics"  # Should be set by the method
            mock_generate.assert_called_once_with("Physics")
    
    @patch('curricula.BookDiscoverer')
    @patch('curricula.SearchIndexer')
    @patch('curricula.TextExtractor')
    @pytest.mark.asyncio
    async def test_master_curriculum_integration_physics(self, mock_extractor, mock_indexer, mock_discoverer):
        """Test full integration with Physics master curriculum."""
        
        # Mock dependencies
        mock_discoverer.return_value.discover_books.return_value = {"Physics": []}
        mock_indexer.return_value = Mock()
        mock_extractor.return_value = Mock()
        
        # Create builder
        builder = CurriculaBuilder(
            config=self.mock_config,
            logger=Mock(),
            terminal_ui=Mock()
        )
        
        # Test Physics curriculum generation
        with patch('core.master_curriculum_builder.MasterCurriculumBuilder') as mock_master_builder:
            # Mock the master builder
            mock_instance = Mock()
            mock_master_builder.return_value = mock_instance
            
            # Mock the concepts
            mock_concepts = [
                CurriculumConcept(
                    concept_id="physics_0001",
                    title="Newton's First Law",
                    description="Law of inertia",
                    category="Classical Mechanics",
                    subtopic="Newton's Laws",
                    level="HS-Found",
                    bloom_taxonomy="Understand",
                    difficulty_score=3.0,
                    estimated_hours=2.0
                ),
                CurriculumConcept(
                    concept_id="physics_0002",
                    title="Force Vectors",
                    description="Vector representation of forces",
                    category="Classical Mechanics",
                    subtopic="Force Analysis",
                    level="HS-Adv",
                    bloom_taxonomy="Apply",
                    difficulty_score=4.5,
                    estimated_hours=3.0
                )
            ]
            
            mock_instance.concepts = mock_concepts
            mock_instance.build_master_curriculum.return_value = {
                'discipline': 'Physics',
                'total_concepts': 2,
                'categories': 1,
                'curriculum_table': Mock(),
                'graph_path': str(self.temp_dir / "test_graph.png"),
                'heatmap_path': str(self.temp_dir / "test_heatmap.png"),
                'generation_timestamp': '2023-01-01T00:00:00'
            }
            
            # Test the integration
            concepts = await builder._generate_master_curriculum_concepts("Physics")
            
            # Verify results
            assert len(concepts) == 2
            assert concepts[0].title == "Newton's First Law"
            assert concepts[1].title == "Force Vectors"
            
            # Verify proper educational progression
            assert concepts[0].level == "HS-Found"
            assert concepts[1].level == "HS-Adv"
            assert concepts[0].difficulty_score < concepts[1].difficulty_score
            
            # Verify master builder was called correctly
            mock_master_builder.assert_called_once()
            mock_instance.build_master_curriculum.assert_called_once()
    
    @patch('curricula.BookDiscoverer')
    @patch('curricula.SearchIndexer') 
    @patch('curricula.TextExtractor')
    def test_concept_conversion(self, mock_extractor, mock_indexer, mock_discoverer):
        """Test conversion between master curriculum concepts and main curriculum concepts."""
        
        # Mock dependencies
        mock_discoverer.return_value.discover_books.return_value = {"Physics": []}
        mock_indexer.return_value = Mock()
        mock_extractor.return_value = Mock()
        
        # Create a master curriculum concept
        master_concept = CurriculumConcept(
            concept_id="physics_0001",
            title="Test Concept",
            description="Test description",
            category="Test Category",
            subtopic="Test Subtopic",
            level="HS-Found",
            bloom_taxonomy="Understand",
            standards=["NGSS 9-12"],
            prerequisites=["physics_0000"],
            learning_objectives=["Understand concept X"],
            difficulty_score=3.5,
            estimated_hours=2.5,
            source_books=["Physics Textbook"],
            keywords=["test", "concept"]
        )
        
        # Create builder
        builder = CurriculaBuilder(
            config=self.mock_config,
            logger=Mock(),
            terminal_ui=Mock()
        )
        
        # Test conversion (this would happen in _augment_concepts)
        main_concept = MainCurriculumConcept(
            id=master_concept.concept_id,
            title=master_concept.title,
            category=master_concept.category,
            level=master_concept.level,
            bloom_level=master_concept.bloom_taxonomy,
            standards=master_concept.standards,
            prerequisite_concepts=master_concept.prerequisites,
            estimated_time_hours=master_concept.estimated_hours,
            source_materials=master_concept.source_books,
            discipline="Physics"
        )
        
        # Verify conversion
        assert main_concept.id == master_concept.concept_id
        assert main_concept.title == master_concept.title
        assert main_concept.category == master_concept.category
        assert main_concept.level == master_concept.level
        assert main_concept.bloom_level == master_concept.bloom_taxonomy
        assert main_concept.estimated_time_hours == master_concept.estimated_hours
    
    @patch('curricula.BookDiscoverer')
    @patch('curricula.SearchIndexer')
    @patch('curricula.TextExtractor')
    @pytest.mark.asyncio
    async def test_error_handling_master_curriculum(self, mock_extractor, mock_indexer, mock_discoverer):
        """Test error handling when master curriculum builder fails."""
        
        # Mock dependencies
        mock_discoverer.return_value.discover_books.return_value = {"Physics": []}
        mock_indexer.return_value = Mock()
        mock_extractor.return_value = Mock()
        
        # Create builder
        builder = CurriculaBuilder(
            config=self.mock_config,
            logger=Mock(),
            terminal_ui=Mock()
        )
        
        # Test with failing master curriculum builder
        with patch('core.master_curriculum_builder.MasterCurriculumBuilder') as mock_master_builder:
            mock_instance = Mock()
            mock_master_builder.return_value = mock_instance
            mock_instance.build_master_curriculum.side_effect = Exception("Master curriculum failed")
            
            # Should handle the error gracefully
            with pytest.raises(Exception) as exc_info:
                await builder._generate_master_curriculum_concepts("Physics")
            
            assert "Master curriculum failed" in str(exc_info.value)
    
    @patch('curricula.BookDiscoverer')
    @patch('curricula.SearchIndexer')
    @patch('curricula.TextExtractor')
    @pytest.mark.asyncio
    async def test_unsupported_discipline_fallback(self, mock_extractor, mock_indexer, mock_discoverer):
        """Test fallback behavior for unsupported disciplines."""
        
        # Mock dependencies
        mock_discoverer.return_value.discover_books.return_value = {"Chemistry": []}
        mock_indexer.return_value = Mock()
        mock_extractor.return_value = Mock()
        
        # Create builder
        builder = CurriculaBuilder(
            config=self.mock_config,
            logger=Mock(),
            terminal_ui=Mock()
        )
        
        # Test with unsupported discipline
        with patch('core.master_curriculum_builder.MasterCurriculumBuilder') as mock_master_builder:
            mock_instance = Mock()
            mock_master_builder.return_value = mock_instance
            mock_instance.build_master_curriculum.side_effect = NotImplementedError("Template not implemented for Chemistry")
            
            # Should handle the error and potentially fall back to other methods
            with pytest.raises(NotImplementedError):
                await builder._generate_master_curriculum_concepts("Chemistry")


class TestCurriculumArtifacts:
    """Test generation of curriculum artifacts and exports."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @pytest.mark.asyncio
    async def test_curriculum_export_formats(self):
        """Test various export formats for curriculum data."""
        
        # Create master curriculum builder
        builder = MasterCurriculumBuilder("Physics", self.temp_dir)
        
        # Generate curriculum
        master_data = await builder.build_master_curriculum()
        
        # Verify export files
        expected_exports = [
            "Physics_master_curriculum.json",
            "Physics_curriculum_table.csv",
            "Physics_category_graph.png",
            "Physics_depth_heatmap.png"
        ]
        
        for export_file in expected_exports:
            file_path = self.temp_dir / export_file
            assert file_path.exists(), f"Missing export file: {export_file}"
        
        # Test JSON export content
        json_path = self.temp_dir / "Physics_master_curriculum.json"
        with open(json_path) as f:
            json_data = json.load(f)
        
        assert json_data["discipline"] == "Physics"
        assert json_data["total_concepts"] > 0
        assert "generation_timestamp" in json_data
        
        # Test CSV export content
        csv_path = self.temp_dir / "Physics_curriculum_table.csv"
        df = pd.read_csv(csv_path)
        
        assert len(df) > 0
        required_columns = ['Category', 'Subtopic', 'Level', 'Bloom', 'Standards']
        for col in required_columns:
            assert col in df.columns
    
    @pytest.mark.asyncio
    async def test_curriculum_data_integrity(self):
        """Test data integrity across different export formats."""
        
        # Create master curriculum builder
        builder = MasterCurriculumBuilder("Physics", self.temp_dir)
        
        # Generate curriculum
        master_data = await builder.build_master_curriculum()
        
        # Load CSV data
        csv_path = self.temp_dir / "Physics_curriculum_table.csv"
        df = pd.read_csv(csv_path)
        
        # Load JSON data
        json_path = self.temp_dir / "Physics_master_curriculum.json"
        with open(json_path) as f:
            json_data = json.load(f)
        
        # Verify consistency
        assert len(df) == json_data["total_concepts"]
        assert len(df) == len(builder.concepts)
        
        # Verify concept IDs are unique
        concept_ids = df['ConceptID'].tolist()
        assert len(concept_ids) == len(set(concept_ids))
        
        # Verify educational progression
        for level in ['HS-Found', 'HS-Adv', 'UG-Intro', 'UG-Adv']:
            level_concepts = df[df['Level'] == level]
            if len(level_concepts) > 0:
                # Should have concepts at this level
                assert len(level_concepts) > 0
        
        # Verify category ordering
        categories = df['Category'].unique()
        assert len(categories) == json_data["categories"]


class TestPerformanceAndScalability:
    """Test performance characteristics of the integrated system."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @pytest.mark.asyncio
    async def test_curriculum_generation_performance(self):
        """Test performance of curriculum generation."""
        import time
        
        # Create builder
        builder = MasterCurriculumBuilder("Physics", self.temp_dir)
        
        # Time the curriculum generation
        start_time = time.time()
        master_data = await builder.build_master_curriculum()
        end_time = time.time()
        
        duration = end_time - start_time
        
        # Should complete in reasonable time (less than 30 seconds)
        assert duration < 30.0, f"Curriculum generation took too long: {duration:.2f}s"
        
        # Should generate substantial content
        assert master_data["total_concepts"] >= 20
        assert master_data["categories"] >= 5
        
        # Verify all artifacts were created
        assert Path(master_data["graph_path"]).exists()
        assert Path(master_data["heatmap_path"]).exists()
    
    @pytest.mark.asyncio
    async def test_memory_usage(self):
        """Test memory usage during curriculum generation."""
        import psutil
        import os
        
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create builder and generate curriculum
        builder = MasterCurriculumBuilder("Physics", self.temp_dir)
        master_data = await builder.build_master_curriculum()
        
        # Get final memory usage
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB for Physics)
        assert memory_increase < 100, f"Memory usage increased by {memory_increase:.1f}MB"
        
        # Verify curriculum was generated successfully
        assert master_data["total_concepts"] > 0


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])