#!/usr/bin/env python3
"""
CNXML Renderer

This module provides functionality to convert OpenStax CNXML content to 
readable HTML and Markdown formats for display in the ReadOpenBooks interface.
"""

import xml.etree.ElementTree as ET
import re
from pathlib import Path
from typing import Optional, Dict, List
import logging
from html import escape


class CNXMLRenderer:
    """Renderer for converting CNXML content to HTML and Markdown."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Define namespace mappings
        self.namespaces = {
            'cnxml': 'http://cnx.rice.edu/cnxml',
            'm': 'http://www.w3.org/1998/Math/MathML',
            'md': 'http://cnx.rice.edu/mdml'
        }
    
    def parse_cnxml(self, cnxml_content: str) -> Optional[ET.Element]:
        """Parse CNXML content and return the root element."""
        try:
            # Clean up the XML content
            content = cnxml_content.strip()
            
            # Parse the XML
            root = ET.fromstring(content)
            return root
            
        except ET.ParseError as e:
            self.logger.error(f"Failed to parse CNXML: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error parsing CNXML: {e}")
            return None
    
    def extract_title(self, root: ET.Element) -> str:
        """Extract the document title."""
        # Try to find title in the document
        title_elem = root.find('.//title')
        if title_elem is not None and title_elem.text:
            return title_elem.text.strip()
        
        # Fallback to metadata title
        title_elem = root.find('.//md:title', self.namespaces)
        if title_elem is not None and title_elem.text:
            return title_elem.text.strip()
        
        return "Untitled Section"
    
    def render_math(self, math_elem: ET.Element) -> str:
        """Render MathML to a readable format."""
        try:
            # For now, extract text content and format as inline math
            math_text = self.extract_text_content(math_elem)
            if math_text.strip():
                # Basic LaTeX-style formatting
                math_text = math_text.replace('×', ' × ').replace('−', ' - ')
                return f"<em>{math_text}</em>"
            else:
                return "[Mathematical Expression]"
        except Exception as e:
            self.logger.warning(f"Failed to render math: {e}")
            return "[Mathematical Expression]"
    
    def extract_text_content(self, element: ET.Element) -> str:
        """Extract all text content from an element and its children."""
        text_parts = []
        
        if element.text:
            text_parts.append(element.text)
        
        for child in element:
            text_parts.append(self.extract_text_content(child))
            if child.tail:
                text_parts.append(child.tail)
        
        return ''.join(text_parts)
    
    def render_para(self, para_elem: ET.Element) -> str:
        """Render a paragraph element."""
        content_parts = []
        
        # Process text and child elements
        if para_elem.text:
            content_parts.append(escape(para_elem.text))
        
        for child in para_elem:
            tag_name = child.tag.split('}')[-1] if '}' in child.tag else child.tag
            
            if tag_name == 'math' or child.tag.endswith('math'):
                content_parts.append(self.render_math(child))
            elif tag_name == 'term':
                term_text = self.extract_text_content(child)
                content_parts.append(f"<strong>{escape(term_text)}</strong>")
            elif tag_name == 'emphasis':
                emph_text = self.extract_text_content(child)
                effect = child.get('effect', 'italics')
                if effect == 'bold':
                    content_parts.append(f"<strong>{escape(emph_text)}</strong>")
                else:
                    content_parts.append(f"<em>{escape(emph_text)}</em>")
            elif tag_name == 'link':
                link_text = self.extract_text_content(child)
                target = child.get('target-id', '#')
                content_parts.append(f'<a href="#{target}">{escape(link_text)}</a>')
            else:
                # For other elements, just extract text
                content_parts.append(escape(self.extract_text_content(child)))
            
            if child.tail:
                content_parts.append(escape(child.tail))
        
        content = ''.join(content_parts).strip()
        return f"<p>{content}</p>" if content else ""
    
    def render_list(self, list_elem: ET.Element) -> str:
        """Render a list element."""
        list_type = list_elem.get('list-type', 'bulleted')
        tag = 'ol' if list_type == 'enumerated' else 'ul'
        
        items = []
        for item in list_elem.findall('.//item'):
            item_content = self.extract_text_content(item)
            if item_content.strip():
                items.append(f"<li>{escape(item_content.strip())}</li>")
        
        if items:
            items_html = '\n'.join(items)
            return f"<{tag}>\n{items_html}\n</{tag}>"
        
        return ""
    
    def render_figure(self, figure_elem: ET.Element) -> str:
        """Render a figure element."""
        figure_parts = []
        
        # Look for image with namespace handling
        image_elem = figure_elem.find('.//image')
        if image_elem is None:
            # Try different paths
            for elem in figure_elem.iter():
                if elem.tag.endswith('image') or elem.tag == 'image':
                    image_elem = elem
                    break
        
        if image_elem is not None:
            src = image_elem.get('src', '')
            # Get alt text from parent media element if not on image
            alt = image_elem.get('alt', '')
            if not alt:
                media_elem = figure_elem.find('.//media')
                if media_elem is not None:
                    alt = media_elem.get('alt', 'Figure')  
                else:
                    alt = 'Figure'
            
            if src:
                # Make relative paths more explicit
                if src.startswith('../../'):
                    src_display = src.replace('../../', '[Path: ')
                    figure_parts.append(f'<div class="figure-image">[📷 {escape(alt)} - {src_display}]</div>')
                else:
                    figure_parts.append(f'<div class="figure-image">[📷 {escape(alt)}]</div>')
            else:
                figure_parts.append(f'<div class="figure-image">[📷 {escape(alt)}]</div>')
        else:
            # Even if no image, show that it's a figure
            figure_parts.append('<div class="figure-image">[📷 Figure]</div>')
        
        # Look for caption with namespace handling
        caption_elem = figure_elem.find('.//caption')
        if caption_elem is None:
            for elem in figure_elem.iter():
                if elem.tag.endswith('caption') or elem.tag == 'caption':
                    caption_elem = elem
                    break
        
        if caption_elem is not None:
            caption_content = []
            if caption_elem.text:
                caption_content.append(escape(caption_elem.text))
            
            for child in caption_elem:
                tag_name = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                if tag_name == 'math' or child.tag.endswith('math'):
                    caption_content.append(self.render_math(child))
                else:
                    caption_content.append(escape(self.extract_text_content(child)))
                if child.tail:
                    caption_content.append(escape(child.tail))
            
            caption_text = ''.join(caption_content).strip()
            if caption_text:
                figure_parts.append(f'<div class="figure-caption"><em>{caption_text}</em></div>')
        
        if figure_parts:
            return f'<div class="figure">\n{"".join(figure_parts)}\n</div>'
        
        return ""
    
    def render_section(self, section_elem: ET.Element, level: int = 2) -> str:
        """Render a section element."""
        content_parts = []
        
        # Render section title
        title_elem = section_elem.find('./title')
        if title_elem is not None and title_elem.text:
            title_text = escape(title_elem.text.strip())
            content_parts.append(f"<h{level}>{title_text}</h{level}>")
        
        # Process section content
        for child in section_elem:
            if child.tag == 'title':
                continue  # Already handled
            elif child.tag.endswith('}para') or child.tag == 'para':
                rendered = self.render_para(child)
                if rendered:
                    content_parts.append(rendered)
            elif child.tag.endswith('}list') or child.tag == 'list':
                rendered = self.render_list(child)
                if rendered:
                    content_parts.append(rendered)
            elif child.tag.endswith('}figure') or child.tag == 'figure':
                rendered = self.render_figure(child)
                if rendered:
                    content_parts.append(rendered)
            elif child.tag.endswith('}section') or child.tag == 'section':
                rendered = self.render_section(child, level + 1)
                if rendered:
                    content_parts.append(rendered)
        
        return '\n\n'.join(content_parts)
    
    def render_content(self, content_elem: ET.Element) -> str:
        """Render the main content element."""
        content_parts = []
        
        for child in content_elem:
            tag_name = child.tag.split('}')[-1] if '}' in child.tag else child.tag
            
            if tag_name == 'para':
                rendered = self.render_para(child)
                if rendered:
                    content_parts.append(rendered)
            elif tag_name == 'section':
                rendered = self.render_section(child)
                if rendered:
                    content_parts.append(rendered)
            elif tag_name == 'figure':
                rendered = self.render_figure(child)
                if rendered:
                    content_parts.append(rendered)
            elif tag_name == 'list':
                rendered = self.render_list(child)
                if rendered:
                    content_parts.append(rendered)
            else:
                # Debug: show what we're skipping
                self.logger.debug(f"Skipping element: {child.tag}")
        
        return '\n\n'.join(content_parts)
    
    def cnxml_to_html(self, cnxml_content: str) -> Dict[str, str]:
        """Convert CNXML content to HTML."""
        try:
            root = self.parse_cnxml(cnxml_content)
            if root is None:
                return {
                    'title': 'Error',
                    'content': '<p>Failed to parse CNXML content.</p>',
                    'raw_content': cnxml_content[:500] + '...' if len(cnxml_content) > 500 else cnxml_content
                }
            
            # Extract title
            title = self.extract_title(root)
            
            # Find and render content - try different approaches
            content_elem = root.find('.//content')
            if content_elem is None:
                # Try with namespace
                content_elem = root.find('.//{http://cnx.rice.edu/cnxml}content')
            if content_elem is None:
                # Try finding content without namespace
                for elem in root.iter():
                    if elem.tag.endswith('content'):
                        content_elem = elem
                        break
            
            if content_elem is not None:
                rendered_content = self.render_content(content_elem)
                if not rendered_content.strip():
                    # Fallback: render all child elements
                    fallback_parts = []
                    for child in content_elem:
                        if child.tag.endswith('figure') or child.tag == 'figure':
                            fallback_parts.append(self.render_figure(child))
                        elif child.text:
                            fallback_parts.append(f"<p>{escape(child.text.strip())}</p>")
                    rendered_content = '\n\n'.join(filter(None, fallback_parts))
            else:
                rendered_content = "<p>No content found in document.</p>"
            
            # Add basic CSS styling
            styled_content = f"""
            <div class="cnxml-content">
                <style>
                    .cnxml-content {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; line-height: 1.6; }}
                    .cnxml-content h2 {{ color: #2E8B57; border-bottom: 2px solid #2E8B57; }}
                    .cnxml-content h3 {{ color: #4682B4; }}
                    .cnxml-content p {{ margin: 1em 0; }}
                    .cnxml-content .figure {{ margin: 1.5em 0; padding: 1em; background-color: #f8f9fa; border-left: 4px solid #007bff; }}
                    .cnxml-content .figure-image {{ font-weight: bold; color: #007bff; }}
                    .cnxml-content .figure-caption {{ margin-top: 0.5em; font-size: 0.9em; }}
                    .cnxml-content ul, .cnxml-content ol {{ margin: 1em 0; padding-left: 2em; }}
                    .cnxml-content li {{ margin: 0.5em 0; }}
                    .cnxml-content strong {{ color: #d63384; }}
                    .cnxml-content em {{ color: #6f42c1; }}
                </style>
                {rendered_content}
            </div>
            """
            
            return {
                'title': title,
                'content': styled_content,
                'raw_content': cnxml_content
            }
            
        except Exception as e:
            self.logger.error(f"Error converting CNXML to HTML: {e}")
            return {
                'title': 'Error',
                'content': f'<p>Error rendering content: {e}</p>',
                'raw_content': cnxml_content[:500] + '...' if len(cnxml_content) > 500 else cnxml_content
            }
    
    def cnxml_to_markdown(self, cnxml_content: str) -> Dict[str, str]:
        """Convert CNXML content to Markdown (simplified version)."""
        try:
            # First convert to HTML, then simplify to Markdown-like format
            html_result = self.cnxml_to_html(cnxml_content)
            
            # Basic HTML to Markdown conversion
            content = html_result['content']
            
            # Remove CSS styling
            content = re.sub(r'<style>.*?</style>', '', content, flags=re.DOTALL)
            content = re.sub(r'<div class="cnxml-content">', '', content)
            content = content.replace('</div>', '')
            
            # Convert HTML tags to Markdown
            content = re.sub(r'<h2>(.*?)</h2>', r'## \1', content)
            content = re.sub(r'<h3>(.*?)</h3>', r'### \1', content)
            content = re.sub(r'<h4>(.*?)</h4>', r'#### \1', content)
            content = re.sub(r'<p>(.*?)</p>', r'\1\n', content)
            content = re.sub(r'<strong>(.*?)</strong>', r'**\1**', content)
            content = re.sub(r'<em>(.*?)</em>', r'*\1*', content)
            content = re.sub(r'<li>(.*?)</li>', r'- \1', content)
            content = re.sub(r'<ul>|</ul>|<ol>|</ol>', '', content)
            
            # Clean up extra whitespace
            content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
            content = content.strip()
            
            return {
                'title': html_result['title'],
                'content': content,
                'raw_content': html_result['raw_content']
            }
            
        except Exception as e:
            self.logger.error(f"Error converting CNXML to Markdown: {e}")
            return {
                'title': 'Error',
                'content': f'Error rendering content: {e}',
                'raw_content': cnxml_content[:500] + '...' if len(cnxml_content) > 500 else cnxml_content
            }


def test_cnxml_renderer():
    """Test the CNXML renderer with sample content."""
    renderer = CNXMLRenderer()
    
    # Test with a sample file
    test_file = Path("/Users/davidlary/Dropbox/Environments/Code/Pedegree/OpenBooks/Books/english/Physics/University/osbooks-university-physics-bundle/modules/m58268/index.cnxml")
    
    if test_file.exists():
        print(f"Testing CNXML renderer with: {test_file}")
        
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                cnxml_content = f.read()
            
            print(f"CNXML content length: {len(cnxml_content)} characters")
            
            # Test HTML conversion
            html_result = renderer.cnxml_to_html(cnxml_content)
            print(f"\n📄 Title: {html_result['title']}")
            print(f"📝 HTML content length: {len(html_result['content'])} characters")
            print(f"🔍 HTML preview:\n{html_result['content'][:500]}...")
            
            # Test Markdown conversion
            md_result = renderer.cnxml_to_markdown(cnxml_content)
            print(f"\n📝 Markdown content length: {len(md_result['content'])} characters")
            print(f"🔍 Markdown preview:\n{md_result['content'][:300]}...")
            
            return True
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            return False
    else:
        print(f"❌ Test file not found: {test_file}")
        return False


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Run test
    success = test_cnxml_renderer()
    print(f"\n{'✅ CNXML Renderer test passed!' if success else '❌ CNXML Renderer test failed!'}")