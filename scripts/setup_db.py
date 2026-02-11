import sqlite3
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.config import Config

def create_database():
    """Create SQLite database with customer support schema"""
    
    try:
        os.makedirs(os.path.dirname(Config.DATABASE_PATH), exist_ok=True)
        
        conn = sqlite3.connect(Config.DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            account_status TEXT DEFAULT 'active',
            tier TEXT DEFAULT 'standard'
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS support_tickets (
            ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            subject TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'open',
            priority TEXT DEFAULT 'medium',
            category TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            resolved_at TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
        )
        """)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_customer_email ON customers(email)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ticket_customer ON support_tickets(customer_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ticket_status ON support_tickets(status)")
        
        conn.commit()
        conn.close()
        
        print(f"Database created successfully at {Config.DATABASE_PATH}")
        return True
        
    except Exception as e:
        print(f"Error creating database: {e}")
        return False

if __name__ == "__main__":
    create_database()
