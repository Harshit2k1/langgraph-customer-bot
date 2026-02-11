import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config import Config
from src.orchestration.graph import MultiAgentOrchestrator

def test_mcp_functionality():
    """Test that MCP server components work"""
    
    try:
        Config.validate()
        
        print("="*60)
        print("Testing MCP Server Components")
        print("="*60)
        
        print("\nInitializing orchestrator...")
        orchestrator = MultiAgentOrchestrator()
        
        print("\nTool 1: query_customer_data")
        result = orchestrator.sql_agent.query("How many customers do we have?")
        print(f"Result: {result[:200]}...")
        
        print("\nTool 2: query_policy_documents")
        result = orchestrator.rag_agent.query("What is the refund policy?")
        print(f"Result: {result[:200]}...")
        
        print("\nTool 3: query_multi_agent")
        result = orchestrator.query("Show premium customers")
        print(f"Result: {result[:200]}...")
        
        print("\nTool 4: get_system_stats")
        sql_stats = orchestrator.sql_agent.get_database_stats()
        vector_stats = orchestrator.rag_agent.vector_store.get_collection_stats()
        print(f"Stats: Customers={sql_stats['customers']}, Tickets={sql_stats['tickets']}, Docs={vector_stats['total_documents']}")
        
        print("\n" + "="*60)
        print("All MCP server components working!")
        print("="*60)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_mcp_functionality()
