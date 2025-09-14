from GoogleSearch import search_google, analyze_all_results
import time

def main():
    """Main function to search and automatically analyze rental results."""
    print("=== Rental Search Analyzer ===")
    
    try:
        # Get user input
        query = input("Enter your search query: ").strip()
        
        # Check if query is empty
        if not query:
            print("Please enter a valid search query.")
            return
        
        print(f"\nSearching for: '{query}'...")
        print("-" * 60)
        
        # Get search results
        results = search_google(query)
        
        if results:
            print(f"Found {len(results)} results:\n")
            
            # Display search results
            for i, result in enumerate(results, 1):
                print(f"{i}. {result['title']}")
                print(f"   🔗 {result['link']}")
                print(f"   📝 {result['snippet']}")
                print()
            
            # Automatically analyze all results
            analyses = analyze_all_results(results)
            
            # Display analysis results
            print("\n🛡️  AI ANALYSIS RESULTS")
            print("=" * 60)
            
            for i, analysis_data in enumerate(analyses, 1):
                result = analysis_data['result']
                analysis = analysis_data['analysis']
                
                print(f"\n{i}. {result['title']}")
                print(f"   🔗 {result['link']}")
                print(f"   🛡️  Analysis: {analysis}")
                print("-" * 40)
            
        else:
            print("No results found or an error occurred.")
        
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user. Goodbye!")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()
