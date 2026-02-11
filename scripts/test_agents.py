import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.orchestration.graph import MultiAgentOrchestrator
from src.config import Config

def test_orchestrator():
    """Test the multi-agent orchestrator"""
    
    try:
        Config.validate()
        
        print("Initializing Multi-Agent Orchestrator...")
        orchestrator = MultiAgentOrchestrator()
        
        print("\n" + "="*60)
        print("Testing Multi-Agent Orchestrator")
        print("="*60)
        
        test_queries = [
            ("What is the refund policy?", "RAG"),
            ("How many customers do we have?", "SQL"),
            ("List all premium tier customers", "SQL"),
            ("How do I cancel my subscription?", "RAG"),
            ("What are the open support tickets?", "SQL"),
            ("What information do you collect about users?", "RAG")
        ]
        
        for i, (query, expected_agent) in enumerate(test_queries, 1):
            print(f"\n{'='*60}")
            print(f"Test {i}: {query}")
            print(f"Expected Agent: {expected_agent}")
            print(f"{'='*60}\n")
            
            response = orchestrator.query(query)
            
            print(f"Response:\n{response}\n")
        
        print("\n" + "="*60)
        print("Multi-Agent Orchestrator testing complete")
        print("="*60)
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_orchestrator()
