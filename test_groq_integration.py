#!/usr/bin/env python3
"""
Test script for Groq API integration with Medical Agent System
"""

import requests
import json
import os
from autogen_realtime_medical import MedicalRealtimeAgentSystem

def test_groq_connection():
    """Test if Groq API key is valid"""
    groq_api_key = os.getenv('GROQ_API_KEY')
    if not groq_api_key:
        print("❌ GROQ_API_KEY environment variable not set")
        print("Please set your Groq API key: export GROQ_API_KEY='your-api-key'")
        return False
    
    try:
        # Test Groq API with a simple request
        headers = {
            "Authorization": f"Bearer {groq_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "llama3.1-8b-8192",
            "messages": [{"role": "user", "content": "Hello, test message"}],
            "max_tokens": 50
        }
        
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Groq API connection successful!")
            return True
        else:
            print(f"❌ Groq API error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error connecting to Groq API: {str(e)}")
        return False

def test_medical_system():
    """Test the medical agent system with Groq"""
    try:
        print("\n🔧 Initializing Medical Agent System with Groq...")
        groq_api_key = os.getenv('GROQ_API_KEY')
        if not groq_api_key:
            print("❌ GROQ_API_KEY not found")
            return False
            
        medical_system = MedicalRealtimeAgentSystem(groq_api_key)
        
        print("✅ Medical Agent System initialized successfully!")
        
        # Test a simple search
        print("\n🔍 Testing medical product search...")
        result = medical_system.search_medical_products("aspirin")
        print(f"Search result: {result[:200]}...")
        
        print("✅ Medical Agent System is working with Groq!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing medical system: {str(e)}")
        return False

def main():
    print("🧪 Testing Groq API Integration with Medical Agent System")
    print("=" * 60)
    
    # Test 1: Check if Groq API is accessible
    if not test_groq_connection():
        return
    
    # Test 2: Test medical system
    if test_medical_system():
        print("\n🎉 All tests passed! Groq integration is working.")
    else:
        print("\n❌ Medical system test failed.")

if __name__ == "__main__":
    main() 