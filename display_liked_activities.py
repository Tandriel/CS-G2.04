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
# Function to display liked activities
def display_liked_activities():
    if not st.session_state.liked_activities:
        st.info("You haven't liked any activities yet. Start swiping!")
        return
    
    st.subheader("Your Liked Activities")
    
    for i, activity in enumerate(st.session_state.liked_activities):
        with st.expander(f"{i+1}. {activity.get('name', 'Unnamed Activity')}"):
            activity_type = activity.get('type', 'Business')
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                if activity_type in ['Hiking', 'Cycling']:
                    # Display route map
                    if 'coordinates' in activity:
                        m = create_route_map(activity['coordinates'])
                        folium_static(m, width=300, height=200)
                else:
                    # Display business image
                    image_url = activity.get('image_url')
                    if image_url:
                        st.image(image_url, width=300)
                    else:
                        st.image("https://via.placeholder.com/300x200?text=No+Image+Available", width=300)
            
            with col2:
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
                    
                    if 'categories' in activity:
                        categories = ", ".join([cat['title'] for cat in activity['categories']])
                        st.write(f"**Categories:** {categories}")
                    
                    if 'display_phone' in activity:
                        st.write(f"**Phone:** {activity['display_phone']}")
                    
                    if 'url' in activity:
                        st.write(f"[View on Yelp]({activity['url']})")
