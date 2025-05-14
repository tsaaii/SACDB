"""
Fixed version of app.py that eliminates duplicate callback issues
"""

import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import flask
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
import os
import time
import threading
from callbacks.enhanced_public_callbacks import register_enhanced_public_callbacks


# Create a Flask server
server = flask.Flask(__name__)
server.config.update(
    SECRET_KEY='your_secret_key_here'
)

# Create a login manager
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = '/login'

# Import components after initializing login_manager
from auth import load_user, User, users
from layouts.main_layout import create_main_layout
from callbacks.auth_callbacks import register_auth_callbacks
from callbacks.dashboard_callbacks import register_dashboard_callbacks
from callbacks.public_landing_callbacks import register_public_landing_callbacks
from data_processing import load_data

# Global variable to track when data file was last modified
DATA_FILE_LAST_MODIFIED = 0

# Function to watch for changes in the data file
def watch_data_file():
    global DATA_FILE_LAST_MODIFIED
    
    # Initialize with current modification time
    try:
        DATA_FILE_LAST_MODIFIED = os.path.getmtime('data.csv')
        print(f"Initial data file timestamp: {time.ctime(DATA_FILE_LAST_MODIFIED)}")
    except Exception as e:
        print(f"Error getting initial file timestamp: {e}")
    
    # Start watching for changes
    while True:
        try:
            current_modified = os.path.getmtime('data.csv')
            if current_modified > DATA_FILE_LAST_MODIFIED:
                print(f"Data file changed at {time.ctime(current_modified)}")
                DATA_FILE_LAST_MODIFIED = current_modified
                
                # Clear any cached data to force a reload
                # This assumes your load_data function has caching
                load_data(force_reload=True)
                
        except Exception as e:
            print(f"Error checking data file: {e}")
        
        # Sleep for a few seconds before checking again
        time.sleep(5)  # Check every 5 seconds

# Start the file watcher thread
@server.before_first_request
def start_file_watcher():
    watcher_thread = threading.Thread(target=watch_data_file)
    watcher_thread.daemon = True  # This ensures the thread will close when the main app closes
    watcher_thread.start()
    print("Data file watcher thread started")

@login_manager.user_loader
def load_user_callback(user_id):
    return load_user(user_id)

# Initialize the Dash app with Bootstrap
app = dash.Dash(
    __name__, 
    server=server,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    url_base_pathname='/'
)

# Define green theme colors
EMERALD = "#2ecc71"
DARK_GREEN = "#27ae60" 
LIGHT_GREEN = "#a9dfbf"
BG_COLOR = "#f1f9f5"

# Custom CSS
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
        <meta name="theme-color" content="#27ae60">
        <meta name="description" content="Swaccha Andhra Corporation Waste Remediation Dashboard">
        <title>Swaccha Andhra Corporation</title>
        {%favicon%}
        {%css%}
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
        <link rel="manifest" href="/assets/manifest.json">
        <link rel="apple-touch-icon" href="/assets/icons/icon-192x192.png">
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
        <script>
            // Register the service worker for PWA
            if ('serviceWorker' in navigator) {
                window.addEventListener('load', function() {
                    navigator.serviceWorker.register('/assets/service-worker.js')
                        .then(function(registration) {
                            console.log('ServiceWorker registration successful with scope: ', registration.scope);
                        }, function(err) {
                            console.log('ServiceWorker registration failed: ', err);
                        });
                });
            }
        </script>
    </body>
</html>
'''

# Set up the app layout
app.layout = create_main_layout()

# Register callbacks
register_auth_callbacks(app)
register_dashboard_callbacks(app)
register_public_landing_callbacks(app)  
register_enhanced_public_callbacks(app)

# Add endpoint to get last modified time
@server.route('/api/data-modified-time')
def get_data_modified_time():
    global DATA_FILE_LAST_MODIFIED
    return {'timestamp': DATA_FILE_LAST_MODIFIED, 'formatted': time.ctime(DATA_FILE_LAST_MODIFIED)}

if __name__ == '__main__':
    # Start the file watcher here for development mode
    watcher_thread = threading.Thread(target=watch_data_file)
    watcher_thread.daemon = True
    watcher_thread.start()
    print("Data file watcher thread started (development mode)")
    
    app.run(debug=True, port=8050)