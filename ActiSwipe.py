import streamlit as st
import requests
import json
import folium
import polyline
import random
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster
import pandas as pd
from PIL import Image
import io
import base64
import os
from datetime import datetime
import numpy as np
from streamlit_card import card
from geopy.geocoders import Nominatim
from sklearn.neighbors import NearestNeighbors
import pickle

# Import application modules
from fetch_cycling_route import fetch_cycling_routes
from fetch_hiking_routes import fetch_hiking_routes
from get_coordinates import get_coordinates
from fetch_yelp_activities import fetch_yelp_activities
from add_user_profile_ui import add_user_profile_ui
from display_liked_activities import display_liked_activities
from display_activity_card import display_activity_card
from create_route_map import create_route_map

# Set page configuration
st.set_page_config(
    page_title="ActiSwipe - Activity Recommender",
    page_icon="🧭",
    layout="wide"
)

# Initialize session state variables if they don't exist
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'liked_activities' not in st.session_state:
    st.session_state.liked_activities = []
if 'current_activities' not in st.session_state:
    st.session_state.current_activities = []
if 'location_coordinates' not in st.session_state:
    st.session_state.location_coordinates = None
if 'current_activity_type' not in st.session_state:
    st.session_state.current_activity_type = None
if 'image_index' not in st.session_state:
    st.session_state.image_index = 0
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {'liked_activities': [], 'preferences': {}}
if 'recommendation_model' not in st.session_state:
    st.session_state.recommendation_model = None

# Define debug function for Streamlit
def st_debug(message):
    """Custom debug function that can be toggled on/off"""
    debug_mode = st.session_state.get('debug_mode', False)
    if debug_mode:
        st.info(f"DEBUG: {message}")

# Attach the debug function to the st module
st.debug = st_debug

# Main application
def main():
    # App header
    st.title("🧭 ActiSwipe - Activity Recommender")
    st.write("Swipe through activities like you're finding your next date!")
    
    # Debug toggle in expander
    with st.expander("Developer Options"):
        st.session_state.debug_mode = st.checkbox("Enable Debug Mode", value=st.session_state.get('debug_mode', False))
        if st.button("Clear Session State"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.success("Session state cleared!")
    
    # Sidebar for filters and options
    with st.sidebar:
        st.header("Find Your Next Activity")
        
        # Location input
        location_input = st.text_input("Enter Location (City, Address, etc.)", "Zürich")
        
        # Get coordinates button
        if st.button("Set Location"):
            try:
                coordinates = get_coordinates(location_input)
                if coordinates:
                    # Make sure coordinates are floats
                    st.session_state.location_coordinates = (float(coordinates[0]), float(coordinates[1]))
                    st.success(f"Location set to: {location_input} ({coordinates[0]:.4f}, {coordinates[1]:.4f})")
                    # Reset current index and activities
                    st.session_state.current_index = 0
                    st.session_state.current_activities = []
                else:
                    st.error(f"Could not find coordinates for {location_input}")
            except Exception as e:
                st.error(f"Error setting location: {str(e)}")
        
        # Distance range slider
        radius = st.slider("Distance Range (km)", min_value=1, max_value=40, value=10)
        radius_meters = radius * 1000  # Convert to meters for API
        
        # Activity type selector
        activity_type = st.selectbox(
            "Activity Type",
            ["Restaurant", "Coffee & Drinks", "Bar", "Hotel / Stay", "Hiking", "Cycling"]
        )
        
        # Button to fetch activities
        if st.button("Find Activities"):
            if st.session_state.location_coordinates:
                latitude, longitude = st.session_state.location_coordinates
                
                with st.spinner("Fetching activities..."):
                    if activity_type in ["Restaurant", "Coffee & Drinks", "Bar", "Hotel / Stay"]:
                        activities = fetch_yelp_activities(latitude, longitude, activity_type, radius_meters)
                    elif activity_type == "Hiking":
                        activities = fetch_hiking_routes(latitude, longitude, radius_meters)
                    elif activity_type == "Cycling":
                        activities = fetch_cycling_routes(latitude, longitude, radius_meters)
                    
                    if activities:
                        st.session_state.current_activities = activities
                        st.session_state.current_index = 0
                        st.session_state.current_activity_type = activity_type
                        st.success(f"Found {len(activities)} {activity_type} activities!")
                    else:
                        st.error(f"No {activity_type} activities found. Try expanding your search radius or changing location.")
            else:
                st.error("Please set a location first!")
        
        # Show liked activities button
        if st.button("View Liked Activities"):
            st.session_state.show_liked = True
        else:
            st.session_state.show_liked = False
    
    add_user_profile_ui()

    # Main content area
    if 'show_liked' in st.session_state and st.session_state.show_liked:
        display_liked_activities()
    else:
        # Initial prompt if no location is set
        if not st.session_state.location_coordinates:
            st.info("👈 Start by setting your location in the sidebar!")
        # Display activities if available
        elif st.session_state.current_activities:
            display_activity_card()
        else:
            st.info("👈 Select an activity type and click 'Find Activities' to start browsing!")

if __name__ == "__main__":
    main()