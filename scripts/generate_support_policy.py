import os
import sys
from fpdf import FPDF

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

OUTPUT_DIR = "./data/sample_policies"

def create_customer_support_policy():
    """Generate customer support policy PDF"""
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Customer Support Policy", ln=True, align='C')
    pdf.set_font("Arial", '', 12)
    pdf.ln(10)
    
    content = """
Effective Date: January 1, 2026

Our customer support team is available to assist you with any questions or concerns.

1. SUPPORT HOURS

Standard Support: Monday to Friday, 9 AM to 6 PM EST
Premium Support: 24/7 availability including weekends and holidays
Enterprise Support: Dedicated account manager with direct phone line

2. RESPONSE TIME GUARANTEES

Standard Tier: First response within 24 business hours
Premium Tier: First response within 4 hours
Enterprise Tier: First response within 1 hour

Priority levels affect response time:
- Urgent: Immediate response for service outages
- High: Response within 2 hours
- Medium: Response within 8 hours
- Low: Response within 24 hours

3. SUPPORT CHANNELS

Email: support@company.com
Phone: 1-800-SUPPORT (Standard and Premium customers)
Live Chat: Available on website during business hours
Help Center: 24/7 access to knowledge base and FAQs

4. TICKET RESOLUTION PROCESS

All support requests are tracked via ticket system. You will receive:
- Ticket confirmation email within 5 minutes
- Status updates every 24 hours until resolution
- Satisfaction survey after ticket closure

Average resolution times:
- Technical issues: 2-3 business days
- Billing inquiries: 1 business day
- Account changes: Same day for Premium/Enterprise

5. ESCALATION POLICY

If your issue is not resolved to your satisfaction:
- Request escalation through your support ticket
- Cases escalate to senior support after 48 hours
- Premium customers can request immediate escalation
- Enterprise customers have direct manager contact

6. SELF-SERVICE OPTIONS

Knowledge Base: 500+ articles covering common questions
Video Tutorials: Step-by-step guides for product features
Community Forum: Connect with other users and experts
Status Page: Real-time service status updates

7. SPECIALIZED SUPPORT

Technical Support: Product functionality and troubleshooting
Billing Support: Invoices, payments, and subscription management
Account Support: Profile changes, upgrades, cancellations
Sales Support: Product inquiries and purchase assistance

8. CONTACT INFORMATION

General Support: support@company.com
Technical Support: tech@company.com
Billing Support: billing@company.com
Phone: 1-800-SUPPORT
    """
    
    pdf.multi_cell(0, 5, content)
    pdf.output(os.path.join(OUTPUT_DIR, "customer_support_policy.pdf"))

if __name__ == "__main__":
    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        print("Generating customer support policy...")
        create_customer_support_policy()
        print("Created customer_support_policy.pdf")
    except Exception as e:
        print(f"Error: {e}")
