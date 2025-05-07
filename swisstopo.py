import streamlit as st
import folium
import requests
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
from geopy.distance import great_circle
import numpy as np
import geocoder

DEFAULT_LAT, DEFAULT_LON = 46.8182, 8.2275
SWISS_BOUNDS = [5.96, 45.82, 10.49, 47.81]  # minlon, minlat, maxlon, maxlat

def calculate_min_distance(trail_coords, user_coords):
    if not trail_coords:
        return float('inf')
    return min(great_circle(user_coords, coord).km for coord in trail_coords)

def tile_bbox(bounds, step=1.0):
    minlon, minlat, maxlon, maxlat = bounds
    lons = np.arange(minlon, maxlon, step)
    lats = np.arange(minlat, maxlat, step)
    tiles = []
    for lon in lons:
        for lat in lats:
            tiles.append([lon, lat, min(lon+step, maxlon), min(lat+step, maxlat)])
    return tiles

def get_trails_for_bbox(bbox):
    url = "https://api3.geo.admin.ch/rest/services/all/MapServer/ch.swisstopo.swisstlm3d-wanderwege/query"
    bbox_str = f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}"
    params = {
        "geometry": bbox_str,
        "geometryType": "esriGeometryEnvelope",
        "spatialRel": "esriSpatialRelIntersects",  # Added required parameter
        "inSR": "4326",
        "outSR": "4326",
        "where": "1=1",
        "returnGeometry": "true",
        "returnDistinctValues": "false",  # Added required parameter
        "outFields": "bezeichnung,bemerkung,laenge,max_hoehe,kategorie",  # Corrected field names
        "resultRecordCount": 2000,
        "f": "json"
    }
    try:
        response = requests.get(url, params=params, timeout=30)
        if response.ok:
            return response.json().get("features", [])
    except Exception as e:
        st.warning(f"API error: {e}")
    return []

@st.cache_data(ttl=86400)
def get_all_hikes_tiled(bounds, step=1.0):
    all_features = []
    tiles = tile_bbox(bounds, step)
    for bbox in tiles:
        features = get_trails_for_bbox(bbox)
        all_features.extend(features)
    return all_features

def preprocess_trails(features):
    processed = []
    for feat in features:
        props = feat.get("attributes", {})
        geom = feat.get("geometry", {})
        paths = geom.get("paths", [])
        if not paths:
            continue
        coords = [(lat, lon) for lon, lat in paths[0] if lon and lat]
        if len(coords) < 2:
            continue
        processed.append({
            'name': props.get('bezeichnung', 'Unnamed Trail'),  # Corrected attribute name
            'geometry': coords,
            'description': props.get('bemerkung', '') or props.get('kategorie', 'No description'),  # Corrected name
            'length': float(props.get('laenge', 0)) / 1000 if props.get('laenge') else 0.0,  # Corrected name
            'elevation': float(props.get('max_hoehe', 0)) if props.get('max_hoehe') else 0.0,  # Corrected name
            'category': props.get('kategorie', '')
        })
    return processed

def draw_trails(map_obj, trails, selected_name=None):
    cluster = MarkerCluster().add_to(map_obj)
    for trail in trails:
        is_selected = trail['name'] == selected_name
        if is_selected:
            folium.PolyLine(
                trail['geometry'],
                color='#ff0000',
                weight=4,
                opacity=0.95,
                tooltip=f"<b>{trail['name']}</b>",
                popup=f"Length: {trail['length']:.1f} km<br>Elevation: {trail['elevation']:.0f} m"
            ).add_to(map_obj)
        if trail['geometry']:
            folium.Marker(
                trail['geometry'][0],
                popup=f"<b>{trail['name']}</b><br>Start Point",
                icon=folium.Icon(color='red' if is_selected else 'blue', icon='flag')
            ).add_to(cluster)

def main():
    st.session_state.setdefault('selected_trail', None)
    st.session_state.setdefault('map_center', [DEFAULT_LAT, DEFAULT_LON])
    st.session_state.setdefault('map_zoom', 8)

    st.title("🇨🇭 Swiss Hiking Trail Finder (swisstopo, tiled)")
    st.markdown("Discover official hiking paths across Switzerland!")

    with st.sidebar:
        st.header("🔍 Search Filters")
        max_dist = st.slider("Max Distance from You (km)", 1, 100, 50)
        max_length = st.slider("Max Trail Length (km)", 0, 40, 40)
        max_alt = st.slider("Max Elevation (m)", 0, 3000, 2500)
        st.markdown("**Tiling Step (degrees)**")
        tile_step = st.slider("Tile size (smaller = slower, more complete)", 0.1, 1.0, 1.0, 0.1)
        try:
            g = geocoder.ip('me')
            if g.latlng:
                user_lat, user_lon = g.latlng
                st.session_state.user_loc = (user_lat, user_lon)
            else:
                raise AttributeError
        except:
            st.warning("Using Switzerland center as your location")
            st.session_state.user_loc = (DEFAULT_LAT, DEFAULT_LON)

    with st.spinner("Loading official Swiss hiking trails..."):
        raw_trails = get_all_hikes_tiled(SWISS_BOUNDS, tile_step)
    all_trails = preprocess_trails(raw_trails)
    if not all_trails:
        st.error("No trail data loaded - check API connection or try again later.")
        return

    filtered_trails = [
        t for t in all_trails
        if (calculate_min_distance(t['geometry'], st.session_state.user_loc) <= max_dist and
            (max_length == 0 or t['length'] == 0.0 or t['length'] <= max_length) and
            (max_alt == 0 or t['elevation'] == 0.0 or t['elevation'] <= max_alt))
    ]

    if filtered_trails and st.session_state.selected_trail not in [t['name'] for t in filtered_trails]:
        st.session_state.selected_trail = filtered_trails[0]['name']

    map_center = st.session_state.get('map_center', [DEFAULT_LAT, DEFAULT_LON])
    map_zoom = st.session_state.get('map_zoom', 8)
    m = folium.Map(location=map_center, zoom_start=map_zoom)
    folium.Marker(
        st.session_state.user_loc,
        popup="Your Location",
        icon=folium.Icon(color='green', icon='user')
    ).add_to(m)
    draw_trails(m, filtered_trails, st.session_state.selected_trail)

    map_data = st_folium(
        m,
        height=500,
        width=900,
        key="main_map",
        returned_objects=["last_clicked", "bounds", "zoom"]
    )

    if map_data.get('zoom'):
        st.session_state.map_zoom = map_data['zoom']

    if map_data.get('bounds'):
        bounds = map_data['bounds']
        if all(k in bounds for k in ('north', 'south', 'east', 'west')):
            st.session_state.map_center = [
                (bounds['north'] + bounds['south']) / 2,
                (bounds['east'] + bounds['west']) / 2
            ]

    st.subheader("📜 Trail Listings")
    if not filtered_trails:
        st.warning("No trails match your filters")
    else:
        trail_names = [t['name'] for t in filtered_trails]
        selected = st.selectbox(
            "Select a trail for details",
            trail_names,
            index=trail_names.index(st.session_state.selected_trail) if st.session_state.selected_trail in trail_names else 0,
            key="trail_selector"
        )
        st.session_state.selected_trail = selected
        selected_trail = next(t for t in filtered_trails if t['name'] == selected)
        with st.expander(f"🗺️ {selected} Details", expanded=True):
            cols = st.columns(4)
            length_str = f"{selected_trail['length']:.1f} km" if selected_trail['length'] > 0 else "-- km"
            elev_str = f"{selected_trail['elevation']:.0f} m" if selected_trail['elevation'] > 0 else "-- m"
            dist_str = f"{calculate_min_distance(selected_trail['geometry'], st.session_state.user_loc):.1f} km"
            category_str = selected_trail.get('category', '--')
            cols[0].metric("Length", length_str)
            cols[1].metric("Max Elevation", elev_str)
            cols[2].metric("Distance from You", dist_str)
            cols[3].metric("Category", category_str)
            st.markdown(f"**Description:** {selected_trail['description']}")

if __name__ == "__main__":
    main()
