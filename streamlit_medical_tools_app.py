import streamlit as st
import logging
from medical_tools_agent import MedicalToolsAgentSystem
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    st.set_page_config(
        page_title="Medical AI Assistant - Tools Edition",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🏥 Medical AI Assistant - Tools Edition")
    st.markdown("**Dynamic Tool Selection for Medical Queries**")
    
    # Initialize session state
    if 'tools_system' not in st.session_state:
        st.session_state.tools_system = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Groq API Key input
        groq_api_key = st.text_input(
            "Groq API Key",
            type="password",
            help="Enter your Groq API key"
        )
        
        if st.button("🔧 Initialize System"):
            if groq_api_key:
                try:
                    with st.spinner("Initializing Medical Tools Agent System..."):
                        st.session_state.tools_system = MedicalToolsAgentSystem(groq_api_key)
                    st.success("✅ System initialized successfully!")
                    logger.info("MedicalToolsAgentSystem initialized successfully")
                except Exception as e:
                    st.error(f"❌ Error initializing system: {str(e)}")
                    logger.error(f"Error initializing system: {str(e)}")
            else:
                st.error("Please enter your Groq API key")
        
        st.markdown("---")
        st.markdown("### 📋 Sample Queries")
        
        sample_queries = [
            "Find pain relief medications",
            "What are the side effects of ibuprofen?",
            "Tell me about acetaminophen dosage for adults",
            "Check insurance coverage for lisinopril",
            "Find alternatives to Tylenol",
            "What should I know about blood pressure medications?",
            "How do I take ibuprofen safely?",
            "What are the warnings for acetaminophen?"
        ]
        
        for query in sample_queries:
            if st.button(query, key=f"sample_{query}"):
                st.session_state.user_input = query
    
    # Main content area
    if st.session_state.tools_system is None:
        st.info("👈 Please initialize the system in the sidebar first.")
        return
    
    # Chat interface
    st.header("💬 Medical Assistant Chat")
    
    # User input
    user_input = st.text_input(
        "Ask me about medications, medical products, or health questions:",
        key="user_input",
        placeholder="e.g., Find pain relief medications, What are ibuprofen side effects?"
    )
    
    # Process user input
    if user_input:
        logger.info(f"User query received: '{user_input}'")
        
        try:
            with st.spinner("🤔 Analyzing your query and selecting appropriate tools..."):
                response = st.session_state.tools_system.process_user_query(user_input)
            
            # Add to chat history
            st.session_state.chat_history.append({
                "user": user_input,
                "assistant": response
            })
            
            logger.info(f"Generated response: {response[:100]}...")
            
        except Exception as e:
            error_msg = f"Error processing your request: {str(e)}"
            st.error(error_msg)
            logger.error(f"Error processing user query: {str(e)}")
            
            st.session_state.chat_history.append({
                "user": user_input,
                "assistant": error_msg
            })
    
    # Display chat history
    st.markdown("---")
    st.subheader("📝 Chat History")
    
    for i, chat in enumerate(st.session_state.chat_history):
        with st.container():
            st.markdown(f"**👤 You:** {chat['user']}")
            st.markdown(f"**🤖 Assistant:** {chat['assistant']}")
            st.markdown("---")
    
    # Clear chat button
    if st.button("🗑️ Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()
    
    # System information
    with st.expander("ℹ️ System Information"):
        st.markdown("""
        **Medical AI Assistant - Tools Edition**
        
        This system uses dynamic tool selection to provide medical information:
        
        **Available Tools:**
        - **search_medical_products**: Find medications and medical products
        - **get_product_details**: Get detailed information about specific products
        - **calculate_dosage**: Calculate appropriate medication dosages
        - **check_safety**: Check safety information and drug interactions
        - **check_insurance_coverage**: Check insurance coverage for medications
        - **find_alternatives**: Find alternative medications
        - **general_medical_advice**: Provide general health information
        
        **How it works:**
        1. You ask a question
        2. The AI analyzes your query
        3. It selects the most appropriate tool(s)
        4. It executes the tool(s) and provides results
        
        **Safety Notice:**
        This is for informational purposes only. Always consult healthcare professionals for medical advice.
        """)

if __name__ == "__main__":
    main() 