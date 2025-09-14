from SerperAPICall import search_google
from firecrawl_scraper import scrape_url_simple
import requests
import json
import time
import os
from dotenv import load_dotenv
load_dotenv()

# OpenRouter API configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"


def analyze_link_suspiciousness(result):
    """
    Scrape URL content and use OpenRouter API to analyze for suspicious content.
    
    Args:
        result (dict): Search result containing title, link, and snippet
    
    Returns:
        str: Analysis of suspicious content or "No suspicious content detected"
    """
    # Scrape the URL to get markdown content
    print(f"    📄 Scraping content from: {result['link']}")
    scraped_content = scrape_url_simple(result['link'])
    
    prompt = f"""
    You are a helpful agent who is helping me to research on someone who I have met online for a rental, these are the results I got when I searched google about them using their name and address. Can you check for the following things - 

    Check if the name and address are matching in reliable sources (property/tax records, directories).
    Confirm ownership/residency 
    Check for scam/fraud reports linked to name/address.
    Look for duplicate or inconsistent rental listings.
    Scan for legal/news mentions (evictions, lawsuits, scams).
    Check if person is alive or currently located elsewhere (e.g., another country) - This is very important, if the name shows up in some other country then flag it in the final analysis.
    Note if another person's name shows up as owner/resident for the property.
    If the source is not trust worthy, then dont worry about it 

    
    Search Result Info:
    Title: {result['title']}
    URL: {result['link']}
    Snippet: {result['snippet']}
    
    Scraped Content from URL:
    {scraped_content[:2000]}...
    
    IMPORTANT: Respond in this exact format:
    ALERT: [true/false]
    ANALYSIS: [Your analysis here]
    
    Set ALERT to true if you find any suspicious elements, scam indicators, or red flags.
    Set ALERT to false if nothing suspicious is detected.
    """
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:3000",  # Optional: replace with your app's URL
        "X-Title": "VeritasAI Rental Analysis"  # Optional: replace with your app's name
    }
    
    data = {
        "model": "anthropic/claude-3.5-sonnet",
        "messages": [
            {"role": "system", "content": "You are a cybersecurity expert analyzing web content for suspicious or harmful elements. Be concise and specific in your analysis."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 300,
        "temperature": 0.3
    }
    
    response = requests.post(OPENROUTER_API_URL, headers=headers, json=data)
    response_data = response.json()
    
    content = response_data['choices'][0]['message']['content'].strip()
    
    # Parse the response to extract alert and analysis
    lines = content.split('\n')
    alert = False
    analysis = content
    
    for line in lines:
        if line.startswith('ALERT:'):
            alert_str = line.split('ALERT:')[1].strip().lower()
            alert = alert_str == 'true'
        elif line.startswith('ANALYSIS:'):
            analysis = line.split('ANALYSIS:')[1].strip()
    
    return {
        'alert': alert,
        'analysis': analysis
    }


def analyze_all_results(results):
    """
    Scrape and analyze all search results for suspicious content using OpenRouter AI.
    
    Args:
        results (list): List of search result dictionaries
    
    Returns:
        list: List of analysis results for each link
    """
    analyses = []
    
    print("🤖 Scraping URLs and running AI analysis using OpenRouter...")
    print("-" * 60)
    
    for i, result in enumerate(results, 1):
        print(f"🔍 Processing result {i}/{len(results)}: {result['title'][:50]}...")
        
        analysis_result = analyze_link_suspiciousness(result)
        analyses.append({
            'result': result,
            'alert': analysis_result['alert'],
            'analysis': analysis_result['analysis']
        })
        
        # Small delay to avoid rate limiting
        time.sleep(2)
    
    print("✅ Scraping and AI analysis completed!")
    return analyses


def search_and_analyze(query):
    """
    Search Google for a query and analyze results using OpenRouter AI.
    
    Args:
        query (str): The search query to analyze
    
    Returns:
        dict: Dictionary containing search results and AI analysis
        {
            'query': str,
            'search_results': list,
            'analyses': list,
            'success': bool,
            'error': str (if any)
        }
    """
    try:
        # Validate input
        if not query or not query.strip():
            return {
                'query': query,
                'search_results': [],
                'analyses': [],
                'success': False,
                'error': 'Empty query provided'
            }
        
        # Search Google
        results = search_google(query.strip())
        
        if not results:
            return {
                'query': query,
                'search_results': [],
                'analyses': [],
                'success': False,
                'error': 'No search results found'
            }
        
        # Analyze results with AI
        analyses = analyze_all_results(results)
        
        return {
            'query': query,
            'search_results': results,
            'analyses': analyses,
            'success': True,
            'error': None
        }
        
    except Exception as e:
        return {
            'query': query,
            'search_results': [],
            'analyses': [],
            'success': False,
            'error': str(e)
        }


def main():
    """Main function to get user input, search Google, and automatically analyze results with AI."""
    print("=== Google Search Tool with AI Analysis ===")
    print("Enter your search query to get the top 5 results from Google.")
    print("Results will be automatically analyzed using OpenRouter AI for suspicious content.\n")
    
    try:
        # Get user input
        query = input("Enter your search query: ").strip()
        
        # Use the abstracted function
        result = search_and_analyze(query)
        
        if not result['success']:
            print(f"Error: {result['error']}")
            return
        
        # Display results
        print(f"\nSearching for: '{result['query']}'...")
        print("-" * 60)
        
        if result['search_results']:
            print(f"Found {len(result['search_results'])} results:\n")
            for i, search_result in enumerate(result['search_results'], 1):
                print(f"{i}. {search_result['title']}")
                print(f"   🔗 {search_result['link']}")
                print(f"   📝 {search_result['snippet']}")
                print()
            
            # Display AI analysis
            print("\n" + "=" * 80)
            print("🛡️  AI ANALYSIS RESULTS (via OpenRouter)")
            print("=" * 80)
            
            for i, analysis_data in enumerate(result['analyses'], 1):
                search_result = analysis_data['result']
                alert = analysis_data['alert']
                analysis = analysis_data['analysis']
                
                alert_icon = "🚨" if alert else "✅"
                alert_status = "ALERT" if alert else "SAFE"
                
                print(f"\n{i}. {search_result['title']}")
                print(f"   🔗 {search_result['link']}")
                print(f"   {alert_icon} Status: {alert_status}")
                print(f"   🤖 AI Analysis: {analysis}")
                print("-" * 60)
        
        print("\n" + "=" * 60)
        print("Analysis complete!")
        
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user. Goodbye!")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        print("Please try again.")


if __name__ == "__main__":
    main()
