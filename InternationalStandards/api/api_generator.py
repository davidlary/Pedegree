#!/usr/bin/env python3
"""
Automated API Generator for International Standards Retrieval System

Generates RESTful APIs for programmatic access to educational standards data
organized by 19 OpenAlex disciplines. Provides automatic endpoint creation,
documentation generation, and external integration capabilities.

Author: Autonomous AI Development System
"""

import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
import re
import hashlib

# Web framework imports
try:
    from flask import Flask, jsonify, request, abort, make_response
    from flask_cors import CORS
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False

try:
    from fastapi import FastAPI, HTTPException, Depends, Query
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    import uvicorn
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

# Add parent directory to path for imports
import sys
sys.path.append(str(Path(__file__).parent.parent))

from data.database_manager import DatabaseManager, DatabaseConfig

@dataclass
class APIEndpoint:
    """API endpoint configuration"""
    path: str
    method: str = "GET"
    description: str = ""
    parameters: List[Dict[str, Any]] = None
    response_format: str = "json"
    cache_duration: int = 3600
    rate_limit: str = "1000/hour"
    authentication_required: bool = False
    discipline_filter: Optional[List[int]] = None

@dataclass
class APIResponse:
    """Standardized API response structure"""
    success: bool
    data: Any = None
    message: str = ""
    timestamp: str = ""
    meta: Optional[Dict[str, Any]] = None
    errors: Optional[List[str]] = None

class APIGenerator:
    """Automated API generator for standards data"""
    
    def __init__(self, database_manager: DatabaseManager, 
                 framework: str = "flask", host: str = "0.0.0.0", port: int = 5000):
        """Initialize API generator
        
        Args:
            database_manager: Database manager instance
            framework: Web framework to use ('flask' or 'fastapi')
            host: API host address
            port: API port number
        """
        self.db = database_manager
        self.framework = framework
        self.host = host
        self.port = port
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # API configuration
        self.api_config = {
            'title': 'International Standards Retrieval API',
            'version': '1.0.0',
            'description': 'RESTful API for educational standards data across 19 OpenAlex disciplines',
            'base_url': f'http://{host}:{port}',
            'documentation_url': f'http://{host}:{port}/docs'
        }
        
        # Initialize web framework
        self.app = None
        self.limiter = None
        self._initialize_framework()
        
        # Generate standard endpoints
        self.endpoints = self._generate_standard_endpoints()
        self._register_endpoints()
        
        # API statistics
        self.api_stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'avg_response_time': 0.0,
            'endpoints_registered': len(self.endpoints)
        }
        
        self.logger.info(f"API Generator initialized with {framework} framework")
    
    def _initialize_framework(self):
        """Initialize the selected web framework"""
        if self.framework == "flask" and HAS_FLASK:
            self._initialize_flask()
        elif self.framework == "fastapi" and HAS_FASTAPI:
            self._initialize_fastapi()
        else:
            raise ValueError(f"Framework {self.framework} not available or not supported")
    
    def _initialize_flask(self):
        """Initialize Flask application"""
        self.app = Flask(__name__)
        CORS(self.app)  # Enable CORS for all routes
        
        # Initialize rate limiter
        self.limiter = Limiter(
            app=self.app,
            key_func=get_remote_address,
            default_limits=["1000 per hour"]
        )
        
        # Add error handlers
        @self.app.errorhandler(404)
        def not_found(error):
            return self._create_error_response("Endpoint not found", 404)
        
        @self.app.errorhandler(500)
        def internal_error(error):
            return self._create_error_response("Internal server error", 500)
        
        # Add request logging
        @self.app.before_request
        def log_request():
            self.api_stats['total_requests'] += 1
            request.start_time = datetime.now()
        
        @self.app.after_request
        def log_response(response):
            if hasattr(request, 'start_time'):
                duration = (datetime.now() - request.start_time).total_seconds()
                self._update_response_stats(response.status_code, duration)
            return response
    
    def _initialize_fastapi(self):
        """Initialize FastAPI application"""
        self.app = FastAPI(
            title=self.api_config['title'],
            version=self.api_config['version'],
            description=self.api_config['description']
        )
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Add request logging middleware
        @self.app.middleware("http")
        async def log_requests(request, call_next):
            start_time = datetime.now()
            self.api_stats['total_requests'] += 1
            
            response = await call_next(request)
            
            duration = (datetime.now() - start_time).total_seconds()
            self._update_response_stats(response.status_code, duration)
            
            return response
    
    def _generate_standard_endpoints(self) -> List[APIEndpoint]:
        """Generate standard API endpoints for the system
        
        Returns:
            List of API endpoint configurations
        """
        endpoints = [
            # System information endpoints
            APIEndpoint(
                path="/api/v1/info",
                description="Get API information and statistics",
                cache_duration=300
            ),
            
            APIEndpoint(
                path="/api/v1/health",
                description="Health check endpoint",
                cache_duration=60
            ),
            
            # Discipline endpoints
            APIEndpoint(
                path="/api/v1/disciplines",
                description="Get all available disciplines",
                cache_duration=7200  # 2 hours
            ),
            
            APIEndpoint(
                path="/api/v1/disciplines/<int:discipline_id>",
                description="Get specific discipline information",
                cache_duration=7200
            ),
            
            APIEndpoint(
                path="/api/v1/disciplines/<int:discipline_id>/summary",
                description="Get discipline summary statistics",
                cache_duration=1800  # 30 minutes
            ),
            
            # Standards endpoints
            APIEndpoint(
                path="/api/v1/standards",
                description="Get educational standards with filtering options",
                parameters=[
                    {"name": "discipline_id", "type": "integer", "description": "Filter by discipline ID"},
                    {"name": "standard_type", "type": "string", "description": "Filter by standard type"},
                    {"name": "education_level", "type": "string", "description": "Filter by education level"},
                    {"name": "min_confidence", "type": "float", "description": "Minimum confidence score"},
                    {"name": "limit", "type": "integer", "description": "Maximum number of results", "default": 100},
                    {"name": "offset", "type": "integer", "description": "Result offset for pagination", "default": 0}
                ],
                cache_duration=1800
            ),
            
            APIEndpoint(
                path="/api/v1/standards/<int:standard_id>",
                description="Get specific standard by ID",
                cache_duration=3600
            ),
            
            APIEndpoint(
                path="/api/v1/disciplines/<int:discipline_id>/standards",
                description="Get standards for a specific discipline",
                parameters=[
                    {"name": "standard_type", "type": "string", "description": "Filter by standard type"},
                    {"name": "min_confidence", "type": "float", "description": "Minimum confidence score", "default": 0.0},
                    {"name": "limit", "type": "integer", "description": "Maximum number of results", "default": 100}
                ],
                cache_duration=1800
            ),
            
            # Competency endpoints
            APIEndpoint(
                path="/api/v1/competencies",
                description="Get competency mappings with filtering",
                parameters=[
                    {"name": "discipline_id", "type": "integer", "description": "Filter by discipline ID"},
                    {"name": "competency_category", "type": "string", "description": "Filter by competency category"},
                    {"name": "bloom_level", "type": "string", "description": "Filter by Bloom's taxonomy level"},
                    {"name": "limit", "type": "integer", "description": "Maximum number of results", "default": 100}
                ],
                cache_duration=3600
            ),
            
            APIEndpoint(
                path="/api/v1/disciplines/<int:discipline_id>/competencies",
                description="Get competencies for a specific discipline",
                parameters=[
                    {"name": "competency_category", "type": "string", "description": "Filter by competency category"}
                ],
                cache_duration=3600
            ),
            
            # Document and source endpoints
            APIEndpoint(
                path="/api/v1/sources",
                description="Get standards sources with filtering",
                parameters=[
                    {"name": "discipline_id", "type": "integer", "description": "Filter by discipline ID"},
                    {"name": "min_quality_score", "type": "float", "description": "Minimum quality score", "default": 0.0},
                    {"name": "source_type", "type": "string", "description": "Filter by source type"}
                ],
                cache_duration=3600
            ),
            
            APIEndpoint(
                path="/api/v1/documents",
                description="Get retrieved documents with filtering",
                parameters=[
                    {"name": "discipline_id", "type": "integer", "description": "Filter by discipline ID"},
                    {"name": "document_type", "type": "string", "description": "Filter by document type"},
                    {"name": "processing_status", "type": "string", "description": "Filter by processing status"}
                ],
                cache_duration=1800
            ),
            
            # Analytics endpoints
            APIEndpoint(
                path="/api/v1/analytics/quality-metrics",
                description="Get quality metrics across disciplines",
                parameters=[
                    {"name": "discipline_id", "type": "integer", "description": "Filter by discipline ID"},
                    {"name": "start_date", "type": "string", "description": "Start date (YYYY-MM-DD)"},
                    {"name": "end_date", "type": "string", "description": "End date (YYYY-MM-DD)"}
                ],
                cache_duration=1800
            ),
            
            APIEndpoint(
                path="/api/v1/analytics/system-performance",
                description="Get overall system performance statistics",
                cache_duration=900  # 15 minutes
            ),
            
            # Search endpoints
            APIEndpoint(
                path="/api/v1/search/standards",
                description="Search educational standards by text query",
                parameters=[
                    {"name": "q", "type": "string", "description": "Search query", "required": True},
                    {"name": "discipline_id", "type": "integer", "description": "Filter by discipline ID"},
                    {"name": "limit", "type": "integer", "description": "Maximum number of results", "default": 50}
                ],
                cache_duration=600  # 10 minutes
            ),
            
            APIEndpoint(
                path="/api/v1/search/competencies",
                description="Search competencies by text query",
                parameters=[
                    {"name": "q", "type": "string", "description": "Search query", "required": True},
                    {"name": "discipline_id", "type": "integer", "description": "Filter by discipline ID"},
                    {"name": "limit", "type": "integer", "description": "Maximum number of results", "default": 50}
                ],
                cache_duration=600
            )
        ]
        
        return endpoints
    
    def _register_endpoints(self):
        """Register all endpoints with the web framework"""
        if self.framework == "flask":
            self._register_flask_endpoints()
        elif self.framework == "fastapi":
            self._register_fastapi_endpoints()
    
    def _register_flask_endpoints(self):
        """Register endpoints with Flask"""
        
        # System endpoints
        @self.app.route('/api/v1/info', methods=['GET'])
        @self.limiter.limit("100/minute")
        def get_api_info():
            return self._handle_request(self._api_info_handler)
        
        @self.app.route('/api/v1/health', methods=['GET'])
        def health_check():
            return self._handle_request(self._health_check_handler)
        
        # Discipline endpoints
        @self.app.route('/api/v1/disciplines', methods=['GET'])
        @self.limiter.limit("500/hour")
        def get_disciplines():
            return self._handle_request(self._get_disciplines_handler)
        
        @self.app.route('/api/v1/disciplines/<int:discipline_id>', methods=['GET'])
        @self.limiter.limit("500/hour")
        def get_discipline(discipline_id):
            return self._handle_request(self._get_discipline_handler, discipline_id)
        
        @self.app.route('/api/v1/disciplines/<int:discipline_id>/summary', methods=['GET'])
        @self.limiter.limit("200/hour")
        def get_discipline_summary(discipline_id):
            return self._handle_request(self._get_discipline_summary_handler, discipline_id)
        
        # Standards endpoints
        @self.app.route('/api/v1/standards', methods=['GET'])
        @self.limiter.limit("1000/hour")
        def get_standards():
            return self._handle_request(self._get_standards_handler)
        
        @self.app.route('/api/v1/standards/<int:standard_id>', methods=['GET'])
        @self.limiter.limit("1000/hour")
        def get_standard(standard_id):
            return self._handle_request(self._get_standard_handler, standard_id)
        
        @self.app.route('/api/v1/disciplines/<int:discipline_id>/standards', methods=['GET'])
        @self.limiter.limit("1000/hour")
        def get_discipline_standards(discipline_id):
            return self._handle_request(self._get_discipline_standards_handler, discipline_id)
        
        # Competency endpoints
        @self.app.route('/api/v1/competencies', methods=['GET'])
        @self.limiter.limit("1000/hour")
        def get_competencies():
            return self._handle_request(self._get_competencies_handler)
        
        @self.app.route('/api/v1/disciplines/<int:discipline_id>/competencies', methods=['GET'])
        @self.limiter.limit("1000/hour")
        def get_discipline_competencies(discipline_id):
            return self._handle_request(self._get_discipline_competencies_handler, discipline_id)
        
        # Analytics endpoints
        @self.app.route('/api/v1/analytics/quality-metrics', methods=['GET'])
        @self.limiter.limit("100/hour")
        def get_quality_metrics():
            return self._handle_request(self._get_quality_metrics_handler)
        
        @self.app.route('/api/v1/analytics/system-performance', methods=['GET'])
        @self.limiter.limit("50/hour")
        def get_system_performance():
            return self._handle_request(self._get_system_performance_handler)
        
        # Search endpoints
        @self.app.route('/api/v1/search/standards', methods=['GET'])
        @self.limiter.limit("200/hour")
        def search_standards():
            return self._handle_request(self._search_standards_handler)
        
        @self.app.route('/api/v1/search/competencies', methods=['GET'])
        @self.limiter.limit("200/hour")
        def search_competencies():
            return self._handle_request(self._search_competencies_handler)
    
    def _register_fastapi_endpoints(self):
        """Register endpoints with FastAPI"""
        
        # System endpoints
        @self.app.get("/api/v1/info")
        async def get_api_info():
            return await self._handle_async_request(self._api_info_handler)
        
        @self.app.get("/api/v1/health")
        async def health_check():
            return await self._handle_async_request(self._health_check_handler)
        
        # Discipline endpoints
        @self.app.get("/api/v1/disciplines")
        async def get_disciplines():
            return await self._handle_async_request(self._get_disciplines_handler)
        
        @self.app.get("/api/v1/disciplines/{discipline_id}")
        async def get_discipline(discipline_id: int):
            return await self._handle_async_request(self._get_discipline_handler, discipline_id)
        
        @self.app.get("/api/v1/disciplines/{discipline_id}/summary")
        async def get_discipline_summary(discipline_id: int):
            return await self._handle_async_request(self._get_discipline_summary_handler, discipline_id)
        
        # Standards endpoints  
        @self.app.get("/api/v1/standards")
        async def get_standards(
            discipline_id: Optional[int] = Query(None),
            standard_type: Optional[str] = Query(None),
            education_level: Optional[str] = Query(None),
            min_confidence: float = Query(0.0),
            limit: int = Query(100),
            offset: int = Query(0)
        ):
            params = {
                'discipline_id': discipline_id,
                'standard_type': standard_type, 
                'education_level': education_level,
                'min_confidence': min_confidence,
                'limit': limit,
                'offset': offset
            }
            return await self._handle_async_request(self._get_standards_handler, **params)
        
        # Additional FastAPI endpoints would follow similar pattern...
    
    def _handle_request(self, handler, *args, **kwargs):
        """Handle Flask request with standardized response format"""
        try:
            start_time = datetime.now()
            result = handler(*args, **kwargs)
            
            response = APIResponse(
                success=True,
                data=result,
                timestamp=datetime.now().isoformat(),
                meta={
                    'processing_time_ms': int((datetime.now() - start_time).total_seconds() * 1000),
                    'api_version': self.api_config['version']
                }
            )
            
            self.api_stats['successful_requests'] += 1
            return jsonify(asdict(response))
            
        except Exception as e:
            self.api_stats['failed_requests'] += 1
            self.logger.error(f"Request handler error: {e}")
            return self._create_error_response(str(e), 500)
    
    async def _handle_async_request(self, handler, *args, **kwargs):
        """Handle FastAPI request with standardized response format"""
        try:
            start_time = datetime.now()
            result = handler(*args, **kwargs)
            
            response = APIResponse(
                success=True,
                data=result,
                timestamp=datetime.now().isoformat(),
                meta={
                    'processing_time_ms': int((datetime.now() - start_time).total_seconds() * 1000),
                    'api_version': self.api_config['version']
                }
            )
            
            self.api_stats['successful_requests'] += 1
            return asdict(response)
            
        except Exception as e:
            self.api_stats['failed_requests'] += 1
            self.logger.error(f"Async request handler error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # ==============================================================================
    # ENDPOINT HANDLERS
    # ==============================================================================
    
    def _api_info_handler(self):
        """Handle API information request"""
        return {
            **self.api_config,
            'statistics': self.api_stats,
            'endpoints_count': len(self.endpoints),
            'database_stats': self.db.get_connection_stats()
        }
    
    def _health_check_handler(self):
        """Handle health check request"""
        try:
            # Test database connection
            disciplines = self.db.get_all_disciplines()
            db_healthy = len(disciplines) >= 0
            
            return {
                'status': 'healthy' if db_healthy else 'unhealthy',
                'timestamp': datetime.now().isoformat(),
                'database_connection': 'ok' if db_healthy else 'failed',
                'api_version': self.api_config['version']
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def _get_disciplines_handler(self):
        """Handle get all disciplines request"""
        return self.db.get_all_disciplines()
    
    def _get_discipline_handler(self, discipline_id: int):
        """Handle get specific discipline request"""
        disciplines = self.db.get_all_disciplines()
        discipline = next((d for d in disciplines if d['discipline_id'] == discipline_id), None)
        
        if not discipline:
            raise Exception(f"Discipline {discipline_id} not found")
        
        return discipline
    
    def _get_discipline_summary_handler(self, discipline_id: int):
        """Handle discipline summary request"""
        return self.db.get_discipline_summary(discipline_id)
    
    def _get_standards_handler(self, **params):
        """Handle get standards request with filtering"""
        discipline_id = params.get('discipline_id')
        standard_type = params.get('standard_type')
        education_level = params.get('education_level')
        min_confidence = params.get('min_confidence', 0.0)
        limit = params.get('limit', 100)
        offset = params.get('offset', 0)
        
        if discipline_id:
            standards = self.db.get_standards_by_discipline(
                discipline_id=discipline_id,
                standard_type=standard_type,
                min_confidence=min_confidence,
                limit=limit
            )
        else:
            # Get standards across all disciplines (would need implementation)
            standards = []
        
        # Apply offset for pagination
        if offset > 0:
            standards = standards[offset:]
        
        return {
            'standards': standards,
            'total_count': len(standards),
            'filters_applied': {
                'discipline_id': discipline_id,
                'standard_type': standard_type,
                'education_level': education_level,
                'min_confidence': min_confidence
            },
            'pagination': {
                'limit': limit,
                'offset': offset
            }
        }
    
    def _get_standard_handler(self, standard_id: int):
        """Handle get specific standard request"""
        # Would need implementation in database_manager
        return {'standard_id': standard_id, 'message': 'Individual standard lookup not yet implemented'}
    
    def _get_discipline_standards_handler(self, discipline_id: int):
        """Handle get discipline standards request"""
        standard_type = request.args.get('standard_type') if self.framework == 'flask' else None
        min_confidence = float(request.args.get('min_confidence', 0.0)) if self.framework == 'flask' else 0.0
        limit = int(request.args.get('limit', 100)) if self.framework == 'flask' else 100
        
        standards = self.db.get_standards_by_discipline(
            discipline_id=discipline_id,
            standard_type=standard_type,
            min_confidence=min_confidence,
            limit=limit
        )
        
        return {
            'discipline_id': discipline_id,
            'standards': standards,
            'count': len(standards)
        }
    
    def _get_competencies_handler(self):
        """Handle get competencies request"""
        discipline_id = request.args.get('discipline_id', type=int) if self.framework == 'flask' else None
        competency_category = request.args.get('competency_category') if self.framework == 'flask' else None
        limit = int(request.args.get('limit', 100)) if self.framework == 'flask' else 100
        
        if discipline_id:
            competencies = self.db.get_competencies_by_discipline(
                discipline_id=discipline_id,
                competency_category=competency_category
            )
        else:
            competencies = []
        
        return {
            'competencies': competencies[:limit],
            'filters_applied': {
                'discipline_id': discipline_id,
                'competency_category': competency_category
            }
        }
    
    def _get_discipline_competencies_handler(self, discipline_id: int):
        """Handle get discipline competencies request"""
        competency_category = request.args.get('competency_category') if self.framework == 'flask' else None
        
        competencies = self.db.get_competencies_by_discipline(
            discipline_id=discipline_id,
            competency_category=competency_category
        )
        
        return {
            'discipline_id': discipline_id,
            'competencies': competencies,
            'count': len(competencies)
        }
    
    def _get_quality_metrics_handler(self):
        """Handle quality metrics request"""
        discipline_id = request.args.get('discipline_id', type=int) if self.framework == 'flask' else None
        start_date_str = request.args.get('start_date') if self.framework == 'flask' else None
        end_date_str = request.args.get('end_date') if self.framework == 'flask' else None
        
        start_date = datetime.fromisoformat(start_date_str) if start_date_str else None
        end_date = datetime.fromisoformat(end_date_str) if end_date_str else None
        
        metrics = self.db.get_quality_metrics(
            discipline_id=discipline_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return {
            'quality_metrics': metrics,
            'filters_applied': {
                'discipline_id': discipline_id,
                'start_date': start_date_str,
                'end_date': end_date_str
            }
        }
    
    def _get_system_performance_handler(self):
        """Handle system performance request"""
        return self.db.get_system_performance_stats()
    
    def _search_standards_handler(self):
        """Handle standards search request"""
        query = request.args.get('q') if self.framework == 'flask' else ""
        discipline_id = request.args.get('discipline_id', type=int) if self.framework == 'flask' else None
        limit = int(request.args.get('limit', 50)) if self.framework == 'flask' else 50
        
        if not query:
            raise Exception("Search query parameter 'q' is required")
        
        # Implement text search (would need full-text search in database)
        return {
            'query': query,
            'results': [],
            'message': 'Full-text search not yet implemented',
            'filters': {
                'discipline_id': discipline_id,
                'limit': limit
            }
        }
    
    def _search_competencies_handler(self):
        """Handle competencies search request"""
        query = request.args.get('q') if self.framework == 'flask' else ""
        discipline_id = request.args.get('discipline_id', type=int) if self.framework == 'flask' else None
        limit = int(request.args.get('limit', 50)) if self.framework == 'flask' else 50
        
        if not query:
            raise Exception("Search query parameter 'q' is required")
        
        # Implement text search (would need full-text search in database)
        return {
            'query': query,
            'results': [],
            'message': 'Full-text search not yet implemented',
            'filters': {
                'discipline_id': discipline_id,
                'limit': limit
            }
        }
    
    # ==============================================================================
    # UTILITY METHODS
    # ==============================================================================
    
    def _create_error_response(self, message: str, status_code: int):
        """Create standardized error response"""
        error_response = APIResponse(
            success=False,
            message=message,
            timestamp=datetime.now().isoformat(),
            errors=[message]
        )
        
        if self.framework == "flask":
            response = make_response(jsonify(asdict(error_response)), status_code)
            return response
        else:
            return JSONResponse(
                status_code=status_code,
                content=asdict(error_response)
            )
    
    def _update_response_stats(self, status_code: int, duration: float):
        """Update API response statistics"""
        if 200 <= status_code < 300:
            self.api_stats['successful_requests'] += 1
        else:
            self.api_stats['failed_requests'] += 1
        
        # Update average response time
        current_avg = self.api_stats['avg_response_time']
        total_requests = self.api_stats['total_requests']
        
        if total_requests > 0:
            self.api_stats['avg_response_time'] = (
                (current_avg * (total_requests - 1) + duration) / total_requests
            )
    
    def generate_openapi_spec(self) -> Dict[str, Any]:
        """Generate OpenAPI 3.0 specification for the API
        
        Returns:
            OpenAPI specification dictionary
        """
        spec = {
            'openapi': '3.0.0',
            'info': {
                'title': self.api_config['title'],
                'version': self.api_config['version'],
                'description': self.api_config['description']
            },
            'servers': [
                {'url': self.api_config['base_url']}
            ],
            'paths': {},
            'components': {
                'schemas': {
                    'APIResponse': {
                        'type': 'object',
                        'properties': {
                            'success': {'type': 'boolean'},
                            'data': {'type': 'object'},
                            'message': {'type': 'string'},
                            'timestamp': {'type': 'string', 'format': 'date-time'},
                            'meta': {'type': 'object'},
                            'errors': {'type': 'array', 'items': {'type': 'string'}}
                        }
                    }
                }
            }
        }
        
        # Generate path specifications from endpoints
        for endpoint in self.endpoints:
            path_spec = {
                endpoint.method.lower(): {
                    'summary': endpoint.description,
                    'parameters': [],
                    'responses': {
                        '200': {
                            'description': 'Successful response',
                            'content': {
                                'application/json': {
                                    'schema': {'$ref': '#/components/schemas/APIResponse'}
                                }
                            }
                        }
                    }
                }
            }
            
            # Add parameters if defined
            if endpoint.parameters:
                for param in endpoint.parameters:
                    param_spec = {
                        'name': param['name'],
                        'in': 'query',
                        'description': param.get('description', ''),
                        'required': param.get('required', False),
                        'schema': {'type': param.get('type', 'string')}
                    }
                    
                    if 'default' in param:
                        param_spec['schema']['default'] = param['default']
                    
                    path_spec[endpoint.method.lower()]['parameters'].append(param_spec)
            
            spec['paths'][endpoint.path] = path_spec
        
        return spec
    
    def save_api_documentation(self, output_path: str):
        """Save API documentation to file
        
        Args:
            output_path: Path to save documentation
        """
        try:
            spec = self.generate_openapi_spec()
            
            with open(output_path, 'w') as f:
                json.dump(spec, f, indent=2)
            
            self.logger.info(f"API documentation saved to: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save API documentation: {e}")
    
    def run_server(self, debug: bool = False):
        """Start the API server
        
        Args:
            debug: Enable debug mode
        """
        try:
            if self.framework == "flask":
                self.logger.info(f"Starting Flask API server on {self.host}:{self.port}")
                self.app.run(host=self.host, port=self.port, debug=debug)
            elif self.framework == "fastapi":
                self.logger.info(f"Starting FastAPI server on {self.host}:{self.port}")
                uvicorn.run(self.app, host=self.host, port=self.port)
                
        except Exception as e:
            self.logger.error(f"Failed to start API server: {e}")
            raise

# Entry point for running the API server
def main():
    """Main entry point for API server"""
    
    # Initialize database manager
    db_config = DatabaseConfig(
        database_type="sqlite",
        sqlite_path="data/international_standards.db"
    )
    
    try:
        db_manager = DatabaseManager(db_config)
        
        # Initialize API generator
        api_generator = APIGenerator(
            database_manager=db_manager,
            framework="flask",  # or "fastapi"
            host="0.0.0.0",
            port=5000
        )
        
        # Save API documentation
        api_generator.save_api_documentation("api/openapi_spec.json")
        
        # Start server
        api_generator.run_server(debug=True)
        
    except Exception as e:
        logging.error(f"Failed to start API server: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()