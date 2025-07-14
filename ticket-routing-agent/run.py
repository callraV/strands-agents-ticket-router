#!/usr/bin/env python3
import os
import sys
import argparse
import colorama
from colorama import Fore

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
    agent = TicketRoutingAgent(region=args.region, profile_name=args.profile).agent

    if not agent:
        print(f"{Fore.RED}✗ Failed to initialize agent. Check your configuration.")
        sys.exit(1)

    print(f"{Fore.GREEN}✓ Agent initialized successfully. Starting session...")

    # Interactive prompt loop
    while True:
        user_input = input(f"\n{Fore.MAGENTA}Prompt (quit by entering q): ").strip().lower()

        if user_input.lower() in ['q', 'quit', 'exit']:
            print(f"{Fore.GREEN}See you next time!")
            break
        else:
            print(f"\n")
            agent(f"{user_input}").message

if __name__ == "__main__":
    main()
