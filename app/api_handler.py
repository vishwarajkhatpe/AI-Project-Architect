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

# UPDATED: Added 'structure_only' parameter
def get_ai_response(user_prompt: str, structure_only: bool = False) -> str:
    token = get_api_token()
    if not token: return "Error: API Token missing."
    
    client = InferenceClient(token=token)
    model_id = st.session_state.get("selected_model", "Qwen/Qwen2.5-Coder-32B-Instruct")

    # --- TWO DIFFERENT MODES ---
    if structure_only:
        # MODE A: Fast, Structure Only
        system_instruction = (
            "You are a Directory Architect. "
            "Return a JSON dictionary of file paths for the user's project. "
            "Values should be empty strings. "
            "Example: {'src/main.py': '', 'tests/test_api.py': ''}. "
            "Do NOT write any code inside the files."
        )
    else:
        # MODE B: Full Code (The one we had before)
        system_instruction = (
            "You are a Senior DevOps Engineer. "
            "Return a JSON dictionary where keys are paths and values are BOILERPLATE CODE. "
            "Include a README.md explaining the structure."
        )

    messages = [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": f"Project Idea: {user_prompt}"}
    ]

    try:
        response = client.chat_completion(
            model=model_id,
            messages=messages,
            # We need fewer tokens for structure only
            max_tokens=500 if structure_only else 2000, 
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"