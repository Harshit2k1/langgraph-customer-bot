import streamlit as st
from typing import List, Dict

class SessionManager:
    """Manage Streamlit session state for conversation history"""
    
    @staticmethod
    def initialize():
        """Initialize session state variables"""
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        
        if 'orchestrator' not in st.session_state:
            st.session_state.orchestrator = None
        
        if 'uploaded_files' not in st.session_state:
            st.session_state.uploaded_files = []
    
    @staticmethod
    def add_message(role: str, content: str):
        """Add a message to conversation history"""
        st.session_state.messages.append({
            "role": role,
            "content": content
        })
    
    @staticmethod
    def get_messages() -> List[Dict[str, str]]:
        """Get all messages"""
        return st.session_state.messages
    
    @staticmethod
    def clear_messages():
        """Clear conversation history"""
        st.session_state.messages = []
    
    @staticmethod
    def get_conversation_history() -> List[Dict[str, str]]:
        """Get formatted conversation history for agents"""
        return st.session_state.messages
