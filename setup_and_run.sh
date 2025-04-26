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
echo -e "${YELLOW}Step 1/4: Setting up virtual environment...${NC}"
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
echo -e "${YELLOW}Step 2/4: Installing requirements...${NC}"
pip install -r requirements.txt
check_status "Requirements installation"
echo -e "${GREEN}Requirements installed successfully.${NC}\n"

# 3. Create Models directory if it doesn't exist
echo -e "${YELLOW}Step 3/4: Setting up models...${NC}"
if [ ! -d "Models" ]; then
    echo "Creating Models directory..."
    mkdir -p Models
    check_status "Creating Models directory"
fi

# Run the model downloader script
echo "Downloading models (this may take some time)..."
python model_requirements.py
check_status "Model download"
echo -e "${GREEN}Models downloaded successfully.${NC}\n"

# 4. Run the application
echo -e "${YELLOW}Step 4/4: Starting ADA...${NC}"
echo "Launching main application..."
echo -e "${BLUE}---------------------------------------${NC}"
echo -e "${BLUE}ADA is now running. Press 'q' to quit.${NC}"
echo -e "${BLUE}---------------------------------------${NC}"
python main.py

# Deactivate virtual environment when done
deactivate
echo -e "\n${GREEN}ADA session ended. Thank you for using ADA!${NC}"#!/bin/bash
# filepath: /Users/haidermalik/Documents/Code/ADA/setup_and_run.sh

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
echo -e "${YELLOW}Step 1/4: Setting up virtual environment...${NC}"
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
echo -e "${YELLOW}Step 2/4: Installing requirements...${NC}"
pip install -r requirements.txt
check_status "Requirements installation"
echo -e "${GREEN}Requirements installed successfully.${NC}\n"

# 3. Create Models directory if it doesn't exist
echo -e "${YELLOW}Step 3/4: Setting up models...${NC}"
if [ ! -d "Models" ]; then
    echo "Creating Models directory..."
    mkdir -p Models
    check_status "Creating Models directory"
fi

# Run the model downloader script
echo "Downloading models (this may take some time)..."
python model_requirements.py
check_status "Model download"
echo -e "${GREEN}Models downloaded successfully.${NC}\n"

# 4. Run the application
echo -e "${YELLOW}Step 4/4: Starting ADA...${NC}"
echo "Launching main application..."
echo -e "${BLUE}---------------------------------------${NC}"
echo -e "${BLUE}ADA is now running. Press 'q' to quit.${NC}"
echo -e "${BLUE}---------------------------------------${NC}"
python main.py

# Deactivate virtual environment when done
deactivate
echo -e "\n${GREEN}ADA session ended. Thank you for using ADA!${NC}"