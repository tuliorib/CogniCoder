# [[cc.block.metadata]]
'''
File: cml_indentation_remover.py
Version: 1.3.0
Last Updated: 2024-09-30
Description: Removes indentation from CML (CogniCoder Markup Language) lines in a given text using Click for CLI, including closing tags.
'''
# [[/cc.block.metadata]]

# [[cc.block.imports]]
import re
import click
# [[/cc.block.imports]]

# [[cc.block.constants]]
CML_PATTERN = r'^\s*(#\s*\[\[/?cc\..*?\]\]|\[\[/?cc\..*?\]\])'
# [[/cc.block.constants]]

# [[cc.block.function.remove_cml_indentation]]
def remove_cml_indentation(text):
    """
    Remove indentation from CML lines in the given text, including closing tags.

    Args:
        text (str): The input text containing CML lines.

    Returns:
        str: The text with CML lines' indentation removed.
    """
    lines = text.split('\n')
    processed_lines = []

    for line in lines:
        if re.match(CML_PATTERN, line):
            processed_lines.append(line.lstrip())
        else:
            processed_lines.append(line)

    return '\n'.join(processed_lines)
# [[/cc.block.function.remove_cml_indentation]]

# [[cc.block.function.process_file]]
def process_file(file_path):
    """
    Read a file, remove CML indentation, and write the result back to the file.

    Args:
        file_path (str): Path to the file to be processed.
    """
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        
        processed_content = remove_cml_indentation(content)
        
        output_file_path = f"{file_path}.CMLINDENTOFF"
        with open(output_file_path, 'w') as file:
            file.write(processed_content)
        
        click.echo(f"Successfully processed {file_path}")
        click.echo(f"Output saved to {output_file_path}")
    except IOError as e:
        click.echo(f"Error processing file {file_path}: {e}", err=True)
# [[/cc.block.function.process_file]]

# [[cc.block.main]]
@click.command()
@click.argument('file_path', type=click.Path(exists=True))
def main(file_path):
    """Remove indentation from CML lines in a file and save to a new file."""
    process_file(file_path)

if __name__ == "__main__":
    main()
# [[/cc.block.main]]