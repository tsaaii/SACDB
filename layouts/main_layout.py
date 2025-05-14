"""
Updated layouts/main_layout.py with fixed public landing page components
"""

from dash import html, dcc
import dash_bootstrap_components as dbc
from layouts.login_layout import create_login_layout
from layouts.dashboard_layout import create_dashboard_layout
from data_processing import load_data, get_dashboard_metrics
from layouts.footer import create_footer


# Define theme colors
EMERALD = "#2ecc71"
DARK_GREEN = "#27ae60" 
LIGHT_GREEN = "#a9dfbf"
BG_COLOR = "#f1f9f5"


def get_enhanced_public_landing():
    """
    Dynamically import the enhanced public landing to avoid circular imports.
    """
    from layouts.enhanced_public_landing import create_enhanced_public_landing
    return create_enhanced_public_landing()


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
            interval=60 * 1000,  # CHANGED: 60 seconds in milliseconds
            n_intervals=0,
            disabled=True  # Initially disabled, enabled only on landing page
        ),
        
        # Store component for rotation state
        dcc.Store(id='rotation-state', data={'vendor_index': 0, 'cluster_index': 0, 'combo_index': 0}),
        
        # Display components for public landing page
        html.Span(id='current-vendor-display', style={'display': 'none'}),
        html.Span(id='current-cluster-display', style={'display': 'none'})
    ])

def create_public_landing_page():
    """
    Create the public landing page with auto-rotating dashboard,
    optimized for both TV displays and mobile viewing.
    
    Returns:
        dash component: The public landing page
    """
    # Load data for the initial dashboard view
    df = load_data()
    metrics = get_dashboard_metrics(df)
    
    # Get all vendors and clusters
    vendors = sorted(df['Vendor'].unique())
    clusters = sorted(df['Cluster'].unique())
    
    # Custom navbar for landing page with login button and large logo for TV visibility
    navbar = dbc.Navbar(
        dbc.Container([
            html.A(
                dbc.Row([
                    dbc.Col(html.I(className="fas fa-leaf", style={"fontSize": "28px", "color": "white"}), width="auto"),
                    dbc.Col(dbc.NavbarBrand("Swaccha Andhra", style={"color": "white", "fontWeight": "bold", "fontSize": "24px"}), width="auto")
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
                        size="md",  # Larger button for TV/touch 
                        className="ms-2 fw-bold",
                        href="/login"
                    )
                ),
            ], className="ms-auto", navbar=True),
        ]),
        color=DARK_GREEN,
        dark=True,
        className="mb-2 py-2"  # Slightly thicker navbar
    )
    
    # Summary section - Hero area with big progress gauge and headline stats (TV-optimized)
    hero_section = dbc.Row([
        dbc.Col([
            html.Div([
                html.H1("Swaccha Andhra Progress", 
                        className="display-4 text-center mb-2",
                        style={"fontSize": "3.5rem", "fontWeight": "bold"}),  # Larger for TV
                html.P(f"Data as of {metrics['latest_date']}", 
                       className="lead text-center mb-3",
                       style={"fontSize": "1.5rem"}),  # Larger for TV
                html.Div([
                    dcc.Graph(
                        id='public-progress-gauge',
                        config={'displayModeBar': False},
                        style={'height': '200px'}  # Taller gauge for TV
                    ),
                ], className="text-center mb-2"),
                html.H3(f"{metrics['percent_complete']:.1f}% Complete", 
                        className="text-center mb-3",
                        style={"fontSize": "2.5rem", "fontWeight": "bold"}),  # Larger for TV
                
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.H2(f"{metrics['total_to_remediate']:,.0f}", 
                                   className="mb-0",
                                   style={"fontSize": "2.2rem", "fontWeight": "bold"}),  # Larger for TV
                            html.P("Target (MT)", 
                                  className="text-muted",
                                  style={"fontSize": "1.2rem"})  # Larger for TV
                        ], className="text-center")
                    ], md=6),
                    dbc.Col([
                        html.Div([
                            html.H2(f"{metrics['total_remediated']:,.0f}", 
                                   className="mb-0",
                                   style={"fontSize": "2.2rem", "fontWeight": "bold", "color": "#2E8B57"}),  # Larger for TV
                            html.P("Remediated (MT)", 
                                  className="text-muted",
                                  style={"fontSize": "1.2rem"})  # Larger for TV
                        ], className="text-center")
                    ], md=6),
                ], className="mb-3")
            ], className="py-4 px-3 bg-white rounded shadow-sm")
        ], md=12, lg=12)
    ], className="mb-3")
    
    # Current view indicator - Enlarged for TV display
    view_indicator = dbc.Card([
        dbc.CardBody([
            html.H4("Currently Viewing", 
                   className="card-title text-center mb-3",
                   style={"fontSize": "2rem", "fontWeight": "bold"}),  # Larger for TV
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Label("Vendor:", className="fw-bold me-2", style={"fontSize": "1.3rem"}),  # Larger for TV
                        html.Span(id="current-vendor-display", 
                                 children=vendors[0] if vendors else "All",
                                 style={"fontSize": "1.3rem", "fontWeight": "bold", "color": "#2E8B57"})  # Highlight with color
                    ], className="d-flex align-items-center justify-content-center mb-2")
                ], md=6),
                dbc.Col([
                    html.Div([
                        html.Label("Cluster:", className="fw-bold me-2", style={"fontSize": "1.3rem"}),  # Larger for TV
                        html.Span(id="current-cluster-display", 
                                 children=clusters[0] if clusters else "All",
                                 style={"fontSize": "1.3rem", "fontWeight": "bold", "color": "#8B4513"})  # Highlight with color
                    ], className="d-flex align-items-center justify-content-center mb-2")
                ], md=6)
            ]),
            html.P("Dashboard auto-rotates every 15 seconds. Login for interactive controls.", 
                   className="text-center text-muted mt-2 mb-0",
                   style={"fontSize": "1.2rem"})  # Larger for TV
        ])
    ], className="mb-3 border-0 shadow-sm")
    
    # Main charts - TV optimized
    charts = dbc.Row([
        # Daily progress chart - Full width for emphasis and readability on TV
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("Daily Remediation Progress", 
                                      style={"fontSize": "1.5rem", "fontWeight": "bold"})),  # Larger for TV
                dbc.CardBody([
                    dcc.Graph(
                        id='public-daily-progress-chart',
                        config={'displayModeBar': False, 'responsive': True},
                        style={'height': '350px'}  # Taller for TV
                    )
                ], className="p-2")  # Reduced padding for more chart space
            ], className="mb-3 shadow-sm border-0")
        ], md=12),
        
        # Vendor comparison and Cluster heatmap in a single row - optimized for glanceability on TV
        dbc.Row([
            # Vendor comparison
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Vendor Performance", 
                                          style={"fontSize": "1.5rem", "fontWeight": "bold"})),  # Larger for TV
                    dbc.CardBody([
                        dcc.Graph(
                            id='public-vendor-comparison-chart',
                            config={'displayModeBar': False, 'responsive': True},
                            style={'height': '300px'}  # Taller for TV
                        )
                    ], className="p-2")  # Reduced padding for more chart space
                ], className="h-100 shadow-sm border-0")
            ], md=12, lg=6, className="mb-3"),
            
            # Cluster heatmap
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Cluster Progress", 
                                          style={"fontSize": "1.5rem", "fontWeight": "bold"})),  # Larger for TV
                    dbc.CardBody([
                        dcc.Graph(
                            id='public-cluster-heatmap',
                            config={'displayModeBar': False, 'responsive': True},
                            style={'height': '300px'}  # Taller for TV
                        )
                    ], className="p-2")  # Reduced padding for more chart space
                ], className="h-100 shadow-sm border-0")
            ], md=12, lg=6, className="mb-3")
        ])
    ])
    
    # Combine into full layout
    return html.Div(style={"backgroundColor": BG_COLOR, "minHeight": "100vh"}, children=[
        navbar,
        dbc.Container([
            # Add a clock for TV display
            html.Div(id="tv-clock", className="text-end mb-2", style={"fontSize": "1.2rem", "color": "#666"}),
            
            hero_section,
            view_indicator,
            charts,
                        
            # Add interval for clock updates
            dcc.Interval(
            id='clock-interval',
            interval=1000,  # 1 second for real-time clock
            n_intervals=0
            )
        ], className="py-2 px-2 px-sm-3", fluid=True),  # Use fluid container for full TV width
        create_footer()
    ])

# URL routing callback function (implemented in callbacks/auth_callbacks.py)
def display_page(pathname, is_authenticated):

    """
    Display the appropriate page based on URL and authentication state.
    """
    if pathname == '/':
        if not is_authenticated:
            # Use the enhanced public landing page
            return get_enhanced_public_landing()
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