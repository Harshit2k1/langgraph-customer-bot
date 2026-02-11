import os
import sys
from fpdf import FPDF

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

OUTPUT_DIR = "./data/sample_policies"

class PolicyPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'TechSupport Solutions Inc.', 0, 1, 'C')
        self.ln(5)
    
    def chapter_title(self, title):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(2)
    
    def chapter_body(self, body):
        self.set_font('Arial', '', 11)
        self.multi_cell(0, 5, body)
        self.ln()

def create_refund_policy():
    pdf = PolicyPDF()
    pdf.add_page()
    
    pdf.chapter_title("Refund and Return Policy")
    pdf.chapter_body("Effective Date: January 1, 2026\nLast Updated: January 1, 2026")
    
    pdf.chapter_title("1. Return Window")
    pdf.chapter_body("""
Standard Tier: 30-day return window from date of purchase
Premium Tier: 60-day return window from date of purchase
Enterprise Tier: 90-day return window with dedicated account manager

All returns must be initiated through your account dashboard or by contacting support at returns@techsupport.com.
""")
    
    pdf.chapter_title("2. Refund Processing Time")
    pdf.chapter_body("""
Credit Card: 5-7 business days after approval
PayPal: 3-5 business days after approval
Bank Transfer: 7-10 business days after approval

You will receive email confirmation once your refund has been processed.
""")
    
    pdf.chapter_title("3. Eligibility Requirements")
    pdf.chapter_body("""
Product must be in original condition with all accessories
No signs of damage or excessive wear
Original packaging preferred but not required
Proof of purchase (receipt or order number) required

Digital products are non-refundable after download unless defective.
""")
    
    pdf.chapter_title("4. Non-Refundable Items")
    pdf.chapter_body("""
- Downloadable software after activation
- Custom or personalized orders
- Gift cards and promotional credits
- Services already rendered
- Subscriptions past 14 days of renewal
""")
    
    pdf.chapter_title("5. Partial Refunds")
    pdf.chapter_body("""
Items returned after 30 days but within 60 days: 50% refund
Items with minor defects or missing accessories: Partial refund determined case-by-case
Opened software or hardware: May incur 15% restocking fee
""")
    
    pdf.chapter_title("6. Defective Products")
    pdf.chapter_body("""
Defective products eligible for full refund regardless of tier or time period.
We cover return shipping costs for defective items.
Replacement option available as alternative to refund.
Technical support will verify defect before processing refund.
""")
    
    pdf.chapter_title("7. How to Request a Refund")
    pdf.chapter_body("""
Step 1: Log into your account at techsupport.com
Step 2: Navigate to Order History
Step 3: Select the order and click "Request Return"
Step 4: Choose reason and provide details
Step 5: Receive return authorization within 24 hours
Step 6: Ship item with provided label
Step 7: Refund processed within 3-5 days of receipt
""")
    
    pdf.chapter_title("8. Contact Information")
    pdf.chapter_body("""
Email: returns@techsupport.com
Phone: 1-800-REFUND (1-800-733-8633)
Hours: Monday-Friday 9AM-6PM EST
Live Chat: Available 24/7 for Premium and Enterprise customers
""")
    
    pdf.output(os.path.join(OUTPUT_DIR, "refund_policy.pdf"))
    print("Created refund_policy.pdf")

def create_privacy_policy():
    pdf = PolicyPDF()
    pdf.add_page()
    
    pdf.chapter_title("Privacy Policy")
    pdf.chapter_body("Effective Date: January 1, 2026\nLast Updated: January 1, 2026")
    
    pdf.chapter_title("1. Information We Collect")
    pdf.chapter_body("""
Personal Information:
- Name, email address, phone number
- Billing and shipping address
- Payment information (encrypted)
- Account credentials

Technical Information:
- IP address and device information
- Browser type and operating system
- Cookies and tracking data
- Usage patterns and preferences

Support Information:
- Support ticket contents and history
- Chat transcripts and call recordings
- Product feedback and reviews
""")
    
    pdf.chapter_title("2. How We Use Your Information")
    pdf.chapter_body("""
We use collected information to:
- Process orders and provide customer support
- Send order confirmations and updates
- Improve our products and services
- Personalize your experience
- Prevent fraud and enhance security
- Comply with legal obligations
- Send marketing communications (with consent)

We never sell your personal information to third parties.
""")
    
    pdf.chapter_title("3. Data Sharing and Disclosure")
    pdf.chapter_body("""
We may share your information with:

Service Providers: Payment processors, shipping companies, email service providers
Legal Requirements: Law enforcement, regulatory agencies when required by law
Business Transfers: In case of merger, acquisition, or asset sale
With Your Consent: When you explicitly authorize sharing

All third parties are bound by confidentiality agreements.
""")
    
    pdf.chapter_title("4. Data Security")
    pdf.chapter_body("""
Security measures include:
- 256-bit SSL encryption for data transmission
- Encrypted storage of sensitive information
- Regular security audits and penetration testing
- Multi-factor authentication available
- Access controls and employee training
- Automated backup systems

No system is 100% secure. We continuously update our security practices.
""")
    
    pdf.chapter_title("5. Your Rights and Choices")
    pdf.chapter_body("""
You have the right to:
- Access your personal information
- Request correction of inaccurate data
- Request deletion of your data
- Opt-out of marketing communications
- Export your data in portable format
- Object to certain data processing activities

Contact privacy@techsupport.com to exercise your rights.
""")
    
    pdf.chapter_title("6. Cookies and Tracking")
    pdf.chapter_body("""
We use cookies for:
- Authentication and session management
- Preferences and settings
- Analytics and performance monitoring
- Advertising and marketing

You can control cookies through browser settings. Disabling cookies may limit functionality.

Third-party cookies: Google Analytics, payment processors, social media widgets.
""")
    
    pdf.chapter_title("7. Data Retention")
    pdf.chapter_body("""
Account Information: Retained while account is active plus 2 years
Transaction Records: 7 years for tax and legal compliance
Support Tickets: 3 years after resolution
Marketing Data: Until you opt-out or 5 years of inactivity
Analytics Data: Aggregated data retained indefinitely

You can request earlier deletion by contacting us.
""")
    
    pdf.chapter_title("8. Children's Privacy")
    pdf.chapter_body("""
Our services are not directed to children under 13. We do not knowingly collect information from children under 13.

If we discover we have collected information from a child under 13, we will delete it immediately.

Parents can contact privacy@techsupport.com with concerns.
""")
    
    pdf.chapter_title("9. International Data Transfers")
    pdf.chapter_body("""
Your information may be transferred to and processed in countries other than your own.

We ensure adequate protection through:
- Standard contractual clauses
- Privacy Shield certification (where applicable)
- Adequacy decisions by regulatory authorities
""")
    
    pdf.chapter_title("10. Contact Us")
    pdf.chapter_body("""
Privacy Officer: privacy@techsupport.com
Data Protection Officer (EU): dpo-eu@techsupport.com
Mail: TechSupport Solutions Inc., Privacy Department, 123 Tech Street, San Francisco, CA 94105
Phone: 1-800-PRIVACY
""")
    
    pdf.output(os.path.join(OUTPUT_DIR, "privacy_policy.pdf"))
    print("Created privacy_policy.pdf")

def create_terms_of_service():
    pdf = PolicyPDF()
    pdf.add_page()
    
    pdf.chapter_title("Terms of Service")
    pdf.chapter_body("Effective Date: January 1, 2026")
    
    pdf.chapter_title("1. Acceptance of Terms")
    pdf.chapter_body("""
By accessing or using TechSupport Solutions services, you agree to be bound by these Terms of Service and all applicable laws and regulations.

If you do not agree with any part of these terms, you may not use our services.

These terms apply to all visitors, users, and customers.
""")
    
    pdf.chapter_title("2. Account Registration")
    pdf.chapter_body("""
To use certain features, you must register for an account:
- You must be at least 18 years old
- Provide accurate and complete information
- Maintain security of your password
- Notify us immediately of unauthorized access
- You are responsible for all activities under your account

Accounts are non-transferable. One person per account.
""")
    
    pdf.chapter_title("3. Subscription Plans")
    pdf.chapter_body("""
Standard Tier: $19.99/month
- Basic support (24-hour response time)
- Access to knowledge base
- Email support

Premium Tier: $49.99/month
- Priority support (4-hour response time)
- Phone support
- Live chat access
- Extended return period

Enterprise Tier: Custom pricing
- Dedicated account manager
- 1-hour response time
- Custom integrations
- SLA guarantees
""")
    
    pdf.chapter_title("4. Billing and Payment")
    pdf.chapter_body("""
Subscriptions billed monthly or annually in advance.
Payment methods: Credit card, PayPal, bank transfer (Enterprise only).

Auto-renewal: Subscriptions automatically renew unless cancelled 24 hours before renewal.
Price changes: 30-day advance notice for price increases.
Failed payments: Account suspended after 7 days, terminated after 30 days.
""")
    
    pdf.chapter_title("5. Cancellation and Termination")
    pdf.chapter_body("""
You may cancel anytime from account settings.
No refunds for partial months (except where required by law).
Access continues until end of current billing period.

We may terminate accounts for:
- Violation of terms
- Fraudulent activity
- Non-payment
- Abusive behavior toward staff

Upon termination, you lose access to all data after 30-day grace period.
""")
    
    pdf.chapter_title("6. Acceptable Use Policy")
    pdf.chapter_body("""
You agree NOT to:
- Violate laws or regulations
- Infringe intellectual property rights
- Transmit malware or harmful code
- Attempt unauthorized access to systems
- Harass, abuse, or threaten others
- Use for illegal or fraudulent purposes
- Resell or redistribute services without permission
- Overload or disrupt systems

Violations may result in immediate termination without refund.
""")
    
    pdf.chapter_title("7. Intellectual Property")
    pdf.chapter_body("""
All content, features, and functionality are owned by TechSupport Solutions Inc.

Protected by copyright, trademark, and other intellectual property laws.

Limited license granted to use services for intended purposes only.
No reproduction, distribution, or derivative works without written permission.

User-generated content: You retain ownership but grant us license to use for service operation.
""")
    
    pdf.chapter_title("8. Disclaimers and Limitations")
    pdf.chapter_body("""
Services provided "AS IS" without warranties of any kind.

We do not guarantee:
- Uninterrupted or error-free service
- Complete accuracy of information
- Specific results or outcomes

Limitation of liability: Not liable for indirect, incidental, or consequential damages.
Maximum liability limited to amount paid in last 12 months.

Some jurisdictions don't allow these limitations.
""")
    
    pdf.chapter_title("9. Indemnification")
    pdf.chapter_body("""
You agree to indemnify and hold harmless TechSupport Solutions from claims arising from:
- Your use of services
- Violation of these terms
- Violation of third-party rights
- Your content or activities
""")
    
    pdf.chapter_title("10. Changes to Terms")
    pdf.chapter_body("""
We may modify these terms at any time.
Changes effective upon posting to website.
Continued use constitutes acceptance of modified terms.
Material changes: 30-day email notice to account holders.
""")
    
    pdf.chapter_title("11. Governing Law and Disputes")
    pdf.chapter_body("""
Governed by laws of State of California, USA.

Dispute resolution:
1. Contact support to resolve informally
2. Mediation (required before litigation)
3. Binding arbitration (waiver of class actions)
4. Small claims court (for eligible claims)

You have 1 year from incident to file claims.
""")
    
    pdf.chapter_title("12. Contact Information")
    pdf.chapter_body("""
Legal Department
TechSupport Solutions Inc.
123 Tech Street
San Francisco, CA 94105

Email: legal@techsupport.com
Phone: 1-800-SUPPORT
""")
    
    pdf.output(os.path.join(OUTPUT_DIR, "terms_of_service.pdf"))
    print("Created terms_of_service.pdf")

def create_support_policy():
    pdf = PolicyPDF()
    pdf.add_page()
    
    pdf.chapter_title("Customer Support Policy")
    pdf.chapter_body("Effective Date: January 1, 2026")
    
    pdf.chapter_title("1. Support Channels")
    pdf.chapter_body("""
Email Support: support@techsupport.com (All tiers)
Live Chat: Available 24/7 for Premium and Enterprise (Business hours for Standard)
Phone Support: 1-800-SUPPORT (Premium and Enterprise only)
Knowledge Base: Free access for everyone at help.techsupport.com
Community Forum: Peer-to-peer support and best practices
""")
    
    pdf.chapter_title("2. Response Time SLA")
    pdf.chapter_body("""
Standard Tier:
- Critical: 24 hours
- High: 48 hours
- Medium: 72 hours
- Low: 5 business days

Premium Tier:
- Critical: 4 hours
- High: 8 hours
- Medium: 24 hours
- Low: 48 hours

Enterprise Tier:
- Critical: 1 hour (24/7)
- High: 4 hours
- Medium: 12 hours
- Low: 24 hours

Critical = service outage affecting multiple users
High = major feature not working
Medium = partial functionality issues
Low = questions, feature requests, minor bugs
""")
    
    pdf.chapter_title("3. Support Hours")
    pdf.chapter_body("""
Standard Tier: Monday-Friday, 9 AM - 6 PM EST (excluding holidays)
Premium Tier: 24/7 via chat and email, phone 9 AM - 9 PM EST daily
Enterprise Tier: 24/7 all channels with dedicated hotline

Holidays observed: New Year's Day, Memorial Day, Independence Day, Labor Day, Thanksgiving, Christmas
""")
    
    pdf.chapter_title("4. What We Support")
    pdf.chapter_body("""
Covered:
- Product installation and setup
- Feature usage and configuration
- Troubleshooting technical issues
- Bug reports and fixes
- Account and billing questions
- Security concerns

Not Covered:
- Third-party software or integrations (unless Enterprise)
- Custom development requests
- Training beyond basic usage
- Data recovery after account deletion
- Issues caused by unauthorized modifications
""")
    
    pdf.chapter_title("5. Ticket Lifecycle")
    pdf.chapter_body("""
1. Submission: You create ticket via email, chat, or phone
2. Acknowledgment: Automated confirmation within 5 minutes
3. Assignment: Routed to appropriate team based on priority
4. Investigation: Agent reviews and may request additional information
5. Resolution: Solution provided with steps to verify
6. Confirmation: You verify issue is resolved
7. Closure: Ticket closed after confirmation or 7 days of inactivity
8. Follow-up: Satisfaction survey sent 24 hours after closure
""")
    
    pdf.chapter_title("6. Escalation Process")
    pdf.chapter_body("""
If unsatisfied with support:

Level 1: Request escalation in ticket - assigned to senior agent
Level 2: Contact supervisor at supervisor@techsupport.com
Level 3: Request manager review via escalations@techsupport.com
Level 4: Enterprise customers: Contact your account manager directly

All escalations reviewed within 24 hours (4 hours for Enterprise).
""")
    
    pdf.chapter_title("7. Remote Access")
    pdf.chapter_body("""
For complex issues, we may request remote access to your system:
- Requires your explicit permission
- Uses secure screen-sharing tools
- Session recorded for quality assurance
- You can terminate session anytime
- Only accesses relevant areas with your guidance

We never access files or data without your presence and consent.
""")
    
    pdf.chapter_title("8. Service Credits")
    pdf.chapter_body("""
If we miss SLA response times (Premium and Enterprise only):

Missed by 2x: 10% service credit
Missed by 3x: 25% service credit
Missed by 4x or more: 50% service credit

Credits applied to next invoice automatically.
Must be claimed within 30 days of incident.
Maximum 100% credit per month.
""")
    
    pdf.chapter_title("9. Best Practices for Tickets")
    pdf.chapter_body("""
To expedite resolution, please:
- Provide detailed description of issue
- Include steps to reproduce problem
- Attach screenshots or error messages
- Specify which product/feature affected
- Mention any recent changes to your setup
- Include account email or order number

Clear information = faster resolution!
""")
    
    pdf.chapter_title("10. Contact Support")
    pdf.chapter_body("""
Email: support@techsupport.com
Phone: 1-800-SUPPORT (1-800-787-7678)
Chat: Available at techsupport.com (click chat icon)
Portal: Login at support.techsupport.com to view tickets
Emergency (Enterprise): emergency@techsupport.com or call hotline
""")
    
    pdf.output(os.path.join(OUTPUT_DIR, "support_policy.pdf"))
    print("Created support_policy.pdf")

if __name__ == "__main__":
    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        print("Generating comprehensive policy documents...")
        print("="*60)
        
        create_refund_policy()
        create_privacy_policy()
        create_terms_of_service()
        create_support_policy()
        
        print("="*60)
        print("All policy documents generated successfully!")
        print(f"Location: {OUTPUT_DIR}")
    except Exception as e:
        print(f"Error: {e}")
