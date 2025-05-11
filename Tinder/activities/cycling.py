import math
from geopy.distance import geodesic

# Note: Removed openrouteservice usage; using geopy for distance calculations.
def get_cycling_route(start_lat, start_lon, end_lat, end_lon):
    """
    Returns a simulated cycling route from start to end with path coordinates,
    total distance (meters), estimated duration (seconds), ascent, and descent.
    """
    try:
        # Calculate distance between start and end points
        dist_m = geodesic((start_lat, start_lon), (end_lat, end_lon)).meters
        # Generate a simple path (straight line with slight curve)
        steps = 10
        lat_step = (end_lat - start_lat) / steps
        lon_step = (end_lon - start_lon) / steps
        path = []
        for i in range(steps + 1):
            lat_i = start_lat + lat_step * i
            lon_i = start_lon + lon_step * i
            # Smaller offset for cycling path curve
            offset = 0.0005 * math.sin(i / steps * math.pi)
            path.append([lat_i + offset, lon_i])
        # Estimate duration assuming ~15 km/hour cycling speed
        dist_km = dist_m / 1000.0
        duration_sec = int((dist_km / 15.0) * 3600)
        # Simulate elevation gain/loss (e.g., ~20 m up and down per km)
        ascent = int(20 * dist_km)
        descent = int(20 * dist_km)
        return {
            "path": path,
            "distance": dist_m,
            "duration": duration_sec,
            "ascent": ascent,
            "descent": descent
        }
    except Exception as e:
        print(f"Error generating cycling route: {e}")
        return {"path": [], "distance": 0, "duration": 0, "ascent": 0, "descent": 0}
