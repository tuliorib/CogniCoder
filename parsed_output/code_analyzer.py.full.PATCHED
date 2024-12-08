# [[cc.block.metadata]]
'''
File: code_analyzer.py
Version: 1.0.0
Last Updated: 2024-09-29
Description: Program to analyze Python files and generate detailed explanations using LLM
'''
# [[/cc.block.metadata]]

# [[cc.block.imports]]
import os
import click
import json
from anthropic import Anthropic
from datetime import datetime
# [[/cc.block.imports]]

# [[cc.block.constants]]
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
MODEL = "claude-3-5-sonnet-20240620"
MAX_TOKENS = 4000
TEMPERATURE = 0.7
OUTPUT_DIR = "./output"
# [[/cc.block.constants]]

# [[cc.block.class.CodeAnalyzer]]
class CodeAnalyzer:
    """CodeAnalyzer class for analyzing Python files and generating explanations using Claude API."""

# [[cc.block.method.init]]
    def __init__(self):
        """Initialize the CodeAnalyzer class."""
        self.client = Anthropic(api_key=ANTHROPIC_API_KEY)
# [[/cc.block.method.init]]

# [[cc.block.method.analyze_code]]
    def analyze_code(self, file_path, original_file_path=None):
        """
        Analyze the given Python file and generate explanations using Claude API.

        Args:
            file_path (str): Path to the Python file to analyze.
            original_file_path (str): Path to the original Python file for comparison (optional).

        Returns:
            dict: A dictionary containing the analysis results.
        """
        with open(file_path, 'r') as f:
            code_content = f.read()

        original_content = None
        if original_file_path:
            with open(original_file_path, 'r') as f:
                original_content = f.read()

        prompt = self._create_analysis_prompt(code_content, original_content)
        response = self._get_llm_response(prompt)
        return self._parse_llm_response(response)
# [[/cc.block.method.analyze_code]]

# [[cc.block.method.create_analysis_prompt]]
    def _create_analysis_prompt(self, code_content, original_content=None):
        """Create the prompt for code analysis."""
        prompt = f"""Analyze the following Python code and provide three blocks of information:

1. A brief but verbose description of what the program does.
2. An extended explanation of each function, including expected inputs, functionality, and outputs.
3. (Optional) If an original file is provided, create a change log comparing the two versions.

Here's the code to analyze:

{code_content}

"""
        if original_content:
            prompt += f"\nHere's the original code for comparison:\n\n{original_content}\n"

        prompt += """
Please format your response as follows:

[[cc.doc.summary]]
Brief description of what the program does
[[/cc.doc.summary]]

[[cc.doc.functions]]
Detailed explanation of each function
[[/cc.doc.functions]]

[[cc.doc.changelog]]
Change log (if applicable)
[[/cc.doc.changelog]]
"""
        return prompt
# [[/cc.block.method.create_analysis_prompt]]

# [[cc.block.method.get_llm_response]]
    def _get_llm_response(self, prompt):
        """Get response from Claude API."""
        response = self.client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.content[0].text
# [[/cc.block.method.get_llm_response]]

# [[cc.block.method.parse_llm_response]]
    def _parse_llm_response(self, response):
        """Parse the LLM response into a structured format."""
        sections = {
            "summary": "",
            "functions": "",
            "changelog": ""
        }
        current_section = None
        for line in response.split('\n'):
            if line.startswith("[[cc.doc."):
                current_section = line[8:-2]
            elif line.startswith("[[/cc.doc."):
                current_section = None
            elif current_section and current_section in sections:
                sections[current_section] += line + "\n"
        return sections
# [[/cc.block.method.parse_llm_response]]

# [[cc.block.method.save_analysis]]
    def save_analysis(self, analysis, output_file):
        """
        Save the analysis results to a file.

        Args:
            analysis (dict): The analysis results.
            output_file (str): The filename to save the analysis to.

        Returns:
            str: The filename of the saved analysis.
        """
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        click.echo(f"Analysis saved to {output_file}")
        return output_file
# [[/cc.block.method.save_analysis]]

# [[cc.block.method.create_metadata]]
    def create_metadata(self, file_path, output_file):
        """
        Create a metadata file for the analyzed Python file.

        Args:
            file_path (str): Path to the analyzed Python file.
            output_file (str): Path to the output analysis file.

        Returns:
            str: The filename of the created metadata file.
        """
        metadata = {
            "analyzed_file": os.path.basename(file_path),
            "analysis_file": os.path.basename(output_file),
            "analysis_version": "1.0.0",
            "analysis_date": datetime.now().isoformat()
        }
        
        metadata_file = os.path.join(os.path.dirname(output_file), "metadata.json")
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        click.echo(f"Metadata file created: {metadata_file}")
        return metadata_file
# [[/cc.block.method.create_metadata]]

# [[/cc.block.class.CodeAnalyzer]]

# [[cc.block.main]]
@click.command()
@click.option('--file', required=True, type=click.Path(exists=True), help='Path to the Python file to analyze.')
@click.option('--original-file', type=click.Path(exists=True), help='Path to the original Python file for comparison (optional).')
@click.option('--output-file', default='./output/analysis.json', help='The filename to save the analysis results.')
def main(file, original_file, output_file):
    """Analyze a Python file and generate detailed explanations using LLM."""
    analyzer = CodeAnalyzer()
    
    analysis = analyzer.analyze_code(file, original_file)
    saved_file = analyzer.save_analysis(analysis, output_file)
    analyzer.create_metadata(file, saved_file)

if __name__ == "__main__":
    main()
# [[/cc.block.main]]
