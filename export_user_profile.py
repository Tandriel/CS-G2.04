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

# Function to export user profile to file
def export_user_profile():
    """Export user profile to a file"""
    try:
        with open('user_profile.pkl', 'wb') as f:
            pickle.dump(st.session_state.user_profile, f)
        return True
    except Exception as e:
        st.error(f"Error saving user profile: {e}")
        return False

