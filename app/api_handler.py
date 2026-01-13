import os
import logging
import streamlit as st
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()
logging.basicConfig(level=logging.INFO)

# We use Qwen 2.5 Coder because it's the best at generating structured JSON and code
MODEL_ID = "Qwen/Qwen2.5-Coder-32B-Instruct"

def get_api_token():
    try:
        if "HF_TOKEN" in st.secrets:
            return st.secrets["HF_TOKEN"]
    except Exception:
        pass
    return os.getenv("HF_TOKEN")

def get_ai_response(user_prompt: str) -> str:
    token = get_api_token()
    if not token:
        return "Error: API Token missing."

    client = InferenceClient(token=token)

    # V2.0 System Instruction: Demanding JSON with actual code boilerplate
    system_instruction = (
        "You are a Senior Software Architect. Generate a starter project structure. "
        "RESPONSE RULES:\n"
        "1. Return ONLY a valid Python dictionary (JSON).\n"
        "2. Keys = file paths (string).\n"
        "3. Values = useful starter boilerplate code (string).\n"
        "4. Do NOT use markdown code blocks like ```json.\n"
        "Example: {'main.py': 'print(\"hello\")', 'README.md': '# Project'}"
    )

    messages = [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": f"Project Idea: {user_prompt}"}
    ]

    try:
        logging.info(f"V2.0 Logic: Contacting {MODEL_ID} for Boilerplate...")
        response = client.chat_completion(
            model=MODEL_ID,
            messages=messages,
            max_tokens=1500, # Increased to allow room for actual code content
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"AI Error: {e}")
        return f"Error: {str(e)}"