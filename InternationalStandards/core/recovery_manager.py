#!/usr/bin/env python3
"""
Recovery Manager for International Standards Retrieval System

Comprehensive recovery and continuation system for autonomous operation.
Handles checkpoints, state persistence, system validation, and seamless
continuation after interruptions.

Author: Autonomous AI Development System  
"""

import json
import pickle
import gzip
import shutil
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime, timedelta
import logging
import hashlib
import threading
import time

class RecoveryManager:
    """Comprehensive recovery and continuation system"""
    
    def __init__(self, recovery_dir: Optional[Path] = None, config: Optional[Dict[str, Any]] = None):
        """Initialize recovery manager
        
        Args:
            recovery_dir: Directory for recovery files (defaults to current/recovery)
            config: Recovery configuration dictionary (defaults to basic config)
        """
        if recovery_dir is None:
            recovery_dir = Path(__file__).parent.parent / "recovery"
        if config is None:
            config = {
                'checkpoint_interval': 300,  # 5 minutes
                'max_checkpoints': 10,
                'compression_enabled': True,
                'integrity_checks': True
            }
            
        self.recovery_dir = Path(recovery_dir)
        self.config = config
        
        # Ensure recovery directory exists
        self.recovery_dir.mkdir(exist_ok=True)
        
        # Recovery file paths
        self.state_file = self.recovery_dir / "system_state.json"
        self.progress_file = self.recovery_dir / "progress_tracker.json" 
        self.agent_states_file = self.recovery_dir / "agent_states.json"
        self.llm_optimization_file = self.recovery_dir / "llm_optimization_state.json"
        self.integrity_file = self.recovery_dir / "data_integrity.json"
        self.checkpoints_dir = self.recovery_dir / "checkpoints"
        
        # Create checkpoints directory
        self.checkpoints_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Recovery settings
        self.checkpoint_frequency = config.get('recovery_settings', {}).get('checkpoint_frequency', {})
        self.auto_save_seconds = self.checkpoint_frequency.get('auto_save_seconds', 300)
        
        # Initialize auto-save thread
        self._auto_save_active = False
        self._auto_save_thread = None
        
        # State tracking
        self.current_state = {}
        self.last_checkpoint_time = datetime.now()
        self.recovery_metrics = {
            'checkpoints_created': 0,
            'successful_recoveries': 0,
            'failed_recoveries': 0,
            'state_saves': 0,
            'data_integrity_checks': 0
        }
    
    def start_auto_save(self):
        """Start automatic state saving thread"""
        if not self._auto_save_active:
            self._auto_save_active = True
            self._auto_save_thread = threading.Thread(target=self._auto_save_worker, daemon=True)
            self._auto_save_thread.start()
            self.logger.info("Auto-save thread started")
    
    def stop_auto_save(self):
        """Stop automatic state saving thread"""
        self._auto_save_active = False
        if self._auto_save_thread:
            self._auto_save_thread.join(timeout=5)
        self.logger.info("Auto-save thread stopped")
    
    def _auto_save_worker(self):
        """Worker thread for automatic state saving"""
        while self._auto_save_active:
            try:
                time.sleep(self.auto_save_seconds)
                if self._auto_save_active and self.current_state:
                    self.save_state(self.current_state, auto_save=True)
            except Exception as e:
                self.logger.error(f"Error in auto-save worker: {e}")
    
    def check_previous_session(self) -> bool:
        """Check if previous session exists
        
        Returns:
            True if previous session found
        """
        return self.state_file.exists() and self.state_file.stat().st_size > 0
    
    def load_previous_state(self) -> Optional[Dict[str, Any]]:
        """Load previous session state
        
        Returns:
            Previous state dictionary or None if not found
        """
        if not self.check_previous_session():
            return None
        
        try:
            with open(self.state_file, 'r') as f:
                state = json.load(f)
            
            self.logger.info("Successfully loaded previous session state")
            return state
            
        except Exception as e:
            self.logger.error(f"Error loading previous state: {e}")
            return None
    
    def save_state(self, state: Dict[str, Any], auto_save: bool = False):
        """Save current system state
        
        Args:
            state: State dictionary to save
            auto_save: Whether this is an automatic save
        """
        try:
            # Add metadata
            enhanced_state = {
                **state,
                'timestamp': datetime.now().isoformat(),
                'recovery_metadata': {
                    'auto_save': auto_save,
                    'state_hash': self._calculate_state_hash(state),
                    'recovery_version': '1.0.0'
                }
            }
            
            # Create backup of existing state
            if self.state_file.exists():
                backup_file = self.recovery_dir / f"system_state_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                shutil.copy2(self.state_file, backup_file)
                
                # Keep only last 10 backups
                self._cleanup_backups('system_state_backup_*.json', 10)
            
            # Save new state
            with open(self.state_file, 'w') as f:
                json.dump(enhanced_state, f, indent=2, default=str)
            
            # Update current state
            self.current_state = enhanced_state
            self.recovery_metrics['state_saves'] += 1
            
            if not auto_save:
                self.logger.info("System state saved successfully")
            
        except Exception as e:
            self.logger.error(f"Error saving system state: {e}")
    
    def create_checkpoint(self, checkpoint_name: str, additional_data: Dict[str, Any] = None) -> bool:
        """Create a system checkpoint
        
        Args:
            checkpoint_name: Name for the checkpoint
            additional_data: Additional data to include in checkpoint
            
        Returns:
            True if checkpoint created successfully
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            checkpoint_file = self.checkpoints_dir / f"checkpoint_{checkpoint_name}_{timestamp}.json"
            
            checkpoint_data = {
                'checkpoint_name': checkpoint_name,
                'timestamp': datetime.now().isoformat(),
                'system_state': self.current_state,
                'additional_data': additional_data or {},
                'recovery_metrics': self.recovery_metrics.copy(),
                'checkpoint_hash': None  # Will be calculated after serialization
            }
            
            # Calculate checkpoint hash
            checkpoint_data['checkpoint_hash'] = self._calculate_checkpoint_hash(checkpoint_data)
            
            # Save checkpoint
            with open(checkpoint_file, 'w') as f:
                json.dump(checkpoint_data, f, indent=2, default=str)
            
            # Compress older checkpoints
            self._compress_old_checkpoints()
            
            # Update metrics
            self.recovery_metrics['checkpoints_created'] += 1
            self.last_checkpoint_time = datetime.now()
            
            self.logger.info(f"Checkpoint '{checkpoint_name}' created successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating checkpoint '{checkpoint_name}': {e}")
            return False
    
    def list_checkpoints(self) -> List[Dict[str, Any]]:
        """List all available checkpoints
        
        Returns:
            List of checkpoint information dictionaries
        """
        checkpoints = []
        
        try:
            # Get all checkpoint files
            checkpoint_files = list(self.checkpoints_dir.glob("checkpoint_*.json"))
            checkpoint_files.extend(self.checkpoints_dir.glob("checkpoint_*.json.gz"))
            
            for checkpoint_file in sorted(checkpoint_files):
                try:
                    if checkpoint_file.suffix == '.gz':
                        # Compressed checkpoint
                        with gzip.open(checkpoint_file, 'rt') as f:
                            checkpoint_data = json.load(f)
                    else:
                        # Uncompressed checkpoint
                        with open(checkpoint_file, 'r') as f:
                            checkpoint_data = json.load(f)
                    
                    checkpoint_info = {
                        'filename': checkpoint_file.name,
                        'checkpoint_name': checkpoint_data.get('checkpoint_name', 'Unknown'),
                        'timestamp': checkpoint_data.get('timestamp', 'Unknown'),
                        'compressed': checkpoint_file.suffix == '.gz',
                        'size_bytes': checkpoint_file.stat().st_size,
                        'hash': checkpoint_data.get('checkpoint_hash', 'Unknown')
                    }
                    
                    checkpoints.append(checkpoint_info)
                    
                except Exception as e:
                    self.logger.error(f"Error reading checkpoint {checkpoint_file}: {e}")
            
        except Exception as e:
            self.logger.error(f"Error listing checkpoints: {e}")
        
        return checkpoints
    
    def restore_checkpoint(self, checkpoint_name: str) -> Optional[Dict[str, Any]]:
        """Restore system from a specific checkpoint
        
        Args:
            checkpoint_name: Name of checkpoint to restore
            
        Returns:
            Restored state dictionary or None if restoration failed
        """
        try:
            # Find checkpoint file
            checkpoint_files = list(self.checkpoints_dir.glob(f"checkpoint_{checkpoint_name}_*.json"))
            checkpoint_files.extend(self.checkpoints_dir.glob(f"checkpoint_{checkpoint_name}_*.json.gz"))
            
            if not checkpoint_files:
                self.logger.error(f"Checkpoint '{checkpoint_name}' not found")
                return None
            
            # Use most recent checkpoint if multiple found
            checkpoint_file = sorted(checkpoint_files)[-1]
            
            # Load checkpoint
            if checkpoint_file.suffix == '.gz':
                with gzip.open(checkpoint_file, 'rt') as f:
                    checkpoint_data = json.load(f)
            else:
                with open(checkpoint_file, 'r') as f:
                    checkpoint_data = json.load(f)
            
            # Validate checkpoint integrity
            if not self._validate_checkpoint(checkpoint_data):
                self.logger.error(f"Checkpoint '{checkpoint_name}' failed integrity validation")
                return None
            
            # Extract system state
            restored_state = checkpoint_data.get('system_state', {})
            
            # Save as current state
            self.save_state(restored_state)
            
            # Update metrics
            self.recovery_metrics['successful_recoveries'] += 1
            
            self.logger.info(f"Successfully restored from checkpoint '{checkpoint_name}'")
            return restored_state
            
        except Exception as e:
            self.logger.error(f"Error restoring checkpoint '{checkpoint_name}': {e}")
            self.recovery_metrics['failed_recoveries'] += 1
            return None
    
    def validate_system_integrity(self) -> Dict[str, Any]:
        """Validate system integrity and data consistency
        
        Returns:
            Validation results dictionary
        """
        validation_results = {
            'timestamp': datetime.now().isoformat(),
            'overall_valid': True,
            'checks_performed': [],
            'errors': [],
            'warnings': []
        }
        
        try:
            # Check 1: State file integrity
            state_valid = self._validate_state_file()
            validation_results['checks_performed'].append('state_file_integrity')
            if not state_valid['valid']:
                validation_results['overall_valid'] = False
                validation_results['errors'].extend(state_valid['errors'])
            
            # Check 2: Checkpoint integrity
            checkpoints_valid = self._validate_checkpoints()
            validation_results['checks_performed'].append('checkpoint_integrity')
            if not checkpoints_valid['valid']:
                validation_results['overall_valid'] = False
                validation_results['errors'].extend(checkpoints_valid['errors'])
            
            # Check 3: Directory structure
            directories_valid = self._validate_directory_structure()
            validation_results['checks_performed'].append('directory_structure')
            if not directories_valid['valid']:
                validation_results['overall_valid'] = False
                validation_results['errors'].extend(directories_valid['errors'])
            
            # Check 4: Recovery files consistency
            recovery_files_valid = self._validate_recovery_files()
            validation_results['checks_performed'].append('recovery_files_consistency')
            if not recovery_files_valid['valid']:
                validation_results['warnings'].extend(recovery_files_valid['warnings'])
            
            # Update metrics
            self.recovery_metrics['data_integrity_checks'] += 1
            
            # Save validation results
            self._save_integrity_results(validation_results)
            
        except Exception as e:
            validation_results['overall_valid'] = False
            validation_results['errors'].append(f"Error during integrity validation: {e}")
            self.logger.error(f"Error validating system integrity: {e}")
        
        return validation_results
    
    def repair_system_state(self) -> bool:
        """Attempt to repair corrupted system state
        
        Returns:
            True if repair was successful
        """
        try:
            self.logger.info("Attempting system state repair...")
            
            # Try to restore from most recent valid checkpoint
            checkpoints = self.list_checkpoints()
            
            for checkpoint in sorted(checkpoints, key=lambda x: x['timestamp'], reverse=True):
                checkpoint_name = checkpoint['checkpoint_name']
                
                try:
                    restored_state = self.restore_checkpoint(checkpoint_name)
                    if restored_state:
                        self.logger.info(f"Successfully repaired system state from checkpoint '{checkpoint_name}'")
                        return True
                except Exception as e:
                    self.logger.warning(f"Failed to restore from checkpoint '{checkpoint_name}': {e}")
                    continue
            
            # If no valid checkpoints, create minimal state
            self.logger.warning("No valid checkpoints found, creating minimal state")
            minimal_state = self._create_minimal_state()
            self.save_state(minimal_state)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error repairing system state: {e}")
            return False
    
    def get_recovery_metrics(self) -> Dict[str, Any]:
        """Get recovery system metrics
        
        Returns:
            Recovery metrics dictionary
        """
        metrics = self.recovery_metrics.copy()
        metrics.update({
            'last_checkpoint_time': self.last_checkpoint_time.isoformat(),
            'auto_save_active': self._auto_save_active,
            'total_checkpoints': len(self.list_checkpoints()),
            'recovery_dir_size_mb': self._calculate_directory_size(self.recovery_dir) / (1024 * 1024)
        })
        
        return metrics
    
    def cleanup_old_files(self, days_to_keep: int = 30):
        """Clean up old recovery files
        
        Args:
            days_to_keep: Number of days of files to keep
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            files_deleted = 0
            
            # Clean up old backups
            backup_files = self.recovery_dir.glob("*_backup_*.json")
            for backup_file in backup_files:
                file_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
                if file_time < cutoff_date:
                    backup_file.unlink()
                    files_deleted += 1
            
            # Clean up old compressed checkpoints
            compressed_checkpoints = self.checkpoints_dir.glob("*.json.gz")
            for checkpoint_file in compressed_checkpoints:
                file_time = datetime.fromtimestamp(checkpoint_file.stat().st_mtime)
                if file_time < cutoff_date:
                    checkpoint_file.unlink()
                    files_deleted += 1
            
            self.logger.info(f"Cleaned up {files_deleted} old recovery files")
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old files: {e}")
    
    # Private helper methods
    
    def _calculate_state_hash(self, state: Dict[str, Any]) -> str:
        """Calculate hash of state for integrity checking"""
        state_str = json.dumps(state, sort_keys=True, default=str)
        return hashlib.sha256(state_str.encode()).hexdigest()
    
    def _calculate_checkpoint_hash(self, checkpoint_data: Dict[str, Any]) -> str:
        """Calculate hash of checkpoint for integrity checking"""
        # Exclude the hash field itself from calculation
        checkpoint_copy = checkpoint_data.copy()
        checkpoint_copy.pop('checkpoint_hash', None)
        checkpoint_str = json.dumps(checkpoint_copy, sort_keys=True, default=str)
        return hashlib.sha256(checkpoint_str.encode()).hexdigest()
    
    def _validate_checkpoint(self, checkpoint_data: Dict[str, Any]) -> bool:
        """Validate checkpoint integrity"""
        try:
            stored_hash = checkpoint_data.get('checkpoint_hash')
            if not stored_hash:
                return False
            
            calculated_hash = self._calculate_checkpoint_hash(checkpoint_data)
            return stored_hash == calculated_hash
            
        except Exception:
            return False
    
    def _compress_old_checkpoints(self, days_old: int = 7):
        """Compress checkpoints older than specified days"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            checkpoint_files = self.checkpoints_dir.glob("checkpoint_*.json")
            for checkpoint_file in checkpoint_files:
                file_time = datetime.fromtimestamp(checkpoint_file.stat().st_mtime)
                
                if file_time < cutoff_date:
                    # Compress the file
                    compressed_file = checkpoint_file.with_suffix('.json.gz')
                    
                    with open(checkpoint_file, 'rb') as f_in:
                        with gzip.open(compressed_file, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    
                    # Remove original file
                    checkpoint_file.unlink()
                    
        except Exception as e:
            self.logger.error(f"Error compressing old checkpoints: {e}")
    
    def _cleanup_backups(self, pattern: str, keep_count: int):
        """Clean up old backup files keeping only the most recent"""
        try:
            backup_files = sorted(self.recovery_dir.glob(pattern))
            
            if len(backup_files) > keep_count:
                files_to_delete = backup_files[:-keep_count]
                for file_to_delete in files_to_delete:
                    file_to_delete.unlink()
                    
        except Exception as e:
            self.logger.error(f"Error cleaning up backups: {e}")
    
    def _validate_state_file(self) -> Dict[str, Any]:
        """Validate state file integrity"""
        result = {'valid': True, 'errors': []}
        
        try:
            if not self.state_file.exists():
                result['errors'].append("State file does not exist")
                result['valid'] = False
                return result
            
            with open(self.state_file, 'r') as f:
                state_data = json.load(f)
            
            # Check for required fields
            required_fields = ['timestamp', 'recovery_metadata']
            for field in required_fields:
                if field not in state_data:
                    result['errors'].append(f"State file missing required field: {field}")
                    result['valid'] = False
            
            # Validate hash if present
            recovery_metadata = state_data.get('recovery_metadata', {})
            stored_hash = recovery_metadata.get('state_hash')
            if stored_hash:
                calculated_hash = self._calculate_state_hash(state_data)
                if stored_hash != calculated_hash:
                    result['errors'].append("State file hash validation failed")
                    result['valid'] = False
            
        except Exception as e:
            result['errors'].append(f"Error validating state file: {e}")
            result['valid'] = False
        
        return result
    
    def _validate_checkpoints(self) -> Dict[str, Any]:
        """Validate all checkpoints"""
        result = {'valid': True, 'errors': []}
        
        try:
            checkpoints = self.list_checkpoints()
            
            for checkpoint in checkpoints:
                checkpoint_name = checkpoint['checkpoint_name']
                
                # Load checkpoint data
                checkpoint_file = self.checkpoints_dir / checkpoint['filename']
                
                if checkpoint['compressed']:
                    with gzip.open(checkpoint_file, 'rt') as f:
                        checkpoint_data = json.load(f)
                else:
                    with open(checkpoint_file, 'r') as f:
                        checkpoint_data = json.load(f)
                
                # Validate checkpoint
                if not self._validate_checkpoint(checkpoint_data):
                    result['errors'].append(f"Checkpoint '{checkpoint_name}' failed integrity validation")
                    result['valid'] = False
                    
        except Exception as e:
            result['errors'].append(f"Error validating checkpoints: {e}")
            result['valid'] = False
        
        return result
    
    def _validate_directory_structure(self) -> Dict[str, Any]:
        """Validate recovery directory structure"""
        result = {'valid': True, 'errors': []}
        
        try:
            required_dirs = [self.recovery_dir, self.checkpoints_dir]
            
            for required_dir in required_dirs:
                if not required_dir.exists():
                    result['errors'].append(f"Required directory does not exist: {required_dir}")
                    result['valid'] = False
                elif not required_dir.is_dir():
                    result['errors'].append(f"Path exists but is not a directory: {required_dir}")
                    result['valid'] = False
                    
        except Exception as e:
            result['errors'].append(f"Error validating directory structure: {e}")
            result['valid'] = False
        
        return result
    
    def _validate_recovery_files(self) -> Dict[str, Any]:
        """Validate recovery files consistency"""
        result = {'valid': True, 'warnings': []}
        
        try:
            recovery_files = [
                self.progress_file,
                self.agent_states_file,
                self.llm_optimization_file
            ]
            
            for recovery_file in recovery_files:
                if recovery_file.exists():
                    try:
                        with open(recovery_file, 'r') as f:
                            json.load(f)
                    except json.JSONDecodeError:
                        result['warnings'].append(f"Recovery file has invalid JSON: {recovery_file.name}")
                        
        except Exception as e:
            result['warnings'].append(f"Error validating recovery files: {e}")
        
        return result
    
    def _save_integrity_results(self, results: Dict[str, Any]):
        """Save integrity validation results"""
        try:
            with open(self.integrity_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Error saving integrity results: {e}")
    
    def _create_minimal_state(self) -> Dict[str, Any]:
        """Create minimal system state for emergency recovery"""
        return {
            'system_initialized': False,
            'recovery_active': True,
            'orchestrator_running': False,
            'selected_disciplines': [],
            'system_stats': {
                'total_standards': 0,
                'active_agents': 0,
                'processing_rate': 0,
                'total_cost': 0.0,
                'quality_score': 0.0
            },
            'agent_status': {},
            'llm_usage': {},
            'last_update': datetime.now().isoformat(),
            'autonomous_decisions': [],
            'recovery_checkpoints': [],
            'emergency_recovery_created': True
        }
    
    def _calculate_directory_size(self, directory: Path) -> int:
        """Calculate total size of directory in bytes"""
        total_size = 0
        try:
            for file_path in directory.rglob('*'):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
        except Exception as e:
            self.logger.error(f"Error calculating directory size: {e}")
        
        return total_size
    
    def __del__(self):
        """Cleanup when recovery manager is destroyed"""
        self.stop_auto_save()