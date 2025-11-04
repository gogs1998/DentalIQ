#!/bin/bash

# DentalCorrectIQ Client Runner

cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run ./setup.sh first"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

echo "🦷 Starting DentalCorrectIQ Client..."
echo "Press Ctrl+Shift+G to check notes from clipboard"
echo "Press Ctrl+C in terminal to stop"
echo ""

python main.py
