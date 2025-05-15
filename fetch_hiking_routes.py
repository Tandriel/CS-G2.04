from geopy.distance import distance
from create_route_map import create_route_map
import os
import traceback
import gpxpy
import numpy as np
import streamlit as st

def load_gpx_file(gpx_file_path):
    """
    Load data from a GPX file and extract route information.
    """
    try:
        with open(gpx_file_path, 'r', encoding='utf-8') as f:
            gpx = gpxpy.parse(f)

        coordinates = []
        elevations = []

        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    coordinates.append((point.latitude, point.longitude))
                    elevations.append(point.elevation)

        # Calculate distance in km
        distance_km = 0
        if len(coordinates) > 1:
            for i in range(len(coordinates) - 1):
                distance_km += distance(coordinates[i], coordinates[i + 1]).km

        # Calculate elevation gain
        elevation_gain = 0
        if elevations:
            elev_diff = np.diff([e for e in elevations if e is not None])
            elevation_gain = sum(diff for diff in elev_diff if diff > 0)

        # Round elevation gain to two decimal places
        elevation_gain = round(elevation_gain, 2)   

        # Estimate hiking time using Naismith's rule
        estimated_time_min = ((distance_km / 5) + (elevation_gain / 600)) * 60

        return {
            "coordinates": coordinates,
            "distance_km": distance_km,
            "elevation_gain": elevation_gain,
            "duration_min": estimated_time_min
        }
    except Exception as e:
        st.error(f"Error loading GPX file {os.path.basename(gpx_file_path)}: {str(e)}")
        st.debug(traceback.format_exc())
        return None

def fetch_hiking_routes(latitude, longitude, radius=10000):
    """
    Fetch hiking trails from GPX files that are near the specified coordinates.
    """
    sample_routes = []

    # Show debug info
    st.debug(f"Fetching hiking routes near: ({latitude}, {longitude}) with radius {radius}m")

    # Check if we have valid coordinates
    if not latitude or not longitude:
        st.error("Invalid coordinates for hiking routes")
        return []

    # Define the directory containing GPX files
    gpx_dir = "GPX_hiking/"

    # Get a list of all GPX files in the directory
    gpx_files = []
    try:
        for file in os.listdir(gpx_dir):
            if file.endswith(".gpx"):
                gpx_files.append(os.path.join(gpx_dir, file))
    except Exception as e:
        st.error(f"Error reading GPX directory: {str(e)}")
        return []

    st.debug(f"Found {len(gpx_files)} GPX files in directory")

    # Process each GPX file
    near_trails = []
    user_location = (latitude, longitude)

    for gpx_file in gpx_files:
        try:
            # Load the GPX file
            route_data = load_gpx_file(gpx_file)

            if route_data and route_data["coordinates"]:
                # Calculate distance from user location to the first coordinate of the route
                start_point = route_data["coordinates"][0]
                dist_to_user = distance(user_location, start_point).meters

                if dist_to_user <= radius:
                    near_trails.append((os.path.basename(gpx_file), route_data, dist_to_user))
        except Exception as e:
            st.error(f"Error processing GPX file {os.path.basename(gpx_file)}: {str(e)}")

    # Sort by distance and select the closest ones
    near_trails.sort(key=lambda x: x[2])
    selected_trails = near_trails[:min(5, len(near_trails))]

    # Create route objects for the selected trails
    for name, route_data, dist in selected_trails:
        try:
            # Extract trail data
            coordinates = route_data["coordinates"]
            distance_km = route_data["distance_km"]
            elevation_gain = route_data["elevation_gain"]
            duration_min = route_data["duration_min"]

            # Determine difficulty based on elevation gain and distance
            if elevation_gain > 300 or distance_km > 8:
                difficulty = "Hard"
            elif elevation_gain > 150 or distance_km > 4:
                difficulty = "Moderate"
            else:
                difficulty = "Easy"

            # Create route object
            sample_routes.append({
                "name": name,
                "type": "Hiking",
                "coordinates": coordinates,
                "distance_km": distance_km,
                "elevation_gain": elevation_gain,
                "estimated_time_min": duration_min,
                "difficulty": difficulty
            })
        except Exception as e:
            st.error(f"Error creating route object for {name}: {str(e)}")

    return sample_routes