import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_tree_select import tree_select
from app.api_handler import get_ai_response
from app.utils import parse_ai_response
from core.creator import create_in_memory_zip

# 1. Page Config
st.set_page_config(
    page_title="AI Architect Pro",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Professional CSS Styling
st.markdown("""
    <style>
    .block-container { padding-top: 2rem; }
    .footer {
        position: fixed; left: 0; bottom: 0; width: 100%;
        background-color: #f8f9fa; color: #6c757d;
        text-align: center; padding: 10px;
        font-size: 0.8rem; border-top: 1px solid #dee2e6;
        z-index: 999;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

def convert_paths_to_tree(file_list):
    """Converts flat list to nested tree structure for the UI."""
    tree_nodes = []
    structure = {}
    
    for path in file_list:
        parts = path.split("/")
        if len(parts) > 1:
            folder = parts[0]
            file = "/".join(parts[1:])
            if folder not in structure: structure[folder] = []
            structure[folder].append(file)
        else:
            if "root" not in structure: structure["root"] = []
            structure["root"].append(path)

    for folder, files in structure.items():
        if folder == "root":
            for f in files: tree_nodes.append({"label": f, "value": f})
        else:
            children = [{"label": f, "value": f"{folder}/{f}"} for f in files]
            tree_nodes.append({"label": folder, "value": folder, "children": children})
            
    return tree_nodes

def main():
    # --- SIDEBAR ---
    with st.sidebar:
        st.title("🏗️ AI Architect")
        selected = option_menu(
            menu_title=None,
            options=["Generator", "History", "Settings"],
            icons=["lightning-fill", "clock-history", "gear"],
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "#fafafa"},
                "nav-link-selected": {"background-color": "#4CAF50"},
            }
        )
        st.divider()
        st.caption("v2.0 Pro | Model: Qwen 2.5")

    # --- PAGE: GENERATOR ---
    if selected == "Generator":
        col1, col2 = st.columns([1.5, 1])

        with col1:
            st.subheader("🛠️ Project Blueprint")
            st.markdown("Describe your app, and AI will architect the perfect folder structure.")
            
            user_prompt = st.text_area("Project Description", height=200, placeholder="Example: A SaaS boilerplate with FastAPI backend...")
            generate_btn = st.button("✨ Generate Architecture", type="primary", use_container_width=True)

        if "generated_files" not in st.session_state:
            st.session_state.generated_files = None

        if generate_btn:
            if not user_prompt.strip():
                st.toast("⚠️ Please describe your project first!", icon="⚠️")
            else:
                with st.spinner("🤖 AI is brainstorming structure..."):
                    raw_text = get_ai_response(user_prompt)
                    if "Error" in raw_text:
                        st.error(raw_text)
                    else:
                        file_list = parse_ai_response(raw_text)
                        if file_list:
                            st.session_state.generated_files = file_list
                            st.toast("✅ Blueprint Generated!", icon="🎉")
                        else:
                            st.error("Could not parse AI response.")

        # --- PREVIEW & DOWNLOAD ---
        if st.session_state.generated_files:
            with col2:
                st.subheader("📂 Interactive Preview")
                tree_data = convert_paths_to_tree(st.session_state.generated_files)
                
                selected_paths = tree_select(
                    tree_data,
                    checked=[node["value"] for node in tree_data],
                    expanded=[node["value"] for node in tree_data],
                    no_cascade=True
                )
                
                st.divider()
                # For simplicity, we zip everything generated, regardless of checkbox
                zip_bytes = create_in_memory_zip(st.session_state.generated_files)
                
                st.download_button(
                    label=f"📥 Download (.zip)",
                    data=zip_bytes,
                    file_name="project_structure.zip",
                    mime="application/zip",
                    type="primary",
                    use_container_width=True
                )

    # --- Footer ---
    st.markdown('<div class="footer">Built with ❤️ by <b>YourName</b></div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()