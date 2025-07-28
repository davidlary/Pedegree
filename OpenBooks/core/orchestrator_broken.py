"""
OpenBooks Orchestrator - Core orchestration module for managing the complete acquisition workflow.

This module contains the main orchestration logic previously embedded in GetOpenBooks.py,
providing a clean separation between command-line interface and core functionality.
All orchestration logic is properly tested and uses only core modules.
"""

import time
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

from .config import OpenBooksConfig
from .terminal_ui import TerminalUI
from .enhanced_logging import OperationLogger
from .book_discoverer import BookDiscoverer
from .repository_manager import RepositoryManager
from .content_processor import ContentProcessor
from .parallel_processor import ParallelProcessor, ProcessingTask, create_parallel_task_batches
from .search_indexer import SearchIndexer
from .language_detector import LanguageDetector

logger = logging.getLogger(__name__)


class OpenBooksOrchestrator:
    """
    Core orchestrator for the OpenBooks acquisition and management system.
    
    This class manages the complete workflow for discovering, acquiring, organizing,
    and indexing open educational textbooks. It uses only core functionality modules
    and is designed to be fully unit testable.
    """
    
    def __init__(self, config: OpenBooksConfig, terminal_ui: TerminalUI = None):
        """Initialize the orchestrator with configuration and UI."""
        self.config = config
        self.ui = terminal_ui or TerminalUI()
        self.logger = OperationLogger('orchestrator')
        
        # Initialize core components
        self.discoverer = BookDiscoverer(config)
        self.repo_manager = RepositoryManager(config)
        self.content_processor = ContentProcessor(config)
        self.search_indexer = SearchIndexer(config)
        self.language_detector = LanguageDetector()
        self.parallel_processor = ParallelProcessor(config)
        
        logger.info(f"OpenBooksOrchestrator initialized with {config.max_workers} workers")
    
    def run_complete_workflow(self, 
                            update_existing: bool = False,
                            dry_run: bool = False,
                            subjects: Optional[List[str]] = None,
                            language_filter: Optional[str] = None,
                            openstax_only: bool = True,
                            check_updates: bool = True) -> Dict[str, Any]:
        """
        Execute the complete OpenBooks workflow.
        
        Args:
            update_existing: Whether to update existing repositories
            dry_run: Preview mode without making changes
            subjects: List of subjects to focus on
            language_filter: Language filter for discovery
            openstax_only: Restrict to OpenStax repositories only
            check_updates: Check existing repositories for updates
            
        Returns:
            Dictionary with workflow results and statistics
        """
        start_time = time.time()
        workflow_results = {
            'phases_completed': [],
            'total_books': 0,
            'errors': 0,
            'warnings': 0,
            'duration': 0
        }
        
        try:
            self.ui.print_header("OpenBooks Acquisition System", 
                               "Comprehensive open textbook discovery and management")
            
            # Display configuration
            self._display_configuration(dry_run, openstax_only, check_updates)
            
            if dry_run:
                self.ui.print_info("DRY RUN MODE - No changes will be made")
            
            # Phase 1: Catalog existing collection
            self._run_phase("catalog_existing_collection", 1, 
                          lambda: self.catalog_existing_collection(openstax_only, language_filter),
                          workflow_results)
            
            # Phase 2: Repository updates (if enabled)
            if check_updates:
                self._run_phase("update_existing_repositories", 2,
                              lambda: self.update_existing_repositories(dry_run),
                              workflow_results)
            
            # Phase 3: Auto-discover available books
            self._run_phase("discover_books", 3,
                          lambda: self.discover_books(subjects, language_filter, openstax_only),
                          workflow_results)
            
            # Phase 4: Acquire books
            self._run_phase("acquire_books", 4,
                          lambda: self.acquire_books(dry_run, openstax_only),
                          workflow_results)
            
            # Phase 5: Update existing books (if enabled)
            if update_existing:
                self._run_phase("update_books", 5,
                              lambda: self.update_existing_books(dry_run),
                              workflow_results)
            
            # Phase 6: Generate catalog
            self._run_phase("generate_catalog", 6,
                          lambda: self.generate_catalog(),
                          workflow_results)
            
            # Phase 7: Build search index
            self._run_phase("build_search_index", 7,
                          lambda: self.build_search_index(),
                          workflow_results)
            
            # Final statistics
            workflow_results['duration'] = time.time() - start_time
            self._display_final_statistics(workflow_results)
            
        except Exception as e:
            self.logger.log_error(e, "workflow execution", "orchestrator", "error")
            workflow_results['errors'] += 1
        finally:
            self.parallel_processor.stop()
        
        return workflow_results
    
    def catalog_existing_collection(self, openstax_only: bool = False, 
                                  language_filter: Optional[str] = None) -> Dict[str, Any]:
        """Catalog existing books in the Books directory."""
        op = self.logger.start_operation("catalog_existing_collection", 
                                       openstax_only=openstax_only, 
                                       language_filter=language_filter)
        
        self.ui.print_phase(1, "Cataloging Existing Collection", 
                           "Scanning Books directory for PDFs and repositories")
        
        if openstax_only:
            self.ui.print_info("Filtering to OpenStax-only repositories")
        if language_filter:
            self.ui.print_info(f"Language filter: {language_filter}")
        
        existing_books = {
            "pdfs": [],
            "git_repos": [],
            "other_formats": [],
            "total_size_mb": 0,
            "languages": {},
            "levels": {},
            "subjects": {},
            "organizations": {}
        }
        
        books_path = Path(self.config.books_path)
        if not books_path.exists():
            error = FileNotFoundError(f"Books directory does not exist: {books_path}")
            self.logger.log_file_error(str(books_path), "catalog", error)
            self.logger.end_operation(False)
            return existing_books
        
        # Find PDFs
        for pdf_file in books_path.glob("*.pdf"):
            size_mb = pdf_file.stat().st_size / (1024 * 1024)
            existing_books["pdfs"].append({
                "name": pdf_file.stem,
                "path": str(pdf_file),
                "size_mb": round(size_mb, 2)
            })
            existing_books["total_size_mb"] += size_mb
        
        # First collect all repository paths for progress tracking
        all_repo_paths = []
        self._collect_repository_paths(books_path, all_repo_paths, openstax_only, language_filter)
        
        # Process repositories with progress bar
        if all_repo_paths:
            for i, repo_path in enumerate(all_repo_paths, 1):
                self.ui.print_progress(i, len(all_repo_paths), "Scanning", repo_path.name)
                self._process_repository(repo_path, existing_books, openstax_only, language_filter)
            
            # Clear progress line
            self.ui.clear_line()
        
        # Display comprehensive results using terminal UI
        stats = {
            "PDFs": len(existing_books['pdfs']),
            "Git Repositories": len(existing_books['git_repos']),
            "Other Formats": len(existing_books['other_formats']),
            "Total Size (MB)": f"{existing_books['total_size_mb']:.1f}",
            "Breakdown by Level": existing_books['levels'],
            "Breakdown by Subject": existing_books['subjects'],
            "Breakdown by Organization": existing_books['organizations']
        }
        
        self.ui.print_statistics(stats)
        
        # Language distribution
        if existing_books['languages']:
            self.ui.print_language_summary(existing_books['languages'])
        
        self.logger.end_operation(True, pdfs=len(existing_books['pdfs']), 
                                 repos=len(existing_books['git_repos']), 
                                 size_mb=existing_books['total_size_mb'])
        
        return existing_books
    
    def discover_books(self, subjects: Optional[List[str]] = None,
                      language_filter: Optional[str] = None,
                      openstax_only: bool = True) -> Dict[str, Any]:
        """
        Discover available books using the discovery engine.
        
        Args:
            subjects: List of subjects to focus on
            language_filter: Language filter for discovery
            openstax_only: Restrict to OpenStax repositories only
            
        Returns:
            Dictionary with discovery results
        """
        return self.discoverer.discover_books(
            subjects=subjects,
            language_filter=language_filter,
            openstax_only=openstax_only
        )
    
    def acquire_books(self, dry_run: bool = False, openstax_only: bool = True) -> Dict[str, Any]:
        """
        Acquire discovered books using parallel processing.
        
        Args:
            dry_run: Preview mode without making changes
            openstax_only: Restrict to OpenStax repositories only
            
        Returns:
            Dictionary with acquisition results
        """
        # Get discovered books from the discoverer
        discovered_books = self.discoverer.get_discovered_books()
        
        if not discovered_books:
            self.ui.print_warning("No books discovered for acquisition")
            return {'books_acquired': 0, 'success_count': 0, 'error_count': 0}
        
        # Create parallel tasks for acquisition
        discovery_tasks, clone_tasks, processing_tasks = create_parallel_task_batches(
            discovered_books, self.config
        )
        
        if dry_run:
            self._preview_acquisition(discovered_books)
            return {'books_acquired': len(discovered_books), 'success_count': 0, 'error_count': 0}
        
        # Execute parallel acquisition
        results = self.parallel_processor.process_batch_parallel(
            discovery_tasks=discovery_tasks,
            clone_tasks=clone_tasks,
            processing_tasks=processing_tasks
        )
        
        return self._process_acquisition_results(results)
    
    def update_existing_repositories(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        Update all existing repositories.
        
        Args:
            dry_run: Preview mode without making changes
            
        Returns:
            Dictionary with update results
        """
        books_path = Path(self.config.books_path)
        update_results = {'updated_count': 0, 'error_count': 0, 'repositories': []}
        
        if not books_path.exists():
            return update_results
        
        # Find all git repositories
        git_repos = []
        for git_dir in books_path.rglob(".git"):
            if git_dir.is_dir():
                repo_path = git_dir.parent
                git_repos.append(repo_path)
        
        self.ui.print_info(f"Found {len(git_repos)} repositories to update")
        
        for i, repo_path in enumerate(git_repos):
            self.ui.print_progress("Updating repositories", i + 1, len(git_repos), 
                                 details=repo_path.name)
            
            if dry_run:
                self.ui.print_info(f"[DRY RUN] Would check and update: {repo_path}")
                continue
            
            try:
                success = self.repo_manager.update_repository(str(repo_path))
                if success:
                    update_results['updated_count'] += 1
                else:
                    update_results['error_count'] += 1
                
                update_results['repositories'].append({
                    'path': str(repo_path),
                    'name': repo_path.name,
                    'success': success
                })
                
            except Exception as e:
                self.logger.log_error(e, f"updating repository {repo_path.name}", 
                                    "repository_manager", "warning")
                update_results['error_count'] += 1
        
        return update_results
    
    def update_existing_books(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        Update existing books (alias for update_existing_repositories).
        
        Args:
            dry_run: Preview mode without making changes
            
        Returns:
            Dictionary with update results
        """
        return self.update_existing_repositories(dry_run)
    
    def generate_catalog(self) -> Dict[str, Any]:
        """
        Generate comprehensive catalog of the collection.
        
        Returns:
            Dictionary with catalog generation results
        """
        return self.content_processor.generate_comprehensive_catalog()
    
    def build_search_index(self) -> Dict[str, Any]:
        """
        Build search index for the collection.
        
        Returns:
            Dictionary with search index results
        """
        books_path = Path(self.config.books_path)
        
        if not books_path.exists():
            return {'books_indexed': 0, 'terms_indexed': 0, 'size_mb': 0.0}
        
        # Find all repositories to index
        repo_paths = []
        for git_dir in books_path.rglob(".git"):
            if git_dir.is_dir():
                repo_paths.append(git_dir.parent)
        
        # Index repositories
        indexed_count = 0
        for repo_path in repo_paths:
            try:
                if self.index_book(repo_path):
                    indexed_count += 1
            except Exception as e:
                self.logger.log_error(e, f"indexing {repo_path.name}", "search_indexer", "warning")
        
        # Get final index statistics
        stats = self.search_indexer.get_index_stats()
        
        return {
            'books_indexed': indexed_count,
            'terms_indexed': stats.unique_terms,
            'size_mb': stats.index_size_mb
        }
    
    def index_book(self, repo_path: Path) -> bool:
        """Index a single book repository for search."""
        try:
            # Use content processor to extract content from the repository
            extracted_content = self.content_processor.extract_content_from_repo(repo_path)
            
            if extracted_content:
                # Index the extracted content
                return self.search_indexer.index_content(extracted_content)
            else:
                self.logger.log_warning(f"No content extracted from {repo_path}")
                return False
                
        except Exception as e:
            self.logger.log_error(e, f"indexing book {repo_path.name}", "search_indexer", "warning")
            return False
    
    def _run_phase(self, phase_name: str, phase_number: int, phase_func, workflow_results: Dict[str, Any]):
        """Execute a workflow phase with timing and error handling."""
        start_time = time.time()
        phase_display_name = phase_name.replace('_', ' ').title()
        
        self.ui.print_phase_header(phase_number, phase_display_name)
        
        try:
            result = phase_func()
            duration = time.time() - start_time
            
            workflow_results['phases_completed'].append(phase_name)
            self.logger.log_info(f"✅ Completed: {phase_name} ({duration:.2f}s) - {result}")
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            self.logger.log_error(e, f"phase {phase_name}", "orchestrator", "error")
            workflow_results['errors'] += 1
            
            self.ui.print_error(f"Phase {phase_number} failed: {e}")
            raise
    
    def _display_configuration(self, dry_run: bool, openstax_only: bool, check_updates: bool):
        """Display current configuration settings."""
        config_info = [
            f"Parallel Processing: {'✓' if self.config.enable_parallel_processing else '✗'}",
            f"Search Indexing: {'✓' if self.config.enable_search_indexing else '✗'}",
            f"Format Preference: {self.config.preferred_format}",
            f"Language Filter: {self.config.language_filter}",
            f"OpenStax Only: {'✓' if openstax_only else '✗'}",
            f"Git Only: {'✓' if self.config.git_only else '✗'}",
            f"Check Updates: {'✓' if check_updates else '✗'}",
            f"Dry Run: {'✓' if dry_run else '✗'}"
        ]
        
        self.ui.print_info("Configuration:")
        for info in config_info:
            self.ui.print_info(f"  {info}")
        print()
    
    def _preview_acquisition(self, books: List[Dict[str, Any]]):
        """Preview what books would be acquired in dry run mode."""
        self.ui.print_info("Books that would be acquired:")
        for book in books:
            repo_name = book.get('repo', book.get('name', 'Unknown'))
            self.ui.print_info(f"  - {repo_name}")
    
    def _process_acquisition_results(self, results: Dict[str, List]) -> Dict[str, Any]:
        """Process and summarize acquisition results."""
        total_success = sum(len(result_list) for result_list in results.values())
        total_tasks = total_success + self.parallel_processor.stats.get('tasks_failed', 0)
        
        return {
            'total_tasks': total_tasks,
            'success_count': total_success,
            'error_count': self.parallel_processor.stats.get('tasks_failed', 0),
            'discovery_results': len(results.get('discovery', [])),
            'clone_results': len(results.get('clone', [])),
            'processing_results': len(results.get('processing', []))
        }
    
    def _display_final_statistics(self, workflow_results: Dict[str, Any]):
        """Display final workflow statistics."""
        phases_completed = len(workflow_results['phases_completed'])
        total_duration = workflow_results['duration']
        
        self.ui.print_success(f"Workflow completed successfully!")
        self.ui.print_info(f"Phases completed: {phases_completed}")
        self.ui.print_info(f"Total duration: {total_duration:.2f} seconds")
        
        if workflow_results['errors'] > 0 or workflow_results['warnings'] > 0:
            self.ui.print_warning(f"Errors: {workflow_results['errors']}, "
                                f"Warnings: {workflow_results['warnings']}")
    
    # ===== ALL ORIGINAL METHODS FROM GetOpenBooks CLASS =====
    
    def _collect_repository_paths(self, books_path: Path, repo_paths: List[Path], openstax_only: bool = False, language_filter: Optional[str] = None) -> None:
        """Recursively collect all repository paths for progress tracking."""
        try:
            # Check for language-based structure first
            language_dirs = ['english', 'spanish', 'french', 'polish', 'german']
            has_language_structure = any((books_path / lang).exists() and (books_path / lang).is_dir() 
                                       for lang in language_dirs)
            
            if has_language_structure:
                for lang_dir in books_path.iterdir():
                    if lang_dir.is_dir() and lang_dir.name in language_dirs:
                        if language_filter and lang_dir.name != language_filter:
                            continue
                        self._collect_fields_in_language(lang_dir, repo_paths, openstax_only)
            else:
                # Try OpenAlex structure or fallback to recursive search
                try:
                    from .openalex_disciplines import get_hierarchy
                    hierarchy = get_hierarchy()
                    
                    # Check for field-based organization
                    field_like_dirs = [d for d in books_path.iterdir() 
                                     if d.is_dir() and any(char.isupper() for char in d.name)]
                    
                    if field_like_dirs:
                        for field_dir in field_like_dirs:
                            self._collect_openalex_structure_single_field(field_dir, repo_paths, openstax_only)
                    else:
                        # Fallback to recursive directory search
                        self._collect_directory_repos(books_path, repo_paths, recursive=True, openstax_only=openstax_only)
                        
                except ImportError:
                    # No OpenAlex available, do recursive search
                    self._collect_directory_repos(books_path, repo_paths, recursive=True, openstax_only=openstax_only)
                
        except Exception as e:
            self.logger.log_error(e, f"collecting repository paths from {books_path}", "file_system", "warning")\n    \n    def _collect_fields_in_language(self, lang_path: Path, repo_paths: List[Path], openstax_only: bool = False) -> None:\n        \"\"\"Collect repositories from fields within a language directory.\"\"\"\n        try:\n            from .openalex_disciplines import get_hierarchy\n            hierarchy = get_hierarchy()\n            \n            for field_dir in lang_path.iterdir():\n                if not field_dir.is_dir():\n                    continue\n                \n                field_name = field_dir.name\n                \n                # Check for level subdirectories or repositories directly\n                level_dirs = [\"HighSchool\", \"University\", \"Graduate\"]\n                has_levels = any((field_dir / level).exists() and (field_dir / level).is_dir() \n                               for level in level_dirs)\n                \n                if has_levels:\n                    for level_dir in field_dir.iterdir():\n                        if level_dir.is_dir() and level_dir.name in level_dirs:\n                            self._collect_directory_repos(level_dir, repo_paths, recursive=False, openstax_only=openstax_only)\n                else:\n                    # Repositories directly under field or non-standard structure\n                    self._collect_directory_repos(field_dir, repo_paths, recursive=True, openstax_only=openstax_only)\n                    \n        except Exception as e:\n            self.logger.log_error(e, f\"collecting fields in {lang_path}\", \"file_system\", \"warning\")\n    \n    def _collect_openalex_structure_single_field(self, field_path: Path, repo_paths: List[Path], openstax_only: bool = False) -> None:\n        \"\"\"Collect repositories from a single OpenAlex field directory.\"\"\"\n        try:\n            field_name = field_path.name\n            \n            # Check for level subdirectories\n            level_dirs = [\"HighSchool\", \"University\", \"Graduate\"]\n            has_levels = any((field_path / level).exists() and (field_path / level).is_dir() \n                           for level in level_dirs)\n            \n            if has_levels:\n                for level_dir in field_path.iterdir():\n                    if level_dir.is_dir() and level_dir.name in level_dirs:\n                        self._collect_directory_repos(level_dir, repo_paths, recursive=False, openstax_only=openstax_only)\n            else:\n                # Repository directory directly under field or non-standard structure\n                self._collect_directory_repos(field_path, repo_paths, recursive=True, openstax_only=openstax_only)\n                \n        except Exception as e:\n            self.logger.log_error(e, f\"collecting from field {field_path}\", \"file_system\", \"warning\")\n    \n    def _collect_directory_repos(self, directory: Path, repo_paths: List[Path], recursive: bool = False, openstax_only: bool = False) -> None:\n        \"\"\"Collect repository paths from a directory.\"\"\"\n        try:\n            for item in directory.iterdir():\n                if not item.is_dir():\n                    continue\n                \n                # Check if this is a git repository\n                if (item / '.git').exists():\n                    # Apply OpenStax filter if requested\n                    if openstax_only and not self._is_openstax_repository_path(item):\n                        continue\n                    repo_paths.append(item)\n                elif recursive:\n                    # Recurse into subdirectories\n                    self._collect_directory_repos(item, repo_paths, recursive=True, openstax_only=openstax_only)\n                    \n        except Exception as e:\n            self.logger.log_error(e, f\"collecting repos from {directory}\", \"file_system\", \"warning\")\n    \n    def _process_repository(self, repo_path: Path, existing_books: Dict[str, Any], openstax_only: bool = False, language_filter: Optional[str] = None) -> None:\n        \"\"\"Process a single repository and add to existing_books.\"\"\"\n        try:\n            if not repo_path.exists() or not repo_path.is_dir():\n                return\n            \n            # Check if it's a git repository\n            if not (repo_path / '.git').exists():\n                return\n            \n            # Apply OpenStax filter\n            if openstax_only and not self._is_openstax_repository_path(repo_path):\n                return\n            \n            # Get repository information\n            repo_name = repo_path.name\n            size_mb = self._get_directory_size(repo_path) / (1024 * 1024)\n            \n            # Detect language\n            detected_language = self.language_detector.detect_language(repo_path, repo_name)\n            \n            # Apply language filter\n            if language_filter and detected_language != language_filter:\n                return\n            \n            # Detect subject, level, and organization\n            subject = self._detect_subject_from_path(repo_path)\n            level = self._detect_level_from_path(repo_path)\n            organization = self._detect_organization_from_path(repo_path)\n            \n            # Create repository entry\n            repo_info = {\n                \"name\": repo_name,\n                \"path\": str(repo_path),\n                \"size_mb\": round(size_mb, 2),\n                \"language\": detected_language,\n                \"level\": level,\n                \"subject\": subject,\n                \"organization\": organization\n            }\n            \n            existing_books[\"git_repos\"].append(repo_info)\n            existing_books[\"total_size_mb\"] += size_mb\n            \n            # Update counters\n            existing_books[\"languages\"][detected_language] = existing_books[\"languages\"].get(detected_language, 0) + 1\n            existing_books[\"levels\"][level] = existing_books[\"levels\"].get(level, 0) + 1\n            existing_books[\"subjects\"][subject] = existing_books[\"subjects\"].get(subject, 0) + 1\n            existing_books[\"organizations\"][organization] = existing_books[\"organizations\"].get(organization, 0) + 1\n            \n            self.ui.print_repository_status(repo_name, \"found\", \n                                           f\"{detected_language} | {level} | {subject} | {organization}\")\n            \n        except Exception as e:\n            self.logger.log_error(e, f\"processing repository {repo_path}\", \"repository\", \"warning\")\n    \n    def _detect_subject_from_path(self, path: Path) -> str:\n        \"\"\"Detect subject from repository path.\"\"\"\n        path_parts = [p.lower() for p in path.parts]\n        \n        # Common subject keywords in path\n        subject_map = {\n            'physics': 'Physics', 'biology': 'Biology', 'chemistry': 'Chemistry',\n            'mathematics': 'Mathematics', 'math': 'Mathematics', 'calculus': 'Mathematics',\n            'algebra': 'Mathematics', 'statistics': 'Statistics', 'psychology': 'Psychology',\n            'sociology': 'Sociology', 'business': 'Business', 'economics': 'Economics',\n            'computer': 'Computer Science', 'engineering': 'Engineering',\n            'history': 'History', 'philosophy': 'Philosophy', 'art': 'Art'\n        }\n        \n        for part in path_parts:\n            for keyword, subject in subject_map.items():\n                if keyword in part:\n                    return subject\n        \n        # Try extracting from repository name\n        return self._extract_subject_from_repo_name(path.name)\n    \n    def _extract_subject_from_repo_name(self, repo_name: str) -> str:\n        \"\"\"Extract subject from repository name.\"\"\"\n        name_lower = repo_name.lower()\n        \n        subject_keywords = {\n            'physics': ['physics', 'fisica'], 'biology': ['biology', 'biologia'], \n            'chemistry': ['chemistry', 'quimica'], 'mathematics': ['math', 'calculus', 'algebra', 'matematicas'],\n            'psychology': ['psychology', 'psicologia'], 'business': ['business', 'negocios'],\n            'economics': ['economics', 'economia'], 'sociology': ['sociology', 'sociologia']\n        }\n        \n        for subject, keywords in subject_keywords.items():\n            if any(keyword in name_lower for keyword in keywords):\n                return subject.title()\n        \n        return \"Other\"\n    \n    def _detect_organization_from_path(self, path: Path) -> str:\n        \"\"\"Detect organization from repository path or name.\"\"\"\n        repo_name = path.name.lower()\n        \n        if 'osbooks-' in repo_name or 'openstax' in str(path).lower():\n            return \"OpenStax\"\n        elif 'cnxbook-' in repo_name or 'cnx' in str(path).lower():\n            return \"CNX\"\n        else:\n            return \"Other\"\n    \n    def _detect_level_from_path(self, path: Path) -> str:\n        \"\"\"Detect educational level from repository path.\"\"\"\n        path_str = str(path).lower()\n        repo_name = path.name.lower()\n        \n        # Check path components\n        if 'highschool' in path_str or 'high-school' in path_str:\n            return \"HighSchool\"\n        elif 'graduate' in path_str:\n            return \"Graduate\"\n        elif 'university' in path_str:\n            return \"University\"\n        \n        # Check repository name for level indicators\n        high_school_indicators = ['prealgebra', 'pre-algebra', 'ap-', 'high-school']\n        graduate_indicators = ['graduate', 'phd', 'advanced', 'research']\n        \n        if any(indicator in repo_name for indicator in high_school_indicators):\n            return \"HighSchool\"\n        elif any(indicator in repo_name for indicator in graduate_indicators):\n            return \"Graduate\"\n        else:\n            return \"University\"\n    \n    def _get_directory_size(self, path: Path) -> int:\n        \"\"\"Get total size of directory in bytes.\"\"\"\n        total_size = 0\n        try:\n            for item in path.rglob('*'):\n                if item.is_file():\n                    total_size += item.stat().st_size\n        except Exception as e:\n            self.logger.log_error(e, f\"calculating size of {path}\", \"file_system\", \"warning\")\n        return total_size\n    \n    def _has_content(self, directory: Path) -> bool:\n        \"\"\"Check if directory has substantial content.\"\"\"\n        try:\n            file_count = sum(1 for _ in directory.rglob('*') if _.is_file())\n            return file_count > 5  # Arbitrary threshold for \"substantial\" content\n        except Exception:\n            return False\n    \n    def _is_openstax_repository_path(self, repo_path: Path) -> bool:\n        \"\"\"Check if repository path indicates an OpenStax repository.\"\"\"\n        repo_name = repo_path.name.lower()\n        path_str = str(repo_path).lower()\n        \n        openstax_indicators = [\n            'osbooks-', 'openstax', 'derived-from-osbooks-'\n        ]\n        \n        return any(indicator in repo_name or indicator in path_str \n                  for indicator in openstax_indicators)\n    \n    def cleanup_non_openstax_repositories(self, dry_run: bool = False) -> Dict[str, Any]:\n        \"\"\"Remove non-OpenStax repositories from the collection.\"\"\"\n        op = self.logger.start_operation(\"cleanup_non_openstax\", dry_run=dry_run)\n        \n        books_path = Path(self.config.books_path)\n        results = {\n            \"repositories_checked\": 0,\n            \"non_openstax_found\": 0,\n            \"removed\": 0,\n            \"errors\": 0,\n            \"removed_repositories\": [],\n            \"error_repositories\": []\n        }\n        \n        if not books_path.exists():\n            self.logger.end_operation(False, error=\"Books directory does not exist\")\n            return results\n        \n        # Find all git repositories\n        for git_dir in books_path.rglob(\".git\"):\n            if git_dir.is_dir():\n                repo_path = git_dir.parent\n                results[\"repositories_checked\"] += 1\n                \n                if not self._is_openstax_repository_path(repo_path):\n                    results[\"non_openstax_found\"] += 1\n                    \n                    if self._remove_repository(repo_path, dry_run):\n                        results[\"removed\"] += 1\n                        results[\"removed_repositories\"].append(str(repo_path))\n                    else:\n                        results[\"errors\"] += 1\n                        results[\"error_repositories\"].append(str(repo_path))\n        \n        self.logger.end_operation(True, **results)\n        return results\n    \n    def _remove_repository(self, repo_path: Path, dry_run: bool = True) -> bool:\n        \"\"\"Remove a repository directory.\"\"\"\n        try:\n            if dry_run:\n                self.ui.print_info(f\"[DRY RUN] Would remove: {repo_path}\")\n                return True\n            else:\n                import shutil\n                shutil.rmtree(repo_path)\n                self.ui.print_success(f\"Removed: {repo_path}\")\n                return True\n        except Exception as e:\n            self.logger.log_error(e, f\"removing repository {repo_path}\", \"file_system\", \"error\")\n            return False\n    \n    def check_for_duplicates(self) -> Dict[str, Any]:\n        \"\"\"Check for duplicate repositories in the collection.\"\"\"\n        op = self.logger.start_operation(\"check_duplicates\")\n        \n        books_path = Path(self.config.books_path)\n        results = {\n            \"total_repositories\": 0,\n            \"duplicates_found\": 0,\n            \"duplicate_groups\": [],\n            \"unique_repositories\": 0\n        }\n        \n        if not books_path.exists():\n            self.logger.end_operation(False, error=\"Books directory does not exist\")\n            return results\n        \n        # Collect all repositories with their characteristics\n        repositories = {}\n        for git_dir in books_path.rglob(\".git\"):\n            if git_dir.is_dir():\n                repo_path = git_dir.parent\n                repo_name = repo_path.name\n                \n                # Create a key for duplicate detection\n                key = repo_name.lower().replace('-', '').replace('_', '')\n                \n                if key not in repositories:\n                    repositories[key] = []\n                repositories[key].append(str(repo_path))\n                results[\"total_repositories\"] += 1\n        \n        # Find duplicates\n        for key, paths in repositories.items():\n            if len(paths) > 1:\n                results[\"duplicates_found\"] += len(paths) - 1\n                results[\"duplicate_groups\"].append({\n                    \"key\": key,\n                    \"paths\": paths,\n                    \"count\": len(paths)\n                })\n            else:\n                results[\"unique_repositories\"] += 1\n        \n        self.logger.end_operation(True, **results)\n        return results"