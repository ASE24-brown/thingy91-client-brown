from decorators import login_required
from flask import render_template, request, jsonify
import requests
import os

BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')

@login_required
def graphs():
    """
    Renders the device coupling page.

    Returns:
        str: The rendered HTML for the coupling page.
    """
    return render_template('graphs.html')

@login_required
def graphs_data():
    """
    Handle the request to fetch graph data based on the provided field name and range.
    This function expects a JSON payload with 'fieldName' and 'range' keys in the request.
    It then makes a POST request to the backend API to fetch the corresponding
    graph data. The response from the backend is returned directly to the frontend.
    Returns:
        Response: A JSON response containing the graph data if successful,
                  or an error message if the field name is missing or if the
                  backend request fails.
    Raises:
        Exception: If there is an issue with the request to the backend API.
    """
    
    field_name = request.json.get('fieldName')
    range = request.json.get('range', '-6h')  # Default to last 6 hours if range is not provided
    if not field_name:
        return jsonify({"error": "Field name is required"}), 400

    # Call the backend API (/api/graphs_data) via requests
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/query",  # Adjust if needed for your backend URL
            json={"fieldName": field_name, "range": range}
        )

        if response.status_code == 200:
            return jsonify(response.json())  # Pass the data directly to the frontend
        else:
            return jsonify({"error": "Failed to fetch data from backend"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500