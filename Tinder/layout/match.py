import streamlit as st
import html
from Tinder.app.ui_components import inject_custom_css

def render_match_screen(activity):
    """
    Display a celebratory match screen with activity info and useful links.
    """
    inject_custom_css()

    name = html.escape(activity.get("name", "Unknown"))
    category = html.escape(activity.get("category", "Activity"))
    rating = activity.get("rating", "N/A")
    address = html.escape(activity.get("address", "No address available"))
    price = activity.get("price", "")
    image_url = activity.get("image_url") or "https://source.unsplash.com/600x400/?activity"
    yelp_url = activity.get("url", "")
    lat = activity.get("lat")
    lon = activity.get("lon")

    st.markdown(f"""
    <div class="card">
        <h2 style='color:#e91e63;'>🎉 It's a Match!</h2>
        <img src="{image_url}" alt="activity image" style="width:100%; border-radius:10px;">
        <h3>{name}</h3>
        <p><strong>{category}</strong> • ⭐ {rating} • {price}</p>
        <p>{address}</p>
    </div>
    """, unsafe_allow_html=True)

    if yelp_url:
        st.markdown(f"🔗 [View on Yelp]({yelp_url})", unsafe_allow_html=True)

    if lat and lon:
        maps_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
        st.markdown(f"🗺️ [Open in Google Maps]({maps_url})", unsafe_allow_html=True)

    st.success("💖 You can now plan your next adventure!")

