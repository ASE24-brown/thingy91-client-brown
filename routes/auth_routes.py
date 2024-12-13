from flask import render_template, jsonify, request, redirect, url_for, session
import requests
import os

BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')

def login():
    return render_template('login.html')

def signup():
    return render_template('signup.html')

def register_user():
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
                return redirect(url_for('index'))
            else:
                return render_template('login.html', error="Token not found"), 401
        else:
            return render_template('login.html', error="Invalid credentials"), 401
    except requests.exceptions.RequestException as e:
        return render_template('login.html', error=f"Login failed: {e}"), 500

def logout_user():
    session['logged_in'] = False
    session.clear()
    return redirect(url_for('login'))
