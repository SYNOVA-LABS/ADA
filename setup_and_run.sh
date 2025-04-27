#!/bin/bash

# Define text colors for better readability
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Print ADA banner
echo -e "${BLUE}"
echo "    _    ____    _    "
echo "   / \\  |  _ \\  / \\   "
echo "  / _ \\ | | | |/ _ \\  "
echo " / ___ \\| |_| / ___ \\ "
echo "/_/   \\_\\____/_/   \\_\\"
echo -e "${NC}"
echo -e "${GREEN}Advanced Digital Agent - Setup and Run Script${NC}\n"

# Function to check if command succeeded
check_status() {
    if [ $? -ne 0 ]; then
        echo -e "${RED}ERROR: $1 failed. Exiting.${NC}"
        exit 1
    fi
}

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# 1. Create and activate virtual environment
echo -e "${YELLOW}Step 1/5: Setting up virtual environment...${NC}"
if [ ! -d "venv" ]; then
    echo "Creating new virtual environment..."
    python3 -m venv venv
    check_status "Virtual environment creation"
else
    echo "Virtual environment already exists."
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
check_status "Virtual environment activation"
echo -e "${GREEN}Virtual environment activated successfully.${NC}\n"

# 2. Install requirements
echo -e "${YELLOW}Step 2/5: Installing requirements...${NC}"
pip install -r requirements.txt
check_status "Requirements installation"
echo -e "${GREEN}Requirements installed successfully.${NC}\n"

# 3. Download Vosk speech recognition model if needed
echo -e "${YELLOW}Step 3/5: Setting up Vosk speech recognition model...${NC}"
# Define model directory (adjust if needed based on your code)
MODEL_DIR="models"
VOSK_MODEL_DIR="$MODEL_DIR/vosk-model-small-en-us-0.15"

# Create models directory if it doesn't exist
if [ ! -d "$MODEL_DIR" ]; then
    mkdir -p "$MODEL_DIR"
fi

# Check if Vosk model already exists
if [ ! -d "$VOSK_MODEL_DIR" ]; then
    echo "Downloading Vosk speech recognition model..."
    # Download and extract the model
    curl -L https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip -o "$MODEL_DIR/vosk-model.zip"
    check_status "Model download"
    
    unzip -q "$MODEL_DIR/vosk-model.zip" -d "$MODEL_DIR"
    check_status "Model extraction"
    
    # Clean up zip file
    rm "$MODEL_DIR/vosk-model.zip"
    
    echo -e "${GREEN}Vosk model downloaded and extracted successfully.${NC}\n"
else
    echo -e "${GREEN}Vosk model already exists.${NC}\n"
fi

# 4. Setup OpenAI API key
echo -e "${YELLOW}Step 4/5: Setting up OpenAI API key...${NC}"
echo "ADA now uses OpenAI's GPT model for improved performance."
echo -e "Please enter your ${BLUE}OpenAI API key${NC} (starts with 'sk-'):"
read -p "> " OPENAI_API_KEY

# Validate API key format - using a much more flexible pattern that accepts modern OpenAI keys
if [[ ! $OPENAI_API_KEY =~ ^sk-[a-zA-Z0-9_\-]+$ ]]; then
    echo -e "${YELLOW}Warning: The key you entered may not be in the correct format.${NC}"
    echo "Keys typically start with 'sk-' followed by alphanumeric characters, hyphens, and underscores."
    read -p "Continue anyway? (y/n) " CONTINUE
    if [[ ! $CONTINUE =~ ^[Yy]$ ]]; then
        echo -e "${RED}Setup cancelled. Please run the script again with a valid API key.${NC}"
        exit 1
    fi
fi

# Create or update .env file with the API key
echo "# OpenAI API key for Vision GPT module" > .env
echo "OPENAI_API_KEY=$OPENAI_API_KEY" >> .env
check_status "Saving API key"
echo -e "${GREEN}API key saved successfully.${NC}\n"

# 5. Run the application
echo -e "${YELLOW}Step 5/5: Starting ADA...${NC}"
echo "Launching main application..."
echo -e "${BLUE}---------------------------------------${NC}"
echo -e "${BLUE}ADA is now running. Press 'q' to quit.${NC}"
echo -e "${BLUE}---------------------------------------${NC}"
python main.py

# Deactivate virtual environment when done
deactivate
echo -e "\n${GREEN}ADA session ended. Thank you for using ADA!${NC}"