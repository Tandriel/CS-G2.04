import requests

YELP_API_KEY = "3CDquv2YIfVJBzNuoyau9lsDbqv21Zohj2ewjXvFlJDovEAGaiJWihHDxImRJatHXFA--wY1vVGuvLUX2bMyS-ipwsXjyDII3afybeUrgoisA1GbR8o0oOSB5bIYaHYx"

HEADERS = {
    "Authorization": f"Bearer {YELP_API_KEY}"
}

def geocode_location(location_str):
    """Geocode a location name to latitude and longitude using OpenStreetMap."""
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": location_str, "format": "json", "limit": 1, "countrycodes": "ch"}
    headers = {"User-Agent": "TinderActivitiesApp/1.0"}
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        data = response.json()
        if data:
            lat = float(data[0]["lat"]); lon = float(data[0]["lon"])
            return lat, lon
    except Exception:
        return None

def fetch_yelp_activities(lat, lon, term="activities", radius_m=5000, limit=20):
    """Fetch activities from the Yelp API based on a search term and location."""
    url = "https://api.yelp.com/v3/businesses/search"
    params = {
        "latitude": lat, "longitude": lon,
        "term": term, "radius": radius_m, "limit": limit
    }
    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=10)
        data = response.json()
        results = []
        for biz in data.get("businesses", []):
            results.append({
                "name": biz.get("name"),
                "lat": biz["coordinates"]["latitude"],
                "lon": biz["coordinates"]["longitude"],
                "rating": biz.get("rating", "N/A"),
                "category": biz.get("categories")[0]["title"] if biz.get("categories") else "Activity",
                "address": ", ".join(biz["location"].get("display_address", [])),
                "image_url": biz.get("image_url"),
                "photos": biz.get("photos", []),
                "url": biz.get("url"),
                "price": biz.get("price", "")
            })
        return results
    except Exception as e:
        print("Yelp API error:", e)
        return []

import requests

EVENTFROG_API_KEY = "YOUR_EVENTFROG_API_KEY"

def fetch_eventfrog_events(lat, lon, term="events", radius_m=5000):
    """
    Fetch events (concerts/parties) from Eventfrog's API based on location.
    Returns a list of events with name, location, date, and other details.
    """
    base_url = "https://api.eventfrog.ch/api/events"
    params = {
        "latitude": lat,
        "longitude": lon,
        "distance": radius_m,
        "keyword": term
    }
    headers = {
        "Authorization": f"Bearer {EVENTFROG_API_KEY}"
    }

    events = []
    try:
        response = requests.get(base_url, headers=headers, params=params, timeout=10)
        data = response.json()
        for ev in data.get("events", []):
            events.append({
                "name": ev.get("title", "Untitled Event"),
                "lat": ev.get("location", {}).get("latitude"),
                "lon": ev.get("location", {}).get("longitude"),
                "category": term.capitalize(),
                "address": f"{ev.get('location', {}).get('name', '')}, {ev.get('location', {}).get('city', '')}",
                "image_url": ev.get("imageUrl", ""),
                "url": ev.get("url", ""),
                "price": ev.get("ticketPrice", ""),
                "date": ev.get("startDate", "")
            })
    except Exception as e:
        print("Eventfrog API error:", e)
    return events
