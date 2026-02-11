import os
import sys
from fpdf import FPDF

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

OUTPUT_DIR = "./data/sample_policies"

def create_refund_policy():
    """Generate refund policy PDF"""
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Refund and Return Policy", ln=True, align='C')
    pdf.set_font("Arial", '', 12)
    pdf.ln(10)
    
    content = """
Our company is committed to customer satisfaction. This refund policy outlines 
the terms and conditions for returns and refunds.

1. ELIGIBILITY FOR REFUNDS

Products must be returned within 30 days of purchase. Items must be in original 
condition with tags attached. Proof of purchase (receipt or order number) is required. 
Digital products are non-refundable once downloaded or accessed.

2. REFUND PROCESS

Request a refund through your customer account or contact our support team. 
Processing time is 5-7 business days after receiving the returned item. Refunds 
will be issued to the original payment method. Shipping costs are non-refundable 
unless the item was defective or shipped incorrectly.

3. TIER-BASED POLICIES

Standard tier customers: 30-day return window
Premium tier customers: 60-day return window with priority processing
Enterprise tier customers: 90-day return window with dedicated account manager

4. EXCEPTIONS AND SPECIAL CASES

Defective items receive full refund including shipping costs. Restocking fee of 
15% applies to opened electronic items. Custom or personalized items cannot be 
returned unless defective. Sale items marked as final sale are not eligible for return.

5. EXCHANGE POLICY

Exchanges are processed within 3-5 business days. Size and color exchanges are 
free for premium and enterprise customers. Standard customers may incur shipping 
charges for exchanges.

6. CONTACT INFORMATION

For refund inquiries, contact our support team at support@company.com or call 
1-800-SUPPORT between 9 AM and 6 PM EST Monday through Friday.
    """
    
    pdf.multi_cell(0, 5, content)
    pdf.output(os.path.join(OUTPUT_DIR, "refund_policy.pdf"))

def create_privacy_policy():
    """Generate privacy policy PDF"""
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Privacy Policy", ln=True, align='C')
    pdf.set_font("Arial", '', 12)
    pdf.ln(10)
    
    content = """
Effective Date: January 1, 2026

We value your privacy and are committed to protecting your personal information.

1. INFORMATION WE COLLECT

We collect information you provide directly such as name, email address, phone 
number, and billing information. We also collect account activity, purchase history, 
and support interactions. Device information and IP addresses are collected for 
security purposes.

2. HOW WE USE YOUR INFORMATION

Your information is used to process orders and provide customer support. We send 
account notifications and service updates. Information helps improve our products 
and services. We use data for fraud prevention and security monitoring.

3. DATA SHARING AND DISCLOSURE

We do not sell your personal information to third parties. We may share data with 
service providers who assist in operations such as payment processors and shipping 
companies. Legal authorities receive information when required by law or to protect 
our rights.

4. YOUR PRIVACY RIGHTS

You can access your personal data at any time through your account settings. 
Request deletion of your account and associated data by contacting our privacy team. 
Opt out of marketing communications through account preferences or email links. 
Update your information directly in your account dashboard.

5. DATA SECURITY MEASURES

We use industry-standard encryption and security measures to protect your data. 
All payment information is processed through secure, PCI-compliant systems. 
Regular security audits ensure ongoing protection of customer information.

6. COOKIES AND TRACKING

We use cookies to enhance user experience and analyze site usage. You can control 
cookie preferences through your browser settings. Third-party analytics help us 
improve our services.

7. DATA RETENTION

We retain your data for as long as your account is active or as needed to provide 
services. Deleted accounts are purged from active systems within 90 days. Some 
information may be retained for legal or regulatory compliance.

Contact our privacy team at privacy@company.com for questions or concerns.
    """
    
    pdf.multi_cell(0, 5, content)
    pdf.output(os.path.join(OUTPUT_DIR, "privacy_policy.pdf"))

def create_terms_of_service():
    """Generate terms of service PDF"""
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Terms of Service", ln=True, align='C')
    pdf.set_font("Arial", '', 12)
    pdf.ln(10)
    
    content = """
Last Updated: January 1, 2026

These Terms of Service govern your use of our services and products.

1. ACCOUNT TERMS

You must be 18 years or older to create an account. You are responsible for 
maintaining account security and all activities under your account. One account 
per person is allowed and multiple accounts are prohibited. Accounts cannot be 
transferred or sold to other parties.

2. ACCEPTABLE USE POLICY

Use services only for lawful purposes and in accordance with these terms. Do not 
attempt to hack, disrupt, or abuse the platform or its users. Do not upload 
malicious content or engage in fraudulent activities. Premium features require 
an active subscription with valid payment method.

3. SUBSCRIPTION AND BILLING

Subscriptions automatically renew unless canceled 24 hours before renewal date. 
Standard tier costs $9.99 per month. Premium tier costs $29.99 per month. 
Enterprise tier pricing is customized based on needs. Price changes will be 
communicated 30 days in advance. Cancel anytime through account settings with 
no penalties.

4. INTELLECTUAL PROPERTY

All content, trademarks, logos, and software are our property or licensed to us. 
Users retain ownership of content they upload or create. By uploading content, 
you grant us license to use it for service provision and improvement.

5. SERVICE AVAILABILITY

We strive for 99.9% uptime but cannot guarantee uninterrupted service. Scheduled 
maintenance will be announced in advance when possible. We are not liable for 
service interruptions beyond our reasonable control.

6. LIMITATION OF LIABILITY

We are not liable for indirect, incidental, or consequential damages. Our liability 
is limited to the amount paid for services in the past 12 months. We do not guarantee 
specific results from using our services.

7. ACCOUNT TERMINATION

We may terminate accounts that violate these terms with 7 days notice. Upon 
termination, you will lose access to all account data and content. You may request 
a data export before account closure.

8. DISPUTE RESOLUTION

Disputes will be resolved through binding arbitration rather than court proceedings. 
Class action lawsuits are waived by using our services.

9. CHANGES TO TERMS

We reserve the right to modify these terms at any time. Users will be notified of 
material changes via email. Continued use after changes constitutes acceptance.

For legal questions, contact legal@company.com
    """
    
    pdf.multi_cell(0, 5, content)
    pdf.output(os.path.join(OUTPUT_DIR, "terms_of_service.pdf"))

if __name__ == "__main__":
    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        print("Generating policy documents...")
        
        create_refund_policy()
        print("Created refund_policy.pdf")
        
        create_privacy_policy()
        print("Created privacy_policy.pdf")
        
        create_terms_of_service()
        print("Created terms_of_service.pdf")
        
        print("Policy generation complete")
        
    except Exception as e:
        print(f"Error generating policies: {e}")
