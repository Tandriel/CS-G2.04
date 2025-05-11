import streamlit as st

def inject_custom_css():
    """Inject shared CSS styles for card containers and content."""
    st.markdown("""
    <style>
    .card, .card-container {
        background-color: #fff;
        border-radius: 20px;
        padding: 20px;
        max-width: 700px;
        margin: 20px auto;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
        text-align: center;
        font-family: 'Segoe UI', sans-serif;
        color: #000;
    }
    .card h2, .card-container h2 {
        font-size: 26px;
        margin: 10px 0 6px;
        color: #000;
    }
    .card p, .card-container p {
        margin: 6px 0;
        font-size: 16px;
        color: #222;
    }
    .card img, .card-container img {
        width: 100%;
        max-height: 400px;
        height: auto;
        object-fit: cover;
        border-radius: 14px;
        background-color: #f0f0f0;
    }
    </style>
    """, unsafe_allow_html=True)
