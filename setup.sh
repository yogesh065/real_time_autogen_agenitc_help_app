#!/bin/bash

# Install system dependencies for audio processing
if [[ "$OSTYPE" == "darwin"* ]]; then
    # For macOS
    brew install portaudio || true
else
    # For Linux
    sudo apt-get update
    sudo apt-get install -y portaudio19-dev python3-pyaudio espeak espeak-data libespeak1 libespeak-dev
fi

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install --upgrade pip
pip install -r requirements.txt

# Set environment variables
if [ -z "$OPENAI_API_KEY" ]; then
    echo "Please set your OpenAI API key as an environment variable."
    echo "export OPENAI_API_KEY=your-openai-api-key-here"
    exit 1
fi

# Run the application
streamlit run streamlit_realtime_medical_app.py 