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

# Function to train KNN model based on liked activities
def train_recommendation_model():
    """Train KNN model based on user's liked activities"""
    if len(st.session_state.user_profile['liked_activities']) < 3:
        # Need at least 3 liked activities to train a meaningful model
        return None
    
    # Separate activities by type since they have different feature sets
    outdoor_activities = []
    business_activities = []
    
    for activity in st.session_state.user_profile['liked_activities']:
        if activity['type'] in ['Hiking', 'Cycling']:
            outdoor_activities.append(activity)
        else:
            business_activities.append(activity)
    
    models = {}
    
    # Train outdoor activity model if enough data
    if len(outdoor_activities) >= 3:
        features = np.array([a['features'] for a in outdoor_activities])
        model = NearestNeighbors(n_neighbors=min(3, len(outdoor_activities)), algorithm='ball_tree')
        model.fit(features)
        models['outdoor'] = model
    
    # Train business activity model if enough data
    if len(business_activities) >= 3:
        features = np.array([a['features'] for a in business_activities])
        model = NearestNeighbors(n_neighbors=min(3, len(business_activities)), algorithm='ball_tree')
        model.fit(features)
        models['business'] = model
    
    return models if models else None
