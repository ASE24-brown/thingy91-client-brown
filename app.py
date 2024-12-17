from flask import Flask
from routes.auth_routes import login, signup, register_user, login_user, logout_user
from routes.dashboard_routes import index, dashboard, frontend_sensor_data, influx_sensor_data
from routes.devices_routes import devices, coupling, couple_device, fetch_device_statuses, decouple_device
from routes.graphs_routes import graphs, graphs_data
import os

app = Flask(__name__)

# Set the backend URL
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')

# Secret key for session management
app.secret_key = os.urandom(24)

# Register routes
app.add_url_rule('/login', view_func=login)
app.add_url_rule('/signup', view_func=signup)
app.add_url_rule('/register_user', view_func=register_user, methods=['POST'])
app.add_url_rule('/login_user', view_func=login_user, methods=['POST'])
app.add_url_rule('/logout', view_func=logout_user, methods=['GET', 'POST'])

app.add_url_rule('/', view_func=index)
app.add_url_rule('/dashboard', view_func=dashboard)
app.add_url_rule('/api/frontend-sensor-data', view_func=frontend_sensor_data)
app.add_url_rule('/api/influx-sensor-data', view_func=influx_sensor_data)

app.add_url_rule('/devices', view_func=devices)
app.add_url_rule('/coupling', view_func=coupling)
app.add_url_rule('/devices/couple', view_func=couple_device, methods=['GET', 'POST'])
app.add_url_rule('/devices/status', view_func=fetch_device_statuses, methods=['GET'])
app.add_url_rule('/devices/decouple', view_func=decouple_device, methods=['POST'])

app.add_url_rule('/graphs', view_func=graphs)
app.add_url_rule('/api/query', view_func=graphs_data, methods=['POST'])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)