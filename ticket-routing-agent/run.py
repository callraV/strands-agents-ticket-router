#!/usr/bin/env python3
import os
import sys
import argparse
import colorama
from colorama import Fore
from tabulate import tabulate

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

from src.agent import TicketRoutingAgent

colorama.init(autoreset=True)

def print_banner():
    banner = f"""
{Fore.CYAN}═════════════════════════════════════════════════════
{Fore.CYAN}                                              
{Fore.CYAN}      {Fore.WHITE}Ticket Classification and Routing Assistant
{Fore.CYAN}          {Fore.WHITE}Made by Aura Vanya (callraV)      
{Fore.CYAN}                 {Fore.WHITE}Powered by AWS          
{Fore.CYAN}                                         
{Fore.CYAN}═════════════════════════════════════════════════════
"""
    print(banner)

def format_date(date_obj):
    if date_obj is None:
        return "N/A"
    return date_obj.strftime("%Y-%m-%d")

def main():
    parser = argparse.ArgumentParser(description='Ticket Routing Agent')
    parser.add_argument('--region', type=str, default='us-east-1', help='AWS region for Bedrock')
    parser.add_argument('--profile', type=str, default='default', help='AWS profile name')
    parser.add_argument('--export', type=str, help='Path to export CSV results')
    args = parser.parse_args()

    print_banner()

    print(f"{Fore.WHITE}Initializing Ticket Routing Agent...")
    agent = TicketRoutingAgent(region=args.region, profile_name=args.profile)

    print(f"{Fore.WHITE}Authenticating with Gmail...")
    if not agent.gmail_handler.authenticate():
        print(f"{Fore.RED}Authentication failed. Check your OAuth setup.")
        sys.exit(1)
    
    print(f"{Fore.CYAN}Scanning Gmail for bugs reported...")

    try:
        tickets = agent.scan_gmail()
    except Exception as e:
        print(f"{Fore.RED}Scan failed: {e}")
        sys.exit(1)

    if not tickets:
        print(f"{Fore.YELLOW}No bug-related emails found.")
        return

    print(f"{Fore.GREEN}✓ Scan complete. Found {len(tickets)} ticket(s).\n")

    print(f"{Fore.CYAN}🛠 Ticket Classification Results:\n")

    table_data = []
    for ticket in tickets:
        table_data.append([
            ticket.get('subject', 'N/A')[:50],
            ticket.get('category', 'Unknown'),
            ticket.get('is_urgent', 'Unknown'),
            ticket.get('timestamp', 'Unknown'),
            ticket.get('from', 'Unknown'),
            # ticket.get('forward_to', 'Unknown') # show forwarded department - optional

        ])

    print(tabulate(
        table_data,
        headers=[
            "Subject",
            "Bug Type",
            "Urgent",
            "Timestamp",
            "Reported By",
            # "Forward To" # show forwarded department - optional
            ],
        tablefmt="fancy_grid"
    ))

    if args.export:
        export_path = args.export if args.export.endswith('.csv') else f"{args.export}.csv"
        if agent.export_to_csv(export_path):
            print(f"\n{Fore.GREEN}✓ Exported results to {export_path}")
        else:
            print(f"\n{Fore.RED}✗ Failed to export results to CSV")

if __name__ == "__main__":
    main()
