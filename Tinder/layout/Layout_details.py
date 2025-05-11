import streamlit as st
import html
import pydeck as pdk  # (pydeck is actually not used here, can be omitted if not needed)
from app.ui_components import inject_custom_css

def render_activity_details(activity):
    """
    Display a detailed view of a matched activity or event, with extended information.
    """
    inject_custom_css()

    # Extract details, escaping HTML in text fields
    name = html.escape(activity.get("name", "Unknown"))
    category = html.escape(activity.get("category", "Activity"))
    rating = activity.get("rating", "N/A")
    price = activity.get("price", "")
    address = html.escape(activity.get("address", "No address available"))
    image_url = activity.get("image_url") or (activity.get("photos")[0] if activity.get("photos") else "https://source.unsplash.com/600x400/?activity")
    event_url = activity.get("url", "")
    date = activity.get("date", "")

    # Build the HTML for the card
    info_parts = [f"<strong>{category}</strong>"]
    if rating and rating != "N/A":
        info_parts.append(f"⭐ {rating}")
    if price:
        info_parts.append(html.escape(price))
    info_line = " • ".join(info_parts)

    detail_html = f'<div class="card">'
    detail_html += f'<img src="{image_url}" alt="activity image">'
    detail_html += f'<h2>{name}</h2>'
    detail_html += f'<p>{info_line}</p>'
    detail_html += f'<p>{address}</p>'
    if date:
        detail_html += f'<p><strong>Date:</strong> {html.escape(date)}</p>'
    detail_html += '</div>'
    st.markdown(detail_html, unsafe_allow_html=True)

    # External link (Yelp or Eventfrog)
    if event_url:
        link_text = "View more details"
        if "yelp.com" in event_url:
            link_text = "View on Yelp"
        elif "eventfrog" in event_url:
            link_text = "View on Eventfrog"
        st.markdown(f"🔗 [{link_text}]({event_url})", unsafe_allow_html=True)

    # Map link for directions
    lat = activity.get("lat")
    lon = activity.get("lon")
    if lat and lon:
        maps_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
        st.markdown(f"🗺️ [Open in Google Maps]({maps_url})", unsafe_allow_html=True)
