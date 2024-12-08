# [[cc.block.metadata]]
'''
File: output_parser.py
Version: 1.1.0
Last Updated: 2024-09-29
Description: Parser for CogniCoder output with separate parsing for code and explanation blocks
'''
# [[/cc.block.metadata]]

# [[cc.block.imports]]
import os
import re
import click
# [[/cc.block.imports]]

# [[cc.block.class.OutputParser]]
class OutputParser:
    """Parser for CogniCoder output with separate parsing for code and explanation blocks"""

    # [[cc.block.method.init]]
    def __init__(self, input_file):
        """
        Initialize the OutputParser.

        Args:
            input_file (str): Path to the input file containing the CogniCoder output.
        """
        self.input_file = input_file
        self.raw_content = self._load_input_file()
        self.parsed_data = self._parse_raw_content()
    # [[/cc.block.method.init]]

    # [[cc.block.method.load_input_file]]
    def _load_input_file(self):
        """Load the raw content from the input file."""
        with open(self.input_file, 'r') as f:
            return f.read()
    # [[/cc.block.method.load_input_file]]

    # [[cc.block.method.parse_raw_content]]
    def _parse_raw_content(self):
        """Parse the raw content into structured data."""
        parsed_data = {}
        parsed_data['filename'] = self._parse_block('filename')
        parsed_data['mode'] = self._parse_block('mode')
        parsed_data['code'] = self._parse_block('code')
        parsed_data['explanation'] = self._parse_block('explanation', optional=True)
        return parsed_data
    # [[/cc.block.method.parse_raw_content]]

    # [[cc.block.method.parse_block]]
    def _parse_block(self, block_name, optional=False):
        """Parse a specific block from the raw content."""
        pattern = rf'\[\[cc\.out\.{block_name}\]\](.*?)\[\[/cc\.out\.{block_name}\]\]'
        match = re.search(pattern, self.raw_content, re.DOTALL)
        if match:
            return match.group(1).strip()
        elif not optional:
            raise ValueError(f"Required block '{block_name}' not found in the input file.")
        return None
    # [[/cc.block.method.parse_block]]

    # [[cc.block.method.save_parsed_output]]
    def save_parsed_output(self, output_dir):
        """Save the parsed output as separate files."""
        if not self.parsed_data:
            click.echo("No parsed data to save.")
            return

        os.makedirs(output_dir, exist_ok=True)
        
        # Save code file
        filename = self.parsed_data.get('filename', 'output')
        mode = self.parsed_data.get('mode', 'FULL')
        code_filename = f"{filename}.py.{mode.lower()}"
        with open(os.path.join(output_dir, code_filename), 'w') as f:
            f.write(self.parsed_data.get('code', ''))
        
        # Save explanation file if present
        explanation = self.parsed_data.get('explanation')
        if explanation:
            explanation_filename = f"{filename}_explanation.txt"
            with open(os.path.join(output_dir, explanation_filename), 'w') as f:
                f.write(explanation)
            click.echo(f"Explanation file: {explanation_filename}")
        
        click.echo(f"Parsed output saved to {output_dir}")
        click.echo(f"Code file: {code_filename}")
    # [[/cc.block.method.save_parsed_output]]

# [[/cc.block.class.OutputParser]]

# [[cc.block.main]]
@click.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output-dir', default='./parsed_output', help='The directory to save the parsed output files.')
def main(input_file, output_dir):
    """Parse CogniCoder output and save the results."""
    parser = OutputParser(input_file)
    parser.save_parsed_output(output_dir)

if __name__ == "__main__":
    main()
# [[/cc.block.main]]