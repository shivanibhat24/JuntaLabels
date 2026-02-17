#!/bin/bash

# Installation script for Sustainability Deception Detector

echo "========================================================================"
echo "   🌍 Sustainability Deception Detector - Installation Script 🌍"
echo "========================================================================"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
echo "Found Python $python_version"

if (( $(echo "$python_version < 3.9" | bc -l) )); then
    echo "❌ Error: Python 3.9 or higher is required"
    exit 1
fi
echo "✓ Python version OK"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
echo "✓ Virtual environment created"
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip --break-system-packages 2>/dev/null || pip install --upgrade pip
echo "✓ pip upgraded"
echo ""

# Install dependencies
echo "Installing dependencies (this may take several minutes)..."
pip install --break-system-packages -r requirements.txt 2>/dev/null || pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Download spaCy model
echo "Downloading spaCy language model..."
python -m spacy download en_core_web_lg
echo "✓ spaCy model downloaded"
echo ""

# Create sample test image directory
mkdir -p test_images
echo "✓ Test directory created"
echo ""

echo "========================================================================"
echo "                      Installation Complete! ✓"
echo "========================================================================"
echo ""
echo "To run the application:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Run the GUI: python main.py"
echo "  3. Or run tests: python tests/test_all.py"
echo ""
echo "To deactivate virtual environment: deactivate"
echo ""
