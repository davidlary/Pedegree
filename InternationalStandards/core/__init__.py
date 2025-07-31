"""
Core modules for International Standards Retrieval System

This package contains the essential components for autonomous educational
standards discovery, retrieval, and cataloging across 19 OpenAlex disciplines.

Components:
- config_manager: Configuration and settings management
- recovery_manager: Comprehensive recovery and continuation system  
- orchestrator: Multi-agent system coordination
- llm_integration: Intelligent LLM Router integration
- discovery_agent: Standards discovery and source identification
- retrieval_agent: Document retrieval and parsing
- processing_agent: Content analysis and classification
- validation_agent: Quality assurance and validation

Author: Autonomous AI Development System
"""

__version__ = "1.0.0"
__author__ = "Autonomous AI Development System" 

# Core module imports will be added as modules are implemented
__all__ = [
    'ConfigManager',
    'RecoveryManager', 
    'StandardsOrchestrator',
    'LLMIntegration',
    'DiscoveryAgent',
    'RetrievalAgent',
    'ProcessingAgent',
    'ValidationAgent'
]