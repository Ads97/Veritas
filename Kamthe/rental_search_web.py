from flask import Flask, render_template, request, jsonify
from GoogleSearch import search_google, analyze_all_results
import json

app = Flask(__name__)

@app.route('/')
def index():
    """Serve the main HTML page."""
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    """Handle search requests and return results."""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'error': 'Please enter a search query'}), 400
        
        # Get search results
        results = search_google(query)
        
        if not results:
            return jsonify({'error': 'No results found'}), 404
        
        # Analyze results
        analyses = analyze_all_results(results)
        
        # Format response
        response_data = {
            'query': query,
            'results': []
        }
        
        for analysis_data in analyses:
            result = analysis_data['result']
            analysis = analysis_data['analysis']
            
            response_data['results'].append({
                'title': result['title'],
                'link': result['link'],
                'snippet': result['snippet'],
                'analysis': analysis
            })
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
