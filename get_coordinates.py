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

# Function to get coordinates from location name
def get_coordinates(location_name):
    try:
        geolocator = Nominatim(user_agent="final_tinder_app")
        location = geolocator.geocode(location_name)
        if location:
            return location.latitude, location.longitude
        else:
            st.error(f"Could not find coordinates for {location_name}")
            return None
    except Exception as e:
        st.error(f"Error getting coordinates: {e}")
        return None
