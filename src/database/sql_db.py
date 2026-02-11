import sqlite3
from src.config import Config
import json

class SQLDatabase:
    """SQLite database connector for customer support data"""
    
    def __init__(self):
        self.db_path = Config.DATABASE_PATH
    
    def get_connection(self):
        """Get database connection"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
        except Exception as e:
            print(f"Error connecting to database: {e}")
            return None
    
    def execute_query(self, query, params=None):
        """Execute SELECT query and return results"""
        conn = self.get_connection()
        if not conn:
            return {"error": "Database connection failed"}
        
        cursor = conn.cursor()
        
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            results = cursor.fetchall()
            
            if not results:
                return []
            
            columns = [description[0] for description in cursor.description]
            result_dicts = [dict(zip(columns, row)) for row in results]
            
            return result_dicts
        
        except sqlite3.Error as e:
            return {"error": f"SQL execution error: {str(e)}"}
        
        finally:
            conn.close()
    
    def get_schema_info(self):
        """Get database schema for LLM context"""
        schema = {
            "customers": {
                "columns": [
                    "customer_id (INTEGER PRIMARY KEY)",
                    "first_name (TEXT)",
                    "last_name (TEXT)",
                    "email (TEXT UNIQUE)",
                    "phone (TEXT)",
                    "created_at (TIMESTAMP)",
                    "account_status (TEXT: active, suspended)",
                    "tier (TEXT: standard, premium, enterprise)"
                ],
                "description": "Customer profile and account information"
            },
            "support_tickets": {
                "columns": [
                    "ticket_id (INTEGER PRIMARY KEY)",
                    "customer_id (INTEGER FOREIGN KEY)",
                    "subject (TEXT)",
                    "description (TEXT)",
                    "status (TEXT: open, in_progress, resolved, closed)",
                    "priority (TEXT: low, medium, high, urgent)",
                    "category (TEXT: billing, technical, account, refund, product_inquiry, complaint)",
                    "created_at (TIMESTAMP)",
                    "updated_at (TIMESTAMP)",
                    "resolved_at (TIMESTAMP)"
                ],
                "description": "Customer support tickets and their status"
            }
        }
        return schema
    
    def validate_query(self, query):
        """Basic safety validation for SQL queries"""
        query_lower = query.lower().strip()
        
        forbidden_keywords = ['drop', 'delete', 'update', 'insert', 'alter', 'create', 'truncate', 'replace']
        
        for keyword in forbidden_keywords:
            if keyword in query_lower:
                return False, f"Operation not allowed: {keyword.upper()}"
        
        if not query_lower.startswith('select'):
            return False, "Only SELECT queries are allowed"
        
        return True, "Valid query"
    
    def test_connection(self):
        """Test database connection and return basic stats"""
        conn = self.get_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM customers")
            customer_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM support_tickets")
            ticket_count = cursor.fetchone()[0]
            
            return {
                "status": "connected",
                "customers": customer_count,
                "tickets": ticket_count
            }
        except Exception as e:
            return {"error": str(e)}
        finally:
            conn.close()
