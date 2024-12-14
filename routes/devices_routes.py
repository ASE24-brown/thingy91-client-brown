from flask import render_template, jsonify, request, redirect, session
import requests
import os
from decorators import login_required  # Import the login_required decorator

BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')

@login_required
def devices():
    """
    Redirects users to an external devices UI dashboard.

    Returns:
        Response: A redirect response to the devices UI.
    """
    return redirect("http://localhost:1880/ui", code=302)

@login_required
def fetch_device_statuses():
    """
    Fetches the status of devices from the backend.

    Handles errors by returning a JSON error message.

    Returns:
        Response: JSON data containing device statuses or an error message.
    """
    try:
        # Get device statuses from the backend (or database)
        response = requests.get(f"{BACKEND_URL}/devices/status")  # Correct endpoint
        response.raise_for_status()
        devices = response.json()  # Fetch the list of devices with status info
        return jsonify(devices)  # Return as JSON
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to fetch devices: {e}"}), 500


@login_required
def coupling():
    """
    Renders the device coupling page.

    Returns:
        str: The rendered HTML for the coupling page.
    """
    return render_template('couple_device.html')

@login_required
def couple_device():
    """
    Handles device coupling for a user. Supports both GET and POST methods.

    - GET: Fetches and displays details for a specific device.
    - POST: Associates a device with a user and displays a success or error message.

    Returns:
        Response: The rendered coupling page with success or error messages.
    """
    if request.method == 'GET':
        device_id = request.args.get('device_id')  # Get device_id from URL
        try:
            response = requests.get(f"{BACKEND_URL}/devices/status/{device_id}")
            response.raise_for_status()
            device = response.json()
            return render_template('couple_device.html', device=device)
        except requests.exceptions.RequestException as e:
            error_message = f"Failed to fetch device details: {e}"
            return render_template('couple_device.html', error=error_message)

    if request.method == 'POST':
        user_id = session.get('user_id')
        device_id = request.form.get('device_id')

        if not user_id or not device_id:
            error_message = "User ID and Device ID are required"
            return render_template('couple_device.html', error=error_message)

        try:
            response = requests.post(
                f"{BACKEND_URL}/associate-device",
                json={"user_id": user_id, "device_id": device_id}
            )
            response.raise_for_status()
            success_message = "Device successfully coupled"
            return render_template('couple_device.html', success=success_message)
        except requests.exceptions.RequestException as e:
            error_message = f"Failed to couple device: {e}"
            return render_template('couple_device.html', error=error_message)

