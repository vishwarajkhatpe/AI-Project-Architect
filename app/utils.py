import json
import re

def parse_ai_response(raw_text):
    """
    Parses the AI's output to extract a valid file structure.
    Now supports:
    1. Nested Folders (Recursive Dicts)
    2. Slash-paths (e.g., "src/components/header.py")
    3. Robust JSON extraction
    """
    
    # 1. Clean and Find JSON
    # We look for content between ```json and ``` or just the first/last brace
    try:
        # Attempt 1: Strict Markdown code block
        match = re.search(r"```json\s*(\{.*?\})\s*```", raw_text, re.DOTALL)
        if match:
            json_str = match.group(1)
        else:
            # Attempt 2: Loose brace finding (Fallback)
            # Find the first '{' and the last '}'
            start = raw_text.find('{')
            end = raw_text.rfind('}') + 1
            if start != -1 and end != 0:
                json_str = raw_text[start:end]
            else:
                return None
                
        # 2. Parse JSON String
        structure = json.loads(json_str)
        
        # 3. Flatten the Structure (The Recursive Magic)
        flattened_files = {}
        
        def _recurse_structure(current_node, current_path=""):
            """
            Walks through the dictionary. 
            - If it finds a Dictionary, it's a Folder -> Dive deeper.
            - If it finds a String, it's a File -> Save it.
            """
            if isinstance(current_node, dict):
                for key, value in current_node.items():
                    # Handle paths that might already have slashes (e.g. "app/utils")
                    # We combine the current_path with the new key
                    new_path = f"{current_path}/{key}" if current_path else key
                    
                    # Clean up double slashes just in case
                    new_path = new_path.replace("//", "/")
                    
                    _recurse_structure(value, new_path)
                    
            elif isinstance(current_node, str):
                # It is a file! Save the content.
                # Remove any leading slash from the path
                final_path = current_path.lstrip("/")
                flattened_files[final_path] = current_node
            
            else:
                # If it's a list or number, ignore it (AI error)
                pass

        # Start the recursion
        _recurse_structure(structure)
        
        return flattened_files

    except (json.JSONDecodeError, AttributeError):
        # JSON was broken or not found
        return None
def format_tree_structure(file_paths):
    """
    Converts a list of file paths ['src/utils/helper.py'] 
    into the nested dictionary format required by streamlit-tree-select.
    """
    tree_nodes = []

    for path in file_paths:
        parts = path.split('/')
        current_level = tree_nodes
        current_full_path = ""

        for i, part in enumerate(parts):
            # Reconstruct the full path for unique IDs (e.g. "src/components")
            current_full_path = f"{current_full_path}/{part}" if current_full_path else part
            
            # Check if this node already exists at this level
            existing_node = next((node for node in current_level if node['label'] == part), None)

            if existing_node:
                # If it's a folder, step inside its children
                if 'children' in existing_node:
                    current_level = existing_node['children']
            else:
                # Create new node
                is_file = (i == len(parts) - 1)
                
                new_node = {
                    "label": part,
                    "value": current_full_path,  # Unique ID
                    "showCheckbox": True         # Allow selecting files
                }
                
                if not is_file:
                    new_node["children"] = []
                    current_level.append(new_node)
                    current_level = new_node["children"]  # Step inside
                else:
                    # It's a file, no children
                    current_level.append(new_node)
    
    return tree_nodes