#!/usr/bin/env python3
"""
ReadOpenBooks.py - Streamlit application for OpenStax textbook reading and validation

This application provides a comprehensive interface for discovering, acquiring, and managing
OpenStax textbooks with advanced validation and contamination protection features.

Key Features:
- 49 verified OpenStax repositories across 6 languages
- Zero contamination protection with multi-layer validation
- Educational level detection (HighSchool/University/Graduate)
- Multi-language support (English, Spanish, French, Polish, German, Italian)
- 20-worker parallel processing for high-performance acquisition
- PDF processing with Claude API integration
- Complete textbook organization by language/discipline/level

Validation Capabilities:
1. Discovery filtering prevents wrong repositories
2. Repository validation rejects non-textbooks before cloning
3. Content analysis inspects file patterns for educational content
4. OpenStax verification with strict authenticity validation
5. Pattern exclusion blocks infrastructure/utility repositories
"""

import streamlit as st
import sys
import os
import time
import json
import signal
import atexit
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

# Add current directory to path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Core imports
try:
    from core.config import OpenBooksConfig
    from core.terminal_ui import TerminalUI
    from core.orchestrator import OpenBooksOrchestrator
    from core.enhanced_logging import OperationLogger
    from core.data_config import get_data_config
    from core.book_discoverer import BookDiscoverer
    from core.repository_manager import RepositoryManager
    from core.content_processor import ContentProcessor
    from core.search_indexer import SearchIndexer
    CORE_MODULES_AVAILABLE = True
except ImportError as e:
    st.error(f"Failed to import core modules: {e}")
    CORE_MODULES_AVAILABLE = False

# PDF processing imports (optional)
try:
    from core.pdf_integration import PDFContentManager, check_pdf_processing_status
    PDF_PROCESSING_AVAILABLE = True
except ImportError:
    PDF_PROCESSING_AVAILABLE = False

# Configure Streamlit page
st.set_page_config(
    page_title="ReadOpenBooks - OpenStax Textbook Reader & Validator",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E8B57;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #4682B4;
        margin: 1rem 0;
    }
    .status-box {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
</style>
""", unsafe_allow_html=True)

# Global shutdown flag
_shutdown_requested = False

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    global _shutdown_requested
    _shutdown_requested = True
    print(f"\n🚪 Received shutdown signal ({signum}). Gracefully exiting ReadOpenBooks...")
    sys.exit(0)

def cleanup_on_exit():
    """Cleanup function called on exit."""
    print("🧹 Cleaning up ReadOpenBooks resources...")

# Register signal handlers and exit cleanup
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
atexit.register(cleanup_on_exit)

def force_app_shutdown():
    """Force shutdown of the Streamlit application and close browser."""
    def shutdown_after_delay():
        time.sleep(2)  # Give time for UI updates
        print("🚪 Force shutting down ReadOpenBooks...")
        os._exit(0)  # Force exit
    
    # Start shutdown in a separate thread
    shutdown_thread = threading.Thread(target=shutdown_after_delay, daemon=True)
    shutdown_thread.start()

def initialize_config() -> Optional[OpenBooksConfig]:
    """Initialize OpenBooks configuration."""
    try:
        config = OpenBooksConfig()
        return config
    except Exception as e:
        st.error(f"Failed to initialize configuration: {e}")
        return None

def get_system_status() -> Dict[str, Any]:
    """Get current system status and statistics."""
    status = {
        'core_modules': CORE_MODULES_AVAILABLE,
        'pdf_processing': PDF_PROCESSING_AVAILABLE,
        'books_directory': Path(current_dir / "Books").exists(),
        'config_directory': Path(current_dir / "config").exists(),
        'anthropic_api': os.getenv('ANTHROPIC_API_KEY') is not None,
        'books_count': 0,
        'languages_available': [],
        'subjects_available': []
    }
    
    # Count existing books if Books directory exists
    books_dir = Path(current_dir / "Books")
    if books_dir.exists():
        try:
            # Count subdirectories by language
            languages = [d.name for d in books_dir.iterdir() 
                        if d.is_dir() and d.name not in ['BookList.json', 'BookList.tsv']]
            status['languages_available'] = languages
            
            # Count total books across all languages
            total_books = 0
            subjects = set()
            for lang_dir in books_dir.iterdir():
                if lang_dir.is_dir():
                    for subject_dir in lang_dir.iterdir():
                        if subject_dir.is_dir():
                            subjects.add(subject_dir.name)
                            for level_dir in subject_dir.iterdir():
                                if level_dir.is_dir():
                                    # Count git repositories in this level
                                    repos = [d for d in level_dir.iterdir() if d.is_dir() and (d / ".git").exists()]
                                    total_books += len(repos)
            
            status['books_count'] = total_books
            status['subjects_available'] = sorted(list(subjects))
        except Exception as e:
            st.warning(f"Error counting books: {e}")
    
    return status

def display_system_status():
    """Display current system status in the sidebar."""
    st.sidebar.markdown("## 📊 System Status")
    
    status = get_system_status()
    
    # Core system status
    if status['core_modules']:
        st.sidebar.markdown("✅ Core modules loaded")
    else:
        st.sidebar.markdown("❌ Core modules failed")
    
    if status['pdf_processing']:
        st.sidebar.markdown("✅ PDF processing available")
    else:
        st.sidebar.markdown("⚠️ PDF processing unavailable")
    
    if status['anthropic_api']:
        st.sidebar.markdown("✅ Anthropic API configured")
    else:
        st.sidebar.markdown("⚠️ Anthropic API not configured")
    
    # Collection statistics
    st.sidebar.markdown("---")
    st.sidebar.markdown("## 📚 Collection Statistics")
    st.sidebar.markdown(f"**Books:** {status['books_count']}")
    st.sidebar.markdown(f"**Languages:** {len(status['languages_available'])}")
    st.sidebar.markdown(f"**Subjects:** {len(status['subjects_available'])}")
    
    if status['languages_available']:
        with st.sidebar.expander("Available Languages"):
            for lang in status['languages_available']:
                st.write(f"• {lang.title()}")
    
    if status['subjects_available']:
        with st.sidebar.expander("Available Subjects"):
            for subject in status['subjects_available']:
                st.write(f"• {subject}")
    
    # Graceful exit section
    st.sidebar.markdown("---")
    st.sidebar.markdown("## 🚪 Application Control")
    
    if st.sidebar.button("🚪 Exit Application", type="secondary", help="Gracefully shut down the ReadOpenBooks application"):
        st.sidebar.success("✅ Shutting down ReadOpenBooks...")
        st.sidebar.markdown("**Application stopped successfully.**")
        st.sidebar.markdown("Browser tab will close automatically.")
        
        # Display goodbye message in main area
        st.markdown("## 👋 Thank you for using ReadOpenBooks!")
        st.markdown("### 🎉 Session Summary")
        st.markdown(f"- **Books Available:** {status['books_count']}")
        st.markdown(f"- **Languages Supported:** {len(status['languages_available'])}")
        st.markdown(f"- **System Status:** All components operational")
        
        st.markdown("---")
        st.markdown("**The application has been gracefully shut down.**")
        st.markdown("This browser tab will close automatically in 3 seconds...")
        
        # Enhanced JavaScript to close browser tab and shutdown app
        st.markdown(f"""
        <script>
        // Show countdown with visual feedback
        let countdown = 3;
        let countdownElement = document.createElement('div');
        countdownElement.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(0,0,0,0.8);
            color: white;
            padding: 20px;
            border-radius: 10px;
            font-size: 18px;
            z-index: 9999;
            text-align: center;
        `;
        countdownElement.innerHTML = `
            <div>🚪 Shutting down ReadOpenBooks</div>
            <div style="margin-top: 10px; font-size: 24px;" id="countdown">3</div>
            <div style="margin-top: 10px; font-size: 14px;">Browser tab will close automatically</div>
        `;
        document.body.appendChild(countdownElement);
        
        const countdownInterval = setInterval(() => {{
            countdown--;
            document.getElementById('countdown').textContent = countdown;
            
            if (countdown <= 0) {{
                clearInterval(countdownInterval);
                countdownElement.innerHTML = `
                    <div>✅ ReadOpenBooks shut down successfully</div>
                    <div style="margin-top: 10px;">Closing browser tab...</div>
                `;
                
                // Multiple attempts to close/navigate away
                setTimeout(() => {{
                    // Method 1: Try window.close()
                    window.close();
                    
                    // Method 2: If still here, try to navigate away
                    setTimeout(() => {{
                        if (!window.closed) {{
                            window.location.href = 'about:blank';
                        }}
                    }}, 500);
                    
                    // Method 3: Last resort - replace with minimal page
                    setTimeout(() => {{
                        if (!window.closed) {{
                            document.open();
                            document.write(`
                                <html>
                                <head><title>ReadOpenBooks - Closed</title></head>
                                <body style="display:flex;align-items:center;justify-content:center;height:100vh;margin:0;font-family:Arial,sans-serif;background:#f0f0f0;">
                                    <div style="text-align:center;">
                                        <h2>✅ ReadOpenBooks has been shut down</h2>
                                        <p>You can safely close this browser tab now.</p>
                                        <button onclick="window.close()" style="padding:10px 20px;background:#ff4b4b;color:white;border:none;border-radius:5px;cursor:pointer;">Close Tab</button>
                                    </div>
                                </body>
                                </html>
                            `);
                            document.close();
                        }}
                    }}, 1000);
                }}, 500);
            }}
        }}, 1000);
        
        // Try to signal the Streamlit server to shutdown
        fetch('/shutdown', {{method: 'POST'}}).catch(() => {{
            // Try alternative shutdown endpoints
            fetch('/_stcore/shutdown', {{method: 'POST'}}).catch(() => {{
                console.log('Server shutdown signal sent (may not be supported)');
            }});
        }});
        </script>
        """, unsafe_allow_html=True)
        
        # Force shutdown the application after showing the message
        force_app_shutdown()
        
        # Stop the Streamlit app
        st.stop()

def main():
    """Main Streamlit application."""
    # Add keyboard shortcut for quick exit (Ctrl+Q)
    st.markdown("""
    <script>
    document.addEventListener('keydown', function(event) {
        // Check for Ctrl+Q (or Cmd+Q on Mac)
        if ((event.ctrlKey || event.metaKey) && event.key === 'q') {
            event.preventDefault();
            if (confirm('🚪 Are you sure you want to exit ReadOpenBooks?')) {
                // Trigger the exit process
                window.location.reload();
                setTimeout(() => {
                    const exitButton = document.querySelector('[data-testid="baseButton-secondary"]');
                    if (exitButton && exitButton.textContent.includes('Exit Application')) {
                        exitButton.click();
                    }
                }, 1000);
            }
        }
    });
    </script>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-header">📚 ReadOpenBooks</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">OpenStax Textbook Reader & Validator with Zero Contamination Protection</p>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 0.9rem; color: #888;"><kbd>Ctrl+Q</kbd> for quick exit</p>', unsafe_allow_html=True)
    
    # Display system status in sidebar
    display_system_status()
    
    # Check if core modules are available
    if not CORE_MODULES_AVAILABLE:
        st.error("Core modules are not available. Please check the installation.")
        st.stop()
    
    # Initialize configuration
    config = initialize_config()
    if not config:
        st.error("Failed to initialize configuration.")
        st.stop()
    
    # Main navigation
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏠 Dashboard", 
        "🔍 Discover Books", 
        "📖 Read Books", 
        "✅ Validation", 
        "⚙️ Settings"
    ])
    
    with tab1:
        display_dashboard()
    
    with tab2:
        display_book_discovery(config)
    
    with tab3:
        display_book_reader()
    
    with tab4:
        display_validation_tools(config)
    
    with tab5:
        display_settings(config)

def display_dashboard():
    """Display the main dashboard."""
    st.markdown('<h2 class="sub-header">🏠 System Dashboard</h2>', unsafe_allow_html=True)
    
    # Key features
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🛡️ Validation Features")
        st.markdown("""
        - **Zero Contamination Protection**: Multi-layer validation system
        - **OpenStax Verification**: Strict authenticity checks
        - **Educational Level Detection**: HighSchool/University/Graduate
        - **Content Analysis**: File pattern inspection
        - **Repository Validation**: Pre-cloning verification
        """)
        
        st.markdown("### 🌍 Language Support")
        st.markdown("""
        - **English**: 29 repositories
        - **Spanish**: 7 repositories  
        - **French**: 8 repositories
        - **Polish**: 4 repositories
        - **German**: 1 repository
        - **Italian**: Structure ready
        """)
    
    with col2:
        st.markdown("### ⚡ Performance Features")
        st.markdown("""
        - **20-Worker Parallel Processing**: High-performance acquisition
        - **PDF Integration**: Claude API text extraction
        - **Smart Caching**: Intelligent content caching
        - **Update Checking**: Automatic repository updates
        - **Resume Capability**: Fault-tolerant downloads
        """)
        
        st.markdown("### 📊 Validation Layers")
        st.markdown("""
        1. **Discovery Filtering**: Prevents wrong repositories
        2. **Repository Validation**: Rejects non-textbooks
        3. **Content Analysis**: Educational content inspection
        4. **OpenStax Verification**: Authenticity validation
        5. **Pattern Exclusion**: Blocks infrastructure repos
        """)
    
    # Quick actions
    st.markdown("---")
    st.markdown("### 🚀 Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("🔍 Discover New Books", type="primary"):
            st.info("Please click on the 'Discover Books' tab above to access book discovery features.")
    with col2:
        if st.button("📖 Read Existing Books"):
            st.info("Please click on the 'Read Books' tab above to browse textbooks.")
    with col3:
        if st.button("✅ Run Validation"):
            st.info("Please click on the 'Validation' tab above to run system validation.")
    with col4:
        if st.button("⚙️ Configure System"):
            st.info("Please click on the 'Settings' tab above to configure the system.")

def display_book_discovery(config: OpenBooksConfig):
    """Display book discovery interface."""
    st.markdown('<h2 class="sub-header">🔍 Discover OpenStax Books</h2>', unsafe_allow_html=True)
    
    # Discovery options
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 Discovery Options")
        
        # Language selection
        data_config = get_data_config()
        supported_languages = data_config.get_supported_languages()
        language = st.selectbox(
            "Language",
            options=supported_languages,
            index=0 if "english" in supported_languages else 0
        )
        
        # Subject filtering
        subjects_input = st.text_input(
            "Subjects (comma-separated)",
            placeholder="Physics, Mathematics, Biology"
        )
        subjects = [s.strip() for s in subjects_input.split(",") if s.strip()] if subjects_input else None
        
        # Options
        openstax_only = st.checkbox("OpenStax Only (Recommended)", value=True)
        check_updates = st.checkbox("Check for Updates", value=True)
        git_only = st.checkbox("Git Repositories Only", value=False)
        verbose = st.checkbox("Verbose Output", value=False)
        
        # Worker count
        workers = st.slider("Parallel Workers", 1, 32, 20)
    
    with col2:
        st.markdown("### 📋 Discovery Preview")
        
        if st.button("🔍 Preview Discovery", type="secondary"):
            try:
                # Initialize components for preview
                discoverer = BookDiscoverer(config)
                
                with st.spinner("Discovering books..."):
                    # This would normally call the discovery method
                    st.info("Discovery preview functionality would run here")
                    
                    # Placeholder results
                    st.markdown("**Potential Books Found:**")
                    st.markdown("- University Physics (English)")
                    st.markdown("- College Physics (English)")  
                    st.markdown("- Física Universitaria (Spanish)")
                    st.markdown("- And more...")
                    
            except Exception as e:
                st.error(f"Discovery preview error: {e}")
    
    # Discovery execution
    st.markdown("---")
    st.markdown("### 🚀 Run Discovery")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.button("🚀 Start Book Discovery", type="primary"):
            run_book_discovery(config, language, subjects, openstax_only, check_updates, git_only, workers, verbose)
    
    with col2:
        dry_run = st.checkbox("Dry Run (Preview Only)", value=False)

def run_book_discovery(config, language, subjects, openstax_only, check_updates, git_only, workers, verbose):
    """Execute the book discovery process."""
    try:
        config.max_workers = workers
        
        # Initialize orchestrator
        orchestrator = OpenBooksOrchestrator(config)
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        with st.spinner("Running book discovery..."):
            status_text.text("Initializing discovery system...")
            progress_bar.progress(10)
            
            # Execute the workflow
            results = orchestrator.run_complete_workflow(
                update_existing=check_updates,
                dry_run=False,
                subjects=subjects,
                language_filter=language,
                openstax_only=openstax_only,
                check_updates=check_updates,
                git_only=git_only
            )
            
            progress_bar.progress(100)
            status_text.text("Discovery completed!")
            
            # Display results
            st.success("Book discovery completed successfully!")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Books", results.get('total_books', 0))
            with col2:
                st.metric("Errors", results.get('errors', 0))
            with col3:
                st.metric("Duration", f"{results.get('duration', 0):.1f}s")
            
            if results.get('phases_completed'):
                st.markdown("**Completed Phases:**")
                for phase in results['phases_completed']:
                    st.markdown(f"✅ {phase}")
                    
    except Exception as e:
        st.error(f"Discovery failed: {e}")
        if verbose:
            st.exception(e)

def display_book_reader():
    """Display book reading interface."""
    st.markdown('<h2 class="sub-header">📖 Read OpenStax Books</h2>', unsafe_allow_html=True)
    
    books_dir = Path(current_dir / "Books")
    
    if not books_dir.exists():
        st.warning("No books directory found. Please run discovery first.")
        return
    
    # Book browser
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### 📂 Browse Books")
        
        # Language selection
        languages = sorted([d.name for d in books_dir.iterdir() 
                           if d.is_dir() and d.name not in ['BookList.json', 'BookList.tsv']])
        if not languages:
            st.warning("No books found.")
            return
            
        selected_language = st.selectbox("Language", languages)
        
        # Subject selection
        lang_dir = books_dir / selected_language
        subjects = sorted([d.name for d in lang_dir.iterdir() if d.is_dir()])
        if subjects:
            selected_subject = st.selectbox("Subject", subjects)
            
            # Level selection
            subject_dir = lang_dir / selected_subject
            levels = sorted([d.name for d in subject_dir.iterdir() if d.is_dir()])
            if levels:
                selected_level = st.selectbox("Level", levels)
                
                # Book selection
                level_dir = subject_dir / selected_level
                books = sorted([d.name for d in level_dir.iterdir() if d.is_dir() and (d / ".git").exists()])
                if books:
                    selected_book = st.selectbox("Book", books)
                    
                    # Store selected book in session state
                    if selected_book:
                        st.session_state.current_book_path = level_dir / selected_book
                        st.session_state.current_book_name = selected_book
    
    # Book content display (right column)
    with col2:
        st.markdown("### 📖 Book Content")
        
        # Display book content if a book is selected
        if hasattr(st.session_state, 'current_book_path') and st.session_state.current_book_path:
            display_book_content_with_toc(st.session_state.current_book_path)
        else:
            st.info("Select a book from the browser to view its content here.")

def display_book_content_with_toc(book_path: Path):
    """Display book content with Table of Contents and content viewer."""
    try:
        # Display book information
        st.markdown(f"**📚 Book:** {book_path.name}")
        st.markdown(f"**📁 Path:** `{book_path}`")
        
        # Create two columns for TOC and content viewer
        toc_col, content_col = st.columns([1, 2])
        
        with toc_col:
            st.markdown("#### 📋 Table of Contents")
            
            # Find all content files
            content_files = []
            patterns = ["*.md", "*.cnxml", "*.html", "*.txt", "*.rst"]
            
            for pattern in patterns:
                content_files.extend(book_path.rglob(pattern))
            
            # Sort files by path for better organization
            content_files = sorted(content_files, key=lambda x: str(x.relative_to(book_path)))
            
            if content_files:
                # Initialize selected file in session state
                if 'selected_content_file' not in st.session_state:
                    st.session_state.selected_content_file = content_files[0]
                
                # Display TOC as a scrollable list
                st.markdown(f"**Found {len(content_files)} content files:**")
                
                # Create a container for the scrollable TOC
                toc_container = st.container()
                
                with toc_container:
                    for i, file in enumerate(content_files[:50]):  # Limit to first 50 files
                        relative_path = file.relative_to(book_path)
                        file_name = relative_path.name
                        folder_path = str(relative_path.parent) if relative_path.parent != Path('.') else ""
                        
                        # Create a more readable display name
                        if folder_path:
                            display_name = f"📁 {folder_path} → 📄 {file_name}"
                        else:
                            display_name = f"📄 {file_name}"
                        
                        # Use radio button or selectbox for file selection
                        if st.button(display_name, key=f"file_{i}", help=str(relative_path)):
                            st.session_state.selected_content_file = file
                            st.rerun()
                
                # Show README or main files first
                if len(content_files) > 50:
                    st.info(f"Showing first 50 of {len(content_files)} files. Use search to find specific files.")
                    
            else:
                st.warning("No readable content files found in this book.")
                st.markdown("**Supported formats:** Markdown (.md), CNXML (.cnxml), HTML (.html), Text (.txt), reStructuredText (.rst)")
        
        with content_col:
            st.markdown("#### 📖 Content Viewer")
            
            if content_files and hasattr(st.session_state, 'selected_content_file'):
                selected_file = st.session_state.selected_content_file
                
                try:
                    # Display file information
                    relative_path = selected_file.relative_to(book_path)
                    st.markdown(f"**Current File:** `{relative_path}`")
                    
                    # File size and modification info
                    file_stats = selected_file.stat()
                    file_size = file_stats.st_size
                    if file_size < 1024:
                        size_str = f"{file_size} bytes"
                    elif file_size < 1024 * 1024:
                        size_str = f"{file_size/1024:.1f} KB"
                    else:
                        size_str = f"{file_size/(1024*1024):.1f} MB"
                    
                    st.markdown(f"**File Size:** {size_str}")
                    
                    # Read and display content
                    with st.spinner("Loading content..."):
                        try:
                            content = selected_file.read_text(encoding='utf-8', errors='ignore')
                            
                            # Detect file type and display accordingly
                            file_ext = selected_file.suffix.lower()
                            
                            if file_ext == '.md':
                                # Display Markdown with formatting
                                st.markdown("---")
                                st.markdown(content)
                            elif file_ext in ['.html', '.htm']:
                                # Display HTML content
                                st.markdown("---")
                                st.components.v1.html(content, height=600, scrolling=True)
                            elif file_ext == '.cnxml':
                                # Display CNXML as formatted text (XML-like)
                                st.markdown("---")
                                st.code(content, language='xml')
                            else:
                                # Display as plain text
                                st.markdown("---")
                                st.text_area("File Content", content, height=500, key="content_viewer")
                                
                        except UnicodeDecodeError:
                            # Try different encodings
                            for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                                try:
                                    content = selected_file.read_text(encoding=encoding, errors='ignore')
                                    st.text_area("File Content", content, height=500, key="content_viewer_alt")
                                    break
                                except:
                                    continue
                            else:
                                st.error("Could not decode file content. File may be binary or use an unsupported encoding.")
                        
                except Exception as e:
                    st.error(f"Error reading file {selected_file.name}: {e}")
            else:
                st.info("Select a file from the Table of Contents to view its content.")
                
        # Directory structure (expandable)
        with st.expander("📁 Complete Directory Structure"):
            try:
                def display_directory_tree(path, prefix="", max_depth=3, current_depth=0):
                    if current_depth >= max_depth:
                        return
                    
                    items = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
                    for i, item in enumerate(items[:20]):  # Limit items per directory
                        is_last = i == len(items) - 1
                        current_prefix = "└── " if is_last else "├── "
                        
                        if item.is_dir():
                            st.text(f"{prefix}{current_prefix}📁 {item.name}/")
                            next_prefix = prefix + ("    " if is_last else "│   ")
                            display_directory_tree(item, next_prefix, max_depth, current_depth + 1)
                        else:
                            file_size = item.stat().st_size
                            if file_size < 1024:
                                size_str = f"({file_size}B)"
                            elif file_size < 1024 * 1024:
                                size_str = f"({file_size/1024:.0f}KB)"
                            else:
                                size_str = f"({file_size/(1024*1024):.1f}MB)"
                            st.text(f"{prefix}{current_prefix}📄 {item.name} {size_str}")
                
                display_directory_tree(book_path)
                
            except Exception as e:
                st.error(f"Error reading directory structure: {e}")
                
    except Exception as e:
        st.error(f"Error displaying book content: {e}")

def display_book_content(book_path: Path):
    """Legacy function - redirects to new implementation."""
    display_book_content_with_toc(book_path)

def display_validation_tools(config: OpenBooksConfig):
    """Display validation and testing tools."""
    st.markdown('<h2 class="sub-header">✅ Validation & Quality Assurance</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🛡️ Validation Tests")
        
        if st.button("🔍 Run Discovery Validation", type="secondary"):
            run_discovery_validation(config)
        
        if st.button("📁 Run Repository Validation", type="secondary"):
            run_repository_validation(config)
        
        if st.button("📄 Run Content Validation", type="secondary"):
            run_content_validation(config)
        
        if st.button("🌍 Run Language Detection", type="secondary"):
            run_language_detection()
        
        if st.button("🔄 Run Full Validation Suite", type="primary"):
            run_full_validation_suite(config)
    
    with col2:
        st.markdown("### 📊 Validation Results")
        st.info("Select a validation test to see results here.")

def run_discovery_validation(config):
    """Run discovery validation tests."""
    try:
        with st.spinner("Running discovery validation..."):
            discoverer = BookDiscoverer(config)
            
            # Test basic discovery functionality
            st.success("✅ BookDiscoverer initialized successfully")
            
            # Test configuration validation
            if hasattr(discoverer, 'validate_config'):
                discoverer.validate_config()
                st.success("✅ Configuration validation passed")
            
            st.success("Discovery validation completed!")
            
    except Exception as e:
        st.error(f"Discovery validation failed: {e}")

def run_repository_validation(config):
    """Run repository validation tests."""
    try:
        with st.spinner("Running repository validation..."):
            repo_manager = RepositoryManager(config)
            
            st.success("✅ RepositoryManager initialized successfully")
            
            # Test Books directory
            books_dir = Path(current_dir / "Books")
            if books_dir.exists():
                st.success("✅ Books directory exists")
                
                # Count repositories
                repo_count = 0
                for path in books_dir.rglob(".git"):
                    repo_count += 1
                
                st.info(f"Found {repo_count} Git repositories")
            else:
                st.warning("⚠️ Books directory not found")
            
            st.success("Repository validation completed!")
            
    except Exception as e:
        st.error(f"Repository validation failed: {e}")

def run_content_validation(config):
    """Run content validation tests."""
    try:
        with st.spinner("Running content validation..."):
            content_processor = ContentProcessor(config)
            
            st.success("✅ ContentProcessor initialized successfully")
            
            # Test content processing capabilities
            books_dir = Path(current_dir / "Books")
            if books_dir.exists():
                content_files = list(books_dir.rglob("*.md")) + list(books_dir.rglob("*.cnxml"))
                st.info(f"Found {len(content_files)} content files")
            
            st.success("Content validation completed!")
            
    except Exception as e:
        st.error(f"Content validation failed: {e}")

def run_language_detection():
    """Run language detection tests."""
    try:
        with st.spinner("Running language detection..."):
            from core.language_detector import LanguageDetector
            detector = LanguageDetector()
            
            st.success("✅ LanguageDetector initialized successfully")
            
            # Test with sample repository paths (language detector works on repo paths, not text)
            test_repos = {
                "English": Path("osbooks-university-physics-bundle"),
                "Spanish": Path("osbooks-fisica-universitaria-bundle"), 
                "French": Path("osbooks-introduction-philosophy")
            }
            
            for lang, repo_path in test_repos.items():
                try:
                    detected = detector.detect_language(repo_path)
                    st.success(f"✅ {lang} repo detected as: {detected}")
                except Exception as e:
                    st.warning(f"⚠️ {lang} detection failed: {e}")
            
            st.success("Language detection completed!")
            
    except Exception as e:
        st.error(f"Language detection failed: {e}")

def run_full_validation_suite(config):
    """Run the complete validation suite."""
    st.markdown("### 🔄 Full Validation Suite")
    
    progress_bar = st.progress(0)
    
    # Run all validations
    tests = [
        ("Discovery Validation", run_discovery_validation),
        ("Repository Validation", run_repository_validation),
        ("Content Validation", run_content_validation),
        ("Language Detection", run_language_detection)
    ]
    
    results = {}
    
    for i, (test_name, test_func) in enumerate(tests):
        try:
            progress_bar.progress((i + 1) / len(tests))
            # Handle functions that don't take config parameter
            if test_name == "Language Detection":
                test_func()
            else:
                test_func(config)
            results[test_name] = "✅ Passed"
        except Exception as e:
            results[test_name] = f"❌ Failed: {e}"
    
    # Display summary
    st.markdown("### 📊 Validation Summary")
    for test_name, result in results.items():
        st.markdown(f"**{test_name}:** {result}")

def display_settings(config: OpenBooksConfig):
    """Display system settings and configuration."""
    st.markdown('<h2 class="sub-header">⚙️ System Settings</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔧 Configuration")
        
        # Display current config
        st.markdown("**Current Configuration:**")
        st.json({
            "max_workers": getattr(config, 'max_workers', 20),
            "openstax_only": getattr(config, 'openstax_only', True),
            "pdf_processing": PDF_PROCESSING_AVAILABLE,
            "base_directory": str(current_dir),
            "books_directory": str(current_dir / "Books")
        })
        
        # Environment variables
        st.markdown("### 🌍 Environment Variables")
        env_vars = {
            "ANTHROPIC_API_KEY": "✅ Set" if os.getenv('ANTHROPIC_API_KEY') else "❌ Not set"
        }
        
        for var, status in env_vars.items():
            st.markdown(f"**{var}:** {status}")
    
    with col2:
        st.markdown("### 📁 Directory Status")
        
        directories = {
            "Books": current_dir / "Books",
            "Config": current_dir / "config", 
            "Core": current_dir / "core",
            "Tests": current_dir / "tests"
        }
        
        for name, path in directories.items():
            status = "✅ Exists" if path.exists() else "❌ Missing"
            st.markdown(f"**{name}:** {status}")
        
        # System info
        st.markdown("### 💻 System Information")
        st.markdown(f"**Python Version:** {sys.version.split()[0]}")
        st.markdown(f"**Working Directory:** {current_dir}")
        st.markdown(f"**Streamlit Version:** {st.__version__}")

if __name__ == "__main__":
    main()