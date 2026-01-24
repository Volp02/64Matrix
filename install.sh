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
sudo apt install -y python3-pip python3-venv build-essential python3-dev git curl python3-pillow

# 3. Install Node.js (v18)
if ! command -v node &> /dev/null; then
    echo -e "${GREEN}[3/6] Installing Node.js...${NC}"
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt install -y nodejs
else
    echo -e "${GREEN}[3/6] Node.js already installed.$(node -v)${NC}"
fi

# 4. Setup Python Environment
echo -e "${GREEN}[4/6] Setting up Python environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv --system-site-packages
fi

source venv/bin/activate
pip install --upgrade pip setuptools wheel

# 5. Setup RGB Matrix Library
echo -e "${GREEN}[5/6] Setting up RGB Matrix Library...${NC}"
if [ ! -d "rpi-rgb-led-matrix" ]; then
    git clone https://github.com/hzeller/rpi-rgb-led-matrix.git
fi

# Compile & Install Python bindings into venv
cd rpi-rgb-led-matrix
# Build C library first
make -j$(nproc)
# Build Python bindings
make build-python PYTHON=$(which python3)
make install-python PYTHON=$(which python3) 
cd ..

# Install dependencies
pip install -r requirements.txt

# 6. Performance Optimizations for RGB Matrix
echo -e "${GREEN}[6/7] Configuring performance optimizations...${NC}"

# Disable onboard audio (required for stable matrix operation)
if ! grep -q "^blacklist snd_bcm2835" /etc/modprobe.d/blacklist-rgb-matrix.conf 2>/dev/null; then
    echo "Disabling onboard audio driver..."
    echo "blacklist snd_bcm2835" | sudo tee -a /etc/modprobe.d/blacklist-rgb-matrix.conf
fi

# Isolate CPU cores for better performance (optional but recommended)
if ! grep -q "isolcpus" /boot/firmware/cmdline.txt 2>/dev/null && ! grep -q "isolcpus" /boot/cmdline.txt 2>/dev/null; then
    echo -e "${GREEN}Tip: For best performance, consider isolating CPU cores.${NC}"
    echo -e "Add 'isolcpus=3' to /boot/firmware/cmdline.txt (or /boot/cmdline.txt on older systems)"
    echo -e "This reserves CPU core 3 for the matrix, reducing jitter."
fi

echo -e "${GREEN}Performance optimizations applied. Reboot required for audio changes to take effect.${NC}"

# 7. Build Frontend
echo -e "${GREEN}[7/7] Building Frontend...${NC}"
cd web
npm install
npm run build
cd ..

echo -e "${GREEN}Installation Complete!${NC}"
echo -e "You can now run the application with: ${GREEN}./run.sh${NC}"
echo -e ""
echo -e "${RED}⚠️  IMPORTANT: Please reboot your Raspberry Pi for audio driver changes to take effect!${NC}"
echo -e "Run: ${GREEN}sudo reboot${NC}"
