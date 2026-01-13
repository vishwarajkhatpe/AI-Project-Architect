import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_tree_select import tree_select
from app.api_handler import get_ai_response
from app.utils import parse_ai_response
from core.creator import create_in_memory_zip

# 1. Page Config
st.set_page_config(page_title="AI Folder Builder", page_icon="📂", layout="wide")

# 2. Styling
st.markdown("""
    <style>
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; background-color: #f8f9fa; color: #6c757d; text-align: center; padding: 8px; font-size: 0.8rem; border-top: 1px solid #dee2e6; z-index: 100; }
    .element-container:has(.stCodeBlock) { max-height: 500px; overflow-y: auto; border: 1px solid #ddd; border-radius: 8px; }
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
    # Load default settings if not present
    if "complexity" not in st.session_state: st.session_state.complexity = "Working Code"
    if "selected_model" not in st.session_state: st.session_state.selected_model = "Qwen/Qwen2.5-Coder-32B-Instruct"

    with st.sidebar:
        st.title("📂 Folder Builder")
        selected = option_menu(None, ["Builder", "Settings"], icons=['folder', 'gear'], menu_icon="cast", default_index=0)
        st.divider()
        st.caption("Version 3.1: 3-Level Logic")

    # --- BUILDER PAGE ---
    if selected == "Builder":
        st.title("AI Folder Structure Builder")
        if "file_data" not in st.session_state: st.session_state.file_data = {}

        col1, col2 = st.columns([1, 1.5], gap="large")

        with col1:
            st.subheader("1. Define Structure")
            
            # Show current settings summary (User feedback)
            st.caption(f"Current Mode: **{st.session_state.complexity}** (Change in Settings)")

            user_input = st.text_area("What do you want to build?", placeholder="E.g. A Django project...", height=150)
            
            if st.button("🔨 Build Structure", type="primary", use_container_width=True):
                if user_input:
                    with st.spinner(f"Building ({st.session_state.complexity} mode)..."):
                        # Pass the saved complexity setting to the backend
                        raw = get_ai_response(user_input, complexity=st.session_state.complexity)
                        parsed = parse_ai_response(raw)
                        if parsed:
                            st.session_state.file_data = parsed
                            st.toast("✅ Built Successfully!", icon="📂")
                        else:
                            st.error("AI Error. Try again.")

        with col2:
            st.subheader("2. Preview & Download")
            with st.container(border=True):
                if st.session_state.file_data:
                    tree_nodes = convert_to_tree(st.session_state.file_data)
                    all_vals = [n["value"] for n in tree_nodes]
                    
                    c1, c2 = st.columns([1, 2])
                    with c1:
                        selected_tree = tree_select(tree_nodes, no_cascade=True, expanded=all_vals)
                    with c2:
                        if selected_tree['checked']:
                            f = selected_tree['checked'][0]
                            if f in st.session_state.file_data:
                                content = st.session_state.file_data[f]
                                if not content.strip():
                                    st.info(f"📄 {f} (Empty File)")
                                else:
                                    lang = "python" if f.endswith(".py") else "text"
                                    st.code(content, language=lang, line_numbers=True)
                else:
                    st.info("Your folder tree will appear here.")

        if st.session_state.file_data:
            st.divider()
            
            # Selective Download Logic
            selected_files_only = {}
            checked_items = selected_tree.get('checked', [])
            if checked_items:
                for f in checked_items:
                    if f in st.session_state.file_data:
                        selected_files_only[f] = st.session_state.file_data[f]
            final_data = selected_files_only if selected_files_only else st.session_state.file_data
            
            b1, b2, b3 = st.columns([1, 2, 1])
            with b2:
                st.download_button(
                    label=f"📥 Download ZIP ({len(final_data)} Items)",
                    data=create_in_memory_zip(final_data),
                    file_name="folder_structure.zip",
                    mime="application/zip",
                    type="primary",
                    use_container_width=True
                )

    # --- SETTINGS PAGE (UPDATED) ---
    elif selected == "Settings":
        st.title("⚙️ Configuration")
        
        # 1. GENERATION COMPLEXITY (NEW!)
        with st.container(border=True):
            st.subheader("🎚️ Output Detail Level")
            st.write("Control how much code the AI writes.")
            
            complexity_choice = st.select_slider(
                "Select Detail Level:",
                options=["Structure Only", "Simple Code", "Working Code"],
                value=st.session_state.get("complexity", "Working Code")
            )
            
            # Explanations for the user
            if complexity_choice == "Structure Only":
                st.info("⚡ **Fastest:** Generates empty files and folders only. Good for starting from scratch.")
            elif complexity_choice == "Simple Code":
                st.info("🚀 **Balanced:** Generates class definitions, functions, and TODO comments. Good for prototyping.")
            else:
                st.info("🧠 **Detailed:** Generates full boilerplate logic, imports, and READMEs. Takes longer.")

        # 2. MODEL ENGINE
        with st.container(border=True):
            st.subheader("🧠 AI Model Engine")
            model_mode = st.radio("Select Source:", ["Official Presets", "Custom Model ID"], horizontal=True)
            if model_mode == "Official Presets":
                model_choice = st.selectbox("Choose Model:", ["Qwen/Qwen2.5-Coder-32B-Instruct", "google/gemma-2-9b-it"], index=0)
            else:
                model_choice = st.text_input("Enter HuggingFace Model ID:", st.session_state.get("selected_model", "Qwen/Qwen2.5-Coder-32B-Instruct"))

        # 3. API KEY
        with st.container(border=True):
            st.subheader("🔑 API Access")
            st.info("Add your custom API key (Overrides local defaults).")
            user_token = st.text_input("Hugging Face Token", type="password")

        st.write("")
        if st.button("💾 Apply Settings", type="primary"):
            if user_token: st.session_state.user_hf_token = user_token
            st.session_state.selected_model = model_choice
            st.session_state.complexity = complexity_choice # SAVE THE SETTING
            st.toast("✅ Configuration Updated!", icon="💾")

    st.markdown('<div class="footer">Created by <b>VishwarajKhatpe</b></div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()