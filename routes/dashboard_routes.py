from flask import render_template, jsonify, request
import requests
import os
from decorators import login_required  # Import the login_required decorator

BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')

@login_required
def index():
    return render_template('index.html')

@login_required
def dashboard():
    return render_template('dashboard.html')

@login_required
def frontend_sensor_data():
    try:
        response = requests.get(f'{BACKEND_URL}/api/sensor-data')
        response.raise_for_status()
        data = response.json()
        return jsonify(data)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching sensor data: {e}")
        error_message = f"Failed to fetch sensor data: {e}"
        return render_template('dashboard.html', error_message=error_message)
