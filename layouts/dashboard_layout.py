"""
layouts/dashboard_layout.py - Dashboard page layout

This file defines the dashboard layout with all visualizations and controls.
"""

from dash import html, dcc
import dash_bootstrap_components as dbc
from data_processing import load_data, get_dashboard_metrics
from visualizations.charts import (
    create_progress_gauge, create_daily_progress_chart, 
    create_vendor_comparison, create_cluster_heatmap
)
from visualizations.maps import create_remediation_map

# Define green theme colors
EMERALD = "#2ecc71"
DARK_GREEN = "#27ae60" 
LIGHT_GREEN = "#a9dfbf"
BG_COLOR = "#f1f9f5"

# Load data and calculate metrics
df = load_data()
metrics = get_dashboard_metrics(df)

def create_dashboard_layout():
    """
    Create the dashboard layout with visualizations.
    
    Returns:
        dash component: The dashboard layout
    """
    return html.Div([
        # Navbar
        create_navbar(),
        
        # Main content
        dbc.Container([
            # Welcome message and date
            html.Div([
                html.H1("Swaccha Andhra Dashboard", className="my-4", style={"color": DARK_GREEN}),
                html.P(f"Data as of {metrics['latest_date']}", className="lead"),
            ], className="mb-4"),
            
            # Summary cards
            create_summary_cards(),
            
            # Filters
            create_filters(),
            
            # Charts
            dbc.Row([
                # Daily progress chart
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Daily Remediation Progress")),
                        dbc.CardBody([
                            dcc.Graph(
                                id='daily-progress-chart',
                                figure=create_daily_progress_chart(df),
                                style={'height': '300px'}
                            )
                        ])
                    ], className="mb-4")
                ], width=12),
                
                # Vendor comparison
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Vendor Performance")),
                        dbc.CardBody([
                            dcc.Graph(
                                id='vendor-comparison-chart',
                                figure=create_vendor_comparison(metrics['vendor_stats']),
                                style={'height': '300px'}
                            )
                        ])
                    ], className="mb-4")
                ], width=6),
                
                # Cluster heatmap
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Cluster Progress")),
                        dbc.CardBody([
                            dcc.Graph(
                                id='cluster-heatmap',
                                figure=create_cluster_heatmap(df),
                                style={'height': '300px'}
                            )
                        ])
                    ], className="mb-4")
                ], width=6),
                
                # Map visualization
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Geographic Remediation Status")),
                        dbc.CardBody([
                            html.Div(id='map-container', children=[
                                html.Iframe(
                                    id='remediation-map',
                                    srcDoc=create_remediation_map(df),
                                    style={'width': '100%', 'height': '400px', 'border': 'none'}
                                )
                            ])
                        ])
                    ], className="mb-4")
                ], width=12),
                
                # ULB detailed data
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("ULB Details")),
                        dbc.CardBody([
                            html.Div(id='ulb-details-table', children=[
                                create_ulb_table(df)
                            ])
                        ])
                    ], className="mb-4")
                ], width=12)
            ])
        ], className="mt-4")
    ])

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
                dbc.NavItem(dbc.NavLink("Dashboard", href="/dashboard", active=True, className="text-white")),
                dbc.NavItem(dbc.NavLink("Reports", href="#", className="text-white")),
                dbc.NavItem(dbc.NavLink("Settings", href="#", className="text-white")),
                dbc.NavItem(dbc.Button("Logout", id="logout-button", color="light", size="sm", className="ms-2")),
            ], className="ms-auto", navbar=True),
        ]),
        color=DARK_GREEN,
        dark=True,
    )

def create_summary_cards():
    """
    Create summary metric cards with fixed size of 416 x 196 pixels.
    
    Returns:
        dash component: Row of uniform-sized summary cards
    """
    total_target = metrics['total_to_remediate']
    total_remediated = metrics['total_remediated']
    percent_complete = metrics['percent_complete']
    
    # Fixed card style
    card_style = {
        'height': '196px',
        'width': '416px',
        'margin': '0 auto',
        'border': 'none',
        'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.05)',
        'borderRadius': '8px',
        'overflow': 'hidden'
    }
    
    # Card body style for centering content
    card_body_style = {
        'height': '196px',
        'padding': '24px',
        'display': 'flex',
        'flexDirection': 'column',
        'justifyContent': 'center',
        'alignItems': 'center',
        'textAlign': 'center'
    }
    
    return dbc.Row([
        # Total target card
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Total Waste Target", className="card-title mb-3"),
                    html.H2(f"{total_target:,.0f} MT", className="text-primary mb-3"),
                    html.P("Total waste to be remediated", className="card-text text-muted mb-0")
                ], style=card_body_style)
            ], style=card_style)
        ], md=4, className="mb-4"),
        
        # Remediated card
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Remediated So Far", className="card-title mb-3"),
                    html.H2(f"{total_remediated:,.0f} MT", className="text-success mb-3"),
                    html.P(f"As of {metrics['latest_date']}", className="card-text text-muted mb-0")
                ], style=card_body_style)
            ], style=card_style)
        ], md=4, className="mb-4"),
        
        # Progress card
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Overall Progress", className="card-title mb-2"),
                    dcc.Graph(
                        figure=create_progress_gauge(percent_complete),
                        config={'displayModeBar': False},
                        style={
                            'height': '100px', 
                            'margin': '0 auto',
                            'marginBottom': '8px'
                        }
                    ),
                    html.P(f"{percent_complete:.1f}% Complete", className="card-text text-center mb-0")
                ], style=card_body_style)
            ], style=card_style)
        ], md=4, className="mb-4")
    ], className="mb-4")

def create_filters():
    """
    Create filter controls with an additional Site filter,
    compatible with dash-bootstrap-components 2.0.2.
    
    Returns:
        dash component: Filters card
    """
    vendors = sorted(df['Vendor'].unique())
    clusters = sorted(df['Cluster'].unique())
    sites = sorted(df['ULB'].unique())
    
    # Style for ensuring consistent spacing
    label_style = {
        'marginBottom': '8px',
        'fontWeight': '500'
    }
    
    # Style for the date picker container
    date_picker_container_style = {
        'display': 'flex',
        'height': '38px',
        'width': '100%'
    }
    
    return dbc.Card([
        dbc.CardHeader(html.H5("Filters")),
        dbc.CardBody([
            dbc.Row([
                # Vendor filter
                dbc.Col([
                    html.Label("Vendor", style=label_style),
                    dcc.Dropdown(
                        id='vendor-filter',
                        options=[{'label': vendor, 'value': vendor} for vendor in vendors],
                        multi=True,
                        placeholder="All Vendors"
                    )
                ], md=3, className="mb-3"),  # Adjusted width to md-3
                
                # Cluster filter
                dbc.Col([
                    html.Label("Cluster", style=label_style),
                    dcc.Dropdown(
                        id='cluster-filter',
                        options=[{'label': cluster, 'value': cluster} for cluster in clusters],
                        multi=True,
                        placeholder="All Clusters"
                    )
                ], md=3, className="mb-3"),  # Adjusted width to md-3
                
                # Site filter (new)
                dbc.Col([
                    html.Label("Site (ULB)", style=label_style),
                    dcc.Dropdown(
                        id='site-filter',
                        options=[{'label': site, 'value': site} for site in sites],
                        multi=True,
                        placeholder="All Sites"
                    )
                ], md=3, className="mb-3"),  # Width md-3
                
                # Date Range filter
                dbc.Col([
                    html.Div([
                        html.Label("Date Range", style=label_style),
                        html.Div([
                            dcc.DatePickerRange(
                                id='date-range-filter',
                                start_date='2025-05-01',
                                end_date=metrics['latest_date'],
                                display_format='YYYY-MM-DD',
                                style={'width': '100%'}
                            )
                        ], style=date_picker_container_style, className="date-range-inputs")
                    ], className="date-range-wrapper")
                ], md=3, className="mb-3")  # Adjusted width to md-3
            ], className="g-3")  # Add gutter spacing between columns
            
            # Optional: Add Reset Filters button
            ,dbc.Row([
                dbc.Col([
                    dbc.Button(
                        "Reset Filters",
                        id="reset-filters-button",
                        color="secondary",
                        size="sm",
                        className="mt-2"
                    )
                ], width={"size": 2, "offset": 10})
            ])
        ], className="p-3")  # Add padding inside card body
    ], className="mb-4")

def create_ulb_table(dataframe):
    """
    Create ULB details table with protection against division by zero.
    """
    # Get latest date column
    date_columns = [col for col in dataframe.columns if col.startswith('Cumulative Quantity')]
    latest_date_col = date_columns[-1] if date_columns else 'Quantity remediated upto 30th April 2025 in MT'
    
    # Prepare ULB data
    ulb_data = dataframe.groupby(['ULB', 'Cluster', 'Vendor']).agg({
        'Quantity to be remediated in MT': 'sum',
        'Quantity remediated upto 30th April 2025 in MT': 'sum',
        latest_date_col: 'sum'
    }).reset_index()
    
    # Initialize Percent Complete column with zeros
    ulb_data['Percent Complete'] = 0.0
    
    # Calculate percentages only for rows with non-zero targets
    mask = ulb_data['Quantity to be remediated in MT'] > 0
    if mask.any():
        ulb_data.loc[mask, 'Percent Complete'] = (
            ulb_data.loc[mask, latest_date_col] / 
            ulb_data.loc[mask, 'Quantity to be remediated in MT'] * 100
        ).round(1)
    # Prepare table columns
    columns = [
        {"name": "ULB", "id": "ULB"},
        {"name": "Cluster", "id": "Cluster"},
        {"name": "Vendor", "id": "Vendor"},
        {"name": "Target (MT)", "id": "Quantity to be remediated in MT", "type": "numeric", "format": {"specifier": ",.0f"}},
        {"name": "April (MT)", "id": "Quantity remediated upto 30th April 2025 in MT", "type": "numeric", "format": {"specifier": ",.0f"}},
        {"name": f"Current (MT)", "id": latest_date_col, "type": "numeric", "format": {"specifier": ",.0f"}},
        {"name": "Completion %", "id": "Percent Complete", "type": "numeric", "format": {"specifier": ".1f"}}
    ]
    
    return dbc.Table.from_dataframe(
        ulb_data, 
        striped=True, 
        bordered=True, 
        hover=True,
        responsive=True
    )