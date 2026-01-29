import ast
import os
import sys
from typing import List, Tuple

def check_file(filepath: str) -> List[Tuple[int, str, str]]:
    """
    Checks a python file for missing docstrings in modules, classes, and functions.
    Returns a list of (line_number, type, name).
    """
    missing = []
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            tree = ast.parse(f.read(), filename=filepath)
        except SyntaxError:
            return [(0, "syntax_error", filepath)]

    # Check module docstring
    if not ast.get_docstring(tree):
        missing.append((1, "module", filepath))

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            if not ast.get_docstring(node):
                missing.append((node.lineno, "class", node.name))
        elif isinstance(node, ast.FunctionDef):
            # Skip private functions unless they are __init__
            if node.name.startswith("_") and node.name != "__init__":
                continue
            if not ast.get_docstring(node):
                missing.append((node.lineno, "function", node.name))
        elif isinstance(node, ast.AsyncFunctionDef):
             # Skip private functions unless they are __init__
            if node.name.startswith("_") and node.name != "__init__":
                continue
            if not ast.get_docstring(node):
                missing.append((node.lineno, "function", node.name))

    return missing

def main():
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "backend"
    print(f"Checking {target_dir} for missing docstrings...")
    
    total_missing = 0
    for root, _, files in os.walk(target_dir):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                missing_in_file = check_file(filepath)
                if missing_in_file:
                    print(f"\nFile: {filepath}")
                    for line, type_, name in missing_in_file:
                        print(f"  Line {line}: Missing {type_} docstring for '{name}'")
                    total_missing += len(missing_in_file)

    print(f"\nTotal missing docstrings: {total_missing}")
    if total_missing > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
