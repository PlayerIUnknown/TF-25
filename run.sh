#!/bin/bash

# AI-Enabled Survey Service - Startup Script

echo "=================================="
echo "AI Survey Backend Starting..."
echo "=================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python3 -m venv venv"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "Please copy .env.example to .env and configure it"
    exit 1
fi

# Activate virtual environment
echo "✓ Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import flask" 2>/dev/null; then
    echo "⚠️  Dependencies not found. Installing..."
    pip install -r requirements.txt
fi

# Display configuration (without sensitive data)
echo ""
echo "Configuration:"
echo "  Port: ${FLASK_PORT:-8000}"
echo "  Environment: ${FLASK_ENV:-development}"
echo ""

# Run the Flask application
echo "🚀 Starting Flask server..."
echo "=================================="
python app.py

