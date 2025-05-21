"""
visualizations/maps.py - Geospatial visualization functions

This file contains functions for creating maps and 
geospatial visualizations for the dashboard.
"""

import folium
from folium.plugins import MarkerCluster
import pandas as pd
import json
import numpy as np

# Define theme colors
EMERALD = "#2ecc71"
DARK_GREEN = "#27ae60" 
LIGHT_GREEN = "#a9dfbf"
BG_COLOR = "#f1f9f5"

# Approximate center of Andhra Pradesh
AP_CENTER = [16.2207, 80.1276]

"""
Fixed create_remediation_map function
"""

def create_remediation_map(dataframe):
    """
    Create a map visualization of remediation status by ULB with vendor-specific colors.
    
    Args:
        dataframe (pandas.DataFrame): The remediation data
        
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
        
        # Define vendor-specific colors - use icon colors that are supported by Folium
        vendor_colors = {
            'Zigma': '#FF6D00',     # Bright orange
            'Tharuni': '#2979FF',   # Bright blue
            'Saurastra': '#6200EA', # Bright purple
            'Sudhakar': '#00BFA5',  # Bright teal
        }
        
        # Icon colors that are available in Folium
        vendor_icon_colors = {
            'Zigma': 'orange',
            'Tharuni': 'blue',
            'Saurastra': 'purple',
            'Sudhakar': 'green'
        }
        
        # Create a base map centered on Andhra Pradesh
        AP_CENTER = [16.2207, 80.1276]
        m = folium.Map(location=AP_CENTER, zoom_start=7, tiles="CartoDB positron")
        
        # Create a marker cluster to group nearby markers
        marker_cluster = folium.plugins.MarkerCluster().add_to(m)
        
        # Since we don't have actual coordinates in the CSV, 
        # we'll create pseudo-random coordinates for demonstration
        import numpy as np
        
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
            
            # Determine icon color based on vendor and completion percentage
            # Use standard Folium icon colors which are limited
            if vendor in vendor_icon_colors:
                if percent < 25:
                    icon_color = 'lightgray' 
                elif percent < 50:
                    icon_color = 'beige'
                elif percent < 75:
                    icon_color = vendor_icon_colors[vendor]
                else:
                    icon_color = vendor_icon_colors[vendor]
            else:
                # Fallback color scheme
                if percent < 25:
                    icon_color = 'lightgray'
                elif percent < 50:
                    icon_color = 'lightgreen'
                elif percent < 75:
                    icon_color = 'green'
                else:
                    icon_color = 'darkgreen'
            
            # Create popup content with vendor-specific styling
            # Use the hex colors for styling within HTML
            popup_html = f"""
            <div style="font-family: 'Segoe UI', Tahoma, sans-serif; width: 220px;">
                <h4 style="color: {vendor_colors.get(vendor, '#27ae60')}; border-bottom: 2px solid {vendor_colors.get(vendor, '#27ae60')}; padding-bottom: 5px;">{ulb}</h4>
                <p style="margin: 5px 0;"><b>Cluster:</b> {cluster}</p>
                <p style="margin: 5px 0;"><b>Vendor:</b> {vendor}</p>
                <p style="margin: 5px 0;"><b>Target:</b> {target:,.0f} MT</p>
                <p style="margin: 5px 0;"><b>Remediated:</b> {current:,.0f} MT</p>
                <div style="background-color: #f3f3f3; height: 12px; width: 100%; border-radius: 6px; margin: 8px 0;">
                    <div style="background-color: {vendor_colors.get(vendor, '#27ae60')}; height: 12px; width: {min(percent, 100)}%; border-radius: 6px;"></div>
                </div>
                <p style="text-align: center; font-weight: bold; margin: 5px 0;"><b>Progress:</b> {percent:.1f}%</p>
            </div>
            """
            
            # Add marker to the cluster with appropriate icon
            folium.Marker(
                location=[row['lat'], row['lon']],
                popup=folium.Popup(popup_html, max_width=300),
                icon=folium.Icon(color=icon_color, icon='info-sign'),
                tooltip=f"{ulb} - {percent:.1f}%"
            ).add_to(marker_cluster)
        
        # Add a legend with vendor-specific colors
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; right: 50px; 
                    border: 2px solid grey; z-index: 9999; 
                    background-color: white;
                    padding: 10px 15px;
                    border-radius: 8px;
                    font-family: 'Segoe UI', Tahoma, sans-serif;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
            <h4 style="margin-top: 0; border-bottom: 1px solid #eee; padding-bottom: 5px;">Completion Status</h4>
            <div style="display: flex; align-items: center; margin-bottom: 5px;">
                <div style="background-color: lightgray; width: 20px; height: 20px; margin-right: 10px; border-radius: 3px;"></div>
                <div>0-25%</div>
            </div>
            <div style="display: flex; align-items: center; margin-bottom: 5px;">
                <div style="background-color: beige; width: 20px; height: 20px; margin-right: 10px; border-radius: 3px;"></div>
                <div>25-50%</div>
            </div>
            <div style="display: flex; align-items: center; margin-bottom: 5px;">
                <div style="background-color: green; width: 20px; height: 20px; margin-right: 10px; border-radius: 3px;"></div>
                <div>50-75%</div>
            </div>
            <div style="display: flex; align-items: center; margin-bottom: 15px;">
                <div style="background-color: darkgreen; width: 20px; height: 20px; margin-right: 10px; border-radius: 3px;"></div>
                <div>75-100%</div>
            </div>
            <h4 style="margin-top: 0; border-bottom: 1px solid #eee; padding-bottom: 5px;">Vendors</h4>
            <div style="display: flex; align-items: center; margin-bottom: 5px;">
                <div style="background-color: #FF6D00; width: 20px; height: 20px; margin-right: 10px; border-radius: 3px;"></div>
                <div>Zigma</div>
            </div>
            <div style="display: flex; align-items: center; margin-bottom: 5px;">
                <div style="background-color: #2979FF; width: 20px; height: 20px; margin-right: 10px; border-radius: 3px;"></div>
                <div>Tharuni</div>
            </div>
            <div style="display: flex; align-items: center; margin-bottom: 5px;">
                <div style="background-color: #6200EA; width: 20px; height: 20px; margin-right: 10px; border-radius: 3px;"></div>
                <div>Saurastra</div>
            </div>
            <div style="display: flex; align-items: center;">
                <div style="background-color: #00BFA5; width: 20px; height: 20px; margin-right: 10px; border-radius: 3px;"></div>
                <div>Sudhakar</div>
            </div>
        </div>
        '''
        
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # Return the HTML representation
        return m._repr_html_()
        
    except Exception as e:
        print(f"Error in create_remediation_map: {e}")
        return f"<div style='text-align: center; padding: 20px;'><p>Error creating map: {str(e)}</p></div>"