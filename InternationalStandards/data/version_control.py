#!/usr/bin/env python3
"""
Data Version Control and Change Tracking System for International Standards Retrieval

Provides comprehensive version control, audit trails, and change tracking for all
database operations across 19 OpenAlex disciplines. Maintains data integrity
with rollback capabilities and detailed change history.

Author: Autonomous AI Development System
"""

import json
import logging
import hashlib
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import copy

# Add parent directory to path for imports
import sys
sys.path.append(str(Path(__file__).parent.parent))

from data.database_manager import DatabaseManager, DatabaseConfig

class ChangeType(Enum):
    """Types of database changes"""
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    BULK_INSERT = "bulk_insert"
    BULK_UPDATE = "bulk_update"
    SCHEMA_CHANGE = "schema_change"

class ChangeStatus(Enum):
    """Status of change tracking"""
    PENDING = "pending"
    COMMITTED = "committed"
    ROLLBACK = "rollback"
    ARCHIVED = "archived"

@dataclass
class VersionedRecord:
    """Versioned database record structure"""
    version_id: int
    table_name: str
    record_id: int
    discipline_id: Optional[int]
    change_type: ChangeType
    old_values: Optional[Dict[str, Any]]
    new_values: Optional[Dict[str, Any]]
    changed_fields: List[str]
    change_timestamp: datetime
    changed_by: str
    change_reason: Optional[str]
    version_hash: str
    is_active_version: bool
    parent_version_id: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class ChangeSet:
    """Collection of related changes"""
    changeset_id: str
    description: str
    timestamp: datetime
    changes: List[VersionedRecord]
    status: ChangeStatus
    discipline_scope: List[int]
    rollback_available: bool = True
    metadata: Optional[Dict[str, Any]] = None

class VersionControlManager:
    """Comprehensive version control and change tracking manager"""
    
    def __init__(self, database_manager: DatabaseManager, 
                 enable_automatic_versioning: bool = True,
                 max_version_history: int = 1000):
        """Initialize version control manager
        
        Args:
            database_manager: Database manager instance
            enable_automatic_versioning: Auto-track all changes
            max_version_history: Maximum versions to keep per record
        """
        self.db = database_manager
        self.enable_automatic_versioning = enable_automatic_versioning
        self.max_version_history = max_version_history
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Version tracking state
        self.active_changesets = {}
        self.changeset_lock = threading.Lock()
        
        # Performance tracking
        self.version_stats = {
            'total_versions': 0,
            'active_changesets': 0,
            'rollbacks_performed': 0,
            'space_usage_mb': 0.0
        }
        
        # Initialize version control tables
        self._initialize_version_control_tables()
        
        # Load versioned table configurations
        self.versioned_tables = self._get_versioned_table_configs()
        
        self.logger.info("Version control manager initialized")
    
    def _initialize_version_control_tables(self):
        """Initialize version control database tables if not exist"""
        try:
            # Check if version control tables exist
            version_tables_query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('data_versions', 'changesets', 'version_metadata')
            """
            
            existing_tables = self.db.execute_query(version_tables_query)
            table_names = [row['table_name'] for row in existing_tables] if existing_tables else []
            
            if 'data_versions' not in table_names:
                self.logger.info("Version control tables not found. They should be created via schema migration.")
                # Tables are created in storage_schema.sql
                
        except Exception as e:
            self.logger.warning(f"Could not verify version control tables: {e}")
    
    def _get_versioned_table_configs(self) -> Dict[str, Dict[str, Any]]:
        """Get configuration for versioned tables"""
        return {
            'disciplines': {
                'primary_key': 'discipline_id',
                'track_fields': ['discipline_name', 'display_name', 'description', 'priority_level', 'is_active'],
                'exclude_fields': ['created_at', 'updated_at']
            },
            'standards_sources': {
                'primary_key': 'source_id',
                'track_fields': ['source_url', 'source_title', 'quality_score', 'authority_score', 'validation_status'],
                'exclude_fields': ['discovery_timestamp', 'last_validated']
            },
            'retrieved_documents': {
                'primary_key': 'document_id',
                'track_fields': ['document_title', 'processing_status', 'content_extracted'],
                'exclude_fields': ['download_timestamp', 'file_size']
            },
            'educational_standards': {
                'primary_key': 'standard_id',
                'track_fields': ['standard_text', 'standard_type', 'confidence_score', 'validation_score', 'is_validated'],
                'exclude_fields': ['processed_timestamp']
            },
            'competency_mappings': {
                'primary_key': 'competency_id',
                'track_fields': ['competency_statement', 'competency_category', 'bloom_level', 'difficulty_level'],
                'exclude_fields': ['created_timestamp']
            }
        }
    
    def track_change(self, table_name: str, record_id: int, 
                    change_type: ChangeType, new_values: Dict[str, Any],
                    old_values: Optional[Dict[str, Any]] = None,
                    changed_by: str = "system", change_reason: Optional[str] = None,
                    discipline_id: Optional[int] = None) -> int:
        """Track a database change
        
        Args:
            table_name: Table being modified
            record_id: Record ID being modified
            change_type: Type of change
            new_values: New field values
            old_values: Previous field values (for updates)
            changed_by: Who made the change
            change_reason: Reason for change
            discipline_id: Associated discipline ID
            
        Returns:
            Version ID of tracked change
        """
        try:
            # Determine changed fields
            changed_fields = self._determine_changed_fields(table_name, old_values, new_values)
            
            # Generate version hash
            version_hash = self._generate_version_hash(table_name, record_id, new_values, change_type)
            
            # Create versioned record
            versioned_record = VersionedRecord(
                version_id=0,  # Will be assigned by database
                table_name=table_name,
                record_id=record_id,
                discipline_id=discipline_id,
                change_type=change_type,
                old_values=old_values,
                new_values=new_values,
                changed_fields=changed_fields,
                change_timestamp=datetime.now(),
                changed_by=changed_by,
                change_reason=change_reason,
                version_hash=version_hash,
                is_active_version=True
            )
            
            # Insert version record
            version_id = self._insert_version_record(versioned_record)
            
            # Update statistics
            self.version_stats['total_versions'] += 1
            
            self.logger.debug(f"Change tracked: {table_name}:{record_id} - {change_type.value}")
            
            return version_id
            
        except Exception as e:
            self.logger.error(f"Error tracking change: {e}")
            raise
    
    def _determine_changed_fields(self, table_name: str, 
                                 old_values: Optional[Dict[str, Any]], 
                                 new_values: Dict[str, Any]) -> List[str]:
        """Determine which fields changed between versions"""
        if not old_values:
            # For inserts, all fields are considered changed
            table_config = self.versioned_tables.get(table_name, {})
            track_fields = table_config.get('track_fields', list(new_values.keys()))
            return [field for field in track_fields if field in new_values]
        
        changed = []
        for field, new_value in new_values.items():
            old_value = old_values.get(field)
            if old_value != new_value:
                changed.append(field)
        
        return changed
    
    def _generate_version_hash(self, table_name: str, record_id: int, 
                              values: Dict[str, Any], change_type: ChangeType) -> str:
        """Generate unique hash for version"""
        hash_data = {
            'table': table_name,
            'record_id': record_id,
            'values': values,
            'change_type': change_type.value,
            'timestamp': datetime.now().isoformat()
        }
        
        hash_string = json.dumps(hash_data, sort_keys=True, default=str)
        return hashlib.sha256(hash_string.encode()).hexdigest()
    
    def _insert_version_record(self, versioned_record: VersionedRecord) -> int:
        """Insert version record into database"""
        query = """
        INSERT INTO data_versions 
        (table_name, record_id, discipline_id, change_type, changed_fields,
         old_values, new_values, change_timestamp, changed_by, change_reason,
         version_hash, is_active_version)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING version_id
        """
        
        params = (
            versioned_record.table_name,
            versioned_record.record_id,
            versioned_record.discipline_id,
            versioned_record.change_type.value,
            json.dumps(versioned_record.changed_fields),
            json.dumps(versioned_record.old_values, default=str) if versioned_record.old_values else None,
            json.dumps(versioned_record.new_values, default=str),
            versioned_record.change_timestamp,
            versioned_record.changed_by,
            versioned_record.change_reason,
            versioned_record.version_hash,
            versioned_record.is_active_version
        )
        
        result = self.db.execute_query(query, params)
        return result[0]['version_id'] if result else None
    
    def create_changeset(self, description: str, discipline_scope: List[int] = None) -> str:
        """Create a new changeset for grouping related changes
        
        Args:
            description: Description of the changeset
            discipline_scope: List of discipline IDs affected
            
        Returns:
            Changeset ID
        """
        changeset_id = f"cs_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.active_changesets)}"
        
        changeset = ChangeSet(
            changeset_id=changeset_id,
            description=description,
            timestamp=datetime.now(),
            changes=[],
            status=ChangeStatus.PENDING,
            discipline_scope=discipline_scope or []
        )
        
        with self.changeset_lock:
            self.active_changesets[changeset_id] = changeset
            self.version_stats['active_changesets'] += 1
        
        self.logger.info(f"Created changeset: {changeset_id}")
        return changeset_id
    
    def commit_changeset(self, changeset_id: str) -> bool:
        """Commit a changeset, making all changes permanent
        
        Args:
            changeset_id: Changeset to commit
            
        Returns:
            True if successful
        """
        try:
            with self.changeset_lock:
                if changeset_id not in self.active_changesets:
                    raise ValueError(f"Changeset {changeset_id} not found")
                
                changeset = self.active_changesets[changeset_id]
                changeset.status = ChangeStatus.COMMITTED
                
                # Store changeset in database
                self._store_changeset(changeset)
                
                # Remove from active changesets
                del self.active_changesets[changeset_id]
                self.version_stats['active_changesets'] -= 1
            
            self.logger.info(f"Committed changeset: {changeset_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error committing changeset {changeset_id}: {e}")
            return False
    
    def rollback_changeset(self, changeset_id: str) -> bool:
        """Rollback a changeset, undoing all changes
        
        Args:
            changeset_id: Changeset to rollback
            
        Returns:
            True if successful
        """
        try:
            # Load changeset if not in active changesets
            changeset = self.active_changesets.get(changeset_id)
            if not changeset:
                changeset = self._load_changeset(changeset_id)
                if not changeset:
                    raise ValueError(f"Changeset {changeset_id} not found")
            
            if not changeset.rollback_available:
                raise ValueError(f"Changeset {changeset_id} cannot be rolled back")
            
            # Perform rollback operations
            rollback_success = self._perform_rollback(changeset)
            
            if rollback_success:
                changeset.status = ChangeStatus.ROLLBACK
                self._store_changeset(changeset)
                
                # Remove from active if present
                if changeset_id in self.active_changesets:
                    del self.active_changesets[changeset_id]
                    self.version_stats['active_changesets'] -= 1
                
                self.version_stats['rollbacks_performed'] += 1
                self.logger.info(f"Rolled back changeset: {changeset_id}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error rolling back changeset {changeset_id}: {e}")
            return False
    
    def _store_changeset(self, changeset: ChangeSet):
        """Store changeset in database"""
        # Create changesets table if using extended schema
        query = """
        INSERT INTO changesets 
        (changeset_id, description, timestamp, status, discipline_scope, 
         rollback_available, change_count, metadata)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (changeset_id) DO UPDATE SET
        status = EXCLUDED.status,
        rollback_available = EXCLUDED.rollback_available
        """
        
        params = (
            changeset.changeset_id,
            changeset.description,
            changeset.timestamp,
            changeset.status.value,
            json.dumps(changeset.discipline_scope),
            changeset.rollback_available,
            len(changeset.changes),
            json.dumps(changeset.metadata, default=str) if changeset.metadata else None
        )
        
        try:
            self.db.execute_query(query, params, fetch_results=False)
        except Exception as e:
            # Handle case where changesets table doesn't exist yet
            self.logger.warning(f"Could not store changeset in database: {e}")
    
    def _load_changeset(self, changeset_id: str) -> Optional[ChangeSet]:
        """Load changeset from database"""
        try:
            query = """
            SELECT * FROM changesets WHERE changeset_id = %s
            """
            
            result = self.db.execute_query(query, (changeset_id,))
            if not result:
                return None
            
            row = result[0]
            
            # Load associated changes
            changes_query = """
            SELECT * FROM data_versions 
            WHERE change_timestamp >= %s AND change_timestamp <= %s
            ORDER BY version_id
            """
            
            # Approximate time range for changeset
            start_time = row['timestamp'] - timedelta(minutes=5)
            end_time = row['timestamp'] + timedelta(minutes=5)
            
            changes_result = self.db.execute_query(changes_query, (start_time, end_time))
            
            # Convert to VersionedRecord objects
            changes = []
            if changes_result:
                for change_row in changes_result:
                    versioned_record = VersionedRecord(
                        version_id=change_row['version_id'],
                        table_name=change_row['table_name'],
                        record_id=change_row['record_id'],
                        discipline_id=change_row.get('discipline_id'),
                        change_type=ChangeType(change_row['change_type']),
                        old_values=json.loads(change_row['old_values']) if change_row['old_values'] else None,
                        new_values=json.loads(change_row['new_values']),
                        changed_fields=json.loads(change_row['changed_fields']),
                        change_timestamp=change_row['change_timestamp'],
                        changed_by=change_row['changed_by'],
                        change_reason=change_row.get('change_reason'),
                        version_hash=change_row['version_hash'],
                        is_active_version=change_row['is_active_version']
                    )
                    changes.append(versioned_record)
            
            return ChangeSet(
                changeset_id=row['changeset_id'],
                description=row['description'],
                timestamp=row['timestamp'],
                changes=changes,
                status=ChangeStatus(row['status']),
                discipline_scope=json.loads(row['discipline_scope']),
                rollback_available=row['rollback_available'],
                metadata=json.loads(row['metadata']) if row['metadata'] else None
            )
            
        except Exception as e:
            self.logger.error(f"Error loading changeset {changeset_id}: {e}")
            return None
    
    def _perform_rollback(self, changeset: ChangeSet) -> bool:
        """Perform actual rollback operations"""
        try:
            # Sort changes in reverse chronological order for rollback
            sorted_changes = sorted(changeset.changes, key=lambda x: x.change_timestamp, reverse=True)
            
            rollback_successful = True
            
            for change in sorted_changes:
                try:
                    if change.change_type == ChangeType.INSERT:
                        # Rollback insert by deleting record
                        self._rollback_insert(change)
                    elif change.change_type == ChangeType.UPDATE:
                        # Rollback update by restoring old values
                        self._rollback_update(change)
                    elif change.change_type == ChangeType.DELETE:
                        # Rollback delete by reinserting record
                        self._rollback_delete(change)
                    
                except Exception as e:
                    self.logger.error(f"Error rolling back change {change.version_id}: {e}")
                    rollback_successful = False
            
            return rollback_successful
            
        except Exception as e:
            self.logger.error(f"Error performing rollback: {e}")
            return False
    
    def _rollback_insert(self, change: VersionedRecord):
        """Rollback an insert operation"""
        table_config = self.versioned_tables.get(change.table_name, {})
        primary_key = table_config.get('primary_key', 'id')
        
        query = f"DELETE FROM {change.table_name} WHERE {primary_key} = %s"
        self.db.execute_query(query, (change.record_id,), fetch_results=False)
    
    def _rollback_update(self, change: VersionedRecord):
        """Rollback an update operation"""
        if not change.old_values:
            self.logger.warning(f"Cannot rollback update without old values: {change.version_id}")
            return
        
        table_config = self.versioned_tables.get(change.table_name, {})
        primary_key = table_config.get('primary_key', 'id')
        
        # Build update query with old values
        set_clauses = []
        params = []
        
        for field, value in change.old_values.items():
            set_clauses.append(f"{field} = %s")
            params.append(value)
        
        params.append(change.record_id)
        
        query = f"UPDATE {change.table_name} SET {', '.join(set_clauses)} WHERE {primary_key} = %s"
        self.db.execute_query(query, tuple(params), fetch_results=False)
    
    def _rollback_delete(self, change: VersionedRecord):
        """Rollback a delete operation"""
        if not change.old_values:
            self.logger.warning(f"Cannot rollback delete without old values: {change.version_id}")
            return
        
        # Build insert query to restore deleted record
        fields = list(change.old_values.keys())
        values = list(change.old_values.values())
        
        placeholders = ', '.join(['%s'] * len(values))
        query = f"INSERT INTO {change.table_name} ({', '.join(fields)}) VALUES ({placeholders})"
        
        self.db.execute_query(query, tuple(values), fetch_results=False)
    
    def get_record_history(self, table_name: str, record_id: int, 
                          limit: int = 50) -> List[VersionedRecord]:
        """Get version history for a specific record
        
        Args:
            table_name: Table name
            record_id: Record ID
            limit: Maximum versions to return
            
        Returns:
            List of versioned records
        """
        query = """
        SELECT * FROM data_versions 
        WHERE table_name = %s AND record_id = %s 
        ORDER BY change_timestamp DESC 
        LIMIT %s
        """
        
        results = self.db.execute_query(query, (table_name, record_id, limit))
        
        versions = []
        if results:
            for row in results:
                version = VersionedRecord(
                    version_id=row['version_id'],
                    table_name=row['table_name'],
                    record_id=row['record_id'],
                    discipline_id=row.get('discipline_id'),
                    change_type=ChangeType(row['change_type']),
                    old_values=json.loads(row['old_values']) if row['old_values'] else None,
                    new_values=json.loads(row['new_values']),
                    changed_fields=json.loads(row['changed_fields']),
                    change_timestamp=row['change_timestamp'],
                    changed_by=row['changed_by'],
                    change_reason=row.get('change_reason'),
                    version_hash=row['version_hash'],
                    is_active_version=row['is_active_version']
                )
                versions.append(version)
        
        return versions
    
    def get_discipline_changes(self, discipline_id: int, 
                              start_date: Optional[datetime] = None,
                              end_date: Optional[datetime] = None,
                              limit: int = 100) -> List[VersionedRecord]:
        """Get all changes for a specific discipline
        
        Args:
            discipline_id: Discipline ID
            start_date: Optional start date filter
            end_date: Optional end date filter
            limit: Maximum changes to return
            
        Returns:
            List of versioned records
        """
        query = """
        SELECT * FROM data_versions 
        WHERE discipline_id = %s
        """
        params = [discipline_id]
        
        if start_date:
            query += " AND change_timestamp >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND change_timestamp <= %s"
            params.append(end_date)
        
        query += " ORDER BY change_timestamp DESC LIMIT %s"
        params.append(limit)
        
        results = self.db.execute_query(query, tuple(params))
        
        changes = []
        if results:
            for row in results:
                change = VersionedRecord(
                    version_id=row['version_id'],
                    table_name=row['table_name'],
                    record_id=row['record_id'],
                    discipline_id=row['discipline_id'],
                    change_type=ChangeType(row['change_type']),
                    old_values=json.loads(row['old_values']) if row['old_values'] else None,
                    new_values=json.loads(row['new_values']),
                    changed_fields=json.loads(row['changed_fields']),
                    change_timestamp=row['change_timestamp'],
                    changed_by=row['changed_by'],
                    change_reason=row.get('change_reason'),
                    version_hash=row['version_hash'],
                    is_active_version=row['is_active_version']
                )
                changes.append(change)
        
        return changes
    
    def cleanup_old_versions(self, days_to_keep: int = 90) -> int:
        """Clean up old version records
        
        Args:
            days_to_keep: Number of days of history to keep
            
        Returns:
            Number of versions deleted
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            # Keep at least one version per record
            query = """
            DELETE FROM data_versions 
            WHERE change_timestamp < %s 
            AND version_id NOT IN (
                SELECT MAX(version_id) 
                FROM data_versions 
                GROUP BY table_name, record_id
            )
            """
            
            result = self.db.execute_query(
                "SELECT COUNT(*) as count FROM data_versions WHERE change_timestamp < %s",
                (cutoff_date,)
            )
            
            old_count = result[0]['count'] if result else 0
            
            self.db.execute_query(query, (cutoff_date,), fetch_results=False)
            
            self.logger.info(f"Cleaned up {old_count} old version records")
            return old_count
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old versions: {e}")
            return 0
    
    def get_version_statistics(self) -> Dict[str, Any]:
        """Get version control statistics
        
        Returns:
            Statistics dictionary
        """
        try:
            stats_queries = {
                'total_versions': "SELECT COUNT(*) as count FROM data_versions",
                'versions_by_table': """
                    SELECT table_name, COUNT(*) as count 
                    FROM data_versions 
                    GROUP BY table_name 
                    ORDER BY count DESC
                """,
                'recent_changes': """
                    SELECT COUNT(*) as count 
                    FROM data_versions 
                    WHERE change_timestamp >= %s
                """,
                'changes_by_discipline': """
                    SELECT discipline_id, COUNT(*) as count 
                    FROM data_versions 
                    WHERE discipline_id IS NOT NULL 
                    GROUP BY discipline_id 
                    ORDER BY count DESC 
                    LIMIT 10
                """
            }
            
            stats = self.version_stats.copy()
            
            # Total versions
            result = self.db.execute_query(stats_queries['total_versions'])
            stats['total_versions'] = result[0]['count'] if result else 0
            
            # Versions by table
            result = self.db.execute_query(stats_queries['versions_by_table'])
            stats['versions_by_table'] = result if result else []
            
            # Recent changes (last 24 hours)
            yesterday = datetime.now() - timedelta(days=1)
            result = self.db.execute_query(stats_queries['recent_changes'], (yesterday,))
            stats['recent_changes_24h'] = result[0]['count'] if result else 0
            
            # Changes by discipline
            result = self.db.execute_query(stats_queries['changes_by_discipline'])
            stats['changes_by_discipline'] = result if result else []
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting version statistics: {e}")
            return self.version_stats.copy()

# Utility functions for version control integration

def create_versioned_database_manager(config: DatabaseConfig, 
                                     enable_versioning: bool = True) -> Tuple[DatabaseManager, VersionControlManager]:
    """Create database manager with version control
    
    Args:
        config: Database configuration
        enable_versioning: Whether to enable automatic versioning
        
    Returns:
        Tuple of (DatabaseManager, VersionControlManager)
    """
    db_manager = DatabaseManager(config)
    
    if enable_versioning:
        version_manager = VersionControlManager(db_manager, enable_automatic_versioning=True)
        return db_manager, version_manager
    else:
        return db_manager, None

# Context manager for versioned transactions
class VersionedTransaction:
    """Context manager for versioned database transactions"""
    
    def __init__(self, version_manager: VersionControlManager, 
                 description: str, discipline_scope: List[int] = None):
        self.version_manager = version_manager
        self.description = description
        self.discipline_scope = discipline_scope or []
        self.changeset_id = None
    
    def __enter__(self):
        self.changeset_id = self.version_manager.create_changeset(
            self.description, 
            self.discipline_scope
        )
        return self.changeset_id
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            # Success - commit changeset
            self.version_manager.commit_changeset(self.changeset_id)
        else:
            # Error - rollback changeset
            self.version_manager.rollback_changeset(self.changeset_id)