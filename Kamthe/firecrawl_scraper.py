import requests
import os
from dotenv import load_dotenv

load_dotenv()

FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
FIRECRAWL_API_URL = "https://api.firecrawl.dev/v0/scrape"

def scrape_url(url):
    """
    Scrape a URL using Firecrawl API.
    
    Args:
        url (str): The URL to scrape
    
    Returns:
        dict: Firecrawl API response
    """
    # Check if URL is a social media platform
    social_platforms = ['facebook.com', 'twitter.com', 'instagram.com', 'tiktok.com', 'x.com']
    if any(platform in url.lower() for platform in social_platforms):
        return {
            'data': {
                'title': 'Social Media Platform',
                'description': 'Social media content',
                'markdown': 'No data available after scraping',
                'links': []
            }
        }
    
    headers = {
        "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "url": url,
        "formats": ["markdown", "links"]
    }
    
    response = requests.post(FIRECRAWL_API_URL, headers=headers, json=data)
    
    # Check if the response is successful
    if response.status_code == 200:
        return response.json()
    else:
        # Return a fallback structure if API fails
        return {
            'data': {
                'title': 'Error',
                'description': 'Failed to scrape content',
                'markdown': 'No data available after scraping',
                'links': []
            }
        }

def scrape_url_simple(url):
    """
    Scrape a URL and return just the markdown content.
    
    Args:
        url (str): The URL to scrape
    
    Returns:
        str: Markdown content of the URL
    """
    result = scrape_url(url)
    
    # Check if 'data' key exists and has 'markdown'
    if 'data' in result and 'markdown' in result['data']:
        return result['data']['markdown']
    else:
        return "No data available after scraping"

def main():
    """Main function to demonstrate URL scraping."""
    print("=== Firecrawl URL Scraper ===")
    
    url = input("Enter URL to scrape: ")
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    print(f"\nScraping: {url}")
    print("-" * 60)
    
    result = scrape_url(url)
    
    print(f"Title: {result['data']['title']}")
    print(f"Description: {result['data']['description']}")
    print(f"\nMarkdown Content:")
    print(result['data']['markdown'])
    
    if result['data']['links']:
        print(f"\nFound {len(result['data']['links'])} links:")
        for i, link in enumerate(result['data']['links'][:5], 1):
            print(f"  {i}. {link}")

if __name__ == "__main__":
    main()
