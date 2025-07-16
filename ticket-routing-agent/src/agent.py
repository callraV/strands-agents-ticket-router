import logging
from typing import List, Dict, Any

from strands import Agent, tool # strands agent framework
from strands.models import BedrockModel # LLM model
from strands_tools import current_time, calculator # tools

from .gmail_handler import GmailHandler
from .ticket_analyzer import TicketAnalyzer

# configure logging
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

    def __init__(self, region: str = 'ap-southeast-1', profile_name: str = 'default'):
        self.region = region
        self.profile_name = profile_name
        self.gmail_handler = GmailHandler()
        self.ticket_analyzer = TicketAnalyzer()
        self.agent = self._create_agent()
        self.tickets = []
        self.summary = {}

    def _create_agent(self) -> Agent:

        # --- define LLM model ---
        bedrock_model = BedrockModel(
            model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",
            region_name=self.region,
            profile_name=self.profile_name,
            temperature=0.2
        )

        # --- define tools ---
        # these are methods that can only be called through the agent.
        # agent can call class methods by redefining the method as a @tool.
        @tool
        def get_all_inbox() -> List[Dict[str, Any]]:
            """
            Get all emails from the user's Gmail inbox.
            """
            return self.gmail_handler.get_all_inbox_emails()
        
        @tool
        def get_tickets() -> List[Dict[str, Any]]:
            """
            Scan Gmail for bug-related tickets.
            """
            return self.scan_gmail()
        
        @tool
        def forward_tickets(tickets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
            """
            Forward classified tickets to their respective departments.
            """
            return self.forward_tickets(tickets)
    

        # --- create agent ---
        agent = Agent(
            model=bedrock_model,
            tools=[
                # current_time, # default strands tool
                calculator, # default strands tool
                get_all_inbox, # custom tool
                get_tickets, # custom tool
                forward_tickets, # custom tool
            ],
            system_prompt="""
            You are a Ticket Classification and Routing Assistant. Your role is to assist in
            identifying and classifying bug reports found in email messages. You can:

            1. Scan Gmail for bug-related tickets.
            2. Analyze and classify tickets based on their content.
            3. Summarize tickets and provide a report.
            4. Forward tickets to the relevant department (frontend, backend, sysops, or cross-functional), if prompted by the user.

            Start by asking what the user needs help with if they haven't specified a task.
            """
        )

        return agent

    # --- define class methods ---
    # these methods can be called directly.
    def scan_gmail(self) -> List[Dict[str, Any]]:
        if not self.gmail_handler.authenticate():
            logger.error("Gmail authentication failed. Check credentials.")
            return []

        logger.info(f"Scanning inbox for bug-related tickets...")

        tickets = self.gmail_handler.query_inbox_for_ticket()

        self.processed_tickets = []

        for ticket in tickets:
            issue_summary = self.gmail_handler.extract_issue_summary(ticket)
            ticket['summary'] = issue_summary

            self.processed_tickets.append(ticket)

        self.tickets = self.ticket_analyzer.summarize_tickets(self.processed_tickets)
        self.summary = self.ticket_analyzer.generate_ticket_report(self.tickets)

        return self.tickets
    
    
    def forward_tickets(self, tickets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
      
        self.forwarded_tickets = self.gmail_handler.forward_classified_emails(tickets)
        self.forwarded_tickets_report = "\n".join(self.forwarded_tickets)

        logger.info(f"Forwarded Tickets: \n{self.forwarded_tickets_report}") 

        return self.forwarded_tickets
