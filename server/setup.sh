#!/bin/bash

# DentalCorrectIQ Server Setup Script for Mac Mini

set -e

echo "🦷 DentalCorrectIQ Server Setup"
echo "================================"
echo ""

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "⚠️  Warning: This script is designed for macOS (Mac Mini)"
    echo "   You can continue, but some features may not work as expected"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if Ollama is installed
echo "Checking for Ollama..."
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama not found!"
    echo ""
    echo "Please install Ollama first:"
    echo "  curl -fsSL https://ollama.ai/install.sh | sh"
    echo ""
    echo "Or download from: https://ollama.ai"
    exit 1
else
    echo "✅ Ollama found: $(which ollama)"
fi

# Check if Ollama service is running
echo ""
echo "Checking Ollama service..."
if ! pgrep -x "ollama" > /dev/null; then
    echo "⚠️  Ollama service not running. Attempting to start..."
    ollama serve &
    sleep 3
fi

# Pull Llama 3.2 3B model
echo ""
echo "Checking for Llama 3.2 3B model..."
if ollama list | grep -q "llama3.2:3b"; then
    echo "✅ Llama 3.2 3B model already installed"
else
    echo "📥 Downloading Llama 3.2 3B model (this may take a few minutes)..."
    ollama pull llama3.2:3b
fi

# Check Python version
echo ""
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
echo "✅ Server setup complete!"
echo ""
echo "To start the server:"
echo "  cd server"
echo "  source venv/bin/activate"
echo "  python main.py"
echo ""
echo "Or simply run:"
echo "  ./server/run.sh"
echo ""
echo "Server will be available at: http://localhost:8000"
echo "Health check: http://localhost:8000/health"
