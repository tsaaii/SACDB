"""
callbacks/reports_callbacks.py - Callbacks for the Reports page

This file registers the callback functions for handling interactive behavior
on the reports page, including API data fetching and exports.
"""

from dash import Input, Output, State, callback_context, html, dcc, dash_table
import dash
import pandas as pd
import requests
import json
from datetime import datetime
import io
import base64
import logging
import traceback

# Setup logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('reports_callbacks')

# Import helper functions from layout file
from layouts.reports_layout import VENDOR_DATA, API_URLS, fetch_api_data, prepare_datatable

def register_reports_callbacks(app):
    """
    Register callbacks for the reports page.
    
    Args:
        app (dash.Dash): The Dash application
    """
    # Callback for updating cluster options based on vendor selection
    @app.callback(
        [Output('report-cluster-filter', 'options'),
         Output('report-cluster-filter', 'value')],
        [Input('report-vendor-filter', 'value')]
    )
    def update_cluster_options(selected_vendor):
        """
        Update cluster dropdown options based on vendor selection.
        """
        if not selected_vendor or selected_vendor not in VENDOR_DATA:
            return [], None
            
        # Get clusters for selected vendor
        clusters = list(VENDOR_DATA[selected_vendor].keys())
        cluster_options = [{'label': cluster, 'value': cluster} for cluster in clusters]
        
        # Set default value to first cluster
        default_value = clusters[0] if clusters else None
        
        return cluster_options, default_value
    
    # Callback for updating site options based on vendor and cluster selection
    @app.callback(
        [Output('report-site-filter', 'options'),
         Output('report-site-filter', 'value')],
        [Input('report-vendor-filter', 'value'),
         Input('report-cluster-filter', 'value')]
    )
    def update_site_options(selected_vendor, selected_cluster):
        """
        Update site dropdown options based on vendor and cluster selection.
        """
        if not selected_vendor or not selected_cluster:
            return [], None
            
        if selected_vendor not in VENDOR_DATA or selected_cluster not in VENDOR_DATA[selected_vendor]:
            return [], None
            
        # Get sites for selected vendor and cluster
        sites = VENDOR_DATA[selected_vendor][selected_cluster]
        site_options = [{'label': site, 'value': site} for site in sites]
        
        # Set default value to first site
        default_value = sites[0] if sites else None
        
        return site_options, default_value
    
    # Callback for updating API URL based on selections
    @app.callback(
        Output('api-url-store', 'data'),
        [Input('report-vendor-filter', 'value'),
         Input('report-cluster-filter', 'value'),
         Input('report-site-filter', 'value')]
    )
    def update_api_url(selected_vendor, selected_cluster, selected_site):
        """
        Update API URL based on selected vendor, cluster, and site.
        """
        # Default to empty URL
        api_url = None
        
        # Check if we have a URL mapping for this combination
        if (selected_vendor in API_URLS and 
            selected_cluster in API_URLS[selected_vendor] and 
            selected_site in API_URLS[selected_vendor][selected_cluster]):
            
            api_url = API_URLS[selected_vendor][selected_cluster][selected_site]
        
        return {"url": api_url}
    
    # Callback for fetching data from API
    @app.callback(
        [Output('report-data-store', 'data'),
         Output('api-info-content', 'children'),
         Output('data-record-count', 'children')],
        [Input('fetch-data-button', 'n_clicks')],
        [State('api-url-store', 'data'),
         State('report-vendor-filter', 'value'),
         State('report-cluster-filter', 'value'),
         State('report-site-filter', 'value'),
         State('report-date-range', 'start_date'),
         State('report-date-range', 'end_date')]
    )
    def fetch_data(n_clicks, api_url_data, vendor, cluster, site, start_date, end_date):
        """
        Fetch data from API based on selected filters.
        """
        # Default values
        api_info = html.P([
            html.I(className="fas fa-info-circle me-2 text-info"),
            "No API data loaded yet. Use the filters above and click 'Fetch Data'."
        ])
        record_count = ""
        
        # Check if button was clicked
        if not n_clicks:
            return None, api_info, record_count
            
        # Check if we have an API URL
        if not api_url_data or not api_url_data.get('url'):
            api_info = html.Div([
                html.P([
                    html.I(className="fas fa-exclamation-triangle me-2 text-warning"),
                    f"No API URL configured for Vendor: {vendor}, Cluster: {cluster}, Site: {site}"
                ]),
                html.P("Please select another combination or contact the administrator to add the API URL.")
            ])
            return None, api_info, record_count
        
        # Prepare parameters for API request
        api_url = api_url_data.get('url')
        
        # Convert dates to expected format (if needed)
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
            
            # Format dates as needed by the API
            start_date_formatted = start_date_obj.strftime('%Y-%m-%d')
            end_date_formatted = end_date_obj.strftime('%Y-%m-%d')
            
            # Build params for API request
            params = {
                'start_date': start_date_formatted,
                'end_date': end_date_formatted
            }
            
        except (ValueError, TypeError):
            # Use default params if date parsing fails
            params = {}
        
        try:
            # Log API request
            logger.info(f"Fetching data from API: {api_url} with params: {params}")
            
            # Call API
            api_response = fetch_api_data(api_url, params)
            
            # Handle API response
            if api_response['success']:
                # Update API info with success message
                api_info = html.Div([
                    html.P([
                        html.I(className="fas fa-check-circle me-2 text-success"),
                        f"Successfully fetched data from API"
                    ]),
                    html.P([
                        html.Strong("URL: "), 
                        html.Code(api_url)
                    ]),
                    html.P([
                        html.Strong("Parameters: "), 
                        html.Code(json.dumps(params))
                    ]),
                    html.P([
                        html.Strong("Status Code: "), 
                        api_response['status_code']
                    ])
                ])
                
                # Set record count
                if isinstance(api_response['data'], list):
                    record_count = f"{len(api_response['data'])} records"
                elif isinstance(api_response['data'], dict) and 'data' in api_response['data']:
                    record_count = f"{len(api_response['data']['data'])} records"
                else:
                    record_count = "Unknown record count"
                
                # Return the data
                return api_response['data'], api_info, record_count
                
            else:
                # Update API info with error message
                api_info = html.Div([
                    html.P([
                        html.I(className="fas fa-exclamation-circle me-2 text-danger"),
                        f"Error fetching data: {api_response['message']}"
                    ]),
                    html.P([
                        html.Strong("URL: "), 
                        html.Code(api_url)
                    ]),
                    html.P([
                        html.Strong("Parameters: "), 
                        html.Code(json.dumps(params))
                    ]),
                    html.P([
                        html.Strong("Status Code: "), 
                        api_response['status_code'] or "N/A"
                    ])
                ])
                
                return None, api_info, record_count
                
        except Exception as e:
            # Log error
            logger.error(f"Error in fetch_data callback: {traceback.format_exc()}")
            
            # Update API info with exception details
            api_info = html.Div([
                html.P([
                    html.I(className="fas fa-exclamation-circle me-2 text-danger"),
                    f"Exception occurred: {str(e)}"
                ]),
                html.P([
                    html.Strong("URL: "), 
                    html.Code(api_url)
                ]),
                html.P([
                    html.Strong("Parameters: "), 
                    html.Code(json.dumps(params))
                ])
            ])
            
            return None, api_info, record_count
    
    # Callback for rendering data table
    @app.callback(
        Output('report-data-table-container', 'children'),
        [Input('report-data-store', 'data')]
    )
    def update_data_table(data):
        """
        Update data table with fetched API data.
        """
        if not data:
            return html.P("No data loaded. Please fetch data using the controls above.")
        
        try:
            # Prepare data for table
            df, columns = prepare_datatable(data)
            
            if df.empty:
                return html.P("No data available in the response.")
            
            # Create DataTable
            return dash_table.DataTable(
                id='report-data-table',
                columns=columns,
                data=df.to_dict('records'),
                sort_action='native',
                filter_action='native',
                page_size=15,
                style_table={'overflowX': 'auto'},
                style_cell={
                    'textAlign': 'left',
                    'padding': '8px',
                    'minWidth': '100px', 
                    'width': '150px', 
                    'maxWidth': '300px',
                    'whiteSpace': 'normal'
                },
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold'
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': 'rgb(248, 248, 248)'
                    }
                ],
                export_format='none'  # We handle exports separately
            )
            
        except Exception as e:
            # Log error
            logger.error(f"Error in update_data_table callback: {traceback.format_exc()}")
            
            return html.Div([
                html.P([
                    html.I(className="fas fa-exclamation-circle me-2 text-danger"),
                    f"Error rendering data table: {str(e)}"
                ]),
                html.Pre(str(data))
            ])
    
    # Callback for exporting data to Excel
    @app.callback(
        Output('download-excel', 'data'),
        [Input('export-excel-button', 'n_clicks')],
        [State('report-data-store', 'data'),
         State('report-vendor-filter', 'value'),
         State('report-cluster-filter', 'value'),
         State('report-site-filter', 'value')]
    )
    def export_excel(n_clicks, data, vendor, cluster, site):
        """
        Export data to Excel file.
        """
        if not n_clicks or not data:
            return dash.no_update
        
        try:
            # Prepare data for export
            df, _ = prepare_datatable(data)
            
            if df.empty:
                return dash.no_update
            
            # Create Excel file
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='Report Data', index=False)
                
                # Get workbook and add a format for headers
                workbook = writer.book
                worksheet = writer.sheets['Report Data']
                
                # Add header format
                header_format = workbook.add_format({
                    'bold': True,
                    'bg_color': '#D4D4D4',
                    'border': 1
                })
                
                # Apply header format
                for col_num, value in enumerate(df.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                    
                # Auto-adjust columns width
                for i, col in enumerate(df.columns):
                    max_len = max(df[col].astype(str).str.len().max(), len(col)) + 2
                    worksheet.set_column(i, i, max_len)
            
            # Create download data
            content = output.getvalue()
            
            # Generate filename
            filename = f"{vendor}_{cluster}_{site}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            return dcc.send_bytes(content, filename)
            
        except Exception as e:
            # Log error
            logger.error(f"Error in export_excel callback: {traceback.format_exc()}")
            return dash.no_update
    
    # Callback for exporting data to CSV
    @app.callback(
        Output('download-csv', 'data'),
        [Input('export-csv-button', 'n_clicks')],
        [State('report-data-store', 'data'),
         State('report-vendor-filter', 'value'),
         State('report-cluster-filter', 'value'),
         State('report-site-filter', 'value')]
    )
    def export_csv(n_clicks, data, vendor, cluster, site):
        """
        Export data to CSV file.
        """
        if not n_clicks or not data:
            return dash.no_update
        
        try:
            # Prepare data for export
            df, _ = prepare_datatable(data)
            
            if df.empty:
                return dash.no_update
            
            # Generate filename
            filename = f"{vendor}_{cluster}_{site}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            # Return CSV data
            return dcc.send_data_frame(df.to_csv, filename, index=False)
            
        except Exception as e:
            # Log error
            logger.error(f"Error in export_csv callback: {traceback.format_exc()}")
            return dash.no_update
