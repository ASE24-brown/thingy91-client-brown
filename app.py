from functools import wraps
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import requests
from flask import redirect, url_for, session
from flask import render_template_string
import os
import base64
import hashlib

# Logging
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


CLIENT_ID = "your-client-id"
CLIENT_SECRET = "your-client"
AUTH_SERVER_URL = "http://localhost:8001"

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

#@app.route('/auth')
#def auth():
#    return render_template('auth.html')

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

@app.route('/api/frontend-sensor-data')
def frontend_sensor_data():
    try:
        response = requests.get('http://localhost:8000/api/sensor-data')  # Call to the backend
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
            'http://localhost:8000/register/',
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
            'http://localhost:8000/login/',
            json={"username": username, "password": password}
        )
        response.raise_for_status()
        if response.status_code == 200:
            token = response.json().get('token')
            if token:
                session['token'] = token  # Store the token in the session
                session['logged_in'] = True
                return redirect('/auth')
                #return redirect(url_for('dashboard'))
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

# Function to generate a code verifier and challenge
def generate_pkce_pair():
    code_verifier = base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8').rstrip('=')
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode('utf-8')).digest()
    ).decode('utf-8').rstrip('=')
    return code_verifier, code_challenge

@app.route('/auth')
def auth():
    # PKCE parameters
    code_verifier, code_challenge = generate_pkce_pair()
    session['code_verifier'] = code_verifier  # Store code verifier securely in session

    # Build authorization URL
    authorization_url = (
        f"{AUTH_SERVER_URL}/oauth/authorize?"
        f"client_id={CLIENT_ID}"
        f"&redirect_uri={url_for('callback', _external=True)}"
        f"&response_type=code"
        f"&scope=openid profile email"
        f"&state=random_state_string"
        f"&code_challenge={code_challenge}"
        f"&code_challenge_method=S256"
    )
    print(f"Generated authorization URL: {authorization_url}")  # Debugging
    return render_template('auth.html', authorization_url=authorization_url)



@app.route('/callback', methods=['GET'])
def callback():
    """
    Handle the callback after user authorization.
    """
    code = request.args.get('code')
    state = request.args.get('state')

    if not code:
        return "Authorization failed: No code provided.", 400

    # Exchange the code for a token
    token_response = requests.post(
        'http://localhost:8001/oauth/token',  # Your OAuth server's token endpoint
        data={
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': 'your-client-id',
            'redirect_uri': 'http://localhost:5050/callback',
        },
    )

    if token_response.status_code == 200:
        token_data = token_response.json()
        # Redirect the user back to the frontend with the token
        return redirect(f"http://localhost:5050/dashboard?access_token={token_data}")
        return render_template_string(
            """
            <h1>Authorization Successful</h1>
            <p>Access Token: {{ token }}</p>
            <p>Refresh Token: {{ refresh_token }}</p>
            """,
            token=token_data.get('access_token'),
            refresh_token=token_data.get('refresh_token'),
        )
    else:
        return "Failed to exchange code for token.", 400




authorization_codes = {}

@app.route('/callback3', methods=['GET'])
def callback3():
    """
    Handle the authorization callback.

    :return: Success or error message.
    """
    code = request.args.get('code')
    state = request.args.get('state')
    
    logger.info(f"Callback received: code={code}, state={state}")
    
    # Check if the code exists in the authorization_codes dictionary
    if code not in authorization_codes:
        logger.error("Invalid or expired authorization code.")
        return "Invalid or expired authorization code.", 400
    
    # Optionally validate the state (if implemented)
    # Here, you can handle state validation logic

    # Retrieve stored data for the code
    auth_code_data = authorization_codes.get(code)
    logger.info(f"Authorization code data: {auth_code_data}")
    
    # Respond to the client
    return "Authorization successful. You may now exchange the code for a token.", 200


@app.route('/callback2')
def callback2():
    code = request.args.get('code')
    state = request.args.get('state')
    
    # Validate state for CSRF protection
    if state != 'random_state_string':
        return "Invalid state parameter", 400

    # Exchange authorization code for tokens
    token_response = requests.post(
        "{AUTH_SERVER_URL}/token",
        data={
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'code': code,
            'redirect_uri': url_for('callback', _external=True),
            'grant_type': 'authorization_code',
            'code_verifier': session.get('code_verifier')
        }
    )

    tokens = token_response.json()
    access_token = tokens.get('access_token')
    refresh_token = tokens.get('refresh_token')

    # Store tokens securely (e.g., in a database or session)
    session['access_token'] = access_token
    return redirect(url_for('devices'))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
