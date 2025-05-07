import streamlit as st
import html
import pydeck as pdk
from ui_components import inject_custom_css

def render_activity_details(activity):
    import streamlit as st
    import html
    name = html.escape(activity.get("name", "Unknown"))
    category = html.escape(activity.get("category", "Activity"))
    rating = activity.get("rating", "N/A")
    price = activity.get("price", "")
    address = html.escape(activity.get("address", "No address available"))
    image_url = activity.get("image_url") or "https://source.unsplash.com/600x400/?activity"
    yelp_url = activity.get("url", "")

    st.markdown(f"""
    <div class="card">
        <img src="{image_url}" alt="activity image">
        <h3>{name}</h3>
        <p><strong>{category}</strong> • ⭐ {rating} • {price}</p>
        <p>{address}</p>
    </div>
    """, unsafe_allow_html=True)

    if yelp_url:
        st.markdown(f"\n🔗 [View on Yelp]({yelp_url})", unsafe_allow_html=True)

    lat = activity.get("lat")
    lon = activity.get("lon")
    if lat and lon:
        maps_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
        st.markdown(f"🗺️ [Open in Google Maps]({maps_url})", unsafe_allow_html=True)
