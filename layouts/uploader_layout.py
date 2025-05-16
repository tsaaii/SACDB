"""
layouts/uploader_layout.py - Improved file uploader page

This file defines the enhanced file uploader page layout with clearer instructions,
better feedback, and a more user-friendly interface.
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
    Create the enhanced uploader page layout with improved user experience.
    
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
            
            # Step-by-step instructions card
            dbc.Card([
                dbc.CardHeader(html.H5("How to Upload Data")),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Div([
                                dbc.Badge("1", color="primary", className="me-2 p-2"),
                                "Prepare your Excel file with the required columns"
                            ], className="d-flex align-items-center mb-3"),
                            
                            html.Div([
                                dbc.Badge("2", color="primary", className="me-2 p-2"),
                                "Name the file following the pattern: Legacy Waste Status_DD.MM.YYYY.xlsx"
                            ], className="d-flex align-items-center mb-3"),
                            
                            html.Div([
                                dbc.Badge("3", color="primary", className="me-2 p-2"),
                                "Click 'Select a File' and choose your Excel file"
                            ], className="d-flex align-items-center mb-3"),
                        ], md=6),
                        
                        dbc.Col([
                            html.Div([
                                dbc.Badge("4", color="primary", className="me-2 p-2"),
                                "Wait for validation to complete"
                            ], className="d-flex align-items-center mb-3"),
                            
                            html.Div([
                                dbc.Badge("5", color="primary", className="me-2 p-2"),
                                "Click 'Process File' to upload and process"
                            ], className="d-flex align-items-center mb-3"),
                            
                            html.Div([
                                dbc.Badge("6", color="primary", className="me-2 p-2"),
                                "The system will update the dashboard with new data"
                            ], className="d-flex align-items-center mb-3"),
                        ], md=6),
                    ]),
                    
                    html.Div([
                        html.P([
                            html.Strong("Required Columns: "),
                            "Vendor, Cluster, ULB, Quantity to be remediated in MT"
                        ], className="mb-1 bg-light p-2 rounded"),
                    ], className="mt-2"),
                ])
            ], className="mb-4"),
            
            # Upload Component Card
            dbc.Card([
                dbc.CardHeader(html.H5("Upload Data File")),
                dbc.CardBody([
                    # File upload component with explicit instructions
                    dcc.Upload(
                        id='upload-data',
                        children=html.Div([
                            html.I(className="fas fa-file-excel me-2", style={"fontSize": "24px", "color": DARK_GREEN}),
                            'Drag and Drop or ',
                            html.A('Select a File', className="text-success fw-bold")
                        ]),
                        style={
                            'width': '100%',
                            'height': '80px',  # Increased height for better touch target
                            'lineHeight': '80px',
                            'borderWidth': '2px',  # Thicker border
                            'borderStyle': 'dashed',
                            'borderRadius': '8px',
                            'borderColor': LIGHT_GREEN,
                            'textAlign': 'center',
                            'margin': '10px 0',
                            'cursor': 'pointer',
                            'backgroundColor': '#f8f9fa'
                        },
                        # Set accept property to only allow Excel files
                        accept='.xlsx, .xls',
                        # Allow only single file upload
                        multiple=False
                    ),
                    
                    # Example file pattern
                    html.Div([
                        html.P([
                            html.Strong("File naming pattern: "),
                            html.Code("Legacy Waste Status_DD.MM.YYYY.xlsx", 
                                     className="p-2 bg-light rounded", 
                                     style={"fontFamily": "monospace"})
                        ], className="mt-3 mb-1"),
                        html.P([
                            html.Strong("Example: "),
                            html.Code("Legacy Waste Status_15.05.2025.xlsx", 
                                      style={"backgroundColor": LIGHT_GREEN})
                        ], className="mb-3", 
                           style={"fontSize": "0.9rem"}),
                    ]),
                    
                    # Alert for upload status
                    dbc.Alert(
                        id="upload-alert",
                        is_open=False,
                        duration=10000,  # Auto-dismiss after 10 seconds
                        dismissable=True,
                        className="mt-3"
                    ),
                    
                    # Progress bar
                    dbc.Progress(
                        id="upload-progress",
                        value=0,
                        striped=True,
                        animated=True,
                        color="success",
                        className="mt-3",
                        style={"display": "none", "height": "15px"}
                    ),
                    
                    # Process button - larger and more visible
                    dbc.Button(
                        [
                            html.I(className="fas fa-cogs me-2"), 
                            "Process File"
                        ],
                        id="process-upload-button",
                        color="success",
                        size="lg",
                        className="mt-4 w-100",
                        disabled=True
                    ),
                    
                    # Debug info (hidden in production)
                    html.Div(id="debug-info", className="mt-3 small text-muted d-none")
                ])
            ], className="mb-4 shadow-sm"),
            
            # Recent Uploads Table Card
            dbc.Card([
                dbc.CardHeader([
                    html.H5("Recent Uploads"),
                    html.Span(id="upload-count", className="badge bg-secondary ms-2")
                ], className="d-flex align-items-center"),
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
                                striped=True,
                                className="align-middle"
                            )
                        ]
                    )
                ])
            ], className="shadow-sm")
        ], className="mt-4"),
        
        # Store for holding the current upload file info
        dcc.Store(id="upload-file-info"),
        
        # Add footer
        create_footer()
    ])