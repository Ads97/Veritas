from SerperAPICall import search_google
from firecrawl_scraper import scrape_url_simple
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# API configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# JSON schema for structured output
AI_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "name_address_match": {
            "type": "integer",
            "description": "1 for yes, -1 for no, 0 for unknown"
        },
        "scam_fraud_report": {
            "type": "integer", 
            "description": "1 for yes, -1 for no, 0 for unknown"
        },
        "ownership_proof": {
            "type": "integer",
            "description": "1 for yes, -1 for no, 0 for unknown"
        },
        "legal_news": {
            "type": "integer",
            "description": "1 for yes, -1 for no, 0 for unknown"
        },
        "alive_or_dead": {
            "type": "integer",
            "description": "1 for yes, -1 for no, 0 for unknown"
        }
    },
    "required": ["name_address_match", "scam_fraud_report", "ownership_proof", "legal_news", "alive_or_dead"]
}

def analyze_landlord(name, address, search_result):
    """Analyze a single search result for landlord verification."""
    print(f"📄 Analyzing: {search_result['title']}")
    
    # Scrape the URL content
    scraped_content = scrape_url_simple(search_result['link'])
    
    # Create analysis prompt
    prompt = f"""
    Your task is to analyze the following information and determine if this "landlord" is a potential scmamer. Here are the results I got when I searched google for information about the "landlord". 

    Search Result:
    Title: {search_result['title']}
    URL: {search_result['link']}
    Snippet: {search_result['snippet']}
    
    Scraped Content: {scraped_content[:3000]}...
    
    Answer these questions:
    1. Does the name and address match {name} at {address}? (Yes/No/Unknown)
    2. Are there any scam/fraud reports for {name}? (Yes/No/Unknown)
    3. Does this prove ownership of {address} by {name}? (Yes/No/Unknown)
    4. Are there any legal issues mentioned? (Yes/No/Unknown)
    5. Is {name} alive and currently at {address}? (Yes/No/Unknown)
    
    Format your response in this exact format:[name_address_match, scam_fraud_report, ownership_proof, legal_news, alive_or_dead] where yes is 1 and no is -1 and everything else is 0.
    """

    
    # Make API request
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "openai/gpt-4o",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 500,
        "temperature": 0.3,
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "landlord_analysis",
                "schema": AI_OUTPUT_SCHEMA
            }
        }
    }
    
    response = requests.post(OPENROUTER_API_URL, headers=headers, json=data)
    response_data = response.json()
    return response_data['choices'][0]['message']['content'].strip()


def search_and_analyze_landlord(name, address):
    """Search for landlord information and analyze results."""
    query = f"{name} {address}"
    
    print(f"🔍 Searching for: {query}")
    
    # Search Google
    results = search_google(query)
    
    if not results:
        print("❌ No search results found")
        return
    
    print(f"✅ Found {len(results)} results")
    print("-" * 60)
    
    # Analyze each result
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['title']}")
        print(f"   🔗 {result['link']}")
        
        analysis = analyze_landlord(name, address, result)
        print(f"   🤖 Analysis: {analysis}")
        print("-" * 60)


def main():
    """Main function to run the landlord verification tool."""
    try:
        # Get user input with default values
        name_input = input("Enter the person's name (default: Tammy Carpenter): ").strip()
        name = name_input if name_input else "Tammy Carpenter"
        
        address_input = input("Enter the address (default: 21686 Drexel Street, Clinton Township, MI 48036): ").strip()
        address = address_input if address_input else "21686 Drexel Street, Clinton Township, MI 48036"
        
        print(f"\n🏠 Verifying landlord: {name}")
        print(f"📍 Address: {address}")
        print("=" * 60)
        
        # Search and analyze
        search_and_analyze_landlord(name, address)
        
        print("\n✅ Analysis complete!")
        
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    main()
