import folium
import streamlit as st
from io import BytesIO
import base64
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import os

def map_to_image(m):
    """
    Converts a Folium map to a base64 encoded image to display in Streamlit
    
    Parameters:
    - m: Folium map object
    
    Returns:
    - URL or base64 encoded image data
    """
    if m is None:
        return "https://via.placeholder.com/400x300?text=Map+Preview"
    
    try:
        # Create a temporary HTML file
        temp_html = "temp_map.html"
        m.save(temp_html)
        
        # Generate a data URL from the HTML - this is a simpler approach
        # that will display the interactive map directly
        map_html = m._repr_html_()
        html_data = f"""
        <div style="width:100%; height:400px; overflow:hidden;">
            {map_html}
        </div>
        """
        
        # Attempt to use selenium if available to create an actual image
        try:
            # Setup headless Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=800,600")
            
            # Initialize browser
            browser = webdriver.Chrome(options=chrome_options)
            browser.get(f"file://{os.path.abspath(temp_html)}")
            
            # Give time for the map to render
            time.sleep(1)
            
            # Take screenshot
            img = BytesIO(browser.get_screenshot_as_png())
            browser.quit()
            
            # Clean up temporary file
            if os.path.exists(temp_html):
                os.remove(temp_html)
            
            # Convert to base64 for embedding
            img_base64 = base64.b64encode(img.getvalue()).decode()
            return f"data:image/png;base64,{img_base64}"
            
        except Exception as e:
            st.debug(f"Screenshot method failed, falling back to HTML: {str(e)}")
            # Return the HTML method as a fallback
            return html_data
            
    except Exception as e:
        st.error(f"Error converting map to image: {str(e)}")
        return "https://via.placeholder.com/400x300?text=Map+Preview+Error"

def get_map_html(m):
    """
    Returns the HTML representation of a Folium map
    
    Parameters:
    - m: Folium map object
    
    Returns:
    - HTML string
    """
    if m is None:
        return "<div>Map preview not available</div>"
    
    try:
        # Get map HTML with additional styling to ensure it displays properly
        map_html = m._repr_html_()
        html = f"""
        <div style="width:100%; height:400px; overflow:hidden; border-radius:10px; box-shadow:0 4px 8px rgba(0,0,0,0.1);">
            {map_html}
        </div>
        <div style="font-size:12px; color:#666; text-align:right; margin-top:2px;">
            Map data © OpenStreetMap contributors
        </div>
        """
        return html
    except Exception as e:
        st.error(f"Error getting map HTML: {str(e)}")
        return "<div>Error rendering map preview</div>"