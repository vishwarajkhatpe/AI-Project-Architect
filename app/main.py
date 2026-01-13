import sys
import os

# --- SYSTEM PATH FIX ---
# This tells Python to look at the project root folder (AI_Scaffolder), 
# not just inside the 'app' folder. This fixes ModuleNotFoundError.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# -----------------------

import streamlit as st
import time
from app.api_handler import get_ai_response
from app.utils import parse_ai_response
from core.creator import create_in_memory_zip

# 1. Page Configuration
st.set_page_config(
    page_title="AI Project Architect",
    page_icon="🏗️",
    layout="centered"
)

# 2. Custom CSS (Watermark Footer)
st.markdown("""
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #f0f2f6;
        color: #31333F;
        text-align: center;
        padding: 10px;
        font-size: 14px;
        border-top: 1px solid #dcdcdc;
        z-index: 100;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

def main():
    with st.sidebar:
        st.title("🏗️ Project Architect")
        st.write("Generate professional folder structures in seconds.")
        st.info("💡 **Tip:** Be specific! Mention languages (Python, React) and tools (Docker, AWS).")
        st.divider()
        st.caption(f"v1.0.0 | Powered by Hugging Face")

    st.title("Turn Ideas into Code Structure")
    st.subheader("What are you building today?")

    user_prompt = st.text_area(
        "Describe your project:",
        placeholder="E.g., A Machine Learning dashboard with Streamlit, using a 'src' folder for logic and 'tests' for unit testing.",
        height=150
    )

    if st.button("🚀 Generate Structure", type="primary"):
        if not user_prompt.strip():
            st.warning("⚠️ Please describe your project first.")
            return

        with st.status("🤖 AI is designing your project...", expanded=True) as status:
            st.write("🧠 Consulting the Architect...")
            raw_text = get_ai_response(user_prompt)
            
            if "Error" in raw_text:
                status.update(label="❌ Failed", state="error")
                st.error(raw_text)
                return

            st.write("🧹 Cleaning up the blueprints...")
            file_list = parse_ai_response(raw_text)
            
            if not file_list:
                status.update(label="❌ Failed to parse", state="error")
                st.error("The AI replied, but I couldn't find a file list. Try being more specific.")
                with st.expander("See Raw Output"):
                    st.code(raw_text)
                return

            st.write("📦 Packaging files...")
            zip_bytes = create_in_memory_zip(file_list)
            
            status.update(label="✅ Ready!", state="complete", expanded=False)

        st.success(f"✨ Success! Generated {len(file_list)} files/folders.")

        with st.expander("📂 Preview Folder Structure", expanded=True):
            for file in file_list:
                st.text(f"📄 {file}")

        st.download_button(
            label="📥 Download Project (.zip)",
            data=zip_bytes,
            file_name="my_ai_project.zip",
            mime="application/zip",
            type="primary"
        )

    st.markdown(
        '<div class="footer">Built with ❤️ by <b>VishwarajKhatpe</b> using AI Project Architect</div>', 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()