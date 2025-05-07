import requests

YELP_API_KEY = "3CDquv2YIfVJBzNuoyau9lsDbqv21Zohj2ewjXvFlJDovEAGaiJWihHDxImRJatHXFA--wY1vVGuvLUX2bMyS-ipwsXjyDII3afybeUrgoisA1GbR8o0oOSB5bIYaHYx"

HEADERS = {
    "Authorization": f"Bearer {YELP_API_KEY}"
}

def geocode_location(location_str):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": location_str,
        "format": "json",
        "limit": 1,
        "countrycodes": "ch"
    }
    headers = {"User-Agent": "TinderActivitiesApp/1.0"}
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        data = response.json()
        if data:
            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])
            return lat, lon
    except:
        return None

def fetch_yelp_activities(lat, lon, term="activities", radius_m=5000, limit=20):
    url = "https://api.yelp.com/v3/businesses/search"
    params = {
        "latitude": lat,
        "longitude": lon,
        "term": term,
        "radius": radius_m,
        "limit": limit
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
                "rating": biz.get("rating"),
                "category": biz["categories"][0]["title"] if biz.get("categories") else "Activity",
                "address": ", ".join(biz["location"].get("display_address", [])),
                "image_url": biz.get("image_url"),
                "url": biz.get("url"),
                "price": biz.get("price", "")
            })
        return results
    except Exception as e:
        print("Yelp API error:", e)
        return []
