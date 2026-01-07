import requests
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class LocationService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.nominatim_url = "https://nominatim.openstreetmap.org/search"
        
    def search_location(self, query: str) -> List[Dict]:
        """
        Search locations using OpenStreetMap Nominatim API
        """
        try:
            # Format parameters for Nominatim
            params = {
                'q': query,
                'format': 'json',
                'limit': 5,
                'accept-language': 'tr',
                'addressdetails': 1
            }
            
            # Add headers to respect usage policy
            headers = {
                'User-Agent': 'AstroAIPredictor/1.0',
                'Accept-Language': 'tr'
            }
            
            response = requests.get(
                self.nominatim_url,
                params=params,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                results = response.json()
                formatted_results = []
                
                for location in results:
                    address = location.get('address', {})
                    formatted_results.append({
                        'display_name': location.get('display_name', ''),
                        'latitude': float(location.get('lat', 0)),
                        'longitude': float(location.get('lon', 0)),
                        'type': location.get('type', ''),
                        'importance': float(location.get('importance', 0)),
                        'components': {
                            'city': address.get('city') or address.get('town') or address.get('village'),
                            'state': address.get('state'),
                            'country': address.get('country')
                        }
                    })
                
                return formatted_results
            else:
                logger.error(f"Location search failed with status code: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error in location search: {str(e)}")
            return []
