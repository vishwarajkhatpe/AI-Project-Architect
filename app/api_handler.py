import os
import logging
import streamlit as st
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()
logging.basicConfig(level=logging.INFO)

def get_api_token():
    """
    Priority: 
    1. UI Input (Session State)
    2. Cloud Secrets
    3. Local .env
    """
    # 1. Check if user entered a key in Settings
    if "user_hf_token" in st.session_state and st.session_state.user_hf_token:
        return st.session_state.user_hf_token
    
    # 2. Check Streamlit Cloud Secrets
    try:
        if "HF_TOKEN" in st.secrets:
            return st.secrets["HF_TOKEN"]
    except Exception:
        pass
    
    # 3. Check Local .env
    return os.getenv("HF_TOKEN")

def get_ai_response(user_prompt: str) -> str:
    token = get_api_token()
    if not token:
        return "Error: API Token missing. Please add it in Settings."

    client = InferenceClient(token=token)

    # Check if user selected a specific model in Settings, otherwise default to Qwen
    model_id = st.session_state.get("selected_model", "Qwen/Qwen2.5-Coder-32B-Instruct")

    system_instruction = (
        "You are a Senior Software Architect. Generate a starter project structure. "
        "RESPONSE RULES:\n"
        "1. Return ONLY a valid Python dictionary (JSON).\n"
        "2. Keys = file paths (string).\n"
        "3. Values = useful starter boilerplate code (string).\n"
        "4. Do NOT use markdown code blocks.\n"
        "Example: {'main.py': 'print(\"hello\")'}"
    )

    messages = [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": f"Project Idea: {user_prompt}"}
    ]

    try:
        logging.info(f"Contacting {model_id}...")
        response = client.chat_completion(
            model=model_id,
            messages=messages,
            max_tokens=1500,
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"AI Error: {e}")
        return f"Error: {str(e)}"