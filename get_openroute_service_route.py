import streamlit as st
import requests
import polyline

def get_openroute_service_route(start_coords, end_coords, profile='foot-hiking', alternative_routes=False):
    """
    Get a route from OpenRouteService API with improved error handling and validation
    
    Parameters:
    - start_coords: tuple of (latitude, longitude)
    - end_coords: tuple of (latitude, longitude)
    - profile: routing profile to use ('foot-hiking', 'cycling-regular', 'cycling-mountain', 'cycling-road')
    - alternative_routes: whether to request alternative routes 
    
    Returns:
    - Dictionary with route details or None if an error occurs
    """
    base_url = "https://api.openrouteservice.org/v2/directions/"
    
    # Debug information
    st.debug(f"Input coordinates: start_coords={start_coords}, end_coords={end_coords}")
    
    try:
        # IMPORTANT: Validate and explicitly convert coordinates to float
        if isinstance(start_coords, (tuple, list)) and len(start_coords) >= 2:
            # Expect (latitude, longitude) from the caller
            start_lat = float(start_coords[0]) 
            start_lon = float(start_coords[1])
        else:
            st.error(f"Invalid start coordinates: {start_coords}")
            return None
            
        if isinstance(end_coords, (tuple, list)) and len(end_coords) >= 2:
            # Expect (latitude, longitude) from the caller
            end_lat = float(end_coords[0])
            end_lon = float(end_coords[1])
        else:
            st.error(f"Invalid end coordinates: {end_coords}")
            return None
        
        # Check for valid coordinate values
        if not (-90 <= start_lat <= 90 and -180 <= start_lon <= 180 and
                -90 <= end_lat <= 90 and -180 <= end_lon <= 180):
            st.error(f"Invalid coordinate values: start=({start_lat}, {start_lon}), end=({end_lat}, {end_lon})")
            return None
            
        # OpenRouteService expects coordinates in [longitude, latitude] order
        url = f"{base_url}{profile}"
        
        # Get API key from session state or environment for better flexibility
        api_key = st.session_state.get('OPENROUTE_API_KEY', None)
        
        # Import only if needed (fallback)
        if not api_key:
            try:
                from key import OPENROUTE_API_KEY
                api_key = OPENROUTE_API_KEY
            except ImportError:
                st.error("OpenRouteService API key not found. Please set OPENROUTE_API_KEY in key.py or session state.")
                return None
                
        headers = {
            'Authorization': api_key,
            'Content-Type': 'application/json'
        }
        
        # CRITICAL FIX: OpenRouteService expects [longitude, latitude] order
        # We received [latitude, longitude] so we need to swap here
        body = {
            "coordinates": [
                [start_lon, start_lat],  # Swapped order for API
                [end_lon, end_lat]       # Swapped order for API
            ],
            "elevation": "true",
            # Add this to get more detailed routes
            "extra_info": ["waytype", "steepness"],
            "geometry_simplify": False,  # Don't simplify geometry to get all road points
        }
        
        # Add option for alternative routes
        if alternative_routes:
            body["alternative_routes"] = {
                "target_count": 3,
                "weight_factor": 1.6
            }
        
        st.debug(f"Sending request to OpenRouteService: {url}")
        st.debug(f"Request body: {body}")
        
        response = requests.post(url, json=body, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            st.debug(f"Response received successfully")
            
            if 'routes' in data and len(data['routes']) > 0:
                route = data['routes'][0]
                
                # Check if 'geometry' exists and is not empty
                if 'geometry' not in route or not route['geometry']:
                    st.error("No geometry found in route data")
                    st.debug(f"Route data without geometry: {route}")
                    return None
                
                geometry = route['geometry']
                st.debug(f"Geometry type: {type(geometry)}")
                
                try:
                    # FIX for "string index out of range" - handle different geometry formats
                    coords = []
                    
                    # Check if the geometry is already a list of coordinates
                    if isinstance(geometry, list):
                        st.debug("Geometry is already a list of coordinates")
                        # Convert from [lon, lat] to [lat, lon] for Folium
                        coords = [(coord[1], coord[0]) for coord in geometry]
                    else:
                        # Try to decode the polyline
                        st.debug("Attempting to decode polyline geometry")
                        try:
                            # polyline.decode with geojson=True returns [lon, lat] format
                            coords_raw = polyline.decode(geometry, geojson=True)
                            # Convert from [lon, lat] to [lat, lon] for Folium
                            coords = [(coord[1], coord[0]) for coord in coords_raw]
                        except Exception as e:
                            st.error(f"Error decoding polyline: {str(e)}")
                            
                            # Fallback method - try to extract coordinates from GeoJSON if polyline decoding fails
                            if 'geometry' in route and route['geometry'] and 'coordinates' in route['geometry']:
                                st.debug("Falling back to GeoJSON coordinates")
                                geojson_coords = route['geometry']['coordinates']
                                coords = [(coord[1], coord[0]) for coord in geojson_coords]
                            
                    # Check if we have valid coordinates
                    if not coords:
                        st.error("Failed to extract coordinates from route")
                        # Create a fallback simple direct route between start and end
                        coords = [
                            (start_lat, start_lon),  # Start point
                            (end_lat, end_lon)       # End point
                        ]
                        st.warning("Using fallback direct route between start and end points")
                    
                    # Extract distance and duration
                    distance_km = route['summary']['distance'] / 1000 if 'summary' in route and 'distance' in route['summary'] else 0
                    duration_min = route['summary']['duration'] / 60 if 'summary' in route and 'duration' in route['summary'] else 0
                    
                    # Extract elevation data if available
                    elevation_gain = 0
                    if 'summary' in route and 'ascent' in route['summary']:
                        elevation_gain = route['summary']['ascent']
                    
                    # Debug the coordinate transformation
                    st.debug(f"Number of coordinates in route: {len(coords)}")
                    if coords:
                        st.debug(f"First coordinate: {coords[0]}")
                        st.debug(f"Last coordinate: {coords[-1]}")
                    
                    return {
                        'coordinates': coords,
                        'distance_km': distance_km,
                        'duration_min': duration_min,
                        'elevation_gain': elevation_gain
                    }
                except Exception as e:
                    st.error(f"Error processing route geometry: {str(e)}")
                    import traceback
                    st.debug(traceback.format_exc())
                    
                    # Return a simple direct route as fallback
                    coords = [
                        (start_lat, start_lon),  # Start point
                        (end_lat, end_lon)       # End point
                    ]
                    return {
                        'coordinates': coords, 
                        'distance_km': 0,
                        'duration_min': 0,
                        'elevation_gain': 0
                    }
            else:
                st.error("No routes found in the response")
                st.debug(f"API response data: {data}")
                return None
        else:
            error_msg = f"Error from OpenRouteService API: {response.status_code}"
            try:
                error_details = response.json()
                if 'error' in error_details and 'message' in error_details['error']:
                    error_msg += f" - {error_details['error']['message']}"
            except:
                error_msg += f" - {response.text}"
            
            st.error(error_msg)
            st.debug(f"Full response: {response.text}")
            return None
            
    except Exception as e:
        st.error(f"Exception when calling OpenRouteService API: {str(e)}")
        # For debugging - show more details about the exception
        import traceback
        st.debug(traceback.format_exc())
        
        # Return a simple direct route as fallback
        coords = [
            (start_lat, start_lon),  # Start point
            (end_lat, end_lon)       # End point
        ]
        return {
            'coordinates': coords, 
            'distance_km': 0,
            'duration_min': 0,
            'elevation_gain': 0
        }