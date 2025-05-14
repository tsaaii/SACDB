"""
Fixed callbacks/dashboard_callbacks.py with unique clock ID
"""

from dash import Input, Output, State, callback_context, dash_table, html
import dash
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from folium.plugins import MarkerCluster  # Corrected import for MarkerCluster
import numpy as np

# Define theme colors
EMERALD = "#2ecc71"
DARK_GREEN = "#27ae60" 
LIGHT_GREEN = "#a9dfbf"
BG_COLOR = "#f1f9f5"

# Make sure to import the necessary functions from data_processing
from data_processing import load_data, get_dashboard_metrics

def register_dashboard_callbacks(app):
    """
    Register dashboard interaction callbacks with the app.
    
    Args:
        app (dash.Dash): The Dash application
    """
    # Load data once
    df = load_data()
    
    # Define the callbacks here...
    @app.callback(
        [Output('cluster-filter', 'options'),
         Output('cluster-filter', 'value'),
         Output('site-filter', 'options'),
         Output('site-filter', 'value')],
        [Input('vendor-filter', 'value'),
         Input('cluster-filter', 'value'),
         Input('site-filter', 'value')]
    )
    def update_filter_options(selected_vendors, selected_clusters, selected_sites):
        """
        Update filter options based on selections, implementing cross-filtering
        to show only relevant options based on current selections.
        
        When vendor is selected, only show clusters for that vendor.
        When vendor and/or cluster are selected, only show sites for those selections.
        """
        # Access callback context INSIDE the callback function
        ctx = callback_context
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
        
        # Load the full dataset
        filtered_df = df.copy()
        
        # Step 1: Apply vendor filter if selected
        if selected_vendors and len(selected_vendors) > 0:
            filtered_df = filtered_df[filtered_df['Vendor'].isin(selected_vendors)]
        
        # Step 2: Get available clusters based on selected vendors
        available_clusters = sorted(filtered_df['Cluster'].unique())
        cluster_options = [{'label': cluster, 'value': cluster} for cluster in available_clusters]
        
        # Step 3: Further filter by selected clusters if they exist
        if selected_clusters and len(selected_clusters) > 0:
            # Check if selected clusters are still valid with the current vendor filter
            valid_clusters = [c for c in selected_clusters if c in available_clusters]
            
            # Only apply filter if there are valid clusters left
            if valid_clusters:
                filtered_df = filtered_df[filtered_df['Cluster'].isin(valid_clusters)]
                # Update selected clusters to only valid ones
                selected_clusters = valid_clusters
            else:
                # If no valid clusters remain, clear the cluster selection
                selected_clusters = []
        
        # Step 4: Get available sites based on filtered data (by vendor and possibly cluster)
        available_sites = sorted(filtered_df['ULB'].unique())
        site_options = [{'label': site, 'value': site} for site in available_sites]
        
        # Step 5: Check if current site selections are still valid
        if selected_sites and len(selected_sites) > 0:
            # Keep only valid sites based on current filters
            valid_sites = [s for s in selected_sites if s in available_sites]
            selected_sites = valid_sites if valid_sites else []
        
        # Return updated options and values
        return cluster_options, selected_clusters, site_options, selected_sites

    @app.callback(
        [Output('vendor-filter', 'value', allow_duplicate=True),
         Output('cluster-filter', 'value', allow_duplicate=True),
         Output('site-filter', 'value', allow_duplicate=True),
         Output('date-range-filter', 'start_date', allow_duplicate=True),
         Output('date-range-filter', 'end_date', allow_duplicate=True)],
        [Input('reset-filters-button', 'n_clicks')],
        prevent_initial_call=True
    )
    def reset_filters(n_clicks):
        """
        Reset all filters to empty/default values when the reset button is clicked.
        """
        if n_clicks:
            # Get the earliest and latest date from the date columns
            date_columns = [col for col in df.columns if col.startswith('Cumulative Quantity')]
            earliest_date = '2025-05-01'  # Default start date
            
            if date_columns:
                latest_date_col = date_columns[-1]
                latest_date = latest_date_col.split('(')[1].split(')')[0]
            else:
                latest_date = '2025-05-12'  # Fallback latest date
            
            # Return empty values for selection filters
            return [], [], [], earliest_date, latest_date
        
        # This should not be reached due to prevent_initial_call=True
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    @app.callback(
        [Output('daily-progress-chart', 'figure'),
         Output('vendor-comparison-chart', 'figure'),
         Output('cluster-heatmap', 'figure'),
         Output('remediation-map', 'srcDoc'),
         Output('ulb-details-table', 'children')],
        [Input('vendor-filter', 'value'),
         Input('cluster-filter', 'value'),
         Input('site-filter', 'value'),
         Input('date-range-filter', 'start_date'),
         Input('date-range-filter', 'end_date')]
    )
    def update_dashboard(vendors, clusters, sites, start_date, end_date):
        """
        Update all dashboard visualizations based on filter selections.
        """
        # Start with the full dataset
        filtered_df = df.copy()
        
        # Apply filters
        if vendors and len(vendors) > 0:
            filtered_df = filtered_df[filtered_df['Vendor'].isin(vendors)]
            
        if clusters and len(clusters) > 0:
            filtered_df = filtered_df[filtered_df['Cluster'].isin(clusters)]
        
        if sites and len(sites) > 0:
            filtered_df = filtered_df[filtered_df['ULB'].isin(sites)]
        
        # Apply date range filter
        date_columns = [col for col in filtered_df.columns if col.startswith('Cumulative Quantity')]
        filtered_date_columns = []
        
        if date_columns:
            for col in date_columns:
                date_str = col.split('(')[1].split(')')[0]
                if start_date <= date_str <= end_date:
                    filtered_date_columns.append(col)
        
        # Make sure we have at least one date column
        if not filtered_date_columns and date_columns:
            filtered_date_columns = [date_columns[-1]]  # Use the latest date if no dates in range
        
        # Update all visualizations with filtered data
        try:
            # Create our own daily progress chart
            daily_fig = create_daily_progress_chart(filtered_df, filtered_date_columns)
        except Exception as e:
            print(f"Error creating daily progress chart: {e}")
            daily_fig = go.Figure().update_layout(title="Error creating daily progress chart")
        
        try:
            # Create our own vendor comparison chart
            vendor_fig = create_vendor_comparison(filtered_df)
        except Exception as e:
            print(f"Error creating vendor comparison: {e}")
            vendor_fig = go.Figure().update_layout(title="Error creating vendor comparison")
        
        try:
            # Create our own cluster heatmap
            cluster_fig = create_cluster_heatmap(filtered_df)
        except Exception as e:
            print(f"Error creating cluster heatmap: {e}")
            cluster_fig = go.Figure().update_layout(title="Error creating cluster heatmap")
        
        try:
            # Use our local create_remediation_map function
            map_html = create_remediation_map(filtered_df)
        except Exception as e:
            print(f"Error creating remediation map: {e}")
            map_html = "<div>Error creating map</div>"
        
        # Create ULB table using our local function
        try:
            ulb_table = create_ulb_table(filtered_df)
        except Exception as e:
            print(f"Error creating ULB table: {e}")
            ulb_table = html.Div("Error creating ULB table")
        
        return daily_fig, vendor_fig, cluster_fig, map_html, ulb_table

    # Update dashboard clock with unique ID
    @app.callback(
        Output('dashboard-tv-clock', 'children'),
        [Input('clock-interval', 'n_intervals')]
    )
    def update_dashboard_clock(n_intervals):
        """
        Update the clock display for the dashboard.
        """
        from datetime import datetime
        current_time = datetime.now().strftime('%B %d, %Y %I:%M:%S %p')
        return current_time

    # Function to create a remediation map
    def create_remediation_map(dataframe):
        """
        Create a map visualization of remediation status by ULB.
        """
        try:
            # Check if dataframe is empty
            if dataframe.empty:
                return "<div style='text-align: center; padding: 20px;'><p>No data available for map visualization</p></div>"
            
            # Get latest date column
            date_columns = [col for col in dataframe.columns if col.startswith('Cumulative Quantity')]
            
            if not date_columns:
                return "<div style='text-align: center; padding: 20px;'><p>No date data available for map visualization</p></div>"
            
            latest_date_col = date_columns[-1]
            
            # Create a base map centered on Andhra Pradesh
            AP_CENTER = [16.2207, 80.1276]
            m = folium.Map(location=AP_CENTER, zoom_start=7, tiles="CartoDB positron")
            
            # Create a marker cluster to group nearby markers
            # Use MarkerCluster from folium.plugins correctly
            from folium.plugins import MarkerCluster
            marker_cluster = MarkerCluster().add_to(m)
            
            # Get ULB data
            ulb_data = dataframe.groupby(['ULB', 'Cluster', 'Vendor']).agg({
                'Quantity to be remediated in MT': 'sum',
                latest_date_col: 'sum'
            }).reset_index()
            
            # Initialize with zeros
            ulb_data['Percent Complete'] = 0.0
            
            # Calculate percentage only where target > 0
            mask = ulb_data['Quantity to be remediated in MT'] > 0
            if mask.any():
                ulb_data.loc[mask, 'Percent Complete'] = (
                    ulb_data.loc[mask, latest_date_col] / 
                    ulb_data.loc[mask, 'Quantity to be remediated in MT'] * 100
                ).round(1)
            
            # Generate pseudo-random coordinates (for demonstration)
            import numpy as np
            np.random.seed(42)  # For reproducibility
            
            # Generate coordinates around Andhra Pradesh
            lat_offset = np.random.uniform(-1.5, 1.5, size=len(ulb_data))
            lon_offset = np.random.uniform(-1.5, 1.5, size=len(ulb_data))
            
            ulb_data['lat'] = AP_CENTER[0] + lat_offset
            ulb_data['lon'] = AP_CENTER[1] + lon_offset
            
            # Create markers for each ULB
            for idx, row in ulb_data.iterrows():
                ulb = row['ULB']
                cluster = row['Cluster']
                vendor = row['Vendor']
                target = row['Quantity to be remediated in MT']
                current = row[latest_date_col]
                percent = row['Percent Complete']
                
                # Determine color based on completion percentage
                if percent < 25:
                    color = 'lightgray'
                elif percent < 50:
                    color = 'lightgreen'
                elif percent < 75:
                    color = 'green'
                else:
                    color = 'darkgreen'
                
                # Create popup content
                popup_html = f"""
                <div style="font-family: Arial; width: 200px;">
                    <h4 style="color: #27ae60;">{ulb}</h4>
                    <p><b>Cluster:</b> {cluster}</p>
                    <p><b>Vendor:</b> {vendor}</p>
                    <p><b>Target:</b> {target:,.0f} MT</p>
                    <p><b>Remediated:</b> {current:,.0f} MT</p>
                    <div style="background-color: #eee; height: 10px; width: 100%; border-radius: 5px;">
                        <div style="background-color: #2ecc71; height: 10px; width: {min(percent, 100)}%; border-radius: 5px;"></div>
                    </div>
                    <p><b>Progress:</b> {percent:.1f}%</p>
                </div>
                """
                
                # Add marker to the cluster
                folium.Marker(
                    location=[row['lat'], row['lon']],
                    popup=folium.Popup(popup_html, max_width=300),
                    icon=folium.Icon(color=color, icon='info-sign'),
                    tooltip=f"{ulb} - {percent:.1f}%"
                ).add_to(marker_cluster)
            
            # Add a legend
            legend_html = '''
            <div style="position: fixed; 
                        bottom: 50px; right: 50px; 
                        border: 2px solid grey; z-index: 9999; 
                        background-color: white;
                        padding: 10px;
                        border-radius: 5px;
                        font-family: Arial;">
                <h4 style="margin-top: 0;">Completion Status</h4>
                <div style="display: flex; align-items: center; margin-bottom: 5px;">
                    <div style="background-color: lightgray; width: 20px; height: 20px; margin-right: 10px;"></div>
                    <div>0-25%</div>
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 5px;">
                    <div style="background-color: lightgreen; width: 20px; height: 20px; margin-right: 10px;"></div>
                    <div>25-50%</div>
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 5px;">
                    <div style="background-color: green; width: 20px; height: 20px; margin-right: 10px;"></div>
                    <div>50-75%</div>
                </div>
                <div style="display: flex; align-items: center;">
                    <div style="background-color: darkgreen; width: 20px; height: 20px; margin-right: 10px;"></div>
                    <div>75-100%</div>
                </div>
            </div>
            '''
            
            m.get_root().html.add_child(folium.Element(legend_html))
            
            # Return the HTML representation
            return m._repr_html_()
            
        except Exception as e:
            print(f"Error in create_remediation_map: {e}")
            return f"<div style='text-align: center; padding: 20px;'><p>Error creating map: {str(e)}</p></div>"

    # Function to create ULB table
    def create_ulb_table(dataframe):
        """
        Create ULB details table.
        """
        # Get latest date column
        date_columns = [col for col in dataframe.columns if col.startswith('Cumulative Quantity')]
        if not date_columns:
            return html.Div("No date columns found in data", style={'padding': '20px', 'textAlign': 'center'})
            
        latest_date_col = date_columns[-1]
        
        # Prepare ULB data with protection against division by zero
        try:
            ulb_data = dataframe.groupby(['ULB', 'Cluster', 'Vendor']).agg({
                'Quantity to be remediated in MT': 'sum',
                'Quantity remediated upto 30th April 2025 in MT': 'sum',
                latest_date_col: 'sum'
            }).reset_index()
            
            # Initialize with default values
            ulb_data['Percent Complete'] = 0.0
            
            # Calculate percentages only for rows with non-zero targets
            mask = ulb_data['Quantity to be remediated in MT'] > 0
            if mask.any():
                ulb_data.loc[mask, 'Percent Complete'] = (
                    ulb_data.loc[mask, latest_date_col] / 
                    ulb_data.loc[mask, 'Quantity to be remediated in MT'] * 100
                ).round(1)
            
            # Create table
            return dash_table.DataTable(
                id='ulb-table',
                columns=[
                    {"name": "ULB", "id": "ULB"},
                    {"name": "Cluster", "id": "Cluster"},
                    {"name": "Vendor", "id": "Vendor"},
                    {"name": "Target (MT)", "id": "Quantity to be remediated in MT", "type": "numeric", "format": {"specifier": ",.0f"}},
                    {"name": "April (MT)", "id": "Quantity remediated upto 30th April 2025 in MT", "type": "numeric", "format": {"specifier": ",.0f"}},
                    {"name": f"Current (MT)", "id": latest_date_col, "type": "numeric", "format": {"specifier": ",.0f"}},
                    {"name": "Completion %", "id": "Percent Complete", "type": "numeric", "format": {"specifier": ".1f"}}
                ],
                data=ulb_data.to_dict('records'),
                sort_action='native',
                filter_action='native',
                page_size=10,
                style_table={'overflowX': 'auto'},
                style_cell={
                    'textAlign': 'left',
                    'padding': '8px',
                    'minWidth': '100px', 
                    'width': '150px', 
                    'maxWidth': '200px',
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
                ]
            )
        except Exception as e:
            print(f"Error in create_ulb_table: {e}")
            return html.Div(f"Error creating table: {str(e)}", style={'padding': '20px', 'textAlign': 'center'})

    # Helper function to create daily progress chart
    def create_daily_progress_chart(dataframe, filtered_date_columns=None):
        """
        Create a line chart showing daily progress.
        """
        # Get all date columns if not specified
        if filtered_date_columns is None or len(filtered_date_columns) == 0:
            date_columns = [col for col in dataframe.columns if col.startswith('Cumulative Quantity')]
        else:
            date_columns = filtered_date_columns
        
        # Check if we have any date columns
        if not date_columns:
            # Return empty figure with message if no date columns
            fig = go.Figure()
            fig.update_layout(
                title="No date data available",
                xaxis_title='Date',
                yaxis_title='Total Remediated (MT)',
                height=300
            )
            return fig
        
        # Prepare data for the chart
        daily_totals = []
        for col in date_columns:
            # Extract date from column name
            try:
                date_str = col.split('(')[1].split(')')[0]
                total = dataframe[col].sum()
                daily_totals.append({'Date': date_str, 'Total Remediated (MT)': total})
            except (IndexError, KeyError) as e:
                print(f"Error processing column {col}: {e}")
                continue
        
        # If we have no data points, return empty figure
        if len(daily_totals) == 0:
            fig = go.Figure()
            fig.update_layout(
                title="No valid data for the selected filters",
                xaxis_title='Date',
                yaxis_title='Total Remediated (MT)',
                height=300
            )
            return fig
        
        # Create DataFrame for plotting
        daily_data = pd.DataFrame(daily_totals)
        
        # Sort by date
        daily_data['Date'] = pd.to_datetime(daily_data['Date'])
        daily_data = daily_data.sort_values('Date')
        
        # Convert back to string for display
        daily_data['Date'] = daily_data['Date'].dt.strftime('%Y-%m-%d')
        
        # Create line chart
        fig = px.line(
            daily_data, 
            x='Date', 
            y='Total Remediated (MT)',
            markers=True,
            line_shape='linear'  # Changed from 'spline' for better handling of edge cases
        )
        
        # Customize the figure
        fig.update_traces(
            mode='lines+markers',
            line=dict(color=DARK_GREEN, width=3),
            marker=dict(size=8, color=EMERALD)
        )
        
        fig.update_layout(
            xaxis_title='Date',
            yaxis_title='Total Remediated (MT)',
            margin=dict(l=40, r=40, t=40, b=40),
            plot_bgcolor='white',
            hovermode='x unified',
            height=300
        )
        
        # Add light grid lines
        fig.update_xaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray',
            tickangle=45  # Angle tick labels for better readability
        )
        fig.update_yaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray'
        )
        
        return fig
    
    # Helper function to create vendor comparison chart
    def create_vendor_comparison(dataframe):
        """
        Create a bar chart comparing vendor performance.
        """
        # Check if dataframe is empty
        if dataframe.empty:
            fig = go.Figure()
            fig.update_layout(
                title="No data available for vendor comparison",
                height=300
            )
            return fig
        
        # Get latest date column
        date_columns = [col for col in dataframe.columns if col.startswith('Cumulative Quantity')]
        
        if not date_columns:
            fig = go.Figure()
            fig.update_layout(
                title="No date data available for vendor comparison",
                height=300
            )
            return fig
        
        latest_date_col = date_columns[-1]
        
        # Group by vendor
        try:
            vendor_stats = dataframe.groupby('Vendor').agg({
                'Quantity to be remediated in MT': 'sum',
                latest_date_col: 'sum'
            }).reset_index()
            
            # Check if we have any data
            if vendor_stats.empty or len(vendor_stats) == 0:
                fig = go.Figure()
                fig.update_layout(
                    title="No vendor data available for the selected filters",
                    height=300
                )
                return fig
            
            # Create the figure
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=vendor_stats['Vendor'],
                y=vendor_stats['Quantity to be remediated in MT'],
                name='Target',
                marker_color='#8B4513'  # SaddleBrown color
            ))
            
            fig.add_trace(go.Bar(
                x=vendor_stats['Vendor'],
                y=vendor_stats[latest_date_col],
                name='Completed',
                marker_color='#2E8B57'  # SeaGreen color
            ))
            
            fig.update_layout(
                title="Vendor Performance Comparison",
                xaxis_title='Vendor',
                yaxis_title='Quantity (MT)',
                barmode='group',
                margin=dict(l=40, r=40, t=60, b=40),
                plot_bgcolor='white',
                hovermode='x unified',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                height=300
            )
            
            return fig
            
        except Exception as e:
            print(f"Error in create_vendor_comparison: {e}")
            fig = go.Figure()
            fig.update_layout(
                title=f"Error creating vendor comparison: {str(e)}",
                height=300
            )
            return fig
    
    # Helper function to create cluster heatmap
    def create_cluster_heatmap(dataframe):
        """
        Create a heatmap showing cluster progress.
        """
        # Check if dataframe is empty
        if dataframe.empty:
            fig = go.Figure()
            fig.update_layout(
                title="No data available for cluster heatmap",
                height=300
            )
            return fig
        
        try:
            # Get latest date column
            date_columns = [col for col in dataframe.columns if col.startswith('Cumulative Quantity')]
            
            if not date_columns:
                fig = go.Figure()
                fig.update_layout(
                    title="No date data available for cluster heatmap",
                    height=300
                )
                return fig
            
            latest_date_col = date_columns[-1]
            
            # Calculate percent completion by cluster
            cluster_data = dataframe.groupby('Cluster').agg({
                'Quantity to be remediated in MT': 'sum',
                latest_date_col: 'sum'
            }).reset_index()
            
            # Check if we have any data
            if cluster_data.empty or len(cluster_data) == 0:
                fig = go.Figure()
                fig.update_layout(
                    title="No cluster data available for the selected filters",
                    height=300
                )
                return fig
            
            # Initialize percent complete with zeros
            cluster_data['Percent Complete'] = 0.0
            
            # Calculate percentages only for rows with non-zero targets
            mask = cluster_data['Quantity to be remediated in MT'] > 0
            if mask.any():
                cluster_data.loc[mask, 'Percent Complete'] = (
                    cluster_data.loc[mask, latest_date_col] / 
                    cluster_data.loc[mask, 'Quantity to be remediated in MT'] * 100
                ).round(1)
            
            # Sort by percentage
            cluster_data = cluster_data.sort_values('Percent Complete', ascending=False)
            
            # Create heatmap
            fig = px.imshow(
                [cluster_data['Percent Complete']],
                x=cluster_data['Cluster'],
                labels=dict(x="Cluster", y="", color="Completion %"),
                color_continuous_scale=[[0, 'lightgray'], [0.5, LIGHT_GREEN], [1, DARK_GREEN]],
                text_auto='.1f'
            )
            
            fig.update_layout(
                title="Cluster Completion Rate (%)",
                margin=dict(l=40, r=40, t=60, b=100),
                plot_bgcolor='white',
                coloraxis_showscale=True,
                xaxis=dict(tickangle=45),
                height=300
            )
            
            return fig
            
        except Exception as e:
            print(f"Error in create_cluster_heatmap: {e}")
            fig = go.Figure()
            fig.update_layout(
                title=f"Error creating cluster heatmap: {str(e)}",
                height=300
            )
            return fig