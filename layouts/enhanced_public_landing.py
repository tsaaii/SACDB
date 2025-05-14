"""
layouts/enhanced_public_landing.py - Enhanced Public Landing Page

This file defines the enhanced public landing page layout optimized for
auto-rotation between overview and vendor-specific views.

Enhancements:
1. Three metrics cards in one row to reduce white space
2. Optimized histogram width
3. Fixed cluster performance labels
4. Consistent card heights
5. Single site card when fewer than 3 sites
6. Layout fits one screen without scrolling
7. Compatibility fixes for different Plotly versions
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
ACCENT_ORANGE = "#e74c3c"
TEXT_DARK = "#2c3e50"
TEXT_MUTED = "#7f8c8d"
BG_COLOR = "#f1f9f5"

def create_public_navbar():
    """
    Create a navbar for the public landing page with optimized height.
    Enhanced to be even smaller/compact based on login button size.
    
    Returns:
        dash component: The navbar component
    """
    return dbc.Navbar(
        dbc.Container([
            html.A(
                dbc.Row([
                    dbc.Col(html.I(className="fas fa-leaf", 
                                   style={"fontSize": "18px", "color": "white"}), # Even smaller icon
                            width="auto"),
                    dbc.Col([
                        dbc.NavbarBrand("Swaccha Andhra", 
                                       style={"color": "white", "fontWeight": "bold", "fontSize": "15px"}), # Smaller font
                        html.Span("Corporation", 
                                 style={"color": "rgba(255,255,255,0.8)", "fontSize": "10px", "display": "block", "marginTop": "-5px"}) # Smaller font
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
        className="mb-2 py-0 shadow", # Further reduced padding
        style={"minHeight": "36px"} # Even smaller fixed height
    )

def create_enhanced_public_landing():
    """
    Enhanced public landing page with:
    - Combined title and subtitle in green
    - Auto-refresh interval changed to 15 seconds
    
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
            
            # Combined Title section - all in green with one styling
            dbc.Row([
                dbc.Col([
                    html.H2([
                        "Swaccha Andhra Waste Remediation ",
                        html.Small("Real-time monitoring dashboard", 
                                  className="d-block", 
                                  style={"fontSize": "0.9rem", "fontWeight": "400"})
                    ], className="text-center mb-2", # Reduced margin
                       style={"color": DARK_GREEN, "fontWeight": "600", "fontSize": "1.6rem"}) # All in green
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
            
            # Auto rotation interval - Changed from 60s to 15s
            dcc.Interval(
                id='auto-rotation-interval',
                interval=15 * 1000,  # 15 seconds in milliseconds (reduced from 60s)
                n_intervals=0,
                disabled=True  # Initially disabled, enabled only on landing page
            ),
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


def create_overview_content(df, metrics):
    """
    Create an optimized grid showing waste remediation overview with enhancements:
    1. Optimized histogram width
    2. Fixed cluster label formatting
    3. Consistent card heights
    4. Layout fits one screen without scrolling
    5. Added axis labels to charts
    6. Improved spacing between cards
    7. Clearer legends
    
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
    
    # Set fixed height for all cards - slightly reduced for better spacing
    main_card_height = "210px"
    vendor_card_height = "170px"
    
    # ===== CARD 1: Overall Progress Gauge =====
    # Create chart with appropriate size
    progress_gauge = create_progress_gauge(metrics['percent_complete'])
    progress_gauge.update_layout(height=110, margin=dict(l=5, r=5, t=5, b=5))
    
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
                
                # Progress gauge - smaller size and centered
                dcc.Graph(
                    figure=progress_gauge,
                    config={'displayModeBar': False},
                    style={'height': '110px', 'width': '100%'} # Full width ensures centering
                ),
                
                # Legend below gauge - ADDED
                html.Div([
                    html.Span(f"{metrics['percent_complete']:.1f}% of waste remediated", 
                             style={"fontWeight": "500", "color": DARK_GREEN, "fontSize": "0.9rem"})
                ], className="text-center mb-2"),
                
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
    
    # Create a more basic horizontal bar chart using go.Figure instead of px.bar
    lagging_fig = go.Figure()
    
    # Add the bars in reverse order so lowest is at the bottom
    lagging_fig.add_trace(go.Bar(
        y=lagging_clusters['Cluster'],
        x=lagging_clusters['Percent Complete'],
        orientation='h',
        marker=dict(
            color=lagging_clusters['Percent Complete'],
            colorscale=[[0, 'lightgray'], [0.5, LIGHT_GREEN], [1, DARK_GREEN]]
        ),
        text=lagging_clusters['Percent Complete'].apply(lambda x: f"{x:.1f}%"),
        textposition='outside',
        hovertemplate='%{y}: %{text}<extra></extra>'
    ))
    
    # Optimize layout for compact display with axis labels
    lagging_fig.update_layout(
        margin=dict(l=10, r=10, t=5, b=30), # Adjusted margins for labels
        paper_bgcolor='white',
        plot_bgcolor='white',
        showlegend=False,
        xaxis=dict(
            title="Completion Percentage",  # Added axis label
            title_font=dict(size=9),  # Small title font
            ticksuffix="%",
            range=[0, 100],
            tickfont=dict(size=8),  # Smaller font
            showgrid=True,
            gridcolor='rgba(0,0,0,0.05)'
        ),
        yaxis=dict(
            title="Cluster",  # Added axis label
            title_font=dict(size=9),  # Small title font
            tickfont=dict(size=8),  # Smaller font
            automargin=True  # Auto adjust margins
        ),
        height=150
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
        
        # Weekly progress mini chart - smaller and more compact using go.Figure
        weekly_fig = go.Figure()
        
        # Add the bars
        weekly_fig.add_trace(go.Bar(
            x=weekly_df['Date'].dt.strftime('%d'),  # Just show day number for compact display
            y=weekly_df['Daily'],
            marker=dict(
                color=DARK_GREEN
            ),
            hovertemplate='Day %{x}: %{y:.0f} MT<extra></extra>'
        ))
        
        weekly_fig.update_layout(
            margin=dict(l=0, r=0, t=0, b=0), # Minimal margins
            paper_bgcolor='white',
            plot_bgcolor='white',
            height=50, # Very small height
            showlegend=False,
            xaxis=dict(
                title='',
                showticklabels=False, # Hide labels to save space
                showgrid=False,
                zeroline=False
            ),
            yaxis=dict(
                title='',
                showticklabels=False, # Hide labels to save space
                showgrid=False,
                zeroline=False
            )
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
    
    # Create optimized layout with cards in grid and more spacing
    return dbc.Container([
        # Top row - Overall Progress and Lagging Clusters side by side
        dbc.Row([
            # Card 1: Overall Progress Gauge
            dbc.Col([card1], xs=12, md=6, className="mb-3"),  # Increased margin
            
            # Card 2: Lagging Clusters
            dbc.Col([card2], xs=12, md=6, className="mb-3")  # Increased margin
        ], className="g-3"),  # Increased gutter
        
        # Extra spacing between sections
        html.Div(className="mb-2"),  # Added spacer
        
        # Bottom row - Vendor summary cards in a grid
        dbc.Row([
            # Cards 3-6: Vendor summary cards
            dbc.Col([vendor_cards[0]], xs=12, sm=6, md=3, className="mb-3"),  # Increased margin
            dbc.Col([vendor_cards[1]], xs=12, sm=6, md=3, className="mb-3"),  # Increased margin
            dbc.Col([vendor_cards[2]], xs=12, sm=6, md=3, className="mb-3"),  # Increased margin
            dbc.Col([vendor_cards[3]], xs=12, sm=6, md=3, className="mb-3")   # Increased margin
        ], className="g-3")  # Increased gutter
    ], fluid=True, className="p-0")  # Removed padding for better fit
    
    # Create optimized layout with cards in grid and more spacing
    return dbc.Container([
        # Top row - Overall Progress and Lagging Clusters side by side
        dbc.Row([
            # Card 1: Overall Progress Gauge
            dbc.Col([card1], xs=12, md=6, className="mb-3"),  # Increased margin
            
            # Card 2: Lagging Clusters
            dbc.Col([card2], xs=12, md=6, className="mb-3")  # Increased margin
        ], className="g-3"),  # Increased gutter
        
        # Extra spacing between sections
        html.Div(className="mb-2"),  # Added spacer
        
        # Bottom row - Vendor summary cards in a grid
        dbc.Row([
            # Cards 3-6: Vendor summary cards
            dbc.Col([vendor_cards[0]], xs=12, sm=6, md=3, className="mb-3"),  # Increased margin
            dbc.Col([vendor_cards[1]], xs=12, sm=6, md=3, className="mb-3"),  # Increased margin
            dbc.Col([vendor_cards[2]], xs=12, sm=6, md=3, className="mb-3"),  # Increased margin
            dbc.Col([vendor_cards[3]], xs=12, sm=6, md=3, className="mb-3")   # Increased margin
        ], className="g-3")  # Increased gutter
    ], fluid=True, className="p-0")  # Removed padding for better fit

def create_vendor_content(df, vendor_name):
    """
    Create an optimized grid layout for vendor-specific view with enhancements:
    1. Added vendor name at the top
    2. Centered gauge in progress card with legend
    3. Added axis labels to charts
    4. Improved padding between card rows
    5. Reduced card sizes for better spacing
    
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
                          style={"fontSize": "2rem", "color":'#e74c3c'}),
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
    
    # Get all ULBs (sites) for this vendor
    vendor_sites = sorted(vendor_df['ULB'].unique())
    
    # Set fixed height for all cards - slightly reduced for better spacing
    fixed_card_height = "185px"
    site_card_height = "calc(100% - 38px)"  # Slightly less to account for header
    
    # Add vendor name and summary at the top
    vendor_header = dbc.Row([
        dbc.Col([
            html.Div([
                html.H3([
                    html.I(className="fas fa-building me-2", style={"color": DARK_GREEN}),
                    f"Vendor: {vendor_name}"
                ], style={"color": DARK_GREEN, "fontSize": "1.4rem", "fontWeight": "600"}),
                html.P([
                    f"Progress Summary: ",
                    html.Span(f"{percent_complete:.1f}% Complete", 
                             style={"fontWeight": "600", "color": DARK_GREEN}),
                    f" ({total_remediated:,.0f} MT of {total_target:,.0f} MT)"
                ], className="mb-0", style={"fontSize": "0.9rem"})
            ], className="bg-white p-2 rounded shadow-sm")
        ], width=12)
    ], className="mb-4")  # More padding between sections
    
    # Create three metrics cards in one row
    # --- CARD 1-3: Vendor Metrics Row - combined into one row to reduce whitespace ---
    metrics_cards_row = dbc.Row([
        # CARD 1: Vendor Progress Gauge (smaller width to fit three cards)
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.I(className="fas fa-chart-pie me-2", style={"color": DARK_GREEN}),
                    f"{vendor_name} Progress"  # Added vendor name to header
                ], className="d-flex align-items-center fw-bold bg-white py-1 small"), # Smaller text
                dbc.CardBody([
                    # Center the gauge and add legend
                    html.Div([
                        # Date info with reduced size
                        html.Div([
                            html.Span("As of ", className="me-1 small text-muted"),
                            html.Span(latest_date, style={"fontWeight": "500", "color": ACCENT_ORANGE, "fontSize": "0.75rem"})
                        ], className="text-center mb-1"),
                        
                        # Create gauge
                        dcc.Graph(
                            figure=create_progress_gauge(percent_complete),
                            config={'displayModeBar': False},
                            style={'height': '90px', 'width': '100%', 'margin': '0 auto'}  # Fixed width to 100%
                        ),
                        
                        # Legend below gauge - ADDED
                        html.Div([
                            html.Span(f"{percent_complete:.1f}% of waste remediated", 
                                     style={"fontWeight": "500", "color": DARK_GREEN, "fontSize": "0.9rem"})
                        ], className="text-center mt-1")
                    ], className="d-flex flex-column justify-content-center align-items-center h-100 text-center")
                ], className="p-2", style={"height": site_card_height})
            ], className="shadow-sm border-0 h-100", style={"height": fixed_card_height})
        ], xs=12, md=4, className="mb-2"),
        
        # CARD 2: Cluster Performance (middle card)
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.I(className="fas fa-layer-group me-2", style={"color": DARK_GREEN}),
                    "Cluster Performance"
                ], className="d-flex align-items-center fw-bold bg-white py-1 small"), # Smaller text
                dbc.CardBody([
                    # Create cluster performance visualization
                    create_cluster_performance_chart(vendor_df, latest_date_col)
                ], className="p-2", style={"height": site_card_height})
            ], className="shadow-sm border-0 h-100", style={"height": fixed_card_height})
        ], xs=12, md=4, className="mb-2"),
        
        # CARD 3: Weekly Progress (right card)
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.I(className="fas fa-calendar-week me-2", style={"color": DARK_GREEN}),
                    "Weekly Progress"
                ], className="d-flex align-items-center fw-bold bg-white py-1 small"), # Smaller text
                dbc.CardBody([
                    # Create weekly progress chart
                    create_weekly_progress_chart(vendor_df, date_columns)
                ], className="p-2", style={"height": site_card_height})
            ], className="shadow-sm border-0 h-100", style={"height": fixed_card_height})
        ], xs=12, md=4, className="mb-2")
    ], className="g-3")  # Increased gap between cards
    
    # --- CARD 4: Sites Performance ---
    # Determine if we should use a single card or multiple based on number of sites
    sites_row = None
    
    # If fewer than 3 sites, use just one card
    if len(vendor_sites) < 3:
        sites_row = dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="fas fa-map-marker-alt me-2", style={"color": DARK_GREEN}),
                        "Sites Progress"
                    ], className="d-flex align-items-center fw-bold bg-white py-1 small"), # Smaller text
                    dbc.CardBody([
                        create_sites_performance_chart(vendor_df, latest_date_col, vendor_sites)
                    ], className="p-2", style={"height": site_card_height})
                ], className="shadow-sm border-0 h-100", style={"height": fixed_card_height})
            ], xs=12, className="mb-2")
        ], className="g-3")  # Increased gap
    else:
        # Create three site cards (top 3 ULBs by target size)
        top_sites = vendor_df.groupby('ULB').agg({
            'Quantity to be remediated in MT': 'sum'
        }).reset_index().sort_values('Quantity to be remediated in MT', ascending=False).head(3)['ULB'].tolist()
        
        sites_row = dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="fas fa-map-marker-alt me-2", style={"color": DARK_GREEN}),
                        f"Site: {site}"
                    ], className="d-flex align-items-center fw-bold bg-white py-1 small"), # Smaller text
                    dbc.CardBody([
                        create_site_card_content(vendor_df, latest_date_col, site)
                    ], className="p-2", style={"height": site_card_height})
                ], className="shadow-sm border-0 h-100", style={"height": fixed_card_height})
            ], xs=12, md=4, className="mb-2") for site in top_sites
        ], className="g-3")  # Increased gap
    
    # Full layout with increased spacing between sections
    return dbc.Container([
        # Vendor name and summary at the top
        vendor_header,
        
        # Top row - Metrics cards combined in a single row
        metrics_cards_row,
        
        # Extra padding between rows
        html.Div(className="mb-4"),  # Added spacer
        
        # Bottom row - Site cards
        sites_row
    ], fluid=True, className="p-0") # Remove padding for better fit


# Helper functions for vendor_content - Enhanced with axis labels and better formatting

def create_cluster_performance_chart(vendor_df, latest_date_col):
    """
    Create a compact horizontal bar chart showing cluster performance.
    Enhanced with axis labels and better formatting.
    
    Args:
        vendor_df (pandas.DataFrame): Vendor-specific data
        latest_date_col (str): Latest date column name
        
    Returns:
        dash component: Chart component
    """
    # Calculate cluster performance
    cluster_data = vendor_df.groupby('Cluster').agg({
        'Quantity to be remediated in MT': 'sum',
        latest_date_col: 'sum'
    }).reset_index()
    
    # Calculate percent complete with zero protection
    cluster_data['Percent Complete'] = 0.0
    mask = cluster_data['Quantity to be remediated in MT'] > 0
    if mask.any():
        cluster_data.loc[mask, 'Percent Complete'] = (
            cluster_data.loc[mask, latest_date_col] / 
            cluster_data.loc[mask, 'Quantity to be remediated in MT'] * 100
        ).round(1)
    
    # Sort by percentage (ascending for better visualization)
    cluster_data = cluster_data.sort_values('Percent Complete', ascending=True)
    
    # Limiting to 5 clusters for better display
    if len(cluster_data) > 5:
        cluster_data = cluster_data.tail(5)
    
    # Create a more basic horizontal bar chart using go.Figure instead of px.bar
    fig = go.Figure()
    
    # Add the bars
    fig.add_trace(go.Bar(
        x=cluster_data['Percent Complete'],
        y=cluster_data['Cluster'],
        orientation='h',
        marker=dict(
            color=cluster_data['Percent Complete'],
            colorscale=[[0, 'lightgray'], [0.5, LIGHT_GREEN], [1, DARK_GREEN]]
        ),
        text=cluster_data['Percent Complete'].apply(lambda x: f"{x:.1f}%"),
        textposition='outside',
        hovertemplate='%{y}: %{text}<extra></extra>'
    ))
    
    # Optimize layout for compact display with axis labels
    fig.update_layout(
        margin=dict(l=10, r=10, t=5, b=20),  # Adjusted margins for labels
        paper_bgcolor='white',
        plot_bgcolor='white',
        showlegend=False,
        xaxis=dict(
            title='Completion Percentage',  # Added axis label
            title_font=dict(size=9),  # Small title font
            ticksuffix='%',
            range=[0, max(100, cluster_data['Percent Complete'].max() * 1.1)],
            tickfont=dict(size=8),  # Smaller font
            showgrid=True,
            gridcolor='rgba(0,0,0,0.05)'
        ),
        yaxis=dict(
            title='Cluster',  # Added axis label
            title_font=dict(size=9),  # Small title font
            tickfont=dict(size=8),  # Smaller font
            automargin=True  # Auto adjust margins
        ),
        height=140  # Slightly reduced height
    )
    
    return dcc.Graph(
        figure=fig,
        config={'displayModeBar': False},
        style={'height': '140px'}
    )

def create_weekly_progress_chart(vendor_df, date_columns):
    """
    Create a compact chart showing weekly progress.
    Enhanced with axis labels and better formatting.
    
    Args:
        vendor_df (pandas.DataFrame): Vendor-specific data
        date_columns (list): List of date columns
        
    Returns:
        dash component: Chart component
    """
    # Use last 7 days (or all if less than 7)
    if len(date_columns) > 7:
        weekly_columns = date_columns[-7:]
    else:
        weekly_columns = date_columns
    
    # Prepare data
    weekly_data = []
    for col in weekly_columns:
        try:
            date_str = col.split('(')[1].split(')')[0]
            total = vendor_df[col].sum()
            weekly_data.append({'Date': date_str, 'Total': total})
        except (IndexError, KeyError):
            continue
    
    # Create dataframe
    weekly_df = pd.DataFrame(weekly_data)
    
    # If we have no data, return a message
    if weekly_df.empty:
        return html.Div("No weekly data available", 
                       className="text-center text-muted d-flex justify-content-center align-items-center h-100")
    
    # Convert to date type and sort
    weekly_df['Date'] = pd.to_datetime(weekly_df['Date'])
    weekly_df = weekly_df.sort_values('Date')
    
    # For cleaner display, use shorter date format
    weekly_df['ShortDate'] = weekly_df['Date'].dt.strftime('%d %b')
    
    # Calculate daily increase
    weekly_df['Daily'] = weekly_df['Total'].diff().fillna(weekly_df['Total'].iloc[0])
    
    # Use go.Figure instead of px.bar for better compatibility
    fig = go.Figure()
    
    # Add the bars
    fig.add_trace(go.Bar(
        x=weekly_df['ShortDate'],
        y=weekly_df['Daily'],
        marker=dict(
            color=DARK_GREEN,
        ),
        text=weekly_df['Daily'].apply(lambda x: f"{x:.0f}"),
        textposition='outside',
        hovertemplate='%{x}: %{y:.0f} MT<extra></extra>'
    ))
    
    # Optimize layout with axis labels
    fig.update_layout(
        margin=dict(l=10, r=10, t=5, b=30),  # Adjusted margins for labels
        paper_bgcolor='white',
        plot_bgcolor='white',
        showlegend=False,
        xaxis=dict(
            title='Date',  # Added axis label
            title_font=dict(size=9),  # Small title font
            tickangle=45,
            tickfont=dict(size=8)  # Smaller font
        ),
        yaxis=dict(
            title='Daily MT',  # Added axis label
            title_font=dict(size=9),  # Small title font
            tickfont=dict(size=8),  # Smaller font
            showgrid=True,
            gridcolor='rgba(0,0,0,0.05)'
        ),
        height=140  # Slightly reduced height
    )
    
    return dcc.Graph(
        figure=fig,
        config={'displayModeBar': False},
        style={'height': '140px'}
    )

def create_sites_performance_chart(vendor_df, latest_date_col, sites):
    """
    Create a single chart showing all sites performance for vendors with few sites.
    Enhanced with axis labels and better formatting.
    
    Args:
        vendor_df (pandas.DataFrame): Vendor-specific data
        latest_date_col (str): Latest date column name
        sites (list): List of site (ULB) names
        
    Returns:
        dash component: Chart component
    """
    # Calculate site performance
    site_data = vendor_df.groupby('ULB').agg({
        'Quantity to be remediated in MT': 'sum',
        latest_date_col: 'sum'
    }).reset_index()
    
    # Calculate percent complete with zero protection
    site_data['Percent Complete'] = 0.0
    mask = site_data['Quantity to be remediated in MT'] > 0
    if mask.any():
        site_data.loc[mask, 'Percent Complete'] = (
            site_data.loc[mask, latest_date_col] / 
            site_data.loc[mask, 'Quantity to be remediated in MT'] * 100
        ).round(1)
    
    # Sort by target size (descending)
    site_data = site_data.sort_values('Quantity to be remediated in MT', ascending=False)
    
    # Use go.Figure instead of px.bar for better compatibility
    fig = go.Figure()
    
    # Add the bars
    fig.add_trace(go.Bar(
        x=site_data['Percent Complete'],
        y=site_data['ULB'],
        orientation='h',
        marker=dict(
            color=site_data['Percent Complete'],
            colorscale=[[0, 'lightgray'], [0.5, LIGHT_GREEN], [1, DARK_GREEN]]
        ),
        text=site_data['Percent Complete'].apply(lambda x: f"{x:.1f}%"),
        textposition='outside',
        hovertemplate='%{y}: %{text}<extra></extra>'
    ))
    
    # Optimize layout with axis labels
    fig.update_layout(
        margin=dict(l=10, r=10, t=5, b=20),  # Adjusted margins for labels
        paper_bgcolor='white',
        plot_bgcolor='white',
        showlegend=False,
        xaxis=dict(
            title='Completion Percentage',  # Added axis label
            title_font=dict(size=9),  # Small title font
            ticksuffix='%',
            range=[0, max(100, site_data['Percent Complete'].max() * 1.1)],
            tickfont=dict(size=8)  # Smaller font
        ),
        yaxis=dict(
            title='ULB Site',  # Added axis label
            title_font=dict(size=9),  # Small title font
            tickfont=dict(size=8),  # Smaller font
            automargin=True  # Auto adjust margins
        ),
        height=140  # Slightly reduced height
    )
    
    return dcc.Graph(
        figure=fig,
        config={'displayModeBar': False},
        style={'height': '140px'}
    )


def create_site_card_content(vendor_df, latest_date_col, site):
    """
    Create content for individual site card.
    
    Args:
        vendor_df (pandas.DataFrame): Vendor-specific data
        latest_date_col (str): Latest date column name
        site (str): Site (ULB) name
        
    Returns:
        dash component: Card content
    """
    # Filter for specific site
    site_df = vendor_df[vendor_df['ULB'] == site]
    
    # Calculate site metrics
    site_target = site_df['Quantity to be remediated in MT'].sum()
    site_remediated = site_df[latest_date_col].sum()
    
    # Calculate percentage with zero protection
    site_percent = 0.0
    if site_target > 0:
        site_percent = (site_remediated / site_target) * 100
    
    # Create a simple metric display with progress bar
    return html.Div([
        # Site metrics
        html.Div([
            html.Div([
                html.Span("Target: ", className="text-muted small"),
                html.Span(f"{site_target:,.0f} MT", 
                         style={"fontWeight": "500"}, className="small")
            ], className="mb-1"),
            
            html.Div([
                html.Span("Remediated: ", className="text-muted small"),
                html.Span(f"{site_remediated:,.0f} MT", 
                         style={"fontWeight": "500", "color": DARK_GREEN}, className="small")
            ], className="mb-2"),
            
            # Progress bar
            html.Div([
                dbc.Progress(
                    value=site_percent,
                    color="success" if site_percent > 50 else "warning",
                    className="mb-1",
                    style={"height": "10px"}
                ),
                html.Div([
                    html.Span(f"{site_percent:.1f}% Complete", 
                             style={"fontWeight": "500"}, className="small")
                ], className="text-end")
            ])
        ], className="p-1")
    ], className="d-flex flex-column justify-content-center h-100")




