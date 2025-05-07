import streamlit as st
import html
import pydeck as pdk
from ui_components import inject_custom_css

def render_activity_card(activity, distance_km):
    """
    Render an activity as a swipe-style card with image carousel and inline map.
    """
    inject_custom_css()

    name = html.escape(activity.get("name", "Unknown"))
    category = html.escape(activity.get("category", "Activity"))
    rating = activity.get("rating", "N/A")
    address = html.escape(activity.get("address", ""))
    price = activity.get("price", "")
    yelp_url = activity.get("url", "")
    photos = activity.get("photos") or [activity.get("image_url")]
    dist_text = f"{distance_km:.1f} km away" if distance_km is not None else ""
    lat = activity.get("lat")
    lon = activity.get("lon")

    # Setup carousel image index
    key_prefix = f"{name.replace(' ', '_')}_carousel"
    index_key = f"image_index_{key_prefix}"
    if index_key not in st.session_state:
        st.session_state[index_key] = 0

    max_index = len(photos) + (1 if lat and lon else 0)
    index = st.session_state[index_key]

    # Carousel navigation buttons
    col1, col2, col3 = st.columns([1, 6, 1])
    with col1:
        if st.button("⬅️", key=f"prev_{key_prefix}"):
            st.session_state[index_key] = max(0, index - 1)
    with col3:
        if st.button("➡️", key=f"next_{key_prefix}"):
            st.session_state[index_key] = min(max_index - 1, index + 1)

    st.markdown("<div class='card'>", unsafe_allow_html=True)

    # Show image or map
    if index < len(photos):
        st.markdown(f"<img src=\"{photos[index]}\" alt=\"activity image\">", unsafe_allow_html=True)
    elif lat and lon:
        st.pydeck_chart(pdk.Deck(
            map_style='mapbox://styles/mapbox/light-v9',
            initial_view_state=pdk.ViewState(
                latitude=lat,
                longitude=lon,
                zoom=13,
                pitch=0,
            ),
            layers=[
                pdk.Layer(
                    'ScatterplotLayer',
                    data=[{"position": [lon, lat]}],
                    get_position='position',
                    get_color='[200, 30, 0, 160]',
                    get_radius=100,
                ),
            ],
        ))

    st.markdown(f"""
        <h3>{name}</h3>
        <p><strong>{category}</strong> • ⭐ {rating} • {price}</p>
        <p>{address}</p>
        <p>{dist_text}</p>
    </div>
    """, unsafe_allow_html=True)
