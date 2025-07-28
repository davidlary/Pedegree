#!/usr/bin/env python3
"""
OpenStax Book Parser

This module provides comprehensive parsing capabilities for OpenStax textbook collections.
It handles collection XML files and module structures to create proper table of contents
and content navigation.
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import logging
from dataclasses import dataclass


@dataclass
class BookModule:
    """Represents a single module/section in a book."""
    id: str
    title: str
    content_path: Path
    content: Optional[str] = None


@dataclass
class BookChapter:
    """Represents a chapter in a book."""
    title: str
    modules: List[BookModule]


@dataclass
class Book:
    """Represents a complete OpenStax book."""
    title: str
    language: str
    uuid: str
    slug: str
    chapters: List[BookChapter]
    collection_path: Path


class OpenStaxBookParser:
    """Parser for OpenStax textbook collections and modules."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def detect_book_collections(self, repository_path: Path) -> List[Path]:
        """Detect all book collections in a repository."""
        collections_dir = repository_path / "collections"
        
        if not collections_dir.exists():
            self.logger.warning(f"No collections directory found in {repository_path}")
            return []
        
        collection_files = list(collections_dir.glob("*.collection.xml"))
        self.logger.info(f"Found {len(collection_files)} book collections in {repository_path}")
        
        return sorted(collection_files)
    
    def parse_collection_metadata(self, collection_path: Path) -> Dict[str, str]:
        """Parse basic metadata from a collection XML file."""
        try:
            tree = ET.parse(collection_path)
            root = tree.getroot()
            
            # Define namespaces
            namespaces = {
                'col': 'http://cnx.rice.edu/collxml',
                'md': 'http://cnx.rice.edu/mdml'
            }
            
            metadata = {}
            
            # Extract metadata - try different paths
            metadata_elem = (root.find('col:metadata', namespaces) or 
                           root.find('metadata') or 
                           root.find('.//metadata'))
            if metadata_elem is not None:
                title_elem = metadata_elem.find('md:title', namespaces) or metadata_elem.find('title')
                if title_elem is not None and title_elem.text:
                    metadata['title'] = title_elem.text.strip()
                
                lang_elem = metadata_elem.find('md:language', namespaces) or metadata_elem.find('language')
                if lang_elem is not None and lang_elem.text:
                    metadata['language'] = lang_elem.text.strip()
                
                # Find UUID and slug by iterating through children
                for child in metadata_elem:
                    if child.tag == '{http://cnx.rice.edu/mdml}uuid' and child.text:
                        metadata['uuid'] = child.text.strip()
                    elif child.tag == '{http://cnx.rice.edu/mdml}slug' and child.text:
                        metadata['slug'] = child.text.strip()
            
            # Fallback: try to extract title from filename if not found
            if 'title' not in metadata or not metadata['title']:
                # Convert filename to title
                filename = collection_path.stem
                title = filename.replace('-', ' ').replace('_', ' ').title()
                if title.endswith('.Collection'):
                    title = title[:-11]  # Remove .Collection suffix
                metadata['title'] = title
            
            # Set defaults
            metadata.setdefault('language', 'en')
            metadata.setdefault('uuid', '')
            metadata.setdefault('slug', '')
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Error parsing collection metadata from {collection_path}: {e}")
            # Fallback title from filename
            title = collection_path.stem.replace('-', ' ').replace('_', ' ').title()
            return {"title": title, "language": "en", "uuid": "", "slug": ""}
    
    def parse_book_structure(self, collection_path: Path) -> Optional[Book]:
        """Parse the complete structure of a book from its collection XML."""
        try:
            tree = ET.parse(collection_path)
            root = tree.getroot()
            
            # Define namespaces
            namespaces = {
                'col': 'http://cnx.rice.edu/collxml',
                'md': 'http://cnx.rice.edu/mdml'
            }
            
            # Get metadata
            metadata = self.parse_collection_metadata(collection_path)
            
            # Parse content structure
            chapters = []
            content_elem = root.find('.//col:content', namespaces)
            
            if content_elem is not None:
                # Find all subcollections (chapters)
                subcollections = content_elem.findall('.//col:subcollection', namespaces)
                
                for subcoll in subcollections:
                    chapter_title_elem = subcoll.find('md:title', namespaces)
                    chapter_title = chapter_title_elem.text if chapter_title_elem is not None else "Untitled Chapter"
                    
                    # Find modules in this chapter
                    modules = []
                    module_elems = subcoll.findall('.//col:module', namespaces)
                    
                    for module_elem in module_elems:
                        module_id = module_elem.get('document', '')
                        if module_id:
                            # Find the module content path
                            modules_dir = collection_path.parent.parent / "modules"
                            module_path = modules_dir / module_id / "index.cnxml"
                            
                            # Get module title from its content
                            module_title = self.get_module_title(module_path) or f"Module {module_id}"
                            
                            module = BookModule(
                                id=module_id,
                                title=module_title,
                                content_path=module_path
                            )
                            modules.append(module)
                    
                    if modules:  # Only add chapters that have modules
                        chapter = BookChapter(title=chapter_title, modules=modules)
                        chapters.append(chapter)
            
            # Create and return the book
            book = Book(
                title=metadata.get('title', 'Untitled Book'),
                language=metadata.get('language', 'en'),
                uuid=metadata.get('uuid', ''),
                slug=metadata.get('slug', ''),
                chapters=chapters,
                collection_path=collection_path
            )
            
            self.logger.info(f"Parsed book '{book.title}' with {len(chapters)} chapters")
            return book
            
        except Exception as e:
            self.logger.error(f"Error parsing book structure from {collection_path}: {e}")
            return None
    
    def get_module_title(self, module_path: Path) -> Optional[str]:
        """Extract the title from a module's CNXML file."""
        if not module_path.exists():
            return None
        
        try:
            tree = ET.parse(module_path)
            root = tree.getroot()
            
            # Try to find title in metadata first
            namespaces = {'md': 'http://cnx.rice.edu/mdml'}
            title_elem = root.find('.//md:title', namespaces)
            
            if title_elem is not None and title_elem.text:
                return title_elem.text.strip()
            
            # Fallback to document title element
            title_elem = root.find('.//title')
            if title_elem is not None and title_elem.text:
                return title_elem.text.strip()
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Could not extract title from {module_path}: {e}")
            return None
    
    def get_module_content(self, module_path: Path) -> Optional[str]:
        """Extract the content from a module's CNXML file."""
        if not module_path.exists():
            return None
        
        try:
            with open(module_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            self.logger.error(f"Error reading module content from {module_path}: {e}")
            return None
    
    def parse_repository_books(self, repository_path: Path) -> List[Book]:
        """Parse all books in a repository."""
        collection_files = self.detect_book_collections(repository_path)
        books = []
        
        for collection_file in collection_files:
            book = self.parse_book_structure(collection_file)
            if book:
                books.append(book)
        
        self.logger.info(f"Successfully parsed {len(books)} books from {repository_path}")
        return books
    
    def get_book_summary(self, book: Book) -> Dict[str, Any]:
        """Get a summary of a book's structure."""
        total_modules = sum(len(chapter.modules) for chapter in book.chapters)
        
        return {
            'title': book.title,
            'language': book.language,
            'chapters': len(book.chapters),
            'total_sections': total_modules,
            'chapter_list': [
                {
                    'title': chapter.title,
                    'sections': len(chapter.modules)
                }
                for chapter in book.chapters
            ]
        }


def test_book_parser():
    """Test the book parser with a sample repository."""
    parser = OpenStaxBookParser()
    
    # Test with the university physics bundle
    test_repo = Path("/Users/davidlary/Dropbox/Environments/Code/Pedegree/OpenBooks/Books/english/Physics/University/osbooks-university-physics-bundle")
    
    if test_repo.exists():
        print(f"Testing book parser with: {test_repo}")
        
        # Test collection detection
        collections = parser.detect_book_collections(test_repo)
        print(f"Found {len(collections)} collections:")
        for collection in collections:
            print(f"  - {collection.name}")
        
        # Test book parsing
        books = parser.parse_repository_books(test_repo)
        print(f"\nParsed {len(books)} books:")
        
        for book in books:
            summary = parser.get_book_summary(book)
            print(f"\n📚 {summary['title']}")
            print(f"   Chapters: {summary['chapters']}, Total Sections: {summary['total_sections']}")
            
            for i, chapter in enumerate(summary['chapter_list'], 1):
                print(f"   {i}. {chapter['title']} ({chapter['sections']} sections)")
        
        return books
    else:
        print(f"Test repository not found: {test_repo}")
        return []


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Run test
    test_books = test_book_parser()