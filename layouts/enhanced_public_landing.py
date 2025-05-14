def create_vendor_cluster_chart(vendor_df, latest_date_col):
    """
    Create a cluster performance chart for a specific vendor.
    
    Args:
        vendor_df (pandas.DataFrame): Filtered data for the vendor
        latest_date_col (str): Column name for latest date
        
    Returns:
        plotly.graph_objects.Figure: Bar chart figure
    """
    # Group by cluster
    cluster_data = vendor_df.groupby('Cluster').agg({
        'Quantity to be remediated in MT': 'sum',
        latest_date_col: 'sum'
    }).reset_index()
    
    # Calculate percent complete
    cluster_data['Percent Complete'] = 0.0
    mask = cluster_data['Quantity to be remediated in MT'] > 0
    if mask.any():
        cluster_data.loc[mask, 'Percent Complete'] = (
            cluster_data.loc[mask, latest_date_col] / 
            cluster_data.loc[mask, 'Quantity to be remediated in MT'] * 100
        ).round(1)
    
    # Sort by percent complete (descending)
    cluster_data = cluster_data.sort_values('Percent Complete', ascending=False)
    
    # Create figure
    fig = go.Figure()
    
    # Add bars for target and remediated
    fig.add_trace(go.Bar(
        x=cluster_data['Cluster'],
        y=cluster_data['Quantity to be remediated in MT'],
        name='Target (MT)',
        marker_color='#8B4513'  # Brown
    ))
    
    fig.add_trace(go.Bar(
        x=cluster_data['Cluster'],
        y=cluster_data[latest_date_col],
        name='Remediated (MT)',
        marker_color=DARK_GREEN,
        text=cluster_data['Percent Complete'].apply(lambda x: f"{x:.1f}%"),
        textposition='auto'
    ))
    
    # Update layout
    fig.update_layout(
        margin=dict(l=30, r=30, t=10, b=30),
        paper_bgcolor='white',
        plot_bgcolor='white',
        barmode='group',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=10)
        ),
        yaxis=dict(
            title='Waste (MT)',
            titlefont=dict(size=11),
            tickfont=dict(size=10),
            showgrid=True,
            gridcolor='lightgray'
        ),
        xaxis=dict(
            tickangle=-45,
            tickfont=dict(size=10),
            showgrid=False
        )
    )
    
    return fig

def create_site_performance_cards(vendor_df, clusters, latest_date_col):
    """
    Create site performance cards for each cluster.
    
    Args:
        vendor_df (pandas.DataFrame): Filtered data for the vendor
        clusters (list): List of clusters for the vendor
        latest_date_col (str): Column name for latest date
        
    Returns:
        list: List of site chart components
    """
    # Maximum number of clusters to display (to avoid overcrowding)
    MAX_CLUSTERS = 8
    clusters = clusters[:MAX_CLUSTERS] if len(clusters) > MAX_CLUSTERS else clusters
    
    site_cards = []
    for cluster in clusters:
        # Filter data for this cluster
        cluster_df = vendor_df[vendor_df['Cluster'] == cluster]
        
        # Get sites data
        site_data = cluster_df.groupby('ULB').agg({
            'Quantity to be remediated in MT': 'sum',
            latest_date_col: 'sum'
        }).reset_index()
        
        # Calculate percent complete
        site_data['Percent Complete'] = 0.0
        mask = site_data['Quantity to be remediated in MT'] > 0
        if mask.any():
            site_data.loc[mask, 'Percent Complete'] = (
                site_data.loc[mask, latest_date_col] / 
                site_data.loc[mask, 'Quantity to be remediated in MT'] * 100
            ).round(1)
        
        # Sort by percent complete (descending)
        site_data = site_data.sort_values('Percent Complete', ascending=False)
        
        # Limit to top 8 sites
        if len(site_data) > 8:
            site_data = site_data.head(8)
        
        # Create horizontal bar chart
        fig = go.Figure()
        
        # Add bars with custom text
        fig.add_trace(go.Bar(
            y=site_data['ULB'],
            x=site_data['Percent Complete'],
            orientation='h',
            marker_color=DARK_GREEN,
            text=site_data['Percent Complete'].apply(lambda x: f"{x:.1f}%"),
            textposition='auto'
        ))
        
        # Update layout
        fig.update_layout(
            title=dict(
                text=f"{cluster} Cluster",
                font=dict(size=14),
                x=0.5
            ),
            margin=dict(l=10, r=10, t=30, b=10),
            height=min(50 + len(site_data) * 25, 180),  # Dynamic height based on number of sites
            paper_bgcolor='white',
            plot_bgcolor='white',
            xaxis=dict(
                title='Completion %',
                titlefont=dict(size=11),
                tickfont=dict(size=10),
                range=[0, 100],
                showgrid=True,
                gridcolor='lightgray'
            ),
            yaxis=dict(
                titlefont=dict(size=11),
                tickfont=dict(size=10)
            )
        )
        
        # Create card
        card = html.Div([
            dcc.Graph(
                figure=fig,
                config={'displayModeBar': False}
            )
        ], style={
            "backgroundColor": "white",
            "borderRadius": "5px",
            "marginBottom": "10px",
            "boxShadow": "0 2px 4px rgba(0,0,0,0.05)"
        })
        
        site_cards.append(card)
    
    return site_cards