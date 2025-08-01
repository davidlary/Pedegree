#!/usr/bin/env python3
"""
Standards Orchestrator for International Standards Retrieval System

Multi-agent system coordinator for autonomous educational standards discovery,
retrieval, and cataloging across 19 OpenAlex disciplines. Manages agent 
lifecycle, task distribution, load balancing, and recovery coordination.

Author: Autonomous AI Development System
"""

import asyncio
import threading
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import logging
from enum import Enum
from dataclasses import dataclass
import json

# Import core modules
from .config_manager import ConfigManager
from .recovery_manager import RecoveryManager
from .llm_integration import LLMIntegration, TaskRequest
from .agents import BaseAgent, DiscoveryAgent, RetrievalAgent, ProcessingAgent, ValidationAgent, AgentStatus as BaseAgentStatus

class AgentStatus(Enum):
    """Agent status enumeration"""
    IDLE = "idle"
    RUNNING = "running"
    ERROR = "error"
    STOPPED = "stopped"
    INITIALIZING = "initializing"

class TaskStatus(Enum):
    """Task status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class AgentInfo:
    """Information about an agent"""
    agent_id: str
    agent_type: str
    status: AgentStatus
    discipline: Optional[str]
    current_task: Optional[str]
    last_heartbeat: datetime
    performance_metrics: Dict[str, Any]
    error_count: int

@dataclass
class Task:
    """Task data structure"""
    task_id: str
    task_type: str
    discipline: str
    parameters: Dict[str, Any]
    priority: int
    status: TaskStatus
    assigned_agent: Optional[str]
    created_time: datetime
    started_time: Optional[datetime]
    completed_time: Optional[datetime]
    result: Optional[Dict[str, Any]]
    error_message: Optional[str]

class StandardsOrchestrator:
    """Central orchestrator for the multi-agent standards retrieval system"""
    
    def __init__(self, config_manager: ConfigManager, recovery_manager: RecoveryManager, 
                 llm_integration: LLMIntegration):
        """Initialize the orchestrator
        
        Args:
            config_manager: Configuration manager instance
            recovery_manager: Recovery manager instance
            llm_integration: LLM integration instance
        """
        self.config_manager = config_manager
        self.recovery_manager = recovery_manager
        self.llm_integration = llm_integration
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # System state
        self.is_running = False
        self.agents = {}  # agent_id -> BaseAgent instance
        self.task_queue = []  # List of pending tasks
        self.active_tasks = {}  # task_id -> Task
        self.completed_tasks = {}  # task_id -> Task
        
        # Performance tracking
        self.system_metrics = {
            'total_tasks_processed': 0,
            'total_standards_discovered': 0,
            'total_agents_active': 0,
            'average_processing_time': 0.0,
            'system_efficiency': 0.0,
            'last_update': datetime.now()
        }
        
        # Load configuration
        self.architecture_config = config_manager.get_system_architecture()
        self.agent_configs = self.architecture_config.get('agent_system', {})
        
        # Threading and async management
        self.orchestrator_thread = None
        self.stop_event = threading.Event()
        self.task_lock = threading.Lock()
        self.agents_lock = threading.Lock()
        
        # Discipline processing tracking
        self.discipline_progress = {}
        self.selected_disciplines = []
        
        # Initialize discipline progress tracking
        self._initialize_discipline_tracking()
    
    def initialize_all_agents(self) -> bool:
        """Initialize all 59 agents as specified in original requirements
        
        Creates:
        - 19 Discovery Agents (one per discipline)
        - 20 Retrieval Agents 
        - 15 Processing Agents
        - 5 Validation Agents
        
        Returns:
            True if all agents initialized successfully
        """
        try:
            self.logger.info("Initializing all 59 agents...")
            
            # Get disciplines for discovery agents
            disciplines = self.config_manager.get_disciplines()
            discipline_names = list(disciplines.keys())[:19]  # First 19
            
            with self.agents_lock:
                # Initialize 19 Discovery Agents (one per discipline)
                for i, discipline in enumerate(discipline_names):
                    agent_id = f"discovery_{discipline.lower().replace(' ', '_')}"
                    agent = DiscoveryAgent(
                        agent_id=agent_id,
                        discipline=discipline,
                        config=self.agent_configs.get('discovery_agents', {}),
                        llm_integration=self.llm_integration,
                        config_manager=self.config_manager
                    )
                    self.agents[agent_id] = agent
                    self.logger.info(f"Created discovery agent for {discipline}")
                
                # Initialize 20 Retrieval Agents
                for i in range(20):
                    agent_id = f"retrieval_agent_{i+1:02d}"
                    agent = RetrievalAgent(
                        agent_id=agent_id,
                        discipline="multi_discipline", 
                        config=self.agent_configs.get('retrieval_agents', {}),
                        llm_integration=self.llm_integration,
                        config_manager=self.config_manager
                    )
                    self.agents[agent_id] = agent
                    self.logger.info(f"Created retrieval agent {i+1}")
                
                # Initialize 15 Processing Agents
                for i in range(15):
                    agent_id = f"processing_agent_{i+1:02d}"
                    agent = ProcessingAgent(
                        agent_id=agent_id,
                        discipline="multi_discipline",
                        config=self.agent_configs.get('processing_agents', {}),
                        llm_integration=self.llm_integration,
                        config_manager=self.config_manager
                    )
                    self.agents[agent_id] = agent
                    self.logger.info(f"Created processing agent {i+1}")
                
                # Initialize 5 Validation Agents
                for i in range(5):
                    agent_id = f"validation_agent_{i+1:02d}"
                    agent = ValidationAgent(
                        agent_id=agent_id,
                        discipline="multi_discipline",
                        config=self.agent_configs.get('validation_agents', {}),
                        llm_integration=self.llm_integration,
                        config_manager=self.config_manager
                    )
                    self.agents[agent_id] = agent
                    self.logger.info(f"Created validation agent {i+1}")
            
            total_agents = len(self.agents)
            self.logger.info(f"Successfully initialized {total_agents} agents")
            
            # Update system metrics
            self.system_metrics['total_agents_active'] = total_agents
            
            return total_agents == 59
            
        except Exception as e:
            self.logger.error(f"Failed to initialize agents: {e}")
            return False
    
    def _initialize_discipline_tracking(self):
        """Initialize progress tracking for all disciplines"""
        disciplines = self.config_manager.get_disciplines()
        
        for discipline_name in disciplines.keys():
            self.discipline_progress[discipline_name] = {
                'status': 'not_started',
                'progress_percentage': 0.0,
                'standards_discovered': 0,
                'standards_processed': 0,
                'active_agents': 0,
                'last_update': datetime.now(),
                'estimated_completion': None
            }
    
    def start_system(self, selected_disciplines: List[str]) -> bool:
        """Start the orchestrator and agent system
        
        Args:
            selected_disciplines: List of disciplines to process
            
        Returns:
            True if system started successfully
        """
        try:
            if self.is_running:
                self.logger.warning("System is already running")
                return True
            
            self.selected_disciplines = selected_disciplines
            self.logger.info(f"Starting orchestrator for disciplines: {selected_disciplines}")
            
            # Start recovery system auto-save
            self.recovery_manager.start_auto_save()
            
            # Initialize agents for selected disciplines
            success = self._initialize_agents()
            
            if not success:
                self.logger.error("Failed to initialize agents")
                return False
            
            # Start all agents
            self.logger.info(f"Starting {len(self.agents)} agents...")
            started_agents = 0
            for agent_id, agent in self.agents.items():
                try:
                    if agent.start():
                        started_agents += 1
                        self.logger.debug(f"Started agent {agent_id}")
                    else:
                        self.logger.warning(f"Failed to start agent {agent_id}")
                except Exception as e:
                    self.logger.error(f"Error starting agent {agent_id}: {e}")
            
            self.logger.info(f"Successfully started {started_agents}/{len(self.agents)} agents")
            
            # Start orchestrator thread
            self.is_running = True
            self.stop_event.clear()
            self.orchestrator_thread = threading.Thread(target=self._orchestrator_main_loop, daemon=True)
            self.orchestrator_thread.start()
            
            # Create startup checkpoint
            self.recovery_manager.create_checkpoint('orchestrator_startup', {
                'selected_disciplines': selected_disciplines,
                'agent_count': len(self.agents),
                'startup_timestamp': datetime.now().isoformat()
            })
            
            self.logger.info("Orchestrator started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting orchestrator: {e}")
            self.is_running = False
            return False
    
    def stop_system(self) -> bool:
        """Stop the orchestrator and all agents
        
        Returns:
            True if system stopped successfully
        """
        try:
            if not self.is_running:
                self.logger.warning("System is not running")
                return True
            
            self.logger.info("Stopping orchestrator...")
            
            # Signal all components to stop
            self.stop_event.set()
            self.is_running = False
            
            # Stop all agents
            self._stop_all_agents()
            
            # Wait for orchestrator thread to finish
            if self.orchestrator_thread and self.orchestrator_thread.is_alive():
                self.orchestrator_thread.join(timeout=10)
            
            # Stop recovery system auto-save
            self.recovery_manager.stop_auto_save()
            
            # Create shutdown checkpoint
            self.recovery_manager.create_checkpoint('orchestrator_shutdown', {
                'shutdown_timestamp': datetime.now().isoformat(),
                'final_metrics': self.system_metrics.copy()
            })
            
            self.logger.info("Orchestrator stopped successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error stopping orchestrator: {e}")
            return False
    
    def add_task(self, task_type: str, discipline: str, parameters: Dict[str, Any], 
                 priority: int = 5) -> str:
        """Add a new task to the queue
        
        Args:
            task_type: Type of task (discovery, retrieval, processing, validation)
            discipline: Academic discipline
            parameters: Task parameters
            priority: Task priority (1-10, lower is higher priority)
            
        Returns:
            Task ID
        """
        task_id = f"{task_type}_{discipline}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        task = Task(
            task_id=task_id,
            task_type=task_type,
            discipline=discipline,
            parameters=parameters,
            priority=priority,
            status=TaskStatus.PENDING,
            assigned_agent=None,
            created_time=datetime.now(),
            started_time=None,
            completed_time=None,
            result=None,
            error_message=None
        )
        
        with self.task_lock:
            self.task_queue.append(task)
            # Sort by priority (lower number = higher priority)
            self.task_queue.sort(key=lambda t: t.priority)
        
        self.logger.info(f"Added task {task_id} for discipline {discipline}")
        return task_id
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status
        
        Returns:
            System status dictionary
        """
        with self.agents_lock:
            agent_status = {}
            for agent_id, agent in self.agents.items():
                agent_status_info = agent.get_status()
                agent_status[agent_id] = {
                    'type': agent.agent_type,
                    'status': agent_status_info['status'],
                    'discipline': agent.discipline,
                    'current_task': agent_status_info['current_task'],
                    'last_heartbeat': agent_status_info['last_heartbeat'],
                    'error_count': agent_status_info['error_count'],
                    'tasks_completed': agent_status_info['performance_stats']['tasks_completed'],
                    'success_rate': agent_status_info['performance_stats']['success_rate']
                }
        
        with self.task_lock:
            task_counts = {
                'pending': len([t for t in self.task_queue if t.status == TaskStatus.PENDING]),
                'in_progress': len(self.active_tasks),
                'completed': len(self.completed_tasks)
            }
        
        return {
            'is_running': self.is_running,
            'agents': agent_status,
            'tasks': task_counts,
            'discipline_progress': self.discipline_progress.copy(),
            'system_metrics': self.system_metrics.copy(),
            'selected_disciplines': self.selected_disciplines
        }
    
    def get_discipline_progress(self, discipline: str) -> Dict[str, Any]:
        """Get progress for a specific discipline
        
        Args:
            discipline: Discipline name
            
        Returns:
            Discipline progress dictionary
        """
        return self.discipline_progress.get(discipline, {})
    
    def force_agent_restart(self, agent_id: str) -> bool:
        """Force restart of a specific agent
        
        Args:
            agent_id: ID of agent to restart
            
        Returns:
            True if restart was successful
        """
        try:
            with self.agents_lock:
                if agent_id not in self.agents:
                    self.logger.error(f"Agent {agent_id} not found")
                    return False
                
                agent = self.agents[agent_id]
                agent_type = agent.agent_type
                discipline = agent.discipline
                
                # Stop the agent
                self._stop_agent(agent_id)
                
                # Restart the agent
                new_agent_id = self._start_agent(agent_type, discipline)
                
                if new_agent_id:
                    self.logger.info(f"Agent {agent_id} restarted successfully as {new_agent_id}")
                    return True
                else:
                    self.logger.error(f"Failed to restart agent {agent_id}")
                    return False
                
        except Exception as e:
            self.logger.error(f"Error restarting agent {agent_id}: {e}")
            return False
    
    # Private methods
    
    def _initialize_agents(self) -> bool:
        """Initialize all required agents
        
        Returns:
            True if initialization was successful
        """
        try:
            # Clear existing agents
            self.agents.clear()
            
            # Initialize discovery agents (one per selected discipline)
            for discipline in self.selected_disciplines:
                agent_id = self._start_agent('discovery', discipline)
                if not agent_id:
                    self.logger.error(f"Failed to start discovery agent for {discipline}")
                    return False
            
            # Initialize retrieval agents (distributed across disciplines)
            retrieval_agents_per_discipline = max(1, 20 // len(self.selected_disciplines))
            for discipline in self.selected_disciplines:
                for i in range(retrieval_agents_per_discipline):
                    agent_id = self._start_agent('retrieval', discipline)
                    if not agent_id:
                        self.logger.warning(f"Failed to start retrieval agent {i} for {discipline}")
            
            # Initialize processing agents (shared across disciplines)
            processing_agents = min(15, len(self.selected_disciplines) * 2)
            for i in range(processing_agents):
                discipline = self.selected_disciplines[i % len(self.selected_disciplines)]
                agent_id = self._start_agent('processing', discipline)
                if not agent_id:
                    self.logger.warning(f"Failed to start processing agent {i}")
            
            # Initialize validation agents (shared)
            for i in range(min(5, len(self.selected_disciplines))):
                discipline = self.selected_disciplines[i % len(self.selected_disciplines)]
                agent_id = self._start_agent('validation', discipline)
                if not agent_id:
                    self.logger.warning(f"Failed to start validation agent {i}")
            
            self.logger.info(f"Initialized {len(self.agents)} agents")
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing agents: {e}")
            return False
    
    def _start_agent(self, agent_type: str, discipline: Optional[str] = None) -> Optional[str]:
        """Start a new agent
        
        Args:
            agent_type: Type of agent to start
            discipline: Optional discipline assignment
            
        Returns:
            Agent ID if successful, None otherwise
        """
        try:
            agent_id = f"{agent_type}_{discipline}_{datetime.now().strftime('%H%M%S_%f')}"
            
            # Get agent configuration
            agent_config = self.agent_configs.get(agent_type, {})
            agent_config.update({
                'data_directory': str(self.config_manager.data_dir),
                'max_errors': 3,
                'recovery_enabled': True
            })
            
            # Create actual agent instance based on type
            agent_instance = None
            if agent_type == 'discovery':
                agent_instance = DiscoveryAgent(
                    agent_id=agent_id,
                    discipline=discipline,
                    config=agent_config,
                    llm_integration=self.llm_integration,
                    config_manager=self.config_manager
                )
            elif agent_type == 'retrieval':
                agent_instance = RetrievalAgent(
                    agent_id=agent_id,
                    discipline=discipline,
                    config=agent_config,
                    llm_integration=self.llm_integration,
                    config_manager=self.config_manager
                )
            elif agent_type == 'processing':
                agent_instance = ProcessingAgent(
                    agent_id=agent_id,
                    discipline=discipline,
                    config=agent_config,
                    llm_integration=self.llm_integration,
                    config_manager=self.config_manager
                )
            elif agent_type == 'validation':
                agent_instance = ValidationAgent(
                    agent_id=agent_id,
                    discipline=discipline,
                    config=agent_config,
                    llm_integration=self.llm_integration,
                    config_manager=self.config_manager
                )
            else:
                raise ValueError(f"Unknown agent type: {agent_type}")
            
            if agent_instance:
                # Set orchestrator callback for communication
                agent_instance.set_orchestrator_callback(self._handle_agent_message)
                
                # Start the agent
                if agent_instance.start():
                    with self.agents_lock:
                        self.agents[agent_id] = agent_instance
                    
                    self.logger.info(f"Started {agent_type} agent {agent_id} for discipline {discipline}")
                    return agent_id
                else:
                    self.logger.error(f"Failed to start agent instance {agent_id}")
                    return None
            else:
                self.logger.error(f"Failed to create agent instance for type {agent_type}")
                return None
            
        except Exception as e:
            self.logger.error(f"Error starting {agent_type} agent: {e}")
            return None
    
    def _handle_agent_message(self, message):
        """Handle messages from agents
        
        Args:
            message: AgentMessage from an agent
        """
        try:
            if message.message_type == 'task_completed':
                self._handle_task_completion(message)
            elif message.message_type == 'task_failed':
                self._handle_task_failure(message)
            elif message.message_type == 'agent_status_update':
                self._handle_agent_status_update(message)
            else:
                self.logger.debug(f"Received message of type {message.message_type} from {message.sender_id}")
                
        except Exception as e:
            self.logger.error(f"Error handling agent message: {e}")
    
    def _handle_task_completion(self, message):
        """Handle task completion from agent"""
        try:
            task_id = message.content.get('task_id')
            result = message.content.get('result')
            
            if task_id in self.active_tasks:
                task = self.active_tasks[task_id]
                task.status = TaskStatus.COMPLETED
                task.completed_time = datetime.now()
                task.result = result
                
                # Move to completed tasks
                self.completed_tasks[task_id] = task
                del self.active_tasks[task_id]
                
                # Update agent status
                with self.agents_lock:
                    if message.sender_id in self.agents:
                        agent = self.agents[message.sender_id]
                        # Agent will update its own current_task in base class
                
                self.logger.info(f"Task {task_id} completed by agent {message.sender_id}")
                
        except Exception as e:
            self.logger.error(f"Error handling task completion: {e}")
    
    def _handle_task_failure(self, message):
        """Handle task failure from agent"""
        try:
            task_id = message.content.get('task_id')
            error = message.content.get('error')
            
            if task_id in self.active_tasks:
                task = self.active_tasks[task_id]
                task.status = TaskStatus.FAILED
                task.completed_time = datetime.now()
                task.error_message = error
                
                # Move to completed tasks (even failed ones)
                self.completed_tasks[task_id] = task
                del self.active_tasks[task_id]
                
                self.logger.warning(f"Task {task_id} failed in agent {message.sender_id}: {error}")
                
        except Exception as e:
            self.logger.error(f"Error handling task failure: {e}")
    
    def _handle_agent_status_update(self, message):
        """Handle status update from agent"""
        try:
            # Agents manage their own status, this is just for logging
            status = message.content.get('status')
            self.logger.debug(f"Agent {message.sender_id} status update: {status}")
            
        except Exception as e:
            self.logger.error(f"Error handling agent status update: {e}")
    
    def _stop_agent(self, agent_id: str):
        """Stop a specific agent
        
        Args:
            agent_id: ID of agent to stop
        """
        try:
            with self.agents_lock:
                if agent_id in self.agents:
                    agent = self.agents[agent_id]
                    agent.stop()
                    del self.agents[agent_id]
                    self.logger.info(f"Stopped agent {agent_id}")
                    
        except Exception as e:
            self.logger.error(f"Error stopping agent {agent_id}: {e}")
    
    def _stop_all_agents(self):
        """Stop all agents"""
        try:
            with self.agents_lock:
                for agent_id in list(self.agents.keys()):
                    self._stop_agent(agent_id)
                    
        except Exception as e:
            self.logger.error(f"Error stopping all agents: {e}")
    
    def _orchestrator_main_loop(self):
        """Main orchestrator loop running in separate thread"""
        self.logger.info("Orchestrator main loop started")
        
        while not self.stop_event.is_set() and self.is_running:
            try:
                # Update agent heartbeats
                self._update_agent_heartbeats()
                
                # Process task queue
                self._process_task_queue()
                
                # Update discipline progress
                self._update_discipline_progress()
                
                # Update system metrics
                self._update_system_metrics()
                
                # Check for failed agents and restart if needed
                self._check_agent_health()
                
                # Create periodic checkpoint
                if self._should_create_checkpoint():
                    self._create_periodic_checkpoint()
                
                # Sleep before next iteration
                time.sleep(5)  # 5 second polling interval
                
            except Exception as e:
                self.logger.error(f"Error in orchestrator main loop: {e}")
                time.sleep(10)  # Longer sleep on error
        
        self.logger.info("Orchestrator main loop ended")
    
    def _update_agent_heartbeats(self):
        """Update agent heartbeats and detect failed agents"""
        current_time = datetime.now()
        timeout_threshold = timedelta(minutes=5)  # 5 minute timeout
        
        with self.agents_lock:
            for agent_id, agent_info in self.agents.items():
                # Simulate heartbeat update (in real implementation, agents would report)
                if agent_info.status == AgentStatus.RUNNING:
                    agent_info.last_heartbeat = current_time
                
                # Check for timeout
                time_since_heartbeat = current_time - agent_info.last_heartbeat
                if time_since_heartbeat > timeout_threshold and agent_info.status == AgentStatus.RUNNING:
                    self.logger.warning(f"Agent {agent_id} timed out, marking as error")
                    agent_info.status = AgentStatus.ERROR
                    agent_info.error_count += 1
    
    def _process_task_queue(self):
        """Process pending tasks and assign to available agents"""
        with self.task_lock:
            if not self.task_queue:
                return
            
            # Get available agents
            available_agents = []
            with self.agents_lock:
                for agent_id, agent in self.agents.items():
                    agent_status = agent.get_status()
                    if (agent_status['status'] == 'idle' and 
                        agent_status['current_task'] is None):
                        available_agents.append((agent_id, agent))
            
            if not available_agents:
                return
            
            # Assign tasks to available agents
            tasks_to_remove = []
            
            for i, task in enumerate(self.task_queue):
                if not available_agents:
                    break
                
                # Find best agent for this task
                best_agent = self._find_best_agent_for_task(task, available_agents)
                
                if best_agent:
                    agent_id, agent = best_agent
                    
                    # Assign task to agent
                    task.assigned_agent = agent_id
                    task.status = TaskStatus.IN_PROGRESS
                    task.started_time = datetime.now()
                    
                    # Convert Task to agent task format
                    agent_task = {
                        'task_id': task.task_id,
                        'type': task.task_type,
                        'discipline': task.discipline,
                        'parameters': task.parameters,
                        'priority': task.priority
                    }
                    
                    # Assign task to agent
                    agent.assign_task(agent_task)
                    
                    # Move task to active tasks
                    self.active_tasks[task.task_id] = task
                    tasks_to_remove.append(i)
                    
                    # Remove agent from available list
                    available_agents.remove(best_agent)
                    
                    self.logger.info(f"Assigned task {task.task_id} to agent {agent_id}")
            
            # Remove assigned tasks from queue
            for i in reversed(tasks_to_remove):
                self.task_queue.pop(i)
    
    def _find_best_agent_for_task(self, task: Task, available_agents: List[Tuple[str, BaseAgent]]) -> Optional[Tuple[str, BaseAgent]]:
        """Find the best agent for a specific task
        
        Args:
            task: Task to assign
            available_agents: List of available agents
            
        Returns:
            Best agent tuple or None
        """
        # Filter agents by type compatibility
        compatible_agents = []
        
        for agent_id, agent in available_agents:
            # Check if agent type is compatible with task type
            if self._is_agent_compatible_with_task(agent, task):
                compatible_agents.append((agent_id, agent))
        
        if not compatible_agents:
            return None
        
        # Find agent with best performance for this discipline
        best_agent = None
        best_score = -1
        
        for agent_id, agent in compatible_agents:
            score = self._calculate_agent_score(agent, task)
            if score > best_score:
                best_score = score
                best_agent = (agent_id, agent)
        
        return best_agent
    
    def _is_agent_compatible_with_task(self, agent: BaseAgent, task: Task) -> bool:
        """Check if agent is compatible with task
        
        Args:
            agent: Agent instance
            task: Task to check
            
        Returns:
            True if compatible
        """
        # Agent type compatibility
        type_compatibility = {
            'discovery': ['discovery'],
            'retrieval': ['retrieval', 'processing'],
            'processing': ['processing', 'validation'],
            'validation': ['validation']
        }
        
        return task.task_type in type_compatibility.get(agent.agent_type, [])
    
    def _calculate_agent_score(self, agent: BaseAgent, task: Task) -> float:
        """Calculate agent suitability score for task
        
        Args:
            agent: Agent instance
            task: Task to score
            
        Returns:
            Suitability score (higher is better)
        """
        score = 1.0
        
        # Discipline affinity
        if agent.discipline == task.discipline:
            score += 2.0
        
        # Performance metrics
        agent_status = agent.get_status()
        success_rate = agent_status['performance_stats'].get('success_rate', 1.0)
        score += success_rate
        
        # Error penalty
        error_count = agent_status.get('error_count', 0)
        if error_count > 0:
            score -= error_count * 0.1
        
        return max(score, 0.1)  # Minimum score
    
    def _update_discipline_progress(self):
        """Update progress tracking for all disciplines"""
        for discipline in self.selected_disciplines:
            progress = self.discipline_progress[discipline]
            
            # Count active agents for this discipline
            active_agents = 0
            with self.agents_lock:
                for agent in self.agents.values():
                    agent_status = agent.get_status()
                    if (agent.discipline == discipline and 
                        agent_status['status'] in ['idle', 'running']):
                        active_agents += 1
            
            progress['active_agents'] = active_agents
            progress['last_update'] = datetime.now()
            
            # Simulate progress increase
            if active_agents > 0:
                progress['progress_percentage'] = min(100, progress['progress_percentage'] + 0.5)
                
                if progress['progress_percentage'] > 0:
                    progress['status'] = 'in_progress'
                if progress['progress_percentage'] >= 100:
                    progress['status'] = 'completed'
    
    def _update_system_metrics(self):
        """Update overall system metrics"""
        current_time = datetime.now()
        
        # Count active agents
        active_agents = 0
        with self.agents_lock:
            for agent in self.agents.values():
                agent_status = agent.get_status()
                if agent_status['status'] in ['idle', 'running']:
                    active_agents += 1
        
        self.system_metrics.update({
            'total_agents_active': active_agents,
            'last_update': current_time
        })
        
        # Calculate efficiency (simulated)
        if active_agents > 0:
            efficiency = min(1.0, active_agents / (len(self.selected_disciplines) * 2))
            self.system_metrics['system_efficiency'] = efficiency
    
    def _check_agent_health(self):
        """Check agent health and restart failed agents if needed"""
        agents_to_restart = []
        
        with self.agents_lock:
            for agent_id, agent in self.agents.items():
                agent_status = agent.get_status()
                if (agent_status['status'] == 'error' and 
                    agent_status['error_count'] < 3):  # Max 3 restart attempts
                    agents_to_restart.append(agent_id)
        
        # Restart failed agents
        for agent_id in agents_to_restart:
            self.force_agent_restart(agent_id)
    
    def _should_create_checkpoint(self) -> bool:
        """Check if a periodic checkpoint should be created"""
        checkpoint_interval = timedelta(minutes=15)  # Every 15 minutes
        time_since_last = datetime.now() - self.recovery_manager.last_checkpoint_time
        return time_since_last > checkpoint_interval
    
    def _create_periodic_checkpoint(self):
        """Create a periodic system checkpoint"""
        try:
            checkpoint_data = {
                'system_status': self.get_system_status(),
                'task_queue_size': len(self.task_queue),
                'active_task_count': len(self.active_tasks),
                'completed_task_count': len(self.completed_tasks)
            }
            
            self.recovery_manager.create_checkpoint('periodic_orchestrator', checkpoint_data)
            
        except Exception as e:
            self.logger.error(f"Error creating periodic checkpoint: {e}")
    
    def get_agent_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all agents"""
        agent_status = {}
        
        with self.agents_lock:
            for agent_id, agent in self.agents.items():
                try:
                    # Get real agent status
                    status = agent.status if hasattr(agent, 'status') else AgentStatus.IDLE
                    agent_type = agent.agent_type if hasattr(agent, 'agent_type') else 'unknown'
                    
                    agent_status[agent_id] = {
                        'id': agent_id,
                        'name': f"{agent_type.title()} Agent {agent_id}",
                        'type': agent_type,
                        'status': status.value if hasattr(status, 'value') else str(status),
                        'last_activity': getattr(agent, 'last_activity', 'Unknown'),
                        'standards_found': getattr(agent, 'standards_found', 0),
                        'success_rate': getattr(agent, 'success_rate', 0.0)
                    }
                except Exception as e:
                    self.logger.error(f"Error getting status for agent {agent_id}: {e}")
                    agent_status[agent_id] = {
                        'id': agent_id,
                        'name': f"Agent {agent_id}",
                        'type': 'unknown',
                        'status': 'error',
                        'last_activity': 'Unknown',
                        'standards_found': 0,
                        'success_rate': 0.0
                    }
        
        return agent_status
    
    def restart_agent(self, agent_id: str) -> bool:
        """Restart a specific agent"""
        try:
            with self.agents_lock:
                if agent_id not in self.agents:
                    self.logger.error(f"Agent {agent_id} not found")
                    return False
                
                agent = self.agents[agent_id]
                
                # Stop the agent
                if hasattr(agent, 'stop'):
                    agent.stop()
                
                # Restart the agent
                if hasattr(agent, 'start'):
                    agent.start()
                    
                self.logger.info(f"Restarted agent {agent_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Error restarting agent {agent_id}: {e}")
            return False
    
    def __del__(self):
        """Cleanup when orchestrator is destroyed"""
        if self.is_running:
            self.stop_system()