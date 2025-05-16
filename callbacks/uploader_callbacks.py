"""
callbacks/uploader_callbacks.py - Callbacks for the file uploader page

This file registers callback functions for the uploader page functionality,
including file validation, processing, and update of the upload history.
"""

from dash import Input, Output, State, callback_context, html, dcc
import dash_bootstrap_components as dbc
import dash
from flask_login import login_required, current_user
import base64
import io
import os
import re
import pandas as pd
import time
from datetime import datetime
import json
import traceback

# Store for upload history (in a real app, this would be a database)
UPLOAD_HISTORY = []

def register_uploader_callbacks(app):
    """
    Register callbacks for the uploader page.
    
    Args:
        app (dash.Dash): The Dash application
    """
    # Callback for handling file upload
    @app.callback(
        [Output('upload-alert', 'children'),
         Output('upload-alert', 'color'),
         Output('upload-alert', 'is_open'),
         Output('upload-progress', 'value'),
         Output('upload-progress', 'style'),
         Output('process-upload-button', 'disabled'),
         Output('upload-file-info', 'data')],
        [Input('upload-data', 'contents')],
        [State('upload-data', 'filename'),
         State('upload-data', 'last_modified')]
    )
    def validate_uploaded_file(contents, filename, last_modified):
        """
        Validate the uploaded file name and prepare for processing.
        """
        if contents is None:
            return (
                "", 
                "info", 
                False, 
                0, 
                {"display": "none"}, 
                True,
                None
            )
        
        # Check if the file name matches the required pattern
        pattern = r'Legacy Waste Status_(\d{2})\.(\d{2})\.(\d{4})\.xlsx'

        if not re.match(pattern, filename):
            return (
                [
                    html.I(className="fas fa-exclamation-triangle me-2"),
                    "Invalid file name. Please use the format: Legacy Waste Status_DD.MM.YYYY.xlsx"
                ], 
                "danger", 
                True, 
                0, 
                {"display": "none"}, 
                True,
                None
            )
            
        # Extract the date from the filename
        match = re.match(pattern, filename)
        day, month, year = match.groups()
        
        # Validate that the date is realistic
        try:
            file_date = datetime(int(year), int(month), int(day))
            
            # Check if file date is in the future
            if file_date > datetime.now():
                return (
                    [
                        html.I(className="fas fa-exclamation-triangle me-2"),
                        "The date in the filename cannot be in the future."
                    ], 
                    "danger", 
                    True, 
                    0, 
                    {"display": "none"}, 
                    True,
                    None
                )
                
        except ValueError:
            return (
                [
                    html.I(className="fas fa-exclamation-triangle me-2"),
                    "The date in the filename is invalid."
                ], 
                "danger", 
                True, 
                0, 
                {"display": "none"}, 
                True,
                None
            )
        
        # Initialize file info for processing
        file_info = {
            'filename': filename,
            'last_modified': last_modified,
            'date': f"{year}-{month}-{day}",
            'contents': contents
        }
        
        return (
            [
                html.I(className="fas fa-check-circle me-2"),
                f"File '{filename}' is valid and ready to process."
            ], 
            "success", 
            True, 
            100,  # Show as validated
            {"display": "block"}, 
            False,  # Enable process button
            file_info
        )
    
    # Callback for processing the uploaded file
    @app.callback(
        [Output('upload-alert', 'children', allow_duplicate=True),
         Output('upload-alert', 'color', allow_duplicate=True),
         Output('upload-alert', 'is_open', allow_duplicate=True),
         Output('upload-progress', 'value', allow_duplicate=True),
         Output('upload-progress', 'style', allow_duplicate=True),
         Output('upload-history-rows', 'children')],
        [Input('process-upload-button', 'n_clicks')],
        [State('upload-file-info', 'data'),
         State('upload-history-rows', 'children')],
        prevent_initial_call=True
    )
    def process_uploaded_file(n_clicks, file_info, existing_rows):
        """
        Process the uploaded file when the process button is clicked.
        """
        if n_clicks is None or file_info is None:
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
        
        try:
            # Parse file content
            content_type, content_string = file_info['contents'].split(',')
            decoded = base64.b64decode(content_string)
            
            # Set up progress
            process_progress_values = [10, 25, 50, 75, 100]  # Processing steps
            
            # First step: Validate the file (10%)
            for progress in [10]:
                # Try to read the Excel file
                try:
                    # Read the Excel file
                    df = pd.read_excel(io.BytesIO(decoded))
                    
                    # Check if it has the expected columns (you can adjust this based on your needs)
                    required_columns = ['Vendor', 'Cluster', 'ULB', 'Quantity to be remediated in MT']
                    missing_columns = [col for col in required_columns if col not in df.columns]
                    if missing_columns:
                        return (
                            [
                                html.I(className="fas fa-exclamation-triangle me-2"),
                                f"Required columns missing: {', '.join(missing_columns)}"
                            ], 
                            "danger", 
                            True, 
                            progress, 
                            {"display": "block"},
                            existing_rows
                        )
                        
                except Exception as e:
                    return (
                        [
                            html.I(className="fas fa-exclamation-triangle me-2"),
                            f"Error reading Excel file: {str(e)}"
                        ], 
                        "danger", 
                        True, 
                        progress, 
                        {"display": "block"},
                        existing_rows
                    )
            
            # Second step: Ensure data directory exists (25%)
            data_dir = 'data'
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
                
            # Third step: Save file to disk (50%)
            file_path = os.path.join(data_dir, file_info['filename'])
            try:
                with open(file_path, 'wb') as f:
                    f.write(decoded)
            except Exception as e:
                return (
                    [
                        html.I(className="fas fa-exclamation-triangle me-2"),
                        f"Error saving file: {str(e)}"
                    ], 
                    "danger", 
                    True, 
                    50, 
                    {"display": "block"},
                    existing_rows
                )
            
            # Fourth step: Update application data (75%)
            try:
                # In a real implementation, you would:
                # 1. Process the Excel data to extract new data
                # 2. Update your application's data store (CSV, database, etc.)
                
                # For demonstration, we'll just wait a bit to simulate processing
                time.sleep(1)
                
                # For a real implementation, you might update your main data.csv file:
                # df.to_csv('data.csv', index=False)  # Replace or append to existing data
                
            except Exception as e:
                return (
                    [
                        html.I(className="fas fa-exclamation-triangle me-2"),
                        f"Error updating application data: {str(e)}"
                    ], 
                    "danger", 
                    True, 
                    75, 
                    {"display": "block"},
                    existing_rows
                )
            
            # Final step: Complete (100%)
            # Add the file to upload history
            upload_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Prepend new upload to history
            new_row = html.Tr([
                html.Td(file_info['filename']),
                html.Td(upload_time),
                html.Td(html.Span("Success", className="text-success fw-bold")),
                html.Td(
                    dbc.Button(
                        html.I(className="fas fa-eye"),
                        color="primary",
                        size="sm",
                        className="me-1",
                        id={"type": "view-upload", "index": upload_time.replace(" ", "-")},
                    )
                )
            ])
            
            # Update upload history
            history_rows = [new_row]
            if existing_rows:
                history_rows.extend(existing_rows)
            
            # Return success message
            return (
                [
                    html.I(className="fas fa-check-circle me-2"),
                    f"File '{file_info['filename']}' processed successfully and saved to data folder!"
                ], 
                "success", 
                True, 
                100,  # Complete
                {"display": "block"}, 
                history_rows[:10]  # Limit to the 10 most recent uploads
            )
            
        except Exception as e:
            print(f"Error processing file: {traceback.format_exc()}")
            return (
                [
                    html.I(className="fas fa-exclamation-triangle me-2"),
                    f"Error processing file: {str(e)}"
                ], 
                "danger", 
                True, 
                0, 
                {"display": "none"},
                existing_rows
            )