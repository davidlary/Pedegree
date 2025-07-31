#!/usr/bin/env python3
"""
Database Manager for International Standards Retrieval System

Programmatic data storage manager organized by 19 OpenAlex disciplines.
Provides comprehensive database operations, query optimization, and
automated API generation for external integration.

Author: Autonomous AI Development System
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
import hashlib
import threading
import pickle
import time
from functools import lru_cache

# Database connectivity
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor, Json
    from psycopg2.pool import ThreadedConnectionPool
    HAS_POSTGRESQL = True
except ImportError:
    HAS_POSTGRESQL = False

try:
    import sqlite3
    HAS_SQLITE = True
except ImportError:
    HAS_SQLITE = False

# DataFrame support for analytics
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

@dataclass
class DatabaseConfig:
    """Database configuration parameters"""
    database_type: str = "postgresql"  # postgresql, sqlite
    host: str = "localhost"
    port: int = 5432
    database: str = "international_standards"
    username: str = "standards_user"
    password: str = ""
    pool_size: int = 10
    max_overflow: int = 20
    sqlite_path: Optional[str] = None
    auto_commit: bool = True
    query_timeout: int = 300  # 5 minutes

@dataclass
class StandardRecord:
    """Educational standard record structure"""
    standard_text: str
    standard_type: str
    discipline_id: int
    document_id: int
    education_level: Optional[str] = None
    cognitive_level: Optional[str] = None
    confidence_score: float = 0.0
    extraction_method: str = "automated"
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class CompetencyRecord:
    """Competency mapping record structure"""
    standard_id: int
    discipline_id: int
    competency_statement: str
    competency_category: str
    bloom_level: Optional[str] = None
    subject_area: Optional[str] = None
    difficulty_level: int = 1
    metadata: Optional[Dict[str, Any]] = None

class DatabaseManager:
    """Comprehensive database manager for standards data"""
    
    def __init__(self, config: DatabaseConfig):
        """Initialize database manager
        
        Args:
            config: Database configuration parameters
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Connection management
        self.connection_pool = None
        self.connection_lock = threading.Lock()
        
        # Comprehensive caching system
        self.cache_dir = Path("cache/database")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.query_cache = {}
        self.cache_lock = threading.Lock()
        self.cache_ttl = 3600  # 1 hour
        
        # Statistics tracking
        self.query_stats = {
            'total_queries': 0,
            'cache_hits': 0,
            'avg_query_time': 0.0,
            'failed_queries': 0
        }
        
        # Initialize database connection
        self._initialize_connection()
        
        # Load discipline mappings
        self.discipline_mappings = self._load_discipline_mappings()
        
        self.logger.info(f"DatabaseManager initialized with {config.database_type}")
    
    def _initialize_connection(self):
        """Initialize database connection pool"""
        try:
            if self.config.database_type == "postgresql" and HAS_POSTGRESQL:
                self._initialize_postgresql_pool()
            elif self.config.database_type == "sqlite" and HAS_SQLITE:
                self._initialize_sqlite_connection()
            else:
                raise ValueError(f"Unsupported database type: {self.config.database_type}")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize database connection: {e}")
            raise
    
    def _initialize_postgresql_pool(self):
        """Initialize PostgreSQL connection pool"""
        connection_string = (
            f"host={self.config.host} "
            f"port={self.config.port} "
            f"dbname={self.config.database} "
            f"user={self.config.username} "
            f"password={self.config.password}"
        )
        
        self.connection_pool = ThreadedConnectionPool(
            minconn=1,
            maxconn=self.config.pool_size,
            dsn=connection_string
        )
        
        self.logger.info("PostgreSQL connection pool initialized")
    
    def _initialize_sqlite_connection(self):
        """Initialize SQLite connection"""
        sqlite_path = self.config.sqlite_path or "data/international_standards.db"
        Path(sqlite_path).parent.mkdir(parents=True, exist_ok=True)
        
        # SQLite doesn't use connection pooling in the same way
        self.sqlite_path = sqlite_path
        
        self.logger.info(f"SQLite database path set: {sqlite_path}")
    
    def get_connection(self):
        """Get database connection from pool"""
        if self.config.database_type == "postgresql":
            return self.connection_pool.getconn()
        elif self.config.database_type == "sqlite":
            conn = sqlite3.connect(self.sqlite_path)
            conn.row_factory = sqlite3.Row  # Enable dict-like access
            return conn
    
    def return_connection(self, connection):
        """Return connection to pool"""
        if self.config.database_type == "postgresql":
            self.connection_pool.putconn(connection)
        elif self.config.database_type == "sqlite":
            connection.close()
    
    def execute_query(self, query: str, params: Optional[Tuple] = None, 
                     fetch_results: bool = True) -> Optional[List[Dict[str, Any]]]:
        """Execute database query with connection management
        
        Args:
            query: SQL query string
            params: Query parameters
            fetch_results: Whether to fetch and return results
            
        Returns:
            Query results or None
        """
        start_time = datetime.now()
        connection = None
        
        try:
            connection = self.get_connection()
            
            if self.config.database_type == "postgresql":
                cursor = connection.cursor(cursor_factory=RealDictCursor)
            else:
                cursor = connection.cursor()
            
            # Execute query
            cursor.execute(query, params or ())
            
            results = None
            if fetch_results:
                if self.config.database_type == "postgresql":
                    results = [dict(row) for row in cursor.fetchall()]
                else:
                    results = [dict(row) for row in cursor.fetchall()]
            
            # Commit if auto_commit is enabled
            if self.config.auto_commit:
                connection.commit()
            
            # Update statistics
            execution_time = (datetime.now() - start_time).total_seconds()
            self._update_query_stats(execution_time, cache_hit=False)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Query execution failed: {e}")
            self.query_stats['failed_queries'] += 1
            if connection:
                connection.rollback()
            raise
            
        finally:
            if connection:
                self.return_connection(connection)
    
    def _update_query_stats(self, execution_time: float, cache_hit: bool = False):
        """Update query execution statistics"""
        self.query_stats['total_queries'] += 1
        
        if cache_hit:
            self.query_stats['cache_hits'] += 1
        
        # Update average query time
        current_avg = self.query_stats['avg_query_time']
        total_queries = self.query_stats['total_queries']
        
        self.query_stats['avg_query_time'] = (
            (current_avg * (total_queries - 1) + execution_time) / total_queries
        )
    
    def _load_discipline_mappings(self) -> Dict[str, int]:
        """Load discipline name to ID mappings"""
        try:
            query = "SELECT discipline_id, discipline_name, openalex_id FROM disciplines WHERE is_active = TRUE"
            results = self.execute_query(query)
            
            mappings = {}
            if results:
                for row in results:
                    mappings[row['discipline_name']] = row['discipline_id']
                    mappings[row['openalex_id']] = row['discipline_id']
            
            return mappings
            
        except Exception as e:
            self.logger.warning(f"Could not load discipline mappings: {e}")
            return {}
    
    # ==============================================================================
    # DISCIPLINE MANAGEMENT
    # ==============================================================================
    
    def insert_discipline(self, discipline_name: str, display_name: str, 
                         openalex_id: str, description: Optional[str] = None,
                         priority_level: int = 5) -> int:
        """Insert new discipline record
        
        Args:
            discipline_name: Internal discipline name
            display_name: Human-readable display name
            openalex_id: OpenAlex concept ID
            description: Optional description
            priority_level: Processing priority (1-10)
            
        Returns:
            Discipline ID of inserted record
        """
        query = """
        INSERT INTO disciplines (discipline_name, display_name, openalex_id, description, priority_level)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING discipline_id
        """
        
        params = (discipline_name, display_name, openalex_id, description, priority_level)
        result = self.execute_query(query, params)
        
        if result:
            discipline_id = result[0]['discipline_id']
            self.discipline_mappings[discipline_name] = discipline_id
            self.discipline_mappings[openalex_id] = discipline_id
            return discipline_id
        
        raise Exception("Failed to insert discipline")
    
    def get_discipline_id(self, discipline_identifier: str) -> Optional[int]:
        """Get discipline ID by name or OpenAlex ID
        
        Args:
            discipline_identifier: Discipline name or OpenAlex ID
            
        Returns:
            Discipline ID or None if not found
        """
        return self.discipline_mappings.get(discipline_identifier)
    
    def get_all_disciplines(self) -> List[Dict[str, Any]]:
        """Get all active disciplines
        
        Returns:
            List of discipline records
        """
        query = """
        SELECT discipline_id, discipline_name, display_name, openalex_id, 
               description, priority_level, created_at
        FROM disciplines 
        WHERE is_active = TRUE 
        ORDER BY priority_level, discipline_name
        """
        
        return self.execute_query(query)
    
    # ==============================================================================
    # STANDARDS SOURCE MANAGEMENT
    # ==============================================================================
    
    def insert_standards_source(self, discipline_id: int, source_url: str,
                               source_title: Optional[str] = None,
                               source_type: Optional[str] = None,
                               quality_scores: Optional[Dict[str, float]] = None,
                               discovery_method: str = "automated",
                               metadata: Optional[Dict[str, Any]] = None) -> int:
        """Insert standards source record
        
        Args:
            discipline_id: Associated discipline ID
            source_url: Source URL
            source_title: Source title
            source_type: Type of source
            quality_scores: Dictionary of quality scores
            discovery_method: How source was discovered
            metadata: Additional metadata
            
        Returns:
            Source ID of inserted record
        """
        scores = quality_scores or {}
        
        query = """
        INSERT INTO standards_sources 
        (discipline_id, source_url, source_title, source_type, authority_score, 
         quality_score, relevance_score, discovery_method, metadata)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (source_url, discipline_id) DO UPDATE SET
        source_title = EXCLUDED.source_title,
        authority_score = EXCLUDED.authority_score,
        quality_score = EXCLUDED.quality_score,
        relevance_score = EXCLUDED.relevance_score,
        last_validated = CURRENT_TIMESTAMP
        RETURNING source_id
        """
        
        params = (
            discipline_id, source_url, source_title, source_type,
            scores.get('authority_score', 0.0),
            scores.get('quality_score', 0.0), 
            scores.get('relevance_score', 0.0),
            discovery_method,
            Json(metadata) if metadata else None
        )
        
        result = self.execute_query(query, params)
        return result[0]['source_id'] if result else None
    
    def get_sources_by_discipline(self, discipline_id: int, 
                                 min_quality_score: float = 0.0) -> List[Dict[str, Any]]:
        """Get standards sources for a discipline
        
        Args:
            discipline_id: Discipline ID
            min_quality_score: Minimum quality score filter
            
        Returns:
            List of source records
        """
        query = """
        SELECT source_id, source_url, source_title, source_type,
               authority_score, quality_score, relevance_score,
               discovery_timestamp, validation_status, metadata
        FROM standards_sources
        WHERE discipline_id = %s AND quality_score >= %s AND is_active = TRUE
        ORDER BY quality_score DESC, authority_score DESC
        """
        
        return self.execute_query(query, (discipline_id, min_quality_score))
    
    # ==============================================================================
    # DOCUMENT MANAGEMENT
    # ==============================================================================
    
    def insert_document(self, source_id: int, discipline_id: int, document_url: str,
                       document_title: Optional[str] = None, document_type: str = "unknown",
                       file_path: Optional[str] = None, file_size: Optional[int] = None,
                       content_hash: Optional[str] = None,
                       metadata: Optional[Dict[str, Any]] = None) -> int:
        """Insert retrieved document record
        
        Args:
            source_id: Associated source ID
            discipline_id: Associated discipline ID
            document_url: Document URL
            document_title: Document title
            document_type: Document type (pdf, html, etc.)
            file_path: Local file path
            file_size: File size in bytes
            content_hash: SHA256 hash for deduplication
            metadata: Additional metadata
            
        Returns:
            Document ID of inserted record
        """
        # Generate content hash if not provided
        if not content_hash and file_path and Path(file_path).exists():
            content_hash = self._calculate_file_hash(file_path)
        
        query = """
        INSERT INTO retrieved_documents 
        (source_id, discipline_id, document_url, document_title, document_type,
         file_path, file_size, content_hash, metadata)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (content_hash) DO UPDATE SET
        document_title = EXCLUDED.document_title,
        file_path = EXCLUDED.file_path
        RETURNING document_id
        """
        
        params = (
            source_id, discipline_id, document_url, document_title, document_type,
            file_path, file_size, content_hash, Json(metadata) if metadata else None
        )
        
        result = self.execute_query(query, params)
        return result[0]['document_id'] if result else None
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA256 hash of file content"""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception:
            return ""
    
    def get_documents_by_discipline(self, discipline_id: int, 
                                   processing_status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get documents for a discipline
        
        Args:
            discipline_id: Discipline ID 
            processing_status: Filter by processing status
            
        Returns:
            List of document records
        """
        base_query = """
        SELECT rd.document_id, rd.document_url, rd.document_title, rd.document_type,
               rd.file_path, rd.file_size, rd.download_timestamp, rd.processing_status,
               ss.source_url, ss.source_title, ss.quality_score
        FROM retrieved_documents rd
        JOIN standards_sources ss ON rd.source_id = ss.source_id
        WHERE rd.discipline_id = %s
        """
        
        params = [discipline_id]
        
        if processing_status:
            base_query += " AND rd.processing_status = %s"
            params.append(processing_status)
        
        base_query += " ORDER BY rd.download_timestamp DESC"
        
        return self.execute_query(base_query, tuple(params))
    
    # ==============================================================================
    # STANDARDS MANAGEMENT
    # ==============================================================================
    
    def insert_standard(self, standard: StandardRecord) -> int:
        """Insert educational standard record
        
        Args:
            standard: StandardRecord instance
            
        Returns:
            Standard ID of inserted record
        """
        query = """
        INSERT INTO educational_standards 
        (document_id, discipline_id, standard_text, standard_type, education_level,
         cognitive_level, confidence_score, extraction_method, metadata)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING standard_id
        """
        
        params = (
            standard.document_id, standard.discipline_id, standard.standard_text,
            standard.standard_type, standard.education_level, standard.cognitive_level,
            standard.confidence_score, standard.extraction_method,
            Json(standard.metadata) if standard.metadata else None
        )
        
        result = self.execute_query(query, params)
        return result[0]['standard_id'] if result else None
    
    def bulk_insert_standards(self, standards: List[StandardRecord]) -> List[int]:
        """Insert multiple standards efficiently
        
        Args:
            standards: List of StandardRecord instances
            
        Returns:
            List of standard IDs
        """
        if not standards:
            return []
        
        # Build bulk insert query
        values_template = "(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        values_list = [values_template] * len(standards)
        
        query = f"""
        INSERT INTO educational_standards 
        (document_id, discipline_id, standard_text, standard_type, education_level,
         cognitive_level, confidence_score, extraction_method, metadata)
        VALUES {', '.join(values_list)}
        RETURNING standard_id
        """
        
        # Flatten parameters
        params = []
        for standard in standards:
            params.extend([
                standard.document_id, standard.discipline_id, standard.standard_text,
                standard.standard_type, standard.education_level, standard.cognitive_level,
                standard.confidence_score, standard.extraction_method,
                Json(standard.metadata) if standard.metadata else None
            ])
        
        results = self.execute_query(query, tuple(params))
        return [row['standard_id'] for row in results] if results else []
    
    def get_standards_by_discipline(self, discipline_id: int, 
                                   standard_type: Optional[str] = None,
                                   min_confidence: float = 0.0,
                                   limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get standards for a discipline
        
        Args:
            discipline_id: Discipline ID
            standard_type: Filter by standard type
            min_confidence: Minimum confidence score
            limit: Maximum number of results
            
        Returns:
            List of standard records
        """
        query = """
        SELECT es.standard_id, es.standard_text, es.standard_type, es.education_level,
               es.cognitive_level, es.confidence_score, es.validation_score,
               es.is_validated, es.processed_timestamp, es.metadata,
               rd.document_title, rd.document_url, ss.source_title
        FROM educational_standards es
        JOIN retrieved_documents rd ON es.document_id = rd.document_id
        JOIN standards_sources ss ON rd.source_id = ss.source_id
        WHERE es.discipline_id = %s AND es.confidence_score >= %s
        """
        
        params = [discipline_id, min_confidence]
        
        if standard_type:
            query += " AND es.standard_type = %s"
            params.append(standard_type)
        
        query += " ORDER BY es.validation_score DESC NULLS LAST, es.confidence_score DESC"
        
        if limit:
            query += f" LIMIT {limit}"
        
        return self.execute_query(query, tuple(params))
    
    # ==============================================================================
    # COMPETENCY MANAGEMENT
    # ==============================================================================
    
    def insert_competency(self, competency: CompetencyRecord) -> int:
        """Insert competency mapping record
        
        Args:
            competency: CompetencyRecord instance
            
        Returns:
            Competency ID of inserted record
        """
        query = """
        INSERT INTO competency_mappings
        (standard_id, discipline_id, competency_statement, competency_category,
         bloom_level, subject_area, difficulty_level, metadata)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING competency_id
        """
        
        params = (
            competency.standard_id, competency.discipline_id, competency.competency_statement,
            competency.competency_category, competency.bloom_level, competency.subject_area,
            competency.difficulty_level, Json(competency.metadata) if competency.metadata else None
        )
        
        result = self.execute_query(query, params)
        return result[0]['competency_id'] if result else None
    
    def get_competencies_by_discipline(self, discipline_id: int,
                                      competency_category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get competencies for a discipline
        
        Args:
            discipline_id: Discipline ID
            competency_category: Filter by competency category
            
        Returns:
            List of competency records
        """
        query = """
        SELECT cm.competency_id, cm.competency_statement, cm.competency_category,
               cm.bloom_level, cm.subject_area, cm.difficulty_level,
               es.standard_text, es.standard_type
        FROM competency_mappings cm
        JOIN educational_standards es ON cm.standard_id = es.standard_id
        WHERE cm.discipline_id = %s
        """
        
        params = [discipline_id]
        
        if competency_category:
            query += " AND cm.competency_category = %s"
            params.append(competency_category)
        
        query += " ORDER BY cm.difficulty_level, cm.competency_category"
        
        return self.execute_query(query, tuple(params))
    
    # ==============================================================================
    # ANALYTICS AND REPORTING
    # ==============================================================================
    
    def get_discipline_summary(self, discipline_id: int) -> Dict[str, Any]:
        """Get comprehensive summary for a discipline
        
        Args:
            discipline_id: Discipline ID
            
        Returns:
            Summary statistics dictionary
        """
        # Use materialized view for performance
        query = """
        SELECT * FROM mv_discipline_standards_summary 
        WHERE discipline_id = %s
        """
        
        result = self.execute_query(query, (discipline_id,))
        
        if result:
            return result[0]
        else:
            # Fallback to direct calculation
            return self._calculate_discipline_summary(discipline_id)
    
    def _calculate_discipline_summary(self, discipline_id: int) -> Dict[str, Any]:
        """Calculate discipline summary directly (fallback)"""
        
        queries = {
            'standards_count': "SELECT COUNT(*) as count FROM educational_standards WHERE discipline_id = %s",
            'validated_standards': "SELECT COUNT(*) as count FROM educational_standards WHERE discipline_id = %s AND is_validated = TRUE",
            'documents_count': "SELECT COUNT(DISTINCT rd.document_id) as count FROM retrieved_documents rd JOIN educational_standards es ON rd.document_id = es.document_id WHERE es.discipline_id = %s",
            'sources_count': "SELECT COUNT(DISTINCT ss.source_id) as count FROM standards_sources ss JOIN retrieved_documents rd ON ss.source_id = rd.source_id JOIN educational_standards es ON rd.document_id = es.document_id WHERE es.discipline_id = %s",
            'avg_quality': "SELECT AVG(validation_score) as avg_score FROM educational_standards WHERE discipline_id = %s AND validation_score IS NOT NULL"
        }
        
        summary = {'discipline_id': discipline_id}
        
        for key, query in queries.items():
            result = self.execute_query(query, (discipline_id,))
            if result:
                if key == 'avg_quality':
                    summary[key] = float(result[0]['avg_score'] or 0.0)
                else:
                    summary[key] = result[0]['count']
            else:
                summary[key] = 0
        
        return summary
    
    def get_quality_metrics(self, discipline_id: Optional[int] = None,
                           start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get quality metrics with optional filters
        
        Args:
            discipline_id: Optional discipline filter
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            List of quality metric records
        """
        query = """
        SELECT dqm.*, d.discipline_name, d.display_name
        FROM discipline_quality_metrics dqm
        JOIN disciplines d ON dqm.discipline_id = d.discipline_id
        WHERE 1=1
        """
        
        params = []
        
        if discipline_id:
            query += " AND dqm.discipline_id = %s"
            params.append(discipline_id)
        
        if start_date:
            query += " AND dqm.measurement_date >= %s"
            params.append(start_date.date())
        
        if end_date:
            query += " AND dqm.measurement_date <= %s"
            params.append(end_date.date())
        
        query += " ORDER BY dqm.measurement_date DESC, d.discipline_name"
        
        return self.execute_query(query, tuple(params))
    
    def get_system_performance_stats(self) -> Dict[str, Any]:
        """Get overall system performance statistics
        
        Returns:
            System performance dictionary
        """
        stats_queries = {
            'total_disciplines': "SELECT COUNT(*) as count FROM disciplines WHERE is_active = TRUE",
            'total_standards': "SELECT COUNT(*) as count FROM educational_standards",
            'total_validated': "SELECT COUNT(*) as count FROM educational_standards WHERE is_validated = TRUE",
            'total_documents': "SELECT COUNT(*) as count FROM retrieved_documents",
            'total_sources': "SELECT COUNT(*) as count FROM standards_sources WHERE is_active = TRUE",
            'avg_quality_score': "SELECT AVG(validation_score) as avg FROM educational_standards WHERE validation_score IS NOT NULL",
            'processing_efficiency': "SELECT AVG(success_rate) as avg FROM agent_sessions WHERE status = 'completed'"
        }
        
        stats = {}
        for key, query in stats_queries.items():
            result = self.execute_query(query)
            if result:
                if 'avg' in result[0]:
                    stats[key] = float(result[0]['avg'] or 0.0)
                else:
                    stats[key] = result[0]['count']
            else:
                stats[key] = 0
        
        # Add query performance stats
        stats['query_performance'] = self.query_stats.copy()
        
        return stats
    
    # ==============================================================================
    # UTILITY METHODS
    # ==============================================================================
    
    def refresh_materialized_views(self):
        """Refresh all materialized views for updated analytics"""
        views = [
            'mv_discipline_standards_summary',
            'mv_llm_cost_efficiency', 
            'mv_system_performance'
        ]
        
        for view in views:
            try:
                self.execute_query(f"REFRESH MATERIALIZED VIEW {view}", fetch_results=False)
                self.logger.info(f"Refreshed materialized view: {view}")
            except Exception as e:
                self.logger.error(f"Failed to refresh view {view}: {e}")
    
    def optimize_database(self):
        """Run database optimization operations"""
        try:
            if self.config.database_type == "postgresql":
                # Run VACUUM and ANALYZE
                self.execute_query("VACUUM ANALYZE", fetch_results=False)
                self.logger.info("Database vacuum and analyze completed")
            elif self.config.database_type == "sqlite":
                # Run VACUUM
                self.execute_query("VACUUM", fetch_results=False)
                self.logger.info("SQLite vacuum completed")
                
        except Exception as e:
            self.logger.error(f"Database optimization failed: {e}")
    
    def backup_database(self, backup_path: str) -> bool:
        """Create database backup
        
        Args:
            backup_path: Path for backup file
            
        Returns:
            True if backup successful
        """
        try:
            if self.config.database_type == "postgresql":
                # Use pg_dump for PostgreSQL
                import subprocess
                cmd = [
                    'pg_dump',
                    f'--host={self.config.host}',
                    f'--port={self.config.port}',
                    f'--username={self.config.username}',
                    f'--dbname={self.config.database}',
                    f'--file={backup_path}'
                ]
                subprocess.run(cmd, check=True)
                
            elif self.config.database_type == "sqlite":
                # Copy SQLite file
                import shutil
                shutil.copy2(self.sqlite_path, backup_path)
            
            self.logger.info(f"Database backup created: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Database backup failed: {e}")
            return False
    
    def get_all_standards(self) -> List[Dict[str, Any]]:
        """Get all standards from database with comprehensive caching
        
        Returns:
            List of all standards
        """
        cache_key = "all_standards"
        
        try:
            # Check memory cache first
            with self.cache_lock:
                if cache_key in self.query_cache:
                    cached_time, cached_data = self.query_cache[cache_key]
                    if time.time() - cached_time < self.cache_ttl:
                        self.logger.debug("Returning cached standards data")
                        return cached_data
            
            # Check file cache
            cache_file = self.cache_dir / f"{cache_key}.pkl"
            if cache_file.exists():
                cache_age = time.time() - cache_file.stat().st_mtime
                if cache_age < self.cache_ttl:
                    try:
                        with open(cache_file, 'rb') as f:
                            cached_data = pickle.load(f)
                            # Update memory cache
                            with self.cache_lock:
                                self.query_cache[cache_key] = (time.time(), cached_data)
                            self.logger.debug("Returning file cached standards data")
                            return cached_data
                    except Exception as e:
                        self.logger.warning(f"Error reading cache file: {e}")
            
            # Query database if no valid cache
            query = """
            SELECT 
                id, title, discipline, organization, 
                quality_score, status, last_updated,
                created_date, metadata
            FROM standards 
            ORDER BY last_updated DESC
            """
            
            result = self._execute_query(query)
            
            if result['success']:
                standards_data = result['data']
                
                # Cache the results
                with self.cache_lock:
                    self.query_cache[cache_key] = (time.time(), standards_data)
                
                # Save to file cache
                try:
                    with open(cache_file, 'wb') as f:
                        pickle.dump(standards_data, f)
                except Exception as e:
                    self.logger.warning(f"Error saving to cache file: {e}")
                
                self.logger.info(f"Retrieved and cached {len(standards_data)} standards")
                return standards_data
            else:
                self.logger.error(f"Failed to get all standards: {result.get('error', 'Unknown error')}")
                return []
                
        except Exception as e:
            self.logger.error(f"Error getting all standards: {e}")
            return []
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics
        
        Returns:
            Connection statistics dictionary
        """
        if self.config.database_type == "postgresql" and self.connection_pool:
            return {
                'pool_size': self.connection_pool.maxconn,
                'connections_in_use': self.connection_pool.maxconn - len(self.connection_pool._pool),
                'available_connections': len(self.connection_pool._pool)
            }
        else:
            return {
                'database_type': self.config.database_type,
                'connection_method': 'direct'
            }
    
    def __del__(self):
        """Cleanup database connections"""
        if self.connection_pool:
            self.connection_pool.closeall()
            self.logger.info("Database connection pool closed")