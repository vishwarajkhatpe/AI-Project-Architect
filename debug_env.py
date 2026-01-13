import os
from dotenv import load_dotenv

# Force reload the .env file
load_dotenv(override=True)

print("--- 🔍 Debugging Environment Variables ---")

# Check if .env file exists
if os.path.exists(".env"):
    print("✅ .env file FOUND.")
else:
    print("❌ .env file NOT found. Check the file name and location.")

# Check if Python can read the token
token = os.getenv("HF_TOKEN")
if token:
    print(f"✅ Token Loaded: {token[:4]}... (First 4 chars visible)")
    print("Now trying to print the type...")
    print(f"Type: {type(token)}")
else:
    print("❌ Token is Empty. Check inside your .env file.")
    print("Make sure it says: HF_TOKEN=hf_...")

print("------------------------------------------")