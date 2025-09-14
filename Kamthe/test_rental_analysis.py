import os
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenRouter API configuration
openai.api_base = "https://openrouter.ai/api/v1"
openai.api_key = os.getenv("OPENROUTER_API_KEY")

def analyze_rental_results(search_results):
    """
    Analyze search results for suspicious rental content using OpenRouter.
    
    Args:
        search_results (list): List of search result dictionaries with 'title', 'link', 'snippet'
    
    Returns:
        list: List of analysis strings for each result
    """
    analyses = []
    
    for result in search_results:
        try:
            # Create the analysis prompt
            prompt = f"""
            You are a helpful agent who is helping me to research on someone who I have met online for a rental, these are the results I got when I searched google about them using their name and address. Can you look for anything suspicious, some things you can check for - 

            Match name ↔ address in reliable sources (property/tax records, directories).
            Confirm ownership/residency 
            Check for scam/fraud reports linked to name/address.
            Look for duplicate or inconsistent rental listings.
            Scan for legal/news mentions (evictions, lawsuits, scams).
            Flag anomalies (address type mismatch, too-cheap rent, conflicting info).
            Check if person is alive or currently located elsewhere (e.g., another country).
            Note if another person's name shows up as owner/resident for the property.
            
            Title: {result['title']}
            URL: {result['link']}
            Snippet: {result['snippet']}
            
            Look for:
            - Phishing attempts
            - Malicious websites
            - Scam indicators
            - Suspicious domain names
            - Misleading content
            - Security risks
            - Fake news or misinformation
            
            Provide a brief analysis (1-2 sentences) of any suspicious elements you find.
            If nothing suspicious is detected, respond with "No suspicious content detected."
            """
            
            # Make API call
            response = openai.ChatCompletion.create(
                model="openai/gpt-o1",
                messages=[
                    {"role": "system", "content": "You are a cybersecurity expert analyzing web content for suspicious or harmful elements. Be concise and specific in your analysis."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            content = response.choices[0].message.content.strip()
            analyses.append(content)
            
        except Exception as e:
            analyses.append(f"Error analyzing result: {str(e)}")
    
    return analyses
