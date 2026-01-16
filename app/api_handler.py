from huggingface_hub import InferenceClient
import json

def get_ai_response(user_prompt, api_key=None, complexity="Working Code", model="Qwen/Qwen2.5-Coder-32B-Instruct"):
    """
    Uses the official huggingface_hub client with a strict One-Shot Prompt.
    """
    
    # 1. Validate API Key
    if not api_key:
        return json.dumps({"error": "No API Key provided. Please check your Settings."})

    # 2. Strict One-Shot Example (The Fix)
    # We show the AI exactly what we want so it stops being lazy.
    example_json = """
    {
      "my_project": {
        "app.py": "print('hello world')",
        "requirements.txt": "flask",
        "utils": {
          "helper.py": "def add(a,b): return a+b"
        }
      }
    }
    """

    base_instruction = f"""
    You are an expert Software Architect. 
    You MUST output a valid JSON object representing a folder structure.
    
    RULES:
    1. The keys are filenames or folder names.
    2. If the value is a STRING, it is file content (code).
    3. If the value is a OBJECT (Dict), it is a folder.
    4. Do not include markdown formatting (like ```json). Just the raw JSON.
    
    EXAMPLE OUTPUT:
    {example_json}
    """

    if complexity == "Structure Only":
        role_msg = "Create a deep folder structure with empty strings for file content."
    elif complexity == "Simple Code":
        role_msg = "Create a folder structure. File content should be short comments or class skeletons only."
    else:
        role_msg = "Create a production-ready structure. File content must be FULL, working code with imports."

    # 3. Create Client
    client = InferenceClient(token=api_key)

    try:
        # 4. Chat Completion
        response = client.chat_completion(
            model=model,
            messages=[
                {"role": "system", "content": base_instruction},
                {"role": "user", "content": f"{role_msg}\n\nRequest: {user_prompt}"}
            ],
            max_tokens=3000, # Increased token limit for deeper trees
            temperature=0.1, # Lower temperature = More strict/deterministic
            stream=False
        )
        
        return response.choices[0].message.content

    except Exception as e:
        error_msg = str(e)
        if "503" in error_msg:
            return json.dumps({"error": "The AI model is loading (Cold Start). Please wait 30s and try again."})
        elif "404" in error_msg:
             return json.dumps({"error": f"Model '{model}' not found. Try switching to 'google/gemma-2-9b-it'."})
        else:
            return json.dumps({"error": f"Connection Error: {error_msg}"})