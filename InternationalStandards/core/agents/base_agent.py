#!/usr/bin/env python3
"""
Base Agent for International Standards Retrieval System

Abstract base class for all agents in the multi-agent system.
Provides common functionality for communication, task management,
LLM integration, health monitoring, and recovery.

Author: Autonomous AI Development System
"""

import asyncio
import threading
import time
import json
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
import logging
import traceback

from ..llm_integration import LLMIntegration, TaskRequest, TaskResult

class AgentStatus(Enum):
    """Agent status enumeration"""
    INITIALIZING = "initializing"
    IDLE = "idle"
    RUNNING = "running"
    ERROR = "error"
    STOPPED = "stopped"
    RECOVERING = "recovering"

@dataclass
class AgentMessage:
    """Message structure for agent communication"""
    message_id: str
    sender_id: str
    recipient_id: str
    message_type: str
    content: Dict[str, Any]
    timestamp: datetime
    priority: int = 5

@dataclass
class TaskMetrics:
    """Metrics for task execution"""
    task_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    success: bool = False
    error_message: Optional[str] = None
    tokens_used: int = 0
    cost: float = 0.0
    quality_score: float = 0.0

class BaseAgent(ABC):
    """Abstract base class for all agents"""
    
    def __init__(self, agent_id: str, agent_type: str, discipline: Optional[str], 
                 config: Dict[str, Any], llm_integration: LLMIntegration):
        """Initialize base agent
        
        Args:
            agent_id: Unique agent identifier
            agent_type: Type of agent (discovery, retrieval, processing, validation)
            discipline: Academic discipline assignment
            config: Agent configuration
            llm_integration: LLM integration instance
        """
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.discipline = discipline
        self.config = config
        self.llm_integration = llm_integration
        
        # Setup logging
        self.logger = logging.getLogger(f"{__name__}.{agent_id}")
        
        # Agent state
        self.status = AgentStatus.INITIALIZING
        self.current_task = None
        self.task_queue = []
        self.message_queue = []
        
        # Performance tracking
        self.task_metrics = []
        self.performance_stats = {
            'tasks_completed': 0,
            'tasks_failed': 0,
            'total_processing_time': 0.0,
            'average_processing_time': 0.0,
            'success_rate': 1.0,
            'tokens_used': 0,
            'total_cost': 0.0,
            'last_activity': datetime.now()
        }
        
        # Health monitoring
        self.last_heartbeat = datetime.now()
        self.error_count = 0
        self.max_errors = config.get('max_errors', 5)
        
        # Threading and async
        self.agent_thread = None
        self.stop_event = threading.Event()
        self.task_lock = threading.Lock()
        self.message_lock = threading.Lock()
        
        # Communication
        self.message_handlers = {}
        self.orchestrator_callback = None
        
        # Recovery and persistence
        self.checkpoint_data = {}
        self.recovery_enabled = config.get('recovery_enabled', True)
        
        # LLM optimization settings
        self.llm_task_types = self._initialize_llm_task_types()
        
        self.logger.info(f"Agent {agent_id} ({agent_type}) initialized for discipline {discipline}")
    
    @abstractmethod
    def _process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a specific task (implemented by subclasses)
        
        Args:
            task: Task dictionary
            
        Returns:
            Task result dictionary
        """
        pass
    
    @abstractmethod
    def _initialize_llm_task_types(self) -> Dict[str, str]:
        """Initialize LLM task type mappings (implemented by subclasses)
        
        Returns:
            Dictionary mapping agent operations to LLM task types
        """
        pass
    
    def start(self) -> bool:
        """Start the agent
        
        Returns:
            True if started successfully
        """
        try:
            if self.agent_thread and self.agent_thread.is_alive():
                self.logger.warning("Agent is already running")
                return True
            
            self.stop_event.clear()
            self.status = AgentStatus.IDLE
            
            # Start agent thread
            self.agent_thread = threading.Thread(target=self._agent_main_loop, daemon=True)
            self.agent_thread.start()
            
            self.logger.info("Agent started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting agent: {e}")
            self.status = AgentStatus.ERROR
            return False
    
    def stop(self) -> bool:
        """Stop the agent
        
        Returns:
            True if stopped successfully
        """
        try:
            self.logger.info("Stopping agent...")
            
            self.stop_event.set()
            self.status = AgentStatus.STOPPED
            
            # Wait for agent thread to finish
            if self.agent_thread and self.agent_thread.is_alive():
                self.agent_thread.join(timeout=10)
            
            self.logger.info("Agent stopped successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error stopping agent: {e}")
            return False
    
    def assign_task(self, task: Dict[str, Any]) -> bool:
        """Assign a new task to the agent
        
        Args:
            task: Task dictionary
            
        Returns:
            True if task was assigned successfully
        """
        try:
            with self.task_lock:
                self.task_queue.append(task)
                # Sort by priority (lower number = higher priority)
                self.task_queue.sort(key=lambda t: t.get('priority', 5))
            
            self.logger.info(f"Task assigned: {task.get('task_id', 'unknown')}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error assigning task: {e}")
            return False
    
    def send_message(self, recipient_id: str, message_type: str, content: Dict[str, Any], 
                     priority: int = 5) -> bool:
        """Send message to another agent or orchestrator
        
        Args:
            recipient_id: ID of recipient
            message_type: Type of message
            content: Message content
            priority: Message priority
            
        Returns:
            True if message was sent successfully
        """
        try:
            message = AgentMessage(
                message_id=f"{self.agent_id}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
                sender_id=self.agent_id,
                recipient_id=recipient_id,
                message_type=message_type,
                content=content,
                timestamp=datetime.now(),
                priority=priority
            )
            
            # Send via orchestrator callback if available
            if self.orchestrator_callback:
                self.orchestrator_callback(message)
                return True
            else:
                self.logger.warning("No orchestrator callback available for message sending")
                return False
                
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            return False
    
    def receive_message(self, message: AgentMessage) -> bool:
        """Receive message from another agent or orchestrator
        
        Args:
            message: Message to receive
            
        Returns:
            True if message was processed successfully
        """
        try:
            with self.message_lock:
                self.message_queue.append(message)
                # Sort by priority
                self.message_queue.sort(key=lambda m: m.priority)
            
            self.logger.debug(f"Message received from {message.sender_id}: {message.message_type}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error receiving message: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status
        
        Returns:
            Status dictionary
        """
        return {
            'agent_id': self.agent_id,
            'agent_type': self.agent_type,
            'discipline': self.discipline,
            'status': self.status.value,
            'current_task': self.current_task,
            'task_queue_size': len(self.task_queue),
            'message_queue_size': len(self.message_queue),
            'last_heartbeat': self.last_heartbeat.isoformat(),
            'error_count': self.error_count,
            'performance_stats': self.performance_stats.copy()
        }
    
    def get_health_metrics(self) -> Dict[str, Any]:
        """Get agent health metrics
        
        Returns:
            Health metrics dictionary
        """
        current_time = datetime.now()
        time_since_heartbeat = (current_time - self.last_heartbeat).total_seconds()
        
        return {
            'agent_id': self.agent_id,
            'status': self.status.value,
            'health_score': self._calculate_health_score(),
            'time_since_heartbeat': time_since_heartbeat,
            'error_count': self.error_count,
            'max_errors': self.max_errors,
            'success_rate': self.performance_stats['success_rate'],
            'is_responsive': time_since_heartbeat < 300,  # 5 minutes
            'last_task_completion': self._get_last_task_completion_time()
        }
    
    def create_checkpoint(self) -> Dict[str, Any]:
        """Create agent checkpoint for recovery
        
        Returns:
            Checkpoint data dictionary
        """
        try:
            checkpoint_data = {
                'agent_id': self.agent_id,
                'agent_type': self.agent_type,
                'discipline': self.discipline,
                'status': self.status.value,
                'current_task': self.current_task,
                'task_queue': self.task_queue.copy(),
                'performance_stats': self.performance_stats.copy(),
                'checkpoint_timestamp': datetime.now().isoformat(),
                'error_count': self.error_count
            }
            
            self.checkpoint_data = checkpoint_data
            return checkpoint_data
            
        except Exception as e:
            self.logger.error(f"Error creating checkpoint: {e}")
            return {}
    
    def restore_from_checkpoint(self, checkpoint_data: Dict[str, Any]) -> bool:
        """Restore agent from checkpoint
        
        Args:
            checkpoint_data: Checkpoint data
            
        Returns:
            True if restoration was successful
        """
        try:
            self.current_task = checkpoint_data.get('current_task')
            self.task_queue = checkpoint_data.get('task_queue', [])
            self.performance_stats.update(checkpoint_data.get('performance_stats', {}))
            self.error_count = checkpoint_data.get('error_count', 0)
            
            self.logger.info("Agent restored from checkpoint successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error restoring from checkpoint: {e}")
            return False
    
    def set_orchestrator_callback(self, callback: Callable):
        """Set callback for communicating with orchestrator
        
        Args:
            callback: Callback function
        """
        self.orchestrator_callback = callback
    
    # Protected/Private methods
    
    def _agent_main_loop(self):
        """Main agent loop running in separate thread"""
        self.logger.info("Agent main loop started")
        
        while not self.stop_event.is_set():
            try:
                # Update heartbeat
                self.last_heartbeat = datetime.now()
                
                # Process messages
                self._process_messages()
                
                # Execute tasks
                self._execute_tasks()
                
                # Update performance stats
                self._update_performance_stats()
                
                # Check if recovery is needed
                if self.status == AgentStatus.ERROR and self.recovery_enabled:
                    self._attempt_recovery()
                
                # Sleep before next iteration
                time.sleep(1)  # 1 second polling interval
                
            except Exception as e:
                self.logger.error(f"Error in agent main loop: {e}")
                self._handle_error(e)
                time.sleep(5)  # Longer sleep on error
        
        self.logger.info("Agent main loop ended")
    
    def _process_messages(self):
        """Process incoming messages"""
        with self.message_lock:
            while self.message_queue:
                message = self.message_queue.pop(0)
                try:
                    self._handle_message(message)
                except Exception as e:
                    self.logger.error(f"Error processing message {message.message_id}: {e}")
    
    def _handle_message(self, message: AgentMessage):
        """Handle a specific message
        
        Args:
            message: Message to handle
        """
        message_type = message.message_type
        
        if message_type in self.message_handlers:
            self.message_handlers[message_type](message)
        elif message_type == 'ping':
            self._handle_ping_message(message)
        elif message_type == 'status_request':
            self._handle_status_request(message)
        elif message_type == 'task_assignment':
            self._handle_task_assignment(message)
        else:
            self.logger.warning(f"Unknown message type: {message_type}")
    
    def _handle_ping_message(self, message: AgentMessage):
        """Handle ping message"""
        # Send pong response
        self.send_message(
            message.sender_id,
            'pong',
            {'agent_id': self.agent_id, 'status': self.status.value}
        )
    
    def _handle_status_request(self, message: AgentMessage):
        """Handle status request message"""
        status = self.get_status()
        self.send_message(
            message.sender_id,
            'status_response',
            status
        )
    
    def _handle_task_assignment(self, message: AgentMessage):
        """Handle task assignment message"""
        task = message.content.get('task')
        if task:
            self.assign_task(task)
    
    def _execute_tasks(self):
        """Execute pending tasks"""
        if self.status not in [AgentStatus.IDLE, AgentStatus.RUNNING]:
            return
        
        with self.task_lock:
            if not self.task_queue:
                if self.status == AgentStatus.RUNNING:
                    self.status = AgentStatus.IDLE
                return
            
            # Get next task
            task = self.task_queue.pop(0)
        
        # Execute the task
        self._execute_single_task(task)
    
    def _execute_single_task(self, task: Dict[str, Any]):
        """Execute a single task
        
        Args:
            task: Task to execute
        """
        task_id = task.get('task_id', 'unknown')
        start_time = datetime.now()
        
        try:
            self.status = AgentStatus.RUNNING
            self.current_task = task_id
            
            self.logger.info(f"Starting task {task_id}")
            
            # Process the task (subclass implementation)
            result = self._process_task(task)
            
            # Record success
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            metrics = TaskMetrics(
                task_id=task_id,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                success=True,
                tokens_used=result.get('tokens_used', 0),
                cost=result.get('cost', 0.0),
                quality_score=result.get('quality_score', 0.0)
            )
            
            self.task_metrics.append(metrics)
            self.performance_stats['tasks_completed'] += 1
            self.performance_stats['total_processing_time'] += duration
            self.performance_stats['tokens_used'] += metrics.tokens_used
            self.performance_stats['total_cost'] += metrics.cost
            
            # Send completion message to orchestrator
            self.send_message(
                'orchestrator',
                'task_completed',
                {
                    'task_id': task_id,
                    'result': result,
                    'metrics': asdict(metrics)
                }
            )
            
            self.logger.info(f"Task {task_id} completed successfully in {duration:.2f}s")
            
        except Exception as e:
            # Record failure
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            metrics = TaskMetrics(
                task_id=task_id,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                success=False,
                error_message=str(e)
            )
            
            self.task_metrics.append(metrics)
            self.performance_stats['tasks_failed'] += 1
            
            self.logger.error(f"Task {task_id} failed: {e}")
            self._handle_error(e)
            
            # Send failure message to orchestrator
            self.send_message(
                'orchestrator',
                'task_failed',
                {
                    'task_id': task_id,
                    'error': str(e),
                    'metrics': asdict(metrics)
                }
            )
        
        finally:
            self.current_task = None
            self.status = AgentStatus.IDLE
            self.performance_stats['last_activity'] = datetime.now()
    
    def _handle_error(self, error: Exception):
        """Handle agent error
        
        Args:
            error: Error that occurred
        """
        self.error_count += 1
        
        if self.error_count >= self.max_errors:
            self.logger.error(f"Maximum errors ({self.max_errors}) reached, stopping agent")
            self.status = AgentStatus.ERROR
        else:
            self.logger.warning(f"Error {self.error_count}/{self.max_errors}: {error}")
    
    def _attempt_recovery(self):
        """Attempt to recover from error state"""
        try:
            self.logger.info("Attempting agent recovery...")
            self.status = AgentStatus.RECOVERING
            
            # Clear task queue of failed tasks
            with self.task_lock:
                self.task_queue.clear()
            
            # Reset error count
            self.error_count = 0
            
            # Mark as idle and ready for new tasks
            self.status = AgentStatus.IDLE
            
            self.logger.info("Agent recovery successful")
            
        except Exception as e:
            self.logger.error(f"Agent recovery failed: {e}")
            self.status = AgentStatus.ERROR
    
    def _update_performance_stats(self):
        """Update performance statistics"""
        if self.task_metrics:
            # Calculate success rate
            total_tasks = len(self.task_metrics)
            successful_tasks = sum(1 for m in self.task_metrics if m.success)
            self.performance_stats['success_rate'] = successful_tasks / total_tasks
            
            # Calculate average processing time
            successful_durations = [m.duration for m in self.task_metrics if m.success and m.duration]
            if successful_durations:
                self.performance_stats['average_processing_time'] = sum(successful_durations) / len(successful_durations)
    
    def _calculate_health_score(self) -> float:
        """Calculate agent health score (0.0 to 1.0)
        
        Returns:
            Health score
        """
        score = 1.0
        
        # Penalize errors
        if self.max_errors > 0:
            error_penalty = (self.error_count / self.max_errors) * 0.5
            score -= error_penalty
        
        # Factor in success rate
        score *= self.performance_stats['success_rate']
        
        # Factor in responsiveness
        time_since_heartbeat = (datetime.now() - self.last_heartbeat).total_seconds()
        if time_since_heartbeat > 300:  # 5 minutes
            score *= 0.5
        
        return max(score, 0.0)
    
    def _get_last_task_completion_time(self) -> Optional[str]:
        """Get timestamp of last completed task
        
        Returns:
            ISO timestamp string or None
        """
        completed_tasks = [m for m in self.task_metrics if m.success and m.end_time]
        if completed_tasks:
            last_task = max(completed_tasks, key=lambda t: t.end_time)
            return last_task.end_time.isoformat()
        return None
    
    def _execute_llm_task(self, prompt: str, task_type: str, quality_requirement: str = "standard") -> TaskResult:
        """Execute an LLM task through the integration layer
        
        Args:
            prompt: LLM prompt
            task_type: Type of LLM task
            quality_requirement: Quality requirement level
            
        Returns:
            Task result
        """
        try:
            # Create task request
            task_request = TaskRequest(
                prompt=prompt,
                task_type=task_type,
                discipline=self.discipline,
                quality_requirement=quality_requirement,
                priority="normal"
            )
            
            # Execute through LLM integration
            result = self.llm_integration.execute_task(task_request)
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing LLM task: {e}")
            # Return error result
            return TaskResult(
                response=f"Error: {e}",
                model_used="error",
                tokens_used={'input': 0, 'output': 0},
                cost=0.0,
                quality_score=0.0,
                processing_time=0.0,
                timestamp=datetime.now()
            )
    
    def __del__(self):
        """Cleanup when agent is destroyed"""
        if hasattr(self, 'stop_event'):
            self.stop()