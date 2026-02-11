from openai import OpenAI
from src.config import Config
from src.database.vector_db import VectorStore

class RAGAgent:
    """RAG agent for document retrieval and question answering"""
    
    def __init__(self):
        if not Config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not set")
        
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.vector_store = VectorStore()
    
    def retrieve_documents(self, query, k=None):
        """Retrieve relevant documents from vector store"""
        k = k or Config.TOP_K_RETRIEVAL
        
        try:
            results = self.vector_store.similarity_search(query, k=k)
            
            if not results:
                return None
            
            return results
            
        except Exception as e:
            print(f"Error retrieving documents: {e}")
            return None
    
    def format_context(self, retrieved_docs):
        """Format retrieved documents as context for LLM"""
        if not retrieved_docs:
            return None
        
        context_parts = []
        
        for i, doc in enumerate(retrieved_docs, 1):
            source = doc['metadata']['source']
            page = doc['metadata']['page']
            text = doc['document']
            
            context_parts.append(f"[Document {i}]\nSource: {source}, Page: {page}\n{text}\n")
        
        return "\n".join(context_parts)
    
    def query(self, user_question, conversation_history=None):
        """Answer questions using retrieved documents"""
        
        retrieved_docs = self.retrieve_documents(user_question)
        
        if not retrieved_docs:
            return "I couldn't find relevant information in the policy documents to answer your question. Please try rephrasing or contact support directly."
        
        context = self.format_context(retrieved_docs)
        
        system_prompt = """You are a helpful customer support assistant that answers questions based on company policy documents.

Instructions:
1. Answer questions using ONLY information from the provided context
2. Include inline citations with format [Source: filename.pdf, Page X]
3. If information isn't in the context, say so clearly
4. Be concise but complete
5. Format answers in a user-friendly way

Context from policy documents:
{context}
"""
        
        messages = [
            {"role": "system", "content": system_prompt.format(context=context)}
        ]
        
        if conversation_history:
            messages.extend(conversation_history[-Config.MEMORY_WINDOW:])
        
        messages.append({"role": "user", "content": user_question})
        
        try:
            response = self.client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=messages
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error generating response: {str(e)}"

    def stream_query(self, user_question, conversation_history=None):
        """Stream answers using retrieved documents."""
        retrieved_docs = self.retrieve_documents(user_question)

        if not retrieved_docs:
            yield "I couldn't find relevant information in the policy documents to answer your question. Please try rephrasing or contact support directly."
            return

        context = self.format_context(retrieved_docs)

        system_prompt = """You are a helpful customer support assistant that answers questions based on company policy documents.

Instructions:
1. Answer questions using ONLY information from the provided context
2. Include inline citations with format [Source: filename.pdf, Page X]
3. If information isn't in the context, say so clearly
4. Be concise but complete
5. Format answers in a user-friendly way

Context from policy documents:
{context}
"""

        messages = [
            {"role": "system", "content": system_prompt.format(context=context)}
        ]

        if conversation_history:
            messages.extend(conversation_history[-Config.MEMORY_WINDOW:])

        messages.append({"role": "user", "content": user_question})

        try:
            stream = self.client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=messages,
                stream=True
            )

            buffer = ""
            for event in stream:
                delta = event.choices[0].delta.content if event.choices else ""
                if not delta:
                    continue
                buffer += delta
                yield buffer

        except Exception as e:
            yield f"Error generating response: {str(e)}"
    
    def get_sources(self, user_question):
        """Get source documents for a query without generating answer"""
        retrieved_docs = self.retrieve_documents(user_question)
        
        if not retrieved_docs:
            return []
        
        sources = []
        for doc in retrieved_docs:
            sources.append({
                'source': doc['metadata']['source'],
                'page': doc['metadata']['page'],
                'preview': doc['document'][:200] + "..."
            })
        
        return sources
