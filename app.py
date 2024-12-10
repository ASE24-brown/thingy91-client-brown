from functools import wraps
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import requests
from flask import redirect, url_for, session
import os

# Get the backend URL from an environment variable, default to localhost for non-Docker usage
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required for session management
CORS(app, resources={r"/api/*": {"origins": "*"}})  # Allow all origins, or specify "http://127.0.0.1:5000" if you want to restrict

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/devices')
@login_required
def devices():
    return redirect("http://localhost:1880/ui", code=302)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/coupling')
@login_required
def coupling():
    return render_template('couple_device.html')

@app.route('/api/frontend-sensor-data')
def frontend_sensor_data():
    try:
        response = requests.get(f'{BACKEND_URL}/api/sensor-data')  # Call to the backend
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()
        return jsonify(data)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching sensor data: {e}")
        return jsonify({"error": "Failed to fetch sensor data"}), 500
    
@app.route('/register_user', methods=['POST'])
def register_user():
    data = request.form
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    # Input validation
    if not username or not email or not password:
        return jsonify({"error": "Missing required fields"}), 400

    # Call your backend API to register the user
    try:
        response = requests.post(
            f'{BACKEND_URL}/register/',
            json={"username": username, "email": email, "password": password}
        )
        response.raise_for_status()
        #return jsonify({"message": "User registered successfully"}), 201
        return redirect(url_for('login'))
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Registration failed: {e}"}), 500
    
@app.route('/login_user', methods=['POST'])
def login_user():
    data = request.form
    username = data.get('username')
    password = data.get('password')

    # Input validation
    if not username or not password:
        return jsonify({"error": "Missing required fields"}), 400

    # Authenticate the user via the backend API
    try:
        response = requests.post(
            f'{BACKEND_URL}/login/',
            json={"username": username, "password": password}
        )
        response.raise_for_status()
        if response.status_code == 200:
            token = response.json().get('token')
            if token:
                session['token'] = token  # Store the token in the session
                session['logged_in'] = True
                return redirect(url_for('dashboard'))
            else:
                return jsonify({"error": "Token not found"}), 401
        else:
            return jsonify({"error": "Invalid credentials"}), 401
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Login failed: {e}"}), 500
    
@app.route('/logout', methods=['GET', 'POST'], endpoint='logout')
def logout_user():
    session['logged_in'] = False
    session.clear()  # Clear all session data
    return redirect(url_for('login'))

@app.route('/devices/couple', methods=['GET', 'POST'])
def couple_device():
    if request.method == 'GET':
        # Fetch available devices for the user
        try:
            response = requests.get(f"{BACKEND_URL}/devices")  # Assuming a route to fetch devices
            response.raise_for_status()
            devices = response.json()
            return render_template('couple_device.html', devices=devices)
        except requests.exceptions.RequestException as e:
            return jsonify({"error": f"Failed to fetch devices: {e}"}), 500

    if request.method == 'POST':
        # Get user ID and selected device ID
        user_id = session.get('user_id')  # Assuming user ID is stored in the session
        device_id = request.form.get('device_id')

        if not user_id or not device_id:
            return jsonify({"error": "User ID and Device ID are required"}), 400

        # Send coupling request to the backend
        try:
            response = requests.post(
                f"{BACKEND_URL}/associate-device",
                json={"user_id": user_id, "device_id": device_id}
            )
            response.raise_for_status()
            return jsonify({"message": "Device successfully coupled"}), 200
        except requests.exceptions.RequestException as e:
            return jsonify({"error": f"Failed to couple device: {e}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
