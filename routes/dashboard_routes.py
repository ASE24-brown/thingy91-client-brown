from flask import render_template, jsonify, request
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
    on the dashboard page.

    Returns:
        Response: JSON data for sensors or an error message.
    """
    try:
        response = requests.get(f'{BACKEND_URL}/api/sensor-data')
        response.raise_for_status()
        data = response.json()
        return jsonify(data)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching sensor data: {e}")
        error_message = f"Failed to fetch sensor data: {e}"
        return render_template('dashboard.html', error_message=error_message)
