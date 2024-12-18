from flask import render_template, jsonify, request, redirect, url_for, session, render_template_string
import requests
import os
import base64
import hashlib
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
# CLIENT_SECRET = os.getenv("CLIENT_SECRET")
AUTH_SERVER_URL = os.getenv("AUTH_SERVER_URL")

BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')

def login():
    """
    Renders the login page.

    Returns:
        str: The rendered HTML for the login page.
    """
    return render_template('login.html')

def signup():
    """
    Renders the signup page.

    Returns:
        str: The rendered HTML for the signup page.
    """
    return render_template('signup.html')

def register_user():
    """
    Handles user registration by sending a POST request to the backend.

    Validates user inputs and returns the signup page with an error message
    if any required fields are missing or the registration fails.

    Returns:
        Response: Redirects to the login page on success or renders the signup
        page with an error message on failure.
    """
    data = request.form
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return render_template('signup.html', error="Missing required fields"), 400

    try:
        response = requests.post(
            f'{BACKEND_URL}/register/',
            json={"username": username, "email": email, "password": password}
        )
        response.raise_for_status()
        return redirect(url_for('login'))
    except requests.exceptions.RequestException as e:
        return render_template('signup.html', error=f"Registration failed: {e}"), 500

def login_user():
    """
    Handles user login by sending a POST request to the backend.

    Validates user inputs and saves the authentication token in the session
    if login is successful.

    Returns:
        Response: Redirects to the index page on success or renders the login
        page with an error message on failure.
    """
    data = request.form
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return render_template('login.html', error="Missing required fields"), 400

    try:
        response = requests.post(
            f'{BACKEND_URL}/login/',
            json={"username": username, "password": password}
        )
        response.raise_for_status()
        if response.status_code == 200:
            token = response.json().get('token')
            if token:
                session['token'] = token
                session['logged_in'] = True
                session['username'] = username
                return redirect(url_for('auth'))
            else:
                return render_template('login.html', error="Token not found"), 401
        else:
            return render_template('login.html', error="Invalid credentials"), 401
    except requests.exceptions.RequestException as e:
        return render_template('login.html', error=f"Login failed: {e}"), 500

def logout_user():
    """
    Logs out the user by clearing the session and decoupling any associated device.

    Returns:
        Response: Redirects to the login page.
    """
    username = session.get('username')
    if username:
        try:
            # Get user ID based on the username
            user_response = requests.get(f"{BACKEND_URL}/users/get_id?username={username}")
            user_response.raise_for_status()
            user_data = user_response.json()
            user_id = user_data.get('id')

            if user_id:
                # Call the decouple route to disassociate the device
                decouple_response = requests.post(
                    f"{BACKEND_URL}/disassociate-device-from-user",
                    json={"user_id": user_id}
                )
                decouple_response.raise_for_status()
        except requests.exceptions.RequestException as e:
            # Log any issues but don't prevent logout
            print(f"Error during device decoupling: {e}")

    # Clear the session
    session['logged_in'] = False
    session.clear()
    return redirect(url_for('login'))



def generate_pkce_pair():
    """
    Generate a PKCE code verifier and code challenge pair.

    Returns:
        tuple: A tuple containing the code verifier and code challenge.
    """
    code_verifier = base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8').rstrip('=')
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode('utf-8')).digest()
    ).decode('utf-8').rstrip('=')
    return code_verifier, code_challenge


def auth():
    """
    Initiate the OAuth authorization flow with PKCE.

    Returns:
        Response: A redirect response to the authorization URL.
    """
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
    return redirect(authorization_url)

def callback():
    """
    Handle the callback after user authorization.

    Returns:
        Response: A redirect response to the index page or an error message.
    """
    code = request.args.get('code')
    token_url = "http://auth_server:8001/oauth/token"

    if not code:
        return "Authorization failed: No code provided.", 400

    # Exchange the code for a token
    token_response = requests.post(
        token_url,  # Your OAuth server's token endpoint
        data={
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': 'your-client-id',
            'redirect_uri': 'http://localhost:5050/callback',
        },
    )

    if token_response.status_code == 200:
        token_data = token_response.json()
        return redirect(url_for('index'))  
    else:
        return "Failed to exchange code for token.", 400