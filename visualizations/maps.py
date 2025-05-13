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
    Create a map visualization of remediation status by ULB.
    
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
        
        # Create a base map centered on Andhra Pradesh
        AP_CENTER = [16.2207, 80.1276]
        m = folium.Map(location=AP_CENTER, zoom_start=7, tiles="CartoDB positron")
        
        # Create a marker cluster to group nearby markers
        marker_cluster = folium.MarkerCluster().add_to(m)
        
        # Since we don't have actual coordinates in the CSV, 
        # we'll create pseudo-random coordinates for demonstration
        # In a real implementation, you would use actual coordinates for each ULB
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