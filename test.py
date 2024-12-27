import unittest
from app import format_message

class TestFormatMessage(unittest.TestCase):
    def test_basic_messages(self):
        """Test basic user and assistant messages"""
        user_result = format_message("Hello", "user", "12:30")
        assistant_result = format_message("Hi there", "assistant", "12:31")
        
        # Check correct CSS classes
        self.assertIn('class="user-message"', user_result)
        self.assertIn('class="assistant-message"', assistant_result)
        
        # Check content inclusion
        self.assertIn("Hello", user_result)
        self.assertIn("Hi there", assistant_result)
        
        # Check timestamp inclusion
        self.assertIn("12:30", user_result)
        self.assertIn("12:31", assistant_result)

    def test_messages_with_special_characters(self):
        """Test messages containing HTML special characters"""
        special_chars = "Hello <script>alert('xss')</script> & < > \" '"
        result = format_message(special_chars, "user", "12:30")
        
        # These shouldn't be interpreted as HTML
        self.assertIn("&lt;script&gt;", result)
        self.assertIn("&amp;", result)
        self.assertIn("&lt;", result)
        self.assertIn("&gt;", result)
        self.assertIn("&quot;", result)  # Changed from &#34;
        self.assertIn("&#x27;", result)

    def test_code_blocks(self):
        """Test messages containing markdown code blocks"""
        code_message = """Here's some code:
        ```python
        def hello():
            print("world")
        ```"""
        result = format_message(code_message, "assistant", "12:30")
        
        # Check code block markers are preserved
        self.assertIn("```python", result)
        self.assertIn("def hello():", result)

    def test_empty_messages(self):
        """Test empty or whitespace-only messages"""
        empty_result = format_message("", "user", "12:30")
        space_result = format_message("   ", "user", "12:30")
        
        # Should still create valid HTML
        self.assertIn('class="user-message"', empty_result)
        self.assertIn('class="user-message"', space_result)

    def test_long_messages(self):
        """Test very long messages"""
        long_text = "This is a very long message. " * 100
        result = format_message(long_text, "user", "12:30")
        
        # Should contain the full text
        self.assertIn(long_text, result)

    def test_multiline_messages(self):
        """Test messages with multiple lines and formatting"""
        multiline = """This is line 1
        This is line 2
        
        This is line 4 after a blank line
        * bullet point
        * another point"""
        
        result = format_message(multiline, "assistant", "12:30")
        
        # Check line breaks are preserved
        self.assertIn("line 1", result)
        self.assertIn("line 2", result)
        self.assertIn("line 4", result)
        self.assertIn("bullet point", result)

    def test_urls_and_links(self):
        """Test messages containing URLs and HTML links"""
        message_with_urls = """Check out https://example.com
        And <a href="https://test.com">this link</a>"""
        
        result = format_message(message_with_urls, "user", "12:30")
        
        # URLs should be preserved but HTML should be escaped
        self.assertIn("https://example.com", result)
        self.assertIn("&lt;a href=", result)

    def test_emoji_and_unicode(self):
        """Test messages with emoji and unicode characters"""
        message_with_emoji = "Hello 👋 World 🌍 ! ⭐️ 漢字"
        result = format_message(message_with_emoji, "user", "12:30")
        
        # Unicode characters should be preserved
        self.assertIn("👋", result)
        self.assertIn("🌍", result)
        self.assertIn("⭐️", result)
        self.assertIn("漢字", result)

if __name__ == '__main__':
    unittest.main()
