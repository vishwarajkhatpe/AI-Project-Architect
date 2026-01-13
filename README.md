# 🏗️ AI Architect (v5.1 Enterprise)

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Stable-success)

**AI Architect** is an intelligent boilerplate generator that turns natural language descriptions into production-ready project structures. Powered by **Qwen 2.5 (32B)** and **Google Gemma 2**, it generates valid file trees, writes boilerplate code, and allows for interactive customization before export.

---

## ✨ Features

- **🚀 Instant Prototyping:** Describe your app (e.g., *"A Flask API with SQLAlchemy and JWT auth"*) and get a full folder structure in seconds.
- **🧠 Intelligent Code Generation:** - **Structure Only:** Fast folder layout for planning.
  - **Simple Code:** Class skeletons, function definitions, and TODOs.
  - **Working Code:** Full logic, imports, error handling, and requirements.
- **🎨 Interactive Studio:** - Visual Tree View to explore generated files.
  - Syntax highlighting for code preview (Python, JSON, etc.).
  - Select/Deselect specific files before downloading.
- **📦 One-Click Export:** Download your entire project as a clean `.zip` package, ready to run.
- **🌈 Modern UI:** A fully responsive, professional interface with "Dark Tech" gradient styling and smooth animations.

---

## 🛠️ Tech Stack

- **Frontend:** [Streamlit](https://streamlit.io/)
- **AI Engine:** [Hugging Face Inference API](https://huggingface.co/inference-api)
- **Models:** - `Qwen/Qwen2.5-Coder-32B-Instruct` (High Precision)
  - `google/gemma-2-9b-it` (High Speed)
- **Utilities:** `streamlit-tree-select`, `streamlit-option-menu`

---

## 💻 Local Installation

If you prefer to run this locally instead of on the cloud:

1. **Clone the repository**
   ```bash
   git clone [https://github.com vishwarajkhatpe/AI-Project-Architect.git](https://github.com/vishwarajkhatpe/AI-Project-Architect.git)

   cd AI-Project-Architect

2. **Install dependencies**
    '''bash
    pip install -r requirements.txt

3. **Set up API Key (Optional)** You can either enter your key in the app's Settings menu or create a .env file for auto-loading:
    '''bash
    # .env file
    HF_TOKEN=hf_your_huggingface_token_here

4. **Run the App**
    '''bash
    streamlit run dashboard.py

---


## **📂 Project Structure**

```text
AI-Architect/
├── app/
│   ├── __init__.py      # Required: Makes 'app' a package
│   ├── api_handler.py   # AI Logic
│   └── utils.py         # Response Parser
├── core/
│   ├── __init__.py      # Required: Makes 'core' a package
│   └── creator.py       # ZIP Creator
├── .streamlit/
│   └── config.toml      # Theme Settings
├── .gitignore           # Ignored files
├── dashboard.py         # Main App
├── requirements.txt     # Dependencies
└── README.md            # Docs
```

---


**❓ FAQ**</br>

Q: Is the generated code production-ready?</br> 
A: The "Working Code" mode produces high-quality boilerplate. However, you should always review AI-generated code for security and specific business logic requirements before deploying to production.

Q: Why does generation take ~45 seconds? </br>A: We use a large 32-Billion parameter model (Qwen 2.5) to ensure logical consistency across multiple files. This deep reasoning takes a moment, but the result is significantly better than smaller, faster models.

Q: Is my data private? </br>
A: Yes. Your prompts are processed via the Hugging Face API and are not stored by this application. If you use a custom API token, it is only stored in your browser's temporary session.

---

**🤝 Contributing**:

Contributions are welcome! Please fork the repository and submit a Pull Request.

1. Fork the Project

2. Create your Feature Branch (git checkout -b feature/AmazingFeature)

3. Commit your Changes (git commit -m 'Add some AmazingFeature')

4. Push to the Branch (git push origin        feature/AmazingFeature)

5. Open a Pull Request

---

Built with ❤️ by **VishwarajKhatpe**