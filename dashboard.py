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
    
    /* --- HERO HEADER --- */
    .hero-container {
        background: var(--primary-gradient);
        padding: 3rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(99, 102, 241, 0.2);
    }
    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .hero-subtitle {
        font-size: 1.2rem;
        opacity: 0.9;
        margin-top: 15px;
        font-weight: 300;
        max-width: 800px;
        margin-left: auto;
        margin-right: auto;
    }

    /* --- INFO CARDS --- */
    .info-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e5e7eb;
        height: 100%;
    }
    .info-title { font-weight: 700; font-size: 1.1rem; color: #111827; margin-bottom: 0.5rem; }
    .info-text { color: #6b7280; font-size: 0.95rem; line-height: 1.5; }

    /* --- BUTTONS --- */
    button[kind="primary"] {
        background: var(--primary-gradient) !important;
        border: none !important;
        color: white !important;
        font-weight: 600 !important;
        padding: 0.6rem 1.2rem;
        border-radius: 6px;
        transition: transform 0.2s ease !important;
    }
    button[kind="primary"]:hover {
        transform: translateY(-2px);
    }

    button[kind="secondary"] {
        border: 1px solid #d1d5db !important;
        color: #374151 !important;
        border-radius: 6px;
    }

    /* --- GENERAL CONTAINERS --- */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 12px;
        border: 1px solid #f3f4f6;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        background-color: white;
        padding: 1.5rem;
    }

    /* --- CODE PREVIEW --- */
    .element-container:has(.stCodeBlock) {
        max-height: 600px;
        overflow-y: auto;
        border-radius: 6px;
    }
    
    /* --- FOOTER --- */
    .footer {
        position: fixed; left: 0; bottom: 0; width: 100%;
        background-color: #ffffff; color: #9ca3af;
        text-align: center; padding: 12px;
        font-size: 0.8rem; border-top: 1px solid #f3f4f6;
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
    # Initialize Session State
    if "complexity" not in st.session_state: st.session_state.complexity = "Working Code"
    if "tree_key" not in st.session_state: st.session_state.tree_key = 0
    if "checked_files" not in st.session_state: st.session_state.checked_files = []
    if "nav_index" not in st.session_state: st.session_state.nav_index = 0 # Controls menu selection

    with st.sidebar:
        # CLEAN HEADER (No Dustbin Icon)
        st.markdown("## AI Architect")
        st.caption("Enterprise Boilerplate Engine")
        st.write("") # Spacer
        
        # NAVIGATION
        # We use manual_select via 'default_index' to allow buttons to redirect users
        selected = option_menu(
            menu_title=None,
            options=["Home", "Builder", "Settings"], 
            icons=['house', 'layers', 'sliders'], 
            default_index=st.session_state.nav_index,
            styles={
                "container": {"padding": "0!important", "background-color": "transparent"},
                "nav-link": {"border-radius": "8px", "margin": "5px 0", "font-size": "0.95rem"},
                "nav-link-selected": {"background-color": "#6366f1", "font-weight": "600"},
            }
        )
        
        st.divider()
        st.caption("v4.3 | Stable Build")

    # --- 1. HOME PAGE ---
    if selected == "Home":
        # Professional Hero Banner
        st.markdown("""
            <div class="hero-container">
                <div class="hero-title">AI Architect</div>
                <div class="hero-subtitle">
                    Accelerate your development process. Transform brief descriptions into 
                    production-ready project structures, complete with valid boilerplate code.
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Call to Action Button
        c_spacer, c_btn, c_spacer2 = st.columns([1, 2, 1])
        with c_btn:
            # When clicked, update index to 1 (Builder) and rerun
            if st.button("🚀 Start Building Project", type="primary", use_container_width=True):
                st.session_state.nav_index = 1
                st.rerun()

        st.write("")
        st.write("")

        # How It Works Section
        st.subheader("How It Works")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
                <div class="info-card">
                    <div class="info-title">1. Define</div>
                    <div class="info-text">
                        Select your preferred complexity level and describe your project requirements in plain English.
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
                <div class="info-card">
                    <div class="info-title">2. Generate</div>
                    <div class="info-text">
                        Our AI engine architects the folder structure and writes the initial boilerplate code for you.
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
                <div class="info-card">
                    <div class="info-title">3. Export</div>
                    <div class="info-text">
                        Review the generated code interactively, customize the selection, and download a ZIP package.
                    </div>
                </div>
            """, unsafe_allow_html=True)

    # --- 2. BUILDER PAGE ---
    elif selected == "Builder":
        st.title("Project Studio")
        
        if "file_data" not in st.session_state: st.session_state.file_data = {}

        col1, col2 = st.columns([1, 1.5], gap="large")

        with col1:
            st.subheader("Configuration")
            
            # Professional Status Indicators (No emojis in text)
            mode = st.session_state.complexity
            if mode == "Structure Only":
                st.info("**Current Mode:** Structure Only (Fast)")
            elif mode == "Simple Code":
                st.warning("**Current Mode:** Simple Code (Drafts)")
            else:
                st.success("**Current Mode:** Working Code (Detailed)")
            
            user_input = st.text_area("Project Description", placeholder="E.g. A Python script to scrape Amazon data using BeautifulSoup...", height=200)
            
            if st.button("Generate Blueprint", type="primary", use_container_width=True):
                if user_input:
                    # Status logic
                    status_label = "Processing..."
                    if mode == "Structure Only": status_label = "Architecting structure..."
                    elif mode == "Simple Code": status_label = "Drafting skeletons..."
                    else: status_label = "Writing full code (approx. 45s)..."

                    with st.status(status_label, expanded=True) as status:
                        st.write("Connecting to engine...")
                        raw = get_ai_response(user_input, complexity=mode)
                        
                        st.write("Parsing response...")
                        parsed = parse_ai_response(raw)
                        
                        if parsed:
                            st.session_state.file_data = parsed
                            st.session_state.checked_files = list(parsed.keys())
                            st.session_state.tree_key += 1 
                            status.update(label="Complete", state="complete", expanded=False)
                            st.toast("Blueprint created successfully", icon="✅")
                        else:
                            status.update(label="Failed", state="error")
                            st.error("Generation failed. Please try again.")
                            with st.expander("Debug Info"):
                                st.code(raw, language="json")

        with col2:
            st.subheader("Preview & Export")
            
            with st.container(border=True):
                if st.session_state.file_data:
                    tree_nodes = convert_to_tree(st.session_state.file_data)
                    all_vals = [n["value"] for n in tree_nodes]
                    
                    # Selection Logic
                    current_checked = st.session_state.checked_files
                    all_files = list(st.session_state.file_data.keys())
                    
                    h1, h2 = st.columns([2, 1])
                    with h1:
                        st.caption(f"{len(current_checked)} files selected")
                    with h2:
                        if not current_checked:
                            if st.button("Select All", use_container_width=True):
                                st.session_state.checked_files = all_files
                                st.session_state.tree_key += 1
                                st.rerun()
                        else:
                            if st.button("Clear Selection", use_container_width=True):
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
                                    st.info(f"{target} is empty")
                                else:
                                    lang = "python" if target.endswith(".py") else "text"
                                    st.markdown(f"**{target}**")
                                    st.code(content, language=lang, line_numbers=True)
                            else:
                                st.info(f"Folder: {target}")
                        else:
                            st.info("Select a file to view content")
                else:
                    st.info("Your project structure will appear here.")

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
                btn_text = f"Download ZIP ({count} Files)" if count > 0 else "Select files to download"
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
        
        # 1. Complexity Section
        with st.container(border=True):
            st.subheader("Complexity Engine")
            complexity_choice = st.selectbox(
                "Output Detail Level",
                options=["Structure Only", "Simple Code", "Working Code"],
                index=["Structure Only", "Simple Code", "Working Code"].index(st.session_state.complexity)
            )
            
            if complexity_choice == "Structure Only": 
                st.info("**Structure Only:** Generates empty files and folders. Best for when you want to write the code yourself.")
            elif complexity_choice == "Simple Code": 
                st.warning("**Simple Code:** Generates classes, functions, and TODO comments. Best for rapid prototyping.")
            else: 
                st.success("**Working Code:** Generates full boilerplate logic, imports, and error handling. Slower generation time.")

        # 2. Model Section (IMPROVED INFO)
        with st.container(border=True):
            st.subheader("Model Selection")
            model_mode = st.radio("Provider Source", ["Presets", "Custom ID"], horizontal=True)
            
            if model_mode == "Presets":
                model_choice = st.selectbox("Select Model Engine", ["Qwen/Qwen2.5-Coder-32B-Instruct", "google/gemma-2-9b-it"])
                
                # Dynamic Info Box for Models
                if "Qwen" in model_choice:
                    st.info("""
                    **Qwen 2.5 (32B):** The "Senior Architect." 
                    * **Strengths:** Excellent at complex logic, Python, and following strict formatting instructions.
                    * **Trade-off:** Slower response time due to large size.
                    """)
                else:
                    st.success("""
                    **Google Gemma 2 (9B):** The "Junior Developer."
                    * **Strengths:** Very fast response times. Great for simple scripts and basic structures.
                    * **Trade-off:** May struggle with very complex logical instructions compared to Qwen.
                    """)
            else:
                model_choice = st.text_input("HuggingFace Model ID", st.session_state.get("selected_model", "Qwen/Qwen2.5-Coder-32B-Instruct"))

        # 3. Credentials Section
        with st.container(border=True):
            st.subheader("API Access")
            user_token = st.text_input("Custom Hugging Face Token (Optional)", type="password", help="Overrides the default server token.")

        if st.button("Save Settings", type="primary"):
            if user_token: st.session_state.user_hf_token = user_token
            st.session_state.selected_model = model_choice
            st.session_state.complexity = complexity_choice
            st.toast("Settings saved successfully", icon="💾")

    st.markdown('<div class="footer">Created by <b>VishwarajKhatpe</b> | AI Architect v4.3</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()