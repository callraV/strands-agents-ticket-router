# Ticket Classification and Routing Assistant

This is a Ticket Classification and Routing Assistant. It assists in identifying and classifying bug reports found in email messages by using specific keywords and context to determine the relevant department (frontend, backend, sysops, or cross-functional). Analyzed emails will be routed to the relevant department based on the classification.

## Features

- **Gmail Integration**: Securely connects to your Gmail account to scan for bug report emails
- **Bug Detection**: Identifies and extracts bug reports from incoming emails
- **Department Classification**: Uses keywords and context to classify bugs as frontend, backend, sysops, or cross-functional
- **Urgency Classification**: Use keywords and context to classify bugs as urgent or not urgent
- **Automated Forwarding**: Forwards analyzed bug reports to the relevant department
- **Contextual Analysis**: Considers email content and attachments for accurate classification

## Prerequisites

- Python 3.8+
- AWS account with access to Bedrock
- Gmail account with OAuth credentials

## Installation and Usage

1. Setup a virtual python environment

2. Open Git Bash and cd to ticket-routing-agent:

   ```
   cd ticket-routing-agent
   ```

3. Run the setup script:

   ```
   ./setup.sh
   ```

4. Set up Gmail API credentials:

   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Enable the Gmail API
   - Create OAuth 2.0 credentials (Desktop application)
   - Download the credentials.json file
   - Place it in the `config/` directory

5. Run the agent with:

   ```
   python run.py
   ```

## How It Works

1. **Authentication**: Securely connects to your Gmail account using OAuth2
2. **Email Scanning**: Searches for emails containing bug reports
3. **Bug Classification**: Analyzes email content to classify the bug and determine its urgency and relevant department
4. **Forwarding**: Forwards the bug report to the appropriate department

## Project Structure

```
ticket-routing-agent/
├── config/
│   ├── credentials.json    # Gmail API credentials
│   └── token.json          # Gmail API token: auto-generated after initial run
├── src/
│   ├── __init__.py
│   ├── agent.py            # Agent implementation
│   ├── gmail_handler.py    # Gmail API integration and email handling
│   └── ticket_analyzer.py  # Bug classification logic
├── requirements.txt        # Project dependencies
├── run.py                  # CLI interface
├── setup.sh                # Installation script
├── LICENSE                 # MIT license
└── README.md               # This file
```

## Security

This application:

- Uses OAuth 2.0 for Gmail authentication (no password storage)
- Stores authentication tokens locally in your config directory
- Requests read and compose access to your Gmail

## License

This project is licensed under the [MIT License](LICENSE)
