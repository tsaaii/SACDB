"""
callbacks/uploader_callbacks.py - Revised implementation with improved file upload handling

This file registers callback functions for the uploader page functionality,
including file validation, processing, and update of the upload history.
"""

from dash import Input, Output, State, callback_context, html, dcc, no_update
import dash_bootstrap_components as dbc
import dash
from flask import request
from flask_login import current_user
import base64
import io
import os
import re
import pandas as pd
import time
from datetime import datetime
import json
import traceback
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('file_uploader')

# Store for upload history (in a real app, this would be a database)
UPLOAD_HISTORY = []

def parse_contents(contents, filename):
    """
    Parse the file contents from the upload component.
    
    Args:
        contents (str): The contents of the uploaded file in base64 format
        filename (str): The name of the uploaded file
        
    Returns:
        tuple: (decoded_content, dataframe, error_message)
    """
    try:
        # Strip the content type header
        content_type, content_string = contents.split(',')
        
        # Decode the file content
        decoded = base64.b64decode(content_string)
        
        # For Excel files
        if filename.endswith('.xlsx') or filename.endswith('.xls'):
            # Try to parse the Excel file
            df = pd.read_excel(io.BytesIO(decoded))
            return decoded, df, None
            
        # Return error for unsupported file types
        return None, None, f"Unsupported file type: {filename}. Please upload an Excel file (.xlsx or .xls)."
            
    except Exception as e:
        logger.error(f"Error parsing file content: {str(e)}")
        return None, None, f"Error parsing file: {str(e)}"

def register_uploader_callbacks(app):
    """
    Register callbacks for the uploader page with improved file handling.
    
    Args:
        app (dash.Dash): The Dash application
    """
    # First callback - handle initial file upload and validation
    @app.callback(
        [Output('upload-alert', 'children'),
         Output('upload-alert', 'color'),
         Output('upload-alert', 'is_open'),
         Output('upload-progress', 'value'),
         Output('upload-progress', 'style'),
         Output('process-upload-button', 'disabled'),
         Output('upload-file-info', 'data'),
         Output('upload-data', 'contents')],  # Clear contents after processing
        [Input('upload-data', 'contents')],
        [State('upload-data', 'filename')]
    )
    def validate_uploaded_file(contents, filename):
        """
        Validate the uploaded file and prepare for processing.
        """
        # Clear the existing upload if no contents
        if contents is None:
            return (
                "", 
                "info", 
                False, 
                0, 
                {"display": "none"}, 
                True,
                None,
                None
            )
            
        # Log the upload attempt
        logger.info(f"File upload received: {filename}")
        
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
                None,
                None  # Clear the upload
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
                    None,
                    None  # Clear the upload
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
                None,
                None  # Clear the upload
            )
        
        # Parse the file content to validate it
        decoded, df, error = parse_contents(contents, filename)
        
        if error:
            return (
                [
                    html.I(className="fas fa-exclamation-triangle me-2"),
                    error
                ], 
                "danger", 
                True, 
                0, 
                {"display": "none"}, 
                True,
                None,
                None  # Clear the upload
            )
            
        # Check for required columns
        # required_columns = ['Vendor', 'Cluster', 'ULB', 'Quantity to be remediated in MT']
        # missing_columns = [col for col in required_columns if col not in df.columns]
        
        # if missing_columns:
        #     return (
        #         [
        #             html.I(className="fas fa-exclamation-triangle me-2"),
        #             f"Required columns missing: {', '.join(missing_columns)}"
        #         ], 
        #         "danger", 
        #         True, 
        #         0, 
        #         {"display": "none"}, 
        #         True,
        #         None,
        #         None  # Clear the upload
        #     )
        
        # Initialize file info for processing
        file_info = {
            'filename': filename,
            'date': f"{year}-{month}-{day}",
            'contents': contents,
            'columns': df.columns.tolist(),
            'row_count': len(df)
        }
        
        return (
            [
                html.I(className="fas fa-check-circle me-2"),
                f"File '{filename}' is valid with {len(df)} rows and {len(df.columns)} columns. Ready to process."
            ], 
            "success", 
            True, 
            50,  # Show as validated
            {"display": "block"}, 
            False,  # Enable process button
            file_info,
            contents  # Keep the contents
        )
    
    # Second callback - process and save the uploaded file
    @app.callback(
        [Output('upload-alert', 'children', allow_duplicate=True),
         Output('upload-alert', 'color', allow_duplicate=True),
         Output('upload-alert', 'is_open', allow_duplicate=True),
         Output('upload-progress', 'value', allow_duplicate=True),
         Output('upload-progress', 'style', allow_duplicate=True),
         Output('upload-history-rows', 'children'),
         Output('process-upload-button', 'disabled', allow_duplicate=True)],
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
            return no_update, no_update, no_update, no_update, no_update, no_update, no_update
        
        try:
            logger.info(f"Processing file: {file_info['filename']}")
            
            # Parse file content again
            contents = file_info['contents']
            filename = file_info['filename']
            
            # Parse content
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            
            # Ensure we have a data directory to save files
            data_dir = 'data'
            os.makedirs(data_dir, exist_ok=True)
            
            # Processing step 1: Save original file (75%)
            xlsx_path = os.path.join(data_dir, filename)
            try:
                with open(xlsx_path, 'wb') as f:
                    f.write(decoded)
                logger.info(f"Original file saved to {xlsx_path}")
            except Exception as e:
                logger.error(f"Error saving original file: {str(e)}")
                return (
                    [
                        html.I(className="fas fa-exclamation-triangle me-2"),
                        f"Error saving original file: {str(e)}"
                    ], 
                    "danger", 
                    True, 
                    50, 
                    {"display": "block"},
                    existing_rows,
                    True  # Disable process button
                )
            
            # Processing step 2: Convert to CSV and update application data (85%)
            try:
                # Read the Excel file we just saved
                df = pd.read_excel(xlsx_path)
                
                # Clean and verify the data
                #df['Cluster'] = df['Cluster'].str.strip()
                
                # Save to CSV format for the application (replacing or adding to the main data file)
                csv_path = os.path.join(data_dir, 'data.csv')
                
                # Choose your update strategy:
                # Option 1: Replace the entire file
                df.to_csv(csv_path, index=False)
                logger.info(f"Data updated and saved to {csv_path}")
                
                # Option 2: Append to existing data (uncomment if needed)
                # if os.path.exists(csv_path):
                #     existing_df = pd.read_csv(csv_path)
                #     combined_df = pd.concat([existing_df, df], ignore_index=True)
                #     combined_df.to_csv(csv_path, index=False)
                #     logger.info(f"Data appended to {csv_path}")
                # else:
                #     df.to_csv(csv_path, index=False)
                #     logger.info(f"New data file created at {csv_path}")
                
            except Exception as e:
                logger.error(f"Error processing data: {str(e)}")
                return (
                    [
                        html.I(className="fas fa-exclamation-triangle me-2"),
                        f"Error processing data: {str(e)}"
                    ], 
                    "danger", 
                    True, 
                    75, 
                    {"display": "block"},
                    existing_rows,
                    True  # Disable process button
                )
            
            # Final step: Update upload history (100%)
            upload_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Prepend new upload to history
            new_row = html.Tr([
                html.Td(filename),
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
                if isinstance(existing_rows, list):
                    history_rows.extend(existing_rows)
                else:
                    # Handle case where existing_rows might not be a list
                    history_rows.append(existing_rows)
            
            # Save upload history to a JSON file for persistence
            try:
                history_data = {
                    'filename': filename,
                    'upload_time': upload_time,
                    'rows': file_info.get('row_count', 0),
                    'columns': file_info.get('columns', [])
                }
                
                history_file = os.path.join(data_dir, 'upload_history.json')
                
                if os.path.exists(history_file):
                    with open(history_file, 'r') as f:
                        try:
                            history = json.load(f)
                        except:
                            history = []
                else:
                    history = []
                
                # Add new entry to history
                history.insert(0, history_data)
                
                # Save updated history
                with open(history_file, 'w') as f:
                    json.dump(history[:20], f)  # Keep only the 20 most recent entries
                    
                logger.info(f"Upload history updated in {history_file}")
                    
            except Exception as e:
                logger.error(f"Error saving upload history: {str(e)}")
                # This is non-critical, so we continue
            
            # Return success message
            return (
                [
                    html.I(className="fas fa-check-circle me-2"),
                    f"File '{filename}' processed successfully with {file_info.get('row_count', 0)} rows!"
                ], 
                "success", 
                True, 
                100,  # Complete
                {"display": "block"}, 
                history_rows[:10],  # Limit to the 10 most recent uploads
                True  # Disable process button after successful processing
            )
            
        except Exception as e:
            logger.error(f"Error processing file: {traceback.format_exc()}")
            return (
                [
                    html.I(className="fas fa-exclamation-triangle me-2"),
                    f"Error processing file: {str(e)}"
                ], 
                "danger", 
                True, 
                0, 
                {"display": "none"},
                existing_rows,
                True  # Disable process button
            )
    
    # Optional - Add callback for the view upload button to show file details
    @app.callback(
        Output('upload-alert', 'children', allow_duplicate=True),
        Output('upload-alert', 'color', allow_duplicate=True),
        Output('upload-alert', 'is_open', allow_duplicate=True),
        Input({'type': 'view-upload', 'index': dash.ALL}, 'n_clicks'),
        prevent_initial_call=True
    )
    def view_upload_details(n_clicks_list):
        """
        Show details for a specific uploaded file when view button is clicked.
        """
        # Get the context to determine which button was clicked
        ctx = callback_context
        if not ctx.triggered:
            return no_update, no_update, no_update
            
        # Get the button ID that was clicked
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        # Parse JSON to get the index
        try:
            parsed_id = json.loads(button_id)
            upload_index = parsed_id['index']
            
            # Read upload history
            history_file = os.path.join('data', 'upload_history.json')
            
            if os.path.exists(history_file):
                with open(history_file, 'r') as f:
                    try:
                        history = json.load(f)
                        
                        # Find the entry with matching index (timestamp)
                        matching_entries = [entry for entry in history 
                                           if entry['upload_time'].replace(' ', '-') == upload_index]
                        
                        if matching_entries:
                            entry = matching_entries[0]
                            return (
                                [
                                    html.I(className="fas fa-info-circle me-2"),
                                    html.Div([
                                        html.Strong(f"File: {entry['filename']}"),
                                        html.Br(),
                                        f"Uploaded: {entry['upload_time']}",
                                        html.Br(),
                                        f"Rows: {entry['rows']}, Columns: {len(entry['columns'])}"
                                    ])
                                ], 
                                "info", 
                                True
                            )
                    except:
                        return (
                            [
                                html.I(className="fas fa-info-circle me-2"),
                                "Upload details not available."
                            ], 
                            "info", 
                            True
                        )
            
            return (
                [
                    html.I(className="fas fa-info-circle me-2"),
                    "Upload details not available."
                ], 
                "info", 
                True
            )
                
        except:
            return no_update, no_update, no_update