# Web Scraper API Startup Script for Windows

Write-Host "🚀 Starting AI Web Scraper API..." -ForegroundColor Green

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  .env file not found. Creating from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "📝 Please edit .env file with your API keys before running again." -ForegroundColor Yellow
    exit 1
}

# Parse arguments
if ($args.Count -eq 0) {
    Write-Host "Usage: .\start.ps1 [docker|local]" -ForegroundColor Red
    Write-Host "  docker - Start with Docker Compose"
    Write-Host "  local  - Start locally with Python virtual environment"
    exit 1
}

$mode = $args[0]

if ($mode -eq "docker") {
    Write-Host "🐳 Starting with Docker Compose..." -ForegroundColor Blue
    docker-compose up --build
}
elseif ($mode -eq "local") {
    Write-Host "💻 Starting locally..." -ForegroundColor Blue
    
    # Check if virtual environment exists
    if (-not (Test-Path "venv")) {
        Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
        python -m venv venv
    }
    
    # Activate virtual environment
    .\venv\Scripts\Activate.ps1
    
    # Install requirements
    Write-Host "📦 Installing requirements..." -ForegroundColor Yellow
    pip install -r requirements.txt
    
    # Start the application
    Write-Host "🚀 Starting Flask application..." -ForegroundColor Green
    $env:FLASK_ENV = "development"
    python app.py
}
else {
    Write-Host "Invalid argument. Use 'docker' or 'local'" -ForegroundColor Red
    exit 1
}
