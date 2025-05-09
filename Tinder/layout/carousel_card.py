import streamlit as st
import html
import pydeck as pdk
from ui_components import inject_custom_css

def render_carousel_card(activity, distance_km=None):
    """
    Render a carousel-style card with up to two images and a map marker for the activity.
    Displays activity name, category, rating, price, address, and distance.
    """
    inject_custom_css()  # Ensure card CSS is loaded for styling

    # Extract and sanitize activity information
    name = html.escape(activity.get("name", "Unknown"))
    category = html.escape(activity.get("category", "Activity"))
    rating = activity.get("rating", "N/A")
    address = html.escape(activity.get("address", ""))
    price = activity.get("price", "")
    distance_text = f"{distance_km:.1f} km away" if distance_km is not None else ""
    lat = activity.get("lat")
    lon = activity.get("lon")

    # Prepare list of images (up to 2) for the carousel. Fallback to a placeholder if none.
    photos = activity.get("photos")
    if not photos or len(photos) == 0:
        # If no photo list, try a single image_url or use a generic Unsplash image
        image_url = activity.get("image_url")
        photos = [image_url] if image_url else []
    # If still no photos, use a random generic image as placeholder
    if len(photos) == 0:
        photos = ["https://source.unsplash.com/600x400/?activity"]
    # Limit to at most 2 photos for the carousel
    photos = photos[:2]

    # Determine total slides (photos + map if location available)
    show_map = (lat is not None and lon is not None)
    total_slides = len(photos) + (1 if show_map else 0)

    # Initialize session state index for this carousel if not set
    carousel_key = f"{name.replace(' ', '_')}_carousel"
    index_key = f"index_{carousel_key}"
    if index_key not in st.session_state:
        st.session_state[index_key] = 0
    current_index = st.session_state[index_key]

    # Carousel navigation arrows
    nav_cols = st.columns([1, 6, 1])  # three columns: left arrow, spacer, right arrow
    with nav_cols[0]:
        if st.button("⬅️", key=f"prev_{carousel_key}") and current_index > 0:
            st.session_state[index_key] = current_index - 1
            current_index = st.session_state[index_key]
    with nav_cols[2]:
        if st.button("➡️", key=f"next_{carousel_key}") and current_index < total_slides - 1:
            st.session_state[index_key] = current_index + 1
            current_index = st.session_state[index_key]

    # Open the card container
    st.markdown(f"<div class='card'>", unsafe_allow_html=True)

    # Display the current slide: either an image or the map marker
    if current_index < len(photos):
        # Show image slide
        img_url = photos[current_index]
        st.markdown(f"<img src='{img_url}' alt='Activity image' style='width:100%;'>", unsafe_allow_html=True)
    elif show_map and current_index == len(photos):
        # Show map slide (Pydeck map with a marker at the activity location)
        st.pydeck_chart(pdk.Deck(
            map_style="mapbox://styles/mapbox/light-v9",
            initial_view_state=pdk.ViewState(latitude=lat, longitude=lon, zoom=13, pitch=0),
            layers=[
                pdk.Layer(
                    "ScatterplotLayer",
                    data=[{"position": [lon, lat]}],
                    get_position="position",
                    get_color=[200, 30, 0, 160],  # semi-transparent red marker
                    get_radius=100
                )
            ]
        ), use_container_width=True)

    # Display the activity metadata under the image/map, then close the card container
    st.markdown(f"""
        <h3>{name}</h3>
        <p><strong>{category}</strong> • ⭐ {rating} • {price}</p>
        <p>{address}</p>
        <p>{distance_text}</p>
    </div>
    """, unsafe_allow_html=True)
