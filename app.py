# app.py
import streamlit as st
from yelp_fetcher import geocode_location, fetch_yelp_activities
from ui_components import inject_custom_css
from layouts.layout_card import render_activity_card
from layouts.layout_details import render_activity_details

# --- Inject style ---
inject_custom_css()

# --- App Header ---
st.title("Tinder for Activities 💖")
st.write("Find cool places around you and swipe your favorites!")

# --- Sidebar Search Filters ---
city = st.text_input("Enter your city or town in Switzerland:", "Zürich")
category = st.selectbox("What are you looking for?", [
    "restaurants", "bars", "coffee", "hiking", "cycling", "swimming", "sightseeing"])
radius_km = st.slider("Search radius (km):", 1, 20, 5)

# --- Button to trigger search ---
if st.button("Find Activities"):
    st.session_state.image_index = 0
    latlon = geocode_location(city)

    if not latlon:
        st.error("Location not found.")
    else:
        lat, lon = latlon
        activities = fetch_yelp_activities(lat, lon, category, radius_m=radius_km * 1000)

        if not activities:
            st.error("No activities found nearby.")
        else:
            # Compute distances
            from math import radians, sin, cos, sqrt, atan2
            def haversine(coord1, coord2):
                R = 6371
                lat1, lon1 = map(radians, coord1)
                lat2, lon2 = map(radians, coord2)
                dlat = lat2 - lat1
                dlon = lon2 - lon1
                a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
                c = 2 * atan2(sqrt(a), sqrt(1-a))
                return R * c

            for act in activities:
                act["distance"] = haversine((lat, lon), (act["lat"], act["lon"]))

            activities.sort(key=lambda x: x["distance"])
            st.session_state.activities = activities
            st.session_state.current = 0

# --- Display Swipable Cards ---
if "activities" in st.session_state and st.session_state.activities:
    index = st.session_state.get("current", 0)
    activities = st.session_state.activities

    if index < len(activities):
        activity = activities[index]
        render_activity_card(activity, activity["distance"])

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("❌ Skip"):
                st.session_state.current += 1
        with col2:
            if st.button("💖 Match"):
                st.session_state.match = activity
                st.session_state.current += 1

    else:
        st.success("You've reached the end! Here are your matches:")
        if "match" in st.session_state:
            render_activity_details(st.session_state.match)

        if st.button("🔄 Restart"):
            for key in ["activities", "current", "match"]:
                st.session_state.pop(key, None)
