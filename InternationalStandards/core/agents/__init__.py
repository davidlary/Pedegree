"""
Agent System for International Standards Retrieval

Multi-agent architecture for autonomous educational standards discovery,
retrieval, processing, and validation across 19 OpenAlex disciplines.

Agent Types:
- DiscoveryAgent: Standards source discovery and identification
- RetrievalAgent: Document retrieval and parsing
- ProcessingAgent: Content analysis and classification  
- ValidationAgent: Quality assurance and validation

Author: Autonomous AI Development System
"""

from .base_agent import BaseAgent, AgentStatus, AgentMessage, TaskMetrics
from .discovery_agent import DiscoveryAgent
from .retrieval_agent import RetrievalAgent
from .processing_agent import ProcessingAgent
from .validation_agent import ValidationAgent

__version__ = "1.0.0"
__all__ = [
    'BaseAgent',
    'DiscoveryAgent', 
    'RetrievalAgent',
    'ProcessingAgent',
    'ValidationAgent',
    'AgentStatus',
    'AgentMessage',
    'TaskMetrics'
]