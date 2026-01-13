# test_local.py
import logging
from app.utils import parse_ai_response
from core.creator import create_in_memory_zip

# Setup logging
logging.basicConfig(level=logging.INFO)

def run_tests():
    print("--- 🧪 Starting Verification Tests ---")

    # TEST 1: Check if the Parser works
    print("\n1. Testing AI Parser...")
    fake_ai_response = "Sure, I can help! Here is your list: ['app/main.py', 'data/data.csv'] Hope this helps."
    parsed_list = parse_ai_response(fake_ai_response)
    
    if parsed_list == ['app/main.py', 'data/data.csv']:
        print("✅ Parser Test PASSED: List extracted correctly.")
    else:
        print(f"❌ Parser Test FAILED. Got: {parsed_list}")

    # TEST 2: Check if ZIP creation works
    print("\n2. Testing ZIP Engine...")
    try:
        dummy_files = ["test_file.txt", "folder/script.py"]
        zip_bytes = create_in_memory_zip(dummy_files)
        
        # Check if we actually got bytes back
        if isinstance(zip_bytes, bytes) and len(zip_bytes) > 0:
            print(f"✅ ZIP Test PASSED: Generated {len(zip_bytes)} bytes of data.")
        else:
            print("❌ ZIP Test FAILED: Returned empty or wrong type.")
            
    except Exception as e:
        print(f"❌ ZIP Test CRASHED: {e}")

    print("\n--- 🏁 Verification Complete ---")

if __name__ == "__main__":
    run_tests()