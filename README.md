# 🏗️ AI Architect — Enterprise Project Generator (v5.2)

[![Version](https://img.shields.io/badge/current%20version-v5.2-blueviolet)](https://github.com/vishwarajkhatpe/AI-Project-Architect/releases/tag/v5.2)
[![Live App](https://img.shields.io/badge/Live%20App-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://ai-project-architect.streamlit.app)
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Inference-yellow?logo=huggingface&logoColor=black)](https://huggingface.co/)
![AI Powered](https://img.shields.io/badge/AI-Powered-purple)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Architecture](https://img.shields.io/badge/Architecture-Modular-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Stable-success)

**AI Architect** is an AI-powered project scaffolding platform that converts natural-language specifications into **production-ready project structures and boilerplate code**.

It is designed for developers, startups, and teams who want to move from idea to codebase **quickly, consistently, and with minimal setup overhead**.

The system leverages large language models such as **Qwen 2.5 (32B)** and **Google Gemma 2** to generate clean folder hierarchies, boilerplate files, and optional working code through an interactive visual workflow.

---

## 🚀 What’s New in v5.2

Version **5.2** introduces major architectural and usability improvements aimed at **enterprise-scale projects**.

- **Infinite Nested Folder Support**  
  A fully recursive parsing engine enables deeply nested paths  
  (e.g. `src/components/ui/buttons/primary.tsx`).

- **Scrollable Project Tree View**  
  Large project structures are rendered inside a fixed container with horizontal and vertical scrolling.

- **Improved AI Output Reliability**  
  Migrated to `huggingface_hub` with one-shot prompting to enforce strict JSON output and prevent partial or malformed generations.

- **UI & Workflow Enhancements**  
  - Expand / Collapse All controls  
  - Balanced 50/50 layout for navigation and preview  
  - Improved visual hierarchy for large projects

---

## ✨ Key Features

### 🚀 Rapid Project Scaffolding
Describe your application in plain English, for example:

> *A Flask REST API with SQLAlchemy, JWT authentication, and PostgreSQL*

AI Architect generates a complete project structure in seconds.

---

### 🧠 Intelligent Code Generation Modes

Choose the level of detail that fits your workflow:

- **Structure Only** — Folder and file layout for planning
- **Simple Code** — Class skeletons, function signatures, TODOs
- **Working Code** — Fully wired logic, imports, error handling, and dependencies

---

### 🎨 Interactive Builder Studio

- Visual file-tree explorer
- Syntax-highlighted code preview (Python, JSON, etc.)
- Select or exclude specific files before export

---

### 📦 One-Click Export

Download the generated project as a clean `.zip` archive, ready to run or commit.

---

### 🌈 Modern Developer UI

- Fully responsive layout
- Dark, tech-inspired gradient theme
- Smooth transitions and animations

---

## 🛠️ Tech Stack

**Frontend**
- Streamlit

**AI & Inference**
- Hugging Face Inference API

**Models**
- `Qwen/Qwen2.5-Coder-32B-Instruct` — high-precision reasoning
- `google/gemma-2-9b-it` — fast generation

**Utilities**
- `streamlit-tree-select`
- `streamlit-option-menu`

---

## 💻 Local Installation

Run AI Architect locally for full control or development.

### 1. **Clone the Repository**
```bash
git clone https://github.com/vishwarajkhatpe/AI-Project-Architect.git
cd AI-Project-Architect
```

### 2. **Install dependencies**
```bash
    pip install -r requirements.txt
```

### 3. **Set up API Key (Optional)** You can either enter your key in the app's Settings menu or create a .env file for auto-loading:
```bash
    # .env file
    HF_TOKEN=hf_your_huggingface_token_here
```
### 4. **Run the App**
```bash
    streamlit run dashboard.py
```
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

2. Create your Feature Branch
```bash
git checkout -b feature/AmazingFeature
```

3. Commit your Changes
```bash
   git commit -m 'Add some AmazingFeature')
```
4. Push to your Branch

5. Open a Pull Request

---

Built with ❤️ by **VishwarajKhatpe**
