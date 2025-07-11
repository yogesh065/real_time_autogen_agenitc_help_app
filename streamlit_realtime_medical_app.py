import streamlit as st
import asyncio
import json
import os
import uuid
import logging
from datetime import datetime
import time
import threading
from typing import Dict, Any

# FastAPI and WebSocket imports
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import uvicorn
from fastapi.staticfiles import StaticFiles

# AutoGen imports
from autogen_realtime_medical import MedicalRealtimeAgentSystem
from medical_database import MedicalProductDatabase

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Medical AI Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for medical theme
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e88e5, #42a5f5);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .realtime-status {
        background: #e8f5e8;
        border: 2px solid #4caf50;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        text-align: center;
    }
    .voice-controls {
        background: #f0f8ff;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .agent-response {
        background: #f8f9fa;
        padding: 1.5rem;
        border-left: 4px solid #1e88e5;
        margin: 1rem 0;
        border-radius: 5px;
    }
    .safety-warning {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .critical-warning {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if 'db' not in st.session_state:
    st.session_state.db = MedicalProductDatabase()

if 'realtime_system' not in st.session_state:
    # Get Groq API key
    groq_api_key = os.getenv('GROQ_API_KEY') or st.secrets.get('GROQ_API_KEY')
    if not groq_api_key:
        st.error("⚠️ Groq API key not found. Please set GROQ_API_KEY environment variable.")
        st.info("Get your API key from: https://console.groq.com/")
        st.stop()
    
    logger.info("Initializing MedicalRealtimeAgentSystem with Groq API key")
    st.session_state.realtime_system = MedicalRealtimeAgentSystem(groq_api_key)
    logger.info("MedicalRealtimeAgentSystem initialized successfully")

if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

# Main header
st.markdown("""
<div class="main-header">
    <h1>🏥 Medical AI Assistant</h1>
    <p>Medical Product Support powered by AutoGen & Groq</p>
    <p>🤖 AI responds in real-time • 🏥 Professional medical guidance • ⚡ Powered by Groq's Fast LLM</p>
</div>
""", unsafe_allow_html=True)

# Main interface
col1, col2 = st.columns([2, 1])

with col1:
    st.header("💬 Medical Product Support")
    
    # Text-based interaction
    st.subheader("Ask about medical products")
    st.info("Use text input below to get information about medical products, dosages, safety, and more")
    
    user_query = st.text_area(
        "Ask about medical products:",
        placeholder="e.g., 'Tell me about acetaminophen dosage for adults' or 'What are the side effects of ibuprofen?'"
    )
    
    if st.button("🧠 Process with Medical Agents"):
        if user_query:
            logger.info(f"User query received: '{user_query}'")
            with st.spinner("Medical agents processing your query..."):
                # Simulate agent processing
                if "search" in user_query.lower() or "find" in user_query.lower():
                    logger.info("Processing as search query")
                    response = st.session_state.realtime_system.search_medical_products(user_query)
                elif "dosage" in user_query.lower() or "dose" in user_query.lower():
                    logger.info("Processing as dosage query")
                    # Extract product name (simplified)
                    product_name = user_query.split()[-1] if user_query.split() else "acetaminophen"
                    response = st.session_state.realtime_system.calculate_dosage(product_name, 30, 70)
                elif "side effect" in user_query.lower() or "safety" in user_query.lower():
                    logger.info("Processing as safety query")
                    product_name = user_query.split()[-1] if user_query.split() else "ibuprofen"
                    response = st.session_state.realtime_system.assess_safety_profile(product_name)
                else:
                    logger.info("Processing as general search query")
                    response = st.session_state.realtime_system.search_medical_products(user_query)
                
                logger.info(f"Generated response: {response[:100]}...")
                
                # Add to conversation history
                st.session_state.conversation_history.append({
                    'user': user_query,
                    'assistant': response,
                    'timestamp': datetime.now(),
                    'method': 'text'
                })
                
                # Display response
                st.markdown(f'<div class="agent-response">{response}</div>', 
                           unsafe_allow_html=True)
                logger.info("Response displayed to user")
        else:
            logger.warning("Empty user query received")

with col2:
    st.header("⚡ Quick Actions")
    
    # Sample medical queries
    st.subheader("🧪 Sample Queries")
    sample_queries = [
        "Find pain relief medications",
        "Acetaminophen dosage for adults",
        "Ibuprofen side effects and warnings",
        "Blood pressure medications available",
        "Drug interactions between aspirin and warfarin",
        "Insurance coverage for diabetes medications",
        "Generic alternatives to brand medications",
        "Pediatric dosing for fever reducers"
    ]
    
    for i, query in enumerate(sample_queries):
        if st.button(query, key=f"sample_{i}"):
            logger.info(f"Sample query clicked: '{query}'")
            # Process sample query
            if "dosage" in query.lower():
                product_name = query.split()[0]
                response = st.session_state.realtime_system.calculate_dosage(product_name, 30, 70)
            elif "side effect" in query.lower():
                product_name = query.split()[0]
                response = st.session_state.realtime_system.assess_safety_profile(product_name)
            elif "interaction" in query.lower():
                meds = ["aspirin", "warfarin"]
                response = st.session_state.realtime_system.check_drug_interactions(meds)
            else:
                response = st.session_state.realtime_system.search_medical_products(query)
            
            logger.info(f"Sample query response: {response[:100]}...")
            
            st.session_state.conversation_history.append({
                'user': query,
                'assistant': response,
                'timestamp': datetime.now(),
                'method': 'quick_action'
            })
            st.rerun()
    
    # Features
    st.subheader("🚀 Features")
    st.markdown("""
    **Medical Specialization:**
    - 🏥 Product search & information
    - 💊 Dosage calculations
    - ⚠️ Safety & interaction checks
    - 💰 Insurance coverage assistance
    
    **AutoGen Features:**
    - 🔄 Multi-agent coordination
    - 🎯 Specialized medical agents
    - 📊 Real-time processing
    - ⚡ Powered by Groq's Fast LLM
    """)

# Conversation History
if st.session_state.conversation_history:
    st.header("📋 Conversation History")
    
    for i, conv in enumerate(reversed(st.session_state.conversation_history[-10:])):
        with st.expander(f"Query {len(st.session_state.conversation_history) - i}: {conv['user'][:50]}..."):
            st.markdown(f"**👤 User:** {conv['user']}")
            st.markdown(f"**🤖 Medical AI:** {conv['assistant']}")
            st.markdown(f"**📅 Time:** {conv['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
            st.markdown(f"**📱 Method:** {conv['method']}")

# Medical Disclaimer
st.markdown("""
<div class="critical-warning">
    <h3>⚠️ Critical Medical Disclaimer</h3>
    <p><strong>This AI assistant provides general information only and should never be used as a substitute for professional medical advice, diagnosis, or treatment.</strong></p>
    <ul>
        <li>🏥 Always consult qualified healthcare professionals for medical decisions</li>
        <li>💊 Never start, stop, or change medications without doctor approval</li>
        <li>🚨 Seek immediate medical attention for emergency situations</li>
        <li>📋 Verify all medication information with pharmacists or physicians</li>
        <li>🔬 This system is for informational and educational purposes only</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
### 🚀 Medical AI Assistant Features:

**🤖 Multi-Agent Medical System:**
- **Medical Product Searcher**: Finds medications and products
- **Dosage Specialist**: Calculates appropriate dosages
- **Safety Checker**: Identifies risks and contraindications  
- **Insurance Specialist**: Provides coverage information
- **Coordinator**: Orchestrates agent collaboration

**🔧 AutoGen Integration:**
- Multi-agent coordination for complex queries
- Real-time function calling capabilities
- Advanced medical product database
- Comprehensive safety and interaction checking

**📊 Advanced Features:**
- Comprehensive medical product database
- Real-time interaction logging and analytics
- Multi-modal interaction support (text + quick actions)
- Professional medical guidance emphasis

**Powered by Microsoft AutoGen Technology**
""") 