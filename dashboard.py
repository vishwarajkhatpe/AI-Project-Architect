import streamlit as st
import time
from streamlit_option_menu import option_menu
from streamlit_tree_select import tree_select
from app.api_handler import get_ai_response
from app.utils import parse_ai_response
from core.creator import create_in_memory_zip

# 1. Page Config
st.set_page_config(page_title="AI Architect", page_icon="🌈", layout="wide")

# 2. VIBRANT CSS STYLING
st.markdown("""
    <style>
    /* --- ANIMATIONS --- */
    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    
    /* --- HERO HEADER --- */
    .hero-container {
        background: linear-gradient(120deg, #84fab0 0%, #8fd3f4 100%);
        padding: 3rem;
        border-radius: 20px;
        color: #2d3436;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        animation: fadeIn 1s ease-in;
    }
    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        margin: 0;
        color: #2d3436;
        text-shadow: 2px 2px 0px white;
    }
    .hero-subtitle {
        font-size: 1.3rem;
        color: #4b6584;
        margin-top: 15px;
        font-weight: 500;
    }

    /* --- FEATURE CARDS --- */
    .feature-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        border: 2px solid #f1f2f6;
        text-align: center;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        height: 100%;
    }
    .feature-card:hover {
        transform: translateY(-10px);
        border-color: #84fab0;
        box-shadow: 0 10px 20px rgba(132, 250, 176, 0.3);
    }
    .feature-icon { font-size: 3rem; margin-bottom: 10px; }
    .feature-title { font-weight: 700; font-size: 1.2rem; color: #2d3436; }
    .feature-desc { color: #636e72; font-size: 0.95rem; }

    /* --- BUTTONS --- */
    button[kind="primary"] {
        background: linear-gradient(to right, #667eea 0%, #764ba2 100%) !important;
        border: none !important;
        color: white !important;
        font-weight: 700 !important;
        padding: 0.7rem 1.5rem;
        border-radius: 10px;
        transition: all 0.2s !important;
    }
    button[kind="primary"]:hover {
        transform: scale(1.05);
        box-shadow: 0 5px 15px rgba(118, 75, 162, 0.4);
    }
    
    /* --- STATUS BADGES --- */
    .stAlert { border-radius: 10px; }
    
    /* --- FOOTER --- */
    .footer {
        position: fixed; left: 0; bottom: 0; width: 100%;
        background: white; color: #b2bec3;
        text-align: center; padding: 10px;
        font-size: 0.8rem; border-top: 1px solid #dfe6e9;
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
    if "nav_index" not in st.session_state: st.session_state.nav_index = 0

    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/8695/8695995.png", width=60)
        st.markdown("### 🏗️ AI Architect")
        
        # NAVIGATION with FAQ added
        selected = option_menu(
            menu_title=None,
            options=["Home", "Builder", "Settings", "Help / FAQ"], 
            icons=['house', 'hammer', 'sliders', 'question-circle'], 
            default_index=st.session_state.nav_index,
            styles={
                "nav-link": {"border-radius": "10px", "margin": "5px 0"},
                "nav-link-selected": {"background-color": "#764ba2"},
            }
        )
        
        st.divider()
        st.caption("Version 5.0 | Colorful Pro 🌈")

    # --- 1. HOME PAGE ---
    if selected == "Home":
        # Colorful Hero
        st.markdown("""
            <div class="hero-container">
                <div class="hero-title">✨ AI Architect</div>
                <div class="hero-subtitle">
                    Don't just code. <b>Architect.</b><br>
                    Turn one sentence into a full project folder in seconds! 🚀
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Big "Start" Button
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            if st.button("🚀 Launch Builder Now", type="primary", use_container_width=True):
                st.session_state.nav_index = 1
                st.rerun()
        
        st.write("")
        st.subheader("🔥 Awesome Features")
        
        # Feature Cards
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
                <div class="feature-card">
                    <div class="feature-icon">⚡</div>
                    <div class="feature-title">Lightning Fast</div>
                    <div class="feature-desc">Get a complete folder structure in under 5 seconds using our optimized AI models.</div>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
                <div class="feature-card">
                    <div class="feature-icon">🧠</div>
                    <div class="feature-title">Smart Code</div>
                    <div class="feature-desc">We don't just make files; we write valid, running Python code inside them!</div>
                </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown("""
                <div class="feature-card">
                    <div class="feature-icon">🎨</div>
                    <div class="feature-title">Total Control</div>
                    <div class="feature-desc">Preview every file, uncheck what you don't need, and download a clean ZIP.</div>
                </div>
            """, unsafe_allow_html=True)

    # --- 2. BUILDER PAGE ---
    elif selected == "Builder":
        st.title("🛠️ Project Builder")
        
        if "file_data" not in st.session_state: st.session_state.file_data = {}

        col1, col2 = st.columns([1, 1.5], gap="large")

        with col1:
            st.subheader("1. 📝 Describe It")
            
            # Fun Mode Indicators
            mode = st.session_state.complexity
            if mode == "Structure Only":
                st.info("⚡ **Mode:** Structure Only (Super Fast!)")
            elif mode == "Simple Code":
                st.warning("🚀 **Mode:** Simple Code (Drafts & Todos)")
            else:
                st.success("🧠 **Mode:** Working Code (The Real Deal)")
            
            user_input = st.text_area("What are we building today?", placeholder="E.g. A Flappy Bird game using Pygame...", height=180)
            
            if st.button("✨ Magic Generate", type="primary", use_container_width=True):
                if user_input:
                    # Fun status messages
                    status_label = "🤔 Thinking..."
                    if mode == "Structure Only": status_label = "⚡ Sketching folder tree..."
                    elif mode == "Simple Code": status_label = "🚀 Drafting blueprints..."
                    else: status_label = "🧠 writing code (Grab a coffee ☕, ~45s)..."

                    with st.status(status_label, expanded=True) as status:
                        st.write("🔌 Connecting to Brain...")
                        raw = get_ai_response(user_input, complexity=mode)
                        
                        st.write("📂 Organizing files...")
                        parsed = parse_ai_response(raw)
                        
                        if parsed:
                            st.session_state.file_data = parsed
                            st.session_state.checked_files = list(parsed.keys())
                            st.session_state.tree_key += 1 
                            status.update(label="🎉 Done! Project Ready.", state="complete", expanded=False)
                            st.toast("Woohoo! Project created!", icon="🎉")
                        else:
                            status.update(label="💥 Oops, failed.", state="error")
                            st.error("AI tripped over its shoelaces. Try again?")
                            with st.expander("🐛 Debug Info"):
                                st.code(raw, language="json")

        with col2:
            st.subheader("2. 👀 Preview & Pick")
            
            with st.container(border=True):
                if st.session_state.file_data:
                    tree_nodes = convert_to_tree(st.session_state.file_data)
                    all_vals = [n["value"] for n in tree_nodes]
                    
                    # Selection Buttons
                    current_checked = st.session_state.checked_files
                    all_files = list(st.session_state.file_data.keys())
                    
                    c_btn1, c_btn2 = st.columns(2)
                    with c_btn1:
                        if st.button("✅ Select All", use_container_width=True):
                            st.session_state.checked_files = all_files
                            st.session_state.tree_key += 1
                            st.rerun()
                    with c_btn2:
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
                                    st.info(f"📄 `{target}` is empty")
                                else:
                                    lang = "python" if target.endswith(".py") else "text"
                                    st.markdown(f"**📄 {target}**")
                                    st.code(content, language=lang, line_numbers=True)
                            else:
                                st.info(f"📂 **Folder:** {target}")
                        else:
                            st.info("👈 Click a file to see the magic!")
                else:
                    st.info("Your masterpiece will appear here! 🎨")

        # Download Section
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
                btn_text = f"📥 Download ZIP ({count} Files)" if count > 0 else "⚠️ Select files first!"
                st.download_button(
                    label=btn_text,
                    data=create_in_memory_zip(files_to_zip) if count > 0 else b"empty",
                    file_name="My_AI_Project.zip",
                    mime="application/zip",
                    type="primary",
                    use_container_width=True,
                    disabled=(count == 0)
                )

    # --- 3. SETTINGS PAGE ---
    elif selected == "Settings":
        st.title("⚙️ Settings & Tweaks")
        
        with st.container(border=True):
            st.subheader("🎚️ Complexity Level")
            st.caption("How much work should the AI do?")
            complexity_choice = st.selectbox(
                "Detail Level",
                options=["Structure Only", "Simple Code", "Working Code"],
                index=["Structure Only", "Simple Code", "Working Code"].index(st.session_state.complexity)
            )
            
            if complexity_choice == "Structure Only": 
                st.info("⚡ **Structure Only:** Just folders and empty files. Perfect if you want to code from scratch!")
            elif complexity_choice == "Simple Code": 
                st.warning("🚀 **Simple Code:** Adds 'TODO' comments and class definitions. Good for planning.")
            else: 
                st.success("🧠 **Working Code:** Writes real, runnable code. Takes longer, but worth it!")

        with st.container(border=True):
            st.subheader("🧠 AI Brain")
            model_mode = st.radio("Choose your Engine:", ["Presets", "Custom ID"], horizontal=True)
            
            if model_mode == "Presets":
                model_choice = st.selectbox("Select Model:", ["Qwen/Qwen2.5-Coder-32B-Instruct", "google/gemma-2-9b-it"])
                
                # HELPFUL INFO BOXES
                if "Qwen" in model_choice:
                    st.info("🤖 **Qwen 2.5 (32B):** The Genius. Slower, but writes amazing Python code.")
                else:
                    st.success("🏎️ **Gemma 2 (9B):** The Speedster. Super fast, great for simple projects.")
            else:
                model_choice = st.text_input("Paste HuggingFace Model ID:", st.session_state.get("selected_model", "Qwen/Qwen2.5-Coder-32B-Instruct"))

        with st.container(border=True):
            st.subheader("🔑 Secret Key")
            user_token = st.text_input("Hugging Face Token (Optional)", type="password", help="Use your own key for unlimited power!")

        if st.button("💾 Save My Settings", type="primary"):
            if user_token: st.session_state.user_hf_token = user_token
            st.session_state.selected_model = model_choice
            st.session_state.complexity = complexity_choice
            st.toast("Settings Saved! Ready to build.", icon="💾")

    # --- 4. FAQ PAGE (NEW!) ---
    elif selected == "Help / FAQ":
        st.title("❓ Help & FAQ")
        st.markdown("Got questions? We've got answers!")
        
        with st.expander("🤔 How do I generate a project?"):
            st.write("1. Go to the **Builder** tab.")
            st.write("2. Type what you want (e.g., 'A To-Do List app').")
            st.write("3. Click **Magic Generate**!")
        
        with st.expander("⏳ Why is 'Working Code' slow?"):
            st.write("Writing code is hard work! The AI is writing hundreds of lines of logic for you. Give it about 45-60 seconds to finish perfectly.")
            
        with st.expander("🔑 Do I need an API Key?"):
            st.write("Nope! The app comes with a free built-in key. However, if you have your own Hugging Face token, adding it in **Settings** might make it faster.")

        with st.expander("🐛 I got a 'Parsing Error'. What do I do?"):
            st.write("This happens if the AI writes too much and gets cut off. Try switching to **Simple Code** mode or simplify your project description slightly.")

    st.markdown('<div class="footer">Made with ❤️ by <b>VishwarajKhatpe</b></div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()