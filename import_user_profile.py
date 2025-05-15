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

def import_user_profile():
    """Import user profile from a file"""
    try:
        if os.path.exists('user_profile.pkl'):
            with open('user_profile.pkl', 'rb') as f:
                st.session_state.user_profile = pickle.load(f)
            
            # Retrain model with loaded data
            st.session_state.recommendation_model = train_recommendation_model()
            return True
        return False
    except Exception as e:
        st.error(f"Error loading user profile: {e}")
        return False
