#!/bin/bash

# Simple startup script for Matrix Display

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Check if frontend is built
if [ ! -d "web/dist" ]; then
    echo "Frontend not built. Building now..."
    cd web
    npm install
    npm run build
    cd ..
fi

# Run the application
echo "Starting Matrix Display..."
python -m app.main
