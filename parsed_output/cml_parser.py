# [[cc.block.metadata]]
'''
File: cml_parser.py
Version: 1.1.0
Last Updated: 2024-09-29
Description: Enhanced parser for Cogni Markup Language (CML) used in CogniCoder output and code blocks
'''
# [[/cc.block.metadata]]

# [[cc.block.imports]]
import re
from typing import Dict, List, Tuple, Generator, Optional
import io
import json
# [[/cc.block.imports]]

# [[cc.block.constants]]
OUT_PATTERN = r'\[\[cc\.out\.(\w+)\]\](.*?)\[\[/cc\.out\.\1\]\]'
BLOCK_PATTERN = r'(?:^|\n)(?:#\s*)?\[\[cc\.block((?:\.\w+)*)\]\](.*?)(?:#\s*)?\[\[/cc\.block\1\]\]'
CML_SYNTAX_ERROR = "CML Syntax Error: {}"
# [[/cc.block.constants]]

# [[cc.block.class.CMLParser]]
class CMLParser:
    """Enhanced parser for Cogni Markup Language (CML) used in CogniCoder output and code blocks"""

    # [[cc.block.method.init]]
    def __init__(self):
        """Initialize the CMLParser."""
        self.out_regex = re.compile(OUT_PATTERN, re.DOTALL)
        self.block_regex = re.compile(BLOCK_PATTERN, re.DOTALL)
    # [[/cc.block.method.init]]

    # [[cc.block.method.parse_out_blocks]]
    def parse_out_blocks(self, content: str) -> Dict[str, str]:
        """
        Parse cc.out blocks from the given content.

        Args:
            content (str): The content containing cc.out blocks.

        Returns:
            Dict[str, str]: A dictionary of parsed cc.out blocks.

        Raises:
            ValueError: If the CML syntax is invalid.
        """
        try:
            return dict(self.out_regex.findall(content))
        except Exception as e:
            raise ValueError(CML_SYNTAX_ERROR.format(str(e)))
    # [[/cc.block.method.parse_out_blocks]]

    # [[cc.block.method.parse_code_blocks]]
    def parse_code_blocks(self, content: str) -> List[Tuple[str, str]]:
        """
        Parse cc.block blocks from the given content.

        Args:
            content (str): The content containing cc.block blocks.

        Returns:
            List[Tuple[str, str]]: A list of tuples containing block identifiers and their content.

        Raises:
            ValueError: If the CML syntax is invalid.
        """
        try:
            return [(tag.strip('.'), block_content) for tag, block_content in self.block_regex.findall(content)]
        except Exception as e:
            raise ValueError(CML_SYNTAX_ERROR.format(str(e)))
    # [[/cc.block.method.parse_code_blocks]]

    # [[cc.block.method.parse_file]]
    def parse_file(self, file_path: str) -> Dict[str, List[Tuple[str, str]]]:
        """
        Parse a file containing CML blocks.

        Args:
            file_path (str): Path to the file to be parsed.

        Returns:
            Dict[str, List[Tuple[str, str]]]: A dictionary with 'out' and 'block' keys containing parsed blocks.

        Raises:
            FileNotFoundError: If the specified file is not found.
            ValueError: If the CML syntax is invalid.
        """
        try:
            with open(file_path, 'r') as file:
                content = file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")

        return self.parse_content(content)
    # [[/cc.block.method.parse_file]]

    # [[cc.block.method.parse_content]]
    def parse_content(self, content: str) -> Dict[str, List[Tuple[str, str]]]:
        """
        Parse a string containing CML blocks.

        Args:
            content (str): The string containing CML blocks.

        Returns:
            Dict[str, List[Tuple[str, str]]]: A dictionary with 'out' and 'block' keys containing parsed blocks.

        Raises:
            ValueError: If the CML syntax is invalid.
        """
        try:
            return {
                'out': self.parse_out_blocks(content),
                'block': self.parse_code_blocks(content)
            }
        except ValueError as e:
            raise ValueError(f"Error parsing content: {str(e)}")
    # [[/cc.block.method.parse_content]]

    # [[cc.block.method.parse_stream]]
    def parse_stream(self, stream: io.TextIOBase) -> Generator[Dict[str, str], None, None]:
        """
        Parse a stream of CML content, yielding parsed blocks as they are encountered.

        Args:
            stream (io.TextIOBase): A text stream containing CML content.

        Yields:
            Dict[str, str]: A dictionary containing the parsed block type and content.

        Raises:
            ValueError: If the CML syntax is invalid.
        """
        buffer = ""
        for line in stream:
            buffer += line
            out_matches = list(self.out_regex.finditer(buffer))
            block_matches = list(self.block_regex.finditer(buffer))
            
            for match in out_matches + block_matches:
                if match.re is self.out_regex:
                    yield {'type': 'out', 'tag': match.group(1), 'content': match.group(2)}
                else:
                    yield {'type': 'block', 'tag': match.group(1).strip('.'), 'content': match.group(2).strip()}
                
                buffer = buffer[match.end():]
        
        # Process any remaining content in the buffer
        for match in self.out_regex.finditer(buffer) + self.block_regex.finditer(buffer):
            if match.re is self.out_regex:
                yield {'type': 'out', 'tag': match.group(1), 'content': match.group(2)}
            else:
                yield {'type': 'block', 'tag': match.group(1).strip('.'), 'content': match.group(2).strip()}
    # [[/cc.block.method.parse_stream]]

    # [[cc.block.method.generate_cml_block]]
    def generate_cml_block(self, block_type: str, tag: str, content: str) -> str:
        """
        Generate a CML block.

        Args:
            block_type (str): The type of block ('out' or 'block').
            tag (str): The tag for the block.
            content (str): The content of the block.

        Returns:
            str: A formatted CML block.

        Raises:
            ValueError: If an invalid block type is provided.
        """
        if block_type == 'out':
            return f"[[cc.out.{tag}]]{content}[[/cc.out.{tag}]]"
        elif block_type == 'block':
            return f"# [[cc.block.{tag}]]\n{content}\n# [[/cc.block.{tag}]]"
        else:
            raise ValueError(f"Invalid block type: {block_type}")
    # [[/cc.block.method.generate_cml_block]]

    # [[cc.block.method.merge_block_lists]]
    def merge_block_lists(self, block_lists: List[List[Tuple[str, str]]]) -> List[Tuple[str, str]]:
        """
        Merge multiple CML block lists.

        Args:
            block_lists (List[List[Tuple[str, str]]]): A list of block lists to merge.

        Returns:
            List[Tuple[str, str]]: A merged list of CML blocks.
        """
        merged = []
        for block_list in block_lists:
            merged.extend(block_list)
        return merged
    # [[/cc.block.method.merge_block_lists]]

# [[/cc.block.class.CMLParser]]

# [[cc.block.main]]
if __name__ == "__main__":
    import sys

    parser = CMLParser()

    if len(sys.argv) == 2:
        # Parse file
        file_path = sys.argv[1]
        try:
            result = parser.parse_file(file_path)
            print(json.dumps(result, indent=2))
        except (FileNotFoundError, ValueError) as e:
            print(f"Error: {str(e)}", file=sys.stderr)
            sys.exit(1)
    else:
        # Parse stdin stream
        try:
            for parsed_block in parser.parse_stream(sys.stdin):
                print(json.dumps(parsed_block))
        except ValueError as e:
            print(f"Error: {str(e)}", file=sys.stderr)
            sys.exit(1)
# [[/cc.block.main]]
