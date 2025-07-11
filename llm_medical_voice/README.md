# Real-time AutoGen Agentic Medical Help App

A real-time, multi-agent, voice-enabled medical product support system built with Microsoft AutoGen, Streamlit, and FastAPI.

## 🚀 Features
- **Real-time Medical Product Support**: Search, dosage, safety, and insurance info for medications
- **Multi-Agent Orchestration**: Specialized agents for product search, dosage, safety, and insurance
- **Text-based and (optionally) Voice-based Interaction**
- **Comprehensive Medical Product Database**
- **Extensible, Modular Python Codebase**

## 🏗️ Project Structure
```
medical_database.py                # Medical product DB and analytics
autogen_realtime_medical.py        # Main AutoGen agent system
streamlit_realtime_medical_app.py  # Streamlit UI for interaction
requirements.txt                   # Python dependencies
setup.sh                           # Setup script for dependencies
.gitignore                         # Ignores venv, .env, etc.
README.md                          # This file
```

## ⚡ Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/yogesh065/real_time_autogen_agenitc_help_app.git
cd real_time_autogen_agenitc_help_app
```

### 2. Install Python 3.10+ (if needed)
- **macOS**: `brew install python@3.11`
- **Ubuntu**: `sudo apt-get install python3.11 python3.11-venv`

### 3. Run the Setup Script
```bash
bash setup.sh
```
This will:
- Create a virtual environment
- Install all Python dependencies
- Prompt you to set your OpenAI API key
- Launch the Streamlit app

### 4. Set Your OpenAI API Key
You can set it as an environment variable:
```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```
Or create a `.streamlit/secrets.toml` file:
```toml
OPENAI_API_KEY = "your-openai-api-key-here"
```

### 5. Run the App Manually (if needed)
```bash
source venv/bin/activate
streamlit run streamlit_realtime_medical_app.py
```

## 🖥️ Usage
- Use the Streamlit web UI to ask about medical products, dosages, safety, and more.
- Sample queries are provided in the sidebar.
- All responses emphasize safety and professional medical guidance.

## 🛠️ Troubleshooting
- **Python version error**: Ensure you are using Python 3.10 or higher.
- **Missing OpenAI API key**: Set the `OPENAI_API_KEY` environment variable or add it to `.streamlit/secrets.toml`.
- **Virtual environment issues**: Delete and recreate the `venv` folder.
- **Dependency errors**: Run `pip install -r requirements.txt` inside the virtual environment.

## 📝 Customization
- Add more sample data in `medical_database.py`.
- Extend agent logic in `autogen_realtime_medical.py`.
- Customize the UI in `streamlit_realtime_medical_app.py`.

## ⚠️ Disclaimer
This app provides general medical information only. **Always consult a healthcare professional for medical advice, diagnosis, or treatment.**

---

**Maintained by [yogesh065](https://github.com/yogesh065)** 