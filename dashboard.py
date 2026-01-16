import streamlit as st
import time
from streamlit_option_menu import option_menu
from streamlit_tree_select import tree_select
from app.api_handler import get_ai_response
from app.utils import parse_ai_response
from core.creator import create_in_memory_zip

# 1. Page Config
st.set_page_config(page_title="AI Architect v5.2", page_icon="🏗️", layout="wide")

# 2. CSS STYLING (Smart Scrolling & Original Design)
st.markdown("""
    <style>
    @keyframes slideIn { from { transform: translateY(-20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
    
    .hero-container {
        background: linear-gradient(135deg, #4338ca 0%, #6366f1 100%);
        padding: 2.5rem;
        border-radius: 16px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(67, 56, 202, 0.3);
        animation: slideIn 0.8s ease-out;
    }
    .hero-title { font-size: 3.2rem; font-weight: 800; margin: 0; color: #ffffff; letter-spacing: -1px; }
    .hero-subtitle { font-size: 1.2rem; color: #e0e7ff; margin-top: 10px; font-weight: 400; }

    .feature-card {
        background: white; padding: 1.5rem; border-radius: 12px; border: 1px solid #e5e7eb;
        text-align: center; transition: all 0.3s ease; height: 100%; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .feature-card:hover { transform: translateY(-5px); border-color: #6366f1; box-shadow: 0 15px 30px rgba(99, 102, 241, 0.15); }
    .feature-icon { font-size: 2.5rem; margin-bottom: 15px; }
    .feature-title { font-weight: 700; font-size: 1.1rem; color: #111827; }
    .feature-desc { color: #6b7280; font-size: 0.9rem; margin-top: 5px; line-height: 1.5; }

    button[kind="primary"] {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
        border: none !important; color: white !important; font-weight: 600 !important;
        padding: 0.6rem 1.4rem; border-radius: 8px; transition: transform 0.2s ease !important;
    }
    button[kind="primary"]:hover { transform: scale(1.02); box-shadow: 0 5px 15px rgba(79, 70, 229, 0.4); }
    
    .footer {
        position: fixed; left: 0; bottom: 0; width: 100%;
        background: #ffffff; color: #9ca3af;
        text-align: center; padding: 12px;
        font-size: 0.8rem; border-top: 1px solid #f3f4f6; z-index: 100;
    }

    /* --- SMART SCROLLING CSS --- */
    
    /* 1. Force Scrollbars to appear ONLY when needed (Auto) */
    div[data-testid="stVerticalBlockBorderWrapper"] > div > div {
        overflow: auto !important; 
    }

    /* 2. Prevent text from wrapping (Forces Horizontal Scroll if text is long) */
    .stTreeSelect div {
        white-space: nowrap !important;
        width: max-content; /* Ensure container grows to fit the widest text */
    }
    </style>
""", unsafe_allow_html=True)

# --- RECURSIVE TREE CONVERTER ---
def convert_to_tree(file_data_keys):
    """
    Converts a list of paths ['src/utils/helper.py'] 
    into nested dictionary format for streamlit-tree-select.
    """
    tree_nodes = []
    for path in file_data_keys:
        parts = path.split('/')
        current_level = tree_nodes
        current_full_path = ""
        for i, part in enumerate(parts):
            current_full_path = f"{current_full_path}/{part}" if current_full_path else part
            existing_node = next((node for node in current_level if node['label'] == part), None)
            if existing_node:
                if 'children' in existing_node:
                    current_level = existing_node['children']
            else:
                is_file = (i == len(parts) - 1)
                new_node = {"label": part, "value": current_full_path, "showCheckbox": True}
                if not is_file:
                    new_node["children"] = []
                    current_level.append(new_node)
                    current_level = new_node["children"]
                else:
                    current_level.append(new_node)
    return tree_nodes

def main():
    if "complexity" not in st.session_state: st.session_state.complexity = "Working Code"
    if "tree_key" not in st.session_state: st.session_state.tree_key = 0
    if "checked_files" not in st.session_state: st.session_state.checked_files = []
    if "nav_index" not in st.session_state: st.session_state.nav_index = 0
    if "menu_key" not in st.session_state: st.session_state.menu_key = 0

    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3767/3767084.png", width=55)
        st.markdown("### AI Architect")
        
        # NAVIGATION
        menu_options = ["Home", "Builder", "Settings", "Help / FAQ"]
        selected = option_menu(
            menu_title=None,
            options=menu_options, 
            icons=['house', 'hammer', 'sliders', 'question-circle'], 
            default_index=st.session_state.nav_index,
            key=f"menu_{st.session_state.menu_key}", 
            styles={
                "nav-link": {"border-radius": "8px", "margin": "5px 0", "font-size": "0.9rem"},
                "nav-link-selected": {"background-color": "#4f46e5", "font-weight": "600"},
            }
        )
        if menu_options.index(selected) != st.session_state.nav_index:
            st.session_state.nav_index = menu_options.index(selected)
        
        st.divider()
        st.caption("v5.2 | Stable Build")

    # --- 1. HOME PAGE ---
    if selected == "Home":
        st.markdown("""
            <div class="hero-container">
                <div class="hero-title">AI Architect</div>
                <div class="hero-subtitle">
                    The intelligent engine for modern developers. 
                    Generate production-ready scaffolding in seconds.
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            if st.button("🚀 Launch Project Builder", type="primary", use_container_width=True):
                st.session_state.nav_index = 1  
                st.session_state.menu_key += 1  
                st.rerun()
        
        st.write("")
        st.write("")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown('<div class="feature-card"><div class="feature-icon">⚡</div><div class="feature-title">Rapid Prototyping</div><div class="feature-desc">Go from idea to folder structure instantly. No more manual file creation.</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="feature-card"><div class="feature-icon">🧠</div><div class="feature-title">Intelligent Logic</div><div class="feature-desc">Our AI writes valid Python, React, and SQL boilerplate code for you.</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown('<div class="feature-card"><div class="feature-icon">🛠️</div><div class="feature-title">Full Customization</div><div class="feature-desc">Interactive tree view allows you to select exactly what you need.</div></div>', unsafe_allow_html=True)

    # --- 2. BUILDER PAGE ---
    elif selected == "Builder":
        st.title("Project Studio")
        if "file_data" not in st.session_state: st.session_state.file_data = {}

        col1, col2 = st.columns([1, 1.5], gap="large")

        with col1:
            st.subheader("1. Configuration")
            mode = st.session_state.complexity
            if mode == "Structure Only": st.info("**Mode:** Structure Only (Fastest)")
            elif mode == "Simple Code": st.warning("**Mode:** Simple Code (Skeletons)")
            else: st.success("**Mode:** Working Code (Detailed)")
            
            user_input = st.text_area("Describe your project:", placeholder="E.g. A Data Analysis pipeline using Pandas...", height=180)
            
            if st.button("✨ Generate Blueprint", type="primary", use_container_width=True):
                if user_input:
                    status_label = "Processing..."
                    if mode == "Structure Only": status_label = "Architecting structure..."
                    elif mode == "Simple Code": status_label = "Drafting code skeletons..."
                    else: status_label = "Writing full boilerplate code (~45s)..."

                    with st.status(status_label, expanded=True) as status:
                        st.write("Connecting to AI Engine...")
                        api_key = st.session_state.get("user_hf_token", None)
                        if not api_key and "HF_TOKEN" in st.secrets:
                            api_key = st.secrets["HF_TOKEN"]
                            
                        raw = get_ai_response(user_input, api_key=api_key, complexity=mode)
                        
                        st.write("Parsing blueprint...")
                        parsed = parse_ai_response(raw)
                        
                        if parsed:
                            st.session_state.file_data = parsed
                            st.session_state.checked_files = list(parsed.keys())
                            st.session_state.tree_key += 1 
                            status.update(label="Blueprint Ready", state="complete", expanded=False)
                            st.toast("Project generated successfully!", icon="✅")
                        else:
                            status.update(label="Generation Failed", state="error")
                            st.error("AI Error. Please try again.")
                            with st.expander("View Debug Info"):
                                st.code(raw, language="json")

        with col2:
            st.subheader("2. Preview & Export")
            
            with st.container(border=True):
                if st.session_state.file_data:
                    file_keys = list(st.session_state.file_data.keys())
                    tree_nodes = convert_to_tree(file_keys)
                    
                    all_vals = []
                    def get_all_values(nodes):
                        for node in nodes:
                            all_vals.append(node["value"])
                            if "children" in node: get_all_values(node["children"])
                    get_all_values(tree_nodes)
                    
                    # Controls
                    c_ctrl1, c_ctrl2, c_ctrl3 = st.columns([1, 1, 1.5])
                    with c_ctrl1:
                        if st.button("Select All", use_container_width=True):
                            st.session_state.checked_files = list(st.session_state.file_data.keys())
                            st.session_state.tree_key += 1
                            st.rerun()
                    with c_ctrl2:
                        if st.button("Clear All", use_container_width=True):
                            st.session_state.checked_files = []
                            st.session_state.tree_key += 1
                            st.rerun()
                    with c_ctrl3:
                        # FIX: Add a callback to force-redraw the tree when toggled
                        def on_toggle_change():
                            st.session_state.tree_key += 1
                            
                        expand_mode = st.toggle(
                            "Expand Folders", 
                            value=True, 
                            on_change=on_toggle_change
                        )
                        expanded_items = all_vals if expand_mode else []

                    c1, c2 = st.columns([1, 1])
                    
                    with c1:
                        st.caption("📂 Structure")
                        # 1. FIXED HEIGHT: This container will scroll if content > 500px
                        with st.container(height=500, border=True):
                            selected_tree = tree_select(
                                tree_nodes, 
                                key=f"tree_{st.session_state.tree_key}", 
                                checked=st.session_state.checked_files,
                                expanded=expanded_items, 
                                no_cascade=False
                            )
                            if selected_tree["checked"] != st.session_state.checked_files:
                                st.session_state.checked_files = selected_tree["checked"]
                                st.rerun()
                    
                    with c2:
                        st.caption("📝 Code Viewer")
                        # 2. FIXED HEIGHT: Match the tree height
                        with st.container(height=500, border=True):
                            if selected_tree['checked']:
                                target = selected_tree['checked'][0]
                                if target in st.session_state.file_data:
                                    content = st.session_state.file_data[target]
                                    if not content.strip():
                                        st.info(f"📄 `{target}` is empty")
                                    else:
                                        lang = "python" if target.endswith(".py") else "text"
                                        st.markdown(f"**📄 {target}**")
                                        st.code(content, language=lang, line_numbers=True)
                                else:
                                    st.info(f"📂 Folder: {target}")
                            else:
                                st.info("👈 Select a file to view code")
                else:
                    st.info("Your project structure will appear here.")

        if st.session_state.file_data:
            st.divider()
            files_to_zip = {f: st.session_state.file_data[f] for f in st.session_state.checked_files if f in st.session_state.file_data}
            count = len(files_to_zip)
            b1, b2, b3 = st.columns([1, 2, 1])
            with b2:
                btn_text = f"📥 Download ZIP ({count} Files)" if count > 0 else "⚠️ Select files to download"
                st.download_button(
                    label=btn_text,
                    data=create_in_memory_zip(files_to_zip) if count > 0 else b"empty",
                    file_name="AI_Project.zip",
                    mime="application/zip",
                    type="primary",
                    use_container_width=True,
                    disabled=(count == 0)
                )

    # --- 3. SETTINGS PAGE ---
    elif selected == "Settings":
        st.title("System Settings")
        
        with st.container(border=True):
            st.subheader("Detail Level")
            complexity_choice = st.selectbox(
                "Code Generation Depth",
                options=["Structure Only", "Simple Code", "Working Code"],
                index=["Structure Only", "Simple Code", "Working Code"].index(st.session_state.complexity)
            )
            if complexity_choice == "Structure Only": st.info("⚡ **Structure Only:** Folders & Empty Files.")
            elif complexity_choice == "Simple Code": st.warning("🚀 **Simple Code:** Classes & TODOs.")
            else: st.success("🧠 **Working Code:** Full Logic & Imports.")

        with st.container(border=True):
            st.subheader("AI Engine")
            model_mode = st.radio("Provider:", ["Presets", "Custom ID"], horizontal=True)
            
            if model_mode == "Presets":
                model_choice = st.selectbox("Select Model:", ["Qwen/Qwen2.5-Coder-32B-Instruct", "google/gemma-2-9b-it"])
                if "Qwen" in model_choice:
                    st.info("🤖 **Qwen 2.5 (32B):** Best for Python/Java logic. Slower.")
                else:
                    st.success("🏎️ **Gemma 2 (9B):** Best for speed and simple scripts.")
            else:
                model_choice = st.text_input("HuggingFace Model ID:", st.session_state.get("selected_model", "Qwen/Qwen2.5-Coder-32B-Instruct"))

        with st.container(border=True):
            st.subheader("API Access")
            user_token = st.text_input("Hugging Face Token (Optional)", type="password")

        if st.button("💾 Save Settings", type="primary"):
            if user_token: st.session_state.user_hf_token = user_token
            st.session_state.selected_model = model_choice
            st.session_state.complexity = complexity_choice
            st.toast("Settings Saved!", icon="💾")

    # --- 4. FAQ PAGE ---
    elif selected == "Help / FAQ":
        st.title("❓ Help & Support")
        
        st.markdown("### Common Questions")
        with st.expander("💻 What programming languages are supported?"):
            st.write("The AI Architect supports **all major languages**. You can ask for Python (Django/Flask), JavaScript (React/Node), Java, C++, or even Rust projects. Just specify the language in your description!")

        with st.expander("🔑 Is my data private?"):
            st.write("Yes. Your prompts are sent to the Hugging Face Inference API for processing and are not stored by this application.")

        with st.expander("💼 Can I use the generated code commercially?"):
            st.write("Yes! The code generated is boilerplate (standard code). You are free to use it, modify it, and sell projects built with it.")

        st.markdown("### Need more help?")
        st.info("If you encounter a 'Parsing Error', try reducing the project complexity or switching to 'Simple Code' mode in Settings.")

    st.markdown('<div class="footer">Made by <b>VishwarajKhatpe</b></div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()