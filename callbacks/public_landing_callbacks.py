"""
callbacks/enhanced_public_callbacks.py - Enhanced callbacks for public landing page

This file registers callbacks for the enhanced public landing page with optimized behavior.
"""

from dash import Input, Output, State, callback_context, html, dcc
import dash
from datetime import datetime
import pandas as pd
import time

from data_processing import load_data, get_dashboard_metrics
from layouts.enhanced_public_landing import (
    create_overview_content, create_vendor_content
)

def register_enhanced_public_callbacks(app):
    """
    Register callbacks for the enhanced public landing page with optimized behavior.
    
    Args:
        app (dash.Dash): The Dash application
    """
    # Load data once
    df = load_data()
    
    # Get metrics
    metrics = get_dashboard_metrics(df)
    
    # Get all vendors for rotation
    vendors = sorted(df['Vendor'].unique())
    
    # Update clock display in navbar with improved formatting
    @app.callback(
        Output('navbar-clock', 'children'),
        [Input('clock-interval', 'n_intervals')]
    )
    def update_navbar_clock(n_intervals):
        """
        Update the clock display in the navbar with improved formatting.
        """
        now = datetime.now()
        return now.strftime('%b %d, %Y • %I:%M:%S %p')
    
    # Animate the refresh indicator when a rotation occurs
    @app.callback(
        Output('refresh-indicator', 'className'),
        [Input('auto-rotation-interval', 'n_intervals')]
    )
    def update_refresh_indicator(n_intervals):
        """
        Flash the refresh indicator when content rotates.
        """
        if n_intervals is None:
            return "fas fa-sync-alt"
        
        # Make the indicator spin for a moment
        return "fas fa-sync-alt fa-spin"
    
    # Main auto-rotation for content with smoother transitions
    @app.callback(
        [Output('public-landing-content', 'children'),
         Output('public-view-state', 'data')],
        [Input('auto-rotation-interval', 'n_intervals')],
        [State('public-view-state', 'data')]
    )
    def update_public_landing_content(n_intervals, current_state):
        """
        Auto-rotate between overview and vendor-specific content 
        with improved transitions and state management.
        """
        # Default state
        if current_state is None:
            current_state = {
                'view_type': 'overview',
                'current_vendor_index': 0,
                'rotation_count': 0
            }
        
        # Get current state
        view_type = current_state.get('view_type', 'overview')
        current_vendor_index = current_state.get('current_vendor_index', 0)
        rotation_count = current_state.get('rotation_count', 0)
        
        # Initial load
        if n_intervals is None:
            # Initial load - show overview
            return create_overview_content(df, metrics), current_state
        
        # On rotation
        if view_type == 'overview':
            # Switch to first vendor
            new_state = {
                'view_type': 'vendor',
                'current_vendor_index': 0,
                'rotation_count': rotation_count + 1,
                'last_updated': time.time()
            }
            return create_vendor_content(df, vendors[0]), new_state
        else:
            # Currently on vendor view
            next_vendor_index = (current_vendor_index + 1) % len(vendors)
            
            # If we've gone through all vendors, go back to overview
            if next_vendor_index == 0:
                new_state = {
                    'view_type': 'overview',
                    'current_vendor_index': 0,
                    'rotation_count': rotation_count + 1,
                    'last_updated': time.time()
                }
                return create_overview_content(df, metrics), new_state
            else:
                # Show next vendor
                new_state = {
                    'view_type': 'vendor',
                    'current_vendor_index': next_vendor_index,
                    'rotation_count': rotation_count + 1,
                    'last_updated': time.time()
                }
                return create_vendor_content(df, vendors[next_vendor_index]), new_state
    
    # Disable auto-rotation when not on the landing page
    @app.callback(
        Output('auto-rotation-interval', 'disabled', allow_duplicate=True),
        [Input('url', 'pathname')],
        prevent_initial_call=True
    )
    def toggle_auto_rotation(pathname):
        """
        Enable auto-rotation only on the landing page.
        """
        return pathname != '/'