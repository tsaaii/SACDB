"""
layouts/footer.py - Footer component for all pages

This file defines the footer component used across all pages.
"""

from dash import html
import dash_bootstrap_components as dbc

# Define theme colors
EMERALD = "#2ecc71"
DARK_GREEN = "#27ae60" 
LIGHT_GREEN = "#a9dfbf"
BG_COLOR = "#f1f9f5"

def create_footer():
    """
    Create a consistent footer for all pages.
    
    Returns:
        dash component: The footer component
    """
    return html.Footer(
        dbc.Container([
            html.Hr(style={"margin": "20px 0"}),
            html.Div([
                html.P([
                    "Made in Andhra Pradesh, with ",
                    html.I(className="fas fa-heart", style={"color": "#e74c3c"}),
                    " • © 2025 Advitia Labs"
                ], className="text-center text-muted")
            ])
        ]),
        style={
            "padding": "10px 0 20px 0",
            "marginTop": "20px",
        }
    )