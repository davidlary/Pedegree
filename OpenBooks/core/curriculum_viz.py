"""
core/curriculum_viz.py - Curriculum Visualization and Export Engine

Goal: Provide comprehensive visualization and export capabilities for curriculum data,
including prerequisite graphs, heatmaps, interactive tables, and multiple export formats.

This module handles all visualization and export functionality for curriculum generation,
creating publication-ready graphics and interactive educational materials.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import warnings

import networkx as nx
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.colors import ListedColormap
from collections import Counter, defaultdict

# Suppress matplotlib warnings for cleaner output
warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')
plt.style.use('default')


class CurriculumVisualizer:
    """
    Comprehensive visualization engine for curriculum data.
    
    Creates publication-ready visualizations including prerequisite graphs,
    curriculum heatmaps, learning progressions, and interactive displays.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize the visualization engine.
        
        Args:
            logger: Optional logging system
        """
        self.logger = logger or logging.getLogger(__name__)
        
        # Color schemes for different educational levels
        self.level_colors = {
            'HS-Found': '#FFE6E6',    # Light red
            'HS-Adv': '#FFB3B3',      # Medium red
            'UG-Intro': '#E6F2FF',    # Light blue
            'UG-Adv': '#B3D9FF',      # Medium blue
            'Grad-Intro': '#E6FFE6',  # Light green
            'Grad-Adv': '#B3FFB3'     # Medium green
        }
        
        # Bloom's taxonomy colors
        self.bloom_colors = {
            'Understand': '#E8F4FD',
            'Apply': '#D1E7DD',
            'Analyze': '#FFF3CD',
            'Evaluate': '#F8D7DA',
            'Create': '#E2E3E5'
        }
    
    async def generate_prerequisite_graph(self, 
                                        curriculum_data: Dict[str, Any],
                                        output_path: Path,
                                        layout: str = 'spring',
                                        show_labels: bool = True,
                                        filter_by_difficulty: Optional[float] = None) -> bool:
        """
        Generate prerequisite relationship graph visualization.
        
        Args:
            curriculum_data: Dictionary containing curriculum information
            output_path: Path where to save the graph image
            layout: Graph layout algorithm ('spring', 'hierarchical', 'circular')
            show_labels: Whether to show concept labels
            filter_by_difficulty: Only show concepts above this difficulty threshold
        
        Returns:
            True if successful, False otherwise
        """
        
        try:
            # Extract graph and concepts
            prerequisite_graph = curriculum_data.get('prerequisite_graph', nx.DiGraph())
            concepts = curriculum_data.get('concepts', [])
            discipline = curriculum_data.get('discipline', 'Unknown')
            
            if not concepts:
                self.logger.warning("No concepts found for prerequisite graph")
                return False
            
            # Filter concepts by difficulty if specified
            if filter_by_difficulty is not None:
                concepts = [c for c in concepts if c.difficulty_score >= filter_by_difficulty]
                # Rebuild graph with filtered concepts
                concept_ids = {c.concept_id for c in concepts}
                prerequisite_graph = prerequisite_graph.subgraph(concept_ids)
            
            # Create figure
            fig, ax = plt.subplots(figsize=(16, 12))
            
            # Choose layout
            if layout == 'spring':
                pos = nx.spring_layout(prerequisite_graph, k=3, iterations=50, seed=42)
            elif layout == 'hierarchical':
                pos = self._hierarchical_layout(prerequisite_graph, concepts)
            elif layout == 'circular':
                pos = nx.circular_layout(prerequisite_graph)
            else:
                pos = nx.spring_layout(prerequisite_graph, k=3, iterations=50, seed=42)
            
            # Prepare node visualization data
            node_colors = []
            node_sizes = []
            concept_map = {c.concept_id: c for c in concepts}
            
            for node_id in prerequisite_graph.nodes():
                concept = concept_map.get(node_id)
                if concept:
                    # Color by educational level
                    node_colors.append(self.level_colors.get(concept.level, '#CCCCCC'))
                    # Size by difficulty and importance
                    base_size = 300
                    difficulty_factor = concept.difficulty_score * 50
                    importance_factor = 100 if 'fundamental' in concept.title.lower() else 0
                    node_sizes.append(base_size + difficulty_factor + importance_factor)
                else:
                    node_colors.append('#CCCCCC')
                    node_sizes.append(300)
            
            # Draw nodes
            nx.draw_networkx_nodes(prerequisite_graph, pos, 
                                 node_color=node_colors, 
                                 node_size=node_sizes, 
                                 alpha=0.8, 
                                 ax=ax)
            
            # Draw edges with different styles for different relationship types
            self._draw_styled_edges(prerequisite_graph, pos, concepts, ax)
            
            # Add labels if requested
            if show_labels:
                self._add_concept_labels(prerequisite_graph, pos, concepts, ax, filter_by_difficulty)
            
            # Set title and styling
            title = f"{discipline} - Prerequisite Relationships"
            if filter_by_difficulty is not None:
                title += f" (Difficulty ≥ {filter_by_difficulty})"
            
            ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
            ax.axis('off')
            
            # Add legend
            self._add_level_legend(ax)
            
            # Add statistics
            stats_text = f"Concepts: {len(concepts)}\nRelationships: {prerequisite_graph.number_of_edges()}"
            ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=10,
                   verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            
            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
            self.logger.info(f"Generated prerequisite graph: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to generate prerequisite graph: {e}")
            return False
    
    async def generate_curriculum_heatmap(self,
                                        curriculum_data: Dict[str, Any],
                                        output_path: Path,
                                        metric: str = 'concept_count',
                                        normalize: bool = True) -> bool:
        """
        Generate curriculum heatmap showing concept density by category and level.
        
        Args:
            curriculum_data: Dictionary containing curriculum information
            output_path: Path where to save the heatmap image
            metric: Metric to visualize ('concept_count', 'difficulty', 'hours')
            normalize: Whether to normalize values for better visualization
        
        Returns:
            True if successful, False otherwise
        """
        
        try:
            concepts = curriculum_data.get('concepts', [])
            discipline = curriculum_data.get('discipline', 'Unknown')
            exam_standards = curriculum_data.get('exam_standards', set())
            
            if not concepts:
                self.logger.warning("No concepts found for heatmap")
                return False
            
            # Prepare data matrix
            categories = sorted(list(set(c.category for c in concepts)))
            levels = ['HS-Found', 'HS-Adv', 'UG-Intro', 'UG-Adv', 'Grad-Intro', 'Grad-Adv']
            
            # Create matrix based on selected metric
            matrix = self._create_heatmap_matrix(concepts, categories, levels, metric)
            
            # Add aggregate row for exam standards
            if exam_standards:
                primary_exam = next(iter(exam_standards))
                categories.append(f"Aggregate ({primary_exam})")
                
                if metric == 'concept_count':
                    # Sum counts across all categories
                    exam_row = np.sum(matrix, axis=0).reshape(1, -1)
                else:
                    # Average for other metrics
                    exam_row = np.mean(matrix, axis=0).reshape(1, -1)
                
                matrix = np.vstack([matrix, exam_row])
            
            # Normalize if requested
            if normalize and metric != 'concept_count':
                matrix = self._normalize_matrix(matrix)
            
            # Create heatmap
            fig, ax = plt.subplots(figsize=(12, max(8, len(categories) * 0.5)))
            
            # Create custom colormap with white background for zeros
            if metric == 'concept_count':
                colors = ['white'] + plt.cm.YlOrRd(np.linspace(0.1, 1, 256)).tolist()
            elif metric == 'difficulty':
                colors = ['white'] + plt.cm.Reds(np.linspace(0.1, 1, 256)).tolist()
            else:  # hours
                colors = ['white'] + plt.cm.Blues(np.linspace(0.1, 1, 256)).tolist()
            
            custom_cmap = ListedColormap(colors)
            
            # Calculate appropriate vmax (98th percentile for better visualization)
            vmax = np.percentile(matrix[matrix > 0], 98) if np.any(matrix > 0) else 1
            
            # Create heatmap
            im = ax.imshow(matrix, cmap=custom_cmap, vmin=0, vmax=vmax, aspect='auto')
            
            # Set ticks and labels
            ax.set_xticks(range(len(levels)))
            ax.set_yticks(range(len(categories)))
            ax.set_xticklabels(levels, rotation=45, ha='right')
            ax.set_yticklabels(categories)
            
            # Add value annotations
            self._add_heatmap_annotations(matrix, ax, vmax, metric)
            
            # Set title and labels
            metric_names = {
                'concept_count': 'Concept Count',
                'difficulty': 'Average Difficulty',
                'hours': 'Total Hours'
            }
            
            title = f"{discipline} - Curriculum Heatmap\n({metric_names.get(metric, metric)} by Category and Level)"
            ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
            ax.set_xlabel('Educational Level', fontsize=12)
            ax.set_ylabel('Subject Category', fontsize=12)
            
            # Add colorbar
            cbar = plt.colorbar(im, ax=ax, shrink=0.8)
            cbar.set_label(metric_names.get(metric, metric), rotation=270, labelpad=20)
            
            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
            self.logger.info(f"Generated curriculum heatmap: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to generate curriculum heatmap: {e}")
            return False
    
    async def generate_learning_progression_chart(self,
                                                curriculum_data: Dict[str, Any],
                                                output_path: Path,
                                                category: Optional[str] = None) -> bool:
        """
        Generate learning progression chart showing concept flow over educational levels.
        
        Args:
            curriculum_data: Dictionary containing curriculum information
            output_path: Path where to save the chart
            category: Optional category to focus on (if None, shows all categories)
        
        Returns:
            True if successful, False otherwise
        """
        
        try:
            concepts = curriculum_data.get('concepts', [])
            discipline = curriculum_data.get('discipline', 'Unknown')
            
            if not concepts:
                self.logger.warning("No concepts found for learning progression chart")
                return False
            
            # Filter by category if specified
            if category:
                concepts = [c for c in concepts if c.category == category]
                if not concepts:
                    self.logger.warning(f"No concepts found for category: {category}")
                    return False
            
            # Create progression data
            levels = ['HS-Found', 'HS-Adv', 'UG-Intro', 'UG-Adv', 'Grad-Intro', 'Grad-Adv']
            bloom_levels = ['Understand', 'Apply', 'Analyze', 'Evaluate', 'Create']
            
            # Count concepts by level and Bloom's taxonomy
            progression_data = defaultdict(lambda: defaultdict(int))
            
            for concept in concepts:
                progression_data[concept.level][concept.bloom_taxonomy] += 1
            
            # Create stacked bar chart
            fig, ax = plt.subplots(figsize=(14, 8))
            
            # Prepare data for stacked bars
            level_counts = {level: 0 for level in levels}
            bloom_data = {bloom: [] for bloom in bloom_levels}
            
            for level in levels:
                level_total = 0
                for bloom in bloom_levels:
                    count = progression_data[level][bloom]
                    bloom_data[bloom].append(count)
                    level_total += count
                level_counts[level] = level_total
            
            # Create stacked bars
            bottom = np.zeros(len(levels))
            for bloom in bloom_levels:
                ax.bar(levels, bloom_data[bloom], bottom=bottom, 
                      label=bloom, color=self.bloom_colors.get(bloom, '#CCCCCC'),
                      alpha=0.8, edgecolor='white', linewidth=0.5)
                bottom += bloom_data[bloom]
            
            # Customize chart
            title = f"{discipline} - Learning Progression"
            if category:
                title += f" ({category})"
            
            ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel('Educational Level', fontsize=12)
            ax.set_ylabel('Number of Concepts', fontsize=12)
            ax.legend(title="Bloom's Taxonomy", bbox_to_anchor=(1.05, 1), loc='upper left')
            
            # Add value labels on bars
            for i, level in enumerate(levels):
                total = level_counts[level]
                if total > 0:
                    ax.text(i, total + 0.5, str(total), ha='center', va='bottom', fontweight='bold')
            
            # Rotate x-axis labels for better readability
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
            self.logger.info(f"Generated learning progression chart: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to generate learning progression chart: {e}")
            return False
    
    def _hierarchical_layout(self, graph: nx.DiGraph, concepts: List[Any]) -> Dict[str, Tuple[float, float]]:
        """Create hierarchical layout based on educational levels."""
        
        # Group concepts by level
        level_groups = defaultdict(list)
        concept_map = {c.concept_id: c for c in concepts}
        
        for node_id in graph.nodes():
            concept = concept_map.get(node_id)
            if concept:
                level_groups[concept.level].append(node_id)
        
        # Assign positions
        pos = {}
        levels = ['HS-Found', 'HS-Adv', 'UG-Intro', 'UG-Adv', 'Grad-Intro', 'Grad-Adv']
        
        for level_idx, level in enumerate(levels):
            nodes_in_level = level_groups[level]
            if nodes_in_level:
                y_pos = len(levels) - level_idx - 1  # Higher levels at top
                
                # Distribute nodes horizontally within level
                for node_idx, node_id in enumerate(nodes_in_level):
                    x_pos = (node_idx - len(nodes_in_level) / 2) / max(len(nodes_in_level), 1)
                    pos[node_id] = (x_pos, y_pos)
        
        return pos
    
    def _draw_styled_edges(self, graph: nx.DiGraph, pos: Dict, concepts: List[Any], ax):
        """Draw edges with different styles based on relationship strength."""
        
        concept_map = {c.concept_id: c for c in concepts}
        
        # Categorize edges by relationship type
        strong_edges = []  # Same category
        medium_edges = []  # Related categories
        weak_edges = []    # Different categories
        
        for source, target in graph.edges():
            source_concept = concept_map.get(source)
            target_concept = concept_map.get(target)
            
            if source_concept and target_concept:
                if source_concept.category == target_concept.category:
                    strong_edges.append((source, target))
                else:
                    # Simple heuristic for relationship strength
                    if any(word in source_concept.category.lower() for word in target_concept.category.lower().split()):
                        medium_edges.append((source, target))
                    else:
                        weak_edges.append((source, target))
        
        # Draw edges with different styles
        if strong_edges:
            nx.draw_networkx_edges(graph, pos, edgelist=strong_edges,
                                 edge_color='darkblue', arrows=True, alpha=0.8,
                                 width=2, ax=ax)
        
        if medium_edges:
            nx.draw_networkx_edges(graph, pos, edgelist=medium_edges,
                                 edge_color='blue', arrows=True, alpha=0.6,
                                 width=1.5, style='--', ax=ax)
        
        if weak_edges:
            nx.draw_networkx_edges(graph, pos, edgelist=weak_edges,
                                 edge_color='gray', arrows=True, alpha=0.4,
                                 width=1, ax=ax)
    
    def _add_concept_labels(self, graph: nx.DiGraph, pos: Dict, concepts: List[Any], ax, 
                          filter_by_difficulty: Optional[float] = None):
        """Add concept labels to the graph."""
        
        concept_map = {c.concept_id: c for c in concepts}
        
        # Select which concepts to label
        labeled_concepts = {}
        for node_id in graph.nodes():
            concept = concept_map.get(node_id)
            if concept:
                # Label high-difficulty concepts or fundamental concepts
                should_label = (
                    (filter_by_difficulty is None and concept.difficulty_score >= 7.0) or
                    (filter_by_difficulty is not None and concept.difficulty_score >= filter_by_difficulty) or
                    'fundamental' in concept.title.lower() or
                    'law' in concept.title.lower()
                )
                
                if should_label:
                    # Truncate long labels
                    label = concept.title[:25] + '...' if len(concept.title) > 25 else concept.title
                    labeled_concepts[node_id] = label
        
        # Draw labels
        if labeled_concepts:
            nx.draw_networkx_labels(graph, pos, labels=labeled_concepts, 
                                  font_size=8, font_weight='bold', ax=ax)
    
    def _add_level_legend(self, ax):
        """Add educational level legend to the plot."""
        
        legend_elements = []
        for level, color in self.level_colors.items():
            legend_elements.append(plt.Rectangle((0, 0), 1, 1, facecolor=color, 
                                               label=level.replace('-', ' ')))
        
        ax.legend(handles=legend_elements, title='Educational Levels',
                 loc='upper left', bbox_to_anchor=(0, 1))
    
    def _create_heatmap_matrix(self, concepts: List[Any], categories: List[str], 
                             levels: List[str], metric: str) -> np.ndarray:
        """Create matrix for heatmap visualization."""
        
        matrix = np.zeros((len(categories), len(levels)))
        
        # Organize concepts by category and level
        category_level_data = defaultdict(lambda: defaultdict(list))
        
        for concept in concepts:
            category_level_data[concept.category][concept.level].append(concept)
        
        # Fill matrix based on metric
        for i, category in enumerate(categories):
            for j, level in enumerate(levels):
                concepts_in_cell = category_level_data[category][level]
                
                if concepts_in_cell:
                    if metric == 'concept_count':
                        matrix[i, j] = len(concepts_in_cell)
                    elif metric == 'difficulty':
                        matrix[i, j] = np.mean([c.difficulty_score for c in concepts_in_cell])
                    elif metric == 'hours':
                        matrix[i, j] = sum(c.estimated_hours for c in concepts_in_cell)
                    else:
                        matrix[i, j] = len(concepts_in_cell)  # Default to count
        
        return matrix
    
    def _normalize_matrix(self, matrix: np.ndarray) -> np.ndarray:
        """Normalize matrix values for better visualization."""
        
        # Normalize each row to [0, 1] range
        normalized = np.zeros_like(matrix)
        
        for i in range(matrix.shape[0]):
            row = matrix[i, :]
            if np.max(row) > 0:
                normalized[i, :] = row / np.max(row)
        
        return normalized
    
    def _add_heatmap_annotations(self, matrix: np.ndarray, ax, vmax: float, metric: str):
        """Add value annotations to heatmap cells."""
        
        for i in range(matrix.shape[0]):
            for j in range(matrix.shape[1]):
                value = matrix[i, j]
                if value > 0:
                    # Choose text color based on cell brightness
                    text_color = 'white' if value > vmax * 0.6 else 'black'
                    
                    # Format value based on metric
                    if metric == 'concept_count':
                        text = str(int(value))
                    elif metric in ['difficulty', 'hours']:
                        text = f"{value:.1f}"
                    else:
                        text = str(int(value))
                    
                    ax.text(j, i, text, ha='center', va='center', 
                           color=text_color, fontweight='bold', fontsize=10)


class CurriculumExporter:
    """
    Comprehensive export engine for curriculum data.
    
    Provides multiple export formats including CSV, JSON, interactive HTML,
    and specialized educational formats.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize the export engine.
        
        Args:
            logger: Optional logging system
        """
        self.logger = logger or logging.getLogger(__name__)
    
    async def export_master_curriculum_csv(self, 
                                         curriculum_data: Dict[str, Any],
                                         output_path: Path) -> bool:
        """Export master curriculum as CSV file."""
        
        try:
            concepts = curriculum_data.get('concepts', [])
            
            if not concepts:
                self.logger.warning("No concepts to export")
                return False
            
            # Prepare CSV data
            csv_data = []
            for concept in concepts:
                csv_data.append({
                    'Category': concept.category,
                    'Subtopic': concept.subtopic,
                    'Level': concept.level,
                    'Bloom': concept.bloom_taxonomy,
                    'Standards': concept.standards,
                    'Title': concept.title,
                    'Description': concept.description,
                    'Prerequisites': ', '.join(concept.prerequisites) if concept.prerequisites else '',
                    'Keywords': ', '.join(concept.keywords) if concept.keywords else '',
                    'Difficulty': concept.difficulty_score,
                    'Hours': concept.estimated_hours,
                    'Source_Books': ', '.join(concept.source_books) if concept.source_books else '',
                    'Learning_Objectives': ', '.join(concept.learning_objectives) if concept.learning_objectives else ''
                })
            
            # Create and save DataFrame
            df = pd.DataFrame(csv_data)
            df.to_csv(output_path, index=False, encoding='utf-8')
            
            self.logger.info(f"Exported master curriculum CSV: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export CSV: {e}")
            return False
    
    async def export_interactive_table_html(self,
                                           curriculum_data: Dict[str, Any],
                                           output_path: Path) -> bool:
        """Export interactive HTML table with DataTables integration."""
        
        try:
            concepts = curriculum_data.get('concepts', [])
            discipline = curriculum_data.get('discipline', 'Unknown')
            
            if not concepts:
                self.logger.warning("No concepts to export")
                return False
            
            # Prepare table data
            table_data = []
            for concept in concepts:
                table_data.append({
                    'ID': concept.concept_id,
                    'Title': concept.title,
                    'Category': concept.category,
                    'Subtopic': concept.subtopic,
                    'Level': concept.level,
                    "Bloom's Taxonomy": concept.bloom_taxonomy,
                    'Standards': concept.standards,
                    'Difficulty': f"{concept.difficulty_score:.1f}",
                    'Hours': f"{concept.estimated_hours:.1f}",
                    'Keywords': ', '.join(concept.keywords[:3]) if concept.keywords else '',
                    'Description': concept.description[:100] + '...' if len(concept.description) > 100 else concept.description
                })
            
            # Create DataFrame and styled table
            df = pd.DataFrame(table_data)
            
            # Apply styling
            styled_df = df.style \
                .set_table_attributes('class="table table-striped table-hover" id="curriculum-table"') \
                .set_caption(f'{discipline} Curriculum - Interactive Table') \
                .format({'Difficulty': '{:.1f}', 'Hours': '{:.1f}'}) \
                .background_gradient(subset=['Difficulty'], cmap='RdYlBu_r', vmin=0, vmax=10) \
                .bar(subset=['Hours'], color='lightblue', vmin=0, vmax=df['Hours'].astype(float).max())
            
            # Generate complete HTML with interactive features
            html_content = self._generate_interactive_html_template(
                discipline, curriculum_data, styled_df
            )
            
            # Write HTML file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.logger.info(f"Exported interactive HTML table: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export interactive HTML: {e}")
            return False
    
    async def export_executive_summary_md(self,
                                        curriculum_data: Dict[str, Any],
                                        output_path: Path) -> bool:
        """Export executive summary as Markdown file."""
        
        try:
            concepts = curriculum_data.get('concepts', [])
            discipline = curriculum_data.get('discipline', 'Unknown')
            exam_standards = curriculum_data.get('exam_standards', set())
            prerequisite_graph = curriculum_data.get('prerequisite_graph', nx.DiGraph())
            generation_time = curriculum_data.get('generation_time', 'Unknown')
            
            if not concepts:
                self.logger.warning("No concepts to export")
                return False
            
            # Calculate comprehensive statistics
            total_concepts = len(concepts)
            categories = len(set(c.category for c in concepts))
            levels = set(c.level for c in concepts)
            bloom_levels = Counter(c.bloom_taxonomy for c in concepts)
            level_counts = Counter(c.level for c in concepts)
            category_counts = Counter(c.category for c in concepts)
            
            # Generate markdown content
            content = self._generate_executive_summary_content(
                discipline, total_concepts, categories, levels, bloom_levels,
                level_counts, category_counts, exam_standards, prerequisite_graph,
                generation_time
            )
            
            # Write summary file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.logger.info(f"Exported executive summary: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export executive summary: {e}")
            return False
    
    async def export_curriculum_json(self,
                                   curriculum_data: Dict[str, Any],
                                   output_path: Path,
                                   include_graph: bool = True) -> bool:
        """Export complete curriculum data as JSON."""
        
        try:
            concepts = curriculum_data.get('concepts', [])
            
            if not concepts:
                self.logger.warning("No concepts to export")
                return False
            
            # Prepare export data
            export_data = {
                'discipline': curriculum_data.get('discipline', 'Unknown'),
                'generation_time': curriculum_data.get('generation_time', 'Unknown'),
                'total_concepts': len(concepts),
                'concepts': [concept.to_dict() for concept in concepts],
                'exam_standards': list(curriculum_data.get('exam_standards', set())),
                'statistics': {
                    'categories': len(set(c.category for c in concepts)),
                    'levels': len(set(c.level for c in concepts)),
                    'average_difficulty': sum(c.difficulty_score for c in concepts) / len(concepts),
                    'total_hours': sum(c.estimated_hours for c in concepts),
                    'level_distribution': dict(Counter(c.level for c in concepts)),
                    'bloom_distribution': dict(Counter(c.bloom_taxonomy for c in concepts)),
                    'category_distribution': dict(Counter(c.category for c in concepts))
                }
            }
            
            # Include prerequisite graph if requested
            if include_graph:
                prerequisite_graph = curriculum_data.get('prerequisite_graph', nx.DiGraph())
                export_data['prerequisite_relationships'] = {
                    'edges': list(prerequisite_graph.edges()),
                    'edge_count': prerequisite_graph.number_of_edges()
                }
            
            # Write JSON file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"Exported curriculum JSON: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export JSON: {e}")
            return False
    
    def _generate_interactive_html_template(self, 
                                          discipline: str,
                                          curriculum_data: Dict[str, Any],
                                          styled_df) -> str:
        """Generate complete HTML template for interactive table."""
        
        total_concepts = len(curriculum_data.get('concepts', []))
        categories = len(set(c.category for c in curriculum_data.get('concepts', [])))
        prerequisite_graph = curriculum_data.get('prerequisite_graph', nx.DiGraph())
        exam_standards = curriculum_data.get('exam_standards', set())
        
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{discipline} Curriculum - Interactive Table</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.datatables.net/1.11.3/css/dataTables.bootstrap5.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body {{ 
            padding: 20px; 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }}
        .table-container {{ margin-top: 20px; }}
        .stats-card {{ margin-bottom: 20px; }}
        .card {{ box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075); }}
        .badge {{ font-size: 0.75em; }}
        .difficulty-low {{ background-color: #d4edda; }}
        .difficulty-medium {{ background-color: #fff3cd; }}
        .difficulty-high {{ background-color: #f8d7da; }}
        .search-controls {{ margin-bottom: 20px; }}
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <div class="col-12">
                <h1 class="mb-4"><i class="fas fa-graduation-cap"></i> {discipline} Curriculum - Interactive Table</h1>
                <p class="lead">Comprehensive curriculum overview with interactive filtering and search capabilities.</p>
            </div>
        </div>
        
        <div class="row stats-card">
            <div class="col-md-3">
                <div class="card text-center h-100">
                    <div class="card-body">
                        <h5 class="card-title text-primary"><i class="fas fa-lightbulb"></i></h5>
                        <h3 class="card-text">{total_concepts:,}</h3>
                        <p class="card-text text-muted">Total Concepts</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center h-100">
                    <div class="card-body">
                        <h5 class="card-title text-success"><i class="fas fa-tags"></i></h5>
                        <h3 class="card-text">{categories}</h3>
                        <p class="card-text text-muted">Categories</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center h-100">
                    <div class="card-body">
                        <h5 class="card-title text-warning"><i class="fas fa-project-diagram"></i></h5>
                        <h3 class="card-text">{prerequisite_graph.number_of_edges():,}</h3>
                        <p class="card-text text-muted">Prerequisites</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center h-100">
                    <div class="card-body">
                        <h5 class="card-title text-info"><i class="fas fa-certificate"></i></h5>
                        <h3 class="card-text">{len(exam_standards)}</h3>
                        <p class="card-text text-muted">Exam Standards</p>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row search-controls">
            <div class="col-md-4">
                <label for="levelFilter" class="form-label">Filter by Level:</label>
                <select id="levelFilter" class="form-select">
                    <option value="">All Levels</option>
                    <option value="HS-Found">High School Foundation</option>
                    <option value="HS-Adv">High School Advanced</option>
                    <option value="UG-Intro">Undergraduate Intro</option>
                    <option value="UG-Adv">Undergraduate Advanced</option>
                    <option value="Grad-Intro">Graduate Intro</option>
                    <option value="Grad-Adv">Graduate Advanced</option>
                </select>
            </div>
            <div class="col-md-4">
                <label for="bloomFilter" class="form-label">Filter by Bloom's Taxonomy:</label>
                <select id="bloomFilter" class="form-select">
                    <option value="">All Bloom Levels</option>
                    <option value="Understand">Understand</option>
                    <option value="Apply">Apply</option>
                    <option value="Analyze">Analyze</option>
                    <option value="Evaluate">Evaluate</option>
                    <option value="Create">Create</option>
                </select>
            </div>
            <div class="col-md-4">
                <label for="difficultyFilter" class="form-label">Filter by Difficulty:</label>
                <select id="difficultyFilter" class="form-select">
                    <option value="">All Difficulties</option>
                    <option value="low">Low (0-3)</option>
                    <option value="medium">Medium (4-6)</option>
                    <option value="high">High (7-10)</option>
                </select>
            </div>
        </div>
        
        <div class="table-container">
            {styled_df.to_html(escape=False)}
        </div>
        
        <div class="row mt-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-info-circle"></i> Usage Instructions</h5>
                    </div>
                    <div class="card-body">
                        <ul>
                            <li><strong>Search:</strong> Use the search box above the table to find specific concepts</li>
                            <li><strong>Filter:</strong> Use the dropdown filters to narrow down concepts by level, Bloom's taxonomy, or difficulty</li>
                            <li><strong>Sort:</strong> Click on column headers to sort the table</li>
                            <li><strong>Navigate:</strong> Use the pagination controls at the bottom to browse through concepts</li>
                            <li><strong>Difficulty Scale:</strong> 0-3 (Basic), 4-6 (Intermediate), 7-10 (Advanced)</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.datatables.net/1.11.3/js/jquery.dataTables.min.js"></script>
    <script src="https://cdn.datatables.net/1.11.3/js/dataTables.bootstrap5.min.js"></script>
    <script>
        $(document).ready(function() {{
            var table = $('#curriculum-table').DataTable({{
                "pageLength": 25,
                "order": [[ 4, "asc" ], [ 2, "asc" ]],
                "columnDefs": [
                    {{ "width": "8%", "targets": 0 }},
                    {{ "width": "25%", "targets": 1 }},
                    {{ "width": "15%", "targets": 2 }},
                    {{ "width": "12%", "targets": 4 }},
                    {{ "width": "8%", "targets": 7 }},
                    {{ "width": "32%", "targets": 10 }}
                ],
                "dom": '<"row"<"col-sm-6"l><"col-sm-6"f>>rtip'
            }});
            
            // Custom filters
            $('#levelFilter').on('change', function() {{
                var filterValue = this.value;
                if (filterValue === '') {{
                    table.column(4).search('').draw();
                }} else {{
                    table.column(4).search('^' + filterValue + '$', true, false).draw();
                }}
            }});
            
            $('#bloomFilter').on('change', function() {{
                var filterValue = this.value;
                if (filterValue === '') {{
                    table.column(5).search('').draw();
                }} else {{
                    table.column(5).search('^' + filterValue + '$', true, false).draw();
                }}
            }});
            
            $('#difficultyFilter').on('change', function() {{
                var filterValue = this.value;
                if (filterValue === '') {{
                    table.column(7).search('').draw();
                }} else if (filterValue === 'low') {{
                    table.column(7).search('^[0-3]', true, false).draw();
                }} else if (filterValue === 'medium') {{
                    table.column(7).search('^[4-6]', true, false).draw();
                }} else if (filterValue === 'high') {{
                    table.column(7).search('^[7-9]|^10', true, false).draw();
                }}
            }});
        }});
    </script>
</body>
</html>
"""
    
    def _generate_executive_summary_content(self, 
                                          discipline: str,
                                          total_concepts: int,
                                          categories: int,
                                          levels: set,
                                          bloom_levels: Counter,
                                          level_counts: Counter,
                                          category_counts: Counter,
                                          exam_standards: set,
                                          prerequisite_graph: nx.DiGraph,
                                          generation_time: str) -> str:
        """Generate executive summary markdown content."""
        
        return f"""# {discipline} Curriculum - Executive Summary

## Overview
This comprehensive curriculum for **{discipline}** contains {total_concepts:,} carefully structured concepts organized across {categories} major categories and {len(levels)} educational levels.

*Generated on: {generation_time}*

## Curriculum Statistics

### Concept Distribution
- **Total Concepts**: {total_concepts:,}
- **Subject Categories**: {categories}
- **Educational Levels**: {len(levels)}
- **Prerequisite Relationships**: {prerequisite_graph.number_of_edges():,}

### Educational Level Distribution
{self._format_level_distribution(level_counts, total_concepts)}

### Bloom's Taxonomy Distribution
{self._format_bloom_distribution(bloom_levels, total_concepts)}

### Subject Categories
{self._format_category_distribution(category_counts, total_concepts)}

{self._format_exam_standards_section(exam_standards)}

## Curriculum Features

### 🎯 **Educational Alignment**
- Comprehensive progression from foundational to advanced concepts
- Proper prerequisite sequencing for optimal learning
- Bloom's taxonomy integration for cognitive development
- Professional exam alignment where applicable

### 📊 **Content Organization**
- Hierarchical concept structure with clear categorization
- Cross-referenced learning objectives and prerequisites
- Difficulty-based concept ordering within categories
- Multi-level educational pathways

### 🔗 **Interconnected Learning**
- {prerequisite_graph.number_of_edges():,} prerequisite relationships mapped
- Topological ordering ensures proper learning sequence
- Cross-category concept dependencies identified
- Knowledge graph structure for advanced analysis

## Usage Instructions

### For Educators
1. **Scope and Sequence**: Use the master curriculum CSV for course planning
2. **Prerequisites**: Consult the prerequisite graph for concept ordering
3. **Assessment Alignment**: Reference standards column for exam preparation
4. **Difficulty Progression**: Use Bloom's taxonomy for appropriate challenge levels

### For Students
1. **Learning Pathways**: Follow prerequisite relationships for optimal progression
2. **Self-Assessment**: Use difficulty scores to gauge concept complexity
3. **Exam Preparation**: Focus on concepts aligned with target assessments
4. **Time Planning**: Use hour estimates for study scheduling

### For Researchers
1. **Curriculum Analysis**: Examine concept density patterns in heatmap
2. **Knowledge Mapping**: Analyze prerequisite graph structure
3. **Educational Data**: Use structured curriculum data for learning analytics
4. **Comparative Studies**: Compare across disciplines using standardized format

## Files Generated

1. **`master_curriculum.csv`** - Complete curriculum data table
2. **`{discipline}_prerequisite_graph.png`** - Visual prerequisite relationships
3. **`{discipline}_curriculum_heatmap.png`** - Concept density visualization
4. **`interactive_table.html`** - Interactive curriculum browser
5. **`executive_summary_{discipline}.md`** - This summary document

---

*This curriculum was generated using the OpenBooks Comprehensive Curriculum Generation System, which combines domain expertise, content analysis, and educational best practices to create rigorous, well-structured learning pathways.*
"""
    
    def _format_level_distribution(self, level_counts: Counter, total: int) -> str:
        """Format level distribution section."""
        levels = ['HS-Found', 'HS-Adv', 'UG-Intro', 'UG-Adv', 'Grad-Intro', 'Grad-Adv']
        content = ""
        for level in levels:
            if level in level_counts:
                count = level_counts[level]
                percentage = (count / total) * 100
                content += f"- **{level}**: {count:,} concepts ({percentage:.1f}%)\n"
        return content
    
    def _format_bloom_distribution(self, bloom_levels: Counter, total: int) -> str:
        """Format Bloom's taxonomy distribution section."""
        content = ""
        for bloom_level, count in bloom_levels.most_common():
            percentage = (count / total) * 100
            content += f"- **{bloom_level}**: {count:,} concepts ({percentage:.1f}%)\n"
        return content
    
    def _format_category_distribution(self, category_counts: Counter, total: int) -> str:
        """Format category distribution section."""
        content = ""
        for category, count in category_counts.most_common():
            percentage = (count / total) * 100
            content += f"- **{category}**: {count:,} concepts ({percentage:.1f}%)\n"
        return content
    
    def _format_exam_standards_section(self, exam_standards: set) -> str:
        """Format exam standards section."""
        if exam_standards:
            content = """
### Standards and Assessments
This curriculum is aligned with the following professional/academic standards:
"""
            for standard in sorted(exam_standards):
                content += f"- {standard}\n"
            return content
        return ""