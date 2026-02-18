#!/usr/bin/env bash
# render-build.sh

echo "🚀 Starting Render build process..."

# Upgrade pip and install build tools
python -m pip install --upgrade pip setuptools wheel

# Install dependencies
pip install -r requirements.txt

echo "✅ Build completed successfully!"