#!/usr/bin/env python3
"""
Performance Monitoring and Optimization System for International Standards Retrieval

Comprehensive monitoring system that tracks performance across all system components,
analyzes bottlenecks, and provides optimization recommendations for the 19 OpenAlex
disciplines processing pipeline.

Author: Autonomous AI Development System
"""

import time
import psutil
import threading
import logging
from typing import Dict, List, Any, Optional, Tuple, Callable
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import statistics
import json
import queue
from collections import defaultdict, deque

# Add parent directory to path for imports
import sys
sys.path.append(str(Path(__file__).parent.parent))

from data.database_manager import DatabaseManager

class PerformanceMetricType(Enum):
    """Types of performance metrics"""
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"
    DATABASE_PERFORMANCE = "database_performance"
    AGENT_EFFICIENCY = "agent_efficiency"
    LLM_PERFORMANCE = "llm_performance"
    QUALITY_SCORE = "quality_score"
    ERROR_RATE = "error_rate"
    RESOURCE_UTILIZATION = "resource_utilization"

class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

@dataclass
class PerformanceMetric:
    """Individual performance metric"""
    metric_type: PerformanceMetricType
    value: float
    unit: str
    timestamp: datetime
    component: str
    discipline_id: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class PerformanceAlert:
    """Performance alert"""
    alert_id: str
    severity: AlertSeverity
    metric_type: PerformanceMetricType
    component: str
    message: str
    current_value: float
    threshold_value: float
    timestamp: datetime
    resolved: bool = False
    resolution_timestamp: Optional[datetime] = None

@dataclass
class OptimizationRecommendation:
    """Optimization recommendation"""
    recommendation_id: str
    component: str
    category: str
    priority: str  # high, medium, low
    description: str
    expected_improvement: str
    implementation_effort: str
    generated_timestamp: datetime
    applied: bool = False

class PerformanceMonitor:
    """Comprehensive performance monitoring system"""
    
    def __init__(self, database_manager: DatabaseManager, 
                 monitoring_interval: int = 30):
        """Initialize performance monitor
        
        Args:
            database_manager: Database manager instance
            monitoring_interval: Monitoring interval in seconds
        """
        self.db = database_manager
        self.monitoring_interval = monitoring_interval
        self.logger = logging.getLogger(__name__)
        
        # Monitoring state
        self.monitoring_active = False
        self.monitoring_thread = None
        
        # Performance data storage
        self.metrics_buffer = deque(maxlen=10000)  # Keep last 10k metrics
        self.metrics_by_component = defaultdict(deque)
        self.alerts = []
        self.recommendations = []
        
        # Performance thresholds
        self.thresholds = self._initialize_performance_thresholds()
        
        # Component trackers
        self.component_trackers = {}
        self.system_baseline = None
        
        # Optimization tracking
        self.optimization_history = []
        
        # Statistics
        self.monitoring_stats = {
            'total_metrics_collected': 0,
            'alerts_generated': 0,
            'recommendations_made': 0,
            'monitoring_uptime': 0.0,
            'last_optimization': None
        }
        
        self.logger.info("Performance monitor initialized")
    
    def _initialize_performance_thresholds(self) -> Dict[str, Dict[str, Any]]:
        """Initialize performance thresholds for different metrics"""
        return {
            'response_time': {
                'warning': 5.0,  # seconds
                'critical': 10.0,
                'emergency': 30.0
            },
            'memory_usage': {
                'warning': 80.0,  # percentage
                'critical': 90.0,
                'emergency': 95.0
            },
            'cpu_usage': {
                'warning': 80.0,  # percentage
                'critical': 90.0,
                'emergency': 95.0
            },
            'database_query_time': {
                'warning': 2.0,  # seconds
                'critical': 5.0,
                'emergency': 10.0
            },
            'agent_efficiency': {
                'warning': 0.7,  # ratio (lower is worse)
                'critical': 0.5,
                'emergency': 0.3
            },
            'error_rate': {
                'warning': 0.05,  # 5%
                'critical': 0.10,  # 10%
                'emergency': 0.20   # 20%
            },
            'quality_score': {
                'warning': 0.7,  # average quality (lower is worse)
                'critical': 0.5,
                'emergency': 0.3
            }
        }
    
    def start_monitoring(self):
        """Start continuous performance monitoring"""
        if self.monitoring_active:
            self.logger.warning("Monitoring already active")
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self.monitoring_thread.start()
        
        self.logger.info("Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        self.logger.info("Performance monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        monitoring_start = datetime.now()
        
        while self.monitoring_active:
            try:
                loop_start = time.time()
                
                # Collect system metrics
                self._collect_system_metrics()
                
                # Collect database metrics
                self._collect_database_metrics()
                
                # Collect component-specific metrics
                self._collect_component_metrics()
                
                # Check for alerts
                self._check_alerts()
                
                # Generate recommendations
                self._generate_recommendations()
                
                # Update monitoring statistics
                self.monitoring_stats['monitoring_uptime'] = (
                    datetime.now() - monitoring_start
                ).total_seconds()
                
                # Sleep for remaining interval time
                elapsed = time.time() - loop_start
                sleep_time = max(0, self.monitoring_interval - elapsed)
                time.sleep(sleep_time)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5)  # Brief pause before retry
    
    def _collect_system_metrics(self):
        """Collect system-level performance metrics"""
        timestamp = datetime.now()
        
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        self._add_metric(PerformanceMetric(
            metric_type=PerformanceMetricType.CPU_USAGE,
            value=cpu_percent,
            unit="percent",
            timestamp=timestamp,
            component="system"
        ))
        
        # Memory usage
        memory = psutil.virtual_memory()
        self._add_metric(PerformanceMetric(
            metric_type=PerformanceMetricType.MEMORY_USAGE,
            value=memory.percent,
            unit="percent",
            timestamp=timestamp,
            component="system",
            metadata={
                'total_gb': round(memory.total / (1024**3), 2),
                'available_gb': round(memory.available / (1024**3), 2),
                'used_gb': round(memory.used / (1024**3), 2)
            }
        ))
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        self._add_metric(PerformanceMetric(
            metric_type=PerformanceMetricType.RESOURCE_UTILIZATION,
            value=disk_percent,
            unit="percent",
            timestamp=timestamp,
            component="disk",
            metadata={
                'total_gb': round(disk.total / (1024**3), 2),
                'used_gb': round(disk.used / (1024**3), 2),
                'free_gb': round(disk.free / (1024**3), 2)
            }
        ))
        
        # Network I/O if available
        try:
            network = psutil.net_io_counters()
            self._add_metric(PerformanceMetric(
                metric_type=PerformanceMetricType.RESOURCE_UTILIZATION,
                value=network.bytes_sent + network.bytes_recv,
                unit="bytes",
                timestamp=timestamp,
                component="network",
                metadata={
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                }
            ))
        except Exception as e:
            self.logger.debug(f"Could not collect network metrics: {e}")
    
    def _collect_database_metrics(self):
        """Collect database performance metrics"""
        timestamp = datetime.now()
        
        try:
            # Test query performance
            start_time = time.time()
            result = self.db.execute_query("SELECT COUNT(*) FROM disciplines")
            query_time = time.time() - start_time
            
            self._add_metric(PerformanceMetric(
                metric_type=PerformanceMetricType.DATABASE_PERFORMANCE,
                value=query_time,
                unit="seconds",
                timestamp=timestamp,
                component="database",
                metadata={'query_type': 'count_disciplines'}
            ))
            
            # Get database statistics if available
            try:
                db_stats = self.db.get_system_performance_stats()
                if db_stats:
                    # Total standards processed
                    total_standards = db_stats.get('total_standards', 0)
                    self._add_metric(PerformanceMetric(
                        metric_type=PerformanceMetricType.THROUGHPUT,
                        value=total_standards,
                        unit="records",
                        timestamp=timestamp,
                        component="database",
                        metadata={'metric': 'total_standards'}
                    ))
                    
                    # Average quality score
                    avg_quality = db_stats.get('avg_quality_score', 0)
                    if avg_quality > 0:
                        self._add_metric(PerformanceMetric(
                            metric_type=PerformanceMetricType.QUALITY_SCORE,
                            value=avg_quality,
                            unit="score",
                            timestamp=timestamp,
                            component="database",
                            metadata={'metric': 'avg_quality_score'}
                        ))
            
            except Exception as e:
                self.logger.debug(f"Could not collect extended database stats: {e}")
                
        except Exception as e:
            self.logger.error(f"Error collecting database metrics: {e}")
    
    def _collect_component_metrics(self):
        """Collect metrics from registered components"""
        for component_name, tracker in self.component_trackers.items():
            try:
                metrics = tracker.get_current_metrics()
                for metric in metrics:
                    self._add_metric(metric)
            except Exception as e:
                self.logger.error(f"Error collecting metrics from {component_name}: {e}")
    
    def _add_metric(self, metric: PerformanceMetric):
        """Add metric to storage and update statistics"""
        self.metrics_buffer.append(metric)
        self.metrics_by_component[metric.component].append(metric)
        self.monitoring_stats['total_metrics_collected'] += 1
        
        # Keep component buffers manageable
        if len(self.metrics_by_component[metric.component]) > 1000:
            self.metrics_by_component[metric.component] = deque(
                list(self.metrics_by_component[metric.component])[-500:],
                maxlen=1000
            )
    
    def _check_alerts(self):
        """Check metrics against thresholds and generate alerts"""
        current_time = datetime.now()
        
        # Check recent metrics for threshold violations
        recent_metrics = [m for m in self.metrics_buffer 
                         if (current_time - m.timestamp).total_seconds() < 300]  # Last 5 minutes
        
        for metric in recent_metrics:
            self._check_metric_thresholds(metric)
    
    def _check_metric_thresholds(self, metric: PerformanceMetric):
        """Check individual metric against thresholds"""
        threshold_key = self._get_threshold_key(metric.metric_type)
        if threshold_key not in self.thresholds:
            return
        
        thresholds = self.thresholds[threshold_key]
        value = metric.value
        
        # Determine severity
        severity = None
        threshold_value = None
        
        if value >= thresholds.get('emergency', float('inf')):
            severity = AlertSeverity.EMERGENCY
            threshold_value = thresholds['emergency']
        elif value >= thresholds.get('critical', float('inf')):
            severity = AlertSeverity.CRITICAL
            threshold_value = thresholds['critical']
        elif value >= thresholds.get('warning', float('inf')):
            severity = AlertSeverity.WARNING
            threshold_value = thresholds['warning']
        
        # For metrics where lower is worse (like efficiency, quality)
        if metric.metric_type in [PerformanceMetricType.AGENT_EFFICIENCY, 
                                 PerformanceMetricType.QUALITY_SCORE]:
            if value <= thresholds.get('emergency', 0):
                severity = AlertSeverity.EMERGENCY
                threshold_value = thresholds['emergency']
            elif value <= thresholds.get('critical', 0):
                severity = AlertSeverity.CRITICAL
                threshold_value = thresholds['critical']
            elif value <= thresholds.get('warning', 0):
                severity = AlertSeverity.WARNING
                threshold_value = thresholds['warning']
        
        if severity:
            self._create_alert(metric, severity, threshold_value)
    
    def _get_threshold_key(self, metric_type: PerformanceMetricType) -> str:
        """Get threshold key for metric type"""
        mapping = {
            PerformanceMetricType.RESPONSE_TIME: 'response_time',
            PerformanceMetricType.MEMORY_USAGE: 'memory_usage',
            PerformanceMetricType.CPU_USAGE: 'cpu_usage',
            PerformanceMetricType.DATABASE_PERFORMANCE: 'database_query_time',
            PerformanceMetricType.AGENT_EFFICIENCY: 'agent_efficiency',
            PerformanceMetricType.ERROR_RATE: 'error_rate',
            PerformanceMetricType.QUALITY_SCORE: 'quality_score'
        }
        return mapping.get(metric_type, 'default')
    
    def _create_alert(self, metric: PerformanceMetric, severity: AlertSeverity, 
                     threshold_value: float):
        """Create performance alert"""
        # Check if similar alert already exists and is recent
        recent_alerts = [a for a in self.alerts 
                        if not a.resolved and 
                        a.component == metric.component and 
                        a.metric_type == metric.metric_type and
                        (datetime.now() - a.timestamp).total_seconds() < 300]
        
        if recent_alerts:
            return  # Don't create duplicate alerts
        
        alert_id = f"{metric.component}_{metric.metric_type.value}_{int(datetime.now().timestamp())}"
        
        message = self._generate_alert_message(metric, severity, threshold_value)
        
        alert = PerformanceAlert(
            alert_id=alert_id,
            severity=severity,
            metric_type=metric.metric_type,
            component=metric.component,
            message=message,
            current_value=metric.value,
            threshold_value=threshold_value,
            timestamp=datetime.now()
        )
        
        self.alerts.append(alert)
        self.monitoring_stats['alerts_generated'] += 1
        
        self.logger.warning(f"Performance alert: {alert.message}")
    
    def _generate_alert_message(self, metric: PerformanceMetric, 
                               severity: AlertSeverity, threshold_value: float) -> str:
        """Generate human-readable alert message"""
        component = metric.component
        metric_name = metric.metric_type.value.replace('_', ' ').title()
        current = metric.value
        threshold = threshold_value
        unit = metric.unit
        
        if metric.metric_type in [PerformanceMetricType.AGENT_EFFICIENCY, 
                                 PerformanceMetricType.QUALITY_SCORE]:
            comparison = "below"
        else:
            comparison = "above"
        
        return (f"{severity.value.upper()}: {component} {metric_name} is {comparison} threshold. "
                f"Current: {current:.2f} {unit}, Threshold: {threshold:.2f} {unit}")
    
    def _generate_recommendations(self):
        """Generate optimization recommendations based on performance data"""
        current_time = datetime.now()
        
        # Only generate recommendations every 10 minutes
        if (self.monitoring_stats.get('last_optimization') and 
            (current_time - self.monitoring_stats['last_optimization']).total_seconds() < 600):
            return
        
        # Analyze performance trends
        recommendations = []
        
        # Check for consistent high resource usage
        recommendations.extend(self._analyze_resource_usage())
        
        # Check for database performance issues
        recommendations.extend(self._analyze_database_performance())
        
        # Check for component-specific optimizations
        recommendations.extend(self._analyze_component_performance())
        
        # Add new recommendations
        for rec in recommendations:
            if not any(existing.description == rec.description for existing in self.recommendations):
                self.recommendations.append(rec)
                self.monitoring_stats['recommendations_made'] += 1
                self.logger.info(f"New optimization recommendation: {rec.description}")
        
        self.monitoring_stats['last_optimization'] = current_time
    
    def _analyze_resource_usage(self) -> List[OptimizationRecommendation]:
        """Analyze system resource usage patterns"""
        recommendations = []
        current_time = datetime.now()
        
        # Get recent system metrics
        recent_metrics = [m for m in self.metrics_buffer 
                         if (current_time - m.timestamp).total_seconds() < 1800 and  # Last 30 minutes
                         m.component == "system"]
        
        if not recent_metrics:
            return recommendations
        
        # Analyze CPU usage
        cpu_metrics = [m for m in recent_metrics if m.metric_type == PerformanceMetricType.CPU_USAGE]
        if cpu_metrics:
            avg_cpu = statistics.mean(m.value for m in cpu_metrics)
            if avg_cpu > 85:
                recommendations.append(OptimizationRecommendation(
                    recommendation_id=f"cpu_optimization_{int(current_time.timestamp())}",
                    component="system",
                    category="resource_optimization",
                    priority="high",
                    description="High CPU usage detected. Consider implementing parallel processing limits or optimizing compute-intensive operations.",
                    expected_improvement="20-40% CPU reduction",
                    implementation_effort="medium",
                    generated_timestamp=current_time
                ))
        
        # Analyze memory usage
        memory_metrics = [m for m in recent_metrics if m.metric_type == PerformanceMetricType.MEMORY_USAGE]
        if memory_metrics:
            avg_memory = statistics.mean(m.value for m in memory_metrics)
            if avg_memory > 85:
                recommendations.append(OptimizationRecommendation(
                    recommendation_id=f"memory_optimization_{int(current_time.timestamp())}",
                    component="system",
                    category="resource_optimization",
                    priority="high",
                    description="High memory usage detected. Consider implementing data streaming, caching optimization, or memory cleanup routines.",
                    expected_improvement="15-30% memory reduction",
                    implementation_effort="medium",
                    generated_timestamp=current_time
                ))
        
        return recommendations
    
    def _analyze_database_performance(self) -> List[OptimizationRecommendation]:
        """Analyze database performance patterns"""
        recommendations = []
        current_time = datetime.now()
        
        # Get recent database metrics
        db_metrics = [m for m in self.metrics_buffer 
                     if (current_time - m.timestamp).total_seconds() < 1800 and  # Last 30 minutes
                     m.component == "database" and
                     m.metric_type == PerformanceMetricType.DATABASE_PERFORMANCE]
        
        if not db_metrics:
            return recommendations
        
        # Analyze query performance
        avg_query_time = statistics.mean(m.value for m in db_metrics)
        if avg_query_time > 2.0:
            recommendations.append(OptimizationRecommendation(
                recommendation_id=f"db_query_optimization_{int(current_time.timestamp())}",
                component="database",
                category="query_optimization",
                priority="medium",
                description="Slow database queries detected. Consider adding indexes, optimizing queries, or implementing query caching.",
                expected_improvement="30-60% query time reduction",
                implementation_effort="low",
                generated_timestamp=current_time
            ))
        
        # Check for high query frequency
        query_frequency = len(db_metrics) / 30  # queries per minute
        if query_frequency > 100:
            recommendations.append(OptimizationRecommendation(
                recommendation_id=f"db_connection_optimization_{int(current_time.timestamp())}",
                component="database",
                category="connection_optimization",
                priority="medium",
                description="High database query frequency detected. Consider implementing connection pooling or batch operations.",
                expected_improvement="25-50% database load reduction",
                implementation_effort="medium",
                generated_timestamp=current_time
            ))
        
        return recommendations
    
    def _analyze_component_performance(self) -> List[OptimizationRecommendation]:
        """Analyze component-specific performance"""
        recommendations = []
        current_time = datetime.now()
        
        # Analyze component efficiency
        for component, metrics in self.metrics_by_component.items():
            if component in ["system", "database"]:
                continue
            
            recent_metrics = [m for m in metrics 
                             if (current_time - m.timestamp).total_seconds() < 1800]
            
            if not recent_metrics:
                continue
            
            # Look for efficiency issues
            efficiency_metrics = [m for m in recent_metrics 
                                if m.metric_type == PerformanceMetricType.AGENT_EFFICIENCY]
            
            if efficiency_metrics:
                avg_efficiency = statistics.mean(m.value for m in efficiency_metrics)
                if avg_efficiency < 0.7:
                    recommendations.append(OptimizationRecommendation(
                        recommendation_id=f"{component}_efficiency_{int(current_time.timestamp())}",
                        component=component,
                        category="efficiency_optimization",
                        priority="high",
                        description=f"Low efficiency detected in {component}. Consider optimizing algorithms, reducing processing overhead, or implementing caching.",
                        expected_improvement="20-40% efficiency improvement",
                        implementation_effort="medium",
                        generated_timestamp=current_time
                    ))
        
        return recommendations
    
    def register_component_tracker(self, component_name: str, tracker: 'ComponentTracker'):
        """Register a component performance tracker"""
        self.component_trackers[component_name] = tracker
        self.logger.info(f"Registered performance tracker for {component_name}")
    
    def get_performance_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance summary for specified time period"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_metrics = [m for m in self.metrics_buffer if m.timestamp >= cutoff_time]
        
        if not recent_metrics:
            return {'message': 'No metrics available for the specified period'}
        
        # Group metrics by type and component
        metrics_by_type = defaultdict(list)
        metrics_by_component = defaultdict(list)
        
        for metric in recent_metrics:
            metrics_by_type[metric.metric_type].append(metric)
            metrics_by_component[metric.component].append(metric)
        
        # Calculate summaries
        type_summaries = {}
        for metric_type, metrics in metrics_by_type.items():
            values = [m.value for m in metrics]
            type_summaries[metric_type.value] = {
                'count': len(values),
                'average': statistics.mean(values),
                'min': min(values),
                'max': max(values),
                'std_dev': statistics.stdev(values) if len(values) > 1 else 0
            }
        
        component_summaries = {}
        for component, metrics in metrics_by_component.items():
            values = [m.value for m in metrics]
            component_summaries[component] = {
                'count': len(values),
                'metric_types': len(set(m.metric_type for m in metrics))
            }
        
        # Recent alerts
        recent_alerts = [a for a in self.alerts if a.timestamp >= cutoff_time]
        alert_summary = {
            'total': len(recent_alerts),
            'by_severity': {
                severity.value: len([a for a in recent_alerts if a.severity == severity])
                for severity in AlertSeverity
            }
        }
        
        return {
            'period_hours': hours,
            'total_metrics': len(recent_metrics),
            'metrics_by_type': type_summaries,
            'metrics_by_component': component_summaries,
            'alerts': alert_summary,
            'active_recommendations': len([r for r in self.recommendations if not r.applied]),
            'monitoring_stats': self.monitoring_stats
        }
    
    def get_optimization_recommendations(self, priority: str = None) -> List[Dict[str, Any]]:
        """Get current optimization recommendations"""
        recommendations = self.recommendations
        
        if priority:
            recommendations = [r for r in recommendations if r.priority == priority]
        
        return [asdict(r) for r in recommendations if not r.applied]
    
    def apply_recommendation(self, recommendation_id: str) -> bool:
        """Mark recommendation as applied"""
        for rec in self.recommendations:
            if rec.recommendation_id == recommendation_id:
                rec.applied = True
                self.optimization_history.append({
                    'recommendation_id': recommendation_id,
                    'applied_timestamp': datetime.now(),
                    'description': rec.description
                })
                self.logger.info(f"Applied optimization recommendation: {rec.description}")
                return True
        
        return False
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Mark alert as resolved"""
        for alert in self.alerts:
            if alert.alert_id == alert_id and not alert.resolved:
                alert.resolved = True
                alert.resolution_timestamp = datetime.now()
                self.logger.info(f"Resolved alert: {alert.message}")
                return True
        
        return False
    
    def get_system_health_score(self) -> Dict[str, Any]:
        """Calculate overall system health score"""
        current_time = datetime.now()
        recent_metrics = [m for m in self.metrics_buffer 
                         if (current_time - m.timestamp).total_seconds() < 300]  # Last 5 minutes
        
        if not recent_metrics:
            return {'health_score': 0.5, 'status': 'unknown', 'message': 'Insufficient data'}
        
        # Calculate component scores
        component_scores = {}
        
        for component in set(m.component for m in recent_metrics):
            component_metrics = [m for m in recent_metrics if m.component == component]
            scores = []
            
            for metric in component_metrics:
                # Normalize metric to 0-1 scale based on thresholds
                threshold_key = self._get_threshold_key(metric.metric_type)
                if threshold_key in self.thresholds:
                    thresholds = self.thresholds[threshold_key]
                    warning_threshold = thresholds.get('warning', 80)
                    
                    if metric.metric_type in [PerformanceMetricType.AGENT_EFFICIENCY, 
                                             PerformanceMetricType.QUALITY_SCORE]:
                        # Higher is better
                        score = min(1.0, metric.value / warning_threshold)
                    else:
                        # Lower is better
                        score = max(0.0, 1.0 - (metric.value / warning_threshold))
                    
                    scores.append(score)
            
            if scores:
                component_scores[component] = statistics.mean(scores)
        
        # Overall health score
        if component_scores:
            overall_score = statistics.mean(component_scores.values())
        else:
            overall_score = 0.5
        
        # Determine status
        if overall_score >= 0.8:
            status = 'excellent'
        elif overall_score >= 0.6:
            status = 'good'
        elif overall_score >= 0.4:
            status = 'fair'
        elif overall_score >= 0.2:
            status = 'poor'
        else:
            status = 'critical'
        
        # Recent alerts impact
        recent_alerts = [a for a in self.alerts 
                        if not a.resolved and 
                        (current_time - a.timestamp).total_seconds() < 300]
        
        critical_alerts = len([a for a in recent_alerts 
                              if a.severity in [AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY]])
        
        if critical_alerts > 0:
            overall_score *= 0.7  # Reduce score for critical alerts
            status = 'degraded'
        
        return {
            'health_score': round(overall_score, 3),
            'status': status,
            'component_scores': component_scores,
            'recent_alerts': len(recent_alerts),
            'critical_alerts': critical_alerts,
            'timestamp': current_time.isoformat()
        }

class ComponentTracker:
    """Base class for component performance tracking"""
    
    def __init__(self, component_name: str):
        self.component_name = component_name
        self.metrics_queue = queue.Queue()
        
    def record_metric(self, metric_type: PerformanceMetricType, 
                     value: float, unit: str, metadata: Dict[str, Any] = None):
        """Record a performance metric"""
        metric = PerformanceMetric(
            metric_type=metric_type,
            value=value,
            unit=unit,
            timestamp=datetime.now(),
            component=self.component_name,
            metadata=metadata
        )
        self.metrics_queue.put(metric)
    
    def get_current_metrics(self) -> List[PerformanceMetric]:
        """Get current metrics from queue"""
        metrics = []
        while not self.metrics_queue.empty():
            try:
                metrics.append(self.metrics_queue.get_nowait())
            except queue.Empty:
                break
        return metrics

# Factory function for easy initialization
def create_performance_monitor(database_manager: DatabaseManager, 
                              monitoring_interval: int = 30) -> PerformanceMonitor:
    """Create and configure performance monitor
    
    Args:
        database_manager: Database manager instance
        monitoring_interval: Monitoring interval in seconds
        
    Returns:
        Configured PerformanceMonitor instance
    """
    return PerformanceMonitor(database_manager, monitoring_interval)