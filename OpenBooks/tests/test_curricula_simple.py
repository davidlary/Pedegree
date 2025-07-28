"""
Simplified Integration Tests for Master Curriculum Builder

Goal: Basic integration testing to ensure master curriculum builder works
with the core system components without complex dependencies.

This simplified test suite validates:
1. Master curriculum builder functionality
2. Basic integration patterns
3. Core data structures and exports
"""

import pytest
import asyncio
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch
import pandas as pd
import sys
import os

# Add the project root to the path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.master_curriculum_builder import MasterCurriculumBuilder, CurriculumConcept


class TestMasterCurriculumBuilderSimple:
    """Simplified tests for master curriculum builder integration."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @pytest.mark.asyncio
    async def test_basic_curriculum_generation(self):
        """Test basic curriculum generation functionality."""
        
        # Create master curriculum builder
        builder = MasterCurriculumBuilder("Physics", self.temp_dir)
        
        # Generate curriculum
        master_data = await builder.build_master_curriculum()
        
        # Verify basic results
        assert isinstance(master_data, dict)
        assert master_data["discipline"] == "Physics"
        assert master_data["total_concepts"] > 0
        assert master_data["categories"] > 0
        
        # Verify files were created
        json_path = self.temp_dir / "Physics_master_curriculum.json"
        csv_path = self.temp_dir / "Physics_curriculum_table.csv"
        graph_path = Path(master_data["graph_path"])
        heatmap_path = Path(master_data["heatmap_path"])
        
        assert json_path.exists()
        assert csv_path.exists()
        assert graph_path.exists()
        assert heatmap_path.exists()
    
    @pytest.mark.asyncio
    async def test_curriculum_data_structure(self):
        """Test the structure of generated curriculum data."""
        
        builder = MasterCurriculumBuilder("Physics", self.temp_dir)
        master_data = await builder.build_master_curriculum()
        
        # Test concepts structure
        assert len(builder.concepts) > 0
        
        first_concept = builder.concepts[0]
        assert hasattr(first_concept, 'concept_id')
        assert hasattr(first_concept, 'title')
        assert hasattr(first_concept, 'category')
        assert hasattr(first_concept, 'level')
        assert hasattr(first_concept, 'bloom_taxonomy')
        
        # Test educational progression
        levels_found = set()
        for concept in builder.concepts:
            levels_found.add(concept.level)
        
        # Should have foundational concepts
        assert "HS-Found" in levels_found
        
        # Should have proper ordering
        for concept in builder.concepts:
            assert concept.difficulty_score >= 0.0
            assert concept.estimated_hours > 0.0
    
    @pytest.mark.asyncio
    async def test_csv_export_structure(self):
        """Test the CSV export structure and content."""
        
        builder = MasterCurriculumBuilder("Physics", self.temp_dir)
        await builder.build_master_curriculum()
        
        # Load CSV
        csv_path = self.temp_dir / "Physics_curriculum_table.csv"
        df = pd.read_csv(csv_path)
        
        # Test structure
        required_columns = ['Category', 'Subtopic', 'Level', 'Bloom', 'Standards']
        for col in required_columns:
            assert col in df.columns
        
        # Test content
        assert len(df) > 0
        
        # Test educational levels
        levels = df['Level'].unique()
        assert 'HS-Found' in levels
        
        # Test categories
        categories = df['Category'].unique()
        assert len(categories) > 1
        
        # Test ordering
        assert df['CategoryOrder'].is_monotonic_increasing or \
               df.groupby('Category')['Sequence'].apply(lambda x: x.is_monotonic_increasing).all()
    
    def test_concept_creation_patterns(self):
        """Test different patterns of concept creation."""
        
        # Test basic concept
        concept1 = CurriculumConcept(
            concept_id="test_001",
            title="Basic Concept",
            description="A basic test concept",
            category="Test Category",
            subtopic="Basic",
            level="HS-Found",
            bloom_taxonomy="Understand"
        )
        
        assert concept1.concept_id == "test_001"
        assert concept1.level == "HS-Found"
        
        # Test advanced concept
        concept2 = CurriculumConcept(
            concept_id="test_002", 
            title="Advanced Concept",
            description="An advanced test concept",
            category="Test Category",
            subtopic="Advanced",
            level="UG-Adv",
            bloom_taxonomy="Analyze",
            prerequisites=["test_001"],
            difficulty_score=7.0,
            estimated_hours=4.0
        )
        
        assert concept2.prerequisites == ["test_001"]
        assert concept2.difficulty_score == 7.0
        assert concept2.level == "UG-Adv"
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling in various scenarios."""
        
        # Test unsupported discipline
        builder = MasterCurriculumBuilder("UnsupportedSubject", self.temp_dir)
        
        with pytest.raises(NotImplementedError):
            await builder.build_master_curriculum()
    
    @pytest.mark.asyncio
    async def test_performance_characteristics(self):
        """Test basic performance characteristics."""
        import time
        
        builder = MasterCurriculumBuilder("Physics", self.temp_dir)
        
        start_time = time.time()
        master_data = await builder.build_master_curriculum()
        end_time = time.time()
        
        duration = end_time - start_time
        
        # Should complete in reasonable time
        assert duration < 60.0  # Less than 1 minute
        
        # Should generate substantial content
        assert master_data["total_concepts"] >= 10
        assert master_data["categories"] >= 3


class TestCurriculumDataIntegration:
    """Test curriculum data integration patterns."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @pytest.mark.asyncio
    async def test_data_consistency(self):
        """Test consistency between different data exports."""
        
        builder = MasterCurriculumBuilder("Physics", self.temp_dir)
        master_data = await builder.build_master_curriculum()
        
        # Load exports
        json_path = self.temp_dir / "Physics_master_curriculum.json"
        csv_path = self.temp_dir / "Physics_curriculum_table.csv"
        
        with open(json_path) as f:
            json_data = json.load(f)
        
        df = pd.read_csv(csv_path)
        
        # Test consistency
        assert json_data["total_concepts"] == len(df)
        assert json_data["total_concepts"] == len(builder.concepts)
        assert json_data["discipline"] == "Physics"
        
        # Test unique IDs
        concept_ids = df['ConceptID'].tolist()
        assert len(concept_ids) == len(set(concept_ids))
    
    @pytest.mark.asyncio
    async def test_educational_progression_logic(self):
        """Test educational progression logic."""
        
        builder = MasterCurriculumBuilder("Physics", self.temp_dir)
        await builder.build_master_curriculum()
        
        # Test progression logic
        progression = builder.progression
        
        assert progression.get_level_order("HS-Found") < progression.get_level_order("HS-Adv")
        assert progression.get_level_order("HS-Adv") < progression.get_level_order("UG-Intro")
        assert progression.get_level_order("UG-Intro") < progression.get_level_order("UG-Adv")
        
        assert progression.get_bloom_order("Understand") < progression.get_bloom_order("Apply")
        assert progression.get_bloom_order("Apply") < progression.get_bloom_order("Analyze")
        
        # Test standards mapping
        assert "NGSS 9-12" in progression.standards_by_level["HS-Found"]
        assert "AP" in progression.standards_by_level["HS-Adv"]


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])