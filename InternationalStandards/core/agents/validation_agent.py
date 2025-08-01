#!/usr/bin/env python3
"""
Validation Agent for International Standards Retrieval System

Specialized agent for autonomous validation and quality assurance of processed
educational standards across 19 OpenAlex disciplines. Handles accuracy verification,
completeness assessment, and quality scoring.

Author: Autonomous AI Development System
"""

import json
import re
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime, timedelta
from pathlib import Path
import hashlib
from collections import defaultdict, Counter
import statistics
import concurrent.futures
import threading

# Text similarity libraries (optional)
try:
    from difflib import SequenceMatcher
    import Levenshtein
    HAS_TEXT_SIMILARITY = True
except ImportError:
    HAS_TEXT_SIMILARITY = False

from .base_agent import BaseAgent, AgentStatus
from ..llm_integration import TaskResult

class ValidationAgent(BaseAgent):
    """Agent specialized for standards validation and quality assurance"""
    
    def __init__(self, agent_id: str, discipline: str, config: Dict[str, Any], 
                 llm_integration, config_manager):
        """Initialize validation agent
        
        Args:
            agent_id: Unique agent identifier
            discipline: Academic discipline focus
            config: Agent configuration
            llm_integration: LLM integration instance
            config_manager: Configuration manager instance
        """
        super().__init__(agent_id, 'validation', discipline, config, llm_integration)
        
        self.config_manager = config_manager
        
        # Validation-specific settings
        self.quality_threshold = config.get('quality_threshold', 0.7)
        self.completeness_threshold = config.get('completeness_threshold', 0.8)
        self.accuracy_threshold = config.get('accuracy_threshold', 0.75)
        self.max_concurrent_validations = config.get('max_concurrent_validations', 3)
        
        # Validation criteria weights
        self.validation_weights = {
            'accuracy': 0.35,
            'completeness': 0.25,
            'relevance': 0.20,
            'authority': 0.15,
            'consistency': 0.05
        }
        
        # Storage configuration
        self.data_dir = Path(config.get('data_directory', 'data'))
        self.validation_dir = self.data_dir / 'validation' / discipline
        self.validation_dir.mkdir(parents=True, exist_ok=True)
        
        # Validation tracking
        self.validated_documents = {}
        self.validation_reports = {}
        self.quality_scores = {}
        self.failed_validations = {}
        
        # Quality assessment criteria
        self.quality_criteria = self._initialize_quality_criteria()
        self.discipline_requirements = self._load_discipline_requirements()
        
        # Validation locks for thread safety
        self.validation_lock = threading.Lock()
        
        self.logger.info(f"Validation agent initialized for discipline: {discipline}")
    
    def _initialize_llm_task_types(self) -> Dict[str, str]:
        """Initialize LLM task type mappings for validation operations"""
        return {
            'accuracy_assessment': 'quality_evaluation',
            'completeness_check': 'quality_evaluation',
            'relevance_scoring': 'quality_evaluation',
            'authority_verification': 'quality_evaluation',
            'consistency_analysis': 'quality_evaluation',
            'cross_validation': 'content_analysis'
        }
    
    def _process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process validation task
        
        Args:
            task: Task dictionary with validation parameters
            
        Returns:
            Validation results dictionary
        """
        task_type = task.get('type', 'validate_standards')
        
        try:
            # Handle main validation task type from orchestrator
            if task_type == 'validation' or task_type == 'validate_standards':
                return self._validate_processed_standards(task)
            elif task_type == 'quality_assessment':
                return self._perform_quality_assessment(task)
            elif task_type == 'cross_validation':
                return self._perform_cross_validation(task)
            elif task_type == 'completeness_check':
                return self._check_completeness(task)
            elif task_type == 'consistency_analysis':
                return self._analyze_consistency(task)
            else:
                raise ValueError(f"Unknown validation task type: {task_type}")
                
        except Exception as e:
            self.logger.error(f"Error processing validation task: {e}")
            return {
                'success': False,
                'error': str(e),
                'task_id': task.get('task_id'),
                'discipline': self.discipline
            }
    
    def _validate_processed_standards(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Validate processed standards documents and extracted data
        
        Args:
            task: Task parameters with processing results
            
        Returns:
            Validation results
        """
        self.logger.info(f"Starting standards validation for {self.discipline}")
        
        processing_results = task.get('processing_results', [])
        validation_results = []
        
        try:
            # Validate documents in batches for concurrent processing
            batch_size = self.max_concurrent_validations
            
            for i in range(0, len(processing_results), batch_size):
                batch_results = processing_results[i:i + batch_size]
                batch_validations = self._validate_result_batch(batch_results)
                validation_results.extend(batch_validations)
            
            # Perform aggregate validation analysis
            aggregate_analysis = self._perform_aggregate_validation(validation_results)
            
            # Generate validation report
            validation_report = self._generate_validation_report(validation_results, aggregate_analysis)
            
            result = {
                'success': True,
                'task_id': task.get('task_id'),
                'discipline': self.discipline,
                'documents_validated': len([r for r in validation_results if r.get('success')]),
                'documents_failed_validation': len([r for r in validation_results if not r.get('success')]),
                'overall_quality_score': aggregate_analysis.get('overall_quality_score', 0.0),
                'validation_results': validation_results,
                'aggregate_analysis': aggregate_analysis,
                'validation_report': validation_report,
                'validation_timestamp': datetime.now().isoformat()
            }
            
            # Store results for future reference
            self.validated_documents[self.discipline] = validation_results
            self.validation_reports[self.discipline] = validation_report
            
            # Save validation report
            self._save_validation_report(validation_report)
            
            self.logger.info(f"Standards validation completed: {len(validation_results)} documents validated")
            return result
            
        except Exception as e:
            self.logger.error(f"Error in standards validation: {e}")
            return {
                'success': False,
                'error': str(e),
                'task_id': task.get('task_id'),
                'discipline': self.discipline
            }
    
    def _validate_result_batch(self, processing_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate a batch of processing results concurrently
        
        Args:
            processing_results: List of processing result dictionaries
            
        Returns:
            List of validation results
        """
        results = []
        
        # Use ThreadPoolExecutor for concurrent validation
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_concurrent_validations) as executor:
            # Submit all validation tasks
            future_to_result = {
                executor.submit(self._validate_single_processing_result, result): result 
                for result in processing_results
            }
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_result):
                processing_result = future_to_result[future]
                try:
                    validation_result = future.result()
                    results.append(validation_result)
                except Exception as e:
                    doc_title = processing_result.get('document', {}).get('document_info', {}).get('title', 'unknown')
                    self.logger.error(f"Error validating processing result for {doc_title}: {e}")
                    results.append({
                        'success': False,
                        'processing_result': processing_result,
                        'error': str(e)
                    })
        
        return results
    
    def _validate_single_processing_result(self, processing_result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a single processing result
        
        Args:
            processing_result: Processing result dictionary
            
        Returns:
            Validation result dictionary
        """
        try:
            if not processing_result.get('success'):
                return {
                    'success': False,
                    'processing_result': processing_result,
                    'validation_error': 'Processing failed, cannot validate'
                }
            
            document = processing_result.get('document', {})
            doc_info = document.get('document_info', {})
            standards = processing_result.get('standards', [])
            competencies = processing_result.get('competencies', [])
            
            validation_result = {
                'success': True,
                'processing_result': processing_result,
                'validation_timestamp': datetime.now().isoformat()
            }
            
            # Perform various validation checks
            accuracy_assessment = self._assess_accuracy(processing_result)
            validation_result['accuracy_assessment'] = accuracy_assessment
            
            completeness_check = self._check_data_completeness(processing_result)
            validation_result['completeness_check'] = completeness_check
            
            relevance_scoring = self._score_relevance(processing_result)
            validation_result['relevance_scoring'] = relevance_scoring
            
            authority_verification = self._verify_authority(processing_result)
            validation_result['authority_verification'] = authority_verification
            
            consistency_analysis = self._analyze_data_consistency(processing_result)
            validation_result['consistency_analysis'] = consistency_analysis
            
            # Calculate overall quality score
            overall_score = self._calculate_overall_quality_score(validation_result)
            validation_result['overall_quality_score'] = overall_score
            
            # Determine validation status
            validation_result['validation_passed'] = overall_score >= self.quality_threshold
            
            # Generate quality recommendations
            recommendations = self._generate_quality_recommendations(validation_result)
            validation_result['recommendations'] = recommendations
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Error validating single processing result: {e}")
            return {
                'success': False,
                'processing_result': processing_result,
                'error': str(e)
            }
    
    def _assess_accuracy(self, processing_result: Dict[str, Any]) -> Dict[str, Any]:
        """Assess accuracy of extracted standards and processing
        
        Args:
            processing_result: Processing result to assess
            
        Returns:
            Accuracy assessment results
        """
        try:
            document = processing_result.get('document', {})
            content_info = document.get('content_info', {})
            text_content = content_info.get('text_content', '')
            standards = processing_result.get('standards', [])
            
            # Use LLM to assess accuracy of extracted standards
            accuracy_scores = []
            
            for standard in standards[:10]:  # Validate first 10 standards
                standard_text = standard.get('text', '')
                
                # Check if standard text actually exists in source document
                text_match_score = self._calculate_text_match_score(standard_text, text_content)
                
                # Use LLM to assess semantic accuracy
                llm_accuracy_score = self._assess_standard_accuracy_with_llm(standard, text_content)
                
                combined_score = (text_match_score * 0.4) + (llm_accuracy_score * 0.6)
                accuracy_scores.append(combined_score)
            
            overall_accuracy = statistics.mean(accuracy_scores) if accuracy_scores else 0.0
            
            return {
                'overall_accuracy_score': overall_accuracy,
                'individual_standard_scores': accuracy_scores,
                'standards_assessed': len(accuracy_scores),
                'accuracy_method': 'text_match_and_llm',
                'accuracy_threshold_met': overall_accuracy >= self.accuracy_threshold
            }
            
        except Exception as e:
            self.logger.error(f"Error assessing accuracy: {e}")
            return {
                'overall_accuracy_score': 0.0,
                'error': str(e)
            }
    
    def _calculate_text_match_score(self, standard_text: str, source_text: str) -> float:
        """Calculate how well standard text matches source document
        
        Args:
            standard_text: Extracted standard text
            source_text: Source document text
            
        Returns:
            Match score (0.0 to 1.0)
        """
        if not standard_text or not source_text:
            return 0.0
        
        # Direct substring match
        if standard_text.lower() in source_text.lower():
            return 1.0
        
        # Fuzzy matching using sequence matcher
        if HAS_TEXT_SIMILARITY:
            # Find best matching substring
            best_match_score = 0.0
            standard_len = len(standard_text)
            
            for i in range(len(source_text) - standard_len + 1):
                substring = source_text[i:i + standard_len]
                similarity = SequenceMatcher(None, standard_text.lower(), substring.lower()).ratio()
                best_match_score = max(best_match_score, similarity)
        else:
            # Fallback: simple word overlap
            standard_words = set(standard_text.lower().split())
            source_words = set(source_text.lower().split())
            overlap = len(standard_words.intersection(source_words))
            best_match_score = overlap / max(len(standard_words), 1)
        
        return best_match_score
    
    def _assess_standard_accuracy_with_llm(self, standard: Dict[str, Any], source_text: str) -> float:
        """Use LLM to assess accuracy of extracted standard
        
        Args:
            standard: Standard dictionary
            source_text: Source document text
            
        Returns:
            LLM accuracy score (0.0 to 1.0)
        """
        try:
            standard_text = standard.get('text', '')
            standard_type = standard.get('type', 'unknown')
            
            # Limit source text for LLM analysis
            source_snippet = source_text[:3000]
            
            prompt = f"""
            Assess the accuracy of this extracted educational standard from a {self.discipline} document:
            
            Extracted Standard:
            Text: "{standard_text}"
            Type: {standard_type}
            
            Source Document Context:
            {source_snippet}...
            
            Evaluate:
            1. Does the extracted text accurately represent content from the source?
            2. Is the standard classification (type) appropriate?
            3. Is the extraction complete and not truncated inappropriately?
            4. Does it represent a valid educational standard for {self.discipline}?
            
            Return JSON with:
            - accuracy_score (0.0 to 1.0)
            - text_fidelity (0.0 to 1.0) 
            - classification_accuracy (0.0 to 1.0)
            - completeness_score (0.0 to 1.0)
            - reasoning (brief explanation)
            """
            
            llm_result = self._execute_llm_task(prompt, 'quality_evaluation', 'high')
            
            try:
                assessment = json.loads(llm_result.response)
                return assessment.get('accuracy_score', 0.5)
            except json.JSONDecodeError:
                return 0.5  # Default score if parsing fails
                
        except Exception as e:
            self.logger.error(f"Error in LLM accuracy assessment: {e}")
            return 0.5
    
    def _check_data_completeness(self, processing_result: Dict[str, Any]) -> Dict[str, Any]:
        """Check completeness of extracted data
        
        Args:
            processing_result: Processing result to check
            
        Returns:
            Completeness assessment results
        """
        try:
            document = processing_result.get('document', {})
            standards = processing_result.get('standards', [])
            competencies = processing_result.get('competencies', [])
            semantic_analysis = processing_result.get('semantic_analysis', {})
            
            completeness_checks = {
                'has_extracted_standards': len(standards) > 0,
                'has_competencies': len(competencies) > 0,
                'has_semantic_analysis': bool(semantic_analysis),
                'has_document_metadata': bool(document.get('document_info')),
                'has_content_classification': bool(processing_result.get('content_classification')),
                'standards_have_types': all(s.get('type') for s in standards),
                'standards_have_confidence': all(s.get('confidence') is not None for s in standards)
            }
            
            # Calculate completeness score
            passed_checks = sum(completeness_checks.values())
            total_checks = len(completeness_checks)
            completeness_score = passed_checks / total_checks
            
            # Check discipline-specific requirements
            discipline_completeness = self._check_discipline_specific_completeness(processing_result)
            
            # Combined completeness score
            overall_completeness = (completeness_score * 0.7) + (discipline_completeness * 0.3)
            
            return {
                'overall_completeness_score': overall_completeness,
                'basic_completeness_checks': completeness_checks,
                'discipline_specific_completeness': discipline_completeness,
                'completeness_threshold_met': overall_completeness >= self.completeness_threshold,
                'missing_elements': [k for k, v in completeness_checks.items() if not v]
            }
            
        except Exception as e:
            self.logger.error(f"Error checking completeness: {e}")
            return {
                'overall_completeness_score': 0.0,
                'error': str(e)
            }
    
    def _check_discipline_specific_completeness(self, processing_result: Dict[str, Any]) -> float:
        """Check discipline-specific completeness requirements
        
        Args:
            processing_result: Processing result
            
        Returns:
            Discipline-specific completeness score
        """
        requirements = self.discipline_requirements.get(self.discipline, {})
        
        if not requirements:
            return 0.8  # Default score if no specific requirements
        
        standards = processing_result.get('standards', [])
        competencies = processing_result.get('competencies', [])
        
        score = 0.0
        checks = 0
        
        # Check minimum standards count
        min_standards = requirements.get('min_standards', 1)
        if len(standards) >= min_standards:
            score += 1.0
        checks += 1
        
        # Check for required standard types
        required_types = requirements.get('required_standard_types', [])
        if required_types:
            found_types = set(s.get('type') for s in standards)
            type_coverage = len(found_types.intersection(required_types)) / len(required_types)
            score += type_coverage
            checks += 1
        
        # Check for competency coverage
        if requirements.get('requires_competencies', False):
            if competencies:
                score += 1.0
            checks += 1
        
        return score / max(checks, 1)
    
    def _score_relevance(self, processing_result: Dict[str, Any]) -> Dict[str, Any]:
        """Score relevance of extracted standards to discipline
        
        Args:
            processing_result: Processing result to score
            
        Returns:
            Relevance scoring results
        """
        try:
            document = processing_result.get('document', {})
            doc_info = document.get('document_info', {})
            standards = processing_result.get('standards', [])
            
            # Use LLM to assess relevance
            prompt = f"""
            Assess the relevance of these extracted standards to {self.discipline} education:
            
            Document: {doc_info.get('title', 'Unknown')}
            Source: {doc_info.get('source_url', 'Unknown')}
            
            Extracted Standards:
            {json.dumps([{'text': s.get('text', '')[:200] + '...', 'type': s.get('type')} for s in standards[:10]], indent=2)}
            
            Evaluate:
            1. Overall relevance to {self.discipline} education (0.0 to 1.0)
            2. Standards appropriateness for the discipline
            3. Alignment with typical {self.discipline} curriculum expectations
            4. Quality and specificity of standards for educational use
            
            Return JSON with detailed relevance assessment.
            """
            
            llm_result = self._execute_llm_task(prompt, 'quality_evaluation', 'high')
            
            try:
                relevance_assessment = json.loads(llm_result.response)
                relevance_score = relevance_assessment.get('overall_relevance', 0.5)
            except json.JSONDecodeError:
                relevance_score = 0.5
            
            return {
                'relevance_score': relevance_score,
                'llm_assessment': llm_result.response,
                'relevance_threshold_met': relevance_score >= 0.6,
                'tokens_used': llm_result.tokens_used,
                'cost': llm_result.cost
            }
            
        except Exception as e:
            self.logger.error(f"Error scoring relevance: {e}")
            return {
                'relevance_score': 0.5,
                'error': str(e)
            }
    
    def _verify_authority(self, processing_result: Dict[str, Any]) -> Dict[str, Any]:
        """Verify authority and credibility of source document
        
        Args:
            processing_result: Processing result to verify
            
        Returns:
            Authority verification results
        """
        try:
            document = processing_result.get('document', {})
            doc_info = document.get('document_info', {})
            source_url = doc_info.get('source_url', '')
            
            authority_indicators = {
                'government_source': '.gov' in source_url.lower(),
                'educational_institution': '.edu' in source_url.lower(),
                'professional_organization': any(org in source_url.lower() for org in ['acm', 'ieee', 'nctm', 'nsta', 'abet']),
                'recognized_standards_body': any(body in source_url.lower() for body in ['iso', 'ansi', 'standards']),
                'international_organization': any(org in source_url.lower() for org in ['unesco', 'oecd', 'who'])
            }
            
            authority_score = sum(authority_indicators.values()) / len(authority_indicators)
            
            # Use LLM for additional authority assessment
            llm_authority_assessment = self._assess_authority_with_llm(doc_info)
            
            # Combine scores
            combined_authority_score = (authority_score * 0.4) + (llm_authority_assessment * 0.6)
            
            return {
                'authority_score': combined_authority_score,
                'authority_indicators': authority_indicators,
                'llm_authority_assessment': llm_authority_assessment,
                'authority_threshold_met': combined_authority_score >= 0.5
            }
            
        except Exception as e:
            self.logger.error(f"Error verifying authority: {e}")
            return {
                'authority_score': 0.5,
                'error': str(e)
            }
    
    def _assess_authority_with_llm(self, doc_info: Dict[str, Any]) -> float:
        """Use LLM to assess document authority
        
        Args:
            doc_info: Document information
            
        Returns:
            LLM authority score (0.0 to 1.0)
        """
        try:
            prompt = f"""
            Assess the authority and credibility of this educational standards source:
            
            Title: {doc_info.get('title', 'Unknown')}
            Source URL: {doc_info.get('source_url', 'Unknown')}
            Document Type: {doc_info.get('type', 'unknown')}
            
            Evaluate authority based on:
            1. Source organization credibility
            2. Official/governmental nature
            3. Professional recognition
            4. Academic/educational authority
            5. Standards body recognition
            
            Return authority score (0.0 to 1.0) where:
            - 1.0 = Highly authoritative (government, major standards bodies)
            - 0.8 = Very credible (recognized professional organizations)
            - 0.6 = Moderately credible (educational institutions)
            - 0.4 = Limited credibility (commercial/informal sources)
            - 0.2 = Low credibility (unverified sources)
            
            Return just the numeric score.
            """
            
            llm_result = self._execute_llm_task(prompt, 'quality_evaluation', 'standard')
            
            try:
                # Extract numeric score from response
                score_match = re.search(r'(\d+\.?\d*)', llm_result.response)
                if score_match:
                    score = float(score_match.group(1))
                    return min(max(score, 0.0), 1.0)  # Clamp to 0.0-1.0
                else:
                    return 0.5
            except:
                return 0.5
                
        except Exception as e:
            self.logger.error(f"Error in LLM authority assessment: {e}")
            return 0.5
    
    def _analyze_data_consistency(self, processing_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze consistency of extracted data
        
        Args:
            processing_result: Processing result to analyze
            
        Returns:
            Consistency analysis results
        """
        try:
            standards = processing_result.get('standards', [])
            competencies = processing_result.get('competencies', [])
            
            consistency_checks = {
                'standards_format_consistency': self._check_standards_format_consistency(standards),
                'competency_format_consistency': self._check_competency_format_consistency(competencies),
                'terminology_consistency': self._check_terminology_consistency(standards + competencies),
                'classification_consistency': self._check_classification_consistency(standards)
            }
            
            overall_consistency = statistics.mean(consistency_checks.values())
            
            return {
                'overall_consistency_score': overall_consistency,
                'consistency_checks': consistency_checks,
                'consistency_threshold_met': overall_consistency >= 0.7
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing consistency: {e}")
            return {
                'overall_consistency_score': 0.5,
                'error': str(e)
            }
    
    def _check_standards_format_consistency(self, standards: List[Dict[str, Any]]) -> float:
        """Check format consistency across extracted standards"""
        if not standards:
            return 1.0
        
        # Check for consistent required fields
        required_fields = ['text', 'type']
        field_consistency_scores = []
        
        for field in required_fields:
            field_present_count = sum(1 for s in standards if s.get(field))
            consistency = field_present_count / len(standards)
            field_consistency_scores.append(consistency)
        
        return statistics.mean(field_consistency_scores)
    
    def _check_competency_format_consistency(self, competencies: List[Dict[str, Any]]) -> float:
        """Check format consistency across extracted competencies"""
        if not competencies:
            return 1.0
        
        # Check for consistent categorization
        has_category = sum(1 for c in competencies if c.get('category'))
        return has_category / len(competencies)
    
    def _check_terminology_consistency(self, items: List[Dict[str, Any]]) -> float:
        """Check terminology consistency across extracted items"""
        if not items:
            return 1.0
        
        # Simple check for consistent terminology patterns
        text_items = [item.get('text', '') for item in items if item.get('text')]
        
        if not text_items:
            return 1.0
        
        # Check for consistent verb usage patterns (simplified)
        action_verbs = ['demonstrate', 'apply', 'understand', 'analyze', 'evaluate', 'create']
        verb_usage = [any(verb in text.lower() for verb in action_verbs) for text in text_items]
        
        return sum(verb_usage) / len(verb_usage) if verb_usage else 1.0
    
    def _check_classification_consistency(self, standards: List[Dict[str, Any]]) -> float:
        """Check classification consistency across standards"""
        if not standards:
            return 1.0
        
        types = [s.get('type') for s in standards if s.get('type')]
        
        if not types:
            return 0.5
        
        # Check for reasonable distribution of types
        type_counts = Counter(types)
        
        # Penalize if all standards have same type (likely over-generalized)
        if len(type_counts) == 1 and len(standards) > 5:
            return 0.6
        
        return 1.0  # Good variety in classification
    
    def _calculate_overall_quality_score(self, validation_result: Dict[str, Any]) -> float:
        """Calculate overall quality score from validation components
        
        Args:
            validation_result: Validation result dictionary
            
        Returns:
            Overall quality score (0.0 to 1.0)
        """
        try:
            scores = {
                'accuracy': validation_result.get('accuracy_assessment', {}).get('overall_accuracy_score', 0.0),
                'completeness': validation_result.get('completeness_check', {}).get('overall_completeness_score', 0.0),
                'relevance': validation_result.get('relevance_scoring', {}).get('relevance_score', 0.0),
                'authority': validation_result.get('authority_verification', {}).get('authority_score', 0.0),
                'consistency': validation_result.get('consistency_analysis', {}).get('overall_consistency_score', 0.0)
            }
            
            # Calculate weighted average
            weighted_sum = sum(score * self.validation_weights[component] 
                             for component, score in scores.items())
            
            return weighted_sum
            
        except Exception as e:
            self.logger.error(f"Error calculating overall quality score: {e}")
            return 0.0
    
    def _generate_quality_recommendations(self, validation_result: Dict[str, Any]) -> List[str]:
        """Generate quality improvement recommendations
        
        Args:
            validation_result: Validation result dictionary
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Check each validation component
        accuracy = validation_result.get('accuracy_assessment', {}).get('overall_accuracy_score', 0.0)
        if accuracy < 0.7:
            recommendations.append("Improve accuracy: Review extraction methods and validate against source documents")
        
        completeness = validation_result.get('completeness_check', {}).get('overall_completeness_score', 0.0)
        if completeness < 0.8:
            missing = validation_result.get('completeness_check', {}).get('missing_elements', [])
            recommendations.append(f"Improve completeness: Address missing elements - {', '.join(missing)}")
        
        relevance = validation_result.get('relevance_scoring', {}).get('relevance_score', 0.0)
        if relevance < 0.6:
            recommendations.append(f"Improve relevance: Ensure extracted standards are specific to {self.discipline}")
        
        authority = validation_result.get('authority_verification', {}).get('authority_score', 0.0)
        if authority < 0.5:
            recommendations.append("Improve authority: Prioritize sources from government, educational institutions, or professional organizations")
        
        consistency = validation_result.get('consistency_analysis', {}).get('overall_consistency_score', 0.0)
        if consistency < 0.7:
            recommendations.append("Improve consistency: Standardize extraction formats and classification schemes")
        
        return recommendations
    
    def _perform_aggregate_validation(self, validation_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform aggregate validation analysis across all results
        
        Args:
            validation_results: List of validation results
            
        Returns:
            Aggregate validation analysis
        """
        successful_validations = [r for r in validation_results if r.get('success')]
        
        if not successful_validations:
            return {'error': 'No successful validations to aggregate'}
        
        # Calculate aggregate scores
        quality_scores = [r.get('overall_quality_score', 0.0) for r in successful_validations]
        
        aggregate_analysis = {
            'total_documents_validated': len(validation_results),
            'successful_validations': len(successful_validations),
            'validation_success_rate': len(successful_validations) / len(validation_results),
            'overall_quality_score': statistics.mean(quality_scores) if quality_scores else 0.0,
            'quality_score_distribution': {
                'min': min(quality_scores) if quality_scores else 0.0,
                'max': max(quality_scores) if quality_scores else 0.0,
                'median': statistics.median(quality_scores) if quality_scores else 0.0,
                'std_dev': statistics.stdev(quality_scores) if len(quality_scores) > 1 else 0.0
            },
            'documents_meeting_threshold': len([s for s in quality_scores if s >= self.quality_threshold]),
            'threshold_compliance_rate': len([s for s in quality_scores if s >= self.quality_threshold]) / len(quality_scores) if quality_scores else 0.0
        }
        
        return aggregate_analysis
    
    def _generate_validation_report(self, validation_results: List[Dict[str, Any]], 
                                  aggregate_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive validation report
        
        Args:
            validation_results: List of validation results
            aggregate_analysis: Aggregate analysis results
            
        Returns:
            Validation report dictionary
        """
        return {
            'report_metadata': {
                'discipline': self.discipline,
                'validation_timestamp': datetime.now().isoformat(),
                'agent_id': self.agent_id,
                'quality_threshold': self.quality_threshold
            },
            'summary': {
                'documents_processed': len(validation_results),
                'overall_quality_score': aggregate_analysis.get('overall_quality_score', 0.0),
                'threshold_compliance_rate': aggregate_analysis.get('threshold_compliance_rate', 0.0),
                'validation_passed': aggregate_analysis.get('overall_quality_score', 0.0) >= self.quality_threshold
            },
            'detailed_analysis': aggregate_analysis,
            'quality_distribution': aggregate_analysis.get('quality_score_distribution', {}),
            'common_issues': self._identify_common_issues(validation_results),
            'recommendations': self._generate_aggregate_recommendations(validation_results),
            'validation_statistics': self._calculate_validation_statistics(validation_results)
        }
    
    def _identify_common_issues(self, validation_results: List[Dict[str, Any]]) -> List[str]:
        """Identify common quality issues across validation results"""
        issue_counts = defaultdict(int)
        
        for result in validation_results:
            if result.get('success'):
                recommendations = result.get('recommendations', [])
                for rec in recommendations:
                    issue_type = rec.split(':')[0] if ':' in rec else rec
                    issue_counts[issue_type] += 1
        
        # Return most common issues
        common_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)
        return [f"{issue}: {count} documents" for issue, count in common_issues[:5]]
    
    def _generate_aggregate_recommendations(self, validation_results: List[Dict[str, Any]]) -> List[str]:
        """Generate aggregate recommendations for quality improvement"""
        recommendations = set()
        
        for result in validation_results:
            if result.get('success'):
                result_recommendations = result.get('recommendations', [])
                recommendations.update(result_recommendations)
        
        return list(recommendations)[:10]  # Top 10 recommendations
    
    def _calculate_validation_statistics(self, validation_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate detailed validation statistics"""
        successful_results = [r for r in validation_results if r.get('success')]
        
        if not successful_results:
            return {}
        
        # Component score statistics
        component_stats = {}
        components = ['accuracy_assessment', 'completeness_check', 'relevance_scoring', 
                     'authority_verification', 'consistency_analysis']
        
        for component in components:
            scores = []
            for result in successful_results:
                component_data = result.get(component, {})
                if component == 'accuracy_assessment':
                    score = component_data.get('overall_accuracy_score', 0.0)
                elif component == 'completeness_check':
                    score = component_data.get('overall_completeness_score', 0.0)
                elif component == 'relevance_scoring':
                    score = component_data.get('relevance_score', 0.0)
                elif component == 'authority_verification':
                    score = component_data.get('authority_score', 0.0)
                elif component == 'consistency_analysis':
                    score = component_data.get('overall_consistency_score', 0.0)
                else:
                    score = 0.0
                scores.append(score)
            
            if scores:
                component_stats[component] = {
                    'mean': statistics.mean(scores),
                    'median': statistics.median(scores),
                    'min': min(scores),
                    'max': max(scores),
                    'std_dev': statistics.stdev(scores) if len(scores) > 1 else 0.0
                }
        
        return component_stats
    
    def _save_validation_report(self, validation_report: Dict[str, Any]):
        """Save validation report to file
        
        Args:
            validation_report: Validation report to save
        """
        try:
            filename = f"validation_report_{self.discipline}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            file_path = self.validation_dir / filename
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(validation_report, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"Saved validation report: {filename}")
            
        except Exception as e:
            self.logger.error(f"Error saving validation report: {e}")
    
    def _initialize_quality_criteria(self) -> Dict[str, Any]:
        """Initialize quality assessment criteria"""
        return {
            'accuracy': {
                'text_match_weight': 0.4,
                'semantic_accuracy_weight': 0.6,
                'minimum_threshold': 0.7
            },
            'completeness': {
                'basic_elements_weight': 0.7,
                'discipline_specific_weight': 0.3,
                'minimum_threshold': 0.8
            },
            'relevance': {
                'discipline_alignment_weight': 1.0,
                'minimum_threshold': 0.6
            },
            'authority': {
                'source_credibility_weight': 0.6,
                'llm_assessment_weight': 0.4,
                'minimum_threshold': 0.5
            },
            'consistency': {
                'format_consistency_weight': 0.4,
                'terminology_consistency_weight': 0.6,
                'minimum_threshold': 0.7
            }
        }
    
    def _load_discipline_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Load discipline-specific validation requirements"""
        return {
            'Mathematics': {
                'min_standards': 3,
                'required_standard_types': ['competency', 'learning_objective'],
                'requires_competencies': True
            },
            'Computer_Science': {
                'min_standards': 2,
                'required_standard_types': ['competency', 'skill_requirement'],
                'requires_competencies': True
            },
            'Physical_Sciences': {
                'min_standards': 2,
                'required_standard_types': ['learning_objective', 'competency'],
                'requires_competencies': False
            },
            'Engineering': {
                'min_standards': 3,
                'required_standard_types': ['competency', 'accreditation_criterion'],
                'requires_competencies': True
            }
        }
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get summary of validation results for this agent
        
        Returns:
            Validation summary dictionary
        """
        return {
            'agent_id': self.agent_id,
            'discipline': self.discipline,
            'documents_validated': len(self.validated_documents.get(self.discipline, [])),
            'validation_reports_generated': len(self.validation_reports.get(self.discipline, [])),
            'quality_threshold': self.quality_threshold,
            'validation_directory': str(self.validation_dir),
            'last_validation': self.performance_stats.get('last_activity'),
            'total_validation_tasks': self.performance_stats.get('tasks_completed', 0)
        }
    
    def __del__(self):
        """Cleanup when validation agent is destroyed"""
        super().__del__()