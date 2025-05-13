"""
Updated app.py with public landing page
"""

import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import flask
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user

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
        <title>Swaccha Andhra Corporation</title>
        {%favicon%}
        {%css%}
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Set up the app layout
app.layout = create_main_layout()

# Register callbacks
register_auth_callbacks(app)
register_dashboard_callbacks(app)
register_public_landing_callbacks(app)  # Add the public landing page callbacks

if __name__ == '__main__':
    app.run(debug=True, port=8050)