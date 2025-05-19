"""
layouts/reports_layout.py - Reports page with API data fetching functionality

This file defines the reports layout with dropdowns for vendor, cluster, and site selection,
API data fetching, and export functionality.
"""

from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import requests
import json
from datetime import datetime, timedelta
import io
import base64
from layouts.footer import create_footer

# PowerBI-style colors
COLORS = {
    'primary': '#217346',
    'secondary': '#6B6B6B',
    'accent1': '#118DFF',
    'accent2': '#F2C811',
    'accent3': '#EB6060',
    'accent4': '#881798',
    'background': '#F5F5F5',
    'card': '#FFFFFF',
}

# Define vendor data structure with clusters and sites
VENDOR_DATA = {
    'Zigma': {
        'GVMC': ['GVMC'],
        'Nellore': ['Allipuram'],
        'Chittoor': ['Chittoor', 'Madanapalle', 'B.Kothakota', 'Punganur', 'Kuppam', 'Palamaneru'],
        'Tirupati': ['Tirupati', 'Srikalahasti', 'Sullurpet', 'Nagari', 'Puttur', 'Venkatagiri'],
        'Anantapur': ['Anantapur', 'Tadipatri', 'Guntakal', 'Kalyanadurgam', 'Rayadurgam', 'Gooty']
    },
    'Tharuni': {
        'Rajahmundry': ['Srikakulam', 'Vizianagaram', 'Rajahmundry'],
        'Kakinada': ['Kakinada', 'Palacole', 'Amalapuram'],
        'Kadapa': ['Kadapa', 'Proddatur', 'Rayachoti', 'Badvel', 'Rajampet', 'Mydukur', 'Pulivendula', 
                  'Jammalamadugu', 'Yerraguntla', 'Kamalapuram'],
        'Eluru': ['Eluru', 'Gudivada', 'Machilipatnam', 'Bhimavaram', 'Tadepalligudem', 'Vijayawada', 
                 'Jaggaiahpet', 'Kondapalli', 'Nandigama', 'Nuzvid', 'Kovvur']
    },
    'Saurastra': {
        'Kurnool': ['Kurnool', 'Dhone', 'Yemmiganur', 'Adoni', 'Gudur(K)'],
        'Nandyal': ['Nandyal', 'Bethamcherla', 'Nandikotkur', 'Atmakur(K)', 'Giddalur', 'Allagadda']
    },
    'Sudhakar': {
        'Tenali': ['Tenali']
    }
}

# Define API URL mapping for vendor-cluster-site combinations
API_URLS = {
    'Zigma': {
        'GVMC': {
            'GVMC': 'https://zigmaglobal.in/vizagsac/api/product/search.php'
        },
        'Nellore': {
            'Allipuram': 'https://zigmaglobal.in/allipuram/api/product/search.php'
        }
        # Other APIs can be added here as they become available
    }
}

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
                    dbc.Col(html.Img(src="/assets/img/logo.png", height="30px"), width="auto"),
                    dbc.Col(dbc.NavbarBrand("Swaccha Andhra", style={"color": "white", "font-weight": "bold"}), width="auto")
                ], align="center", className="g-0"),
                href="/dashboard",
                style={"text-decoration": "none"}
            ),
            dbc.Nav([
                dbc.NavItem(dbc.NavLink("Dashboard", href="/dashboard", className="text-white")),
                dbc.NavItem(dbc.NavLink("Uploader", href="/uploader", className="text-white")),
                dbc.NavItem(dbc.NavLink("Reports", href="/reports", active=True, className="text-white")),
                dbc.NavItem(dbc.NavLink("Settings", href="#", className="text-white")),
                dbc.NavItem(dbc.Button("Logout", id="logout-button", color="light", size="sm", className="ms-2")),
            ], className="ms-auto", navbar=True),
        ]),
        color=COLORS['primary'],
        dark=True,
    )

def create_reports_layout():
    """
    Create the reports page layout.
    
    Returns:
        dash component: The reports layout
    """
    # Get vendors, first vendor's clusters, and first cluster's sites for initial dropdown values
    vendors = list(VENDOR_DATA.keys())
    first_vendor = vendors[0]
    first_vendor_clusters = list(VENDOR_DATA[first_vendor].keys())
    first_cluster = first_vendor_clusters[0]
    first_cluster_sites = VENDOR_DATA[first_vendor][first_cluster]
    
    # Calculate default date range (last 7 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    return html.Div([
        # Navbar
        create_navbar(),
        
        # Main content
        dbc.Container([
            # Header
            html.Div([
                html.H1("Reports & Data Analysis", className="my-4", style={"color": COLORS['primary']}),
                html.P("Select parameters to fetch and analyze data from APIs.", className="lead"),
            ], className="mb-4"),
            
            # Selection filters card
            dbc.Card([
                dbc.CardHeader(html.H5("Data Selection Filters")),
                dbc.CardBody([
                    dbc.Row([
                        # Vendor dropdown
                        dbc.Col([
                            html.Label("Vendor", style={"fontWeight": "500"}),
                            dcc.Dropdown(
                                id='report-vendor-filter',
                                options=[{'label': vendor, 'value': vendor} for vendor in vendors],
                                value=first_vendor,  # Default to first vendor
                                clearable=False
                            )
                        ], md=3, className="mb-3"),
                        
                        # Cluster dropdown (will be populated based on vendor selection)
                        dbc.Col([
                            html.Label("Cluster", style={"fontWeight": "500"}),
                            dcc.Dropdown(
                                id='report-cluster-filter',
                                options=[{'label': cluster, 'value': cluster} for cluster in first_vendor_clusters],
                                value=first_cluster,  # Default to first cluster
                                clearable=False
                            )
                        ], md=3, className="mb-3"),
                        
                        # Site dropdown (will be populated based on cluster selection)
                        dbc.Col([
                            html.Label("Site", style={"fontWeight": "500"}),
                            dcc.Dropdown(
                                id='report-site-filter',
                                options=[{'label': site, 'value': site} for site in first_cluster_sites],
                                value=first_cluster_sites[0] if first_cluster_sites else None,  # Default to first site
                                clearable=False
                            )
                        ], md=3, className="mb-3"),
                        
                        # Date Range filter
                        dbc.Col([
                            html.Label("Date Range", style={"fontWeight": "500"}),
                            dcc.DatePickerRange(
                                id='report-date-range',
                                start_date=start_date.date(),
                                end_date=end_date.date(),
                                display_format='YYYY-MM-DD',
                                style={"width": "100%"}
                            )
                        ], md=3, className="mb-3")
                    ], className="mb-3"),
                    
                    # Fetch data button
                    dbc.Row([
                        dbc.Col([
                            dbc.Button(
                                [html.I(className="fas fa-sync-alt me-2"), "Fetch Data"],
                                id="fetch-data-button",
                                color="primary",
                                className="me-2"
                            ),
                            dbc.Button(
                                [html.I(className="fas fa-file-excel me-2"), "Export to Excel"],
                                id="export-excel-button",
                                color="success",
                                className="me-2"
                            ),
                            dbc.Button(
                                [html.I(className="fas fa-file-csv me-2"), "Export to CSV"],
                                id="export-csv-button",
                                color="info"
                            )
                        ], className="d-flex justify-content-end")
                    ])
                ])
            ], className="mb-4 shadow-sm"),
            
            # API Info Box
            dbc.Card([
                dbc.CardHeader(html.H5("API Information")),
                dbc.CardBody([
                    html.Div(id="api-info-content", children=[
                        html.P([
                            html.I(className="fas fa-info-circle me-2 text-info"),
                            "No API data loaded yet. Use the filters above and click 'Fetch Data'."
                        ])
                    ])
                ])
            ], className="mb-4 shadow-sm"),
            
            # Data Display Card
            dbc.Card([
                dbc.CardHeader([
                    html.H5("API Data"),
                    html.Span(id="data-record-count", className="badge bg-secondary ms-2")
                ], className="d-flex align-items-center"),
                dbc.CardBody([
                    # Loading component for data table
                    dbc.Spinner(
                        html.Div(id="report-data-table-container", children=[
                            html.P("No data loaded. Please fetch data using the controls above.")
                        ]),
                        color=COLORS['primary'],
                        type="grow",
                        fullscreen=False
                    )
                ])
            ], className="mb-4 shadow-sm"),
            
            # Download links (hidden until data is fetched)
            html.Div(id="download-links", style={"display": "none"}),
            
            # Download components (no UI, just functional)
            dcc.Download(id="download-excel"),
            dcc.Download(id="download-csv"),
            
            # Store components to hold data
            dcc.Store(id="report-data-store"),
            dcc.Store(id="api-url-store")
            
        ], className="mt-4"),
        
        # Add footer
        create_footer()
    ])

# Helper function to fetch data from API
def fetch_api_data(url, params=None):
    """
    Fetch data from API.
    
    Args:
        url (str): API URL
        params (dict, optional): Parameters to include in request
        
    Returns:
        dict: API response or error message
    """
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise exception for 4XX/5XX responses
        
        # Try to parse JSON response
        try:
            data = response.json()
            return {
                'success': True,
                'data': data,
                'status_code': response.status_code,
                'message': 'Data fetched successfully'
            }
        except json.JSONDecodeError:
            return {
                'success': False,
                'data': None,
                'status_code': response.status_code,
                'message': 'Error parsing JSON response'
            }
            
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'data': None,
            'status_code': getattr(e.response, 'status_code', None),
            'message': f'Error fetching data: {str(e)}'
        }

# Helper function to prepare data for datatable
def prepare_datatable(api_data):
    """
    Convert API data to a format suitable for Dash DataTable.
    This version handles the specific formats of the GVMC and Allipuram APIs.
    
    Args:
        api_data (dict): API response data
        
    Returns:
        tuple: (DataFrame, columns configuration for DataTable)
    """
    # Initialize an empty DataFrame
    df = pd.DataFrame()
    
    try:
        # Check for GVMC API format (has 'records' key)
        if isinstance(api_data, dict) and 'records' in api_data:
            df = pd.DataFrame(api_data['records'])
        
        # Check for Allipuram API format (has 'data' key)
        elif isinstance(api_data, dict) and 'data' in api_data:
            df = pd.DataFrame(api_data['data'])
        
        # Try to handle it as a plain list of records
        elif isinstance(api_data, list):
            df = pd.DataFrame(api_data)
        
        # Try to handle any other JSON structure at the root level
        elif isinstance(api_data, dict):
            # Try to find array data in any of the keys
            for key, value in api_data.items():
                if isinstance(value, list) and len(value) > 0:
                    # Use the first array we find
                    df = pd.DataFrame(value)
                    break
            
            # If we still don't have data, try to convert the entire dict to a single row
            if df.empty and api_data:
                df = pd.DataFrame([api_data])
    
    except Exception as e:
        print(f"Error in prepare_datatable: {str(e)}")
        # Return empty DataFrame and columns in case of error
        return pd.DataFrame(), []
    
    # If DataFrame is empty, return empty result
    if df.empty:
        return df, []
    
    # Format numeric columns
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            # Convert to numeric and format with 2 decimal places
            df[col] = pd.to_numeric(df[col], errors='coerce').round(2)
    
    # Format date columns
    for col in df.columns:
        if col.lower() in ['date', 'transaction_date', 'report_date']:
            try:
                df[col] = pd.to_datetime(df[col]).dt.strftime('%Y-%m-%d')
            except:
                pass
    
    # Create columns configuration for DataTable
    columns = [
        {"name": col.replace('_', ' ').title(), "id": col, "selectable": True} for col in df.columns
    ]
    
    return df, columns