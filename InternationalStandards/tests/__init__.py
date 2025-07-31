"""
Testing Framework for International Standards Retrieval System

Comprehensive testing suite covering all 11 testing categories with automation:
1. Unit Tests - Individual component testing
2. Integration Tests - Cross-component interaction testing  
3. System Tests - End-to-end system behavior testing
4. Performance Tests - Speed, throughput, and scalability testing
5. Load Tests - High-volume concurrent operation testing
6. Recovery Tests - System recovery and continuation testing
7. LLM Integration Tests - AI model integration and optimization testing
8. Data Quality Tests - Standards extraction and validation testing
9. Agent Communication Tests - Multi-agent system communication testing
10. Configuration Tests - System configuration and setup testing
11. Compliance Tests - Educational standards compliance and accuracy testing

Author: Autonomous AI Development System
"""

import sys
import os
from pathlib import Path

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

__version__ = "1.0.0"
__all__ = [
    'TestSuite',
    'TestRunner',
    'TestReporter',
    'AutomatedTestFramework'
]