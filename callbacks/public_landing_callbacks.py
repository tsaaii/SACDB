"""
callbacks/public_landing_callbacks.py - Auto-rotating public landing page callbacks
"""

from dash import Input, Output, State, callback_context
import dash
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from folium.plugins import MarkerCluster
import numpy as np

# Define theme colors
EMERALD = "#2ecc71"
DARK_GREEN = "#27ae60" 
LIGHT_GREEN = "#a9dfbf"
BG_COLOR = "#f1f9f5"

# Import from data_processing and visualization modules
from data_processing import load_data, get_dashboard_metrics
from visualizations.charts import create_progress_gauge

def register_public_landing_callbacks(app):
    """
    Register callbacks for the public landing page.
    
    Args:
        app (dash.Dash): The Dash application
    """
    # Load data once
    df = load_data()
    
    # Get all vendors and clusters for rotation
    all_vendors = sorted(df['Vendor'].unique())
    all_clusters = sorted(df['Cluster'].unique())
    
    # Define metrics
    metrics = get_dashboard_metrics(df)
    
    # Enable/disable auto-rotation based on the current page
    @app.callback(
        Output('auto-rotation-interval', 'disabled'),
        [Input('url', 'pathname')]
    )
    def toggle_rotation_interval(pathname):
        """
        Enable auto-rotation only on the public landing page.
        
        Args:
            pathname (str): Current URL path
            
        Returns:
            bool: Whether the interval should be disabled
        """
        # Enable auto-rotation only on the landing page
        return pathname != '/'
    
    # Update rotation state
    # Update rotation state with smarter cycle logic
    @app.callback(
        [Output('rotation-state', 'data'),
         Output('public-vendor-filter', 'data'),
         Output('public-cluster-filter', 'data'),
         Output('current-vendor-display', 'children'),
         Output('current-cluster-display', 'children')],
        [Input('auto-rotation-interval', 'n_intervals'),
         Input('url', 'pathname')],
        [State('rotation-state', 'data')]
    )
    def update_rotation_state(n_intervals, pathname, current_state):
        """
        Update rotation state to cycle through vendors and clusters intelligently.
        This rotates through all valid vendor-cluster combinations to show
        the full range of data.
        
        Args:
            n_intervals (int): Number of interval triggers
            pathname (str): Current URL path
            current_state (dict): Current rotation state
                
        Returns:
            tuple: (rotation_state, vendor_filter, cluster_filter, vendor_display, cluster_display)
        """
        # Skip updates if not on the landing page
        if pathname != '/':
            raise dash.exceptions.PreventUpdate
        
        # Build a mapping of vendors to their clusters
        vendor_cluster_map = {}
        for vendor in all_vendors:
            vendor_df = df[df['Vendor'] == vendor]
            vendor_cluster_map[vendor] = sorted(vendor_df['Cluster'].unique())
        
        # Initialize state if needed
        if n_intervals is None or not current_state:
            # Initial state
            vendor = all_vendors[0] if all_vendors else "All"
            clusters = vendor_cluster_map.get(vendor, [])
            cluster = clusters[0] if clusters else "All"
            
            return (
                {'vendor_index': 0, 'cluster_index': 0, 'combo_index': 0},
                [vendor],
                [cluster],
                vendor,
                cluster
            )
        
        # Build a flat list of all vendor-cluster combinations
        all_combos = []
        for v_idx, vendor in enumerate(all_vendors):
            clusters = vendor_cluster_map.get(vendor, [])
            for c_idx, cluster in enumerate(clusters):
                all_combos.append({
                    'vendor_index': v_idx,
                    'cluster_index': c_idx,
                    'vendor': vendor,
                    'cluster': cluster
                })
        
        # Get the current combo index, defaulting to 0
        combo_index = current_state.get('combo_index', 0)
        
        # Move to the next combination
        combo_index = (combo_index + 1) % len(all_combos)
        
        # Get the current combination
        current_combo = all_combos[combo_index]
        vendor = current_combo['vendor']
        cluster = current_combo['cluster']
        
        # Update state
        new_state = {
            'vendor_index': current_combo['vendor_index'],
            'cluster_index': current_combo['cluster_index'],
            'combo_index': combo_index
        }
        
        return (
            new_state,         # Updated rotation state
            [vendor],          # Vendor filter value
            [cluster],         # Cluster filter value
            vendor,            # Vendor display text
            cluster            # Cluster display text
        )
    # Update public progress gauge
    @app.callback(
        Output('public-progress-gauge', 'figure'),
        [Input('url', 'pathname')]
    )
    def update_public_progress_gauge(pathname):
        """
        Update the progress gauge on the public landing page.
        
        Args:
            pathname (str): Current URL path
            
        Returns:
            plotly.graph_objects.Figure: Progress gauge figure
        """
        # Only proceed if we're on the landing page
        if pathname != '/':
            return dash.no_update
        
        # Get latest metrics
        metrics = get_dashboard_metrics(df)
        
        # Create progress gauge - make it responsive
        fig = create_progress_gauge(metrics['percent_complete'])
        
        # Ensure it works better on mobile
        fig.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            autosize=True,
        )
        
        return fig
    
    # Update all public charts based on current filters

# Update all public charts based on current filters
    @app.callback(
        [Output('public-daily-progress-chart', 'figure'),
         Output('public-vendor-comparison-chart', 'figure'),
         Output('public-cluster-heatmap', 'figure')],
        [Input('public-vendor-filter', 'data'),
         Input('public-cluster-filter', 'data')]
    )
    def update_public_charts(vendors, clusters):
        """
        Update all charts on the public landing page based on current filters.
        
        Args:
            vendors (list): Selected vendors
            clusters (list): Selected clusters
            
        Returns:
            tuple: (daily_fig, vendor_fig, cluster_fig)
        """
        # Start with the full dataset
        filtered_df = df.copy()
        
        # Apply filters
        if vendors and len(vendors) > 0:
            filtered_df = filtered_df[filtered_df['Vendor'].isin(vendors)]
            
        if clusters and len(clusters) > 0:
            filtered_df = filtered_df[filtered_df['Cluster'].isin(clusters)]
        
        # Get date columns for filtering
        date_columns = [col for col in filtered_df.columns if col.startswith('Cumulative Quantity')]
        
        # Create daily progress chart
        daily_fig = create_daily_progress_chart(filtered_df)
        
        # Create vendor comparison
        vendor_fig = create_vendor_comparison(filtered_df)
        
        # Create cluster heatmap
        cluster_fig = create_cluster_heatmap(filtered_df)
        
        # Enhance mobile responsiveness for all charts
        for fig in [daily_fig, vendor_fig, cluster_fig]:
            # Reduce margins for mobile
            fig.update_layout(
                margin=dict(l=10, r=10, t=40, b=40),
                autosize=True,
                legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5)
            )
            
            # Adjust axis labels for better mobile view
            fig.update_xaxes(
                title_font=dict(size=12),
                tickfont=dict(size=10),
                title_standoff=5
            )
            
            fig.update_yaxes(
                title_font=dict(size=12),
                tickfont=dict(size=10),
                title_standoff=5
            )
        
        return daily_fig, vendor_fig, cluster_fig
    
    # Helper function to create daily progress chart
    def create_daily_progress_chart(dataframe):
        """
        Create a line chart showing daily progress.
        
        Args:
            dataframe (pandas.DataFrame): The filtered data
            
        Returns:
            plotly.graph_objects.Figure: Line chart figure
        """
        try:
            # Get date columns
            date_columns = [col for col in dataframe.columns if col.startswith('Cumulative Quantity')]
            
            # Check if we have any date columns
            if not date_columns:
                # Return empty figure
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
                line_shape='linear'
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
            
        except Exception as e:
            print(f"Error creating daily progress chart: {e}")
            # Return empty figure with error message
            fig = go.Figure()
            fig.update_layout(title=f"Error creating chart")
            return fig
    
    # Helper function to create vendor comparison
    def create_vendor_comparison(dataframe):
        """
        Create a bar chart comparing vendor performance.
        
        Args:
            dataframe (pandas.DataFrame): The filtered data
            
        Returns:
            plotly.graph_objects.Figure: Bar chart figure
        """
        try:
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
            print(f"Error creating vendor comparison: {e}")
            # Return empty figure with error message
            fig = go.Figure()
            fig.update_layout(title=f"Error creating chart")
            return fig
    
    # Helper function to create cluster heatmap
    def create_cluster_heatmap(dataframe):
        """
        Create a heatmap showing cluster progress.
        
        Args:
            dataframe (pandas.DataFrame): The filtered data
            
        Returns:
            plotly.graph_objects.Figure: Heatmap figure
        """
        try:
            # Check if dataframe is empty
            if dataframe.empty:
                fig = go.Figure()
                fig.update_layout(
                    title="No data available for cluster heatmap",
                    height=300
                )
                return fig
            
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
            print(f"Error creating cluster heatmap: {e}")
            # Return empty figure with error message
            fig = go.Figure()
            fig.update_layout(title=f"Error creating heatmap")
            return fig
    
    # Helper function to create remediation map
    def create_remediation_map(dataframe):
        """
        Create a map visualization of remediation status by ULB.
        
        Args:
            dataframe (pandas.DataFrame): The filtered data
            
        Returns:
            str: HTML string of the map
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
            # Import MarkerCluster locally
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
            print(f"Error creating remediation map: {e}")
            return f"<div style='text-align: center; padding: 20px;'><p>Error creating map: {str(e)}</p></div>"