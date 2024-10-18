from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

# Frontend route to render the main page
@app.route('/')
def index():
    return render_template('index.html')

# Frontend route to render devices page and fetch data from backend API
@app.route('/devices')
def devices():
    return render_template('devices.html', devices=devices)

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


# Run the frontend server
if __name__ == "__main__":
    app.run(debug=True)
