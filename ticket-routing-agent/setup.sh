#!/bin/bash

# ANSI color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=======================================${NC}"
echo -e "${BLUE}\nSetup Begins..."


# Check if Python 3 is installed
if command -v python3 &>/dev/null; then
    echo -e "${BLUE}\nChecking python version..."
    echo -e "${GREEN}✓ Python 3 is installed${NC}"
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    # Check if 'python' is Python 3
    PY_VERSION=$(python --version 2>&1)
    if [[ $PY_VERSION == *"Python 3"* ]]; then
        echo -e "${GREEN}✓ Python 3 is installed${NC}"
        PYTHON_CMD="python3"
    else
        echo -e "${RED}✗ Python 3 is required but not found${NC}"
        exit 1
    fi
else
    echo -e "${RED}✗ Python 3 is required but not found${NC}"
    exit 1
fi

# Install dependencies
echo -e "\n${BLUE}Installing dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Failed to install dependencies${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Check for AWS credentials
echo -e "\n${BLUE}Checking AWS credentials...${NC}"
if [ -f ~/.aws/credentials ] || [ -f ~/.aws/config ]; then
    echo -e "${GREEN}✓ AWS credentials found${NC}"
    
    # Check if AWS CLI is installed
    if command -v aws &>/dev/null; then
        echo -e "${GREEN}✓ AWS CLI is installed${NC}"
        
        # Check if default profile exists and has credentials
        if aws sts get-caller-identity --profile default &>/dev/null; then
            echo -e "${GREEN}✓ AWS default profile is configured${NC}"
            AWS_REGION=$(aws configure get region --profile default)
            if [ -z "$AWS_REGION" ]; then
                echo -e "${YELLOW}⚠ AWS region not set in default profile${NC}"
                echo -e "${YELLOW}⚠ Using us-east-1 as default region${NC}"
            else
                echo -e "${GREEN}✓ AWS region is set to: $AWS_REGION${NC}"
            fi
        else
            echo -e "${YELLOW}⚠ AWS default profile not configured or invalid${NC}"
            echo -e "${YELLOW}⚠ You may need to run 'aws configure' to set up your credentials${NC}"
        fi
    else
        echo -e "${YELLOW}⚠ AWS CLI not found. Consider installing it for better AWS integration${NC}"
    fi
else
    echo -e "${YELLOW}⚠ AWS credentials not found${NC}"
    echo -e "${YELLOW}⚠ You may need to run 'aws configure' to set up your credentials${NC}"
fi

# Create necessary directories if they don't exist
echo -e "\n${BLUE}Ensuring all directories exist...${NC}"
mkdir -p src config
echo -e "${GREEN}✓ Directory structure verified${NC}"

# Gmail API setup instructions
echo -e "\n${BLUE}Gmail API Setup Instructions:${NC}"
echo -e "${YELLOW}1. Go to https://console.developers.google.com/${NC}"
echo -e "${YELLOW}2. Create a new project${NC}"
echo -e "${YELLOW}3. Enable the Gmail API${NC}"
echo -e "${YELLOW}4. Create OAuth 2.0 credentials (Desktop application)${NC}"
echo -e "${YELLOW}5. Download the credentials.json file${NC}"
echo -e "${YELLOW}6. Place the credentials.json file in the config/ directory${NC}"

echo -e "\n${GREEN}Setup complete! You can now run the agent with:${NC}"
echo -e "${BLUE}python run.py${NC}"

# Make the script executable
chmod +x run.py

echo -e "\n${BLUE}=======================================${NC}"
