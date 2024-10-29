from flask import Flask, render_template, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://127.0.0.1:5050"}})  # Allow all origins, or specify "http://127.0.0.1:5000" if you want to restrict

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/devices')
def devices():
    return render_template('devices.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/frontend-sensor-data')
def frontend_sensor_data():
    try:
        response = requests.get('http://localhost:8080/api/sensor-data')  # Call to the backend
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()
        return jsonify(data)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching sensor data: {e}")
        return jsonify({"error": "Failed to fetch sensor data"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
