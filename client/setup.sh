#!/bin/bash

# DentalCorrectIQ Client Setup Script

set -e

echo "🦷 DentalCorrectIQ Client Setup"
echo "================================"
echo ""

# Check Python version
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found! Please install Python 3.8 or later"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✅ Python found: $PYTHON_VERSION"

# Create virtual environment
echo ""
echo "Creating Python virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists, skipping..."
else
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment and install dependencies
echo ""
echo "Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ Client setup complete!"
echo ""
echo "To start the client:"
echo "  cd client"
echo "  source venv/bin/activate"
echo "  python main.py"
echo ""
echo "Or simply run:"
echo "  ./client/run.sh"
echo ""
echo "Usage:"
echo "1. Copy text from any application (Ctrl+C / Cmd+C)"
echo "2. Press Ctrl+Shift+G (Windows) or Cmd+Shift+G (Mac)"
echo "3. View corrected text in popup window"
