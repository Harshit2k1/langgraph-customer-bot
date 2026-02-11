import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents.sql_agent import SQLAgent
from src.config import Config

def test_sql_agent():
    """Test SQL agent with various queries"""
    
    try:
        Config.validate()
        
        print("Initializing SQL Agent...")
        agent = SQLAgent()
        
        stats = agent.get_database_stats()
        print(f"\nDatabase Status: {stats}")
        
        if not stats or "error" in stats:
            print("Database not accessible. Run setup_db.py and generate_data.py first")
            return
        
        print("\n" + "="*60)
        print("Testing SQL Agent")
        print("="*60)
        
        test_queries = [
            "How many customers do we have in total?",
            "Show me all customers with premium tier",
            "What are the open support tickets?",
            "Give me customer Emma's profile if it exists",
            "List the 5 most recent support tickets",
            "How many tickets are in resolved status?",
            "Show me customers who have more than 3 support tickets"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{'='*60}")
            print(f"Test {i}: {query}")
            print(f"{'='*60}")
            
            response = agent.query(query)
            print(f"\nResponse:\n{response}")
        
        print("\n" + "="*60)
        print("SQL Agent testing complete")
        print("="*60)
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_sql_agent()
