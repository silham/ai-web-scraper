from flask import Flask, request, jsonify
import asyncio
import aiohttp
import concurrent.futures
from bs4 import BeautifulSoup
import google.generativeai as genai
import os
from functools import wraps
import logging
from typing import List, Dict, Any
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
API_KEY_HEADER = 'X-API-Key'
EXPECTED_API_KEY = os.getenv('API_KEY', 'your-secret-api-key')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
MAX_CONCURRENT_REQUESTS = 4

# Configure Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')
else:
    logger.warning("GEMINI_API_KEY not set. AI features will not work.")
    model = None

def require_api_key(f):
    """Decorator to require API key authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get(API_KEY_HEADER)
        if not api_key or api_key != EXPECTED_API_KEY:
            return jsonify({'error': 'Invalid or missing API key'}), 401
        return f(*args, **kwargs)
    return decorated_function

def extract_text_content(html: str) -> str:
    """Extract useful text content from HTML"""
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text content
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    except Exception as e:
        logger.error(f"Error extracting text content: {str(e)}")
        return ""

async def fetch_url(session: aiohttp.ClientSession, url: str) -> Dict[str, Any]:
    """Fetch content from a single URL"""
    try:
        timeout = aiohttp.ClientTimeout(total=30)
        async with session.get(url, timeout=timeout) as response:
            if response.status == 200:
                content = await response.text()
                return {
                    'link': url,
                    'status': 'success',
                    'content': content,
                    'status_code': response.status
                }
            else:
                return {
                    'link': url,
                    'status': 'error',
                    'error': f'HTTP {response.status}',
                    'status_code': response.status
                }
    except asyncio.TimeoutError:
        return {
            'link': url,
            'status': 'error',
            'error': 'Request timeout',
            'status_code': 408
        }
    except Exception as e:
        return {
            'link': url,
            'status': 'error',
            'error': str(e),
            'status_code': 500
        }

async def scrape_urls_batch(urls: List[str]) -> List[Dict[str, Any]]:
    """Scrape multiple URLs concurrently with batch processing"""
    results = []
    
    # Process URLs in batches of MAX_CONCURRENT_REQUESTS
    for i in range(0, len(urls), MAX_CONCURRENT_REQUESTS):
        batch = urls[i:i + MAX_CONCURRENT_REQUESTS]
        
        async with aiohttp.ClientSession(
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        ) as session:
            tasks = [fetch_url(session, url) for url in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in batch_results:
                if isinstance(result, Exception):
                    results.append({
                        'link': 'unknown',
                        'status': 'error',
                        'error': str(result),
                        'status_code': 500
                    })
                else:
                    results.append(result)
    
    return results

def process_with_ai(content: str, summarize: bool = False) -> str:
    """Process content with Gemini AI"""
    if not model:
        return "AI processing unavailable - Gemini API key not configured"
    
    try:
        if summarize:
            prompt = f"""
            Please provide a concise summary of the following web content, highlighting the key points and main topics (Only output the summarized content, no explanations, no introductions):
            {content[:1000000]}
            """
        else:
            prompt = f"""
            Please extract and organize the useful information from the following web content, removing any navigation elements, ads, or irrelevant content. Present the information in a clean, structured format. Don't remove any part of the content that seems relevant. (Only output the content, no explanations, no introductions):

            {content[:1000000]}
            """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"AI processing error: {str(e)}")
        return f"AI processing failed: {str(e)}"

def run_async_in_thread(coro):
    """Run async function in a thread with new event loop"""
    def run():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(run)
        return future.result()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'gemini_configured': model is not None
    })

@app.route('/scrape', methods=['POST'])
@require_api_key
def scrape_links():
    """Main scraping endpoint"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Validate required fields
        links = data.get('links', [])
        if not links or not isinstance(links, list):
            return jsonify({'error': 'links field is required and must be an array'}), 400
        
        if len(links) == 0:
            return jsonify({'error': 'At least one link is required'}), 400
        
        # Get optional parameters
        raw = data.get('raw', False)
        summarize = data.get('summarize', False)
        
        logger.info(f"Processing {len(links)} links, raw={raw}, summarize={summarize}")
        
        # Scrape URLs
        scrape_results = run_async_in_thread(scrape_urls_batch(links))
        
        # Process results
        final_results = []
        for result in scrape_results:
            if result['status'] == 'success':
                content = result['content']
                
                if not raw:
                    # Extract text content
                    text_content = extract_text_content(content)
                    
                    if text_content and len(text_content.strip()) > 0:
                        # Process with AI if available
                        if model:
                            processed_content = process_with_ai(text_content, summarize)
                            final_results.append({
                                'link': result['link'],
                                'content': processed_content,
                                'status': 'success'
                            })
                        else:
                            final_results.append({
                                'link': result['link'],
                                'content': text_content,
                                'status': 'success',
                                'note': 'AI processing unavailable'
                            })
                    else:
                        final_results.append({
                            'link': result['link'],
                            'status': 'error',
                            'error': 'No extractable content found'
                        })
                else:
                    # Return raw HTML
                    final_results.append({
                        'link': result['link'],
                        'content': content,
                        'status': 'success'
                    })
            else:
                # Error case
                final_results.append({
                    'link': result['link'],
                    'status': 'error',
                    'error': result.get('error', 'Unknown error'),
                    'status_code': result.get('status_code', 500)
                })
        
        return jsonify({
            'results': final_results,
            'total_processed': len(links),
            'successful': len([r for r in final_results if r['status'] == 'success']),
            'failed': len([r for r in final_results if r['status'] == 'error'])
        })
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
