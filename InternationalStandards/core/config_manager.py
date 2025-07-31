#!/usr/bin/env python3
"""
Configuration Manager for International Standards Retrieval System

Autonomous configuration management with dynamic loading and validation.
Handles all system configuration including disciplines, LLM optimization,
recovery settings, and runtime parameters.

Author: Autonomous AI Development System
"""

import yaml
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging
from datetime import datetime

class ConfigManager:
    """Comprehensive configuration management system"""
    
    def __init__(self, config_dir: Path):
        """Initialize configuration manager
        
        Args:
            config_dir: Path to configuration directory
        """
        self.config_dir = Path(config_dir)
        self.data_dir = self.config_dir.parent / "data"  # Add data_dir attribute
        self.config_cache = {}
        self.last_loaded = {}
        
        # Ensure config and data directories exist
        self.config_dir.mkdir(exist_ok=True)
        self.data_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Load all configurations
        self._load_all_configurations()
    
    def _load_all_configurations(self):
        """Load all configuration files"""
        config_files = [
            'openalex_disciplines.yaml',
            'standards_ecosystem.yaml',
            'recovery_system.yaml', 
            'llm_optimization.yaml',
            'system_architecture.yaml'
        ]
        
        for config_file in config_files:
            try:
                self._load_config_file(config_file)
            except Exception as e:
                self.logger.error(f"Error loading {config_file}: {e}")
    
    def _load_config_file(self, filename: str) -> Dict[str, Any]:
        """Load a specific configuration file
        
        Args:
            filename: Name of configuration file
            
        Returns:
            Configuration dictionary
        """
        file_path = self.config_dir / filename
        config_key = filename.replace('.yaml', '').replace('.json', '')
        
        if not file_path.exists():
            self.logger.warning(f"Configuration file not found: {filename}")
            self.config_cache[config_key] = {}
            return {}
        
        try:
            with open(file_path, 'r') as f:
                if filename.endswith('.yaml'):
                    config_data = yaml.safe_load(f)
                elif filename.endswith('.json'):
                    config_data = json.load(f)
                else:
                    self.logger.error(f"Unsupported config file format: {filename}")
                    return {}
            
            self.config_cache[config_key] = config_data
            self.last_loaded[config_key] = datetime.now()
            
            self.logger.info(f"Successfully loaded configuration: {filename}")
            return config_data
            
        except Exception as e:
            self.logger.error(f"Error loading configuration file {filename}: {e}")
            self.config_cache[config_key] = {}
            return {}
    
    def get_config(self, config_name: str, refresh: bool = False) -> Dict[str, Any]:
        """Get configuration by name
        
        Args:
            config_name: Name of configuration (without extension)
            refresh: Whether to refresh from file
            
        Returns:
            Configuration dictionary
        """
        if refresh or config_name not in self.config_cache:
            filename = f"{config_name}.yaml"
            if not (self.config_dir / filename).exists():
                filename = f"{config_name}.json"  # Try JSON if YAML doesn't exist
            
            return self._load_config_file(filename)
        
        return self.config_cache.get(config_name, {})
    
    def get_disciplines(self) -> Dict[str, Any]:
        """Get OpenAlex disciplines configuration
        
        Returns:
            Disciplines configuration dictionary
        """
        config = self.get_config('openalex_disciplines')
        return config.get('disciplines', {})
    
    def get_discipline_info(self, discipline_name: str) -> Dict[str, Any]:
        """Get information for a specific discipline
        
        Args:
            discipline_name: Name of the discipline
            
        Returns:
            Discipline information dictionary
        """
        disciplines = self.get_disciplines()
        return disciplines.get(discipline_name, {})
    
    def get_cross_disciplinary_standards(self) -> Dict[str, List[str]]:
        """Get cross-disciplinary standards mapping
        
        Returns:
            Cross-disciplinary standards dictionary
        """
        config = self.get_config('openalex_disciplines')
        return config.get('cross_disciplinary_standards', {})
    
    def get_standards_ecosystem(self) -> Dict[str, Any]:
        """Get standards ecosystem configuration
        
        Returns:
            Standards ecosystem configuration
        """
        return self.get_config('standards_ecosystem')
    
    def get_llm_optimization_config(self) -> Dict[str, Any]:
        """Get LLM optimization configuration
        
        Returns:
            LLM optimization configuration
        """
        return self.get_config('llm_optimization')
    
    def get_recovery_config(self) -> Dict[str, Any]:
        """Get recovery system configuration
        
        Returns:
            Recovery system configuration
        """
        return self.get_config('recovery_system')
    
    def get_system_architecture(self) -> Dict[str, Any]:
        """Get system architecture configuration
        
        Returns:
            System architecture configuration
        """
        return self.get_config('system_architecture')
    
    def get_task_optimization_config(self, task_type: str) -> Dict[str, Any]:
        """Get LLM optimization config for specific task type
        
        Args:
            task_type: Type of task (e.g., 'standards_discovery')
            
        Returns:
            Task-specific optimization configuration
        """
        llm_config = self.get_llm_optimization_config()
        task_optimization = llm_config.get('task_optimization', {})
        return task_optimization.get(task_type, {})
    
    def get_discipline_optimization_config(self, discipline: str) -> Dict[str, Any]:
        """Get LLM optimization config for specific discipline
        
        Args:
            discipline: Name of the discipline
            
        Returns:
            Discipline-specific optimization configuration
        """
        llm_config = self.get_llm_optimization_config()
        discipline_optimization = llm_config.get('discipline_optimization', {})
        return discipline_optimization.get(discipline, {})
    
    def get_agent_config(self, agent_type: str) -> Dict[str, Any]:
        """Get configuration for specific agent type
        
        Args:
            agent_type: Type of agent (e.g., 'discovery_agents')
            
        Returns:
            Agent configuration dictionary
        """
        architecture = self.get_system_architecture()
        agent_system = architecture.get('agent_system', {})
        return agent_system.get(agent_type, {})
    
    def update_config(self, config_name: str, updates: Dict[str, Any]):
        """Update configuration with new values
        
        Args:
            config_name: Name of configuration to update
            updates: Dictionary of updates to apply
        """
        current_config = self.get_config(config_name)
        current_config.update(updates)
        
        # Save updated configuration
        self.save_config(config_name, current_config)
    
    def save_config(self, config_name: str, config_data: Dict[str, Any]):
        """Save configuration to file
        
        Args:
            config_name: Name of configuration
            config_data: Configuration data to save
        """
        try:
            filename = f"{config_name}.yaml"
            file_path = self.config_dir / filename
            
            with open(file_path, 'w') as f:
                yaml.dump(config_data, f, default_flow_style=False, indent=2)
            
            # Update cache
            self.config_cache[config_name] = config_data
            self.last_loaded[config_name] = datetime.now()
            
            self.logger.info(f"Successfully saved configuration: {filename}")
            
        except Exception as e:
            self.logger.error(f"Error saving configuration {config_name}: {e}")
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Validate all configurations
        
        Returns:
            Validation results dictionary
        """
        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'configs_validated': []
        }
        
        # Validate disciplines configuration
        disciplines_valid = self._validate_disciplines_config()
        validation_results['configs_validated'].append('disciplines')
        if not disciplines_valid['valid']:
            validation_results['valid'] = False
            validation_results['errors'].extend(disciplines_valid['errors'])
        
        # Validate LLM optimization configuration
        llm_valid = self._validate_llm_config()
        validation_results['configs_validated'].append('llm_optimization')
        if not llm_valid['valid']:
            validation_results['valid'] = False
            validation_results['errors'].extend(llm_valid['errors'])
        
        # Validate recovery configuration
        recovery_valid = self._validate_recovery_config()
        validation_results['configs_validated'].append('recovery_system')
        if not recovery_valid['valid']:
            validation_results['valid'] = False
            validation_results['errors'].extend(recovery_valid['errors'])
        
        return validation_results
    
    def _validate_disciplines_config(self) -> Dict[str, Any]:
        """Validate disciplines configuration
        
        Returns:
            Validation results for disciplines
        """
        result = {'valid': True, 'errors': []}
        
        try:
            disciplines = self.get_disciplines()
            
            # Check that we have 19 disciplines
            if len(disciplines) != 19:
                result['valid'] = False
                result['errors'].append(f"Expected 19 disciplines, found {len(disciplines)}")
            
            # Validate each discipline has required fields
            required_fields = ['display_name', 'description', 'subdisciplines', 'priority']
            
            for discipline_name, discipline_info in disciplines.items():
                for field in required_fields:
                    if field not in discipline_info:
                        result['valid'] = False
                        result['errors'].append(f"Discipline {discipline_name} missing required field: {field}")
            
        except Exception as e:
            result['valid'] = False
            result['errors'].append(f"Error validating disciplines config: {e}")
        
        return result
    
    def _validate_llm_config(self) -> Dict[str, Any]:
        """Validate LLM optimization configuration
        
        Returns:
            Validation results for LLM config
        """
        result = {'valid': True, 'errors': []}
        
        try:
            llm_config = self.get_llm_optimization_config()
            
            # Check required sections
            required_sections = ['llm_router_integration', 'task_optimization', 'discipline_optimization']
            
            for section in required_sections:
                if section not in llm_config:
                    result['valid'] = False
                    result['errors'].append(f"LLM config missing required section: {section}")
            
            # Validate router integration
            router_config = llm_config.get('llm_router_integration', {})
            if 'router_path' not in router_config:
                result['valid'] = False
                result['errors'].append("LLM router path not configured")
            
        except Exception as e:
            result['valid'] = False
            result['errors'].append(f"Error validating LLM config: {e}")
        
        return result
    
    def _validate_recovery_config(self) -> Dict[str, Any]:
        """Validate recovery system configuration
        
        Returns:
            Validation results for recovery config
        """
        result = {'valid': True, 'errors': []}
        
        try:
            recovery_config = self.get_recovery_config()
            
            # Check required sections
            required_sections = ['recovery_settings', 'agent_recovery', 'data_recovery']
            
            for section in required_sections:
                if section not in recovery_config:
                    result['valid'] = False
                    result['errors'].append(f"Recovery config missing required section: {section}")
            
        except Exception as e:
            result['valid'] = False
            result['errors'].append(f"Error validating recovery config: {e}")
        
        return result
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get summary of all configurations
        
        Returns:
            Configuration summary dictionary
        """
        summary = {
            'total_configs': len(self.config_cache),
            'loaded_configs': list(self.config_cache.keys()),
            'last_loaded_times': self.last_loaded,
            'disciplines_count': len(self.get_disciplines()),
            'validation_status': self.validate_configuration()
        }
        
        return summary