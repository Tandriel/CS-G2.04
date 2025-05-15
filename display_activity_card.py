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
import numpy as np
from sklearn.neighbors import NearestNeighbors
import pickle
from create_route_map import create_route_map
from pass_activity import pass_activity
from like_activity import like_activity
# Function to display current activity card
def display_activity_card():
    if not st.session_state.current_activities or st.session_state.current_index >= len(st.session_state.current_activities):
        st.info("No more activities to show. Try changing your filters or location!")
        return
    if st.session_state.recommendation_model:
        st.markdown("✨ **Recommendations personalized based on your likes**")
    
    activity = st.session_state.current_activities[st.session_state.current_index]
    
    # Container for the card
    with st.container():
        # Display the image carousel or map
        col1, col2, col3 = st.columns([1, 4, 1])
        
        with col1:
            # Previous image button
            if st.button("◀️", key="prev_img"):
                if 'photos' in activity and len(activity['photos']) > 1:
                    st.session_state.image_index = (st.session_state.image_index - 1) % len(activity['photos'])
        
        with col2:
            activity_type = activity.get('type', 'Business')
            
            if activity_type in ['Hiking', 'Cycling']:
                # Display route map
                if 'coordinates' in activity:
                    m = create_route_map(activity['coordinates'])
                    folium_static(m, width=600, height=400)
            else:
                # Display business image
                image_url = activity.get('image_url')
                if image_url:
                    st.image(image_url, use_column_width=True)
                else:
                    st.image("https://via.placeholder.com/600x400?text=No+Image+Available", use_column_width=True)
        
        with col3:
            # Next image button
            if st.button("▶️", key="next_img"):
                if 'photos' in activity and len(activity['photos']) > 1:
                    st.session_state.image_index = (st.session_state.image_index + 1) % len(activity['photos'])
        
        # Activity info box
        st.subheader(activity.get('name', 'Unnamed Activity'))
        
        col1, col2 = st.columns(2)
        
        with col1:
            if activity_type in ['Hiking', 'Cycling']:
                st.write(f"**Type:** {activity_type}")
                st.write(f"**Distance:** {activity.get('distance_km', 0):.1f} km")
                st.write(f"**Est. Time:** {activity.get('estimated_time_min', 0):.0f} min")
                st.write(f"**Difficulty:** {activity.get('difficulty', 'N/A')}")
                st.write(f"**Elevation Gain:** {activity.get('elevation_gain', 0)} m")
            else:
                if 'location' in activity and 'display_address' in activity['location']:
                    address = ", ".join(activity['location']['display_address'])
                    st.write(f"**Address:** {address}")
                
                rating = activity.get('rating', 'N/A')
                if rating != 'N/A':
                    stars = "⭐" * int(rating) + ("½" if rating % 1 >= 0.5 else "")
                    st.write(f"**Rating:** {rating} {stars}")
                
                price = activity.get('price', 'N/A')
                st.write(f"**Price:** {price}")
                
                if 'distance' in activity:
                    distance_km = activity['distance'] / 1000
                    st.write(f"**Distance:** {distance_km:.1f} km")
        
        with col2:
            if activity_type not in ['Hiking', 'Cycling']:
                if 'categories' in activity:
                    categories = ", ".join([cat['title'] for cat in activity['categories']])
                    st.write(f"**Categories:** {categories}")
                
                if 'display_phone' in activity:
                    st.write(f"**Phone:** {activity['display_phone']}")
                
                if 'url' in activity:
                    st.write(f"[View on Yelp]({activity['url']})")
        
        # Action buttons
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("👎 Pass", key="pass_btn", use_container_width=True):
                pass_activity()
                st.rerun()
        
        with col3:
            if st.button("👍 Like", key="like_btn", use_container_width=True):
                like_activity()
                st.rerun()
