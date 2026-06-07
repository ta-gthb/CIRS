import requests

def reverse_geocode(lat, lng):
    """
    Uses OpenStreetMap Nominatim API to get city/state from coordinates.
    Returns (city, state) or (None, None) on failure.
    """
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lng}&zoom=10&addressdetails=1"
        headers = {
            'User-Agent': 'CivicIssueReportingSystem/1.0'
        }
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            address = data.get('address', {})
            # Nominatim uses different keys for city: city, town, village, county, district
            city = address.get('city') or address.get('town') or address.get('village') or \
                   address.get('county') or address.get('district') or address.get('suburb')
            state = address.get('state')
            return city, state
    except Exception as e:
        print(f"Geocoding error: {e}")
    return None, None
