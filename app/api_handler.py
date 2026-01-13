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

    # --- TOKEN LIMITS UPGRADED ---
    if complexity == "Structure Only":
        system_instruction = (
            "You are a JSON generator. Return a JSON dict of file paths with empty values. "
            "Strictly JSON only. No markdown."
        )
        max_tokens = 500
        
    elif complexity == "Simple Code":
        system_instruction = (
            "You are a Software Architect. Return JSON where values are SKELETON code (class/def signatures only). "
            "Strictly JSON only. No markdown."
        )
        max_tokens = 1500
        
    else: # Working Code
        system_instruction = (
            "You are a Senior Developer. "
            "Return a valid JSON dictionary where keys are paths and values are WORKING CODE. "
            "Do NOT stop mid-stream. Keep code concise to fit in JSON. "
            "Strictly JSON only. No markdown intro/outro."
        )
        # BUMPED TO 4096 (Max safe limit)
        max_tokens = 4096

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