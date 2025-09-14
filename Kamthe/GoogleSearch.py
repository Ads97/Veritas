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


def analyze_link_suspiciousness(name, address, result):
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
    Your task is to analyze the following information and determine if this "landlord" is a potential scammer. Here are the results I got when I searched google for information about the "landlord". 
    
    Search Result Info:
    Title: {result['title']}
    URL: {result['link']}
    Snippet: {result['snippet']}
    
    Complete Information:
    {scraped_content[:2000]}...
    
    Answer the following questions about the above profile: 

    IMPORTANT: Question 1: (Yes/No/Unknown) Does the name and the address in the above document match with this name ({name}) and address {address}? 
    Question 2: (Yes/No/NA) Are there ANY scam/fraud reports mentioned for the above name '{name}'?
    Question 3: (Yes/No/Unknown) Does the above information prove ownership of address '{address}' by name '{name}'?
    Question 4: (Yes/No/Unknown) Does the above information contain any legal/news mentions (evictions, lawsuits, scams)? 
    Question 5: (Yes/No/Unknown) Does the above information indicate if the person '{name}' is alive and currently at address '{address}'? If the information indicates the person is dead or currently not at the address, mention 'No'. This is very IMPORTANT!

    If the above information does not help answer the question, mark it "unknown" or NA". 
        
    Respond in this exact format:
    name_address_match: # yes/no/unkonwn for whether the name and address in the above information match '{name}' and '{address}'
    scam_fraud_report: # yes/no/unkonwn for whether there are any scam/fraud reports mentioned
    ownership_proof: # yes/no/unkonwn for whether the above information provides proof of ownership
    legal_news: # yes/no/unknown for whether the above information contain any legal/news mentions
    alive_or_dead: # yes/no/unknown for if the information indicates the person is dead or currently not at the address
    
    alert: #(True/False) if any of the above is suspicous, set alert to True
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


def analyze_all_results(name, address, results):
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
        
        analysis_result = analyze_link_suspiciousness(name, address, result)
        analyses.append({
            'result': result,
            'alert': analysis_result['alert'],
            'analysis': analysis_result['analysis']
        })
        
        # Small delay to avoid rate limiting
        time.sleep(2)
    
    print("✅ Scraping and AI analysis completed!")
    return analyses


def search_and_analyze(name, address):
    query = name + address
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
        analyses = analyze_all_results(name, address, results)
        
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
    print("Enter the name and address to search for potential rental scam information.")
    print("Results will be automatically analyzed using OpenRouter AI for suspicious content.\n")
    
    try:
        # Get user input
        name = input("Enter the person's name: ").strip()
        address = input("Enter the address: ").strip()
        
        # Use the abstracted function
        result = search_and_analyze(name, address)
        
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
