import http.client
import json
import os
from dotenv import load_dotenv

load_dotenv()

def search_google(query, api_key=os.getenv("SERPER_API_KEY"), num_results=5):
    """
    Search Google using Serper API and return the top search results.
    
    Args:
        query (str): The search query
        api_key (str): Serper API key
        num_results (int): Number of results to return (default: 5)
    
    Returns:
        list: List of dictionaries containing search results with title, link, and snippet
    """
    conn = http.client.HTTPSConnection("google.serper.dev")
    payload = json.dumps({
        "q": query,
        "num": num_results
    })
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }
    
    conn.request("POST", "/search", payload, headers)
    res = conn.getresponse()
    data = res.read()
    
    response_data = json.loads(data.decode("utf-8"))
    
    results = []
    for item in response_data['organic'][:num_results]:
        result = {
            'title': item['title'],
            'link': item['link'],
            'snippet': item['snippet']
        }
        results.append(result)
    
    conn.close()
    return results

if __name__ == "__main__":
    query = input("Enter your search query: ")
    results = search_google(query)
    
    print(f"\nTop {len(results)} search results for '{query}':")
    print("-" * 50)
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['title']}")
        print(f"   Link: {result['link']}")
        print(f"   Snippet: {result['snippet']}")
        print()