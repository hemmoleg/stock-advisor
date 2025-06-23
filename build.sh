#!/bin/bash
set -e

echo "Installing Python dependencies..."
pip install --upgrade pip

# Install PyTorch CPU version first (smaller, no compilation needed)
echo "Installing PyTorch CPU version..."
pip install torch --index-url https://download.pytorch.org/whl/cpu

# Install other requirements
echo "Installing other requirements..."
pip install -r requirements.txt

echo "Build completed successfully!" 