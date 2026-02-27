#!/bin/bash
echo "Setting up Python Virtual Environment..."

# Create a virtual environment named 'venv' if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Virtual environment created!"
fi

echo "Installing requirements..."
# Use the virtual environment's pip to install requirements
./venv/bin/pip install -r requirements.txt

echo "Starting Discord Time Tracker in PM2..."
pm2 start ecosystem.config.js
pm2 save
echo "Bot is now running in the background!"
