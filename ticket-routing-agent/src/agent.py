import logging
from datetime import datetime
from typing import List, Dict, Any

from strands import Agent
from strands.models import BedrockModel

from .gmail_handler import GmailHandler
from .ticket_analyzer import TicketAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('ticket_routing_agent')

class TicketRoutingAgent:
    """
    A Strands agent for scanning Gmail, classifying bug-related tickets, and forwarding them to the relevant department.
    """

    def __init__(self, region: str = 'us-east-1', profile_name: str = 'default'):
        self.region = region
        self.profile_name = profile_name
        self.gmail_handler = GmailHandler()
        self.ticket_analyzer = TicketAnalyzer()
        self.agent = self._create_agent()
        self.tickets = []
        self.summary = {}

    def _create_agent(self) -> Agent:
        bedrock_model = BedrockModel(
            model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",
            region_name=self.region,
            profile_name=self.profile_name,
            temperature=0.2
        )

        agent = Agent(
            model=bedrock_model,
            tools=[
                self.gmail_handler,
                self.ticket_analyzer
            ],
            system_prompt="""
            You are a Ticket Classification and Routing Assistant. Your role is to assist in
            identifying and classifying bug reports found in email messages. Use specific
            keywords and context to determine the relevant department (frontend, backend,
            sysops, or cross-functional). Analyzed emails will be routed as tickets to the
            relevant department based on the classification.

            Your output should be concise, well-structured, and informative for triage purposes.
            """
        )

        return agent

    def scan_gmail(self) -> List[Dict[str, Any]]:
        if not self.gmail_handler.authenticate():
            logger.error("Gmail authentication failed. Check credentials.")
            return []

        logger.info(f"Scanning inbox for bug-related tickets...")

        all_inbox_emails = self.gmail_handler.get_all_inbox_emails()
        tickets = self.gmail_handler.query_inbox_for_ticket()

        self.processed_tickets = []

        for ticket in tickets:
            issue_summary = self.gmail_handler.extract_issue_summary(ticket)
            ticket['summary'] = issue_summary
            
            # # logs reasoning - optional
            # analysis_result = self.agent(f"Analyze and classify this issue email: {email_content[:5000]}").message
            # email['agent_analysis'] = analysis_result
            # logger.info(f"Analysis result: {analysis_result}")

            self.processed_tickets.append(ticket)

        self.tickets = self.ticket_analyzer.summarize_tickets(self.processed_tickets)
        self.summary = self.ticket_analyzer.generate_ticket_report(self.tickets)
        self.forwarded_tickets = self.gmail_handler.forward_classified_emails(self.tickets)
        self.forwarded_tickets_report = "\n".join(self.forwarded_tickets)

        logger.info(f"Found {len(all_inbox_emails)} emails in inbox")
        logger.info(f"Out of which, {len(tickets)} potential bug tickets were identified")

        logger.info(f"Forwarded Tickets: \n{self.forwarded_tickets_report}") 

        logger.info(f"Summary:{self.summary}")
        # logger.info(f"Tickets: {self.tickets}") # for debugging

        return self.tickets

    def export_to_csv(self, filepath: str) -> bool:
        if not self.tickets:
            logger.warning("No ticket data to export")
            return False

        try:
            import csv

            with open(filepath, 'w', newline='') as csvfile:
                fieldnames = [
                    'subject', 'from', 'date', 'summary', 'department', 'timestamp'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for ticket in self.tickets:
                    row = {field: ticket.get(field, '') for field in fieldnames}
                    if isinstance(row['date'], datetime):
                        row['date'] = row['date'].strftime('%Y-%m-%d')
                    writer.writerow(row)

            logger.info(f"Exported ticket data to {filepath}")
            return True

        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            return False
