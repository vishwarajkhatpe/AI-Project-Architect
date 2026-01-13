import streamlit as st
import time
from streamlit_option_menu import option_menu
from streamlit_tree_select import tree_select
from app.api_handler import get_ai_response
from app.utils import parse_ai_response
from core.creator import create_in_memory_zip

# 1. Page Config
st.set_page_config(page_title="AI Architect", page_icon="🏗️", layout="wide")

# 2. PRO CSS STYLING
st.markdown("""
    <style>
    /* --- GLOBAL THEME --- */
    :root {
        --primary-gradient: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        --hover-gradient: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
    }
    
    /* --- HERO HEADER (Home Page) --- */
    .hero-container {
        background: var(--primary-gradient);
        padding: 3rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(99, 102, 241, 0.3);
    }
    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -1px;
    }
    .hero-subtitle {
        font-size: 1.3rem;
        opacity: 0.9;
        margin-top: 15px;
        font-weight: 300;
    }

    /* --- FEATURE CARDS (Home Page) --- */
    .feature-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid #f3f4f6;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        text-align: center;
        height: 100%;
    }
    .feature-icon { font-size: 2rem; margin-bottom: 10px; }
    .feature-title { font-weight: 700; font-size: 1.1rem; color: #1f2937; }
    .feature-desc { color: #6b7280; font-size: 0.9rem; margin-top: 5px; }

    /* --- PRIMARY BUTTONS --- */
    button[kind="primary"] {
        background: var(--primary-gradient) !important;
        border: none !important;
        color: white !important;
        font-weight: 700 !important;
        padding: 0.6rem 1.2rem;
        transition: all 0.3s ease !important;
    }
    button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 15px rgba(99, 102, 241, 0.4);
    }

    /* --- SECONDARY BUTTONS --- */
    button[kind="secondary"] {
        border: 1px solid #e5e7eb !important;
        color: #374151 !important;
    }

    /* --- GENERAL CONTAINERS --- */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 16px;
        border: 1px solid #f3f4f6;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        background-color: white;
        padding: 1.5rem;
    }

    /* --- CODE PREVIEW --- */
    .element-container:has(.stCodeBlock) {
        max-height: 600px;
        overflow-y: auto;
        border-radius: 8px;
    }
    
    /* --- FOOTER --- */
    .footer {
        position: fixed; left: 0; bottom: 0; width: 100%;
        background-color: #ffffff; color: #6b7280;
        text-align: center; padding: 12px;
        font-size: 0.85rem; border-top: 1px solid #f3f4f6;
        z-index: 100;
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
    if "complexity" not in st.session_state: st.session_state.complexity = "Working Code"
    if "tree_key" not in st.session_state: st.session_state.tree_key = 0
    if "checked_files" not in st.session_state: st.session_state.checked_files = []
    
    with st.sidebar:
        # VISUAL SIDEBAR HEADER
        st.image("https://cdn-icons-png.flaticon.com/512/8695/8695995.png", width=60)
        st.markdown("### AI Architect")
        
        # NAVIGATION MENU
        selected = option_menu(
            menu_title=None,
            options=["Home", "Builder", "Settings"], 
            icons=['house', 'layers', 'sliders'], 
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "transparent"},
                "nav-link": {"border-radius": "10px", "margin": "5px 0", "font-size": "1rem"},
                "nav-link-selected": {"background-color": "#6366f1", "font-weight": "600"},
            }
        )
        
        st.divider()
        st.caption("v4.2 | Enterprise")

    # --- 1. HOME PAGE ---
    if selected == "Home":
        # Hero Banner
        st.markdown("""
            <div class="hero-container">
                <div class="hero-title">AI Architect</div>
                <div class="hero-subtitle">The Intelligent Boilerplate Engine for Modern Developers.</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Feature Cards Row
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("""
                <div class="feature-card">
                    <div class="feature-icon">⚡</div>
                    <div class="feature-title">Instant Structure</div>
                    <div class="feature-desc">Generate production-ready folder trees in seconds.</div>
                </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown("""
                <div class="feature-card">
                    <div class="feature-icon">🧠</div>
                    <div class="feature-title">Smart Code</div>
                    <div class="feature-desc">Get valid boilerplate code for Python, React, and more.</div>
                </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown("""
                <div class="feature-card">
                    <div class="feature-icon">🎨</div>
                    <div class="feature-title">Fully Custom</div>
                    <div class="feature-desc">Preview, select, and customize before you download.</div>
                </div>
            """, unsafe_allow_html=True)
        
        st.write("")
        st.write("")
        st.info("👈 **Select 'Builder' in the sidebar to start a new project.**")

    # --- 2. BUILDER PAGE ---
    elif selected == "Builder":
        st.title("🛠️ Project Studio")
        
        if "file_data" not in st.session_state: st.session_state.file_data = {}

        col1, col2 = st.columns([1, 1.5], gap="large")

        with col1:
            st.subheader("Blueprint Configuration")
            
            # Mode Indicator
            mode = st.session_state.complexity
            if mode == "Structure Only":
                st.info("⚡ **Mode:** Structure Only (Fastest)")
            elif mode == "Simple Code":
                st.warning("🚀 **Mode:** Simple Code (Prototypes)")
            else:
                st.success("🧠 **Mode:** Working Code (Deep Logic)")
            
            user_input = st.text_area("Describe your project idea:", placeholder="E.g. A Python script to scrape Amazon data...", height=180)
            
            if st.button("✨ Initialize Project", type="primary", use_container_width=True):
                if user_input:
                    status_label = "Initializing..."
                    if mode == "Structure Only": status_label = "⚡ Architecting folder structure..."
                    elif mode == "Simple Code": status_label = "🚀 Drafting code skeletons..."
                    else: status_label = "🧠 Writing full boilerplate code (Please wait ~45s)..."

                    with st.status(status_label, expanded=True) as status:
                        st.write("🔌 Connecting to Neural Engine...")
                        raw = get_ai_response(user_input, complexity=mode)
                        
                        st.write("📂 Parsing blueprint...")
                        parsed = parse_ai_response(raw)
                        
                        if parsed:
                            st.session_state.file_data = parsed
                            st.session_state.checked_files = list(parsed.keys())
                            st.session_state.tree_key += 1 
                            status.update(label="✅ Blueprint Created!", state="complete", expanded=False)
                            st.toast("✅ Success! Scaffold ready.", icon="🎉")
                        else:
                            status.update(label="❌ Generation Failed", state="error")
                            st.error("The AI generated code, but the JSON format broke.")
                            with st.expander("👀 View Raw Debug Info"):
                                st.code(raw, language="json")

        with col2:
            st.subheader("Interactive Preview")
            
            with st.container(border=True):
                if st.session_state.file_data:
                    tree_nodes = convert_to_tree(st.session_state.file_data)
                    all_vals = [n["value"] for n in tree_nodes]
                    
                    # Selection Logic
                    current_checked = st.session_state.checked_files
                    all_files = list(st.session_state.file_data.keys())
                    
                    h1, h2 = st.columns([2, 1])
                    with h1:
                        st.caption(f"**{len(current_checked)}** files selected")
                    with h2:
                        if not current_checked:
                            if st.button("✅ Select All", use_container_width=True):
                                st.session_state.checked_files = all_files
                                st.session_state.tree_key += 1
                                st.rerun()
                        else:
                            if st.button("🧹 Clear All", use_container_width=True):
                                st.session_state.checked_files = []
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
                                    st.info(f"📄 `{target}` is empty", icon="ℹ️")
                                else:
                                    lang = "python" if target.endswith(".py") else "text"
                                    st.markdown(f"**📄 {target}**")
                                    st.code(content, language=lang, line_numbers=True)
                            else:
                                st.info(f"📂 **Folder:** {target}")
                        else:
                            st.info("👈 Select a file")
                else:
                    st.info("Waiting for input... Your scaffold will appear here.")

        # Download Bar
        if st.session_state.file_data:
            st.divider()
            files_to_zip = {}
            checked_list = st.session_state.checked_files
            
            if checked_list:
                for f in checked_list:
                    if f in st.session_state.file_data:
                        files_to_zip[f] = st.session_state.file_data[f]
            
            count = len(files_to_zip)
            b1, b2, b3 = st.columns([1, 2, 1])
            with b2:
                btn_text = f"📥 Download Package ({count} Files)" if count > 0 else "⚠️ Select files to download"
                st.download_button(
                    label=btn_text,
                    data=create_in_memory_zip(files_to_zip) if count > 0 else b"empty",
                    file_name="AI_Architect_Project.zip",
                    mime="application/zip",
                    type="primary",
                    use_container_width=True,
                    disabled=(count == 0)
                )

    # --- 3. SETTINGS PAGE ---
    elif selected == "Settings":
        st.title("⚙️ System Settings")
        
        with st.container(border=True):
            st.subheader("🎚️ Complexity Engine")
            complexity_choice = st.selectbox(
                "Code Generation Depth",
                options=["Structure Only", "Simple Code", "Working Code"],
                index=["Structure Only", "Simple Code", "Working Code"].index(st.session_state.complexity)
            )
            if complexity_choice == "Structure Only": st.info("⚡ **Fastest:** Generates empty files.")
            elif complexity_choice == "Simple Code": st.warning("🚀 **Balanced:** Generates skeletons.")
            else: st.success("🧠 **Deep:** Generates full logic.")

        with st.container(border=True):
            st.subheader("🧠 Model Interface")
            model_mode = st.radio("Provider:", ["Presets", "Custom ID"], horizontal=True)
            if model_mode == "Presets":
                model_choice = st.selectbox("Select Model:", ["Qwen/Qwen2.5-Coder-32B-Instruct", "google/gemma-2-9b-it"])
            else:
                model_choice = st.text_input("HuggingFace Model ID:", st.session_state.get("selected_model", "Qwen/Qwen2.5-Coder-32B-Instruct"))

        with st.container(border=True):
            st.subheader("🔑 Credentials")
            user_token = st.text_input("Hugging Face API Token (Optional)", type="password")

        if st.button("💾 Save Configuration", type="primary"):
            if user_token: st.session_state.user_hf_token = user_token
            st.session_state.selected_model = model_choice
            st.session_state.complexity = complexity_choice
            st.toast("✅ System Config Updated!", icon="💾")

    st.markdown('<div class="footer">Created by <b>VishwarajKhatpe</b> | AI Architect v4.2</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()