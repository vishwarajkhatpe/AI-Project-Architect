import streamlit as st
import time
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
    if "complexity" not in st.session_state: st.session_state.complexity = "Working Code"
    
    # Session State for Tree
    if "tree_key" not in st.session_state: st.session_state.tree_key = 0
    if "checked_files" not in st.session_state: st.session_state.checked_files = []
    
    with st.sidebar:
        st.title("📂 Folder Builder")
        selected = option_menu(None, ["Builder", "Settings"], icons=['folder', 'gear'], menu_icon="cast", default_index=0)
        st.divider()
        st.caption("Version 3.5: Better UX")

    if selected == "Builder":
        st.title("AI Folder Structure Builder")
        if "file_data" not in st.session_state: st.session_state.file_data = {}

        col1, col2 = st.columns([1, 1.5], gap="large")

        with col1:
            st.subheader("1. Define Structure")
            
            # Helper text for the mode
            mode = st.session_state.complexity
            if mode == "Structure Only":
                st.caption(f"Active Mode: **{mode}** (⚡ Fast)")
            elif mode == "Simple Code":
                st.caption(f"Active Mode: **{mode}** (🚀 ~10s)")
            else:
                st.caption(f"Active Mode: **{mode}** (🧠 ~45s wait)")
            
            user_input = st.text_area("What do you want to build?", placeholder="E.g. A flask app...", height=150)
            
            if st.button("🔨 Build Structure", type="primary", use_container_width=True):
                if user_input:
                    # --- NEW LOADING LOGIC ---
                    # We use st.status instead of st.spinner for better feedback
                    status_label = "Initializing..."
                    if mode == "Structure Only":
                        status_label = "⚡ Generating folder structure..."
                    elif mode == "Simple Code":
                        status_label = "🚀 Drafting code skeletons..."
                    else:
                        status_label = "🧠 Writing full boilerplate code (Please wait ~45s)..."

                    # st.status creates a container that shows we are working
                    with st.status(status_label, expanded=True) as status:
                        st.write("Connecting to AI Brain...")
                        
                        # API Call
                        raw = get_ai_response(user_input, complexity=mode)
                        
                        st.write("Parsing response...")
                        parsed = parse_ai_response(raw)
                        
                        if parsed:
                            st.session_state.file_data = parsed
                            
                            # RESET: Default Select All
                            all_files = list(parsed.keys())
                            st.session_state.checked_files = all_files
                            st.session_state.tree_key += 1 
                            
                            status.update(label="✅ Complete!", state="complete", expanded=False)
                            st.toast("✅ Built Successfully!", icon="📂")
                        else:
                            status.update(label="❌ Failed", state="error")
                            st.error("AI Error. Try again.")

        with col2:
            st.subheader("2. Preview & Select")
            with st.container(border=True):
                if st.session_state.file_data:
                    tree_nodes = convert_to_tree(st.session_state.file_data)
                    all_vals = [n["value"] for n in tree_nodes]
                    
                    # --- SINGLE BUTTON LOGIC ---
                    all_files = list(st.session_state.file_data.keys())
                    current_checked = st.session_state.checked_files
                    
                    if not current_checked:
                        btn_label = "✅ Select All"
                        new_state = all_files
                    else:
                        btn_label = "⬜ Clear All"
                        new_state = []
                    
                    if st.button(btn_label, type="secondary"):
                        st.session_state.checked_files = new_state
                        st.session_state.tree_key += 1 
                        st.rerun()

                    c1, c2 = st.columns([1, 2])
                    with c1:
                        selected_tree = tree_select(
                            tree_nodes, 
                            key=f"tree_{st.session_state.tree_key}", 
                            checked=st.session_state.checked_files,
                            expanded=all_vals, 
                            no_cascade=False
                        )
                        if selected_tree["checked"] != st.session_state.checked_files:
                            st.session_state.checked_files = selected_tree["checked"]
                    
                    with c2:
                        if selected_tree['checked']:
                            target = selected_tree['checked'][0]
                            if target in st.session_state.file_data:
                                content = st.session_state.file_data[target]
                                if not content.strip():
                                    st.info(f"📄 {target} (Empty)")
                                else:
                                    lang = "python" if target.endswith(".py") else "text"
                                    st.code(content, language=lang, line_numbers=True)
                            else:
                                st.info(f"📂 Folder: {target}")
                        else:
                            st.info("Select a file.")
                else:
                    st.info("Your folder tree will appear here.")

        if st.session_state.file_data:
            st.divider()
            files_to_zip = {}
            checked_list = st.session_state.checked_files
            
            if checked_list:
                for f in checked_list:
                    if f in st.session_state.file_data:
                        files_to_zip[f] = st.session_state.file_data[f]
            
            count = len(files_to_zip)
            btn_label = f"📥 Download ZIP ({count} Files)" if count > 0 else "Select files to download"
            
            b1, b2, b3 = st.columns([1, 2, 1])
            with b2:
                st.download_button(
                    label=btn_label,
                    data=create_in_memory_zip(files_to_zip) if count > 0 else b"empty",
                    file_name="custom_structure.zip",
                    mime="application/zip",
                    type="primary",
                    use_container_width=True,
                    disabled=(count == 0)
                )

    elif selected == "Settings":
        st.title("⚙️ Configuration")
        with st.container(border=True):
            st.subheader("🎚️ Output Detail Level")
            complexity_choice = st.selectbox("Select Detail Level:", ["Structure Only", "Simple Code", "Working Code"], index=["Structure Only", "Simple Code", "Working Code"].index(st.session_state.complexity))
            if complexity_choice == "Structure Only": st.info("⚡ Fastest: Empty files.")
            elif complexity_choice == "Simple Code": st.info("🚀 Balanced: Skeleton code.")
            else: st.info("🧠 Detailed: Full logic.")

        with st.container(border=True):
            st.subheader("🧠 AI Model Engine")
            model_mode = st.radio("Select Source:", ["Official Presets", "Custom Model ID"], horizontal=True)
            if model_mode == "Official Presets":
                model_choice = st.selectbox("Choose Model:", ["Qwen/Qwen2.5-Coder-32B-Instruct", "google/gemma-2-9b-it"])
            else:
                model_choice = st.text_input("Model ID:", st.session_state.get("selected_model", "Qwen/Qwen2.5-Coder-32B-Instruct"))

        with st.container(border=True):
            st.subheader("🔑 API Access")
            user_token = st.text_input("Custom Token (Optional)", type="password")

        st.write("")
        if st.button("💾 Apply Settings", type="primary"):
            if user_token: st.session_state.user_hf_token = user_token
            st.session_state.selected_model = model_choice
            st.session_state.complexity = complexity_choice
            st.toast("✅ Settings Saved!", icon="💾")

    st.markdown('<div class="footer">Created by <b>VishwarajKhatpe</b></div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()