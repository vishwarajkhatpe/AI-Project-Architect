import re
import ast
import logging

# Configure logging to track what happens inside the parser
logging.basicConfig(level=logging.INFO)

def parse_ai_response(response_text: str) -> list:
    """
    Extracts a Python list of file paths from a string containing mixed text.
    
    Args:
        response_text (str): The raw string output from the AI model.
        
    Returns:
        list: A clean list of file strings (e.g., ["main.py", "requirements.txt"])
    """
    try:
        # 1. Regex Pattern: Look for content strictly inside square brackets [ ... ]
        # The pattern \[.*?\] matches anything starting with [ and ending with ]
        # re.DOTALL allows the search to work even if the list spans multiple lines
        match = re.search(r"\[.*\]", response_text, re.DOTALL)
        
        if match:
            # Extract just the list string part (e.g., "['file1.py', 'file2.py']")
            list_str = match.group()
            
            # 2. AST (Abstract Syntax Tree): Safely convert string to a real Python list
            # We use ast.literal_eval instead of eval() because it is safer (avoids running malicious code)
            file_list = ast.literal_eval(list_str)
            
            # Ensure it's actually a list
            if isinstance(file_list, list):
                return file_list
        
        # Fallback: If regex fails, assume the AI failed or gave plain text
        logging.warning("Regex failed to find a list. Returning empty.")
        return []

    except Exception as e:
        logging.error(f"Error parsing AI response: {e}")
        return []