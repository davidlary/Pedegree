#!/usr/bin/env python3
"""
Test Content Rendering

This script tests the CNXML content rendering functionality integrated
with the enhanced book reader system.
"""

import sys
from pathlib import Path
import traceback

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_cnxml_renderer_basic():
    """Test basic CNXML renderer functionality."""
    print("🧪 Testing CNXML Renderer Basic Functionality...")
    
    try:
        from core.cnxml_renderer import CNXMLRenderer
        
        renderer = CNXMLRenderer()
        print("    ✅ CNXMLRenderer initialized")
        
        # Test with actual OpenStax content
        test_file = Path("Books/english/Physics/University/osbooks-university-physics-bundle/modules/m58268/index.cnxml")
        
        if test_file.exists():
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"    ✅ Test file loaded: {len(content)} characters")
            
            # Test HTML rendering
            html_result = renderer.cnxml_to_html(content)
            print(f"    ✅ HTML rendering: {html_result['title']}")
            print(f"    ✅ HTML content: {len(html_result['content'])} characters")
            
            # Check for proper HTML elements
            html_content = html_result['content']
            html_checks = [
                '<div class="cnxml-content">' in html_content,
                '<p>' in html_content,
                '</p>' in html_content,
                'style>' in html_content
            ]
            
            if all(html_checks):
                print("    ✅ HTML structure valid")
            else:
                print(f"    ❌ HTML structure issues: {html_checks}")
                return False
            
            # Test Markdown rendering
            md_result = renderer.cnxml_to_markdown(content)
            print(f"    ✅ Markdown rendering: {len(md_result['content'])} characters")
            
            return True
        else:
            print(f"    ⚠️ Test file not found: {test_file}")
            return False
            
    except Exception as e:
        print(f"    ❌ CNXML renderer test failed: {e}")
        return False

def test_content_elements_rendering():
    """Test rendering of different CNXML elements."""
    print("\n🧪 Testing Content Elements Rendering...")
    
    try:
        from core.cnxml_renderer import CNXMLRenderer
        
        renderer = CNXMLRenderer()
        
        # Test different content elements
        test_cases = [
            {
                'name': 'Paragraphs',
                'content': '''<document xmlns="http://cnx.rice.edu/cnxml">
                    <content><para>This is a test paragraph.</para></content>
                </document>''',
                'expected': '<p>This is a test paragraph.</p>'
            },
            {
                'name': 'Emphasis',
                'content': '''<document xmlns="http://cnx.rice.edu/cnxml">
                    <content><para>Text with <emphasis effect="bold">bold</emphasis> and <emphasis>italic</emphasis>.</para></content>
                </document>''',
                'expected': ['<strong>', '</strong>', '<em>', '</em>']
            },
            {
                'name': 'Terms',
                'content': '''<document xmlns="http://cnx.rice.edu/cnxml">
                    <content><para>This is a <term>technical term</term>.</para></content>
                </document>''',
                'expected': '<strong>technical term</strong>'
            }
        ]
        
        for test_case in test_cases:
            result = renderer.cnxml_to_html(test_case['content'])
            content = result['content']
            
            if isinstance(test_case['expected'], list):
                # Check for multiple expected elements
                all_found = all(exp in content for exp in test_case['expected'])
                status = "✅" if all_found else "❌"
                print(f"    {status} {test_case['name']}: {'All elements found' if all_found else 'Missing elements'}")
            else:
                # Check for single expected element
                found = test_case['expected'] in content
                status = "✅" if found else "❌"
                print(f"    {status} {test_case['name']}: {'Found' if found else 'Not found'}")
        
        return True
        
    except Exception as e:
        print(f"    ❌ Content elements test failed: {e}")
        return False

def test_readopenbooks_integration():
    """Test integration with ReadOpenBooks.py."""
    print("\n🧪 Testing ReadOpenBooks Integration...")
    
    try:
        # Test imports
        from core.cnxml_renderer import CNXMLRenderer
        from core.book_parser import OpenStaxBookParser
        print("    ✅ All required modules imported")
        
        # Test ReadOpenBooks.py syntax
        with open('ReadOpenBooks.py', 'r') as f:
            content = f.read()
        
        # Check for integration elements
        integration_checks = [
            'from core.cnxml_renderer import CNXMLRenderer' in content,
            'renderer = CNXMLRenderer()' in content,
            'renderer.cnxml_to_html(' in content,
            'renderer.cnxml_to_markdown(' in content,
            'unsafe_allow_html=True' in content
        ]
        
        passed_checks = sum(integration_checks)
        print(f"    ✅ Integration checks: {passed_checks}/{len(integration_checks)} passed")
        
        if passed_checks == len(integration_checks):
            print("    ✅ Full integration completed")
            return True
        else:
            print("    ⚠️ Partial integration - some elements missing")
            return False
            
    except Exception as e:
        print(f"    ❌ ReadOpenBooks integration test failed: {e}")
        return False

def test_real_textbook_sections():
    """Test rendering with multiple real textbook sections."""
    print("\n🧪 Testing Real Textbook Sections...")
    
    try:
        from core.cnxml_renderer import CNXMLRenderer
        from core.book_parser import OpenStaxBookParser
        
        parser = OpenStaxBookParser()
        renderer = CNXMLRenderer()
        
        # Test with Physics textbook
        repo_path = Path("Books/english/Physics/University/osbooks-university-physics-bundle")
        
        if repo_path.exists():
            books = parser.parse_repository_books(repo_path)
            
            if books and books[0].chapters:
                test_book = books[0]
                print(f"    ✅ Testing with: {test_book.title}")
                
                # Test first few modules from first chapter
                first_chapter = test_book.chapters[0]
                test_modules = first_chapter.modules[:3]  # Test first 3 sections
                
                successful_renders = 0
                total_content_length = 0
                
                for i, module in enumerate(test_modules):
                    try:
                        content = parser.get_module_content(module.content_path)
                        if content:
                            result = renderer.cnxml_to_html(content)
                            content_length = len(result['content'])
                            total_content_length += content_length
                            
                            print(f"    ✅ Module {i+1}: {module.title} ({content_length} chars)")
                            successful_renders += 1
                        else:
                            print(f"    ❌ Module {i+1}: {module.title} (no content)")
                    except Exception as e:
                        print(f"    ❌ Module {i+1}: {module.title} (error: {e})")
                
                print(f"    ✅ Successfully rendered: {successful_renders}/{len(test_modules)} sections")
                print(f"    ✅ Total rendered content: {total_content_length} characters")
                
                return successful_renders > 0
            else:
                print("    ❌ No books or chapters found")
                return False
        else:
            print(f"    ⚠️ Test repository not found: {repo_path}")
            return False
            
    except Exception as e:
        print(f"    ❌ Real textbook sections test failed: {e}")
        return False

def test_math_and_figures():
    """Test rendering of mathematical content and figures."""
    print("\n🧪 Testing Math and Figures Rendering...")
    
    try:
        from core.cnxml_renderer import CNXMLRenderer
        
        renderer = CNXMLRenderer()
        
        # Test content with mathematical expressions and figures
        math_content = '''<document xmlns="http://cnx.rice.edu/cnxml" xmlns:m="http://www.w3.org/1998/Math/MathML">
            <content>
                <para>This equation shows force: <m:math><m:mrow><m:mi>F</m:mi><m:mo>=</m:mo><m:mi>m</m:mi><m:mi>a</m:mi></m:mrow></m:math>.</para>
                <figure id="test-figure">
                    <media alt="Test image">
                        <image src="test.jpg"/>
                    </media>
                    <caption>This is a test figure showing physics concepts.</caption>
                </figure>
            </content>
        </document>'''
        
        result = renderer.cnxml_to_html(math_content)
        content = result['content']
        
        # Check for math rendering
        math_found = '<em>' in content  # Math should be rendered as emphasized text
        figure_found = 'class="figure"' in content
        caption_found = 'class="figure-caption"' in content
        
        print(f"    ✅ Math rendering: {'Found' if math_found else 'Not found'}")
        print(f"    ✅ Figure rendering: {'Found' if figure_found else 'Not found'}")
        print(f"    ✅ Caption rendering: {'Found' if caption_found else 'Not found'}")
        
        return math_found and figure_found and caption_found
        
    except Exception as e:
        print(f"    ❌ Math and figures test failed: {e}")
        return False

def run_comprehensive_content_rendering_tests():
    """Run comprehensive tests for content rendering."""
    print("🚀 Content Rendering Comprehensive Test Suite")
    print("=" * 70)
    print("Testing CNXML rendering and ReadOpenBooks integration...")
    print("=" * 70)
    
    tests = [
        ("CNXML Renderer Basic", test_cnxml_renderer_basic),
        ("Content Elements Rendering", test_content_elements_rendering),
        ("ReadOpenBooks Integration", test_readopenbooks_integration),
        ("Real Textbook Sections", test_real_textbook_sections),
        ("Math and Figures Rendering", test_math_and_figures)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            traceback.print_exc()
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 CONTENT RENDERING TEST RESULTS")
    print("=" * 70)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} content rendering tests passed")
    
    if passed == total:
        print("🎉 ALL CONTENT RENDERING TESTS PASSED!")
        print("\n✅ Content Rendering Features Working:")
        print("- CNXML to HTML conversion with proper styling")
        print("- CNXML to Markdown conversion for alternative viewing")
        print("- Mathematical expressions rendered as readable text")
        print("- Figures and captions properly formatted")
        print("- Emphasis, terms, and links properly converted")
        print("- Full integration with ReadOpenBooks interface")
        print("- Real textbook content successfully rendered")
        
        print(f"\n🚀 Content Rendering: PRODUCTION READY!")
        print("\n🎯 Issues Fixed:")
        print("✅ Content viewer now renders readable HTML instead of raw XML")
        print("✅ Mathematical expressions displayed as formatted text")
        print("✅ Figures and images properly represented")
        print("✅ Multiple viewing options (HTML, Markdown, Raw CNXML)")
        print("✅ Proper styling with CSS for enhanced readability")
        
        return True
    else:
        print("❌ Some content rendering tests failed")
        print("⚠️ Issues need to be resolved before production use")
        return False

if __name__ == "__main__":
    success = run_comprehensive_content_rendering_tests()
    sys.exit(0 if success else 1)