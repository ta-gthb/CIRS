import requests

def reverse_geocode(lat, lng):
    """
    Uses OpenStreetMap Nominatim API to get city/state/address from coordinates.
    Returns (district, state, full_address) or (None, None, None) on failure.
    """
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lng}&zoom=18&addressdetails=1"
        headers = {
            'User-Agent': 'CivicIssueReportingSystem/1.0'
        }
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            address = data.get('address', {})
            
            # In India, administrative routing is usually district-based.
            # Nominatim 'state_district' or 'county' usually maps to the Indian District.
            district = address.get('state_district') or address.get('county')
            
            # Local area (City/Town/Village)
            city_town = address.get('city') or address.get('town') or address.get('village') or address.get('suburb')
            
            # For routing purposes in this app, 'city' should be the District if available.
            # If not, fallback to the local town name.
            final_city = district or city_town
            
            state = address.get('state')
            full_address = data.get('display_name')
            
            return final_city, state, full_address
    except Exception as e:
        print(f"Geocoding error: {e}")
    return None, None, None
