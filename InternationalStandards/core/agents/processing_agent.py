#!/usr/bin/env python3
"""
Processing Agent for International Standards Retrieval System

Specialized agent for autonomous processing and semantic analysis of retrieved
educational standards documents across 19 OpenAlex disciplines. Handles content
classification, standards extraction, and competency mapping.

Author: Autonomous AI Development System
"""

import json
import re
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime, timedelta
from pathlib import Path
import hashlib
from collections import defaultdict, Counter
import concurrent.futures
import threading

# NLP libraries (optional)
try:
    import nltk
    from nltk.tokenize import sent_tokenize, word_tokenize
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer
    HAS_NLTK = True
except ImportError:
    HAS_NLTK = False

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

from .base_agent import BaseAgent, AgentStatus
from ..llm_integration import TaskResult

class ProcessingAgent(BaseAgent):
    """Agent specialized for standards document processing and analysis"""
    
    def __init__(self, agent_id: str, discipline: str, config: Dict[str, Any], 
                 llm_integration, config_manager):
        """Initialize processing agent
        
        Args:
            agent_id: Unique agent identifier
            discipline: Academic discipline focus
            config: Agent configuration
            llm_integration: LLM integration instance
            config_manager: Configuration manager instance
        """
        super().__init__(agent_id, 'processing', discipline, config, llm_integration)
        
        self.config_manager = config_manager
        
        # Processing-specific settings
        self.max_concurrent_processing = config.get('max_concurrent_processing', 3)
        self.chunk_size = config.get('chunk_size', 2000)  # Characters per chunk
        self.min_standard_length = config.get('min_standard_length', 50)
        self.competency_extraction_enabled = config.get('competency_extraction', True)
        
        # Storage configuration
        self.data_dir = Path(config.get('data_directory', 'data'))
        self.processed_dir = self.data_dir / 'processed' / discipline
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        
        # Processing tracking
        self.processed_documents = {}
        self.extracted_standards = {}
        self.competency_maps = {}
        self.processing_queue = []
        
        # Standards taxonomy and patterns
        self.standards_patterns = self._initialize_standards_patterns()
        self.competency_patterns = self._initialize_competency_patterns()
        
        # NLP components
        self.nlp_tools = self._initialize_nlp_tools()
        
        # Processing locks for thread safety
        self.processing_lock = threading.Lock()
        
        self.logger.info(f"Processing agent initialized for discipline: {discipline}")
    
    def _initialize_llm_task_types(self) -> Dict[str, str]:
        """Initialize LLM task type mappings for processing operations"""
        return {
            'standards_extraction': 'information_extraction',
            'competency_mapping': 'classification',
            'content_structuring': 'content_analysis',
            'quality_assessment': 'quality_evaluation',
            'semantic_analysis': 'content_analysis',
            'taxonomy_classification': 'classification'
        }
    
    def _process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process document processing task
        
        Args:
            task: Task dictionary with processing parameters
            
        Returns:
            Processing results dictionary
        """
        task_type = task.get('type', 'process_documents')
        
        try:
            # Handle main processing task type from orchestrator
            if task_type == 'processing' or task_type == 'process_documents':
                return self._process_documents(task)
            elif task_type == 'extract_standards':
                return self._extract_standards_from_document(task)
            elif task_type == 'map_competencies':
                return self._map_document_competencies(task)
            elif task_type == 'classify_content':
                return self._classify_document_content(task)
            elif task_type == 'semantic_analysis':
                return self._perform_semantic_analysis(task)
            else:
                raise ValueError(f"Unknown processing task type: {task_type}")
                
        except Exception as e:
            self.logger.error(f"Error processing task: {e}")
            return {
                'success': False,
                'error': str(e),
                'task_id': task.get('task_id'),
                'discipline': self.discipline
            }
    
    def _process_documents(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process multiple retrieved documents
        
        Args:
            task: Task parameters with document list
            
        Returns:
            Processing results
        """
        self.logger.info(f"Starting document processing for {self.discipline}")
        
        documents = task.get('documents', [])
        processing_results = []
        
        try:
            # Process documents in batches for concurrent processing
            batch_size = self.max_concurrent_processing
            
            for i in range(0, len(documents), batch_size):
                batch_documents = documents[i:i + batch_size]
                batch_results = self._process_document_batch(batch_documents)
                processing_results.extend(batch_results)
            
            # Aggregate processing results
            aggregated_results = self._aggregate_processing_results(processing_results)
            
            result = {
                'success': True,
                'task_id': task.get('task_id'),
                'discipline': self.discipline,
                'documents_processed': len([r for r in processing_results if r.get('success')]),
                'documents_failed': len([r for r in processing_results if not r.get('success')]),
                'extracted_standards_count': sum(len(r.get('standards', [])) for r in processing_results if r.get('success')),
                'processing_results': processing_results,
                'aggregated_analysis': aggregated_results,
                'processing_timestamp': datetime.now().isoformat()
            }
            
            # Store results for future reference
            self.processed_documents[self.discipline] = processing_results
            
            self.logger.info(f"Document processing completed: {len(processing_results)} documents processed")
            return result
            
        except Exception as e:
            self.logger.error(f"Error in document processing: {e}")
            return {
                'success': False,
                'error': str(e),
                'task_id': task.get('task_id'),
                'discipline': self.discipline
            }
    
    def _process_document_batch(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process a batch of documents concurrently
        
        Args:
            documents: List of document dictionaries
            
        Returns:
            List of processing results
        """
        results = []
        
        # Use ThreadPoolExecutor for concurrent processing
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_concurrent_processing) as executor:
            # Submit all processing tasks
            future_to_doc = {
                executor.submit(self._process_single_document, doc): doc 
                for doc in documents
            }
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_doc):
                doc = future_to_doc[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    self.logger.error(f"Error processing document {doc.get('document_info', {}).get('title', 'unknown')}: {e}")
                    results.append({
                        'success': False,
                        'document': doc,
                        'error': str(e)
                    })
        
        return results
    
    def _process_single_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single document for standards extraction and analysis
        
        Args:
            document: Document information dictionary
            
        Returns:
            Processing result dictionary
        """
        try:
            doc_info = document.get('document_info', {})
            content_info = document.get('content_info', {})
            text_content = content_info.get('text_content', '')
            
            if not text_content.strip():
                return {
                    'success': False,
                    'document': document,
                    'error': 'No text content available for processing'
                }
            
            processing_result = {
                'success': True,
                'document': document,
                'processing_timestamp': datetime.now().isoformat()
            }
            
            # Extract standards from document
            standards_extraction = self._extract_standards_from_text(text_content, doc_info)
            processing_result['standards'] = standards_extraction.get('standards', [])
            processing_result['standards_metadata'] = standards_extraction.get('metadata', {})
            
            # Map competencies if enabled
            if self.competency_extraction_enabled:
                competency_mapping = self._extract_competencies_from_text(text_content, doc_info)
                processing_result['competencies'] = competency_mapping.get('competencies', [])
                processing_result['competency_metadata'] = competency_mapping.get('metadata', {})
            
            # Classify content structure
            content_classification = self._classify_content_structure(text_content, doc_info)
            processing_result['content_classification'] = content_classification
            
            # Perform semantic analysis using LLM
            semantic_analysis = self._perform_llm_semantic_analysis(text_content, doc_info)
            processing_result['semantic_analysis'] = semantic_analysis
            
            # Save processed results to file
            self._save_processed_document(processing_result, doc_info)
            
            return processing_result
            
        except Exception as e:
            self.logger.error(f"Error processing single document: {e}")
            return {
                'success': False,
                'document': document,
                'error': str(e)
            }
    
    def _extract_standards_from_text(self, text_content: str, doc_info: Dict[str, Any]) -> Dict[str, Any]:
        """Extract educational standards from text content
        
        Args:
            text_content: Document text content
            doc_info: Document information
            
        Returns:
            Standards extraction results
        """
        try:
            extracted_standards = []
            
            # Use pattern-based extraction first
            pattern_standards = self._extract_standards_by_patterns(text_content)
            extracted_standards.extend(pattern_standards)
            
            # Use LLM for advanced standards extraction
            llm_standards = self._extract_standards_with_llm(text_content, doc_info)
            extracted_standards.extend(llm_standards)
            
            # Deduplicate and validate standards
            unique_standards = self._deduplicate_standards(extracted_standards)
            validated_standards = self._validate_extracted_standards(unique_standards)
            
            return {
                'standards': validated_standards,
                'metadata': {
                    'extraction_methods': ['patterns', 'llm'],
                    'total_raw_extractions': len(extracted_standards),
                    'unique_standards': len(unique_standards),
                    'validated_standards': len(validated_standards),
                    'extraction_timestamp': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting standards: {e}")
            return {
                'standards': [],
                'metadata': {'error': str(e)}
            }
    
    def _extract_standards_by_patterns(self, text_content: str) -> List[Dict[str, Any]]:
        """Extract standards using regex patterns
        
        Args:
            text_content: Text content to analyze
            
        Returns:
            List of extracted standards
        """
        extracted_standards = []
        
        # Get discipline-specific patterns
        patterns = self.standards_patterns.get(self.discipline, self.standards_patterns.get('default', []))
        
        for pattern_info in patterns:
            pattern = pattern_info['pattern']
            standard_type = pattern_info['type']
            
            matches = re.finditer(pattern, text_content, re.IGNORECASE | re.MULTILINE)
            
            for match in matches:
                standard_text = match.group().strip()
                
                if len(standard_text) >= self.min_standard_length:
                    extracted_standards.append({
                        'text': standard_text,
                        'type': standard_type,
                        'extraction_method': 'pattern',
                        'pattern_matched': pattern_info['name'],
                        'position': match.start(),
                        'confidence': pattern_info.get('confidence', 0.7)
                    })
        
        return extracted_standards
    
    def _extract_standards_with_llm(self, text_content: str, doc_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract standards using LLM analysis
        
        Args:
            text_content: Text content to analyze
            doc_info: Document information
            
        Returns:
            List of extracted standards
        """
        try:
            # Chunk text for LLM processing
            text_chunks = self._chunk_text_for_llm(text_content)
            
            extracted_standards = []
            
            for i, chunk in enumerate(text_chunks[:5]):  # Process first 5 chunks
                prompt = f"""
                Extract educational standards from this {self.discipline} document chunk:
                
                Document: {doc_info.get('title', 'Unknown')}
                Chunk {i+1}/{len(text_chunks)}:
                
                {chunk}
                
                Extract:
                1. Learning objectives and outcomes
                2. Competency requirements
                3. Performance indicators
                4. Assessment criteria
                5. Curriculum standards
                6. Knowledge and skill requirements
                
                For each standard found, provide:
                - Standard text (exact quote)
                - Standard type (objective, competency, indicator, criterion, requirement)
                - Subject area within {self.discipline}
                - Education level (if identifiable)
                - Confidence score (0.0 to 1.0)
                
                Return JSON array of standards found.
                """
                
                llm_result = self._execute_llm_task(prompt, 'information_extraction', 'high')
                
                try:
                    chunk_standards = json.loads(llm_result.response)
                    if isinstance(chunk_standards, list):
                        for standard in chunk_standards:
                            standard.update({
                                'extraction_method': 'llm',
                                'chunk_index': i,
                                'llm_tokens_used': llm_result.tokens_used,
                                'llm_cost': llm_result.cost
                            })
                        extracted_standards.extend(chunk_standards)
                except json.JSONDecodeError:
                    self.logger.warning(f"Failed to parse LLM response for chunk {i}")
            
            return extracted_standards
            
        except Exception as e:
            self.logger.error(f"Error in LLM standards extraction: {e}")
            return []
    
    def _extract_competencies_from_text(self, text_content: str, doc_info: Dict[str, Any]) -> Dict[str, Any]:
        """Extract competencies and learning outcomes from text
        
        Args:
            text_content: Document text content
            doc_info: Document information
            
        Returns:
            Competency extraction results
        """
        try:
            # Use LLM to extract and map competencies
            prompt = f"""
            Analyze this {self.discipline} educational document and extract competencies:
            
            Document: {doc_info.get('title', 'Unknown')}
            Content: {text_content[:3000]}...
            
            Extract and categorize competencies:
            1. Knowledge competencies (what students should know)
            2. Skill competencies (what students should be able to do)
            3. Attitude competencies (values and dispositions)
            4. Cognitive levels (remembering, understanding, applying, analyzing, evaluating, creating)
            
            For each competency:
            - Competency statement
            - Category (knowledge/skill/attitude)
            - Cognitive level (Bloom's taxonomy)
            - Subject area within {self.discipline}
            - Education level if identifiable
            - Associated assessment methods if mentioned
            
            Return JSON format with structured competency mapping.
            """
            
            llm_result = self._execute_llm_task(prompt, 'classification', 'high')
            
            try:
                competencies_data = json.loads(llm_result.response)
            except json.JSONDecodeError:
                competencies_data = {'competencies': [], 'error': 'LLM response parsing failed'}
            
            return {
                'competencies': competencies_data.get('competencies', []),
                'metadata': {
                    'extraction_method': 'llm',
                    'llm_tokens_used': llm_result.tokens_used,
                    'llm_cost': llm_result.cost,
                    'extraction_timestamp': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting competencies: {e}")
            return {
                'competencies': [],
                'metadata': {'error': str(e)}
            }
    
    def _classify_content_structure(self, text_content: str, doc_info: Dict[str, Any]) -> Dict[str, Any]:
        """Classify the structure and organization of document content
        
        Args:
            text_content: Document text content
            doc_info: Document information
            
        Returns:
            Content classification results
        """
        try:
            # Analyze document structure
            structure_analysis = {
                'document_length': len(text_content),
                'word_count': len(text_content.split()),
                'paragraph_count': len(text_content.split('\n\n')),
                'section_headers': self._extract_section_headers(text_content),
                'document_type': self._classify_document_type(text_content, doc_info),
                'content_organization': self._analyze_content_organization(text_content)
            }
            
            return structure_analysis
            
        except Exception as e:
            self.logger.error(f"Error classifying content structure: {e}")
            return {'error': str(e)}
    
    def _perform_llm_semantic_analysis(self, text_content: str, doc_info: Dict[str, Any]) -> Dict[str, Any]:
        """Perform semantic analysis using LLM
        
        Args:
            text_content: Document text content
            doc_info: Document information
            
        Returns:
            Semantic analysis results
        """
        try:
            # Limit content for LLM analysis
            analysis_content = text_content[:4000]
            
            prompt = f"""
            Perform semantic analysis of this {self.discipline} educational standards document:
            
            Document: {doc_info.get('title', 'Unknown')}
            Type: {doc_info.get('type', 'unknown')}
            
            Content:
            {analysis_content}
            
            Analyze:
            1. Main themes and topics covered
            2. Educational philosophy and approach
            3. Target audience and education level
            4. Key terminology and vocabulary
            5. Relationships between concepts
            6. Pedagogical frameworks referenced
            7. Assessment approaches mentioned
            8. Implementation guidance provided
            
            Provide structured analysis with:
            - Theme extraction with importance scores
            - Concept relationships and hierarchies
            - Educational level classification
            - Implementation complexity assessment
            - Quality and comprehensiveness rating
            
            Return detailed JSON analysis.
            """
            
            llm_result = self._execute_llm_task(prompt, 'content_analysis', 'high')
            
            try:
                semantic_analysis = json.loads(llm_result.response)
            except json.JSONDecodeError:
                semantic_analysis = {
                    'analysis': 'LLM response parsing failed',
                    'raw_response': llm_result.response
                }
            
            semantic_analysis.update({
                'llm_tokens_used': llm_result.tokens_used,
                'llm_cost': llm_result.cost,
                'analysis_timestamp': datetime.now().isoformat()
            })
            
            return semantic_analysis
            
        except Exception as e:
            self.logger.error(f"Error in semantic analysis: {e}")
            return {'error': str(e)}
    
    def _chunk_text_for_llm(self, text_content: str) -> List[str]:
        """Chunk text content for LLM processing
        
        Args:
            text_content: Text to chunk
            
        Returns:
            List of text chunks
        """
        chunks = []
        
        # Split by paragraphs first
        paragraphs = text_content.split('\n\n')
        
        current_chunk = ""
        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) > self.chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = paragraph
                else:
                    # Single paragraph is too long, split by sentences
                    sentences = paragraph.split('. ')
                    for sentence in sentences:
                        if len(current_chunk) + len(sentence) > self.chunk_size:
                            if current_chunk:
                                chunks.append(current_chunk.strip())
                                current_chunk = sentence
            else:
                current_chunk += "\n\n" + paragraph if current_chunk else paragraph
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _deduplicate_standards(self, standards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate standards based on text similarity
        
        Args:
            standards: List of extracted standards
            
        Returns:
            Deduplicated standards list
        """
        if not standards:
            return []
        
        unique_standards = []
        seen_texts = set()
        
        for standard in standards:
            standard_text = standard.get('text', '').strip().lower()
            
            # Create a normalized version for comparison
            normalized_text = re.sub(r'\s+', ' ', standard_text)
            text_hash = hashlib.md5(normalized_text.encode()).hexdigest()
            
            if text_hash not in seen_texts:
                seen_texts.add(text_hash)
                unique_standards.append(standard)
        
        return unique_standards
    
    def _validate_extracted_standards(self, standards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate and filter extracted standards
        
        Args:
            standards: List of standards to validate
            
        Returns:
            Validated standards list
        """
        validated_standards = []
        
        for standard in standards:
            standard_text = standard.get('text', '')
            
            # Basic validation criteria
            if (len(standard_text) >= self.min_standard_length and
                len(standard_text.split()) >= 5 and  # At least 5 words
                standard.get('confidence', 0) >= 0.3):  # Minimum confidence
                
                validated_standards.append(standard)
        
        return validated_standards
    
    def _extract_section_headers(self, text_content: str) -> List[str]:
        """Extract section headers from document
        
        Args:
            text_content: Document text
            
        Returns:
            List of section headers
        """
        headers = []
        
        # Common header patterns
        header_patterns = [
            r'^[A-Z][A-Z\s]{10,}$',  # ALL CAPS headers
            r'^\d+\.\s+[A-Z][^.]+$',  # Numbered headers
            r'^\w+\s+\d+[:\.]?\s+[A-Z][^.]+$',  # Chapter/Section headers
            r'^[A-Z][^.]{20,}:$',  # Headers ending with colon
        ]
        
        lines = text_content.split('\n')
        
        for line in lines:
            line = line.strip()
            if line:
                for pattern in header_patterns:
                    if re.match(pattern, line):
                        headers.append(line)
                        break
        
        return headers[:20]  # Limit to first 20 headers
    
    def _classify_document_type(self, text_content: str, doc_info: Dict[str, Any]) -> str:
        """Classify the type of educational document
        
        Args:
            text_content: Document content
            doc_info: Document information
            
        Returns:
            Document type classification
        """
        content_lower = text_content.lower()
        title_lower = doc_info.get('title', '').lower()
        
        # Check for document type indicators
        if any(term in content_lower or term in title_lower for term in ['standard', 'standards']):
            return 'standards_document'
        elif any(term in content_lower or term in title_lower for term in ['curriculum', 'course', 'syllabus']):
            return 'curriculum_guide'
        elif any(term in content_lower or term in title_lower for term in ['assessment', 'evaluation', 'test']):
            return 'assessment_framework'
        elif any(term in content_lower or term in title_lower for term in ['accreditation', 'certification']):
            return 'accreditation_criteria'
        elif any(term in content_lower or term in title_lower for term in ['guideline', 'guidance', 'recommendation']):
            return 'guidance_document'
        else:
            return 'general_educational'
    
    def _analyze_content_organization(self, text_content: str) -> Dict[str, Any]:
        """Analyze how content is organized in the document
        
        Args:
            text_content: Document content
            
        Returns:
            Content organization analysis
        """
        return {
            'has_table_of_contents': 'table of contents' in text_content.lower() or 'contents' in text_content.lower()[:1000],
            'has_numbered_sections': bool(re.search(r'\n\d+\.\s+[A-Z]', text_content)),
            'has_bullet_points': '•' in text_content or '*' in text_content,
            'has_appendices': 'appendix' in text_content.lower(),
            'has_references': any(term in text_content.lower() for term in ['references', 'bibliography', 'citations']),
            'average_paragraph_length': self._calculate_average_paragraph_length(text_content)
        }
    
    def _calculate_average_paragraph_length(self, text_content: str) -> float:
        """Calculate average paragraph length
        
        Args:
            text_content: Document content
            
        Returns:
            Average paragraph length in words
        """
        paragraphs = [p.strip() for p in text_content.split('\n\n') if p.strip()]
        if not paragraphs:
            return 0.0
        
        total_words = sum(len(p.split()) for p in paragraphs)
        return total_words / len(paragraphs)
    
    def _aggregate_processing_results(self, processing_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate results from multiple document processing operations
        
        Args:
            processing_results: List of processing results
            
        Returns:
            Aggregated analysis results
        """
        successful_results = [r for r in processing_results if r.get('success')]
        
        if not successful_results:
            return {'error': 'No successful processing results to aggregate'}
        
        # Aggregate standards
        all_standards = []
        for result in successful_results:
            all_standards.extend(result.get('standards', []))
        
        # Aggregate competencies
        all_competencies = []
        for result in successful_results:
            all_competencies.extend(result.get('competencies', []))
        
        # Count document types
        document_types = Counter()
        for result in successful_results:
            doc_type = result.get('content_classification', {}).get('document_type', 'unknown')
            document_types[doc_type] += 1
        
        return {
            'total_standards_extracted': len(all_standards),
            'total_competencies_extracted': len(all_competencies),
            'document_type_distribution': dict(document_types),
            'standards_by_type': self._categorize_standards_by_type(all_standards),
            'competencies_by_category': self._categorize_competencies(all_competencies),
            'processing_success_rate': len(successful_results) / len(processing_results),
            'aggregation_timestamp': datetime.now().isoformat()
        }
    
    def _categorize_standards_by_type(self, standards: List[Dict[str, Any]]) -> Dict[str, int]:
        """Categorize standards by type
        
        Args:
            standards: List of standards
            
        Returns:
            Standards categorized by type
        """
        categories = Counter()
        for standard in standards:
            standard_type = standard.get('type', 'unknown')
            categories[standard_type] += 1
        return dict(categories)
    
    def _categorize_competencies(self, competencies: List[Dict[str, Any]]) -> Dict[str, int]:
        """Categorize competencies by category
        
        Args:
            competencies: List of competencies
            
        Returns:
            Competencies categorized by category
        """
        categories = Counter()
        for competency in competencies:
            comp_category = competency.get('category', 'unknown')
            categories[comp_category] += 1
        return dict(categories)
    
    def _save_processed_document(self, processing_result: Dict[str, Any], doc_info: Dict[str, Any]):
        """Save processed document results to file
        
        Args:
            processing_result: Processing results
            doc_info: Document information
        """
        try:
            # Generate filename
            doc_title = doc_info.get('title', 'unknown')
            safe_title = re.sub(r'[^\w\s-]', '', doc_title)[:50]
            filename = f"processed_{safe_title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            file_path = self.processed_dir / filename
            
            # Save processing result
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(processing_result, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.debug(f"Saved processed document: {filename}")
            
        except Exception as e:
            self.logger.error(f"Error saving processed document: {e}")
    
    def _initialize_standards_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize regex patterns for standards extraction"""
        return {
            'default': [
                {
                    'name': 'learning_objective',
                    'pattern': r'(?:students?\s+(?:will|shall|should|must|can)\s+.{20,200})',
                    'type': 'learning_objective',
                    'confidence': 0.8
                },
                {
                    'name': 'competency_statement',
                    'pattern': r'(?:demonstrate|understand|analyze|evaluate|apply|create).{20,200}',
                    'type': 'competency',
                    'confidence': 0.7
                },
                {
                    'name': 'standard_number',
                    'pattern': r'(?:standard|std\.?)\s*\d+[.\d]*[:\s].{20,200}',
                    'type': 'numbered_standard',
                    'confidence': 0.9
                }
            ],
            'Mathematics': [
                {
                    'name': 'math_standard',
                    'pattern': r'(?:solve|calculate|interpret|graph|model).{20,200}',
                    'type': 'math_competency',
                    'confidence': 0.8
                }
            ],
            'Computer_Science': [
                {
                    'name': 'cs_standard',
                    'pattern': r'(?:program|code|algorithm|debug|design).{20,200}',
                    'type': 'cs_competency',
                    'confidence': 0.8
                }
            ]
        }
    
    def _initialize_competency_patterns(self) -> Dict[str, List[str]]:
        """Initialize patterns for competency extraction"""
        return {
            'knowledge': ['know', 'understand', 'recall', 'identify', 'describe', 'explain'],
            'skill': ['demonstrate', 'apply', 'use', 'perform', 'execute', 'implement'],
            'attitude': ['appreciate', 'value', 'respect', 'exhibit', 'demonstrate']
        }
    
    def _initialize_nlp_tools(self) -> Dict[str, Any]:
        """Initialize NLP tools if available"""
        tools = {}
        
        if HAS_NLTK:
            try:
                # Download required NLTK data (if not already present)
                import nltk
                nltk.download('punkt', quiet=True)
                nltk.download('stopwords', quiet=True)
                nltk.download('wordnet', quiet=True)
                
                tools['tokenizer'] = word_tokenize
                tools['sentence_tokenizer'] = sent_tokenize
                tools['stopwords'] = set(stopwords.words('english'))
                tools['lemmatizer'] = WordNetLemmatizer()
            except Exception as e:
                self.logger.warning(f"Failed to initialize NLTK tools: {e}")
        
        if HAS_SKLEARN:
            tools['tfidf_vectorizer'] = TfidfVectorizer
            tools['kmeans'] = KMeans
        
        return tools
    
    def get_processing_summary(self) -> Dict[str, Any]:
        """Get summary of processing results for this agent
        
        Returns:
            Processing summary dictionary
        """
        return {
            'agent_id': self.agent_id,
            'discipline': self.discipline,
            'documents_processed': len(self.processed_documents.get(self.discipline, [])),
            'standards_extracted': len(self.extracted_standards.get(self.discipline, [])),
            'processing_directory': str(self.processed_dir),
            'last_processing': self.performance_stats.get('last_activity'),
            'total_processing_tasks': self.performance_stats.get('tasks_completed', 0)
        }
    
    def __del__(self):
        """Cleanup when processing agent is destroyed"""
        super().__del__()