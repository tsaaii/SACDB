"""
layouts/uploader_layout.py - File Uploader page

This file defines the file uploader page layout with file validation for the naming pattern:
Legacy Waste Status_{dd}.{mm}.{yyyy}.xlsx
"""

from dash import html, dcc
import dash_bootstrap_components as dbc
from layouts.footer import create_footer
import re

# Define green theme colors
EMERALD = "#2ecc71"
DARK_GREEN = "#27ae60" 
LIGHT_GREEN = "#a9dfbf"
BG_COLOR = "#f1f9f5"
ACCENT_BLUE = "#3498db"

def create_navbar():
    """
    Create the navigation bar.
    
    Returns:
        dash component: The navbar component
    """
    return dbc.Navbar(
        dbc.Container([
            html.A(
                dbc.Row([
                    dbc.Col(html.I(className="fas fa-leaf", style={"font-size": "24px"}), width="auto"),
                    dbc.Col(dbc.NavbarBrand("Swaccha Andhra", style={"color": "white", "font-weight": "bold"}), width="auto")
                ], align="center", className="g-0"),
                href="/dashboard",
                style={"text-decoration": "none"}
            ),
            dbc.Nav([
                dbc.NavItem(dbc.NavLink("Dashboard", href="/dashboard", className="text-white")),
                dbc.NavItem(dbc.NavLink("Uploader", href="/uploader", active=True, className="text-white")),
                dbc.NavItem(dbc.NavLink("Reports", href="#", className="text-white")),
                dbc.NavItem(dbc.NavLink("Settings", href="#", className="text-white")),
                dbc.NavItem(dbc.Button("Logout", id="logout-button", color="light", size="sm", className="ms-2")),
            ], className="ms-auto", navbar=True),
        ]),
        color=DARK_GREEN,
        dark=True,
    )

def create_uploader_layout():
    """
    Create the uploader page layout with file validation for data uploads.
    
    Returns:
        dash component: The uploader layout
    """
    return html.Div([
        # Navbar
        create_navbar(),
        
        # Main content
        dbc.Container([
            # Header
            html.Div([
                html.H1("Data Uploader", className="my-4", style={"color": DARK_GREEN}),
                html.P("Upload waste remediation data files in XLSX format.", className="lead"),
            ], className="mb-4"),
            
            # Upload Component Card
            dbc.Card([
                dbc.CardHeader(html.H5("Upload Data File")),
                dbc.CardBody([
                    # File upload component with explicit accept property for Excel files
                    dcc.Upload(
                        id='upload-data',
                        children=html.Div([
                            html.I(className="fas fa-file-excel me-2", style={"fontSize": "24px", "color": DARK_GREEN}),
                            'Drag and Drop or ',
                            html.A('Select a File', className="text-success fw-bold")
                        ]),
                        style={
                            'width': '100%',
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                            'margin': '10px 0',
                            'cursor': 'pointer'
                        },
                        # Set accept property to only allow Excel files
                        accept='.xlsx',
                        # Allow only single file upload
                        multiple=False
                    ),
                    
                    # Detailed instructions with example
                    html.Div([
                        html.P([
                            html.Strong("Important: "),
                            "File must follow the naming pattern:"
                        ], className="mb-1 mt-3"),
                        html.Code("Legacy Waste Status_{dd}.{mm}.{yyyy}.xlsx", 
                                 className="d-block p-2 bg-light rounded", 
                                 style={"fontFamily": "monospace"}),
                        html.P([
                            html.Strong("Example: "),
                            html.Code("Legacy Waste Status_15.05.2025.xlsx", 
                                      style={"backgroundColor": LIGHT_GREEN})
                        ], className="mt-2", 
                           style={"fontSize": "0.9rem"}),
                        html.P([
                            html.I(className="fas fa-info-circle me-2", style={"color": ACCENT_BLUE}),
                            "Files will be saved to the ", 
                            html.Code("data", style={"backgroundColor": LIGHT_GREEN}),
                            " folder and used to update the dashboard."
                        ], className="mt-3 small p-2 rounded", style={"backgroundColor": "#e7f5ff"})
                    ], className="mt-3"),
                    
                    # Alert for upload status
                    dbc.Alert(
                        id="upload-alert",
                        is_open=False,
                        duration=5000,  # Auto-dismiss after 5 seconds
                        dismissable=True,
                        className="mt-3"
                    ),
                    
                    # Progress bar
                    dbc.Progress(
                        id="upload-progress",
                        value=0,
                        striped=True,
                        animated=True,
                        className="mt-3",
                        style={"display": "none"}
                    ),
                    
                    # Upload button (optional if you want explicit upload instead of automatic)
                    dbc.Button(
                        [html.I(className="fas fa-upload me-2"), "Process File"],
                        id="process-upload-button",
                        color="success",
                        className="mt-3",
                        disabled=True
                    )
                ])
            ], className="mb-4"),
            
            # Recent Uploads Table Card
            dbc.Card([
                dbc.CardHeader(html.H5("Recent Uploads")),
                dbc.CardBody([
                    html.Div(
                        id="recent-uploads-table",
                        children=[
                            dbc.Table(
                                [
                                    html.Thead(
                                        html.Tr([
                                            html.Th("File Name"),
                                            html.Th("Upload Date"),
                                            html.Th("Status"),
                                            html.Th("Actions")
                                        ])
                                    ),
                                    html.Tbody(id="upload-history-rows")
                                ],
                                bordered=True,
                                hover=True,
                                responsive=True,
                                striped=True
                            )
                        ]
                    )
                ])
            ])
        ], className="mt-4"),
        
        # Store for holding the current upload file info
        dcc.Store(id="upload-file-info"),
        
        # Add footer
        create_footer()
    ])