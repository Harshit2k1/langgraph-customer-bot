import streamlit as st
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.orchestration.graph import MultiAgentOrchestrator
from src.config import Config
from src.utils.session import SessionManager
from src.processing.document_processor import DocumentProcessor
from src.database.vector_db import VectorStore

st.set_page_config(
    page_title="Customer Support AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

def initialize_system():
    """Initialize the multi-agent system"""
    try:
        Config.validate()
        
        if st.session_state.orchestrator is None:
            with st.spinner("Initializing AI agents..."):
                st.session_state.orchestrator = MultiAgentOrchestrator()
        
        return True
    except Exception as e:
        st.error(f"Failed to initialize system: {e}")
        return False

def process_uploaded_pdf(uploaded_file):
    """Process and ingest uploaded PDF into vector store"""
    try:
        upload_dir = "./data/uploaded_pdfs"
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, uploaded_file.name)
        
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        processor = DocumentProcessor()
        chunks = processor.process_pdf(file_path)
        
        if not chunks:
            return False, "Failed to process PDF"
        
        vector_store = st.session_state.orchestrator.rag_agent.vector_store
        
        documents = [chunk['text'] for chunk in chunks]
        metadatas = [chunk['metadata'] for chunk in chunks]
        
        existing_count = vector_store.get_collection_stats()['total_documents']
        ids = [f"chunk_{existing_count + i}" for i in range(len(chunks))]
        
        success = vector_store.add_documents(documents, metadatas, ids)
        
        if success:
            return True, f"Successfully processed {len(chunks)} chunks from {uploaded_file.name}"
        else:
            return False, "Failed to add documents to vector store"
            
    except Exception as e:
        return False, f"Error processing PDF: {str(e)}"

def render_sidebar():
    """Render sidebar with file upload and system info"""
    with st.sidebar:
        st.title("🤖 Customer Support AI")
        st.markdown("---")
        
        st.subheader("📄 Upload Policy Documents")
        uploaded_file = st.file_uploader(
            "Upload PDF",
            type=['pdf'],
            help="Upload company policy documents to expand the knowledge base"
        )
        
        if uploaded_file is not None:
            if uploaded_file.name not in st.session_state.uploaded_files:
                with st.spinner(f"Processing {uploaded_file.name}..."):
                    success, message = process_uploaded_pdf(uploaded_file)
                    
                    if success:
                        st.success(message)
                        st.session_state.uploaded_files.append(uploaded_file.name)
                    else:
                        st.error(message)
        
        st.markdown("---")
        
        st.subheader("📊 System Status")
        
        if st.session_state.orchestrator:
            try:
                sql_stats = st.session_state.orchestrator.sql_agent.get_database_stats()
                vector_stats = st.session_state.orchestrator.rag_agent.vector_store.get_collection_stats()
                
                st.metric("Customers", sql_stats.get('customers', 'N/A'))
                st.metric("Support Tickets", sql_stats.get('tickets', 'N/A'))
                st.metric("Policy Documents", vector_stats.get('total_documents', 'N/A'))
            except Exception as e:
                st.warning("Unable to fetch stats")
        
        st.markdown("---")
        
        if st.button("🗑️ Clear Conversation", use_container_width=True):
            SessionManager.clear_messages()
            st.rerun()
        
        st.markdown("---")
        
        st.subheader("ℹ️ About")
        st.markdown("""
        This multi-agent system uses:
        - **LangGraph** for orchestration
        - **OpenAI GPT** for language understanding
        - **FAISS** for document retrieval
        - **SQLite** for customer data
        
        The system automatically routes queries to the appropriate agent (SQL or RAG) based on intent.
        """)
        
        if st.session_state.uploaded_files:
            st.markdown("---")
            st.subheader("📁 Uploaded Files")
            for file in st.session_state.uploaded_files:
                st.text(f"✓ {file}")

def render_chat():
    """Render chat interface"""
    st.title("💬 Customer Support Assistant")
    st.markdown("Ask questions about customer data or company policies")
    
    chat_container = st.container()
    
    with chat_container:
        for message in SessionManager.get_messages():
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    if prompt := st.chat_input("Ask a question..."):
        SessionManager.add_message("user", prompt)
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                conversation_history = SessionManager.get_conversation_history()
                
                response = st.session_state.orchestrator.query(
                    prompt,
                    conversation_history[:-1] if len(conversation_history) > 1 else None
                )
                
                st.markdown(response)
        
        SessionManager.add_message("assistant", response)

def main():
    """Main application entry point"""
    SessionManager.initialize()
    
    if not initialize_system():
        st.stop()
    
    render_sidebar()
    render_chat()

if __name__ == "__main__":
    main()
