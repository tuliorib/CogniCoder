import re
from typing import Dict, List, Any, Optional
import io
import os
import ast

class LanguageConfig:
    def __init__(self, start_marker: str, end_marker: str = ''):
        self.start_marker = start_marker
        self.end_marker = end_marker

class CMLField:
    def __init__(self, key: str, content: str, params: Dict[str, Any] = None):
        self.key = key
        self.content = content  # Store content exactly as it is, including leading/trailing whitespace
        self.params = params or {}

    def __repr__(self):
        return f"CMLField(key={self.key}, params={self.params})"

class CMLParser:
    LANGUAGE_CONFIGS = {
        'python': LanguageConfig('#'),
        'javascript': LanguageConfig('//'),
        'c': LanguageConfig('//'),
        'go': LanguageConfig('//'),
        'html': LanguageConfig('<!--', '-->'),
        'css': LanguageConfig('/*', '*/'),
        'cml': LanguageConfig(''),
    }

    def __init__(self, language: str = 'python'):
        self.fields: Dict[str, CMLField] = {}
        self.set_language(language)

    def set_language(self, language: str):
        self.language = language.lower()
        if self.language not in self.LANGUAGE_CONFIGS:
            raise ValueError(f"Unsupported language: {language}")
        
        self.language_config = self.LANGUAGE_CONFIGS[self.language]
        self._compile_regexes()

    def _compile_regexes(self):
        start_marker = re.escape(self.language_config.start_marker)
        end_marker = re.escape(self.language_config.end_marker)
        
        self.field_pattern = re.compile(
            rf'{start_marker}?\s*\[\[cc\.([\w.]+)(,\s*params\s*=\s*(.+?))?\]\](.*?){start_marker}?\s*\[\[/cc\.\1\]\]\s*{end_marker}?',
            re.DOTALL
        )

    def parse_file(self, file_path: str) -> Dict[str, CMLField]:
        with open(file_path, 'r') as file:
            content = file.read()
        
        cml_file_path = f"{file_path}.cml"
        if os.path.exists(cml_file_path):
            with open(cml_file_path, 'r') as cml_file:
                content += "\n" + cml_file.read()
        
        return self.parse_content(content)

    def parse_content(self, content: str) -> Dict[str, CMLField]:
        self.fields = {}
        for match in self.field_pattern.finditer(content):
            key, _, params_str, field_content = match.groups()
            params = {}
            if params_str:
                try:
                    params = ast.literal_eval(params_str)
                except (SyntaxError, ValueError):
                    print(f"Warning: Invalid params for {key}: {params_str}")
            
            if key in self.fields:
                print(f"Warning: Duplicate field key found: {key}")
            
            # Store the field_content exactly as it is, without stripping
            self.fields[key] = CMLField(key, field_content, params)
        
        return self.fields

    def get_param_value(self, field_key: str, param_name: str) -> Any:
        field = self.fields.get(field_key)
        if field:
            return field.params.get(param_name)
        print(f"Warning: Field {field_key} not found")
        return None

    def set_param_value(self, field_key: str, param_name: str, value: Any):
        field = self.fields.get(field_key)
        if field:
            field.params[param_name] = value
        else:
            print(f"Warning: Field {field_key} not found")

    def change_field_name(self, old_key: str, new_key: str):
        if old_key in self.fields:
            field = self.fields.pop(old_key)
            field.key = new_key
            self.fields[new_key] = field
        else:
            print(f"Warning: Field {old_key} not found")

    def get_field_content(self, field_key: str) -> Optional[str]:
        field = self.fields.get(field_key)
        if field:
            return field.content
        print(f"Warning: Field {field_key} not found")
        return None

    def delete_field(self, field_key: str):
        if field_key in self.fields:
            del self.fields[field_key]
        else:
            print(f"Warning: Field {field_key} not found")

    def add_field(self, field_key: str, content: str, params: Dict[str, Any] = None):
        if field_key in self.fields:
            print(f"Warning: Field {field_key} already exists. Use replace_field_content to modify.")
        else:
            self.fields[field_key] = CMLField(field_key, content, params or {})

    def replace_field_content(self, field_key: str, new_content: str):
        field = self.fields.get(field_key)
        if field:
            field.content = new_content
        else:
            print(f"Warning: Field {field_key} not found")

    def generate_cml_field(self, field: CMLField) -> str:
        start_marker = self.language_config.start_marker
        end_marker = self.language_config.end_marker
        
        params_str = f", params={field.params}" if field.params else ""
        
        # Remove one trailing newline if it exists, as we'll add it back later
        content = field.content[:-1] if field.content.endswith('\n') else field.content
        
        return f"{start_marker} [[cc.{field.key}{params_str}]]{content}\n{start_marker} [[/cc.{field.key}]]{end_marker}"

    def generate_cml_content(self) -> str:
        return "\n\n".join(self.generate_cml_field(field) for field in self.fields.values())

# Example usage
if __name__ == "__main__":
    parser = CMLParser(language='python')

    # Parse some content
    content = """
    # [[cc.field1.subfield2.subfield3, params={'arg1': 'value1', 'arg2': 'value2'}]]
    def example_method(arg1, arg2):
        print(f"Args: {arg1}, {arg2}")
    # [[/cc.field1.subfield2.subfield3]]

    # [[cc.output.result]]
        Output line 1
            Output line 2
    # [[/cc.output.result]]

    """

    parser.parse_content(content)

    print("Original content:")
    print(parser.generate_cml_content())
    print("\n" + "="*50 + "\n")

    # Get and set param value
    print("Param value:", parser.get_param_value('field1.subfield2.subfield3', 'arg1'))
    parser.set_param_value('field1.subfield2.subfield3', 'arg1', 'new_value')
    print("Updated param value:", parser.get_param_value('field1.subfield2.subfield3', 'arg1'))

    # Change field name
    parser.change_field_name('field1.subfield2.subfield3', 'field1.subfield2.new_subfield3')

    # Get field content
    print("\nField content:")
    print(repr(parser.get_field_content('field1.subfield2.new_subfield3')))

    # Replace field content
    parser.replace_field_content('field1.subfield2.new_subfield3', '\ndef new_example_method(arg1, arg2):\n    print(f"New method: {arg1}, {arg2}")\n')

    # Add new field
    parser.add_field('analysis.performance', '\nTime: 1.23s\nMemory: 256MB\n', {'unit': 'seconds'})

    # Generate updated CML content
    print("\nUpdated content:")
    print(parser.generate_cml_content())

    # Delete a field
    parser.delete_field('output.result')

    print("\nFinal content after deletion:")
    print(parser.generate_cml_content())
