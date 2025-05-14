"""
visualizations/charts.py - Chart creation functions

This file contains functions to create various charts and visualizations
for the dashboard.
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from data_processing import get_daily_progress, get_vendor_progress, get_cluster_progress
import plotly.graph_objects as go

# Define theme colors
EMERALD = "#2ecc71"
DARK_GREEN = "#27ae60" 
LIGHT_GREEN = "#a9dfbf"
BG_COLOR = "#f1f9f5"

"""
Update to visualizations/charts.py to optimize the progress gauge for fixed-size cards
"""

def create_progress_gauge(percent_complete):
    """
    Create a gauge chart for overall progress with normal size
    and properly visible markers and percentage.
    
    Args:
        percent_complete (float): Percentage completion value
        
    Returns:
        plotly.graph_objects.Figure: The gauge chart figure
    """
    fig = go.Figure()
    
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=percent_complete,
        domain={'x': [0, 1], 'y': [0, 1]},  # Full domain for normal size
        gauge={
            'axis': {
                'range': [0, 100],  # Explicit range from 0 to 100
                'tickwidth': 1.5,  # Wider ticks for visibility
                'tickcolor': "#555555",  # Darker tick color
                'visible': True,
                'tickfont': {'family': 'Palatino Linotype, Book Antiqua, Palatino, serif', 'size': 12},  # Larger font
                'tickmode': 'array',  # Set explicit tick values
                'tickvals': [0, 20, 40, 60, 80, 100],  # Force specific tick values
                'ticktext': ['0', '20', '40', '60', '80', '100'],  # Force specific tick labels
                'showticklabels': True,  # Ensure tick labels are shown
            },
            'bar': {'color': EMERALD, 'thickness': 0.7},  # Normal thickness
            'bgcolor': "white",
            'borderwidth': 0,
            'steps': [
                {'range': [0, 100], 'color': LIGHT_GREEN}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 2},
                'thickness': 0.75,
                'value': 90
            }
        },
        number={
            'suffix': "%", 
            'font': {'size': 28, 'family': 'Palatino Linotype, Book Antiqua, Palatino, serif', 'color': DARK_GREEN},  # Larger size
            'valueformat': '.1f',  # One decimal place
        }
    ))
    
    # Update layout to ensure proper display
    fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),  # Adjusted margins to ensure markers are visible
        paper_bgcolor="white",
        autosize=True,  # Enable autosize for responsive behavior
        height=140,  # Normal height - increased from previous
        font_family="Palatino Linotype, Book Antiqua, Palatino, serif",  # Palatino font family
        xaxis=dict(visible=False),
        yaxis=dict(visible=False)
    )
    
    return fig
    # Update layout to ensure proper display
    fig.update_layout(
        margin=dict(l=20, r=20, t=30, b=30),  # Increased margins to ensure markers are visible
        paper_bgcolor="white",
        autosize=True,  # Enable autosize for responsive behavior
        height=95,  # Reduced height (15% less than original 110px)
        font_family="Palatino Linotype, Book Antiqua, Palatino, serif",  # Palatino font family
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        annotations=[
            dict(
                x=0.5,
                y=0,
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(
                    family="Palatino Linotype, Book Antiqua, Palatino, serif",
                    size=10,
                    color="#666666"
                )
            )
        ]
    )
    
    return fig
    
    # Update layout for proper centering and responsive behavior
    fig.update_layout(
        # Remove all margins to ensure centering
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="white",
        # Use autosize for better container fitting
        autosize=True,
        # Set a reasonable height that works well in cards
        height=20,
        # Font settings for all text elements
        font_family="Georgia",
        # Make sure the gauge fits well in its container
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
    
    Args:
        dataframe (pandas.DataFrame): The remediation data
        
    Returns:
        plotly.graph_objects.Figure: Bar chart figure
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
            marker_color='#8B4513'
        ))
        
        fig.add_trace(go.Bar(
            x=vendor_stats['Vendor'],
            y=vendor_stats[latest_date_col],
            name='Completed',
            marker_color='#2E8B57'
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

def create_cluster_heatmap(dataframe):
    """
    Create a heatmap showing cluster progress.
    
    Args:
        dataframe (pandas.DataFrame): The remediation data
        
    Returns:
        plotly.graph_objects.Figure: Heatmap figure
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