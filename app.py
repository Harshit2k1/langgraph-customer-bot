import streamlit as st
import os
import sys
import tempfile
import time
from pathlib import Path
import logging

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

logging.basicConfig(
    level=getattr(logging, Config.LOGGING_LEVEL.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger(__name__)
if not Config.LOGGING_ENABLED:
    logging.disable(logging.CRITICAL)

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

def delete_permanent_document(filename):
    """Delete a specific document from permanent storage"""
    try:
        vector_store = st.session_state.orchestrator.rag_agent.vector_store
        
        success = vector_store.delete_by_source(filename)
        
        if not success:
            return False, "Document not found in vector store"
        
        file_path = f"./data/uploaded_pdfs/{filename}"
        if os.path.exists(file_path):
            os.remove(file_path)
        
        sample_policy_path = f"./data/sample_policies/{filename}"
        if os.path.exists(sample_policy_path):
            os.remove(sample_policy_path)
        
        return True, f"Successfully deleted {filename}"
        
    except Exception as e:
        return False, f"Error deleting document: {str(e)}"



def delete_temporary_document(filename):
    """Delete a specific temporary document"""
    try:
        if 'temp_documents' not in st.session_state:
            return False, "No temporary documents"
        
        original_count = len(st.session_state.temp_documents)
        st.session_state.temp_documents = [
            chunk for chunk in st.session_state.temp_documents 
            if chunk['metadata']['source'] != filename
        ]
        
        deleted_count = original_count - len(st.session_state.temp_documents)
        
        if deleted_count == 0:
            return False, "Document not found"
        
        return True, f"Successfully deleted {filename} ({deleted_count} chunks)"
        
    except Exception as e:
        return False, f"Error deleting document: {str(e)}"

def get_all_permanent_files():
    """Get list of all files in permanent vector store"""
    try:
        vector_store = st.session_state.orchestrator.rag_agent.vector_store
        return vector_store.get_all_sources()
    except Exception as e:
        return []



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
                        
                        if persist_mode and uploaded_file.name not in st.session_state.uploaded_files:
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
                st.metric("Permanent Chunks", vector_stats.get('total_documents', 'N/A'))
                
                temp_count = len(st.session_state.get('temp_documents', []))
                if temp_count > 0:
                    st.metric("Temporary Chunks", temp_count)
                
            except Exception as e:
                st.warning("Unable to fetch stats")
        
        st.markdown("---")
        
        if st.button("🗑️ Clear Conversation", use_container_width=True):
            SessionManager.clear_messages()
            st.rerun()
        
        if st.button("🔄 Clear All Temporary", use_container_width=True):
            if 'temp_documents' in st.session_state:
                st.session_state.temp_documents = []
            if 'processed_files' in st.session_state:
                st.session_state.processed_files = [f for f in st.session_state.processed_files if 'persist' in f]
            st.success("All temporary documents cleared")
            st.rerun()
        
        st.markdown("---")
        
        st.subheader("ℹ️ About")
        st.markdown("""
        Multi-agent system with:
        - **LangGraph** orchestration
        - **OpenAI GPT** understanding
        - **LanceDB** for vector storage
        - **SQLite** customer data
        """)
        
        st.markdown("---")
        
        all_permanent_files = get_all_permanent_files()
        temp_files = []
        if 'temp_documents' in st.session_state:
            temp_files = list(set([chunk['metadata']['source'] for chunk in st.session_state.temp_documents]))
        
        if all_permanent_files or temp_files:
            st.subheader("📁 Documents")
            
            if all_permanent_files:
                st.markdown("**Permanent:**")
                for file in all_permanent_files:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.text(f"✓ {file}")
                    with col2:
                        if st.button("🗑️", key=f"del_perm_{file}", help=f"Delete {file}"):
                            with st.spinner(f"Deleting {file}..."):
                                success, message = delete_permanent_document(file)
                                if success:
                                    if file in st.session_state.uploaded_files:
                                        st.session_state.uploaded_files.remove(file)
                                    st.success(message)
                                    st.rerun()
                                else:
                                    st.error(message)
            
            if temp_files:
                st.markdown("**Temporary:**")
                for file in temp_files:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.text(f"📄 {file}")
                    with col2:
                        if st.button("🗑️", key=f"del_temp_{file}", help=f"Delete {file}"):
                            success, message = delete_temporary_document(file)
                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)

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
        logger.info("User submitted prompt")
        SessionManager.add_message("user", prompt)
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            status_placeholder = st.empty()
            message_placeholder = st.empty()
            status_placeholder.markdown("⏳ **Thinking...**")

            cursor_char = "▍"
            cursor_blink_interval = 0.6
            last_blink = 0.0
            show_cursor = True

            def render_with_cursor(text: str, prefix: str = "") -> None:
                nonlocal last_blink, show_cursor
                now = time.time()
                if now - last_blink >= cursor_blink_interval:
                    show_cursor = not show_cursor
                    last_blink = now
                cursor = cursor_char if show_cursor else " "
                message_placeholder.markdown(f"{prefix}{text}{cursor}")

            conversation_history = SessionManager.get_conversation_history()

            has_temp_docs = 'temp_documents' in st.session_state and len(st.session_state.temp_documents) > 0

            response = ""

            render_with_cursor("")

            if has_temp_docs:
                status_placeholder.markdown("🔎 **Searching temporary documents...**")
                temp_results = search_temp_documents(prompt)

                if temp_results:
                    status_placeholder.markdown("🧠 **Generating response...**")
                    from openai import OpenAI
                    client = OpenAI(api_key=Config.OPENAI_API_KEY)

                    context = "\n\n".join([
                        f"[Source: {r['metadata']['source']}, Page {r['metadata']['page']}]\n{r['document']}"
                        for r in temp_results
                    ])

                    stream = client.chat.completions.create(
                        model=Config.OPENAI_MODEL,
                        messages=[
                            {"role": "system", "content": f"Answer based on this context:\n\n{context}"},
                            {"role": "user", "content": prompt}
                        ],
                        stream=True
                    )

                    render_with_cursor(response, "📄 **From Temporary Document:**\n\n")
                    for event in stream:
                        delta = event.choices[0].delta.content if event.choices else ""
                        if not delta:
                            continue
                        response += delta
                        render_with_cursor(response, "📄 **From Temporary Document:**\n\n")
                else:
                    status_placeholder.markdown("🧠 **Generating response...**")
                    for chunk in st.session_state.orchestrator.stream_query(
                        prompt,
                        conversation_history[:-1] if len(conversation_history) > 1 else None
                    ):
                        response = chunk
                        render_with_cursor(response)
            else:
                status_placeholder.markdown("🧠 **Generating response...**")
                for chunk in st.session_state.orchestrator.stream_query(
                    prompt,
                    conversation_history[:-1] if len(conversation_history) > 1 else None
                ):
                    response = chunk
                    render_with_cursor(response)

            status_placeholder.empty()
            message_placeholder.markdown(response)

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
