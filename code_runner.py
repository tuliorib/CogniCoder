# <.cg.metadata>
"""
File: cogni_engineer.py
Version: 1.0.0
Last Updated: 2024-09-30
Description: Tool for executing Python files and capturing output and errors
"""
# </.cg.metadata>

# <.cg.imports>
import argparse
import json
import subprocess
import sys
# </.cg.imports>

# <.cg.constants>
JSON_OUTPUT_FILE = 'cogni_engineer_output.json'
# </.cg.constants>

# <.cg.function_run_python_file>
def run_python_file(filename):
    """
    Run the specified Python file and capture its output and errors.

    Args:
        filename (str): The name of the Python file to execute.

    Returns:
        tuple: A tuple containing (executed_output, error_occurred, error_message)
    """
    try:
        result = subprocess.run([sys.executable, filename], capture_output=True, text=True, check=True)
        return result.stdout, False, ''
    except subprocess.CalledProcessError as e:
        return e.stdout, True, e.stderr
    except Exception as e:
        return '', True, str(e)
# </.cg.function_run_python_file>

# <.cg.function_create_json_output>
def create_json_output(executed, error, error_message):
    """
    Create a JSON object with the execution results.

    Args:
        executed (str): The output of the executed code.
        error (bool): Whether an error occurred.
        error_message (str): The error message, if any.

    Returns:
        dict: A dictionary containing the execution results.
    """
    return {
        'error': error,
        'executed': executed,
        'error_message': error_message
    }
# </.cg.function_create_json_output>

# <.cg.function_main>
def main():
    """Main function to run the CogniEngineer."""
    parser = argparse.ArgumentParser(description='Execute a Python file and capture its output and errors.')
    parser.add_argument('--input', required=True, help='The Python file to execute')
    args = parser.parse_args()

    executed, error, error_message = run_python_file(args.input)
    output = create_json_output(executed, error, error_message)

    with open(JSON_OUTPUT_FILE, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Execution results saved to {JSON_OUTPUT_FILE}")
# </.cg.function_main>

# <.cg.main>
if __name__ == '__main__':
    main()
# </.cg.main>
