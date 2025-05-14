"""
Updated layouts/main_layout.py with public landing page
"""

from dash import html, dcc
import dash_bootstrap_components as dbc
from layouts.login_layout import create_login_layout
from layouts.dashboard_layout import create_dashboard_layout
from data_processing import load_data, get_dashboard_metrics

# Define theme colors
EMERALD = "#2ecc71"
DARK_GREEN = "#27ae60" 
LIGHT_GREEN = "#a9dfbf"
BG_COLOR = "#f1f9f5"

def create_main_layout():
    """
    Create the main application layout with URL routing.
    
    Returns:
        dash component: The main layout
    """
    return html.Div([
        dcc.Location(id='url', refresh=False),
        html.Div(id='page-content'),
        
        # Add interval component for auto-rotation on landing page
        dcc.Interval(
            id='auto-rotation-interval',
            interval=15 * 1000,  # 15 seconds in milliseconds
            n_intervals=0,
            disabled=True  # Initially disabled, enabled only on landing page
        ),
        
        # Store components
        dcc.Store(id='rotation-state', data={'vendor_index': 0, 'cluster_index': 0}),
        dcc.Store(id='public-vendor-filter', data=[]),
        dcc.Store(id='public-cluster-filter', data=[]),
        
        # Hidden components for public landing page
        html.Div([
            # Display components
            html.Span(id='current-vendor-display', children=''),
            html.Span(id='current-cluster-display', children=''),
            
            # Chart placeholders - Make sure to use the correct component types
            dcc.Graph(id='public-progress-gauge', figure={}),
            dcc.Graph(id='public-daily-progress-chart', figure={}),
            dcc.Graph(id='public-vendor-comparison-chart', figure={}),
            dcc.Graph(id='public-cluster-heatmap', figure={}),
            
            # Important: Use html.Iframe for srcDoc property
            html.Iframe(id='public-remediation-map', srcDoc='')
        ], style={'display': 'none'})
    ])
def create_public_landing_page():
    """
    Create the public landing page with auto-rotating dashboard.
    
    Returns:
        dash component: The public landing page
    """
    # Load data for the initial dashboard view
    df = load_data()
    metrics = get_dashboard_metrics(df)
    
    # Get all vendors and clusters
    vendors = sorted(df['Vendor'].unique())
    clusters = sorted(df['Cluster'].unique())
    
    # Custom navbar for landing page with login button
    navbar = dbc.Navbar(
        dbc.Container([
            html.A(
                dbc.Row([
                    #dbc.Col(html.I(className="fas fa-leaf", style={"fontSize": "24px"}), width="auto"),
                    dbc.Col(dbc.NavbarBrand("Swaccha Andhra", style={"color": "white", "fontWeight": "bold"}), width="auto")
                ], align="center", className="g-0"),
                href="/",
                style={"textDecoration": "none"}
            ),
            dbc.Nav([
                dbc.NavItem(
                    dbc.Button(
                        "Login", 
                        id="login-nav-button", 
                        color="light", 
                        size="sm", 
                        className="ms-2",
                        href="/login"
                    )
                ),
            ], className="ms-auto", navbar=True),
        ]),
        color=DARK_GREEN,
        dark=True,
        className="mb-4"
    )
    
    # Summary cards
    summary_cards = dbc.Row([
        # Total target card
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Total Waste Target", className="card-title"),
                    html.H2(f"{metrics['total_to_remediate']:,.0f} MT", className="text-primary"),
                    html.P("Total waste to be remediated", className="card-text text-muted")
                ])
            ], className="text-center border-0 shadow-sm h-100")
        ], md=4),
        
        # Remediated card
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Remediated So Far", className="card-title"),
                    html.H2(f"{metrics['total_remediated']:,.0f} MT", className="text-success"),
                    html.P(f"As of {metrics['latest_date']}", className="card-text text-muted")
                ])
            ], className="text-center border-0 shadow-sm h-100")
        ], md=4),
        
        # Progress card
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Overall Progress", className="card-title"),
                    dcc.Graph(
                        id='public-progress-gauge',
                        config={'displayModeBar': False},
                        style={'height': '100px'}
                    ),
                    html.P(f"{metrics['percent_complete']:.1f}% Complete", className="card-text text-center")
                ])
            ], className="text-center border-0 shadow-sm h-100")
        ], md=4)
    ], className="mb-4")
    
    # Current view indicator
    view_indicator = dbc.Card([
        dbc.CardBody([
            html.H4("Currently Viewing", className="card-title text-center mb-3"),
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Label("Vendor:", className="fw-bold me-2"),
                        html.Span(id="current-vendor-display", children=vendors[0] if vendors else "All")
                    ], className="d-flex align-items-center justify-content-center mb-2")
                ], md=6),
                dbc.Col([
                    html.Div([
                        html.Label("Cluster:", className="fw-bold me-2"),
                        html.Span(id="current-cluster-display", children=clusters[0] if clusters else "All")
                    ], className="d-flex align-items-center justify-content-center mb-2")
                ], md=6)
            ]),
            html.P("Dashboard auto-rotates every 15 seconds. Login for interactive controls.", 
                   className="text-center text-muted mt-2 mb-0")
        ])
    ], className="mb-4 border-0 shadow-sm")
    
    # Main charts
    charts = dbc.Row([
        # Daily progress chart
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("Daily Remediation Progress")),
                dbc.CardBody([
                    dcc.Graph(
                        id='public-daily-progress-chart',
                        config={'displayModeBar': False},
                        style={'height': '300px'}
                    )
                ])
            ], className="mb-4 shadow-sm border-0")
        ], md=12),
        
        # Vendor comparison
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("Vendor Performance")),
                dbc.CardBody([
                    dcc.Graph(
                        id='public-vendor-comparison-chart',
                        config={'displayModeBar': False},
                        style={'height': '300px'}
                    )
                ])
            ], className="mb-4 shadow-sm border-0")
        ], md=6),
        
        # Cluster heatmap
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("Cluster Progress")),
                dbc.CardBody([
                    dcc.Graph(
                        id='public-cluster-heatmap',
                        config={'displayModeBar': False},
                        style={'height': '300px'}
                    )
                ])
            ], className="mb-4 shadow-sm border-0")
        ], md=6),
        
        # Map visualization
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("Geographic Remediation Status")),
                dbc.CardBody([
                    html.Div(id='public-map-container', children=[
                        html.Iframe(
                            id='public-remediation-map',
                            style={'width': '100%', 'height': '400px', 'border': 'none'}
                        )
                    ])
                ])
            ], className="mb-4 shadow-sm border-0")
        ], md=12),
    ])
    
    # Hidden stored values for current selections
    current_selections = html.Div([
        dcc.Store(id='public-vendor-filter', data=[vendors[0]] if vendors else []),
        dcc.Store(id='public-cluster-filter', data=[clusters[0]] if clusters else [])
    ], style={'display': 'none'})
    
    # Combine into full layout
    return html.Div(style={"backgroundColor": BG_COLOR, "minHeight": "100vh"}, children=[
        navbar,
        dbc.Container([
            html.H1("Swaccha Andhra Waste Remediation Dashboard", 
                    className="my-4 text-center", 
                    style={"color": DARK_GREEN}),
            html.P(f"Data as of {metrics['latest_date']}", 
                   className="lead text-center mb-4"),
            summary_cards,
            view_indicator,
            charts,
            current_selections
        ], className="py-4")
    ])

# URL routing callback function (implemented in callbacks/auth_callbacks.py)
def display_page(pathname, is_authenticated):
    """
    Display the appropriate page based on URL and authentication state.
    """
    # Make sure this condition is working correctly
    if pathname == '/':
        if not is_authenticated:
            return create_public_landing_page()  # This should show the public dashboard
        else:
            return create_dashboard_layout()
    elif pathname == '/login':
        return create_login_layout()
    elif pathname == '/dashboard':
        if is_authenticated:
            return create_dashboard_layout()
        return create_login_layout()
    else:
        # 404 page
        return html.Div([
            html.H1('404 - Page Not Found', className='text-center mt-5'),
            html.P('The page you requested does not exist.', className='text-center')
        ])