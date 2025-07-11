#!/bin/bash

echo "🚀 Setting up Groq API for Medical AI Assistant"
echo "================================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

echo "✅ Python 3 is installed"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3 first."
    exit 1
fi

echo "✅ pip3 is installed"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

# Check for Groq API key
if [ -z "$GROQ_API_KEY" ]; then
    echo ""
    echo "⚠️  GROQ_API_KEY environment variable is not set"
    echo ""
    echo "To set up your Groq API key:"
    echo "1. Get your API key from: https://console.groq.com/"
    echo "2. Set the environment variable:"
    echo "   export GROQ_API_KEY='your-api-key-here'"
    echo ""
    echo "Or add it to your .bashrc/.zshrc file:"
    echo "   echo 'export GROQ_API_KEY=\"your-api-key-here\"' >> ~/.bashrc"
    echo "   source ~/.bashrc"
    echo ""
    echo "After setting the API key, run:"
    echo "   python3 test_groq_integration.py"
    echo ""
else
    echo "✅ GROQ_API_KEY is set"
    
    # Test the API key
    echo "🧪 Testing Groq API connection..."
    python3 test_groq_integration.py
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "🎉 Setup complete! Your Medical AI Assistant is ready to use."
        echo ""
        echo "To start the application:"
        echo "  streamlit run streamlit_realtime_medical_app.py"
        echo ""
        echo "To test Groq integration:"
        echo "  python3 test_groq_integration.py"
        echo ""
    else
        echo ""
        echo "❌ Setup failed. Please check your API key and try again."
        echo ""
    fi
fi 