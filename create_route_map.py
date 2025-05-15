import streamlit as st
import folium
from folium.plugins import MarkerCluster

# Function to create a map for a route
def create_route_map(coordinates, start_icon='play', end_icon='stop'):
    """
    Creates an interactive Folium map displaying a route with markers
    
    Parameters:
    - coordinates: List of (latitude, longitude) points defining the route
    - start_icon: Icon to use for start marker
    - end_icon: Icon to use for end marker
    
    Returns:
    - Folium map object
    """
    # Ensure we have coordinates
    if not coordinates or len(coordinates) < 2:
        return None
    
    try:
        # Create map centered at the middle point of the route
        mid_point = coordinates[len(coordinates)//2]
        
        # Create the map with OpenStreetMap tiles that reliably show roads
        m = folium.Map(
            location=mid_point, 
            zoom_start=13
        )
        
        # Use OpenStreetMap tiles - these match the roads in the data
        folium.TileLayer(
            'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
            attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
            name='OpenStreetMap',
            overlay=False,
            control=True
        ).add_to(m)
        
        # Use all route coordinates from the API to create a route that follows roads
        folium.PolyLine(
            coordinates,
            color='blue',
            weight=5,
            opacity=0.8,
            tooltip="Route"
        ).add_to(m)
        
        # Add markers for start and end points
        start_point = coordinates[0]
        end_point = coordinates[-1]
        
        # Add distance markers along the route for better visualization
        num_points = len(coordinates)
        if num_points > 10:
            # Add markers at 20%, 40%, 60%, and 80% of the route
            for i in range(1, 5):
                idx = (num_points * i) // 5
                if 0 < idx < num_points - 1:  # Avoid start and end points
                    point = coordinates[idx]
                    folium.CircleMarker(
                        location=point,
                        radius=5,
                        color='green',
                        fill=True,
                        fill_color='green',
                        fill_opacity=0.7,
                        popup=f"{i*20}% of route"
                    ).add_to(m)
        
        # Add start and end markers
        folium.Marker(
            location=start_point,
            icon=folium.Icon(color='green', icon=start_icon, prefix='fa'),
            popup='Start'
        ).add_to(m)
        
        folium.Marker(
            location=end_point,
            icon=folium.Icon(color='red', icon=end_icon, prefix='fa'),
            popup='End'
        ).add_to(m)
        
        # Fit the map to the route bounds
        if len(coordinates) > 1:
            southwest = [min(coord[0] for coord in coordinates), min(coord[1] for coord in coordinates)]
            northeast = [max(coord[0] for coord in coordinates), max(coord[1] for coord in coordinates)]
            # Add padding to the bounds for better visibility
            padding = 0.01  # ~1km padding
            southwest = [southwest[0] - padding, southwest[1] - padding]
            northeast = [northeast[0] + padding, northeast[1] + padding]
            m.fit_bounds([southwest, northeast])
        
        # Add alternative layers for better map visualization
        folium.TileLayer(
            'https://stamen-tiles-{s}.a.ssl.fastly.net/terrain/{z}/{x}/{y}.png',
            attr='Map tiles by <a href="http://stamen.com">Stamen Design</a>',
            name='Stamen Terrain'
        ).add_to(m)
        
        folium.TileLayer(
            'https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}',
            attr='Esri',
            name='Esri Streets'
        ).add_to(m)
        
        # Add a layer control
        folium.LayerControl().add_to(m)
        
        return m
        
    except Exception as e:
        import traceback
        print(f"Error creating route map: {str(e)}")
        print(traceback.format_exc())
        return None