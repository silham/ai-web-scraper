# AI Web Scraper API

A powerful Flask-based web scraper API that can extract content from multiple URLs concurrently and process it using Google's Gemini AI.

## Features

- **Concurrent Processing**: Scrapes up to 4 URLs simultaneously per batch
- **AI-Powered Content Extraction**: Uses Google Gemini to extract useful content and summarize
- **Raw HTML Support**: Option to return raw HTML instead of processed content
- **API Key Protection**: Secure your API with custom API keys
- **Docker Ready**: Fully containerized for easy deployment
- **Error Handling**: Comprehensive error handling with detailed response codes
- **Health Check**: Built-in health monitoring endpoint

## API Endpoints

### POST /scrape

Main scraping endpoint that processes URLs and returns extracted content.

**Headers:**
- `X-API-Key`: Your API key for authentication
- `Content-Type`: application/json

**Request Body:**
```json
{
  "links": ["https://example.com", "https://another-site.com"],
  "raw": false,
  "summarize": false
}
```

**Parameters:**
- `links` (array, required): Array of URLs to scrape
- `raw` (boolean, optional, default: false): Return raw HTML or process with AI
- `summarize` (boolean, optional, default: false): Summarize content (only when raw=false)

**Response:**
```json
{
  "results": [
    {
      "link": "https://example.com",
      "content": "Processed content here...",
      "status": "success"
    },
    {
      "link": "https://failed-site.com",
      "status": "error",
      "error": "HTTP 404",
      "status_code": 404
    }
  ],
  "total_processed": 2,
  "successful": 1,
  "failed": 1
}
```

### GET /health

Health check endpoint to monitor API status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": 1693958400.123,
  "gemini_configured": true
}
```

## Setup and Installation

### Option 1: Docker (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd ai-web-scraper
```

2. Create environment file:
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. Build and run with Docker:
```bash
docker-compose up --build
```

### Option 2: Local Development

1. Clone the repository:
```bash
git clone <repository-url>
cd ai-web-scraper
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set environment variables:
```bash
export API_KEY="your-secret-api-key"
export GEMINI_API_KEY="your-gemini-api-key"
```

5. Run the application:
```bash
python app.py
```

## Configuration

### Environment Variables

- `API_KEY`: Your custom API key for protecting the endpoint
- `GEMINI_API_KEY`: Google Gemini API key (get from Google AI Studio)
- `FLASK_ENV`: Flask environment (development/production)

### Getting Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy the key to your `.env` file

## Usage Examples

### Basic scraping (processed content):
```bash
curl -X POST http://localhost:5000/scrape \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-api-key" \
  -d '{
    "links": ["https://example.com"]
  }'
```

### Raw HTML extraction:
```bash
curl -X POST http://localhost:5000/scrape \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-api-key" \
  -d '{
    "links": ["https://example.com"],
    "raw": true
  }'
```

### Summarized content:
```bash
curl -X POST http://localhost:5000/scrape \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-api-key" \
  -d '{
    "links": ["https://example.com"],
    "raw": false,
    "summarize": true
  }'
```

### Multiple URLs:
```bash
curl -X POST http://localhost:5000/scrape \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-api-key" \
  -d '{
    "links": [
      "https://example.com",
      "https://another-site.com",
      "https://third-site.com"
    ]
  }'
```

## Performance Features

- **Concurrent Processing**: Processes up to 4 URLs simultaneously
- **Batch Processing**: Large numbers of URLs are processed in batches
- **Timeout Handling**: 30-second timeout per request
- **Memory Efficient**: Content is processed in streams where possible
- **Error Resilience**: Individual URL failures don't affect other URLs

## Error Handling

The API provides detailed error information:

- **401**: Invalid or missing API key
- **400**: Invalid request format or missing required fields
- **408**: Request timeout
- **404**: URL not found
- **500**: Internal server error

## Security Features

- API key authentication required for all scraping operations
- Non-root user in Docker container
- Input validation and sanitization
- Rate limiting through concurrent request limits

## Monitoring

- Health check endpoint at `/health`
- Comprehensive logging
- Docker health checks included
- Request/response tracking

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest
```

### Code Structure

```
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── Dockerfile         # Docker configuration
├── docker-compose.yml # Docker Compose setup
├── .env.example       # Environment variables template
└── README.md          # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
