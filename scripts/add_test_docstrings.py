import os

def add_docstring(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    if content.strip().startswith('"""') or content.strip().startswith("'''"):
        return # Already has docstring
        
    filename = os.path.basename(filepath)
    docstring = f'"""\nTests for {filename.replace("test_", "").replace(".py", "")}.\n"""\n'
    
    with open(filepath, 'w') as f:
        f.write(docstring + content)
    print(f"Added docstring to {filepath}")

def main():
    target_dir = "backend/tests"
    for root, _, files in os.walk(target_dir):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                add_docstring(os.path.join(root, file))
            elif file == "__init__.py":
                 # Handle __init__.py separately
                 filepath = os.path.join(root, file)
                 with open(filepath, 'r') as f:
                    content = f.read()
                 if not content.strip().startswith('"""'):
                     with open(filepath, 'w') as f:
                        f.write('"""\nTest suite for backend.\n"""\n' + content)
                     print(f"Added docstring to {filepath}")

if __name__ == "__main__":
    main()
