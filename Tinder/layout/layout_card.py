import streamlit as st
import html
import pydeck as pdk
from app.ui_components import inject_custom_css
from activities.hiking import get_hiking_route
from activities.cycling import get_cycling_route
from layout.carousel_card import render_carousel_card

def render_activity_card(activity, distance_km=None):
    """
    Display a swipe-style activity card. For hiking/cycling, show a route map and trail info.
    For other activities, use the image carousel card.
    """
    inject_custom_css()  # Ensure custom CSS is applied for the cards

    # Extract and sanitize basic activity info
    name = html.escape(activity.get("name", "Unknown"))
    category = html.escape(activity.get("category", "Activity"))
    category_lower = category.lower()
    rating = activity.get("rating", "N/A")
    address = html.escape(activity.get("address", "")) or "Location not available"
    price = activity.get("price", "")
    lat = activity.get("lat")
    lon = activity.get("lon")

    if category_lower in ["hiking", "cycling"]:
        # --- Hiking/Cycling: Display route map and trail information ---
        user_lat, user_lon = st.session_state.get("user_location", (None, None))
        if user_lat and user_lon and lat and lon:
            # Get route path and stats (mocked data from our functions)
            route = get_hiking_route(user_lat, user_lon, lat, lon) if category_lower == "hiking" \
                    else get_cycling_route(user_lat, user_lon, lat, lon)
            path = route["path"]
            trail_distance = route["distance"] / 1000.0  # meters to kilometers
            duration_min = int(route["duration"] / 60)   # seconds to minutes
            ascent = route.get("ascent", 0)
            descent = route.get("descent", 0)
            # Determine difficulty based on distance and elevation
            if category_lower == "hiking":
                if trail_distance > 15 or ascent > 1000:
                    difficulty = "Hard"
                elif trail_distance > 7 or ascent > 400:
                    difficulty = "Moderate"
                else:
                    difficulty = "Easy"
            else:  # cycling
                if trail_distance > 30 or ascent > 1000:
                    difficulty = "Hard"
                elif trail_distance > 15 or ascent > 500:
                    difficulty = "Moderate"
                else:
                    difficulty = "Easy"

            # Start card container with activity title and basic info
            info_parts = [f"<strong>{category}</strong>"]
            if rating and rating != "N/A":
                info_parts.append(f"⭐ {rating}")
            if price:
                info_parts.append(html.escape(price))
            info_html = " • ".join(info_parts)
            st.markdown(f"""
                <div class="card">
                    <h2>{name}</h2>
                    <p>{info_html}</p>
                    <p>{address}</p>
            """, unsafe_allow_html=True)

            # Render an interactive map with the route path and destination marker
            st.pydeck_chart(pdk.Deck(
                map_style="mapbox://styles/mapbox/outdoors-v11",
                initial_view_state=pdk.ViewState(latitude=user_lat, longitude=user_lon, zoom=12, pitch=0),
                layers=[
                    # PathLayer to draw the route polyline
                    pdk.Layer(
                        "PathLayer",
                        data=[{"path": path}],
                        get_path="path",
                        get_color=[0, 100, 200],
                        width_scale=5,
                        width_min_pixels=3,
                    ),
                    # Marker at the destination (activity location)
                    pdk.Layer(
                        "ScatterplotLayer",
                        data=[{"position": [lon, lat]}],
                        get_position="position",
                        get_color=[255, 0, 0],
                        get_radius=100
                    )
                ]
            ), use_container_width=True)

            # Close the card with trail details (distance, duration, ascent/descent, difficulty)
            st.markdown(f"""
                    <p><strong>Trail Info:</strong></p>
                    <ul>
                        <li>Length: {trail_distance:.2f} km</li>
                        <li>Duration: ~{duration_min} min</li>
                        <li>Ascent: +{int(ascent)} m &nbsp;•&nbsp; Descent: -{int(descent)} m</li>
                        <li>Difficulty: {difficulty}</li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)
        else:
            # If we lack user or activity coordinates, default to image carousel view
            render_carousel_card(activity, distance_km)
    else:
        # --- Other categories: use the generic carousel card layout ---
        render_carousel_card(activity, distance_km)
