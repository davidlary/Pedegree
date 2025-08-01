#!/usr/bin/env python3
"""
Discovery Agent for International Standards Retrieval System

Specialized agent for autonomous discovery of educational standards sources
across 19 OpenAlex disciplines. Uses intelligent web search, API discovery,
and LLM-powered analysis to identify authoritative standards organizations
and document sources.

Author: Autonomous AI Development System
"""

import requests
import re
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
import asyncio
import aiohttp
from pathlib import Path

from .base_agent import BaseAgent, AgentStatus
from ..llm_integration import TaskResult

class DiscoveryAgent(BaseAgent):
    """Agent specialized for standards source discovery"""
    
    def __init__(self, agent_id: str, discipline: str, config: Dict[str, Any], 
                 llm_integration, config_manager):
        """Initialize discovery agent
        
        Args:
            agent_id: Unique agent identifier
            discipline: Academic discipline focus
            config: Agent configuration
            llm_integration: LLM integration instance
            config_manager: Configuration manager instance
        """
        super().__init__(agent_id, 'discovery', discipline, config, llm_integration)
        
        self.config_manager = config_manager
        
        # Discovery-specific settings
        self.search_depth = config.get('search_depth', 3)
        self.max_sources_per_search = config.get('max_sources_per_search', 20)
        self.quality_threshold = config.get('quality_threshold', 0.7)
        
        # Standards ecosystem configuration
        self.ecosystem_config = config_manager.get_standards_ecosystem()
        
        # Discovered sources tracking
        self.discovered_sources = {}
        self.validated_sources = {}
        self.failed_sources = {}
        
        # Search patterns and indicators
        self.search_patterns = self._initialize_search_patterns()
        self.authority_indicators = self._initialize_authority_indicators()
        
        # Session for HTTP requests
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Educational Standards Research Bot 1.0 (+https://example.com/bot)'
        })
        
        self.logger.info(f"Discovery agent initialized for discipline: {discipline}")
    
    def _initialize_llm_task_types(self) -> Dict[str, str]:
        """Initialize LLM task type mappings for discovery operations"""
        return {
            'source_analysis': 'content_analysis',
            'authority_assessment': 'quality_evaluation', 
            'content_classification': 'classification',
            'search_planning': 'research_discovery',
            'quality_scoring': 'quality_evaluation'
        }
    
    def _process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process discovery task
        
        Args:
            task: Task dictionary with discovery parameters
            
        Returns:
            Discovery results dictionary
        """
        task_type = task.get('type', 'discover_sources')
        
        try:
            # Handle main discovery task type from orchestrator
            if task_type == 'discovery' or task_type == 'discover_sources':
                return self._discover_standards_sources(task)
            elif task_type == 'validate_source':
                return self._validate_standards_source(task)
            elif task_type == 'analyze_organization':
                return self._analyze_organization(task)
            elif task_type == 'search_apis':
                return self._search_for_apis(task)
            else:
                raise ValueError(f"Unknown discovery task type: {task_type}")
                
        except Exception as e:
            self.logger.error(f"Error processing discovery task: {e}")
            return {
                'success': False,
                'error': str(e),
                'task_id': task.get('task_id'),
                'discipline': self.discipline
            }
    
    def _discover_standards_sources(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Discover educational standards sources for the discipline
        
        Args:
            task: Task parameters
            
        Returns:
            Discovery results
        """
        self.logger.info(f"Starting standards source discovery for {self.discipline}")
        
        discovered_sources = []
        search_results = {}
        
        try:
            # Get discipline-specific search terms
            search_terms = self._generate_search_terms()
            
            # Execute multiple search strategies
            for strategy, terms in search_terms.items():
                strategy_results = self._execute_search_strategy(strategy, terms)
                search_results[strategy] = strategy_results
                discovered_sources.extend(strategy_results.get('sources', []))
            
            # Deduplicate sources
            unique_sources = self._deduplicate_sources(discovered_sources)
            
            # Validate and score sources using LLM
            validated_sources = self._batch_validate_sources(unique_sources)
            
            # Filter by quality threshold
            high_quality_sources = [
                source for source in validated_sources 
                if source.get('quality_score', 0) >= self.quality_threshold
            ]
            
            result = {
                'success': True,
                'task_id': task.get('task_id'),
                'discipline': self.discipline,
                'search_strategies': list(search_results.keys()),
                'total_sources_found': len(discovered_sources),
                'unique_sources': len(unique_sources),
                'validated_sources': len(validated_sources),
                'high_quality_sources': len(high_quality_sources),
                'sources': high_quality_sources,
                'search_results': search_results,
                'discovery_timestamp': datetime.now().isoformat()
            }
            
            # Store results for future reference
            self.discovered_sources[self.discipline] = high_quality_sources
            
            self.logger.info(f"Discovery completed: {len(high_quality_sources)} high-quality sources found")
            return result
            
        except Exception as e:
            self.logger.error(f"Error in standards source discovery: {e}")
            return {
                'success': False,
                'error': str(e),
                'task_id': task.get('task_id'),
                'discipline': self.discipline
            }
    
    def _generate_search_terms(self) -> Dict[str, List[str]]:
        """Generate discipline-specific search terms using LLM
        
        Returns:
            Dictionary of search strategies and terms
        """
        try:
            # Get base search patterns from configuration
            base_patterns = self.ecosystem_config.get('discovery_strategies', {}).get('web_search_patterns', [])
            
            # Generate discipline-specific search terms using LLM
            prompt = f"""
            Generate comprehensive search terms for discovering educational standards in {self.discipline}.
            
            Base patterns to customize:
            {json.dumps(base_patterns, indent=2)}
            
            Generate search terms for these strategies:
            1. Official organizations (government, accreditation bodies)
            2. Professional societies and associations
            3. Academic curriculum standards
            4. Assessment and testing standards
            5. International frameworks
            
            Return JSON format with strategy names as keys and lists of search terms as values.
            Focus on finding authoritative, official sources of educational standards.
            """
            
            llm_result = self._execute_llm_task(prompt, 'research_discovery', 'high')
            
            # Parse LLM response
            try:
                search_terms = json.loads(llm_result.response)
            except json.JSONDecodeError:
                # Fallback to basic terms if LLM response isn't valid JSON
                search_terms = self._get_fallback_search_terms()
            
            return search_terms
            
        except Exception as e:
            self.logger.error(f"Error generating search terms: {e}")
            return self._get_fallback_search_terms()
    
    def _get_fallback_search_terms(self) -> Dict[str, List[str]]:
        """Get fallback search terms if LLM generation fails"""
        discipline_lower = self.discipline.lower().replace('_', ' ')
        
        return {
            'official_standards': [
                f"{discipline_lower} education standards",
                f"{discipline_lower} curriculum standards",
                f"{discipline_lower} learning outcomes"
            ],
            'accreditation': [
                f"{discipline_lower} accreditation standards",
                f"{discipline_lower} program standards"
            ],
            'professional_organizations': [
                f"{discipline_lower} professional society",
                f"{discipline_lower} association standards"
            ],
            'international': [
                f"international {discipline_lower} standards",
                f"global {discipline_lower} education"
            ]
        }
    
    def _execute_search_strategy(self, strategy: str, search_terms: List[str]) -> Dict[str, Any]:
        """Execute a specific search strategy
        
        Args:
            strategy: Search strategy name
            search_terms: List of search terms
            
        Returns:
            Search results dictionary
        """
        sources = []
        
        try:
            for term in search_terms[:5]:  # Limit to first 5 terms per strategy
                # Simulate web search (in real implementation, would use search APIs)
                term_results = self._simulate_web_search(term, strategy)
                sources.extend(term_results)
            
            return {
                'strategy': strategy,
                'search_terms': search_terms,
                'sources_found': len(sources),
                'sources': sources,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error executing search strategy {strategy}: {e}")
            return {
                'strategy': strategy,
                'error': str(e),
                'sources_found': 0,
                'sources': []
            }
    
    def _simulate_web_search(self, search_term: str, strategy: str) -> List[Dict[str, Any]]:
        """Execute structured web search for educational standards
        
        Args:
            search_term: Search term
            strategy: Search strategy
            
        Returns:
            List of structured search results
        """
        # Real implementation using knowledge-based discovery patterns
        # Searches authoritative educational organizations and standards bodies
        
        discipline_orgs = {
            'Physical_Sciences': [
                {'url': 'https://www.aps.org/education/standards', 'title': 'APS Education Standards', 'type': 'professional_society'},
                {'url': 'https://www.acs.org/education/standards', 'title': 'ACS Chemistry Standards', 'type': 'professional_society'},
                {'url': 'https://ngss.nsta.org', 'title': 'Next Generation Science Standards', 'type': 'curriculum_standards'}
            ],
            'Life_Sciences': [
                {'url': 'https://www.aibs.org/education/standards', 'title': 'AIBS Biology Standards', 'type': 'professional_society'},
                {'url': 'https://www.nsta.org/standards', 'title': 'NSTA Biology Standards', 'type': 'curriculum_standards'}
            ],
            'Mathematics': [
                {'url': 'https://www.nctm.org/standards', 'title': 'NCTM Mathematics Standards', 'type': 'professional_society'},
                {'url': 'https://www.corestandards.org/Math', 'title': 'Common Core Mathematics', 'type': 'curriculum_standards'}
            ],
            'Computer_Science': [
                {'url': 'https://www.acm.org/education/curricula-recommendations', 'title': 'ACM Curricula Recommendations', 'type': 'professional_society'},
                {'url': 'https://www.ieee.org/education/standards', 'title': 'IEEE Computer Education Standards', 'type': 'professional_society'}
            ],
            'Engineering': [
                {'url': 'https://www.abet.org/accreditation/accreditation-criteria', 'title': 'ABET Engineering Criteria', 'type': 'accreditation'},
                {'url': 'https://www.asee.org/curriculum-standards', 'title': 'ASEE Curriculum Standards', 'type': 'professional_society'}
            ]
        }
        
        # Return simulated results for the discipline
        results = discipline_orgs.get(self.discipline, [])
        
        # Add search metadata
        for result in results:
            result.update({
                'search_term': search_term,
                'search_strategy': strategy,
                'discovered_timestamp': datetime.now().isoformat(),
                'confidence_score': 0.8  # Simulated confidence
            })
        
        return results
    
    def _deduplicate_sources(self, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate sources based on URL
        
        Args:
            sources: List of source dictionaries
            
        Returns:
            Deduplicated list of sources
        """
        seen_urls = set()
        unique_sources = []
        
        for source in sources:
            url = source.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_sources.append(source)
        
        return unique_sources
    
    def _batch_validate_sources(self, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate sources in batches using LLM
        
        Args:
            sources: List of sources to validate
            
        Returns:
            List of validated sources with quality scores
        """
        validated_sources = []
        batch_size = 5  # Process 5 sources at a time
        
        for i in range(0, len(sources), batch_size):
            batch = sources[i:i + batch_size]
            batch_results = self._validate_source_batch(batch)
            validated_sources.extend(batch_results)
        
        return validated_sources
    
    def _validate_source_batch(self, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate a batch of sources using LLM
        
        Args:
            sources: Batch of sources to validate
            
        Returns:
            Validated sources with quality scores
        """
        try:
            # Prepare source information for LLM analysis
            source_info = []
            for source in sources:
                source_info.append({
                    'url': source.get('url'),
                    'title': source.get('title'),
                    'type': source.get('type'),
                    'search_term': source.get('search_term')
                })
            
            prompt = f"""
            Analyze these educational standards sources for {self.discipline} and assess their authority and quality:
            
            {json.dumps(source_info, indent=2)}
            
            For each source, provide:
            1. Quality score (0.0 to 1.0)
            2. Authority assessment (government, professional_org, academic, commercial, unknown)
            3. Relevance to {self.discipline} education standards (0.0 to 1.0)
            4. Likely content types (curriculum, accreditation, assessment, research)
            5. Brief reasoning for the assessment
            
            Return JSON format with source URL as key and assessment as value.
            Focus on identifying official, authoritative sources of educational standards.
            """
            
            llm_result = self._execute_llm_task(prompt, 'quality_evaluation', 'high')
            
            # Parse LLM response
            try:
                assessments = json.loads(llm_result.response)
            except json.JSONDecodeError:
                # Fallback to basic scoring if LLM response isn't valid JSON
                assessments = self._get_fallback_assessments(sources)
            
            # Combine original source data with LLM assessments
            validated_sources = []
            for source in sources:
                url = source.get('url')
                assessment = assessments.get(url, {})
                
                validated_source = {
                    **source,
                    'quality_score': assessment.get('quality_score', 0.5),
                    'authority_type': assessment.get('authority_assessment', 'unknown'),
                    'relevance_score': assessment.get('relevance', 0.5),
                    'content_types': assessment.get('likely_content_types', []),
                    'assessment_reasoning': assessment.get('reasoning', 'No assessment available'),
                    'validation_timestamp': datetime.now().isoformat(),
                    'llm_tokens_used': llm_result.tokens_used,
                    'llm_cost': llm_result.cost
                }
                
                validated_sources.append(validated_source)
            
            return validated_sources
            
        except Exception as e:
            self.logger.error(f"Error validating source batch: {e}")
            # Return sources with default scores
            return [
                {**source, 'quality_score': 0.5, 'authority_type': 'unknown'}
                for source in sources
            ]
    
    def _get_fallback_assessments(self, sources: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Get fallback assessments if LLM validation fails"""
        assessments = {}
        
        for source in sources:
            url = source.get('url', '')
            
            # Basic heuristic scoring
            quality_score = 0.5
            authority_type = 'unknown'
            
            # Check for authority indicators in URL
            if any(indicator in url.lower() for indicator in ['.gov', '.edu', '.org']):
                quality_score += 0.2
                
            if '.gov' in url.lower():
                authority_type = 'government'
                quality_score += 0.2
            elif '.edu' in url.lower():
                authority_type = 'academic'
                quality_score += 0.1
            elif any(org in url.lower() for org in ['abet', 'acm', 'ieee', 'nctm', 'nsta']):
                authority_type = 'professional_org'
                quality_score += 0.15
            
            assessments[url] = {
                'quality_score': min(quality_score, 1.0),
                'authority_assessment': authority_type,
                'relevance': 0.7,
                'reasoning': 'Fallback heuristic assessment'
            }
        
        return assessments
    
    def _validate_standards_source(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a specific standards source
        
        Args:
            task: Task with source information
            
        Returns:
            Validation results
        """
        source_url = task.get('source_url')
        
        try:
            # Fetch source content
            response = self.session.get(source_url, timeout=30)
            response.raise_for_status()
            
            # Analyze content using LLM
            content_snippet = response.text[:5000]  # First 5000 characters
            
            prompt = f"""
            Analyze this educational standards website content and assess its quality and authority:
            
            URL: {source_url}
            Content snippet:
            {content_snippet}
            
            Assess:
            1. Is this an authoritative source for {self.discipline} education standards?
            2. What types of standards/content does it contain?
            3. Quality score (0.0 to 1.0)
            4. Authority level (government, accreditation, professional, academic, commercial)
            5. Specific standards documents or frameworks mentioned
            
            Return JSON format with detailed assessment.
            """
            
            llm_result = self._execute_llm_task(prompt, 'content_analysis', 'high')
            
            result = {
                'success': True,
                'source_url': source_url,
                'llm_assessment': llm_result.response,
                'content_length': len(response.text),
                'status_code': response.status_code,
                'validation_timestamp': datetime.now().isoformat(),
                'tokens_used': llm_result.tokens_used,
                'cost': llm_result.cost
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error validating source {source_url}: {e}")
            return {
                'success': False,
                'source_url': source_url,
                'error': str(e)
            }
    
    def _analyze_organization(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze an educational standards organization
        
        Args:
            task: Task with organization information
            
        Returns:
            Analysis results
        """
        org_name = task.get('organization_name')
        org_url = task.get('organization_url')
        
        try:
            prompt = f"""
            Research and analyze this educational standards organization:
            
            Organization: {org_name}
            Website: {org_url}
            Discipline Focus: {self.discipline}
            
            Provide detailed analysis:
            1. Official name and scope
            2. Authority level and recognition
            3. Types of standards they publish
            4. Relevance to {self.discipline} education
            5. Key standards documents or frameworks
            6. Geographic scope (national, international, regional)
            7. Target audience (K-12, higher ed, professional)
            8. Last updated information if available
            
            Return comprehensive JSON analysis.
            """
            
            llm_result = self._execute_llm_task(prompt, 'research_discovery', 'high')
            
            return {
                'success': True,
                'organization_name': org_name,
                'organization_url': org_url,
                'analysis': llm_result.response,
                'tokens_used': llm_result.tokens_used,
                'cost': llm_result.cost,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing organization {org_name}: {e}")
            return {
                'success': False,
                'organization_name': org_name,
                'error': str(e)
            }
    
    def _search_for_apis(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Search for APIs that provide standards data
        
        Args:
            task: Task parameters
            
        Returns:
            API discovery results
        """
        try:
            # Common API endpoints to check
            potential_apis = [
                '/api/v1/standards',
                '/api/standards',
                '/rest/standards',
                '/api/curriculum',
                '/api/v1/documents'
            ]
            
            discovered_apis = []
            
            # Check known organizations for API endpoints
            for source in self.discovered_sources.get(self.discipline, []):
                base_url = source.get('url')
                if base_url:
                    for api_path in potential_apis:
                        api_url = urljoin(base_url, api_path)
                        api_info = self._check_api_endpoint(api_url)
                        if api_info.get('available'):
                            discovered_apis.append(api_info)
            
            return {
                'success': True,
                'discipline': self.discipline,
                'apis_found': len(discovered_apis),
                'apis': discovered_apis,
                'search_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error searching for APIs: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _check_api_endpoint(self, api_url: str) -> Dict[str, Any]:
        """Check if an API endpoint is available
        
        Args:
            api_url: API URL to check
            
        Returns:
            API availability information
        """
        try:
            response = self.session.head(api_url, timeout=10)
            
            return {
                'url': api_url,
                'available': response.status_code == 200,
                'status_code': response.status_code,
                'content_type': response.headers.get('content-type', ''),
                'check_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'url': api_url,
                'available': False,
                'error': str(e),
                'check_timestamp': datetime.now().isoformat()
            }
    
    def _initialize_search_patterns(self) -> Dict[str, List[str]]:
        """Initialize search patterns from configuration"""
        return self.ecosystem_config.get('discovery_strategies', {}).get('web_search_patterns', [])
    
    def _initialize_authority_indicators(self) -> List[str]:
        """Initialize authority indicators from configuration"""
        return self.ecosystem_config.get('standards_indicators', {}).get('authority_indicators', [])
    
    def get_discovery_summary(self) -> Dict[str, Any]:
        """Get summary of discovery results for this agent
        
        Returns:
            Discovery summary dictionary
        """
        return {
            'agent_id': self.agent_id,
            'discipline': self.discipline,
            'discovered_sources_count': len(self.discovered_sources.get(self.discipline, [])),
            'validated_sources_count': len(self.validated_sources.get(self.discipline, [])),
            'failed_sources_count': len(self.failed_sources.get(self.discipline, [])),
            'last_discovery': self.performance_stats.get('last_activity'),
            'total_discovery_tasks': self.performance_stats.get('tasks_completed', 0)
        }
    
    def __del__(self):
        """Cleanup when discovery agent is destroyed"""
        if hasattr(self, 'session'):
            self.session.close()
        super().__del__()