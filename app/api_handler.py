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

def get_ai_response(user_prompt: str, complexity: str = "Working Code") -> str:
    token = get_api_token()
    if not token: return "Error: API Token missing."
    
    client = InferenceClient(token=token)
    model_id = st.session_state.get("selected_model", "Qwen/Qwen2.5-Coder-32B-Instruct")

    # --- SPEED OPTIMIZATION ---
    if complexity == "Structure Only":
        # Ultra-short prompt for maximum speed
        system_instruction = (
            "You are a fast JSON generator. "
            "Return a JSON dict of file paths for this project. "
            "Values MUST be empty strings. "
            "NO explanations. NO markdown."
        )
        max_tokens = 300 # Reduced to force brevity
        
    elif complexity == "Simple Code":
        system_instruction = (
            "You are a Software Architect. "
            "Return JSON where values are SKELETON code (class/def only, pass body). "
            "NO markdown."
        )
        max_tokens = 1000
        
    else: # Working Code
        system_instruction = (
            "You are a Senior Developer. "
            "Return JSON with FULL WORKING boilerplate code and a README.md."
        )
        max_tokens = 2000

    messages = [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": user_prompt}
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