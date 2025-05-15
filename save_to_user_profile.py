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
from features import extract_features

# Function to save user preferences to user profile
def save_to_user_profile(activity):
    """Save liked activity and update user preferences"""
    # Add activity to liked activities list
    st.session_state.user_profile['liked_activities'].append({
        'id': activity.get('id', str(datetime.now())),
        'name': activity.get('name', 'Unnamed Activity'),
        'type': activity.get('type', 'Business'),
        'timestamp': datetime.now().isoformat(),
        'features': extract_features(activity).tolist()[0]
    })
    
    # Update preferences based on this activity
    activity_type = activity.get('type', 'Business')
    
    # Increment activity type counter
    if 'activity_types' not in st.session_state.user_profile['preferences']:
        st.session_state.user_profile['preferences']['activity_types'] = {}
    if activity_type not in st.session_state.user_profile['preferences']['activity_types']:
        st.session_state.user_profile['preferences']['activity_types'][activity_type] = 0
    st.session_state.user_profile['preferences']['activity_types'][activity_type] += 1
    
    # Track other preferences based on activity type
    if activity_type in ['Hiking', 'Cycling']:
        # Track preferred difficulty
        difficulty = activity.get('difficulty', 'Easy')
        if 'difficulty' not in st.session_state.user_profile['preferences']:
            st.session_state.user_profile['preferences']['difficulty'] = {}
        if difficulty not in st.session_state.user_profile['preferences']['difficulty']:
            st.session_state.user_profile['preferences']['difficulty'][difficulty] = 0
        st.session_state.user_profile['preferences']['difficulty'][difficulty] += 1
        
        # Track preferred distance range
        distance = activity.get('distance_km', 0)
        if 'distance_ranges' not in st.session_state.user_profile['preferences']:
            st.session_state.user_profile['preferences']['distance_ranges'] = {'short': 0, 'medium': 0, 'long': 0}
        if distance < 5:
            st.session_state.user_profile['preferences']['distance_ranges']['short'] += 1
        elif distance < 15:
            st.session_state.user_profile['preferences']['distance_ranges']['medium'] += 1
        else:
            st.session_state.user_profile['preferences']['distance_ranges']['long'] += 1
    else:
        # Track price preferences
        price = activity.get('price', '$$')
        if 'price' not in st.session_state.user_profile['preferences']:
            st.session_state.user_profile['preferences']['price'] = {}
        if price not in st.session_state.user_profile['preferences']['price']:
            st.session_state.user_profile['preferences']['price'][price] = 0
        st.session_state.user_profile['preferences']['price'][price] += 1
        
        # Track category preferences
        if 'categories' in activity:
            if 'categories' not in st.session_state.user_profile['preferences']:
                st.session_state.user_profile['preferences']['categories'] = {}
            for cat in activity['categories']:
                cat_title = cat['title']
                if cat_title not in st.session_state.user_profile['preferences']['categories']:
                    st.session_state.user_profile['preferences']['categories'][cat_title] = 0
                st.session_state.user_profile['preferences']['categories'][cat_title] += 1
