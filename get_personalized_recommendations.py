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

# Function to get personalized recommendations
def get_personalized_recommendations(activities):
    """Sort activities based on personalized recommendations"""
    if not st.session_state.recommendation_model or not activities:
        return activities
    
    # Determine activity type for first activity
    activity_type = activities[0].get('type', 'Business')
    model_type = 'outdoor' if activity_type in ['Hiking', 'Cycling'] else 'business'
    
    # If we don't have a model for this type, return original list
    if model_type not in st.session_state.recommendation_model:
        return activities
    
    # Extract features for all activities
    features_list = []
    for activity in activities:
        features_list.append(extract_features(activity)[0])
    
    features_array = np.array(features_list)
    
    # Get model for this activity type
    model = st.session_state.recommendation_model[model_type]
    
    # Calculate distances to liked activities
    distances, _ = model.kneighbors(features_array)
    
    # Calculate average distance for each activity (smaller is better)
    avg_distances = np.mean(distances, axis=1)
    
    # Sort activities by similarity (smaller distance is better)
    sorted_indices = np.argsort(avg_distances)
    sorted_activities = [activities[i] for i in sorted_indices]
    
    return sorted_activities