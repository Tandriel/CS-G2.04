import streamlit as st
import html
import pydeck as pdk
from ui_components import inject_custom_css
from activity_types.hiking import get_hiking_route
from activity_types.cycling import get_cycling_route
from layouts.carousel_card import render_carousel_card

def render_activity_card(activity, distance_km=None):
    """
    Display a swipe-style activity card. For hiking/cycling, show a route map and trail info.
    For other activities, use the image carousel card.
    """
    inject_custom_css()  # Ensure custom CSS (e.g., card styling) is applied

    # Extract and sanitize basic activity info
    name = html.escape(activity.get("name", "Unknown"))
    category = html.escape(activity.get("category", "Activity"))
    category_lower = category.lower()
    rating = activity.get("rating", "N/A")
    address = html.escape(activity.get("address", ""))
    price = activity.get("price", "")
    # (Optional: Yelp URL could be used for a "View on Yelp" link in details view)
    lat = activity.get("lat")
    lon = activity.get("lon")

    if category_lower in ["hiking", "cycling"]:
        # --- Hiking/Cycling: Display route map and trail information ---
        # Only proceed if we have user location and destination coordinates
        user_lat, user_lon = st.session_state.get("user_location", (None, None))
        if user_lat and user_lon and lat and lon:
            # Get route path and stats from OpenRouteService helper functions
            route = get_hiking_route(user_lat, user_lon, lat, lon) if category_lower == "hiking" \
                    else get_cycling_route(user_lat, user_lon, lat, lon)
            path = route["path"]  # list of [lat, lon] or [lon, lat] coordinates forming the route
            trail_distance = route["distance"] / 1000.0  # convert meters to kilometers
            duration_min = int(route["duration"] / 60.0)  # convert seconds to minutes
            ascent = route.get("ascent", 0)
            descent = route.get("descent", 0)

            # Open a card container (HTML) and insert the activity header
            st.markdown(f"""
            <div class="card">
                <h3>{name}</h3>
                <p><strong>{category}</strong> • ⭐ {rating} • {price}</p>
                <p>{address}</p>
            """, unsafe_allow_html=True)

            # Show interactive route map with Pydeck (path and marker)
            st.pydeck_chart(pdk.Deck(
                map_style="mapbox://styles/mapbox/light-v9",
                initial_view_state=pdk.ViewState(latitude=lat, longitude=lon, zoom=13, pitch=0),
                layers=[
                    # Path layer for the trail/route
                    pdk.Layer(
                        "PathLayer",
                        data=[{"path": path}],
                        get_path="path",
                        get_color=[0, 100, 200],
                        width_scale=10,
                        width_min_pixels=2,
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

            # Close the card container with trail info list
            st.markdown(f"""
                <p><strong>Trail Info:</strong></p>
                <ul>
                    <li>Length: {trail_distance:.2f} km</li>
                    <li>Duration: ~{duration_min} min</li>
                    <li>Ascent: +{int(ascent)} m &nbsp;•&nbsp; Descent: -{int(descent)} m</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        else:
            # If no user location or coordinates, fall back to a basic carousel card display
            render_carousel_card(activity, distance_km)
    else:
        # --- Other categories: use the generic carousel card layout ---
        render_carousel_card(activity, distance_km)
