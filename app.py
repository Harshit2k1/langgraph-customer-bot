import streamlit as st
import os
import sys
import tempfile
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

def process_uploaded_pdf(uploaded_file, persist=False):
    """Process and ingest uploaded PDF into vector store"""
    try:
        if persist:
            upload_dir = "./data/uploaded_pdfs"
            os.makedirs(upload_dir, exist_ok=True)
            file_path = os.path.join(upload_dir, uploaded_file.name)
            
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
        else:
            temp_dir = tempfile.gettempdir()
            file_path = os.path.join(temp_dir, uploaded_file.name)
            
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
        
        processor = DocumentProcessor()
        chunks = processor.process_pdf(file_path)
        
        if not chunks:
            return False, "Failed to process PDF"
        
        if persist:
            vector_store = st.session_state.orchestrator.rag_agent.vector_store
            
            documents = [chunk['text'] for chunk in chunks]
            metadatas = [chunk['metadata'] for chunk in chunks]
            
            existing_count = vector_store.get_collection_stats()['total_documents']
            ids = [f"chunk_{existing_count + i}" for i in range(len(chunks))]
            
            success = vector_store.add_documents(documents, metadatas, ids)
            
            if success:
                return True, f"✅ Permanently stored {len(chunks)} chunks from {uploaded_file.name}"
            else:
                return False, "Failed to add documents to vector store"
        else:
            if 'temp_documents' not in st.session_state:
                st.session_state.temp_documents = []
            
            st.session_state.temp_documents.extend(chunks)
            
            if not os.path.exists(file_path):
                return False, "Temporary file not accessible"
            
            return True, f"📄 Temporarily loaded {len(chunks)} chunks from {uploaded_file.name} (session only)"
            
    except Exception as e:
        return False, f"Error processing PDF: {str(e)}"

def search_temp_documents(query, k=4):
    """Search temporary documents without vector store"""
    if 'temp_documents' not in st.session_state or not st.session_state.temp_documents:
        return None
    
    from sentence_transformers import SentenceTransformer
    import numpy as np
    
    model = SentenceTransformer(Config.EMBEDDING_MODEL)
    
    query_embedding = model.encode(query)
    
    doc_texts = [chunk['text'] for chunk in st.session_state.temp_documents]
    doc_embeddings = model.encode(doc_texts)
    
    similarities = np.dot(doc_embeddings, query_embedding)
    top_k_indices = np.argsort(similarities)[-k:][::-1]
    
    results = []
    for idx in top_k_indices:
        chunk = st.session_state.temp_documents[idx]
        results.append({
            'document': chunk['text'],
            'metadata': chunk['metadata'],
            'distance': float(1 - similarities[idx])
        })
    
    return results

def render_sidebar():
    """Render sidebar with file upload and system info"""
    with st.sidebar:
        st.title("🤖 Customer Support AI")
        st.markdown("---")
        
        st.subheader("📄 Upload Policy Documents")
        
        persist_mode = st.checkbox(
            "💾 Save Permanently",
            value=False,
            help="OFF: Document available only in current session\nON: Document saved to database permanently"
        )
        
        if persist_mode:
            st.info("🔒 Documents will be saved permanently")
        else:
            st.warning("⚠️ Documents will be cleared when session ends")
        
        uploaded_file = st.file_uploader(
            "Upload PDF",
            type=['pdf'],
            help="Upload company policy documents"
        )
        
        if uploaded_file is not None:
            file_key = f"{uploaded_file.name}_{'persist' if persist_mode else 'temp'}"
            
            if file_key not in st.session_state.get('processed_files', []):
                with st.spinner(f"Processing {uploaded_file.name}..."):
                    success, message = process_uploaded_pdf(uploaded_file, persist=persist_mode)
                    
                    if success:
                        st.success(message)
                        if 'processed_files' not in st.session_state:
                            st.session_state.processed_files = []
                        st.session_state.processed_files.append(file_key)
                        
                        if persist_mode:
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
                st.metric("Permanent Docs", vector_stats.get('total_documents', 'N/A'))
                
                temp_count = len(st.session_state.get('temp_documents', []))
                if temp_count > 0:
                    st.metric("Temporary Docs", temp_count)
                
            except Exception as e:
                st.warning("Unable to fetch stats")
        
        st.markdown("---")
        
        if st.button("🗑️ Clear Conversation", use_container_width=True):
            SessionManager.clear_messages()
            st.rerun()
        
        if st.button("🔄 Clear Temporary Docs", use_container_width=True):
            if 'temp_documents' in st.session_state:
                st.session_state.temp_documents = []
            if 'processed_files' in st.session_state:
                st.session_state.processed_files = [f for f in st.session_state.processed_files if 'persist' in f]
            st.success("Temporary documents cleared")
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
            st.subheader("📁 Permanent Files")
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
                
                has_temp_docs = 'temp_documents' in st.session_state and len(st.session_state.temp_documents) > 0
                
                if has_temp_docs:
                    temp_results = search_temp_documents(prompt)
                    
                    if temp_results:
                        from openai import OpenAI
                        client = OpenAI(api_key=Config.OPENAI_API_KEY)
                        
                        context = "\n\n".join([
                            f"[Source: {r['metadata']['source']}, Page {r['metadata']['page']}]\n{r['document']}"
                            for r in temp_results
                        ])
                        
                        temp_response = client.chat.completions.create(
                            model=Config.OPENAI_MODEL,
                            messages=[
                                {"role": "system", "content": f"Answer based on this context:\n\n{context}"},
                                {"role": "user", "content": prompt}
                            ]
                        )
                        
                        response = "📄 **From Temporary Document:**\n\n" + temp_response.choices[0].message.content
                    else:
                        response = st.session_state.orchestrator.query(
                            prompt,
                            conversation_history[:-1] if len(conversation_history) > 1 else None
                        )
                else:
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
