import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_tree_select import tree_select
from app.api_handler import get_ai_response
from app.utils import parse_ai_response
from core.creator import create_in_memory_zip

# 1. Page Config
st.set_page_config(
    page_title="AI Architect Pro V2",
    page_icon="🚀",
    layout="wide"
)

# 2. Styling
st.markdown("""
    <style>
    .footer {
        position: fixed; left: 0; bottom: 0; width: 100%;
        background-color: #f8f9fa; color: #6c757d;
        text-align: center; padding: 8px;
        font-size: 0.8rem; border-top: 1px solid #dee2e6;
    }
    /* Make the code block look cleaner */
    .stCodeBlock { border: 1px solid #ececec; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

def convert_to_tree(file_data):
    """Converts the Dictionary keys into a tree structure for the UI."""
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
        st.caption("Version 2.0: Boilerplate Engine")

    # --- GENERATOR PAGE ---
    if selected == "Generator":
        st.title("V2.0: Project Boilerplate Generator")
        
        # Initialize session state
        if "file_data" not in st.session_state:
            st.session_state.file_data = {}

        col1, col2 = st.columns([1, 1.5], gap="large") # Added GAP for better spacing

        with col1:
            st.subheader("📝 Project Idea")
            st.write("Describe your app, and I'll write the starter code.")
            user_input = st.text_area(
                "Description:",
                placeholder="Example: A Python script that uses Selenium to log into a website and download invoices.",
                height=200,
                label_visibility="collapsed"
            )
            
            st.write("") # Spacer
            if st.button("✨ Generate Full Boilerplate", type="primary", use_container_width=True):
                if user_input:
                    with st.spinner("🤖 AI is writing your starter code..."):
                        raw_response = get_ai_response(user_input)
                        parsed_dict = parse_ai_response(raw_response)
                        
                        if parsed_dict:
                            st.session_state.file_data = parsed_dict
                            st.toast("✅ Code Generated Successfully!", icon="🚀")
                        else:
                            st.error("AI failed to generate a valid JSON structure. Try again.")

        with col2:
            st.subheader("📂 Code Preview")
            
            # Container for the results adds a nice border visual
            with st.container(border=True):
                if st.session_state.file_data:
                    tree_nodes = convert_to_tree(st.session_state.file_data)
                    all_node_values = [n["value"] for n in tree_nodes]

                    # Inner columns for Tree vs Code
                    c1, c2 = st.columns([1, 2])
                    
                    with c1:
                        st.caption("File Tree")
                        selected_tree = tree_select(
                            tree_nodes, 
                            no_cascade=True, 
                            expanded=all_node_values
                        )
                    
                    with c2:
                        st.caption("Content Preview")
                        if selected_tree['checked']:
                            target_file = selected_tree['checked'][0]
                            if target_file in st.session_state.file_data:
                                lang = "python" if target_file.endswith(".py") else "text"
                                st.code(st.session_state.file_data[target_file], language=lang, line_numbers=True)
                            else:
                                st.info("Select a file, not a folder.")
                        else:
                            st.info("👈 Select a file to view code.")

                else:
                    st.info("Your generated project structure and code will appear here.")
                    # Placeholder image to make empty state look better
                    st.markdown("Waiting for input...", help="Enter a prompt on the left")

        # --- DOWNLOAD SECTION (CENTERED) ---
        if st.session_state.file_data:
            st.divider()
            
            # THE CENTERING TRICK: 3 Columns
            # We put the button in the middle column (b2)
            b1, b2, b3 = st.columns([1, 2, 1])
            
            with b2:
                zip_bytes = create_in_memory_zip(st.session_state.file_data)
                st.download_button(
                    label="📥 Download Complete Project ZIP",
                    data=zip_bytes,
                    file_name="architect_project.zip",
                    mime="application/zip",
                    type="primary",
                    use_container_width=True
                )

    # --- FOOTER ---
    st.markdown('<div class="footer">Created by <b>YourName</b> | Project Architect V2.0</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()