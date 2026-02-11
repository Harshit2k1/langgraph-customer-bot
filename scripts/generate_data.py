import sqlite3
import os
import sys
from faker import Faker
import random
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.config import Config

fake = Faker()

def generate_customers(num=50):
    """Generate synthetic customer data"""
    
    try:
        conn = sqlite3.connect(Config.DATABASE_PATH)
        cursor = conn.cursor()
        
        customer_ids = []
        
        for _ in range(num):
            first_name = fake.first_name()
            last_name = fake.last_name()
            email = f"{first_name.lower()}.{last_name.lower()}@{fake.free_email_domain()}"
            phone = fake.phone_number()
            tier = random.choice(['standard'] * 6 + ['premium'] * 3 + ['enterprise'])
            status = random.choice(['active'] * 9 + ['suspended'])
            
            try:
                cursor.execute("""
                INSERT INTO customers (first_name, last_name, email, phone, tier, account_status)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (first_name, last_name, email, phone, tier, status))
                customer_ids.append(cursor.lastrowid)
            except sqlite3.IntegrityError:
                # Skip duplicate emails
                continue
        
        conn.commit()
        conn.close()
        
        print(f"Generated {len(customer_ids)} customers")
        return customer_ids
        
    except Exception as e:
        print(f"Error generating customers: {e}")
        return []

def generate_tickets(customer_ids, num=200):
    """Generate synthetic support ticket data"""
    
    if not customer_ids:
        print("No customer IDs provided")
        return
    
    try:
        conn = sqlite3.connect(Config.DATABASE_PATH)
        cursor = conn.cursor()
        
        categories = ['billing', 'technical', 'account', 'refund', 'product_inquiry', 'complaint']
        statuses = ['open', 'in_progress', 'resolved', 'closed']
        priorities = ['low', 'medium', 'high', 'urgent']
        
        subjects = [
            "Cannot access my account",
            "Billing discrepancy on invoice",
            "Refund request for order",
            "Technical issue with product",
            "Account upgrade inquiry",
            "Password reset not working",
            "Charged twice for subscription",
            "Product defect complaint",
            "Feature request",
            "General inquiry about services",
            "Subscription cancellation help",
            "Payment method update issue",
            "Unable to download content",
            "Service outage report",
            "Data export request"
        ]
        
        tickets_created = 0
        
        for _ in range(num):
            customer_id = random.choice(customer_ids)
            subject = random.choice(subjects)
            description = fake.text(max_nb_chars=200)
            status = random.choice(statuses)
            priority = random.choice(priorities)
            category = random.choice(categories)
            
            created_at = fake.date_time_between(start_date='-1y', end_date='now')
            updated_at = created_at + timedelta(hours=random.randint(1, 48))
            
            resolved_at = None
            if status in ['resolved', 'closed']:
                resolved_at = updated_at + timedelta(hours=random.randint(1, 72))
            
            cursor.execute("""
            INSERT INTO support_tickets 
            (customer_id, subject, description, status, priority, category, created_at, updated_at, resolved_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (customer_id, subject, description, status, priority, category, 
                  created_at, updated_at, resolved_at))
            
            tickets_created += 1
        
        conn.commit()
        conn.close()
        
        print(f"Generated {tickets_created} support tickets")
        
    except Exception as e:
        print(f"Error generating tickets: {e}")

if __name__ == "__main__":
    print("Generating synthetic customer support data...")
    customer_ids = generate_customers(50)
    
    if customer_ids:
        generate_tickets(customer_ids, 200)
        print("Data generation complete")
    else:
        print("Failed to generate data")
