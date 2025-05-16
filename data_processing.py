"""
data_processing.py - Data loading and processing for Swaccha Andhra Dashboard

This file contains functions for loading, cleaning, and processing 
the waste remediation data.
"""

import pandas as pd
import json
import os
from functools import lru_cache

def load_data(force_reload=False):
    """
    Load data from CSV and perform initial cleaning.
    Uses caching to improve performance but allows for forced reload.
    
    Args:
        force_reload (bool): Whether to force reload the data
    
    Returns:
        pandas.DataFrame: Cleaned data frame
    """
    # If force_reload is True, clear the cache
    if force_reload:
        load_data.cache_clear()
    
    return _load_data_cached()

@lru_cache(maxsize=1)


def _load_data_cached():
    """
    Cached version of load_data function.
    
    Returns:
        pandas.DataFrame: Cleaned data frame
    """
    # Get data file path from environment variable or use default
    data_file = os.environ.get('DATA_FILE', 'data.csv')
    
    df = pd.read_csv(data_file)
    
    # Clean column names and data
    df['Cluster'] = df['Cluster'].str.strip()
    
    return df


def get_dashboard_metrics(dataframe):
    """
    Calculate main dashboard metrics with protection against division by zero.
    
    Args:
        dataframe (pandas.DataFrame): The remediation data
        
    Returns:
        dict: Dictionary containing all calculated metrics
    """
    total_to_remediate = dataframe['Quantity to be remediated in MT'].sum()
    
    # Get latest date column (most recent data)
    date_columns = [col for col in dataframe.columns if col.startswith('Cumulative Quantity')]
    latest_date_col = date_columns[-1] if date_columns else 'Quantity remediated upto 30th April 2025 in MT'
    latest_date = latest_date_col.split('(')[1].split(')')[0] if '(' in latest_date_col else '2025-04-30'
    
    # Calculate total remediated as of latest date
    total_remediated_latest = dataframe[latest_date_col].sum()
    
    # Calculate percentage complete - FIX: Check for zero division
    percent_complete = 0  # Default to 0%
    if total_to_remediate > 0:  # Only calculate if denominator is non-zero
        percent_complete = (total_remediated_latest / total_to_remediate) * 100
    
    # April data
    april_remediated = dataframe['Quantity remediated upto 30th April 2025 in MT'].sum()
    
    # Get vendor statistics
    vendor_stats = dataframe.groupby('Vendor').agg({
        'Quantity to be remediated in MT': 'sum',
        latest_date_col: 'sum'
    }).reset_index()
    
    # Calculate percent complete - FIX: Handle zero division
    vendor_stats['Percent Complete'] = 0.0  # Default to 0%
    # Only calculate for rows where target > 0
    mask = vendor_stats['Quantity to be remediated in MT'] > 0
    if mask.any():
        vendor_stats.loc[mask, 'Percent Complete'] = (
            vendor_stats.loc[mask, latest_date_col] / 
            vendor_stats.loc[mask, 'Quantity to be remediated in MT'] * 100
        ).round(1)
    
    # Get cluster statistics
    cluster_stats = dataframe.groupby('Cluster').agg({
        'Quantity to be remediated in MT': 'sum',
        latest_date_col: 'sum'
    }).reset_index()
    
    # Calculate percent complete - FIX: Handle zero division
    cluster_stats['Percent Complete'] = 0.0  # Default to 0%
    # Only calculate for rows where target > 0
    mask = cluster_stats['Quantity to be remediated in MT'] > 0
    if mask.any():
        cluster_stats.loc[mask, 'Percent Complete'] = (
            cluster_stats.loc[mask, latest_date_col] / 
            cluster_stats.loc[mask, 'Quantity to be remediated in MT'] * 100
        ).round(1)
    
    # Get ULB statistics
    ulb_stats = dataframe.groupby(['ULB', 'Cluster']).agg({
        'Quantity to be remediated in MT': 'sum',
        latest_date_col: 'sum'
    }).reset_index()
    
    # Calculate percent complete - FIX: Handle zero division
    ulb_stats['Percent Complete'] = 0.0  # Default to 0%
    # Only calculate for rows where target > 0
    mask = ulb_stats['Quantity to be remediated in MT'] > 0
    if mask.any():
        ulb_stats.loc[mask, 'Percent Complete'] = (
            ulb_stats.loc[mask, latest_date_col] / 
            ulb_stats.loc[mask, 'Quantity to be remediated in MT'] * 100
        ).round(1)
    
    return {
        'total_to_remediate': total_to_remediate,
        'total_remediated': total_remediated_latest,
        'percent_complete': percent_complete,
        'april_remediated': april_remediated,
        'latest_date': latest_date,
        'latest_date_col': latest_date_col,
        'vendor_stats': vendor_stats,
        'cluster_stats': cluster_stats,
        'ulb_stats': ulb_stats
    }


def get_daily_progress(dataframe):
    """
    Calculate daily progress for time series visualization.
    
    Args:
        dataframe (pandas.DataFrame): The remediation data
        
    Returns:
        pandas.DataFrame: Daily progress data
    """
    date_columns = [col for col in dataframe.columns if col.startswith('Cumulative Quantity')]
    
    daily_totals = []
    for col in date_columns:
        date = col.split('(')[1].split(')')[0]
        total = dataframe[col].sum()
        daily_totals.append({'Date': date, 'Total Remediated (MT)': total})
    
    return pd.DataFrame(daily_totals)

def get_vendor_statistics(dataframe, latest_date_col):
    """
    Calculate vendor statistics with protection against division by zero.
    """
    vendor_stats = dataframe.groupby('Vendor').agg({
        'Quantity to be remediated in MT': 'sum',
        latest_date_col: 'sum'
    }).reset_index()
    
    # Initialize Percent Complete column with zeros
    vendor_stats['Percent Complete'] = 0.0
    
    # Calculate percentages only for rows with non-zero targets
    mask = vendor_stats['Quantity to be remediated in MT'] > 0
    if mask.any():
        vendor_stats.loc[mask, 'Percent Complete'] = (
            vendor_stats.loc[mask, latest_date_col] / 
            vendor_stats.loc[mask, 'Quantity to be remediated in MT'] * 100
        ).round(1)
        
    return vendor_stats

def get_vendor_progress(dataframe):
    """
    Calculate vendor progress over time.
    
    Args:
        dataframe (pandas.DataFrame): The remediation data
        
    Returns:
        dict: Dictionary with vendor progress data
    """
    date_columns = [col for col in dataframe.columns if col.startswith('Cumulative Quantity')]
    vendors = dataframe['Vendor'].unique()
    
    vendor_progress = {}
    for vendor in vendors:
        vendor_data = []
        vendor_df = dataframe[dataframe['Vendor'] == vendor]
        
        for col in date_columns:
            date = col.split('(')[1].split(')')[0]
            total = vendor_df[col].sum()
            vendor_data.append({'Date': date, 'Total Remediated (MT)': total})
        
        vendor_progress[vendor] = pd.DataFrame(vendor_data)
    
    return vendor_progress

def get_cluster_progress(dataframe):
    """
    Calculate cluster progress over time.
    
    Args:
        dataframe (pandas.DataFrame): The remediation data
        
    Returns:
        dict: Dictionary with cluster progress data
    """
    date_columns = [col for col in dataframe.columns if col.startswith('Cumulative Quantity')]
    clusters = dataframe['Cluster'].unique()
    
    cluster_progress = {}
    for cluster in clusters:
        cluster_data = []
        cluster_df = dataframe[dataframe['Cluster'] == cluster]
        
        for col in date_columns:
            date = col.split('(')[1].split(')')[0]
            total = cluster_df[col].sum()
            cluster_data.append({'Date': date, 'Total Remediated (MT)': total})
        
        cluster_progress[cluster] = pd.DataFrame(cluster_data)
    
    return cluster_progress

def get_geospatial_data(dataframe):
    """
    Prepare data for geospatial visualization.
    
    Args:
        dataframe (pandas.DataFrame): The remediation data
        
    Returns:
        pandas.DataFrame: Data prepared for geospatial visualization
    """
    # In a real implementation, you would have latitude and longitude for each ULB
    # For now, we'll return a simplified dataframe
    latest_date_col = [col for col in dataframe.columns if col.startswith('Cumulative Quantity')][-1]
    
    geo_data = dataframe.groupby(['ULB', 'Cluster']).agg({
        'Quantity to be remediated in MT': 'sum',
        latest_date_col: 'sum'
    }).reset_index()
    
    geo_data['Percent Complete'] = (geo_data[latest_date_col] / geo_data['Quantity to be remediated in MT']) * 100
    
    # In a real implementation, you would add lat/long coordinates here
    # geo_data['lat'] = ...
    # geo_data['lon'] = ...
    
    return geo_data