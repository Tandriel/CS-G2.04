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
from train_recommendation_model import train_recommendation_model 
from save_to_user_profile import save_to_user_profile 
# Function to like an activity
def like_activity():
    if st.session_state.current_activities and st.session_state.current_index < len(st.session_state.current_activities):
        current_activity = st.session_state.current_activities[st.session_state.current_index]
        
        # Add to liked activities list (original functionality)
        st.session_state.liked_activities.append(current_activity)
        
        # Save to user profile and update preferences
        save_to_user_profile(current_activity)
        
        # Train recommendation model if enough data
        st.session_state.recommendation_model = train_recommendation_model()
        
        # Move to next activity
        st.session_state.current_index += 1
        st.session_state.image_index = 0  # Reset image index for next activity

# Function to import user profile from file