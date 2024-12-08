
# <.cg.metadata>
"""
File: utils.py
Version: 1.0.0
Last Updated: 2024-09-27
Description: Utility functions for CogniCoder
"""
# </.cg.metadata>

# <.cg.function_load_file_content>
def load_file_content(file):
    """
    Load content from a file object if it exists.

    Args:
        file: A file object or None.

    Returns:
        str: The content of the file, or None if the file doesn't exist.
    """
    return file.read() if file else None
# </.cg.function_load_file_content>
