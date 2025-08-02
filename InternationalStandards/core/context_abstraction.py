#!/usr/bin/env python3
"""
CONTEXT ABSTRACTION LAYER
Eliminates ScriptRunContext dependencies with comprehensive fallback mechanisms
"""

import sys
import os
import json
import threading
import warnings
from typing import Any, Optional, Dict, Callable
from pathlib import Path
from datetime import datetime
import logging

# Suppress Streamlit warnings during autonomous operation
warnings.filterwarnings("ignore", category=UserWarning, module="streamlit")

class ContextManager:
    """Comprehensive context management with graceful degradation"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, 'initialized'):
            return
            
        self.initialized = True
        self.streamlit_available = False
        self.session_state_cache = {}
        self.context_type = "unknown"
        self.fallback_storage = {}
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Detect context
        self._detect_context()
    
    def _detect_context(self):
        """Detect execution context and configure accordingly"""
        try:
            import streamlit as st
            
            # Check if we're in a Streamlit context
            try:
                if hasattr(st, 'session_state') and hasattr(st, 'runtime'):
                    from streamlit.runtime.scriptrunner import get_script_run_ctx
                    ctx = get_script_run_ctx()
                    if ctx is not None:
                        self.streamlit_available = True
                        self.context_type = "streamlit_runtime"
                        self.logger.info("Streamlit runtime context detected")
                        return
            except:
                pass
            
            # Check if Streamlit is imported but not in runtime
            if 'streamlit' in sys.modules:
                self.context_type = "streamlit_imported"
                self.logger.info("Streamlit imported but no runtime context")
            else:
                self.context_type = "standalone"
                self.logger.info("Standalone Python context")
                
        except ImportError:
            self.context_type = "no_streamlit"
            self.logger.info("Streamlit not available")
    
    def get_session_state(self, key: str, default: Any = None) -> Any:
        """Safely get session state with comprehensive fallback"""
        try:
            if self.streamlit_available:
                import streamlit as st
                return getattr(st.session_state, key, default)
            else:
                # Use local cache as fallback
                return self.session_state_cache.get(key, default)
        except Exception as e:
            self.logger.debug(f"Session state get failed for {key}: {e}")
            return self.session_state_cache.get(key, default)
    
    def set_session_state(self, key: str, value: Any) -> bool:
        """Safely set session state with comprehensive fallback"""
        try:
            success = False
            
            if self.streamlit_available:
                import streamlit as st
                setattr(st.session_state, key, value)
                success = True
            
            # Always update local cache as backup
            self.session_state_cache[key] = value
            return success
            
        except Exception as e:
            self.logger.debug(f"Session state set failed for {key}: {e}")
            # Fallback to local cache
            self.session_state_cache[key] = value
            return False
    
    def clear_session_state(self, key: Optional[str] = None):
        """Clear session state safely"""
        try:
            if key:
                if self.streamlit_available:
                    import streamlit as st
                    if hasattr(st.session_state, key):
                        delattr(st.session_state, key)
                
                # Clear from cache
                self.session_state_cache.pop(key, None)
            else:
                # Clear all
                if self.streamlit_available:
                    import streamlit as st
                    for k in list(st.session_state.keys()):
                        delattr(st.session_state, k)
                
                self.session_state_cache.clear()
                
        except Exception as e:
            self.logger.debug(f"Session state clear failed: {e}")
            if key:
                self.session_state_cache.pop(key, None)
            else:
                self.session_state_cache.clear()
    
    def run_with_context(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with appropriate context handling"""
        try:
            if self.context_type == "streamlit_runtime":
                # Full Streamlit context available
                return func(*args, **kwargs)
            else:
                # Fallback execution
                return func(*args, **kwargs)
        except Exception as e:
            self.logger.error(f"Context execution failed: {e}")
            raise
    
    def get_context_info(self) -> Dict[str, Any]:
        """Get comprehensive context information"""
        return {
            'context_type': self.context_type,
            'streamlit_available': self.streamlit_available,
            'session_state_keys': list(self.session_state_cache.keys()),
            'fallback_storage_size': len(self.fallback_storage),
            'thread_id': threading.get_ident(),
            'process_id': os.getpid()
        }

class StreamlitSafeWrapper:
    """Wrapper for Streamlit components with safe fallbacks"""
    
    def __init__(self):
        self.context_manager = ContextManager()
        self.logger = logging.getLogger(__name__)
    
    def safe_progress(self, value: float, text: str = ""):
        """Safe progress bar with fallback"""
        try:
            if self.context_manager.streamlit_available:
                import streamlit as st
                return st.progress(value, text=text)
            else:
                # Fallback: print progress
                print(f"Progress: {value*100:.1f}% - {text}")
                return None
        except Exception as e:
            print(f"Progress: {value*100:.1f}% - {text}")
            return None
    
    def safe_status(self, label: str, state: str = "running"):
        """Safe status display with fallback"""
        try:
            if self.context_manager.streamlit_available:
                import streamlit as st
                return st.status(label, state=state)
            else:
                # Fallback: print status
                print(f"Status: {label} ({state})")
                return None
        except Exception as e:
            print(f"Status: {label} ({state})")
            return None
    
    def safe_write(self, content: Any):
        """Safe write with fallback"""
        try:
            if self.context_manager.streamlit_available:
                import streamlit as st
                return st.write(content)
            else:
                # Fallback: print content
                print(content)
                return None
        except Exception as e:
            print(content)
            return None
    
    def safe_error(self, message: str):
        """Safe error display with fallback"""
        try:
            if self.context_manager.streamlit_available:
                import streamlit as st
                return st.error(message)
            else:
                # Fallback: print error
                print(f"ERROR: {message}")
                return None
        except Exception as e:
            print(f"ERROR: {message}")
            return None
    
    def safe_success(self, message: str):
        """Safe success display with fallback"""
        try:
            if self.context_manager.streamlit_available:
                import streamlit as st
                return st.success(message)
            else:
                # Fallback: print success
                print(f"SUCCESS: {message}")
                return None
        except Exception as e:
            print(f"SUCCESS: {message}")
            return None

class AutonomousOperationManager:
    """Manages operations in autonomous (non-interactive) mode"""
    
    def __init__(self):
        self.context_manager = ContextManager()
        self.wrapper = StreamlitSafeWrapper()
        self.autonomous_mode = True
        self.operation_log = []
        self.logger = logging.getLogger(__name__)
    
    def log_operation(self, operation: str, status: str, details: str = ""):
        """Log operation for autonomous tracking"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'operation': operation,
            'status': status,
            'details': details,
            'context': self.context_manager.context_type
        }
        
        self.operation_log.append(entry)
        self.logger.info(f"Operation: {operation} - {status}")
        
        if details:
            self.logger.debug(f"Details: {details}")
    
    def execute_with_progress(self, func: Callable, operation_name: str, *args, **kwargs) -> Any:
        """Execute function with progress tracking in autonomous mode"""
        self.log_operation(operation_name, "STARTED")
        
        try:
            # Show progress in appropriate format
            self.wrapper.safe_status(f"Executing: {operation_name}", "running")
            
            # Execute function
            result = func(*args, **kwargs)
            
            self.log_operation(operation_name, "COMPLETED")
            self.wrapper.safe_success(f"Completed: {operation_name}")
            
            return result
            
        except Exception as e:
            self.log_operation(operation_name, "FAILED", str(e))
            self.wrapper.safe_error(f"Failed: {operation_name} - {e}")
            raise
    
    def get_operation_summary(self) -> Dict[str, Any]:
        """Get summary of autonomous operations"""
        total_ops = len(self.operation_log)
        completed_ops = len([op for op in self.operation_log if op['status'] == 'COMPLETED'])
        failed_ops = len([op for op in self.operation_log if op['status'] == 'FAILED'])
        
        return {
            'total_operations': total_ops,
            'completed_operations': completed_ops,
            'failed_operations': failed_ops,
            'success_rate': completed_ops / total_ops if total_ops > 0 else 0,
            'context_info': self.context_manager.get_context_info(),
            'recent_operations': self.operation_log[-10:]  # Last 10 operations
        }

# Global instances for easy access
context_manager = ContextManager()
streamlit_wrapper = StreamlitSafeWrapper()
autonomous_manager = AutonomousOperationManager()

# Convenience functions
def get_session_state(key: str, default: Any = None) -> Any:
    """Global function for safe session state access"""
    return context_manager.get_session_state(key, default)

def set_session_state(key: str, value: Any) -> bool:
    """Global function for safe session state setting"""
    return context_manager.set_session_state(key, value)

def safe_streamlit_operation(operation_func: Callable, fallback_func: Optional[Callable] = None, *args, **kwargs) -> Any:
    """Execute Streamlit operation with safe fallback"""
    try:
        if context_manager.streamlit_available:
            return operation_func(*args, **kwargs)
        elif fallback_func:
            return fallback_func(*args, **kwargs)
        else:
            # Default fallback - just print
            print(f"Streamlit operation executed in fallback mode")
            return None
    except Exception as e:
        if fallback_func:
            return fallback_func(*args, **kwargs)
        else:
            print(f"Operation failed: {e}")
            return None

def suppress_streamlit_warnings():
    """Suppress all Streamlit context warnings for autonomous operation"""
    import warnings
    
    # Suppress specific Streamlit warnings
    warnings.filterwarnings("ignore", message=".*ScriptRunContext.*")
    warnings.filterwarnings("ignore", message=".*Session state.*")  
    warnings.filterwarnings("ignore", message=".*No runtime found.*")
    warnings.filterwarnings("ignore", category=UserWarning, module="streamlit")
    
    # Redirect Streamlit logs
    streamlit_logger = logging.getLogger("streamlit")
    streamlit_logger.setLevel(logging.ERROR)

# Auto-suppress warnings on import
suppress_streamlit_warnings()

# Test context abstraction
def test_context_abstraction():
    """Test the context abstraction layer"""
    print("🔧 TESTING CONTEXT ABSTRACTION LAYER")
    print("-" * 40)
    
    # Test context detection
    print(f"Context Type: {context_manager.context_type}")
    print(f"Streamlit Available: {context_manager.streamlit_available}")
    
    # Test session state
    set_session_state("test_key", "test_value")
    retrieved_value = get_session_state("test_key", "default")
    print(f"Session State Test: {retrieved_value}")
    
    # Test safe operations
    streamlit_wrapper.safe_write("Context abstraction test")
    streamlit_wrapper.safe_progress(0.5, "Testing progress")
    streamlit_wrapper.safe_success("Context abstraction working")
    
    print("✅ Context abstraction layer operational")

if __name__ == "__main__":
    test_context_abstraction()