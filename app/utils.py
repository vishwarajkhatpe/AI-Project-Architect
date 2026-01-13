import re
import ast
import json
import logging

def flatten_dict(d, parent_key='', sep='/'):
    """
    Recursively flattens a nested dictionary.
    Example: {'src': {'main.py': 'print(1)'}} -> {'src/main.py': 'print(1)'}
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            # Recursively flatten sub-dictionaries
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def parse_ai_response(response_text: str) -> dict:
    """
    Robust parser that handles Markdown, JSON, Python Dicts, AND Nested Structures.
    """
    # 0. Safety Check: If it's already a dict (rare), just flatten and return
    if isinstance(response_text, dict):
        return flatten_dict(response_text)
        
    try:
        # 1. Clean up Markdown wrappers
        clean_text = re.sub(r"^```[a-zA-Z]*\n", "", response_text.strip())
        clean_text = re.sub(r"\n```$", "", clean_text)

        # 2. Extract the JSON/Dict part
        match = re.search(r"(\{.*\})", clean_text, re.DOTALL)
        if not match:
            return {}
            
        json_str = match.group(1)
        
        # 3. Parse it
        data = {}
        try:
            data = json.loads(json_str)
        except:
            try:
                data = ast.literal_eval(json_str)
            except:
                pass
        
        # 4. CRITICAL FIX: Flatten the data before returning
        # This prevents the 'dict object has no attribute strip' error
        if isinstance(data, dict):
            return flatten_dict(data)
            
        return {}

    except Exception as e:
        logging.error(f"Parsing Error: {e}")
        return {}