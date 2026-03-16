#!/bin/bash

# Swatantra Backend Quick Start Script
set -e

echo "🚀 Swatantra Backend Setup"
echo "=========================="
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create virtual environment if needed
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔗 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env if doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️ Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your configuration"
fi

# Create data directory
mkdir -p data

echo ""
echo "✅ Setup complete!"
echo ""
echo "📖 Quick Start:"
echo ""
echo "Option 1: Local Development (SQLite + Ollama)"
echo "  $ source venv/bin/activate"
echo "  $ python -m uvicorn app.main:app --reload"
echo ""
echo "Option 2: Docker Compose (PostgreSQL + Backend)"
echo "  $ docker-compose up -d"
echo ""
echo "Option 3: Docker Development with Ollama"
echo "  $ docker-compose up -d postgres ollama"
echo "  $ source venv/bin/activate"
echo "  $ python -m uvicorn app.main:app --reload"
echo ""
echo "📚 Documentation: http://localhost:8000/docs"
echo "💾 Database mode: Check .env DB_TYPE setting"
echo ""
