"""
callbacks/auth_callbacks.py - Authentication callbacks

This file registers the authentication-related callbacks.
"""

from dash import Input, Output, State
from flask_login import login_user, logout_user, current_user
from auth import validate_user
from layouts.main_layout import display_page

def register_auth_callbacks(app):
    """
    Register authentication callbacks with the app.
    
    Args:
        app (dash.Dash): The Dash application
    """
    # URL routing callback
    @app.callback(
        Output('page-content', 'children'),
        [Input('url', 'pathname')]
    )
    def route_page(pathname):
        """
        Route to the appropriate page based on URL and authentication state.
        """
        is_authenticated = current_user.is_authenticated
        return display_page(pathname, current_user.is_authenticated)
    
    # Login callback
    @app.callback(
        [Output('login-alert', 'is_open'),
         Output('url', 'pathname')],
        [Input('login-button', 'n_clicks')],
        [State('username', 'value'),
         State('password', 'value')],
        prevent_initial_call=True
    )
    def login_callback(n_clicks, username, password):
        """
        Handle login form submission.
        
        Args:
            n_clicks: Button click event
            username: Entered username
            password: Entered password
            
        Returns:
            tuple: (alert_is_open, redirect_path)
        """
        if n_clicks is None:
            return False, '/login'
            
        user = validate_user(username, password)
        if user:
            login_user(user)
            return False, '/dashboard'
        
        # Invalid credentials
        return True, '/login'

    # Logout callback
    @app.callback(
        Output('url', 'pathname', allow_duplicate=True),
        [Input('logout-button', 'n_clicks')],
        prevent_initial_call=True
    )
    def logout_callback(n_clicks):
        """
        Handle logout button click.
        
        Args:
            n_clicks: Button click event
            
        Returns:
            str: Redirect path
        """
        if n_clicks:
            logout_user()
        return '/'