#!/bin/bash

# Web Scraper API Startup Script

echo "🚀 Starting AI Web Scraper API..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo "📝 Please edit .env file with your API keys before running again."
    exit 1
fi

# Source environment variables
source .env

# Check required variables
if [ -z "$API_KEY" ] || [ "$API_KEY" = "your-secret-api-key-here" ]; then
    echo "❌ Please set a proper API_KEY in .env file"
    exit 1
fi

if [ -z "$GEMINI_API_KEY" ] || [ "$GEMINI_API_KEY" = "your-gemini-api-key-here" ]; then
    echo "⚠️  GEMINI_API_KEY not set. AI features will be disabled."
fi

# Check if running in Docker or local
if [ "$1" = "docker" ]; then
    echo "🐳 Starting with Docker Compose..."
    docker-compose up --build
elif [ "$1" = "local" ]; then
    echo "💻 Starting locally..."
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "📦 Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install requirements
    echo "📦 Installing requirements..."
    pip install -r requirements.txt
    
    # Start the application
    echo "🚀 Starting Flask application..."
    export FLASK_ENV=development
    python app.py
else
    echo "Usage: $0 [docker|local]"
    echo "  docker - Start with Docker Compose"
    echo "  local  - Start locally with Python virtual environment"
    exit 1
fi
