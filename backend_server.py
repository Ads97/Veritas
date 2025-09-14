from flask import Flask, request, jsonify
from flask_cors import CORS
from check_if_scammer import check_if_scammer, check_if_scammer_mock

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/api/data', methods=['POST'])
def fetch_information():
    """
    Endpoint that accepts POST requests with name, address, listing_url, other_details
    and any additional kwargs to check if the information indicates a scammer
    """
    try:
        # Get the JSON data from the request
        request_data = request.get_json()
        
        if not request_data:
            return jsonify({
                "status": "error",
                "message": "No JSON data provided in request"
            }), 400
        
        # Extract required parameters from request data
        name = request_data.get('name')
        address = request_data.get('address')
        listing_url = request_data.get('listing_url')
        other_details = request_data.get('other_details')
        
        # Extract any additional kwargs (excluding the known required fields)
        additional_kwargs = {k: v for k, v in request_data.items() 
                           if k not in ['name', 'address', 'listing_url', 'other_details']}
        
        # Call the scammer check function with all parameters
        scammer_result = check_if_scammer_mock(
            name=name, 
            address=address, 
            listing_url=listing_url, 
            other_details=other_details,
            **additional_kwargs
        )
        
        return jsonify(scammer_result), 200
        
    except Exception as e:
        # Return error response
        error_response = {
            "status": "error",
            "message": f"Error processing request: {str(e)}",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        return jsonify(error_response), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({"status": "healthy", "message": "Server is running"}), 200

if __name__ == '__main__':
    print("Starting simple Flask server...")
    app.run(debug=True, host='0.0.0.0', port=5000)
