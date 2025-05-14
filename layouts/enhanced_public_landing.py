"""
layouts/enhanced_public_landing.py - Enhanced public landing page with auto-rotation interval fix
"""

from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from data_processing import get_dashboard_metrics
from visualizations.charts import create_progress_gauge
from layouts.footer import create_footer

# Define theme colors
EMERALD = "#2ecc71"
DARK_GREEN = "#27ae60" 
LIGHT_GREEN = "#a9dfbf"
BG_COLOR = "#f1f9f5"

def create_enhanced_public_landing():
    """
    Create the enhanced public landing page with auto-rotation feature.
    
    Returns:
        dash component: The public landing page
    """
    return html.Div(style={"backgroundColor": BG_COLOR, "minHeight": "100vh"}, children=[
        # Navbar
        create_public_navbar(),
        
        # Main content area
        dbc.Container([
            # Clock for TV display
            html.Div(id="navbar-clock", className="text-end mb-2", 
                    style={"fontSize": "1.2rem", "color": "#666"}),
            
            # Dynamic content area that will auto-rotate
            html.Div(id="public-landing-content"),
            
            # Store component to maintain view state
            dcc.Store(id='public-view-state', data={
                'view_type': 'overview',
                'current_vendor_index': 0,
                'rotation_count': 0
            }),
            
            # NOTE: Don't include these intervals here since they're in the main_layout
            # The auto-rotation-interval is now always present in the main layout
            # Interval for real-time clock updates is also in the main layout
        ], fluid=True, className="py-3 px-3"),
        
        # Footer
        create_footer()
    ])

def create_public_navbar():
    """
    Create a navbar for the public landing page.
    
    Returns:
        dash component: The navbar component
    """
    return dbc.Navbar(
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
                html.Div(id="navbar-clock", className="text-white me-3", style={"fontSize": "1rem"}),
                dbc.NavItem(
                    dbc.Button(
                        "Login", 
                        id="login-nav-button", 
                        color="light", 
                        size="md",
                        className="ms-2 fw-bold",
                        href="/login"
                    )
                ),
            ], className="ms-auto", navbar=True),
        ]),
        color=DARK_GREEN,
        dark=True,
        className="mb-3 py-2"
    )

def create_overview_content(df, metrics):
    """
    Create the overview content for the public landing page.
    
    Args:
        df (pandas.DataFrame): The dashboard data
        metrics (dict): Pre-calculated metrics
        
    Returns:
        dash component: The overview content
    """
    # Main title and overall progress
    header_section = dbc.Row([
        dbc.Col([
            html.H1("Swaccha Andhra Progress Dashboard", 
                    className="text-center mb-3",
                    style={"fontSize": "2.5rem", "color": DARK_GREEN, "fontWeight": "bold"}),
            html.P(f"Data as of {metrics['latest_date']}", 
                   className="lead text-center mb-4",
                   style={"fontSize": "1.2rem"}),
        ], width=12)
    ], className="mb-4")
    
    # Progress gauge and statistics
    progress_section = dbc.Row([
        # Left column - Progress gauge
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H3("Overall Progress", className="text-center mb-3"),
                    html.Div([
                        dcc.Graph(
                            figure=create_progress_gauge(metrics['percent_complete']),
                            config={'displayModeBar': False},
                            style={'height': '200px'}
                        ),
                    ], className="text-center"),
                    html.H3(f"{metrics['percent_complete']:.1f}% Complete", 
                           className="text-center mt-2",
                           style={"color": DARK_GREEN})
                ])
            ], className="h-100 shadow-sm border-0")
        ], md=6),
        
        # Right column - Statistics
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H3("Remediation Stats", className="text-center mb-3"),
                    html.Div([
                        html.Div([
                            html.H4("Target", className="mb-1"),
                            html.H2(f"{metrics['total_to_remediate']:,.0f} MT", 
                                   className="text-primary",
                                   style={"fontWeight": "bold"})
                        ], className="mb-4"),
                        html.Div([
                            html.H4("Remediated", className="mb-1"),
                            html.H2(f"{metrics['total_remediated']:,.0f} MT", 
                                   style={"color": DARK_GREEN, "fontWeight": "bold"})
                        ])
                    ])
                ])
            ], className="h-100 shadow-sm border-0")
        ], md=6)
    ], className="mb-4")
    
    # Vendor Progress Table
    vendor_stats = metrics['vendor_stats']
    
    # Create a table showing vendor progress
    vendor_rows = []
    for _, row in vendor_stats.iterrows():
        vendor = row['Vendor']
        target = row['Quantity to be remediated in MT']
        remediated = row[metrics['latest_date_col']]
        percent = row['Percent Complete']
        
        # Determine color based on percentage
        if percent < 25:
            color = "lightgray"
        elif percent < 50:
            color = LIGHT_GREEN
        elif percent < 75:
            color = EMERALD
        else:
            color = DARK_GREEN
        
        # Create progress bar
        progress_bar = html.Div([
            html.Div(
                style={
                    "width": f"{min(percent, 100)}%",
                    "height": "15px",
                    "backgroundColor": color,
                    "borderRadius": "5px"
                }
            )
        ], style={
            "width": "100%",
            "backgroundColor": "#f0f0f0",
            "borderRadius": "5px",
            "marginTop": "5px"
        })
        
        # Create table row
        vendor_row = html.Tr([
            html.Td(vendor, style={"fontWeight": "bold"}),
            html.Td(f"{target:,.0f} MT"),
            html.Td(f"{remediated:,.0f} MT"),
            html.Td([
                html.Span(f"{percent:.1f}%", style={"marginRight": "10px"}),
                progress_bar
            ])
        ])
        
        vendor_rows.append(vendor_row)
    
    vendor_table = dbc.Table([
        html.Thead(
            html.Tr([
                html.Th("Vendor"),
                html.Th("Target (MT)"),
                html.Th("Remediated (MT)"),
                html.Th("Progress")
            ])
        ),
        html.Tbody(vendor_rows)
    ], bordered=True, hover=True, responsive=True, className="shadow-sm")
    
    vendor_section = dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H3("Vendor Progress Overview", className="mb-0")),
                dbc.CardBody([
                    vendor_table
                ])
            ], className="shadow-sm border-0")
        ], width=12)
    ], className="mb-4")
    
    # Auto-rotation message
    rotation_message = dbc.Row([
        dbc.Col([
            dbc.Alert([
                html.I(className="fas fa-sync-alt me-2"),
                "Dashboard auto-rotates to show detailed vendor and cluster progress"
            ], color="info", className="text-center")
        ], width={"size": 10, "offset": 1})
    ])
    
    # Combine all sections
    return html.Div([
        header_section,
        progress_section,
        vendor_section,
        rotation_message
    ])

def create_vendor_content(df, vendor_name):
    """
    Create vendor-specific content for the public landing page.
    
    Args:
        df (pandas.DataFrame): The dashboard data
        vendor_name (str): The vendor to display
        
    Returns:
        dash component: The vendor-specific content
    """
    # Filter data for the selected vendor
    vendor_df = df[df['Vendor'] == vendor_name].copy()
    
    # If no data for this vendor, show a message
    if vendor_df.empty:
        return html.Div([
            html.H2(f"No data available for {vendor_name}", className="text-center my-5")
        ])
    
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
    
    # Vendor header section
    header_section = dbc.Row([
        dbc.Col([
            html.H2([
                "Vendor: ",
                html.Span(vendor_name, style={"color": DARK_GREEN, "fontWeight": "bold"})
            ], className="mb-3"),
            html.P(f"Data as of {latest_date}", className="lead")
        ], width=12)
    ], className="mb-4")
    
    # Vendor progress statistics
    progress_section = dbc.Row([
        # Left column - Progress gauge
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H3("Vendor Progress", className="text-center mb-3"),
                    html.Div([
                        dcc.Graph(
                            figure=create_progress_gauge(percent_complete),
                            config={'displayModeBar': False},
                            style={'height': '180px'}
                        ),
                    ], className="text-center"),
                    html.H3(f"{percent_complete:.1f}% Complete", 
                           className="text-center mt-2",
                           style={"color": DARK_GREEN})
                ])
            ], className="h-100 shadow-sm border-0")
        ], md=6),
        
        # Right column - Statistics
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H3("Target Statistics", className="text-center mb-3"),
                    html.Div([
                        html.Div([
                            html.H4("Target", className="mb-1"),
                            html.H2(f"{total_target:,.0f} MT", 
                                   className="text-primary",
                                   style={"fontWeight": "bold"})
                        ], className="mb-4"),
                        html.Div([
                            html.H4("Remediated", className="mb-1"),
                            html.H2(f"{total_remediated:,.0f} MT", 
                                   style={"color": DARK_GREEN, "fontWeight": "bold"})
                        ])
                    ])
                ])
            ], className="h-100 shadow-sm border-0")
        ], md=6)
    ], className="mb-4")
    
    # Create a chart showing cluster performance
    cluster_data = vendor_df.groupby('Cluster').agg({
        'Quantity to be remediated in MT': 'sum',
        latest_date_col: 'sum'
    }).reset_index()
    
    # Calculate percent complete
    cluster_data['Percent Complete'] = 0.0
    mask = cluster_data['Quantity to be remediated in MT'] > 0
    if mask.any():
        cluster_data.loc[mask, 'Percent Complete'] = (
            cluster_data.loc[mask, latest_date_col] / 
            cluster_data.loc[mask, 'Quantity to be remediated in MT'] * 100
        ).round(1)
    
    # Sort by percent complete
    cluster_data = cluster_data.sort_values('Percent Complete', ascending=False)
    
    # Create horizontal bar chart for clusters
    cluster_fig = px.bar(
        cluster_data,
        y='Cluster',
        x='Percent Complete',
        orientation='h',
        text='Percent Complete',
        labels={'Percent Complete': 'Completion %', 'Cluster': ''},
        color='Percent Complete',
        color_continuous_scale=[[0, 'lightgray'], [0.5, LIGHT_GREEN], [1, DARK_GREEN]],
    )
    
    cluster_fig.update_traces(
        texttemplate='%{text:.1f}%',
        textposition='outside',
        marker_line_color='white',
        marker_line_width=1.5
    )
    
    cluster_fig.update_layout(
        title="Cluster Completion Rates",
        margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor='white',
        plot_bgcolor='white',
        height=300,
        xaxis=dict(
            range=[0, 100],
            title="Completion %",
            showgrid=True,
            gridcolor='lightgray'
        ),
        yaxis=dict(
            title="",
            showgrid=False
        ),
        coloraxis_showscale=False
    )
    
    # Create stack bar chart for target vs remediated
    stack_fig = go.Figure()
    
    stack_fig.add_trace(go.Bar(
        x=cluster_data['Cluster'],
        y=cluster_data['Quantity to be remediated in MT'],
        name='Target',
        marker_color='#8B4513'  # Brown
    ))
    
    stack_fig.add_trace(go.Bar(
        x=cluster_data['Cluster'],
        y=cluster_data[latest_date_col],
        name='Remediated',
        marker_color=DARK_GREEN
    ))
    
    stack_fig.update_layout(
        title="Target vs. Remediated by Cluster",
        margin=dict(l=10, r=10, t=40, b=40),
        paper_bgcolor='white',
        plot_bgcolor='white',
        height=350,
        barmode='group',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1,
            xanchor="right",
            x=1
        ),
        xaxis=dict(
            title="",
            showgrid=False,
            tickangle=-45
        ),
        yaxis=dict(
            title="Quantity (MT)",
            showgrid=True,
            gridcolor='lightgray'
        )
    )
    
    # Charts section
    charts_section = dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(
                        figure=cluster_fig,
                        config={'displayModeBar': False}
                    )
                ])
            ], className="shadow-sm border-0 mb-4")
        ], md=12),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(
                        figure=stack_fig,
                        config={'displayModeBar': False}
                    )
                ])
            ], className="shadow-sm border-0")
        ], md=12)
    ])
    
    # Combine all sections
    return html.Div([
        header_section,
        progress_section,
        charts_section
    ])

def create_vendor_cluster_chart(vendor_df, latest_date_col):
    """
    Create a cluster performance chart for a specific vendor.
    
    Args:
        vendor_df (pandas.DataFrame): Filtered data for the vendor
        latest_date_col (str): Column name for latest date
        
    Returns:
        plotly.graph_objects.Figure: Bar chart figure
    """
    # Group by cluster
    cluster_data = vendor_df.groupby('Cluster').agg({
        'Quantity to be remediated in MT': 'sum',
        latest_date_col: 'sum'
    }).reset_index()
    
    # Calculate percent complete
    cluster_data['Percent Complete'] = 0.0
    mask = cluster_data['Quantity to be remediated in MT'] > 0
    if mask.any():
        cluster_data.loc[mask, 'Percent Complete'] = (
            cluster_data.loc[mask, latest_date_col] / 
            cluster_data.loc[mask, 'Quantity to be remediated in MT'] * 100
        ).round(1)
    
    # Sort by percent complete (descending)
    cluster_data = cluster_data.sort_values('Percent Complete', ascending=False)
    
    # Create figure
    fig = go.Figure()
    
    # Add bars for target and remediated
    fig.add_trace(go.Bar(
        x=cluster_data['Cluster'],
        y=cluster_data['Quantity to be remediated in MT'],
        name='Target (MT)',
        marker_color='#8B4513'  # Brown
    ))
    
    fig.add_trace(go.Bar(
        x=cluster_data['Cluster'],
        y=cluster_data[latest_date_col],
        name='Remediated (MT)',
        marker_color=DARK_GREEN,
        text=cluster_data['Percent Complete'].apply(lambda x: f"{x:.1f}%"),
        textposition='auto'
    ))
    
    # Update layout
    fig.update_layout(
        margin=dict(l=30, r=30, t=10, b=30),
        paper_bgcolor='white',
        plot_bgcolor='white',
        barmode='group',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=10)
        ),
        yaxis=dict(
            title='Waste (MT)',
            titlefont=dict(size=11),
            tickfont=dict(size=10),
            showgrid=True,
            gridcolor='lightgray'
        ),
        xaxis=dict(
            tickangle=-45,
            tickfont=dict(size=10),
            showgrid=False
        )
    )
    
    return fig

def create_site_performance_cards(vendor_df, clusters, latest_date_col):
    """
    Create site performance cards for each cluster.
    
    Args:
        vendor_df (pandas.DataFrame): Filtered data for the vendor
        clusters (list): List of clusters for the vendor
        latest_date_col (str): Column name for latest date
        
    Returns:
        list: List of site chart components
    """
    # Maximum number of clusters to display (to avoid overcrowding)
    MAX_CLUSTERS = 8
    clusters = clusters[:MAX_CLUSTERS] if len(clusters) > MAX_CLUSTERS else clusters
    
    site_cards = []
    for cluster in clusters:
        # Filter data for this cluster
        cluster_df = vendor_df[vendor_df['Cluster'] == cluster]
        
        # Get sites data
        site_data = cluster_df.groupby('ULB').agg({
            'Quantity to be remediated in MT': 'sum',
            latest_date_col: 'sum'
        }).reset_index()
        
        # Calculate percent complete
        site_data['Percent Complete'] = 0.0
        mask = site_data['Quantity to be remediated in MT'] > 0
        if mask.any():
            site_data.loc[mask, 'Percent Complete'] = (
                site_data.loc[mask, latest_date_col] / 
                site_data.loc[mask, 'Quantity to be remediated in MT'] * 100
            ).round(1)
        
        # Sort by percent complete (descending)
        site_data = site_data.sort_values('Percent Complete', ascending=False)
        
        # Limit to top 8 sites
        if len(site_data) > 8:
            site_data = site_data.head(8)
        
        # Create horizontal bar chart
        fig = go.Figure()
        
        # Add bars with custom text
        fig.add_trace(go.Bar(
            y=site_data['ULB'],
            x=site_data['Percent Complete'],
            orientation='h',
            marker_color=DARK_GREEN,
            text=site_data['Percent Complete'].apply(lambda x: f"{x:.1f}%"),
            textposition='auto'
        ))
        
        # Update layout
        fig.update_layout(
            title=dict(
                text=f"{cluster} Cluster",
                font=dict(size=14),
                x=0.5
            ),
            margin=dict(l=10, r=10, t=30, b=10),
            height=min(50 + len(site_data) * 25, 180),  # Dynamic height based on number of sites
            paper_bgcolor='white',
            plot_bgcolor='white',
            xaxis=dict(
                title='Completion %',
                titlefont=dict(size=11),
                tickfont=dict(size=10),
                range=[0, 100],
                showgrid=True,
                gridcolor='lightgray'
            ),
            yaxis=dict(
                titlefont=dict(size=11),
                tickfont=dict(size=10)
            )
        )
        
        # Create card
        card = html.Div([
            dcc.Graph(
                figure=fig,
                config={'displayModeBar': False}
            )
        ], style={
            "backgroundColor": "white",
            "borderRadius": "5px",
            "marginBottom": "10px",
            "boxShadow": "0 2px 4px rgba(0,0,0,0.05)"
        })
        
        site_cards.append(card)
    
    return site_cards