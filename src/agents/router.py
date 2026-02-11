from openai import OpenAI
from src.config import Config
import json

class RouterAgent:
    """Routes queries to appropriate agent (SQL, RAG, or both)"""
    
    def __init__(self):
        if not Config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not set")
        
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
    
    def route(self, user_question):
        """Determine which agent should handle the query"""
        
        system_prompt = """You are a routing agent that classifies user queries for a customer support system.

Your job is to determine which agent should handle each query:

1. SQL_AGENT: For queries about customer data, support tickets, account information
   Examples:
   - "Show me customer John's profile"
   - "How many open tickets are there?"
   - "List all premium customers"
   - "What tickets does customer X have?"

2. RAG_AGENT: For queries about company policies, procedures, refunds, terms
   Examples:
   - "What is the refund policy?"
   - "How do I cancel my subscription?"
   - "What information do you collect?"
   - "What are the terms of service?"

3. BOTH: When query needs information from both database AND policy documents
   Examples:
   - "Show me Emma's tickets and check if she's eligible for refund"
   - "List VIP customers and their refund policy"

Respond with JSON only:
{
  "agent": "SQL_AGENT" | "RAG_AGENT" | "BOTH",
  "reasoning": "brief explanation",
  "confidence": "high" | "medium" | "low"
}"""

        try:
            response = self.client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_question}
                ]
            )
            
            content = response.choices[0].message.content.strip()
            
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            result = json.loads(content)
            
            return result
            
        except Exception as e:
            print(f"Routing error: {e}")
            return {
                "agent": "RAG_AGENT",
                "reasoning": "Default to RAG due to routing error",
                "confidence": "low"
            }
