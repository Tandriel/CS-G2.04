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
from export_user_profile import export_user_profile
from import_user_profile import import_user_profile

def add_user_profile_ui():
    with st.sidebar:
        st.divider()
        st.subheader("📊 User Profile")
        
        # Show basic stats
        total_liked = len(st.session_state.user_profile['liked_activities'])
        st.write(f"Total liked activities: {total_liked}")
        
        if total_liked > 0:
            # Show top preferences if available
            with st.expander("Your Preferences"):
                prefs = st.session_state.user_profile['preferences']
                
                # Show preferred activity types
                if 'activity_types' in prefs and prefs['activity_types']:
                    st.write("**Favorite activity types:**")
                    sorted_types = sorted(prefs['activity_types'].items(), key=lambda x: x[1], reverse=True)
                    for t, count in sorted_types[:3]:
                        st.write(f"- {t}: {count} likes")
                
                # Show other preferences based on what's available
                if 'difficulty' in prefs and prefs['difficulty']:
                    st.write("**Preferred difficulty:**")
                    sorted_diff = sorted(prefs['difficulty'].items(), key=lambda x: x[1], reverse=True)
                    st.write(f"- {sorted_diff[0][0]}")
                
                if 'price' in prefs and prefs['price']:
                    st.write("**Price preference:**")
                    sorted_price = sorted(prefs['price'].items(), key=lambda x: x[1], reverse=True)
                    st.write(f"- {sorted_price[0][0]}")
        
        # Export/Import buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Save Profile"):
                if export_user_profile():
                    st.success("Profile saved!")
        
        with col2:
            if st.button("📂 Load Profile"):
                if import_user_profile():
                    st.success("Profile loaded!")
                else:
                    st.warning("No profile found.")