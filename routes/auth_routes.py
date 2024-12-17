from flask import render_template, jsonify, request, redirect, url_for, session
import requests
import os

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
                return redirect(url_for('index'))
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

