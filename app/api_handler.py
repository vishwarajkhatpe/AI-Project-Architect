import os
import logging
import streamlit as st
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()
logging.basicConfig(level=logging.INFO)

def get_api_token():
    if "user_hf_token" in st.session_state and st.session_state.user_hf_token:
        return st.session_state.user_hf_token
    try:
        if "HF_TOKEN" in st.secrets: return st.secrets["HF_TOKEN"]
    except: pass
    return os.getenv("HF_TOKEN")

# UPDATED: Now accepts a 'complexity' string
def get_ai_response(user_prompt: str, complexity: str = "Working Code") -> str:
    token = get_api_token()
    if not token: return "Error: API Token missing."
    
    client = InferenceClient(token=token)
    model_id = st.session_state.get("selected_model", "Qwen/Qwen2.5-Coder-32B-Instruct")

    # --- THREE LEVELS OF COMPLEXITY ---
    if complexity == "Structure Only":
        # Level 1: Just files, no content
        system_instruction = (
            "You are a Directory Architect. "
            "Return a JSON dictionary of file paths. "
            "Values MUST be empty strings. "
            "Example: {'src/main.py': '', 'tests/test_api.py': ''}."
        )
        max_tokens = 500
        
    elif complexity == "Simple Code":
        # Level 2: Skeletons and TODOs
        system_instruction = (
            "You are a Software Architect. "
            "Return a JSON dictionary where values are SKELETON code. "
            "Include class names, function definitions, and docstrings, but use 'pass' for the body. "
            "Example: {'main.py': 'def run():\\n    # TODO: Add logic\\n    pass'}"
        )
        max_tokens = 1000
        
    else: # "Working Code"
        # Level 3: Full logic
        system_instruction = (
            "You are a Senior Developer. "
            "Return a JSON dictionary where values are FULL WORKING boilerplate code. "
            "Include imports, error handling, and a README.md."
        )
        max_tokens = 2000

    messages = [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": f"Project Idea: {user_prompt}"}
    ]

    try:
        response = client.chat_completion(
            model=model_id,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"