import geocoder

def get_location():
    """
    Get current location using IP-based geolocation.
    Returns (latitude, longitude, google_maps_link)
    """
    try:
        # Get approximate location using public IP
        g = geocoder.ip("me")
        
        if g.ok and g.latlng:
            lat, lon = g.latlng
            map_link = f"https://www.google.com/maps?q={lat},{lon}"
            print(f"📍 Location detected: {lat}, {lon}")
            return lat, lon, map_link
        else:
            print("⚠️ Could not determine location. Check your internet connection.")
            return None, None, None

    except Exception as e:
        print(f"❌ Error getting location: {e}")
        return None, None, None
