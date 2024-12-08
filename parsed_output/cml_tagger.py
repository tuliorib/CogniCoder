# [[cc.block.metadata]]
"""
File: cml_tagger.py
Version: 1.1.0
Last Updated: 2024-09-30
Description: CML (Cogni Markup Language) Tagger using Anthropic's API with Click CLI
"""
# [[/cc.block.metadata]]

# [[cc.block.imports]]
import os
import click
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

# [[cc.block.class.CMLTagger]]
class CMLTagger:
    """CML Tagger class for adding CML tags to code using Anthropic's API."""

    # [[cc.block.method.init]]
    def __init__(self):
        """Initialize the CMLTagger class."""
        if not ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
        self.client = Anthropic(api_key=ANTHROPIC_API_KEY)
    # [[/cc.block.method.init]]

    # [[cc.block.method.add_cml_tags]]
    def add_cml_tags(self, code: str, language: str) -> str:
        """
        Add CML tags to the given code using Anthropic's API.

        Args:
            code (str): The original code to be tagged.
            language (str): The programming language of the code.

        Returns:
            str: The tagged code.
        """
        prompt = self._create_prompt(code, language)
        
        try:
            response = self.client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text
        except Exception as e:
            click.echo(f"Error occurred while calling Anthropic API: {str(e)}", err=True)
            return None
    # [[/cc.block.method.add_cml_tags]]

    # [[cc.block.method.create_prompt]]
    def _create_prompt(self, code: str, language: str) -> str:
        """
        Create the prompt for the Anthropic API.

        Args:
            code (str): The original code to be tagged.
            language (str): The programming language of the code.

        Returns:
            str: The formatted prompt.
        """
        return f"""Human: I need you to add CML (Cogni Markup Language) tags to the following {language} code. Here are the guidelines for adding CML tags:

1. Basic Syntax:
   - Use `[[cc.field1.subfield2.subfield3]]` for opening tags and `[[/cc.field1.subfield2.subfield3]]` for closing tags.
   - Tags can be nested to any depth, allowing for precise code structure representation.
   - Always place CML tags inside appropriate comment syntax for the language.

2. Comment Syntax:
   - Python: Use `#` before each CML tag line
   - JavaScript/C/Go: Use `//` before each CML tag line
   - HTML: Use `<!--` before opening tags and `-->` after closing tags
   - CSS: Use `/*` before opening tags and `*/` after closing tags

3. Field Naming Conventions:
   - Use descriptive, hierarchical names for fields (e.g., `cc.code.class.ClassName`, `cc.code.method.MethodName`)
   - Common top-level fields: `cc.code.imports`, `cc.code.constants`, `cc.code.class`, `cc.code.function`, `cc.code.method`, `cc.code.main`, `cc.code.tests`

4. Indentation and Structure:
   - Maintain the existing code's indentation when adding CML tags, but the CML tags themselves do not have any indentation. Ensure CML tags do not have any trailing spaces or indentation.

5. Best Practices:
   - Tag all significant code structures (classes, methods, functions, etc.)
   - Create a `cc.metadata` field at the beginning of the file for overall file information, include the programming language.
   - Tag imports, constants, and main code sections separately.
   - Use nested fields for methods within classes.

Here's the code to tag:

```{language}
{code}
```

Please add CML tags to this code following the guidelines above. Return only the tagged code without any additional explanation.

```
       """
    # [[/cc.block.method.create_prompt]]

# [[/cc.block.class.CMLTagger]]

# [[cc.block.function.tag_file]]
@click.command()
@click.option('--original', required=True, type=click.Path(exists=True), help='Path to the original code file')
@click.option('--output', default=None, type=click.Path(), help='Path to save the tagged code (default: original_tagged.ext)')
def tag_file(original: str, output: str):
    """
    Add CML tags to the specified file and save the result.

    Args:
        original (str): Path to the original code file.
        output (str): Path to save the tagged code (default: original_tagged.ext).
    """
    # Read the original file
    with open(original, 'r') as file:
        code = file.read()

    # Determine the language based on file extension
    _, ext = os.path.splitext(original)
    language = ext.lstrip('.')

    # Create CMLTagger instance and add tags
    tagger = CMLTagger()
    tagged_code = tagger.add_cml_tags(code, language)

    if tagged_code:
        # Determine output file path
        if not output:
            base, ext = os.path.splitext(original)
            output = f"{base}_tagged{ext}"

        # Save the tagged code
        with open(output, 'w') as file:
            file.write(tagged_code)

        click.echo(f"Tagged code saved to: {output}")
    else:
        click.echo("Failed to tag the code.", err=True)
# [[/cc.block.function.tag_file]]

# [[cc.block.main]]
if __name__ == "__main__":
    tag_file()
# [[/cc.block.main]]
