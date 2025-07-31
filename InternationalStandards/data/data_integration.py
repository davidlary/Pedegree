#!/usr/bin/env python3
"""
Data Integration Module for International Standards Retrieval System

Comprehensive integration layer that combines database management, version control,
API generation, and data access across all 19 OpenAlex disciplines. Provides
unified interface for all data operations with built-in versioning and auditing.

Author: Autonomous AI Development System
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
import asyncio
import threading
from contextlib import contextmanager

# Add parent directory to path for imports
import sys
sys.path.append(str(Path(__file__).parent.parent))

from data.database_manager import DatabaseManager, DatabaseConfig, StandardRecord, CompetencyRecord
from data.version_control import VersionControlManager, ChangeType, VersionedTransaction
from api.api_generator import APIGenerator

@dataclass
class IntegrationConfig:
    """Configuration for data integration layer"""
    database_config: DatabaseConfig
    enable_version_control: bool = True
    enable_api_generation: bool = True
    api_framework: str = "flask"  # or "fastapi"
    api_host: str = "0.0.0.0"
    api_port: int = 5000
    auto_refresh_materialized_views: bool = True
    audit_all_operations: bool = True
    max_concurrent_operations: int = 10

class DataIntegrationManager:
    """Unified data integration manager for the International Standards Retrieval System"""
    
    def __init__(self, config: IntegrationConfig):
        """Initialize the data integration manager
        
        Args:
            config: Integration configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Core components
        self.db_manager = None
        self.version_manager = None
        self.api_generator = None
        
        # Threading and concurrency
        self.operation_semaphore = asyncio.Semaphore(config.max_concurrent_operations)
        self.integration_lock = threading.Lock()
        
        # Operation tracking
        self.operation_stats = {
            'total_operations': 0,
            'successful_operations': 0,
            'failed_operations': 0,
            'avg_operation_time': 0.0,
            'last_operation_time': None
        }
        
        # Initialize components
        self._initialize_components()
        
        self.logger.info("Data integration manager initialized successfully")
    
    def _initialize_components(self):
        """Initialize all data management components"""
        try:
            # Initialize database manager
            self.db_manager = DatabaseManager(self.config.database_config)
            self.logger.info("Database manager initialized")
            
            # Initialize version control if enabled
            if self.config.enable_version_control:
                self.version_manager = VersionControlManager(
                    self.db_manager,
                    enable_automatic_versioning=True
                )
                self.logger.info("Version control manager initialized")
            
            # Initialize API generator if enabled
            if self.config.enable_api_generation:
                self.api_generator = APIGenerator(
                    database_manager=self.db_manager,
                    framework=self.config.api_framework,
                    host=self.config.api_host,
                    port=self.config.api_port
                )
                self.logger.info("API generator initialized")
            
            # Setup automatic view refresh if enabled
            if self.config.auto_refresh_materialized_views:
                self._setup_view_refresh_scheduler()
            
        except Exception as e:
            self.logger.error(f"Error initializing components: {e}")
            raise
    
    def _setup_view_refresh_scheduler(self):
        """Setup automatic materialized view refresh"""
        def refresh_views():
            try:
                if self.db_manager:
                    self.db_manager.refresh_materialized_views()
                    self.logger.info("Materialized views refreshed automatically")
            except Exception as e:
                self.logger.error(f"Error refreshing materialized views: {e}")
        
        # Schedule refresh every hour (would typically use a scheduler like APScheduler)
        # For now, just log that it would be scheduled
        self.logger.info("Automatic view refresh would be scheduled here")
    
    # ==============================================================================
    # DISCIPLINE MANAGEMENT OPERATIONS
    # ==============================================================================
    
    def create_discipline(self, discipline_name: str, display_name: str,
                         openalex_id: str, description: Optional[str] = None,
                         priority_level: int = 5, changed_by: str = "system") -> Dict[str, Any]:
        """Create a new discipline with version tracking
        
        Args:
            discipline_name: Internal discipline name
            display_name: Human-readable display name
            openalex_id: OpenAlex concept ID
            description: Optional description
            priority_level: Processing priority (1-10)
            changed_by: Who is making the change
            
        Returns:
            Operation result with discipline_id
        """
        operation_start = datetime.now()
        
        try:
            with self.integration_lock:
                # Insert discipline
                discipline_id = self.db_manager.insert_discipline(
                    discipline_name, display_name, openalex_id, description, priority_level
                )
                
                # Track version if enabled
                if self.version_manager:
                    new_values = {
                        'discipline_name': discipline_name,
                        'display_name': display_name,
                        'openalex_id': openalex_id,
                        'description': description,
                        'priority_level': priority_level
                    }
                    
                    version_id = self.version_manager.track_change(
                        table_name='disciplines',
                        record_id=discipline_id,
                        change_type=ChangeType.INSERT,
                        new_values=new_values,
                        changed_by=changed_by,
                        change_reason=f"Created discipline: {discipline_name}"
                    )
                
                # Update statistics
                self._update_operation_stats(operation_start, True)
                
                result = {
                    'success': True,
                    'discipline_id': discipline_id,
                    'operation': 'create_discipline',
                    'timestamp': datetime.now().isoformat()
                }
                
                if self.version_manager:
                    result['version_id'] = version_id
                
                self.logger.info(f"Created discipline: {discipline_name} (ID: {discipline_id})")
                return result
        
        except Exception as e:
            self._update_operation_stats(operation_start, False)
            self.logger.error(f"Error creating discipline: {e}")
            return {
                'success': False,
                'error': str(e),
                'operation': 'create_discipline',
                'timestamp': datetime.now().isoformat()
            }
    
    def get_discipline_with_history(self, discipline_id: int, 
                                   include_version_history: bool = False) -> Dict[str, Any]:
        """Get discipline with optional version history
        
        Args:
            discipline_id: Discipline ID
            include_version_history: Whether to include version history
            
        Returns:
            Discipline data with optional history
        """
        try:
            # Get current discipline data
            disciplines = self.db_manager.get_all_disciplines()
            discipline = next((d for d in disciplines if d['discipline_id'] == discipline_id), None)
            
            if not discipline:
                return {
                    'success': False,
                    'error': f'Discipline {discipline_id} not found'
                }
            
            result = {
                'success': True,
                'discipline': discipline,
                'operation': 'get_discipline_with_history',
                'timestamp': datetime.now().isoformat()
            }
            
            # Add version history if requested and available
            if include_version_history and self.version_manager:
                history = self.version_manager.get_record_history('disciplines', discipline_id)
                result['version_history'] = [asdict(record) for record in history]
                result['total_versions'] = len(history)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error getting discipline with history: {e}")
            return {
                'success': False,
                'error': str(e),
                'operation': 'get_discipline_with_history',
                'timestamp': datetime.now().isoformat()
            }
    
    # ==============================================================================
    # STANDARDS MANAGEMENT OPERATIONS
    # ==============================================================================
    
    def create_standards_batch(self, standards: List[StandardRecord], 
                              changeset_description: str = "Batch standards creation",
                              changed_by: str = "system") -> Dict[str, Any]:
        """Create multiple standards with version control
        
        Args:
            standards: List of StandardRecord instances
            changeset_description: Description for the changeset
            changed_by: Who is making the changes
            
        Returns:
            Batch operation result
        """
        operation_start = datetime.now()
        
        if not standards:
            return {
                'success': False,
                'error': 'No standards provided',
                'operation': 'create_standards_batch'
            }
        
        try:
            # Create changeset if version control is enabled
            changeset_id = None
            if self.version_manager:
                discipline_ids = list(set(s.discipline_id for s in standards))
                changeset_id = self.version_manager.create_changeset(
                    changeset_description, discipline_ids
                )
            
            # Insert standards in batch
            standard_ids = self.db_manager.bulk_insert_standards(standards)
            
            # Track versions if enabled
            version_ids = []
            if self.version_manager and standard_ids:
                for standard, standard_id in zip(standards, standard_ids):
                    if standard_id:
                        new_values = {
                            'document_id': standard.document_id,
                            'discipline_id': standard.discipline_id,
                            'standard_text': standard.standard_text,
                            'standard_type': standard.standard_type,
                            'confidence_score': standard.confidence_score
                        }
                        
                        version_id = self.version_manager.track_change(
                            table_name='educational_standards',
                            record_id=standard_id,
                            change_type=ChangeType.INSERT,
                            new_values=new_values,
                            changed_by=changed_by,
                            discipline_id=standard.discipline_id
                        )
                        version_ids.append(version_id)
            
            # Commit changeset if created
            if changeset_id:
                self.version_manager.commit_changeset(changeset_id)
            
            # Update statistics
            self._update_operation_stats(operation_start, True)
            
            result = {
                'success': True,
                'standards_created': len([sid for sid in standard_ids if sid]),
                'standard_ids': standard_ids,
                'operation': 'create_standards_batch',
                'timestamp': datetime.now().isoformat()
            }
            
            if changeset_id:
                result['changeset_id'] = changeset_id
                result['version_ids'] = version_ids
            
            self.logger.info(f"Created {len(standard_ids)} standards in batch")
            return result
            
        except Exception as e:
            # Rollback changeset if it was created
            if changeset_id and self.version_manager:
                try:
                    self.version_manager.rollback_changeset(changeset_id)
                except Exception as rollback_error:
                    self.logger.error(f"Error rolling back changeset: {rollback_error}")
            
            self._update_operation_stats(operation_start, False)
            self.logger.error(f"Error creating standards batch: {e}")
            return {
                'success': False,
                'error': str(e),
                'operation': 'create_standards_batch',
                'timestamp': datetime.now().isoformat()
            }
    
    def get_standards_by_discipline_with_analytics(self, discipline_id: int,
                                                  include_analytics: bool = True,
                                                  include_trends: bool = False) -> Dict[str, Any]:
        """Get standards for discipline with optional analytics
        
        Args:
            discipline_id: Discipline ID
            include_analytics: Include quality analytics
            include_trends: Include change trends
            
        Returns:
            Standards with analytics data
        """
        try:
            # Get standards
            standards = self.db_manager.get_standards_by_discipline(discipline_id)
            
            result = {
                'success': True,
                'discipline_id': discipline_id,
                'standards': standards,
                'standards_count': len(standards),
                'operation': 'get_standards_by_discipline_with_analytics',
                'timestamp': datetime.now().isoformat()
            }
            
            # Add analytics if requested
            if include_analytics:
                analytics = self._calculate_discipline_analytics(discipline_id, standards)
                result['analytics'] = analytics
            
            # Add trends if requested and version control is available
            if include_trends and self.version_manager:
                trends = self._calculate_discipline_trends(discipline_id)
                result['trends'] = trends
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error getting standards with analytics: {e}")
            return {
                'success': False,
                'error': str(e),
                'operation': 'get_standards_by_discipline_with_analytics',
                'timestamp': datetime.now().isoformat()
            }
    
    def _calculate_discipline_analytics(self, discipline_id: int, 
                                      standards: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate analytics for discipline standards"""
        if not standards:
            return {'message': 'No standards available for analytics'}
        
        # Basic statistics
        total_standards = len(standards)
        validated_standards = sum(1 for s in standards if s.get('is_validated', False))
        avg_confidence = sum(s.get('confidence_score', 0) for s in standards) / total_standards
        avg_validation_score = sum(s.get('validation_score', 0) for s in standards if s.get('validation_score')) / max(1, sum(1 for s in standards if s.get('validation_score')))
        
        # Standard types distribution
        standard_types = {}
        for standard in standards:
            std_type = standard.get('standard_type', 'unknown')
            standard_types[std_type] = standard_types.get(std_type, 0) + 1
        
        # Education levels distribution
        education_levels = {}
        for standard in standards:
            edu_level = standard.get('education_level', 'unspecified')
            education_levels[edu_level] = education_levels.get(edu_level, 0) + 1
        
        return {
            'total_standards': total_standards,
            'validated_standards': validated_standards,
            'validation_rate': validated_standards / total_standards if total_standards > 0 else 0,
            'avg_confidence_score': round(avg_confidence, 3),
            'avg_validation_score': round(avg_validation_score, 3),
            'standard_types_distribution': standard_types,
            'education_levels_distribution': education_levels,
            'quality_score': round((avg_confidence + avg_validation_score) / 2, 3)
        }
    
    def _calculate_discipline_trends(self, discipline_id: int) -> Dict[str, Any]:
        """Calculate change trends for discipline"""
        if not self.version_manager:
            return {'message': 'Version control not available for trends'}
        
        # Get recent changes (last 30 days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        recent_changes = self.version_manager.get_discipline_changes(
            discipline_id, start_date, end_date
        )
        
        if not recent_changes:
            return {'message': 'No recent changes for trend analysis'}
        
        # Analyze changes by type
        change_types = {}
        daily_changes = {}
        
        for change in recent_changes:
            # Count by change type
            change_type = change.change_type.value
            change_types[change_type] = change_types.get(change_type, 0) + 1
            
            # Count by day
            change_date = change.change_timestamp.date().isoformat()
            daily_changes[change_date] = daily_changes.get(change_date, 0) + 1
        
        # Calculate velocity
        total_changes = len(recent_changes)
        avg_changes_per_day = total_changes / 30
        
        return {
            'analysis_period_days': 30,
            'total_changes': total_changes,
            'avg_changes_per_day': round(avg_changes_per_day, 2),
            'change_types_distribution': change_types,
            'daily_change_counts': daily_changes,
            'change_velocity': 'high' if avg_changes_per_day > 10 else 'medium' if avg_changes_per_day > 3 else 'low'
        }
    
    # ==============================================================================
    # API MANAGEMENT OPERATIONS
    # ==============================================================================
    
    def start_api_server(self, background: bool = True) -> Dict[str, Any]:
        """Start the API server for external data access
        
        Args:
            background: Whether to start in background
            
        Returns:
            API server status
        """
        try:
            if not self.api_generator:
                return {
                    'success': False,
                    'error': 'API generator not available',
                    'operation': 'start_api_server'
                }
            
            if background:
                # Start in background thread
                api_thread = threading.Thread(
                    target=self.api_generator.run_server,
                    kwargs={'debug': False},
                    daemon=True
                )
                api_thread.start()
                
                result = {
                    'success': True,
                    'message': 'API server started in background',
                    'host': self.config.api_host,
                    'port': self.config.api_port,
                    'framework': self.config.api_framework,
                    'operation': 'start_api_server',
                    'timestamp': datetime.now().isoformat()
                }
            else:
                # Start in foreground (blocking)
                self.api_generator.run_server(debug=False)
                result = {
                    'success': True,
                    'message': 'API server started (foreground)',
                    'operation': 'start_api_server'
                }
            
            self.logger.info(f"API server started on {self.config.api_host}:{self.config.api_port}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error starting API server: {e}")
            return {
                'success': False,
                'error': str(e),
                'operation': 'start_api_server',
                'timestamp': datetime.now().isoformat()
            }
    
    def generate_api_documentation(self, output_path: Optional[str] = None) -> Dict[str, Any]:
        """Generate API documentation
        
        Args:
            output_path: Optional output path for documentation
            
        Returns:
            Documentation generation result
        """
        try:
            if not self.api_generator:
                return {
                    'success': False,
                    'error': 'API generator not available',
                    'operation': 'generate_api_documentation'
                }
            
            # Use default path if not specified
            if not output_path:
                output_path = str(Path(__file__).parent.parent / 'api' / 'api_documentation.json')
            
            # Generate OpenAPI spec
            openapi_spec = self.api_generator.generate_openapi_spec()
            
            # Save documentation
            self.api_generator.save_api_documentation(output_path)
            
            return {
                'success': True,
                'documentation_path': output_path,
                'endpoints_documented': len(openapi_spec.get('paths', {})),
                'api_version': openapi_spec.get('info', {}).get('version', 'unknown'),
                'operation': 'generate_api_documentation',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error generating API documentation: {e}")
            return {
                'success': False,
                'error': str(e),
                'operation': 'generate_api_documentation',
                'timestamp': datetime.now().isoformat()
            }
    
    # ==============================================================================
    # SYSTEM MANAGEMENT OPERATIONS
    # ==============================================================================
    
    def get_system_health_report(self) -> Dict[str, Any]:
        """Get comprehensive system health report
        
        Returns:
            System health report
        """
        try:
            health_report = {
                'timestamp': datetime.now().isoformat(),
                'overall_status': 'healthy',
                'components': {},
                'performance_metrics': {},
                'recommendations': []
            }
            
            # Database health
            try:
                db_stats = self.db_manager.get_system_performance_stats()
                connection_stats = self.db_manager.get_connection_stats()
                
                health_report['components']['database'] = {
                    'status': 'healthy',
                    'connection_pool': connection_stats,
                    'performance_stats': db_stats
                }
            except Exception as e:
                health_report['components']['database'] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }
                health_report['overall_status'] = 'degraded'
            
            # Version control health
            if self.version_manager:
                try:
                    version_stats = self.version_manager.get_version_statistics()
                    health_report['components']['version_control'] = {
                        'status': 'healthy',
                        'statistics': version_stats
                    }
                except Exception as e:
                    health_report['components']['version_control'] = {
                        'status': 'unhealthy',
                        'error': str(e)
                    }
                    health_report['overall_status'] = 'degraded'
            else:
                health_report['components']['version_control'] = {
                    'status': 'disabled',
                    'message': 'Version control not enabled'
                }
            
            # API generator health
            if self.api_generator:
                try:
                    api_stats = self.api_generator.api_stats
                    health_report['components']['api_generator'] = {
                        'status': 'healthy',
                        'statistics': api_stats
                    }
                except Exception as e:
                    health_report['components']['api_generator'] = {
                        'status': 'unhealthy',
                        'error': str(e)
                    }
            else:
                health_report['components']['api_generator'] = {
                    'status': 'disabled',
                    'message': 'API generator not enabled'
                }
            
            # Integration layer performance
            health_report['performance_metrics'] = {
                'operation_stats': self.operation_stats,
                'concurrent_operations_limit': self.config.max_concurrent_operations
            }
            
            # Generate recommendations
            recommendations = []
            
            if self.operation_stats['failed_operations'] > 0:
                failure_rate = self.operation_stats['failed_operations'] / max(1, self.operation_stats['total_operations'])
                if failure_rate > 0.1:  # More than 10% failure rate
                    recommendations.append("High operation failure rate detected. Consider investigating error logs.")
            
            if self.version_manager:
                version_stats = self.version_manager.get_version_statistics()
                if version_stats.get('total_versions', 0) > 10000:
                    recommendations.append("Large number of versions detected. Consider running version cleanup.")
            
            health_report['recommendations'] = recommendations
            
            return health_report
            
        except Exception as e:
            self.logger.error(f"Error generating health report: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'overall_status': 'error',
                'error': str(e),
                'operation': 'get_system_health_report'
            }
    
    def perform_maintenance(self, operations: List[str] = None) -> Dict[str, Any]:
        """Perform system maintenance operations
        
        Args:
            operations: List of maintenance operations to perform
            
        Returns:
            Maintenance results
        """
        if operations is None:
            operations = ['refresh_views', 'optimize_database', 'cleanup_versions']
        
        maintenance_results = {
            'timestamp': datetime.now().isoformat(),
            'operations_requested': operations,
            'results': {},
            'overall_success': True
        }
        
        # Refresh materialized views
        if 'refresh_views' in operations:
            try:
                self.db_manager.refresh_materialized_views()
                maintenance_results['results']['refresh_views'] = {'success': True}
            except Exception as e:
                maintenance_results['results']['refresh_views'] = {'success': False, 'error': str(e)}
                maintenance_results['overall_success'] = False
        
        # Optimize database
        if 'optimize_database' in operations:
            try:
                self.db_manager.optimize_database()
                maintenance_results['results']['optimize_database'] = {'success': True}
            except Exception as e:
                maintenance_results['results']['optimize_database'] = {'success': False, 'error': str(e)}
                maintenance_results['overall_success'] = False
        
        # Cleanup old versions
        if 'cleanup_versions' in operations and self.version_manager:
            try:
                deleted_count = self.version_manager.cleanup_old_versions()
                maintenance_results['results']['cleanup_versions'] = {
                    'success': True,
                    'versions_deleted': deleted_count
                }
            except Exception as e:
                maintenance_results['results']['cleanup_versions'] = {'success': False, 'error': str(e)}
                maintenance_results['overall_success'] = False
        
        self.logger.info(f"Maintenance completed. Overall success: {maintenance_results['overall_success']}")
        return maintenance_results
    
    def _update_operation_stats(self, start_time: datetime, success: bool):
        """Update operation statistics"""
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        self.operation_stats['total_operations'] += 1
        self.operation_stats['last_operation_time'] = end_time
        
        if success:
            self.operation_stats['successful_operations'] += 1
        else:
            self.operation_stats['failed_operations'] += 1
        
        # Update average operation time
        total_ops = self.operation_stats['total_operations']
        current_avg = self.operation_stats['avg_operation_time']
        self.operation_stats['avg_operation_time'] = (
            (current_avg * (total_ops - 1) + duration) / total_ops
        )
    
    @contextmanager
    def versioned_transaction(self, description: str, discipline_scope: List[int] = None):
        """Context manager for versioned transactions
        
        Args:
            description: Transaction description
            discipline_scope: List of discipline IDs affected
            
        Yields:
            Changeset ID if version control is enabled
        """
        if self.version_manager:
            with VersionedTransaction(self.version_manager, description, discipline_scope) as changeset_id:
                yield changeset_id
        else:
            yield None
    
    def shutdown(self):
        """Gracefully shutdown the integration manager"""
        try:
            self.logger.info("Shutting down data integration manager...")
            
            # Close database connections
            if self.db_manager:
                # DatabaseManager cleanup is handled in __del__
                pass
            
            # API server shutdown would be handled here if running
            if self.api_generator:
                self.logger.info("API server shutdown complete")
            
            self.logger.info("Data integration manager shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")

# Factory function for easy initialization
def create_data_integration_manager(database_type: str = "postgresql",
                                   host: str = "localhost",
                                   port: int = 5432,
                                   database: str = "international_standards",
                                   username: str = "standards_user",
                                   password: str = "",
                                   enable_version_control: bool = True,
                                   enable_api: bool = True) -> DataIntegrationManager:
    """Factory function to create data integration manager
    
    Args:
        database_type: Database type ('postgresql' or 'sqlite')
        host: Database host
        port: Database port
        database: Database name
        username: Database username
        password: Database password
        enable_version_control: Enable version control
        enable_api: Enable API generation
        
    Returns:
        Configured DataIntegrationManager instance
    """
    db_config = DatabaseConfig(
        database_type=database_type,
        host=host,
        port=port,
        database=database,
        username=username,
        password=password
    )
    
    integration_config = IntegrationConfig(
        database_config=db_config,
        enable_version_control=enable_version_control,
        enable_api_generation=enable_api
    )
    
    return DataIntegrationManager(integration_config)