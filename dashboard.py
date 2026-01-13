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
    # Load defaults
    if "complexity" not in st.session_state: st.session_state.complexity = "Working Code"
    
    with st.sidebar:
        st.title("📂 Folder Builder")
        selected = option_menu(None, ["Builder", "Settings"], icons=['folder', 'gear'], menu_icon="cast", default_index=0)
        st.divider()
        st.caption("Version 3.2: Optimized")

    # --- BUILDER PAGE ---
    if selected == "Builder":
        st.title("AI Folder Structure Builder")
        if "file_data" not in st.session_state: st.session_state.file_data = {}

        col1, col2 = st.columns([1, 1.5], gap="large")

        with col1:
            st.subheader("1. Define Structure")
            
            # Show active mode
            st.caption(f"Active Mode: **{st.session_state.complexity}**")
            
            user_input = st.text_area("What do you want to build?", placeholder="E.g. A flask app with templates...", height=150)
            
            if st.button("🔨 Build Structure", type="primary", use_container_width=True):
                if user_input:
                    with st.spinner(f"Building ({st.session_state.complexity})..."):
                        raw = get_ai_response(user_input, complexity=st.session_state.complexity)
                        parsed = parse_ai_response(raw)
                        if parsed:
                            st.session_state.file_data = parsed
                            st.toast("✅ Built Successfully!", icon="📂")
                        else:
                            st.error("AI Error. Try again.")

        with col2:
            st.subheader("2. Preview & Select")
            with st.container(border=True):
                if st.session_state.file_data:
                    tree_nodes = convert_to_tree(st.session_state.file_data)
                    all_vals = [n["value"] for n in tree_nodes]
                    
                    c1, c2 = st.columns([1, 2])
                    with c1:
                        # Interactive Tree
                        selected_tree = tree_select(tree_nodes, no_cascade=True, expanded=all_vals)
                    with c2:
                        # Code Preview
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

        # --- SELECTIVE DOWNLOAD LOGIC ---
        if st.session_state.file_data:
            st.divider()
            
            # 1. Filter: Get only files that are checked in the tree
            files_to_zip = {}
            checked_list = selected_tree.get('checked', [])
            
            # If nothing is checked, we assume 0 files.
            # If items are checked, we filter the main data.
            if checked_list:
                for f in checked_list:
                    if f in st.session_state.file_data:
                        files_to_zip[f] = st.session_state.file_data[f]
            else:
                # If user unchecks everything, list is empty
                files_to_zip = {}

            # 2. Dynamic Button Label
            count = len(files_to_zip)
            btn_label = f"📥 Download ZIP ({count} Files)" if count > 0 else "Select files to download"
            btn_disabled = count == 0
            
            b1, b2, b3 = st.columns([1, 2, 1])
            with b2:
                st.download_button(
                    label=btn_label,
                    data=create_in_memory_zip(files_to_zip) if count > 0 else b"empty",
                    file_name="custom_structure.zip",
                    mime="application/zip",
                    type="primary",
                    use_container_width=True,
                    disabled=btn_disabled
                )

    # --- SETTINGS PAGE ---
    elif selected == "Settings":
        st.title("⚙️ Configuration")
        
        # 1. COMPLEXITY DROPDOWN (Replaces Slider)
        with st.container(border=True):
            st.subheader("🎚️ Output Detail Level")
            st.write("Control how much code the AI writes.")
            
            complexity_choice = st.selectbox(
                "Select Detail Level:",
                options=["Structure Only", "Simple Code", "Working Code"],
                index=["Structure Only", "Simple Code", "Working Code"].index(st.session_state.complexity)
            )
            
            # Helper text changes based on selection
            if complexity_choice == "Structure Only":
                st.info("⚡ **Fastest:** Generates empty files. Best for pure folder structures.")
            elif complexity_choice == "Simple Code":
                st.info("🚀 **Balanced:** Generates class/function skeletons (TODOs).")
            else:
                st.info("🧠 **Detailed:** Generates full boilerplate logic. Slower.")

        # 2. MODEL
        with st.container(border=True):
            st.subheader("🧠 AI Model Engine")
            model_mode = st.radio("Select Source:", ["Official Presets", "Custom Model ID"], horizontal=True)
            if model_mode == "Official Presets":
                model_choice = st.selectbox(
                    "Choose Model:", 
                    ["Qwen/Qwen2.5-Coder-32B-Instruct", "google/gemma-2-9b-it"],
                    help="Gemma is faster. Qwen is smarter."
                )
            else:
                model_choice = st.text_input("Enter HuggingFace Model ID:", st.session_state.get("selected_model", "Qwen/Qwen2.5-Coder-32B-Instruct"))

        # 3. API
        with st.container(border=True):
            st.subheader("🔑 API Access")
            st.info("Add your custom API key (Overrides local defaults).")
            user_token = st.text_input("Hugging Face Token", type="password")

        st.write("")
        if st.button("💾 Apply Settings", type="primary"):
            if user_token: st.session_state.user_hf_token = user_token
            st.session_state.selected_model = model_choice
            st.session_state.complexity = complexity_choice
            st.toast("✅ Settings Saved!", icon="💾")

    st.markdown('<div class="footer">Created by <b>VishwarajKhatpe</b></div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()