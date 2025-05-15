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

# API keys
YELP_API_KEY = "3CDquv2YIfVJBzNuoyau9lsDbqv21Zohj2ewjXvFlJDovEAGaiJWihHDxImRJatHXFA--wY1vVGuvLUX2bMyS-ipwsXjyDII3afybeUrgoisA1GbR8o0oOSB5bIYaHYx"  # Replace with your actual API key
OPENROUTE_API_KEY = "5b3ce3597851110001cf6248ee3c2977b26a41be8e066e26be3f95bf"  # Your OpenRouteService API key
def extract_features(activity):
    """Extract relevant features from an activity for ML processing"""
    features = []
    
    # Common features
    activity_type = activity.get('type', 'Business')
    
    if activity_type in ['Hiking', 'Cycling']:
        # Outdoor activity features
        features = [
            activity.get('distance_km', 0),
            activity.get('estimated_time_min', 0),
            # Convert difficulty to numeric value
            {'Easy': 1, 'Moderate': 2, 'Hard': 3}.get(activity.get('difficulty', 'Easy'), 1),
            activity.get('elevation_gain', 0)
        ]
    else:
        # Business activity features
        features = [
            activity.get('rating', 3.0),  # Default to 3.0 if not available
            len(activity.get('categories', [])),  # Number of categories
            {'$': 1, '$$': 2, '$$$': 3, '$$$$': 4}.get(activity.get('price', '$$'), 2),  # Price level
            activity.get('review_count', 0) / 100 if activity.get('review_count') else 0  # Normalized review count
        ]
        
    return np.array(features).reshape(1, -1)