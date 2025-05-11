import math
from geopy.distance import geodesic

# Note: Removed dependency on openrouteservice – using geopy for distance calculations.
def get_hiking_route(start_lat, start_lon, end_lat, end_lon):
    """
    Returns a simulated hiking route from start to end with path coordinates,
    total distance (meters), estimated duration (seconds), ascent, and descent.
    """
    try:
        # Calculate great-circle distance between start and end:contentReference[oaicite:0]{index=0}
        dist_m = geodesic((start_lat, start_lon), (end_lat, end_lon)).meters
        # Generate a simple path with a slight curve (straight line approximation)
        steps = 10
        lat_step = (end_lat - start_lat) / steps
        lon_step = (end_lon - start_lon) / steps
        path = []
        for i in range(steps + 1):
            # Linear interpolation between start and end
            lat_i = start_lat + lat_step * i
            lon_i = start_lon + lon_step * i
            # Add a small sinusoidal offset to latitude to simulate a curved trail
            offset = 0.001 * math.sin(i / steps * math.pi)
            path.append([lat_i + offset, lon_i])
        # Estimate duration assuming ~5 km/hour pace for hiking
        dist_km = dist_m / 1000.0
        duration_sec = int((dist_km / 5.0) * 3600)  # convert hours to seconds
        # Simulate elevation gain/loss (e.g., ~30 m up and down per km)
        ascent = int(30 * dist_km)
        descent = int(30 * dist_km)
        return {
            "path": path,
            "distance": dist_m,
            "duration": duration_sec,
            "ascent": ascent,
            "descent": descent
        }
    except Exception as e:
        print(f"Error generating hiking route: {e}")
        return {"path": [], "distance": 0, "duration": 0, "ascent": 0, "descent": 0}
