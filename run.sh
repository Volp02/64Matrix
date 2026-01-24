#!/bin/bash

# Simple startup script for Matrix Display

# Ensure we are in the script's directory
cd "$(dirname "$0")"

# Check if running on Pi (simple check)
IS_PI=false
if [ -f /etc/rpi-issue ]; then
    IS_PI=true
fi

# Activate venv
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Virtual environment not found. Please run ./install.sh first."
    exit 1
fi

# Run the application
echo "Starting Matrix Display..."

if [ "$IS_PI" = true ]; then
    # Matrix library often requires root for hardware access
    # We pass the python path explicitly to ensure we use the venv python
    echo "Running with sudo for hardware access..."
    sudo $(which python) -m app.main
else
    # Development/Emulator mode
    python -m app.main
fi
