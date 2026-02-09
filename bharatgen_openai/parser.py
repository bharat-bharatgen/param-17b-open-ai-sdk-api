"""Parser for Gradio HTML/SSE responses."""

import json
import re
from html.parser import HTMLParser
from typing import Optional, Iterator


class GradioHTMLParser(HTMLParser):
    """Custom HTML parser to filter out thought process and debug info."""

    def __init__(self):
        super().__init__()
        self.result = []
        self.skip_section = False
        self.in_details = False
        self.details_class = None

    def handle_starttag(self, tag, attrs):
        """Track opening tags and filter thought/debug sections."""
        attrs_dict = dict(attrs)

        # Check for details tags
        if tag == "details":
            self.in_details = True
            self.details_class = attrs_dict.get("class", "")
            self.details_style = attrs_dict.get("style", "")

            # Skip thought process details
            if "thought" in self.details_class:
                self.skip_section = True
            # Skip debug details (check for opacity or font-size in style)
            elif "opacity" in self.details_style or ("font-size" in self.details_style and "0.85em" in self.details_style):
                self.skip_section = True

        # Check for metadata divs (latency info)
        elif tag == "div" and "style" in attrs_dict:
            style = attrs_dict.get("style", "")
            # Skip divs with latency info (color:#666, border-top, etc.)
            if ("color" in style and "#666" in style) or "border-top" in style:
                self.skip_section = True

    def handle_endtag(self, tag):
        """Track closing tags and reset filters."""
        if tag == "details":
            self.in_details = False
            self.skip_section = False
            self.details_class = None
            self.details_style = None
        elif tag == "div":
            # Reset skip on div close
            if self.skip_section and not self.in_details:
                self.skip_section = False

    def handle_data(self, data):
        """Collect data that's not in filtered sections."""
        if not self.skip_section:
            # Only add non-empty, non-whitespace-only data
            text = data.strip()
            if text and text not in ['🧠 Thinking...', '🔍 Debug: Raw Response']:
                self.result.append(text)

    def get_text(self) -> str:
        """Get the cleaned text result."""
        # Join and clean up any duplicate text or special characters
        text = " ".join(self.result)
        # Remove the � character that appears in responses
        text = text.replace('\ufffd', '')
        return text.strip()


class GradioResponseParser:
    """Parser for Gradio SSE responses."""

    def __init__(self):
        self.html_parser = GradioHTMLParser()

    def parse_sse_line(self, line: str) -> Optional[dict]:
        """Parse a single SSE line.

        Args:
            line: SSE formatted line (e.g., "event: message" or "data: {...}")

        Returns:
            Parsed data dict if it's a data line, None otherwise
        """
        line = line.strip()

        # Skip empty lines and event lines
        if not line or line.startswith("event:"):
            return None

        # Parse data lines
        if line.startswith("data:"):
            data_str = line[5:].strip()

            # Skip empty data
            if not data_str:
                return None

            try:
                return json.loads(data_str)
            except json.JSONDecodeError:
                return None

        return None

    def extract_content(self, data: dict) -> Optional[str]:
        """Extract clean text content from Gradio response data.

        Gradio structure: [[{user_msg}, {assistant_msg}], ""]
        We want: data[0][1]['content'][0]['text']

        Args:
            data: Parsed JSON data from Gradio SSE response

        Returns:
            Clean text content, or None if no content found
        """
        try:
            # Check if data is a list with at least one element
            if not isinstance(data, list) or len(data) == 0:
                return None

            # Get the inner list: [[user, assistant], ""] -> [user, assistant]
            messages = data[0]
            if not isinstance(messages, list) or len(messages) < 2:
                return None

            # Get the assistant message (second element)
            assistant_msg = messages[1]
            if not isinstance(assistant_msg, dict):
                return None

            # Get the content array from assistant message
            if "content" not in assistant_msg:
                return None

            content_list = assistant_msg["content"]
            if not isinstance(content_list, list) or len(content_list) == 0:
                return None

            # Get the first content item
            text_item = content_list[0]
            if not isinstance(text_item, dict) or "text" not in text_item:
                return None

            html_text = text_item["text"]

            # Parse HTML to remove thought process and debug info
            self.html_parser = GradioHTMLParser()  # Reset parser
            self.html_parser.feed(html_text)
            clean_text = self.html_parser.get_text()

            return clean_text if clean_text else None

        except (KeyError, IndexError, TypeError):
            return None

    def parse_streaming_response(self, response) -> Iterator[str]:
        """Parse streaming SSE response from Gradio.

        Args:
            response: requests.Response object with streaming content

        Yields:
            Clean text deltas (incremental content)
        """
        previous_content = ""

        for line in response.iter_lines(decode_unicode=True):
            if not line:
                continue

            # Parse SSE line
            data = self.parse_sse_line(line)
            if data is None:
                continue

            # Extract content
            current_content = self.extract_content(data)
            if current_content is None:
                continue

            # Calculate delta (new content since last update)
            if len(current_content) > len(previous_content):
                delta = current_content[len(previous_content):]
                previous_content = current_content
                yield delta

    def parse_complete_response(self, response) -> Optional[str]:
        """Parse complete (non-streaming) response from Gradio.

        Args:
            response: requests.Response object

        Returns:
            Complete clean text content
        """
        # For non-streaming, we still need to parse SSE format
        # Just get the final content
        final_content = None

        for line in response.iter_lines(decode_unicode=True):
            if not line:
                continue

            data = self.parse_sse_line(line)
            if data is None:
                continue

            content = self.extract_content(data)
            if content is not None:
                final_content = content

        return final_content
