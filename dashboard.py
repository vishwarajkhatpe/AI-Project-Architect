import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_tree_select import tree_select
from app.api_handler import get_ai_response
from app.utils import parse_ai_response
from core.creator import create_in_memory_zip

# 1. Page Config
st.set_page_config(page_title="AI Architect Pro V2", page_icon="🚀", layout="wide")

# 2. Styling (CSS)
st.markdown("""
    <style>
    /* Footer Styling */
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; background-color: #f8f9fa; color: #6c757d; text-align: center; padding: 8px; font-size: 0.8rem; border-top: 1px solid #dee2e6; z-index: 100; }
    
    /* SCROLLABLE CODE BLOCK FIX */
    /* This forces the code box to be max 500px tall with a scrollbar */
    .element-container:has(.stCodeBlock) {
        max-height: 500px;
        overflow-y: auto;
        border: 1px solid #ddd;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

def convert_to_tree(file_data):
    nodes = []
    for path in file_data.keys():
        parts = path.split('/')
        if len(parts) == 1:
            nodes.append({"label": parts[0], "value": path})
        else:
            folder = parts[0]
            existing = next((n for n in nodes if n["label"] == folder), None)
            if not existing:
                existing = {"label": folder, "value": folder, "children": []}
                nodes.append(existing)
            existing["children"].append({"label": parts[-1], "value": path})
    return nodes

def main():
    # --- SIDEBAR ---
    with st.sidebar:
        st.title("🏗️ AI Architect")
        selected = option_menu(
            None, ["Generator", "Settings"], 
            icons=['lightning', 'gear'], menu_icon="cast", default_index=0,
            styles={"nav-link-selected": {"background-color": "#007BFF"}}
        )
        st.divider()
        st.caption("Version 2.3: Scrollable UI")

    # --- PAGE: GENERATOR ---
    if selected == "Generator":
        st.title("V2.0: Project Boilerplate Generator")
        if "file_data" not in st.session_state: st.session_state.file_data = {}

        col1, col2 = st.columns([1, 1.5], gap="large")

        with col1:
            st.subheader("📝 Project Idea")
            user_input = st.text_area("Description:", placeholder="E.g. A React app with Tailwind...", height=200)
            
            st.write("")
            if st.button("✨ Generate Boilerplate", type="primary", use_container_width=True):
                if user_input:
                    with st.spinner("🤖 AI is working..."):
                        if "selected_model" not in st.session_state:
                            st.session_state.selected_model = "Qwen/Qwen2.5-Coder-32B-Instruct"
                            
                        raw_response = get_ai_response(user_input)
                        parsed_dict = parse_ai_response(raw_response)
                        if parsed_dict:
                            st.session_state.file_data = parsed_dict
                            st.toast("✅ Success!", icon="🚀")
                        else:
                            st.error("AI Error. Check Settings.")

        with col2:
            st.subheader("📂 Preview")
            with st.container(border=True):
                if st.session_state.file_data:
                    tree_nodes = convert_to_tree(st.session_state.file_data)
                    all_vals = [n["value"] for n in tree_nodes]
                    
                    c1, c2 = st.columns([1, 2])
                    with c1:
                        # Fixed Tree: Takes up 1/3 of space
                        selected_tree = tree_select(tree_nodes, no_cascade=True, expanded=all_vals)
                    with c2:
                        # Fixed Code: Takes up 2/3 of space
                        if selected_tree['checked']:
                            f = selected_tree['checked'][0]
                            if f in st.session_state.file_data:
                                lang = "python" if f.endswith(".py") else "text"
                                # The CSS above will automatically make this scrollable!
                                st.code(st.session_state.file_data[f], language=lang, line_numbers=True)
                else:
                    st.info("Waiting for input...")

        if st.session_state.file_data:
            st.divider()
            b1, b2, b3 = st.columns([1, 2, 1])
            with b2:
                st.download_button("📥 Download ZIP", create_in_memory_zip(st.session_state.file_data), "project.zip", "application/zip", type="primary", use_container_width=True)

    # --- PAGE: SETTINGS ---
    elif selected == "Settings":
        st.title("⚙️ Configuration")
        
        with st.container(border=True):
            st.subheader("🔑 API Access")
            st.info("Your local .env token is used by default.")
            user_token = st.text_input("Override Token (Optional)", type="password", placeholder="hf_...")

        with st.container(border=True):
            st.subheader("🧠 AI Model Engine")
            model_mode = st.radio("Select Source:", ["Official Presets", "Custom Model ID"], horizontal=True)
            
            if model_mode == "Official Presets":
                model_choice = st.selectbox("Choose Model:", ["Qwen/Qwen2.5-Coder-32B-Instruct", "google/gemma-2-9b-it"], index=0)
            else:
                model_choice = st.text_input("Enter HuggingFace Model ID:", "Qwen/Qwen2.5-Coder-32B-Instruct")

        st.write("")
        if st.button("💾 Apply Settings", type="primary"):
            if user_token: st.session_state.user_hf_token = user_token
            st.session_state.selected_model = model_choice
            st.toast("✅ Settings Saved!", icon="💾")
            st.success(f"Model set to: **{model_choice}**")

    st.markdown('<div class="footer">Created by <b>VishwarajKhatpe</b></div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()