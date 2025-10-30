#!/bin/bash

# Second Brain - Setup Script
# This script automates the initial setup process

set -e  # Exit on any error

echo "🧠 Second Brain - Automated Setup"
echo "=================================="
echo ""

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Found Python $PYTHON_VERSION"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists. Skipping..."
else
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Create .env file if it doesn't exist
if [ -f ".env" ]; then
    echo "⚠️  .env file already exists. Skipping..."
else
    echo "Creating .env file..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your OPENAI_API_KEY"
    echo "   You can get an API key from: https://platform.openai.com/api-keys"
fi
echo ""

# Create necessary directories
echo "Creating data directories..."
mkdir -p data/uploads data/chroma_db
echo "✅ Data directories created"
echo ""

# Make scripts executable
echo "Making scripts executable..."
chmod +x test_api.py example_usage.py
echo "✅ Scripts are now executable"
echo ""

echo "=================================="
echo "✅ Setup completed successfully!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Edit .env and add your OPENAI_API_KEY"
echo "2. Activate the virtual environment: source venv/bin/activate"
echo "3. Start the server: python -m app.main"
echo "4. Test the API: python test_api.py"
echo ""
echo "For more information, see QUICKSTART.md"
echo ""
