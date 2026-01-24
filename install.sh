#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Matrix Display Installation...${NC}"

# Check for sudo
if [ "$EUID" -eq 0 ]; then 
    echo -e "${RED}Please run as normal user (not root). Script will use sudo where needed.${NC}"
    exit 1
fi

# 1. Update System
echo -e "${GREEN}[1/6] Updating system packages...${NC}"
sudo apt update && sudo apt upgrade -y

# 2. Install Dependencies
echo -e "${GREEN}[2/6] Installing system dependencies...${NC}"
sudo apt install -y python3-pip python3-venv build-essential python3-dev git curl

# 3. Install Node.js (v18)
if ! command -v node &> /dev/null; then
    echo -e "${GREEN}[3/6] Installing Node.js...${NC}"
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt install -y nodejs
else
    echo -e "${GREEN}[3/6] Node.js already installed.$(node -v)${NC}"
fi

# 4. Setup RGB Matrix Library
echo -e "${GREEN}[4/6] Setting up RGB Matrix Library...${NC}"
if [ ! -d "rpi-rgb-led-matrix" ]; then
    git clone https://github.com/hzeller/rpi-rgb-led-matrix.git
fi

# Compile Python bindings
cd rpi-rgb-led-matrix
# Minimal flags for performance, can be adjusted
make build-python PYTHON=$(which python3)
sudo make install-python PYTHON=$(which python3)
cd ..

# 5. Setup Python Environment
echo -e "${GREEN}[5/6] Setting up Python environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip

# Install dependencies
# Note: rgbmatrix is installed globally/system-site-packages often, 
# so we might need to allow system site packages or handle it carefully.
# For simplicity in this script, we assume the make install-python put it in a place reachable.
# If using venv, we might need to link it or install it inside.
# Let's try installing requirements first.
pip install -r requirements.txt

# 6. Build Frontend
echo -e "${GREEN}[6/6] Building Frontend...${NC}"
cd web
npm install
npm run build
cd ..

echo -e "${GREEN}Installation Complete!${NC}"
echo -e "You can now run the application with: ${GREEN}./run.sh${NC}"
