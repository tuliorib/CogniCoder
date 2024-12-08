# [[cc.block.metadata]]
'''
File: code_patcher_cml.py
Version: 1.0.0
Last Updated: 2024-09-30
Description: CogniCoder Markup Language (CML) code patcher for applying patches to original files
'''
# [[/cc.block.metadata]]

# [[cc.block.imports]]
import os
import click
from datetime import datetime
from cml_parser import CMLParser
from typing import List, Tuple
# [[/cc.block.imports]]

# [[cc.block.constants]]
PATCHED_EXTENSION = ".PATCHED"
INDENT_EXTENSION = "_INDENT"
# [[/cc.block.constants]]

# [[cc.block.class.CodePatcherCML]]
class CodePatcherCML:
    # [[cc.block.method.__init__]]
    def __init__(self, original_file: str, patch_file: str):
        self.original_file = original_file
        self.patch_file = patch_file
        self.cml_parser = CMLParser()
        self.patch_content = self._load_patch_file()
        self.patched_blocks = set()
    # [[/cc.block.method.__init__]]

    # [[cc.block.method._load_patch_file]]
    def _load_patch_file(self) -> List[Tuple[str, str]]:
        try:
            with open(self.patch_file, 'r') as f:
                patch_content = f.read()
            return self.cml_parser.parse_content(patch_content)['block']
        except Exception as e:
            raise click.ClickException(f"Error loading patch file: {str(e)}")
    # [[/cc.block.method._load_patch_file]]

    # [[cc.block.method.apply_patch]]
    def apply_patch(self):
        if not os.path.exists(self.original_file):
            raise FileNotFoundError(f"Original file not found: {self.original_file}")

        try:
            with open(self.original_file, 'r') as f:
                original_content = f.read()

            patched_content = self._process_patch(original_content)

            patched_file = f"{self.original_file}{PATCHED_EXTENSION}"
            with open(patched_file, 'w') as f:
                f.write(patched_content)

            click.echo(f"Successfully created patched file: {patched_file}")
            return patched_file
        except Exception as e:
            raise click.ClickException(f"Error applying patch: {str(e)}")
    # [[/cc.block.method.apply_patch]]

    # [[cc.block.method._process_patch]]
    def _process_patch(self, original_content: str) -> str:
        patched_content = original_content

        for block_type, block_content in self.patch_content:
            click.echo(f"Applying patch on code block '[[cc.block.{block_type}]]'")
            if 'remove' in block_type:
                patched_content = self._remove_block(patched_content, block_type.replace('remove.', ''))
            else:
                patched_content = self._add_or_replace_block(patched_content, block_type, block_content)
                self.patched_blocks.add(block_type)

        return patched_content
    # [[/cc.block.method._process_patch]]

    # [[cc.block.method._add_or_replace_block]]
    def _add_or_replace_block(self, content: str, block_type: str, block_content: str) -> str:
        block_start = f"# [[cc.block.{block_type}]]"
        block_end = f"# [[/cc.block.{block_type}]]"
        
        # Remove any leading or trailing newlines from block_content
        block_content = block_content.strip('\n')
        
        # Construct full_block without adding extra newlines
        full_block = f"{block_start}\n{block_content}\n{block_end}"
        
        start_index = content.find(block_start)
        end_index = content.find(block_end)
        if start_index != -1 and end_index != -1:
            # Replace existing block
            end_index += len(block_end)
            return content[:start_index] + full_block + content[end_index:]
        else:
            # Add new block
            if content and not content.endswith('\n'):
                return f"{content}\n{full_block}"
            else:
                return f"{content}{full_block}"
    # [[/cc.block.method._add_or_replace_block]]

    # [[cc.block.method._remove_block]]
    def _remove_block(self, content: str, block_type: str) -> str:
        block_start = f"# [[cc.block.{block_type}]]"
        block_end = f"# [[/cc.block.{block_type}]]"
        
        start_index = content.find(block_start)
        end_index = content.find(block_end)

        if start_index != -1 and end_index != -1:
            return content[:start_index] + content[end_index + len(block_end):]
        
        return content
    # [[/cc.block.method._remove_block]]

# [[/cc.block.class.CodePatcherCML]]

# [[cc.block.main]]
@click.command()
@click.option('--original', required=True, type=click.Path(exists=True), help='Path to the original file to be patched.')
@click.option('--patch', required=True, type=click.Path(exists=True), help='Path to the patch file.')
def apply_patch(original, patch):
    """Apply a CogniCoder-generated patch."""
    try:
        patcher = CodePatcherCML(original, patch)
        patched_file = patcher.apply_patch()
    except Exception as e:
        raise click.ClickException(str(e))

if __name__ == '__main__':
    apply_patch()
# [[/cc.block.main]]
