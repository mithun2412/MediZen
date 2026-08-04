import requests
import math
from typing import List, Dict, Any, Optional
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import os

# Google Maps API Key (store in environment variables)
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")

# OpenStreetMap Nominatim geocoder
geolocator = Nominatim(user_agent="medizen_ai")

def _find_nearby_facilities(
    latitude: float,
    longitude: float,
    symptoms: str = "",
    radius: int = 10000  # meters
) -> List[Dict[str, Any]]:
    """
    Get nearby hospitals using OpenStreetMap Overpass API and Google Maps.
    """
    try:
        hospitals = []
        
        # Method 1: OpenStreetMap Overpass API (Free)
        overpass_hospitals = get_hospitals_from_overpass(latitude, longitude, radius)
        hospitals.extend(overpass_hospitals)
        
        # Method 2: Google Maps Places API (if API key is available)
        if GOOGLE_MAPS_API_KEY:
            google_hospitals = get_hospitals_from_google_maps(latitude, longitude, radius)
            # Merge and deduplicate
            hospitals = merge_hospital_lists(hospitals, google_hospitals)
        
        # Add Google Maps search links
        for hospital in hospitals:
            hospital['google_maps_link'] = create_google_maps_link(
                hospital.get('name', ''),
                hospital.get('latitude', latitude),
                hospital.get('longitude', longitude)
            )
            hospital['directions_link'] = create_google_directions_link(
                latitude,
                longitude,
                hospital.get('latitude', latitude),
                hospital.get('longitude', longitude)
            )
        
        # Sort by distance
        for hospital in hospitals:
            hospital['distance'] = calculate_distance(
                latitude, longitude,
                hospital.get('latitude', 0),
                hospital.get('longitude', 0)
            )
        
        hospitals.sort(key=lambda x: x.get('distance', float('inf')))
        
        return hospitals[:10]  # Return top 10
        
    except Exception as e:
        print(f"Hospital Search Error: {e}")
        return get_fallback_hospitals(latitude, longitude)

def get_hospitals_from_overpass(latitude: float, longitude: float, radius: int) -> List[Dict[str, Any]]:
    """
    Get hospitals from OpenStreetMap Overpass API.
    """
    try:
        # Overpass API query
        query = f"""
        [out:json];
        (
          node["amenity"="hospital"](around:{radius},{latitude},{longitude});
          node["amenity"="clinic"](around:{radius},{latitude},{longitude});
          way["amenity"="hospital"](around:{radius},{latitude},{longitude});
          way["amenity"="clinic"](around:{radius},{latitude},{longitude});
        );
        out body;
        """
        
        response = requests.post(
            "https://overpass-api.de/api/interpreter",
            data={"data": query},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            hospitals = []
            
            for element in data.get('elements', []):
                tags = element.get('tags', {})
                lat = element.get('lat')
                lon = element.get('lon')
                
                if lat and lon:
                    hospital = {
                        'name': tags.get('name', 'Medical Facility'),
                        'latitude': lat,
                        'longitude': lon,
                        'address': tags.get('addr:street', ''),
                        'phone': tags.get('phone', ''),
                        'website': tags.get('website', ''),
                        'source': 'OpenStreetMap'
                    }
                    hospitals.append(hospital)
            
            return hospitals
        
        return []
        
    except Exception as e:
        print(f"Overpass API Error: {e}")
        return []

def get_hospitals_from_google_maps(latitude: float, longitude: float, radius: int) -> List[Dict[str, Any]]:
    """
    Get hospitals from Google Maps Places API.
    """
    try:
        if not GOOGLE_MAPS_API_KEY:
            return []
        
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            "location": f"{latitude},{longitude}",
            "radius": radius,
            "type": "hospital",
            "key": GOOGLE_MAPS_API_KEY
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            hospitals = []
            
            for place in data.get('results', []):
                location = place.get('geometry', {}).get('location', {})
                hospital = {
                    'name': place.get('name', 'Medical Facility'),
                    'latitude': location.get('lat', latitude),
                    'longitude': location.get('lng', longitude),
                    'address': place.get('vicinity', ''),
                    'rating': place.get('rating', 0),
                    'user_ratings_total': place.get('user_ratings_total', 0),
                    'place_id': place.get('place_id', ''),
                    'source': 'Google Maps'
                }
                hospitals.append(hospital)
            
            return hospitals
        
        return []
        
    except Exception as e:
        print(f"Google Maps API Error: {e}")
        return []

def merge_hospital_lists(list1: List[Dict], list2: List[Dict]) -> List[Dict]:
    """
    Merge two hospital lists and remove duplicates.
    """
    merged = []
    seen_names = set()
    
    for hospital in list1 + list2:
        name = hospital.get('name', '').lower()
        if name not in seen_names:
            seen_names.add(name)
            merged.append(hospital)
    
    return merged

def create_google_maps_link(name: str, latitude: float, longitude: float) -> str:
    """
    Create a Google Maps link for a hospital.
    """
    return f"https://www.google.com/maps/place/{name.replace(' ', '+')}/@{latitude},{longitude},15z"

def create_google_directions_link(
    source_lat: float,
    source_lon: float,
    dest_lat: float,
    dest_lon: float
) -> str:
    """
    Create a Google Maps directions link.
    """
    return f"https://www.google.com/maps/dir/{source_lat},{source_lon}/{dest_lat},{dest_lon}/"

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two coordinates in kilometers.
    """
    try:
        return geodesic((lat1, lon1), (lat2, lon2)).kilometers
    except:
        return 9999

def get_fallback_hospitals(latitude: float, longitude: float) -> List[Dict[str, Any]]:
    """
    Provide fallback hospital search using geocoding.
    """
    try:
        # Get location name
        location = geolocator.reverse(f"{latitude}, {longitude}")
        
        # Create search link for user to find hospitals themselves
        return [{
            'name': 'Search Nearby Hospitals',
            'latitude': latitude,
            'longitude': longitude,
            'google_maps_link': f"https://www.google.com/maps/search/hospitals/@{latitude},{longitude},15z",
            'directions_link': f"https://www.google.com/maps/dir/{latitude},{longitude}/hospitals/",
            'address': location.address if location else '',
            'distance': 0,
            'source': 'Fallback'
        }]
        
    except Exception as e:
        print(f"Fallback hospital search error: {e}")
        return []

def get_hospital_details(place_id: str) -> Optional[Dict[str, Any]]:
    """
    Get detailed information about a hospital using Place ID.
    """
    try:
        if not GOOGLE_MAPS_API_KEY:
            return None
        
        url = "https://maps.googleapis.com/maps/api/place/details/json"
        params = {
            "place_id": place_id,
            "key": GOOGLE_MAPS_API_KEY,
            "fields": "name,formatted_address,formatted_phone_number,website,opening_hours,rating,reviews"
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            result = data.get('result', {})
            
            return {
                'name': result.get('name', ''),
                'address': result.get('formatted_address', ''),
                'phone': result.get('formatted_phone_number', ''),
                'website': result.get('website', ''),
                'rating': result.get('rating', 0),
                'opening_hours': result.get('opening_hours', {}).get('weekday_text', []),
                'reviews': result.get('reviews', [])
            }
        
        return None
        
    except Exception as e:
        print(f"Hospital details error: {e}")
        return None

# Cache for hospital data
_hospital_cache = {}

def get_hospitals_with_cache(
    latitude: float,
    longitude: float,
    radius: int = 10000,
    use_cache: bool = True
) -> List[Dict[str, Any]]:
    """
    Get hospitals with caching.
    """
    cache_key = f"{latitude:.4f}_{longitude:.4f}_{radius}"
    
    if use_cache and cache_key in _hospital_cache:
        return _hospital_cache[cache_key]
    
    hospitals = get_nearby_hospitals(latitude, longitude, radius)
    _hospital_cache[cache_key] = hospitals
    
    return hospitals





def get_nearby_hospitals(
    latitude: float,
    longitude: float,
    symptoms: str = "",
    radius: int = 10000,
    specialty: str | None = None,
) -> List[Dict[str, Any]]:
    """Find nearby facilities and attach the symptom-appropriate care specialty."""
    specialty = specialty or get_recommended_specialty(symptoms)
    hospitals = _find_nearby_facilities(latitude, longitude, symptoms, radius)
    specialty_search_link = create_specialty_maps_search_link(latitude, longitude, specialty)

    for hospital in hospitals:
        hospital["recommended_specialty"] = specialty
        hospital["specialty_search_link"] = specialty_search_link

    return hospitals


def get_recommended_specialty(symptoms: str) -> str:
    """Legacy helper; specialty selection is performed by the LLM triage service."""
    raise RuntimeError("Care specialty must be selected by the LLM triage service.")


def create_specialty_maps_search_link(latitude: float, longitude: float, specialty: str) -> str:
    query = f"{specialty} hospital"
    return f"https://www.google.com/maps/search/?api=1&query={query.replace(' ', '+')}&query_place_id=&center={latitude},{longitude}"
