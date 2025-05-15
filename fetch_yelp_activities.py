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
from get_personalized_recommendations import get_personalized_recommendations 
from key import YELP_API_KEY
def fetch_yelp_activities(latitude, longitude, category, radius=10000, limit=20):
    # Original code to fetch activities from Yelp API
    url = "https://api.yelp.com/v3/businesses/search"
    
    headers = {
        "Authorization": f"Bearer {YELP_API_KEY}"
    }
    
    category_map = {
        "Restaurant": "restaurants",
        "Coffee & Drinks": "coffee,cafes",
        "Bar": "bars,pubs",
        "Hotel / Stay": "hotels"
    }
    
    category_alias = category_map.get(category, category)
    
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "categories": category_alias,
        "radius": radius,
        "limit": limit,
        "sort_by": "rating"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            activities = response.json().get("businesses", [])
            
            # Apply personalized recommendations if model exists
            if st.session_state.recommendation_model:
                activities = get_personalized_recommendations(activities)
            
            return activities
        else:
            st.error(f"Error fetching from Yelp API: {response.status_code}, {response.text}")
            return []
    except Exception as e:
        st.error(f"Exception when calling Yelp API: {e}")
        return []