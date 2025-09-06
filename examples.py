#!/usr/bin/env python3
"""
Example usage of the Web Scraper API
"""

import requests
import json
import os
from typing import List, Dict, Any

class WebScraperClient:
    """Client for interacting with the Web Scraper API"""
    
    def __init__(self, base_url: str = "http://localhost:5000", api_key: str = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key or os.getenv('API_KEY', 'your-secret-api-key')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'X-API-Key': self.api_key
        })
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health status"""
        response = self.session.get(f"{self.base_url}/health")
        return response.json()
    
    def scrape(self, links: List[str], raw: bool = False, summarize: bool = False) -> Dict[str, Any]:
        """Scrape content from URLs"""
        data = {
            'links': links,
            'raw': raw,
            'summarize': summarize
        }
        
        response = self.session.post(f"{self.base_url}/scrape", json=data)
        response.raise_for_status()
        return response.json()

def main():
    """Example usage of the Web Scraper API"""
    
    # Initialize client
    client = WebScraperClient()
    
    print("🔍 Web Scraper API Examples")
    print("=" * 50)
    
    # 1. Health check
    print("\n1. Health Check:")
    try:
        health = client.health_check()
        print(f"✅ API Status: {health['status']}")
        print(f"🤖 Gemini AI: {'Enabled' if health['gemini_configured'] else 'Disabled'}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    # 2. Single URL scraping
    print("\n2. Single URL Scraping (Processed):")
    try:
        result = client.scrape(['https://httpbin.org/html'])
        print(f"✅ Processed {result['total_processed']} URL(s)")
        if result['results']:
            content = result['results'][0]['content']
            print(f"📄 Content preview: {content[:200]}...")
    except Exception as e:
        print(f"❌ Single URL scraping failed: {e}")
    
    # 3. Raw HTML scraping
    print("\n3. Raw HTML Scraping:")
    try:
        result = client.scrape(['https://httpbin.org/html'], raw=True)
        if result['results']:
            content = result['results'][0]['content']
            print(f"✅ Raw HTML length: {len(content)} characters")
            print(f"📄 HTML preview: {content[:200]}...")
    except Exception as e:
        print(f"❌ Raw HTML scraping failed: {e}")
    
    # 4. Multiple URLs
    print("\n4. Multiple URLs Scraping:")
    urls = [
        'https://httpbin.org/html',
        'https://httpbin.org/json',
        'https://httpbin.org/status/200'
    ]
    try:
        result = client.scrape(urls)
        print(f"✅ Total processed: {result['total_processed']}")
        print(f"✅ Successful: {result['successful']}")
        print(f"❌ Failed: {result['failed']}")
        
        for item in result['results']:
            status_emoji = "✅" if item['status'] == 'success' else "❌"
            print(f"  {status_emoji} {item['link']}: {item['status']}")
    except Exception as e:
        print(f"❌ Multiple URLs scraping failed: {e}")
    
    # 5. Content summarization (if Gemini is available)
    print("\n5. Content Summarization:")
    try:
        result = client.scrape(['https://httpbin.org/html'], summarize=True)
        if result['results'] and result['results'][0]['status'] == 'success':
            content = result['results'][0]['content']
            print(f"✅ Summarized content: {content[:300]}...")
        else:
            print("⚠️  Summarization may not be available (check Gemini API key)")
    except Exception as e:
        print(f"❌ Content summarization failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Examples completed!")

if __name__ == "__main__":
    main()
