"""
layouts/login_layout.py - Login page layout

This file defines the login page layout.
"""

from dash import html
import dash_bootstrap_components as dbc
from layouts.footer import create_footer

# Define green theme colors
EMERALD = "#2ecc71"
DARK_GREEN = "#27ae60" 
LIGHT_GREEN = "#a9dfbf"
BG_COLOR = "#f1f9f5"

def create_login_layout():
    """
    Create the login page layout.
    
    Returns:
        dash component: The login layout
    """
    return html.Div([
        html.Div(className='login-container', children=[
            html.Div(className='logo', children=[
                html.I(className='fas fa-leaf'),
            ]),
            html.H2('Swaccha Andhra Corporation', className='login-header'),
            
            dbc.Alert(
                "Invalid username or password",
                id="login-alert",
                dismissable=True,
                is_open=False,
                color="danger"
            ),
            
            dbc.Form([
                # Username field
                dbc.Label("Username", html_for="username"),
                dbc.Input(
                    type="text",
                    id="username",
                    placeholder="Enter username",
                    className="mb-3"
                ),
                
                # Password field
                dbc.Label("Password", html_for="password"),
                dbc.Input(
                    type="password",
                    id="password",
                    placeholder="Enter password",
                    className="mb-4"
                ),
                
                # Login button
                dbc.Button(
                    "LOG IN",
                    id="login-button",
                    color="primary",
                    className="login-button mt-3"
                ),
                
                # Forgot password text
                dbc.FormText(
                    "Forgot password?",
                    className="text-center mt-3",
                    style={"display": "block", "color": DARK_GREEN, "cursor": "pointer"}
                )
            ])
        ], style={
            'max-width': '400px',
            'margin': '80px auto',
            'padding': '30px',
            'border-radius': '8px',
            'box-shadow': '0 4px 20px rgba(0, 0, 0, 0.1)',
            'background-color': 'white',
        }),
        
        # Add footer
        create_footer()
    ], style={"backgroundColor": BG_COLOR, "minHeight": "100vh"})