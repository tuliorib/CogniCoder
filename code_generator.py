# [[cc.block.metadata]]
"""
File: cognicoder.py
Version: 2.4.0
Last Updated: 2024-09-30
Description: CogniCoder app for generating code using Claude API with Click CLI, raw output saving, improved input handling, and corrected metadata scheme
"""
# [[/cc.block.metadata]]

# [[cc.block.imports]]
import os
import json
import click
from anthropic import Anthropic
from datetime import datetime
# [[/cc.block.imports]]

# [[cc.block.constants]]
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
MODEL = "claude-3-5-sonnet-latest"
MAX_TOKENS = 4000
TEMPERATURE = 0.7
OUTPUT_DIR = "./output"
# [[/cc.block.constants]]

# [[cc.block.class.CogniCoder]]
class CogniCoder:
    """CogniCoder class for generating code using Claude API."""

    # [[cc.block.method.init]]
    def __init__(self):
        """Initialize the CogniCoder class."""
        self.client = Anthropic(api_key=ANTHROPIC_API_KEY)
    # [[/cc.block.method.init]]

    # [[cc.block.method.generate_code]]
    def generate_code(self, prompt, mode="FULL", previous_code=None, error_messages=None, documentation=None, other_code_files=None):
        """
        Generate code using Claude API.

        Args:
            prompt (str): The prompt for code generation.
            mode (str): The generation mode, either "FULL", "PATCH", or "NEW".
            previous_code (str): The previous code to be altered (optional).
            error_messages (list): List of error messages (optional).
            documentation (list): List of documentation files (optional).
            other_code_files (list): List of other relevant code files (optional).

        Returns:
            str: The raw response from the Claude API.
        """
        system_prompt = self._get_system_prompt(mode)
        
        user_message = f"""Prompt: {prompt}

Generate code based on the prompt. Additionally, infer an appropriate filename for the code (excluding the extension).
Do not include any explanatory text in the code itself. The code should be ready to use as-is.
Provide your response in the following format:

[[cc.out.filename]]inferred_filename[[/cc.out.filename]]
[[cc.out.mode]]{mode}[[/cc.out.mode]]
[[cc.out.code]]
# [[cc.block.metadata]]
'''
File: inferred_filename.py
Version: 1.0.0
Last Updated: {datetime.now().strftime('%Y-%m-%d')}
Description: Brief description of the file's purpose
'''
# [[/cc.block.metadata]]

# Generated code here, with all necessary [[cc.block]] tags inside comments
[[/cc.out.code]]
[[cc.out.explanation]]
detailed_explanation_here
[[/cc.out.explanation]]

Ensure that the code field preserves all necessary indentation and formatting, and that all [[cc.block]] tags are placed inside comments.
"""
        if previous_code:
            user_message += f"Previous code:\n```\n{previous_code}\n```\n\n"
        if error_messages:
            user_message += "Error messages:\n"
            for msg in error_messages:
                user_message += f"- {msg}\n"
            user_message += "\n"
        if documentation:
            user_message += "Additional documentation:\n"
            for doc in documentation:
                user_message += f"{doc}\n\n"
        if other_code_files:
            user_message += "Other relevant code files:\n"
            for file in other_code_files:
                user_message += f"File: {file['name']}\n```\n{file['content']}\n```\n\n"
        
        response = self.client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )

        return response.content[0].text
    # [[/cc.block.method.generate_code]]

    # [[cc.block.method.save_response]]
    def save_response(self, response, output_file):
        """
        Save the raw response to a file.

        Args:
            response (str): The raw response from the API.
            output_file (str): The filename to save the response to.

        Returns:
            str: The filename of the saved response.
        """
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w') as f:
            f.write(response)
        
        click.echo(f"Raw response saved to {output_file}")
        return output_file
    # [[/cc.block.method.save_response]]

    # [[cc.block.method.get_system_prompt]]
    def _get_system_prompt(self, mode):
        """
        Get the system prompt based on the generation mode.

        Args:
            mode (str): The generation mode, either "FULL", "PATCH", or "NEW".

        Returns:
            str: The system prompt for Claude.
        """
        base_prompt = """
        # CogniCoder: Custom Instructions for Code Generation and Patching

        ## Overview
        CogniCoder is a system for generating and patching code using metadata blocks. It supports Python and Lua, allowing for granular updates and maintaining code structure integrity.

        ## Metadata Block Structure
        - Use double square brackets with cc.block prefix for metadata blocks.
        - Format: # [[cc.block.subtag1.subsubtag2]] for opening, # [[/cc.block.subtag1.subsubtag2]] for closing.
        - Always place these tags inside comments.
        - Allow nesting up to 2 levels deep (only for class methods).

        ## Block Naming Conventions
        - Classes: # [[cc.block.class.classname]]
        - Methods within classes: # [[cc.block.method.methodname]]
        - Standalone functions: # [[cc.block.function.functionname]]
        - Imports: # [[cc.block.imports]]
        - Constants: # [[cc.block.constants]]
        - Main sections: # [[cc.block.main]]
        - Tests: # [[cc.block.tests]]
        - Metadata: # [[cc.block.metadata]]

        ## Indentation and Code Structure
        - Maintain correct indentation for all generated code.
        - For patches, ensure that the indentation of new or modified code matches the surrounding context.
        - Use consistent indentation (e.g., 4 spaces for Python) throughout the generated code.
        - When adding new blocks or modifying existing ones, make sure the indentation is correct relative to the parent blocks.

        ## Output Format
        Your response should be structured as follows:
        [[cc.out.filename]]inferred_filename[[/cc.out.filename]]
        [[cc.out.mode]]FULL, PATCH, or NEW[[/cc.out.mode]]
        [[cc.out.code]]
        # [[cc.block.metadata]]
        '''
        File: inferred_filename.py
        Version: 1.0.0
        Last Updated: current_date
        Description: Brief description of the file's purpose
        '''
        # [[/cc.block.metadata]]

        # Generated code here, with all necessary [[cc.block]] tags inside comments
        [[/cc.out.code]]
        [[cc.out.explanation]]
        detailed explanation
        [[/cc.out.explanation]]

        The explanation should be comprehensive and LLM-friendly, describing what the code does, why certain decisions were made, and any changes to the indentation or structure (if applicable).
        """

        if mode == "FULL":
            base_prompt += """
            ## Generation Mode: FULL
            - Create a complete file structure with correct indentation throughout.
            - Include all necessary blocks.
            - Do not use removal tags.
            - If previous code is provided, use it as a starting point and improve upon it while maintaining its overall structure.
            - Incorporate the additional documentation to ensure the generated code is up-to-date and accurate.
            """
        elif mode == "PATCH":
            base_prompt += """
            ## Generation Mode: PATCH
            - Only include blocks to be changed, added, or removed.
            - Use removal tags for deletions.
            - For new class methods, create method block inside existing class block with correct indentation.
            - Use removal syntax for deleting blocks: # [[cc.block.remove]]block_identifier[[/cc.block.remove]]
            - Focus on addressing specific issues or adding new functionality to the previous code.
            - Ensure that the indentation of new or modified code matches the surrounding context exactly.
            - If adding new blocks, make sure they are indented correctly relative to their parent blocks.
            - Use the additional documentation to guide your patching process and ensure compatibility with the latest API or library versions.
            - The output should be a patch that can be applied to the existing code, not a complete file.
            """
        elif mode == "NEW":
            base_prompt += """
            ## Generation Mode: NEW
            - Create a new file from scratch with correct and consistent indentation.
            - Include all necessary blocks for a complete and functional new file.
            - Do not reference or depend on previous code unless explicitly mentioned in the prompt.
            - Utilize the additional documentation to ensure the new code is up-to-date and follows best practices.
            """

        base_prompt += """
        ## Best Practices
        1. Include version number and last update date in metadata block.
        2. Provide detailed docstrings for functions and classes.
        3. Include brief comments explaining complex logic.
        4. Maintain consistent order: metadata, imports, constants, functions, classes, main code, tests.
        5. Include appropriate error handling.
        6. Use descriptive names for variables, functions, and classes.
        7. Follow language-specific conventions (e.g., PEP 8 for Python).
        8. Include unit tests for key functionality.
        9. Define constants in a dedicated # [[cc.block.constants]] block.
        10. Encapsulate main code in a `main()` function within the # [[cc.block.main]] block.
        11. When using additional documentation, cite the source in comments to justify decisions or implementations.
        12. Always maintain correct and consistent indentation, especially for patches and nested structures.

        Generate code according to these instructions, the provided prompt, and any additional context given, including the up-to-date documentation. Pay special attention to indentation and code structure to ensure the generated code can be seamlessly integrated or run without indentation-related errors.
        """
        return base_prompt
    # [[/cc.block.method.get_system_prompt]]

# [[/cc.block.class.CogniCoder]]

# [[cc.block.function.read_file_content]]
def read_file_content(file_path):
    """Read and return the content of a file."""
    with open(file_path, 'r') as f:
        return f.read()
# [[/cc.block.function.read_file_content]]

# [[cc.block.main]]
@click.command()
@click.option('--prompt', help='The prompt for code generation.')
@click.option('--mode', type=click.Choice(['FULL', 'PATCH', 'NEW'], case_sensitive=False), help='The generation mode (FULL, PATCH, or NEW).')
@click.option('--previous-code', type=click.File('r'), help='File containing the previous code to be altered.')
@click.option('--error-message', type=click.File('r'), help='File containing error messages.')
@click.option('--documentation', type=click.File('r'), help='File containing additional documentation or context.')
@click.option('--other-code-file', type=click.File('r'), help='Other relevant code file.')
@click.option('--input-json', type=click.File('r'), help='JSON file containing all input parameters.')
@click.option('--output-file', default='./output/result.out', help='The filename to save the raw response.')
def main(prompt, mode, previous_code, error_message, documentation, other_code_file, input_json, output_file):
    """CogniCoder: Generate or patch code using Claude API with support for additional documentation and context."""
    cognicoder = CogniCoder()

    if input_json:
        # Use input from JSON file
        input_data = json.load(input_json)
        prompt = input_data.get('prompt', '')
        mode = input_data.get('mode', 'FULL')
        previous_code_content = read_file_content(input_data['previous_code']) if 'previous_code' in input_data else None
        error_messages = [read_file_content(f) for f in input_data.get('error_messages', [])]
        documentation_content = [read_file_content(f) for f in input_data.get('documentation', [])]
        other_code_files = [{'name': f, 'content': read_file_content(f)} for f in input_data.get('other_code_files', [])]
    else:
        # Use command-line arguments
        if not prompt:
            prompt = click.prompt('Enter your code generation prompt')
        if not mode:
            mode = click.prompt('Enter generation mode', type=click.Choice(['FULL', 'PATCH', 'NEW'], case_sensitive=False), default='FULL')
        previous_code_content = previous_code.read() if previous_code else None
        error_messages = [error_message.read()] if error_message else None
        documentation_content = [documentation.read()] if documentation else None
        other_code_files = [{'name': other_code_file.name, 'content': other_code_file.read()}] if other_code_file else None

    response = cognicoder.generate_code(
        prompt, mode.upper(), previous_code_content, error_messages, documentation_content, other_code_files
    )
    
    cognicoder.save_response(response, output_file)

if __name__ == "__main__":
    main()
# [[/cc.block.main]]
