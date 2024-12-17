from flask import render_template, jsonify, request, session
import requests
import os
from decorators import login_required  # Import the login_required decorator

BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')

@login_required
def index():
    """
    Renders the main index page for logged-in users.

    Returns:
        str: The rendered HTML for the index page.
    """
    return render_template('index.html')

@login_required
def dashboard():
    """
    Renders the dashboard page for logged-in users.

    Returns:
        str: The rendered HTML for the dashboard page.
    """
    return render_template('dashboard.html')

@login_required
def frontend_sensor_data():
    """
    Fetches sensor data from the backend and returns it as JSON.

    Handles errors by printing them and displaying an error message
    as JSON.

    Returns:
        Response: JSON data for sensors or an error message.
    """
    username = session.get('username')
    try:
        # Get user_id by username
        user_response = requests.get(f"{BACKEND_URL}/users/get_id?username={username}")
        user_response.raise_for_status()
        user_data = user_response.json()
        user_id = user_data.get('id')
        if not user_id:
            return jsonify({"error": "User ID not found"}), 404
    except requests.exceptions.RequestException as e:
        print(f"Error fetching user ID: {e}")
        error_message = {"error": f"Failed to fetch user ID: {e}"}
        return jsonify(error_message), 500

    try:
        response = requests.get(f'{BACKEND_URL}/sensor_data/user/{user_id}')
        response.raise_for_status()
        data = response.json()
        return jsonify(data)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching sensor data: {e}")
        error_message = {"error": f"Failed to fetch sensor data: {e}"}
        return jsonify(error_message), 500
    
@login_required
def influx_sensor_data():
    username = session.get('username')
    try:
        # Get user_id by username
        user_response = requests.get(f"{BACKEND_URL}/users/get_id?username={username}")
        user_response.raise_for_status()
        user_data = user_response.json()
        user_id = user_data.get('id')
        if not user_id:
            return jsonify({"error": "User ID not found"}), 404
    except requests.exceptions.RequestException as e:
        print(f"Error fetching user ID: {e}")
        error_message = {"error": f"Failed to fetch user ID: {e}"}
        return jsonify(error_message), 500
    try:
        response = requests.get(f'{BACKEND_URL}/get_influx_sensor_data/user/{user_id}')
        response.raise_for_status()
        data = response.json()
        return jsonify(data)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching sensor data: {e}")
        error_message = {"error": f"Failed to fetch sensor data: {e}"}
        return jsonify(error_message), 500
