import streamlit as st
import html
import pydeck as pdk

def render_carousel_card(activity, distance_km=None):
    """Render an activity card with a carousel of images and a map (if available)."""
    # Prepare activity data
    name = html.escape(activity.get("name", "Unknown"))
    category = html.escape(activity.get("category", "Activity"))
    rating = activity.get("rating", "N/A")
    address = html.escape(activity.get("address", ""))
    price = activity.get("price", "")
    photos = activity.get("photos") or [activity.get("image_url")]
    lat = activity.get("lat")
    lon = activity.get("lon")

    # Use at most two photos for the carousel, plus a map placeholder if coordinates are available
    items = photos[:2]
    if lat and lon:
        items.append("__map__")

    # Initialize carousel index in session state if not present
    if "carousel_index" not in st.session_state:
        st.session_state.carousel_index = 0
    index = st.session_state.carousel_index
    max_index = len(items) - 1

    # Carousel navigation buttons (Previous/Next)
    cols = st.columns([1, 6, 1])
    with cols[0]:
        if st.button("⬅️", key=f"left-{name}"):
            st.session_state.carousel_index = max(index - 1, 0)
    with cols[2]:
        if st.button("➡️", key=f"right-{name}"):
            st.session_state.carousel_index = min(index + 1, max_index)

    # Card container for carousel content
    st.markdown('<div class="card-container">', unsafe_allow_html=True)

    # Display either an image or the map, depending on the current carousel item
    if items[index] == "__map__":
        # Show an interactive map with a marker and label at the activity location
        label_text = name
        if rating and rating != "N/A":
            label_text += f" – {rating}★"
        map_layers = [
            # Marker for location
            pdk.Layer(
                "ScatterplotLayer",
                data=[{"position": [lon, lat]}],
                get_position="position",
                get_color=[200, 30, 0, 160],
                get_radius=150
            )
        ]
        # Add a text label layer for name (and rating if available)
        map_layers.append(
            pdk.Layer(
                "TextLayer",
                data=[{"position": [lon, lat], "text": label_text}],
                get_position="position",
                get_text="text",
                get_color=[0, 0, 0, 200],
                get_size=16,
                get_alignment_baseline="'bottom'"
            )
        )
        st.pydeck_chart(pdk.Deck(
            map_style='mapbox://styles/mapbox/light-v9',
            initial_view_state=pdk.ViewState(latitude=lat, longitude=lon, zoom=13, pitch=0),
            layers=map_layers
        ))
    else:
        # Display photo
        image_url = items[index]
        if image_url:  # Only display if URL is valid
            st.markdown(f'<img src="{image_url}" alt="Activity Image">', unsafe_allow_html=True)
        else:
            st.markdown(f'<p><em>No image available</em></p>', unsafe_allow_html=True)

    # Display activity info (name, category, rating, price, address, distance)
    info_parts = [f"<strong>{category}</strong>"]
    if rating and rating != "N/A":
        info_parts.append(f"⭐ {rating}")
    if price:
        info_parts.append(html.escape(price))
    info_line = " • ".join(info_parts)
    info_html = f"<h2>{name}</h2>\n<p>{info_line}</p>\n<p>{address}</p>"
    if distance_km is not None:
        info_html += f"\n<p>{distance_km:.1f} km away</p>"
    st.markdown(info_html + "\n</div>", unsafe_allow_html=True)
