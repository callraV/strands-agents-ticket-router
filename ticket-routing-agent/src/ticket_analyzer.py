import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple

class TicketAnalyzer:
    """
    A class to analyze support ticket data extracted from emails.
    """

    # Email addresses for department support
    frontend_support_email = "frontend@fakemail.com"
    backend_support_email = "backend@fakemail.com"
    sysops_support_email = "sysops@fakemail.com"

    def __init__(self):
        """
        Initialize the TicketAnalyzer.
        """

        # Define department categories for ticket classification
        self.issue_categories = {
            'frontend': [
                'ui', 'ux', 'layout', 'button', 'form validation', 'design', 'style',
                'visual', 'alignment', 'text overflow', 'mobile view', 'responsive', 
                'dropdown', 'checkbox', 'radio button', 'modal', 'link not working'
            ],
            'backend': [
                'api', 'data mismatch', 'data error', 'processing error', 'database', 
                'data inconsistency', 'query error', 'logic bug', 'long loading time',
                'backend crash', 'json error', '500 error'
            ],
            'sysops': [
                'server', 'downtime', 'deployment', 'dns', 'infrastructure', 
                'unable to connect', 'timeout', 'network issue', 'ssl error',
                'hosting', 'latency', 'maintenance', 'outage', '502', '504', 'bad gateway'
            ],
            'cross_functional': [
                'slowness', 'intermittent issue', 'frontend triggers backend crash',
                'authentication error affecting UI', 'mixed origin issue', 
                'combined api and ui failure', 'user action leads to server error',
                'redirect loops involving infra', 'complex failure', 'timeout after form submission'
            ]
        }


    def classify_ticket(self, subject: str, body: str) -> str:
        """
        Classify a support ticket into a category based on subject and body content.

        Args:
            subject: The email subject
            body: The email body content

        Returns:
            A string representing the issue category
        """
        text = f"{subject} {body}".lower()

        for category, keywords in self.issue_categories.items():
            for keyword in keywords:
                if keyword in text:
                    return category.title()

        return "Cross-Functional"
    
    def classify_department(self, category: str):
        """
        Classify a support ticket into a category based on subject and body content.

        Args:
            subject: The email subject
            body: The email body content

        Returns:
            A string representing the issue category
        """

        forward_to = []

        if category in 'Frontend':
            forward_to.append(self.frontend_support_email);
        elif category in 'Backend':
            forward_to.append(self.backend_support_email);
        elif category in 'Sysops':
            forward_to.append(self.sysops_support_email);
        elif category in 'Cross-Functional':
            forward_to.append(self.frontend_support_email)
            forward_to.append(self.backend_support_email)
            forward_to.append(self.sysops_support_email)
        
        return forward_to

    def is_urgent(self, subject: str, body: str) -> bool:
        """
        Determine if a ticket is urgent based on specific keywords.

        Args:
            subject: Email subject
            body: Email body

        Returns:
            Boolean indicating urgency
        """
        urgent_keywords = ['urgent', 'asap', 'immediately', 'critical', 'important', 'high priority', '500', '502', 'crash']
        combined = f"{subject} {body}".lower()
        return any(word in combined for word in urgent_keywords)

    def summarize_tickets(self, emails: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze and categorize a list of support ticket emails.

        Args:
            emails: List of email data dictionaries

        Returns:
            List of ticket summaries
        """
        tickets = []
        for email in emails:
            subject = email.get('subject', '')
            body = email.get('body_text', '')
            timestamp = datetime.fromtimestamp(email.get('timestamp', 0))

            category = self.classify_ticket(subject, body)
            is_urgent = self.is_urgent(subject, body)

            ticket = {
                'id': email.get('id'),
                'subject': subject,
                'category': category,
                'is_urgent': is_urgent,
                'timestamp': timestamp,
                'from': email.get('from'),
                'forward_to': self.classify_department(category),
                'body': body,
            }
            tickets.append(ticket)

        return tickets

    def generate_ticket_report(self, tickets: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate summary statistics and insights from ticket data.

        Args:
            tickets: List of ticket summaries

        Returns:
            A report dictionary
        """
        total = len(tickets)
        category_counts = {}
        urgent_count = 0

        for ticket in tickets:
            category = ticket['category']
            if category not in category_counts:
                category_counts[category] = 0
            category_counts[category] += 1

            if ticket['is_urgent']:
                urgent_count += 1

        return {
            'total_tickets': total,
            'category_breakdown': category_counts,
            'urgent_tickets': urgent_count,
        }
