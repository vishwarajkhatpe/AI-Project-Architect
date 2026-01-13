import os
import logging
import streamlit as st
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# 1. Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)

# --- THE ROBUST MODEL LIST ---
# We try these models in order. If one fails, we try the next.
# These are all high-performance, free, and usually available.
MODELS_TO_TRY = [
    "Qwen/Qwen2.5-Coder-32B-Instruct",      # Best for code
    "microsoft/Phi-3.5-mini-instruct",      # Very fast & reliable
    "google/gemma-2-2b-it",                 # Strong fallback
    "HuggingFaceH4/zephyr-7b-beta"          # Old reliable
]

def get_api_token():
    """Smartly fetches token from Cloud Secrets or Local .env"""
    try:
        if "HF_TOKEN" in st.secrets:
            return st.secrets["HF_TOKEN"]
    except Exception:
        pass
    
    token = os.getenv("HF_TOKEN")
    if not token:
        logging.error("❌ No HF_TOKEN found! Check .env or Secrets.")
    return token

def get_ai_response(user_prompt: str) -> str:
    token = get_api_token()
    if not token:
        return "Error: API Token missing."

    client = InferenceClient(token=token)

    system_instruction = (
        "You are a Senior DevOps Engineer. "
        "Your task: Convert the user's project description into a Python list of file paths. "
        "Rules: "
        "1. Return ONLY the Python list. "
        "2. Do NOT write explanations. "
        "3. Do NOT use code blocks (```). "
        "4. Example output: ['app/main.py', 'data/raw.csv']"
    )

    messages = [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": f"Project Idea: {user_prompt}"}
    ]

    # --- THE RETRY LOOP ---
    for model in MODELS_TO_TRY:
        try:
            logging.info(f"🔄 Attempting to connect to: {model}...")
            
            response = client.chat_completion(
                model=model,
                messages=messages,
                max_tokens=500,
                temperature=0.1
            )
            
            result = response.choices[0].message.content
            logging.info(f"✅ Success with {model}!")
            return result

        except Exception as e:
            logging.warning(f"⚠️ Failed with {model}: {e}")
            continue  # Try the next model in the list

    return "Error: All AI models failed. Please check your token or try again later."