import re
import ast
import logging

def parse_ai_response(response_text: str) -> dict:
    """
    Extracts a dictionary from the AI text.
    V2.0: Expects {'path': 'content'}
    """
    try:
        # Sniper regex to find the dictionary content between curly braces
        match = re.search(r"\{.*\}", response_text, re.DOTALL)
        
        if match:
            dict_str = match.group()
            # Safely evaluate the string into a Python dictionary
            file_data = ast.literal_eval(dict_str)
            
            if isinstance(file_data, dict):
                return file_data
        
        logging.warning("V2.0 Parser: No dictionary found in response.")
        return {}
    except Exception as e:
        logging.error(f"V2.0 Parsing Error: {e}")
        return {}