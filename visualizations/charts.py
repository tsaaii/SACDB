"""
visualizations/charts.py - Complete charts file with all functions

This file contains all chart creation functions including the improved progress gauge
and the missing create_daily_progress_chart function.
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from data_processing import get_daily_progress, get_vendor_progress, get_cluster_progress

# Define theme colors
EMERALD = "#2ecc71"
DARK_GREEN = "#27ae60" 
LIGHT_GREEN = "#a9dfbf"
BG_COLOR = "#f1f9f5"

def create_progress_gauge(percent_complete):
    """
    Create a gauge chart for overall progress with improved design and alignment.
    
    Args:
        percent_complete (float): Percentage completion value
        
    Returns:
        plotly.graph_objects.Figure: The gauge chart figure
    """
    # Define color stops
    color_stops = [
        [0, "#f5f5f5"],        # Light gray for empty
        [0.25, "#BBDEFB"],     # Light blue at 25%
        [0.5, "#2979FF"],      # Bright blue at 50% 
        [0.75, "#00BFA5"],     # Teal at 75%
        [1, "#2E8B57"]         # SeaGreen at 100%
    ]
    
    fig = go.Figure()
    
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=percent_complete,
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {
                'range': [0, 100],
                'tickwidth': 1,
                'tickcolor': "#555555",
                'visible': True,
                'tickfont': {'family': 'Segoe UI, Tahoma, sans-serif', 'size': 10},
                'tickmode': 'array',
                'tickvals': [0, 25, 50, 75, 100],
                'ticktext': ['0', '25', '50', '75', '100'],
                'showticklabels': True,
            },
            'bar': {'color': "#2E8B57", 'thickness': 0.6},
            'bgcolor': "white",
            'borderwidth': 0,
            'steps': [
                {'range': [0, 25], 'color': color_stops[0][1]},
                {'range': [25, 50], 'color': color_stops[1][1]},
                {'range': [50, 75], 'color': color_stops[2][1]},
                {'range': [75, 100], 'color': color_stops[3][1]}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 1.5},
                'thickness': 0.6,
                'value': 95
            }
        },
        number={
            'suffix': "%", 
            'font': {'size': 22, 'family': 'Segoe UI, Tahoma, sans-serif', 'color': "#2E8B57"},
            'valueformat': '.1f'
        }
    ))
    
    # Update layout with better padding and alignment
    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor="white",
        autosize=True,
        height=112,
        font_family="Segoe UI, Tahoma, sans-serif",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False)
    )
    
    return fig

def create_daily_progress_chart(dataframe, filtered_date_columns=None):
    """
    Create a line chart showing daily progress.
    
    Args:
        dataframe (pandas.DataFrame): The remediation data
        filtered_date_columns (list, optional): List of date columns to include
        
    Returns:
        plotly.graph_objects.Figure: Line chart figure
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

def create_vendor_comparison(dataframe):
    """
    Create a bar chart comparing vendor performance.
    Using consistent vendor-specific colors.
    
    Args:
        dataframe (pandas.DataFrame): The remediation data or vendor stats
        
    Returns:
        plotly.graph_objects.Figure: Bar chart figure
    """
    # Define vendor colors using standard hex colors without transparency
    vendor_colors = {
        'Zigma': '#FF6D00',     # Bright orange
        'Tharuni': '#2979FF',   # Bright blue
        'Saurastra': '#6200EA', # Bright purple
        'Sudhakar': '#00BFA5',  # Bright teal
        # Add fallback color for other vendors
        'default': '#27ae60'    # Default green
    }
    
    # Define the target colors with lower opacity (using rgba)
    target_vendor_colors = {
        'Zigma': 'rgba(255, 109, 0, 0.5)',     # Transparent orange
        'Tharuni': 'rgba(41, 121, 255, 0.5)',   # Transparent blue
        'Saurastra': 'rgba(98, 0, 234, 0.5)', # Transparent purple
        'Sudhakar': 'rgba(0, 191, 165, 0.5)',  # Transparent teal
        # Add fallback color for other vendors
        'default': 'rgba(39, 174, 96, 0.5)'    # Transparent green
    }
    
    # Check if dataframe is a vendor stats dataframe (from metrics)
    if 'Vendor' in dataframe.columns and 'Percent Complete' in dataframe.columns:
        vendor_stats = dataframe
        
        # Get latest date column for the vendor stats
        date_columns = [col for col in vendor_stats.columns if col.startswith('Cumulative Quantity') or col.endswith('MT')]
        latest_date_col = date_columns[-1] if date_columns else None
        
        if latest_date_col is None:
            fig = go.Figure()
            fig.update_layout(
                title="No date data available for vendor comparison",
                height=300
            )
            return fig
    else:
        # This is raw data, check if it's empty
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
            
            # Calculate percent complete
            vendor_stats['Percent Complete'] = 0.0
            mask = vendor_stats['Quantity to be remediated in MT'] > 0
            if mask.any():
                vendor_stats.loc[mask, 'Percent Complete'] = (
                    vendor_stats.loc[mask, latest_date_col] / 
                    vendor_stats.loc[mask, 'Quantity to be remediated in MT'] * 100
                ).round(1)
        except Exception as e:
            print(f"Error calculating vendor stats: {e}")
            fig = go.Figure()
            fig.update_layout(
                title=f"Error creating vendor comparison: {str(e)}",
                height=300
            )
            return fig
    
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
    
    # Targets
    target_col = 'Quantity to be remediated in MT'
    if target_col not in vendor_stats.columns:
        # Try to find another suitable column
        possible_cols = [col for col in vendor_stats.columns if 'MT' in col]
        if possible_cols:
            target_col = possible_cols[0]
        else:
            # If we can't find a suitable column, create a dummy one
            vendor_stats[target_col] = 100
    
    # Create color array based on vendor names
    target_colors = []
    completed_colors = []
    for vendor in vendor_stats['Vendor']:
        # Get color for this vendor, fall back to default if not found
        target_colors.append(target_vendor_colors.get(vendor, target_vendor_colors['default']))
        completed_colors.append(vendor_colors.get(vendor, vendor_colors['default']))
    
    fig.add_trace(go.Bar(
        x=vendor_stats['Vendor'],
        y=vendor_stats[target_col],
        name='Target',
        marker_color=target_colors,  # Use vendor-specific colors with transparency
        opacity=0.8,
        customdata=vendor_stats['Vendor'],  # Store vendor names for hover
        hovertemplate='<b>%{customdata}</b><br>Target: %{y:,.0f} MT<extra></extra>'
    ))
    
    # Completed
    if latest_date_col in vendor_stats.columns:
        fig.add_trace(go.Bar(
            x=vendor_stats['Vendor'],
            y=vendor_stats[latest_date_col],
            name='Completed',
            marker_color=completed_colors,  # Use vendor-specific colors
            customdata=vendor_stats['Vendor'],  # Store vendor names for hover
            hovertemplate='<b>%{customdata}</b><br>Completed: %{y:,.0f} MT<extra></extra>'
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
    
    # Add font styling
    fig.update_layout(
        font=dict(
            family="Segoe UI, Tahoma, sans-serif",
            size=12,
            color="#333333"
        )
    )
    
    # Update bargap for better spacing
    fig.update_layout(bargap=0.2, bargroupgap=0.1)
    
    # Add grid lines for better readability
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="rgba(0, 0, 0, 0.1)"
    )
    
    return fig

def create_cluster_heatmap(dataframe):
    """
    Create a heatmap showing cluster progress with improved color styling.
    """
    # Define vendor colors with a gradient
    color_scale = [
        [0, 'lightgray'],      # Start with lightgray
        [0.25, '#BBDEFB'],     # Light blue at 25%
        [0.5, '#2979FF'],      # Bright blue at 50%
        [0.75, '#00BFA5'],     # Teal at 75%
        [1, '#2E8B57']         # End with SeaGreen
    ]
    
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
        
        # Create heatmap with improved color scale
        fig = px.imshow(
            [cluster_data['Percent Complete']],
            x=cluster_data['Cluster'],
            labels=dict(x="Cluster", y="", color="Completion %"),
            color_continuous_scale=color_scale,
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

def create_completion_timeline(dataframe):
    """
    Create a timeline chart showing projected completion.
    
    Args:
        dataframe (pandas.DataFrame): The remediation data
        
    Returns:
        plotly.graph_objects.Figure: Timeline chart figure
    """
    # Calculate daily average progress
    daily_data = get_daily_progress(dataframe)
    
    # Skip the first day (often 0 progress)
    if len(daily_data) > 1:
        daily_data = daily_data.iloc[1:]
    
    # Calculate daily rate
    daily_data['Daily Increase'] = daily_data['Total Remediated (MT)'].diff().fillna(0)
    avg_daily_rate = daily_data['Daily Increase'].mean()
    
    # Calculate remaining amount and estimated days
    total_target = dataframe['Quantity to be remediated in MT'].sum()
    current_progress = daily_data['Total Remediated (MT)'].iloc[-1]
    remaining = total_target - current_progress
    
    days_remaining = int(np.ceil(remaining / avg_daily_rate)) if avg_daily_rate > 0 else float('inf')
    
    # Create projection dataframe
    import datetime
    
    last_date = datetime.datetime.strptime(daily_data['Date'].iloc[-1], '%Y-%m-%d')
    dates = [last_date + datetime.timedelta(days=i) for i in range(days_remaining + 1)]
    progress_values = [current_progress + (avg_daily_rate * i) for i in range(days_remaining + 1)]
    
    projection_df = pd.DataFrame({
        'Date': [d.strftime('%Y-%m-%d') for d in dates],
        'Projected Progress': progress_values
    })
    
    # Plot actual and projected progress
    fig = go.Figure()
    
    # Actual progress
    fig.add_trace(go.Scatter(
        x=daily_data['Date'],
        y=daily_data['Total Remediated (MT)'],
        mode='lines+markers',
        name='Actual Progress',
        line=dict(color=DARK_GREEN, width=2),
        marker=dict(size=6, color=EMERALD)
    ))
    
    # Projected progress
    fig.add_trace(go.Scatter(
        x=projection_df['Date'],
        y=projection_df['Projected Progress'],
        mode='lines',
        name='Projected Progress',
        line=dict(color='gray', width=2, dash='dash')
    ))
    
    # Target line
    fig.add_trace(go.Scatter(
        x=[daily_data['Date'].iloc[0], projection_df['Date'].iloc[-1]],
        y=[total_target, total_target],
        mode='lines',
        name='Target',
        line=dict(color='red', width=1, dash='dot')
    ))
    
    # Add completion point
    projected_completion_date = projection_df['Date'].iloc[-1]
    fig.add_trace(go.Scatter(
        x=[projected_completion_date],
        y=[total_target],
        mode='markers',
        name='Projected Completion',
        marker=dict(size=12, color='red', symbol='star')
    ))
    
    fig.update_layout(
        title=f"Projected Completion Timeline (Est. Completion Date: {projected_completion_date})",
        xaxis_title='Date',
        yaxis_title='Total Remediated (MT)',
        margin=dict(l=40, r=40, t=60, b=40),
        plot_bgcolor='white',
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig

def create_vendor_performance_radar(dataframe):
    """
    Create a radar chart comparing vendor performance.
    
    Args:
        dataframe (pandas.DataFrame): The remediation data
        
    Returns:
        plotly.graph_objects.Figure: Radar chart figure
    """
    # Get latest date column
    date_columns = [col for col in dataframe.columns if col.startswith('Cumulative Quantity')]
    latest_date_col = date_columns[-1]
    
    # Calculate metrics by vendor
    vendor_metrics = dataframe.groupby('Vendor').agg({
        'Quantity to be remediated in MT': 'sum',
        latest_date_col: 'sum'
    }).reset_index()
    
    vendor_metrics['Percent Complete'] = (vendor_metrics[latest_date_col] / vendor_metrics['Quantity to be remediated in MT'] * 100).round(1)
    
    # Create radar chart
    fig = go.Figure()
    
    categories = ['Percent Complete', 'Quantity Remediated', 'Target Size']
    
    for _, row in vendor_metrics.iterrows():
        vendor = row['Vendor']
        
        # Normalize metrics for radar chart (0-1 scale)
        percent_complete_norm = row['Percent Complete'] / 100
        quantity_remediated_norm = row[latest_date_col] / vendor_metrics[latest_date_col].max()
        target_size_norm = row['Quantity to be remediated in MT'] / vendor_metrics['Quantity to be remediated in MT'].max()
        
        fig.add_trace(go.Scatterpolar(
            r=[percent_complete_norm, quantity_remediated_norm, target_size_norm],
            theta=categories,
            fill='toself',
            name=vendor
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )
        ),
        title="Vendor Performance Metrics",
        showlegend=True,
        margin=dict(l=40, r=40, t=60, b=40)
    )
    
    return fig