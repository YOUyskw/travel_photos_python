from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="test")

def reverse_geocoding(latitude, longitude):
    location = geolocator.reverse(f"{latitude}, {longitude}")
    return location.address

def get_location(latitude, longitude):
    address = reverse_geocoding(latitude, longitude)
    location = address.split(",")[0]
    return location
