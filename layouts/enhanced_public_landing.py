"""
layouts/enhanced_public_landing.py - Part 1: Imports and Base Functions
"""

from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

from data_processing import get_dashboard_metrics
from visualizations.charts import create_progress_gauge
from layouts.footer import create_footer

# Theme colors
EMERALD = "#2ecc71"
DARK_GREEN = "#27ae60" 
LIGHT_GREEN = "#a9dfbf"
VERY_LIGHT_GREEN = "#ebf7f0"
ACCENT_BLUE = "#3498db"
ACCENT_ORANGE = "#e67e22"
TEXT_DARK = "#2c3e50"
TEXT_MUTED = "#7f8c8d"
BG_COLOR = "#f1f9f5"

def create_enhanced_public_landing():
    """
    Create the enhanced public landing page with square card grid layout.
    
    Returns:
        dash component: The public landing page
    """
    return html.Div(style={
        "backgroundColor": BG_COLOR, 
        "minHeight": "100vh",
        "color": TEXT_DARK,
        "fontFamily": "'Segoe UI', 'Helvetica Neue', Arial, sans-serif"
    }, children=[
        # Navbar
        create_public_navbar(),
        
        # Main content area with optimized height
        dbc.Container([
            # Status bar with clock and rotation indicator - more compact
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.I(className="fas fa-clock me-2", style={"color": DARK_GREEN}),
                        html.Span(id="navbar-clock", style={"fontWeight": 500})
                    ], className="d-flex align-items-center")
                ], sm=6, className="mb-1 mt-1"), # Reduced margin
                dbc.Col([
                    html.Div([
                        html.Span("Auto-refreshing data ", className="me-2"),
                        html.I(id="refresh-indicator", className="fas fa-sync-alt fa-spin", 
                              style={"color": DARK_GREEN})
                    ], className="d-flex align-items-center justify-content-end")
                ], sm=6, className="mb-1 mt-1 text-end") # Reduced margin
            ], className="bg-white rounded shadow-sm py-1 px-3 mb-2"), # Reduced padding
            
            # Title section - more compact
            dbc.Row([
                dbc.Col([
                    html.H2("Swaccha Andhra Waste Remediation", 
                           className="text-center mb-1", # Reduced margin
                           style={"color": DARK_GREEN, "fontWeight": "600", "fontSize": "1.6rem"}), # Smaller font
                    html.P("Real-time monitoring dashboard", 
                          className="text-center text-muted mb-2", # Reduced margin
                          style={"fontSize": "0.9rem"}) # Smaller font
                ], width=12)
            ]),
            
            # Dynamic content area with optimized height
            html.Div(id="public-landing-content", className="mb-2"), # Reduced margin
            
            # Login prompt - more compact
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Div([
                                html.I(className="fas fa-info-circle me-2", style={"color": ACCENT_BLUE}),
                                html.Span("Dashboard auto-rotates to show all vendor data", 
                                         style={"color": TEXT_DARK, "fontWeight": 500, "fontSize": "0.9rem"})
                            ], className="d-flex align-items-center")
                        ], sm=8),
                        dbc.Col([
                            dbc.Button([
                                html.I(className="fas fa-user-lock me-2"),
                                "Login for Controls"
                            ], color="primary", href="/login", className="w-100", size="sm") # Smaller button
                        ], sm=4, className="d-flex align-items-center justify-content-end")
                    ])
                ], className="py-2") # Reduced padding
            ], className="shadow-sm mb-2 border-0"), # Reduced margin
            
            # Store component to maintain view state
            dcc.Store(id='public-view-state', data={
                'view_type': 'overview',
                'current_vendor_index': 0,
                'rotation_count': 0
            }),
        ], fluid=True, className="py-2 px-3"), # Reduced padding
        
        # Simplified footer for better fit
        html.Footer(
            dbc.Container([
                html.Hr(style={"margin": "10px 0"}), # Reduced margin
                html.Div([
                    html.P([
                        "Made in Andhra Pradesh, with ",
                        html.I(className="fas fa-heart", style={"color": "#e74c3c"}),
                        " • © 2025 Advitia Labs"
                    ], className="text-center text-muted small mb-0") # Smaller font
                ])
            ]),
            style={
                "padding": "5px 0 10px 0", # Reduced padding
                "marginTop": "5px", # Reduced margin
            }
        )
    ])

def create_public_navbar():
    """
    Create a navbar for the public landing page with optimized height.
    
    Returns:
        dash component: The navbar component
    """
    return dbc.Navbar(
        dbc.Container([
            html.A(
                dbc.Row([
                    dbc.Col(html.I(className="fas fa-leaf", 
                                   style={"fontSize": "22px", "color": "white"}), # Smaller icon
                            width="auto"),
                    dbc.Col([
                        dbc.NavbarBrand("Swaccha Andhra", 
                                       style={"color": "white", "fontWeight": "bold", "fontSize": "18px"}), # Smaller font
                        html.Span("Corporation", 
                                 style={"color": "rgba(255,255,255,0.8)", "fontSize": "11px", "display": "block", "marginTop": "-5px"}) # Smaller font
                    ], width="auto")
                ], align="center", className="g-0"),
                href="/",
                style={"textDecoration": "none"}
            ),
            dbc.Nav([
                dbc.Button([
                    html.I(className="fas fa-sign-in-alt me-2"),
                    "Login"
                ], 
                id="login-nav-button", 
                color="light", 
                size="sm", # Smaller button
                className="ms-2 fw-bold",
                href="/login")
            ], className="ms-auto", navbar=True),
        ]),
        color=DARK_GREEN,
        dark=True,
        className="mb-2 py-1 shadow", # Reduced padding
        style={"minHeight": "42px"} # Fixed smaller height
    )


def create_overview_content(df, metrics):
    """
    Create an optimized grid showing waste remediation overview with enhancements:
    1. Optimized histogram width
    2. Fixed cluster label formatting
    3. Consistent card heights
    4. Layout fits one screen without scrolling
    
    Args:
        df (pandas.DataFrame): The dashboard data
        metrics (dict): Pre-calculated metrics
        
    Returns:
        dash component: The overview content
    """
    # Get latest date for display
    latest_date = metrics['latest_date']
    
    # Get all date columns for weekly progress
    date_columns = [col for col in df.columns if col.startswith('Cumulative Quantity')]
    
    # Get all vendors and their stats
    vendors = sorted(df['Vendor'].unique())
    vendor_stats = metrics['vendor_stats']
    cluster_stats = metrics['cluster_stats']
    
    # Set fixed height for all cards
    main_card_height = "220px"
    vendor_card_height = "180px"
    
    # ===== CARD 1: Overall Progress Gauge =====
    # Create chart with appropriate size
    progress_gauge = create_progress_gauge(metrics['percent_complete'])
    progress_gauge.update_layout(height=120, margin=dict(l=5, r=5, t=5, b=5))
    
    card1 = dbc.Card([
        dbc.CardHeader([
            html.I(className="fas fa-chart-pie me-2", style={"color": DARK_GREEN}),
            "Overall Progress"
        ], className="d-flex align-items-center fw-bold bg-white py-1"), # Minimal padding
        dbc.CardBody([
            # Center the gauge
            html.Div([
                # Date info
                html.Div([
                    html.Span("Data as of ", className="me-1"),
                    html.Span(latest_date, 
                             style={"fontWeight": "500", "color": ACCENT_ORANGE, "fontSize": "0.8rem"})
                ], className="text-center mb-1"),
                
                # Progress gauge - smaller size
                dcc.Graph(
                    figure=progress_gauge,
                    config={'displayModeBar': False},
                    style={'height': '120px'}
                ),
                
                # Statistics below gauge
                html.Div([
                    html.Div([
                        html.Div([
                            html.Span("Remediated: ", className="me-1 text-muted small"),
                            html.Span(f"{metrics['total_remediated']:,.0f} MT", 
                                     style={"fontWeight": "500", "color": DARK_GREEN}, className="small")
                        ], className="me-2"),
                        html.Div([
                            html.Span("Target: ", className="me-1 text-muted small"),
                            html.Span(f"{metrics['total_to_remediate']:,.0f} MT", 
                                     style={"fontWeight": "500"}, className="small")
                        ])
                    ], className="d-flex justify-content-center")
                ], className="mt-1")
            ], className="d-flex flex-column justify-content-center align-items-center h-100")
        ], className="p-2", style={"height": "calc(100% - 38px)"}) # Fixed height minus header
    ], className="shadow-sm border-0 h-100", style={"height": main_card_height})
    
    # ===== CARD 2: Lagging Clusters Histogram =====
    # Sort clusters by completion percentage
    sorted_clusters = cluster_stats.sort_values('Percent Complete')
    # Take bottom clusters - reduce to 5 for better fit
    lagging_clusters = sorted_clusters.head(5)
    
    # Format text values for labels - Fix for the %{text}% issue
    lagging_clusters['Label'] = lagging_clusters['Percent Complete'].apply(lambda x: f"{x:.1f}%")
    
    # Create histogram for lagging clusters - optimized width
    lagging_fig = px.bar(
        lagging_clusters,
        x='Cluster',
        y='Percent Complete',
        color='Percent Complete',
        color_continuous_scale=[[0, 'lightgray'], [0.5, LIGHT_GREEN], [1, DARK_GREEN]],
        labels={'Percent Complete': 'Completion %', 'Cluster': 'Cluster'},
        text='Label'  # Fixed text formatting
    )
    
    lagging_fig.update_traces(
        textposition='outside',
        marker_line_width=0
    )
    
    lagging_fig.update_layout(
        margin=dict(l=10, r=10, t=5, b=30), # Reduced margins
        paper_bgcolor='white',
        plot_bgcolor='white',
        height=160, # Optimized height
        xaxis=dict(
            title="", # Removed title to save space
            tickangle=-45,
            tickfont=dict(size=8), # Smaller font
            automargin=True, # Auto adjust margins
            # Limit maximum width by reducing range if needed
            constrain="domain",
            constraintoward="center"
        ),
        yaxis=dict(
            title="Completion %",
            range=[0, 100],
            ticksuffix="%",
            title_font=dict(size=9), # Smaller font
            tickfont=dict(size=8) # Smaller font
        ),
        coloraxis_showscale=False
    )
    
    card2 = dbc.Card([
        dbc.CardHeader([
            html.I(className="fas fa-exclamation-triangle me-2", style={"color": ACCENT_ORANGE}),
            "Lagging Clusters"
        ], className="d-flex align-items-center fw-bold bg-white py-1"), # Minimal padding
        dbc.CardBody([
            dcc.Graph(
                figure=lagging_fig,
                config={'displayModeBar': False}
            )
        ], className="p-1", style={"height": "calc(100% - 38px)"}) # Fixed height minus header
    ], className="shadow-sm border-0 h-100", style={"height": main_card_height})
    
    # ===== CARDS 3-6: Vendor Summary Cards =====
    # Take top 4 vendors for cards 3-6
    top_vendors = vendor_stats.head(4) if len(vendors) > 4 else vendor_stats
    vendor_cards = []
    
    for i, (_, vendor_row) in enumerate(top_vendors.iterrows()):
        vendor_name = vendor_row['Vendor']
        vendor_df = df[df['Vendor'] == vendor_name]
        
        # Calculate completion percentage
        vendor_target = vendor_row['Quantity to be remediated in MT']
        vendor_remediated = vendor_row[metrics['latest_date_col']]
        vendor_percent = vendor_row['Percent Complete']
        
        # Get weekly progress (last 5 days for smaller chart)
        if len(date_columns) > 5:
            weekly_columns = date_columns[-5:]
        else:
            weekly_columns = date_columns
        
        weekly_data = []
        for col in weekly_columns:
            date_str = col.split('(')[1].split(')')[0]
            total = vendor_df[col].sum()
            weekly_data.append({'Date': date_str, 'Total': total})
        
        weekly_df = pd.DataFrame(weekly_data)
        
        # Convert to date type and sort
        weekly_df['Date'] = pd.to_datetime(weekly_df['Date'])
        weekly_df = weekly_df.sort_values('Date')
        
        # Calculate daily increase
        weekly_df['Daily'] = weekly_df['Total'].diff().fillna(0)
        
        # Weekly progress mini chart - smaller and more compact
        weekly_fig = px.bar(
            weekly_df,
            x='Date',
            y='Daily',
            labels={'Daily': 'MT/day', 'Date': ''},
            color='Daily',
            color_continuous_scale=[[0, LIGHT_GREEN], [1, DARK_GREEN]]
        )
        
        weekly_fig.update_layout(
            margin=dict(l=0, r=0, t=0, b=0), # Minimal margins
            paper_bgcolor='white',
            plot_bgcolor='white',
            height=50, # Very small height
            showlegend=False,
            xaxis=dict(
                showticklabels=False, # Hide labels to save space
                showgrid=False,
                zeroline=False
            ),
            yaxis=dict(
                showticklabels=False, # Hide labels to save space
                showgrid=False,
                zeroline=False
            ),
            coloraxis_showscale=False
        )
        
        # Get vendor's lagging clusters
        vendor_clusters = vendor_df.groupby('Cluster').agg({
            'Quantity to be remediated in MT': 'sum',
            metrics['latest_date_col']: 'sum'
        }).reset_index()
        
        vendor_clusters['Percent Complete'] = 0.0
        mask = vendor_clusters['Quantity to be remediated in MT'] > 0
        if mask.any():
            vendor_clusters.loc[mask, 'Percent Complete'] = (
                vendor_clusters.loc[mask, metrics['latest_date_col']] / 
                vendor_clusters.loc[mask, 'Quantity to be remediated in MT'] * 100
            ).round(1)
        
        # Sort by percent complete and get bottom 1
        vendor_clusters = vendor_clusters.sort_values('Percent Complete')
        lagging_vendor_clusters = vendor_clusters.head(1)
        
        # Create vendor card - ultra compact
        vendor_card = dbc.Card([
            dbc.CardHeader([
                html.I(className="fas fa-building me-2", style={"color": DARK_GREEN}),
                vendor_name
            ], className="d-flex align-items-center fw-bold bg-white py-1 small"), # Minimal padding, smaller text
            dbc.CardBody([
                # Two-column layout for better space usage
                dbc.Row([
                    # Left column: Progress and metrics
                    dbc.Col([
                        # Progress percentage with colored pill
                        html.Div([
                            dbc.Badge(
                                f"{vendor_percent:.1f}%", 
                                color="success" if vendor_percent > 50 else "warning",
                                className="py-1 px-2 mb-1"
                            ),
                        ], className="text-center"),
                        
                        # Target/Remediated as inline text
                        html.Div([
                            html.Span(f"{vendor_remediated:,.0f}", 
                                     style={"fontWeight": "500", "color": DARK_GREEN, "fontSize": "0.75rem"}),
                            html.Span(" / ", className="mx-1", style={"fontSize": "0.75rem"}),
                            html.Span(f"{vendor_target:,.0f}", 
                                     style={"fontWeight": "500", "fontSize": "0.75rem"})
                        ], className="text-center small"),
                        
                        # Small label for MT
                        html.Div([
                            html.Span("MT", className="text-muted", style={"fontSize": "0.7rem"})
                        ], className="text-center"),
                        
                        # Lagging cluster in tiny text
                        html.Div([
                            *[html.Div([
                                html.Span("Lagging: ", className="text-muted", style={"fontSize": "0.7rem"}),
                                html.Span(f"{row['Cluster'].split()[0]}", 
                                         style={"fontSize": "0.7rem", "fontWeight": "500"})
                            ], className="text-center") for _, row in lagging_vendor_clusters.iterrows()]
                        ], className="mt-1")
                    ], xs=5, className="pe-0"),
                    
                    # Right column: Weekly chart
                    dbc.Col([
                        html.Div([
                            html.Span("Weekly", className="text-muted", style={"fontSize": "0.7rem"})
                        ], className="text-center mb-1"),
                        
                        # Chart takes up remaining space
                        dcc.Graph(
                            figure=weekly_fig,
                            config={'displayModeBar': False}
                        )
                    ], xs=7, className="ps-0")
                ], className="g-0") # No gutters
            ], className="p-2", style={"height": "calc(100% - 31px)"}) # Fixed height minus smaller header
        ], className="shadow-sm border-0 h-100", style={"height": vendor_card_height})
        
        vendor_cards.append(vendor_card)

    while len(vendor_cards) < 4:
        # Add placeholder card
        placeholder_card = dbc.Card([
            dbc.CardHeader([
                html.I(className="fas fa-building me-2", style={"color": DARK_GREEN}),
                "No Data"
            ], className="d-flex align-items-center fw-bold bg-white py-1 small"), # Minimal padding, smaller text
            dbc.CardBody([
                html.Div([
                    html.I(className="fas fa-exclamation-circle mb-2", 
                          style={"fontSize": "20px", "color": TEXT_MUTED}),
                    html.P("No vendor data available", className="text-muted small mb-0")
                ], className="d-flex flex-column justify-content-center align-items-center h-100")
            ], className="p-2", style={"height": "calc(100% - 31px)"}) # Fixed height minus header
        ], className="shadow-sm border-0 h-100", style={"height": vendor_card_height})
        
        vendor_cards.append(placeholder_card)
    
    # Create optimized layout with cards in grid
    return dbc.Container([
        # Top row - Overall Progress and Lagging Clusters side by side
        dbc.Row([
            # Card 1: Overall Progress Gauge
            dbc.Col([card1], xs=12, md=6, className="mb-2"),
            
            # Card 2: Lagging Clusters
            dbc.Col([card2], xs=12, md=6, className="mb-2")
        ], className="g-2"), # Reduced gap
        
        # Bottom row - Vendor summary cards in a grid
        dbc.Row([
            # Cards 3-6: Vendor summary cards
            dbc.Col([vendor_cards[0]], xs=12, sm=6, md=3, className="mb-2"),
            dbc.Col([vendor_cards[1]], xs=12, sm=6, md=3, className="mb-2"),
            dbc.Col([vendor_cards[2]], xs=12, sm=6, md=3, className="mb-2"),
            dbc.Col([vendor_cards[3]], xs=12, sm=6, md=3, className="mb-2")
        ], className="g-2") # Reduced gap
    ], fluid=True, className="p-0") # Removed padding to fit better in one view


def create_vendor_content(df, vendor_name):
    """
    Create an optimized grid layout for vendor-specific view with enhancements:
    1. Three metrics cards in one row to reduce white space
    2. Optimized histogram width
    3. Fixed cluster performance labels
    4. Consistent card heights
    5. Single site card when fewer than 3 sites
    6. Layout fits one screen without scrolling
    
    Args:
        df (pandas.DataFrame): The dashboard data
        vendor_name (str): The vendor to display
        
    Returns:
        dash component: The vendor-specific content
    """
    # Filter data for the selected vendor
    vendor_df = df[df['Vendor'] == vendor_name].copy()
    
    # If no data for this vendor, show an error card
    if vendor_df.empty:
        return dbc.Card([
            dbc.CardBody([
                html.Div([
                    html.I(className="fas fa-exclamation-triangle me-2", 
                          style={"fontSize": "2rem", "color": ACCENT_ORANGE}),
                    html.H2(f"No data available for {vendor_name}", className="mb-0")
                ], className="d-flex align-items-center justify-content-center")
            ], className="py-4")
        ], className="shadow-sm border-0 my-2")
    
    # Get latest date column
    date_columns = [col for col in vendor_df.columns if col.startswith('Cumulative Quantity')]
    latest_date_col = date_columns[-1] if date_columns else 'Quantity remediated upto 30th April 2025 in MT'
    latest_date = latest_date_col.split('(')[1].split(')')[0] if '(' in latest_date_col else '2025-04-30'
    
    # Calculate vendor metrics
    total_target = vendor_df['Quantity to be remediated in MT'].sum()
    total_remediated = vendor_df[latest_date_col].sum()
    
    # Calculate percentage with protection against division by zero
    percent_complete = 0
    if total_target > 0:
        percent_complete = (total_remediated / total_target) * 100
    
    # Get all clusters for this vendor
    vendor_clusters = sorted(vendor_df['Cluster'].unique())
    
    # --- CARD 1: Vendor Progress Gauge ---
    # Set fixed height for all cards
    card_height = "220px"
    
    # Create chart with appropriate size
    progress_gauge = create_progress_gauge(percent_complete)
    progress_gauge.update_layout(height=120, margin=dict(l=5, r=5, t=5, b=5))
    
    card1 = dbc.Card([
        dbc.CardHeader([
            html.I(className="fas fa-chart-pie me-2", style={"color": DARK_GREEN}),
            f"{vendor_name} Progress"
        ], className="d-flex align-items-center fw-bold bg-white py-1"), # Minimal padding
        dbc.CardBody([
            # Center the gauge
            html.Div([
                # Date info
                html.Div([
                    html.Span("Data as of ", className="me-1"),
                    html.Span(latest_date, 
                             style={"fontWeight": "500", "color": ACCENT_ORANGE, "fontSize": "0.8rem"})
                ], className="text-center mb-1"),
                
                # Progress gauge - smaller size
                dcc.Graph(
                    figure=progress_gauge,
                    config={'displayModeBar': False},
                    style={'height': '120px'}
                ),
                
                # Statistics below gauge
                html.Div([
                    html.Div([
                        html.Div([
                            html.Span("Remediated: ", className="me-1 text-muted small"),
                            html.Span(f"{total_remediated:,.0f} MT", 
                                     style={"fontWeight": "500", "color": DARK_GREEN}, className="small")
                        ], className="me-2"),
                        html.Div([
                            html.Span("Target: ", className="me-1 text-muted small"),
                            html.Span(f"{total_target:,.0f} MT", 
                                     style={"fontWeight": "500"}, className="small")
                        ])
                    ], className="d-flex justify-content-center")
                ], className="mt-1")
            ], className="d-flex flex-column justify-content-center align-items-center h-100")
        ], className="p-2", style={"height": "calc(100% - 38px)"}) # Fixed height minus header
    ], className="shadow-sm border-0 h-100", style={"height": card_height})
    
    # --- CARD 2: Clusters Performance ---
    # Calculate cluster performance for this vendor
    cluster_data = vendor_df.groupby('Cluster').agg({
        'Quantity to be remediated in MT': 'sum',
        latest_date_col: 'sum'
    }).reset_index()
    
    # Calculate percent complete for each cluster
    cluster_data['Percent Complete'] = 0.0
    mask = cluster_data['Quantity to be remediated in MT'] > 0
    if mask.any():
        cluster_data.loc[mask, 'Percent Complete'] = (
            cluster_data.loc[mask, latest_date_col] / 
            cluster_data.loc[mask, 'Quantity to be remediated in MT'] * 100
        ).round(1)

