import os
import base64
from pathlib import Path
from typing import List, Dict, Any

import html2text
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

import base64
from email.mime.text import MIMEText

# Define the scopes required for Gmail API
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly', # Read emails for classification
    'https://www.googleapis.com/auth/gmail.compose',  # Compose and send forwarded emails
]


class GmailHandler:
    """ 
    A class to handle Gmail API authentication, scan for bug tickets, and forward tickets to relevant departments.
    """
    
    def __init__(self, credentials_path: str = None, token_path: str = None):
        """
        Initialize the agent for classifying bug tickets into development departments.
        
        Args:
            credentials_path: Path to the credentials.json file
            token_path: Path to the token.json file
        """

        self.credentials_path = credentials_path or os.path.join(
            Path(__file__).parent.parent, 'config', 'credentials.json'
        )
        self.token_path = token_path or os.path.join(
            Path(__file__).parent.parent, 'config', 'token.json'
        )
        self.service = None

        # Define search queries for finding bug report emails
        self.ticket_queries = [
            "bug",
            "issue",
            "problem",
            "error",
            "not working",
            "fails",
            "broken",
            "crash",
            "down",
            "support request",
            "help needed",
            "502",
            "500",
            "slow loading",
            "timeout",
            "page not loading",
            "site is down"
        ]
        
        # Define keywords or categories to help classify tickets
        self.classification_keywords = {
            'frontend': ['button', 'UI', 'UX', 'click', 'design', 'layout', 'form', 'link'],
            'backend': ['API', 'database', 'query', 'data mismatch', 'server error', 'slow response'],
            'sysops': ['502', '504', 'server down', 'timeout', 'infrastructure', 'deployment'],
            'cross': ['unknown error', 'upload issue', 'dashboard broken', 'mixed symptoms']
        }

    ### Authenticate Email ###
    
    def authenticate(self) -> bool:
        """
        Authenticate with the Gmail API using OAuth2.
        
        Returns:
            bool: True if authentication was successful, False otherwise
        """
        creds = None
        
        # Check if token.json exists with valid credentials
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_info(
                eval(open(self.token_path, 'r').read()), SCOPES
            )
        
        # If credentials don't exist or are invalid, refresh or get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    return False
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for future use
            with open(self.token_path, 'w') as token:
                token.write(str(creds.to_json()))
        
        # Build the Gmail API service
        self.service = build('gmail', 'v1', credentials=creds)
        return True
    
    ### Retrieve Emails from Inbox ###
    
    def extract_email_content(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract relevant content from an email message.
        
        Args:
            message: Gmail API message object
            
        Returns:
            Dictionary with extracted email content
        """
        headers = {header['name']: header['value'] for header in message['payload']['headers']}
        
        # Extract basic email metadata
        email_data = {
            'id': message['id'],
            'thread_id': message['threadId'],
            'subject': headers.get('Subject', ''),
            'from': headers.get('From', ''),
            'to': headers.get('To', ''),
            'date': headers.get('Date', ''),
            'timestamp': int(message['internalDate']) / 1000,  # Convert to seconds
            'body_text': '',
            'body_html': ''
        }
        
        # Extract email body
        if 'parts' in message['payload']:
            for part in message['payload']['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        email_data['body_text'] = base64.urlsafe_b64decode(
                            part['body']['data']).decode('utf-8')
                elif part['mimeType'] == 'text/html':
                    if 'data' in part['body']:
                        email_data['body_html'] = base64.urlsafe_b64decode(
                            part['body']['data']).decode('utf-8')
        elif 'body' in message['payload'] and 'data' in message['payload']['body']:
            # Handle single-part messages
            data = message['payload']['body']['data']
            decoded_data = base64.urlsafe_b64decode(data).decode('utf-8')
            
            if message['payload']['mimeType'] == 'text/plain':
                email_data['body_text'] = decoded_data
            elif message['payload']['mimeType'] == 'text/html':
                email_data['body_html'] = decoded_data
        
        # If we have HTML but no plain text, convert HTML to text
        if not email_data['body_text'] and email_data['body_html']:
            h = html2text.HTML2Text()
            h.ignore_links = False
            email_data['body_text'] = h.handle(email_data['body_html'])
        
        return email_data
               
    def get_all_inbox_emails(self):
        """
        Retrieve all emails currently in the user's inbox.

        Returns:
            List[Dict[str, Any]]: List of email message dictionaries.
        """
        try:
            response = self.service.users().messages().list(userId='me', labelIds=['INBOX']).execute()
            
            messages = response.get('messages', [])
            detailed_messages = []

            for message in messages:
                msg = self.service.users().messages().get(
                    userId='me', id=message['id'], format='full'
                ).execute()
                detailed_messages.append(msg)

            return detailed_messages

        except Exception as e:
            print(f"An error occurred: {e}")
            return -100

    def query_inbox_for_ticket(self) -> List[Dict[str, Any]]:
        """
        Scan Gmail for bug ticket-related emails.

        Args:
            days_back: Number of days back to search
            max_results: Maximum number of results per query

        Returns:
            List of ticket-related emails
        """
        all_queried_emails = []
        all_inbox_emails = self.get_all_inbox_emails()

        # Search using bug/ticket-related queries
        for email in all_inbox_emails:
            extracted_email = self.extract_ticket_content(email)

            body_text = extracted_email.get('body_text', '').lower()
            subject = extracted_email.get('subject', '').lower()

            for query in self.ticket_queries:
                if query.lower() in subject:
                    all_queried_emails.append(extracted_email)
                elif query.lower() in body_text:
                    all_queried_emails.append(extracted_email)
        
        unique_queried_emails = self.filter_duplicate_emails(all_queried_emails)
        return unique_queried_emails

    def filter_duplicate_emails(self, email_data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        seen_ids = set()
        unique_emails = []

        for email in email_data_list:
            if email['id'] not in seen_ids:
                seen_ids.add(email['id'])
                unique_emails.append(email)

        return unique_emails

    
    def extract_ticket_content(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract relevant content from an email message.
        
        Args:
            message: Gmail API message object
            
        Returns:
            Dictionary with extracted email content
        """
        headers = {header['name']: header['value'] for header in message['payload']['headers']}
        
        # Extract basic email metadata
        email_data = {
            'id': message['id'],
            'thread_id': message['threadId'],
            'subject': headers.get('Subject', ''),
            'from': headers.get('From', ''),
            'to': headers.get('To', ''),
            'date': headers.get('Date', ''),
            'timestamp': int(message['internalDate']) / 1000,  # Convert to seconds
            'body_text': '',
            'body_html': ''
        }
        
        # Extract email body
        if 'parts' in message['payload']:
            for part in message['payload']['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        email_data['body_text'] = base64.urlsafe_b64decode(
                            part['body']['data']).decode('utf-8')
                elif part['mimeType'] == 'text/html':
                    if 'data' in part['body']:
                        email_data['body_html'] = base64.urlsafe_b64decode(
                            part['body']['data']).decode('utf-8')
        elif 'body' in message['payload'] and 'data' in message['payload']['body']:
            # Handle single-part messages
            data = message['payload']['body']['data']
            decoded_data = base64.urlsafe_b64decode(data).decode('utf-8')
            
            if message['payload']['mimeType'] == 'text/plain':
                email_data['body_text'] = decoded_data
            elif message['payload']['mimeType'] == 'text/html':
                email_data['body_html'] = decoded_data
        
        # If we have HTML but no plain text, convert HTML to text
        if not email_data['body_text'] and email_data['body_html']:
            h = html2text.HTML2Text()
            h.ignore_links = False
            email_data['body_text'] = h.handle(email_data['body_html'])
        
        return email_data
    
    def extract_issue_summary(self, email_data: Dict[str, Any]) -> str:
        """
        Extract a short summary or key issue description from the email.

        Args:
            email_data: Email data dictionary

        Returns:
            A brief issue summary string
        """
        email_content = email_data.get('body_text', '')

        if not email_content:
            return
        
        subject = email_data.get('subject', '').strip()
        snippet = email_data.get('snippet', '').strip()
        
        # Prioritize subject line if informative
        if subject and any(keyword in subject.lower() for keyword in ['bug', 'issue', 'error', 'problem', 'not working']):

            return subject

        # Otherwise, try to extract a meaningful snippet
        if snippet:
            return snippet[:200]  # Truncate for brevity

        return "No clear issue summary available"
    
    ### Forward Emails to Departments ###

    def forward_classified_emails(self, emails):
        """
        Forwards each email to its respective department(s) using Gmail's 'compose' API.
        
        Args:
            emails: List of email dictionaries.
        """

        forwarded_emails = []

        for email in emails:
            forward_to = email.get('forward_to', [])

            if not forward_to:
                continue
            
            original_subject = email.get('subject', '(No Subject)')
            original_sender = email.get('from', 'Unknown')
            email_id = email.get('id', 'Unknown ID')
            body = email.get('body', '')
            urgent = "URGENT -" if email.get('is_urgent') is True else "-"

            # Compose the forwarded content
            forwarded_body = (
                f"Forwarded message from: {original_sender}\n"
                f"Subject: {original_subject}\n"
                f"Ticket ID: {email_id}\n\n"
                f"{body}"
            )
        
            for recipient in forward_to:
                try:
                    raw = self.create_raw_email(
                        to=recipient,
                        subject=f"[FORWARDED] {urgent} {original_subject}",
                        body=forwarded_body
                    )

                    self.service.users().messages().send(
                        userId='me',
                        body={'raw': raw}
                    ).execute()

                    forwarded_emails.append(f"'{original_subject}' to {recipient} - ✓ Forwarded successfully")
                except Exception as e:
                    forwarded_emails.append(f"'{original_subject}' to {recipient} - ✗ Failed to forward: {e}")

        return forwarded_emails

    def create_raw_email(self, to, subject, body):
        """
            Helper to create a raw base64-encoded email message string.
        """

        mime_msg = MIMEText(body)
        mime_msg['to'] = to
        mime_msg['subject'] = subject

        raw = base64.urlsafe_b64encode(mime_msg.as_bytes()).decode()
        return raw
