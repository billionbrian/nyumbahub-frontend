import logging
import urllib.parse
import urllib.request
import json
from decimal import Decimal
from abc import ABC, abstractmethod
from django.conf import settings

logger = logging.getLogger(__name__)


class BaseGeocodingProvider(ABC):
    """
    Abstract interface for reverse geocoding providers.
    """
    @abstractmethod
    def reverse_geocode(self, latitude, longitude) -> str:
        pass


class NominatimGeocodingProvider(BaseGeocodingProvider):
    """
    OpenStreetMap Nominatim reverse geocoding provider.
    Extracts a clean, non-verbose human-readable location string.
    """
    def __init__(self, user_agent=None, base_url=None, timeout=None):
        self.user_agent = user_agent or getattr(
            settings, 'GEOCODING_NOMINATIM_USER_AGENT', 'TapIn-StudentHousing/1.0 (admin@tapin.test)'
        )
        self.base_url = base_url or getattr(
            settings, 'GEOCODING_NOMINATIM_URL', 'https://nominatim.openstreetmap.org/reverse'
        )
        self.timeout = timeout or getattr(settings, 'GEOCODING_TIMEOUT_SECONDS', 5)

    def reverse_geocode(self, latitude, longitude) -> str:
        try:
            lat = float(latitude)
            lon = float(longitude)
        except (ValueError, TypeError):
            logger.warning(f"Invalid coordinate format passed to reverse_geocode: {latitude}, {longitude}")
            return f"Location ({latitude}, {longitude})"

        params = urllib.parse.urlencode({
            'lat': lat,
            'lon': lon,
            'format': 'jsonv2',
            'addressdetails': 1,
            'zoom': 18
        })
        url = f"{self.base_url}?{params}"
        headers = {
            'User-Agent': self.user_agent,
            'Accept': 'application/json'
        }

        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode('utf-8'))
                    return self._format_address(data, lat, lon)
                else:
                    logger.warning(f"Nominatim returned HTTP {resp.status} for ({lat}, {lon})")
        except Exception as e:
            logger.warning(f"Geocoding request failed for ({lat}, {lon}): {str(e)}")

        # Fallback if network/API is unreachable
        return f"Location ({lat:.4f}, {lon:.4f})"

    def _format_address(self, data: dict, lat: float, lon: float) -> str:
        if not data:
            return f"Location ({lat:.4f}, {lon:.4f})"

        address = data.get('address', {})
        if not address:
            # Fall back to display_name or coordinates
            display_name = data.get('display_name', '')
            if display_name:
                parts = [p.strip() for p in display_name.split(',') if p.strip()]
                return ", ".join(parts[:3])
            return f"Location ({lat:.4f}, {lon:.4f})"

        parts = []

        # 1. Local entity / street level
        local_keys = [
            'amenity', 'building', 'neighbourhood', 'suburb', 'quarter', 
            'residential', 'village', 'hamlet', 'road', 'pedestrian'
        ]
        for key in local_keys:
            val = address.get(key)
            if val and val not in parts:
                parts.append(val)
                break

        # 2. City / Town / Municipality
        city_keys = ['city', 'town', 'municipality', 'county_district', 'district']
        for key in city_keys:
            val = address.get(key)
            if val and val not in parts:
                parts.append(val)
                break

        # 3. County / State / Region
        county_keys = ['county', 'state_district', 'state']
        for key in county_keys:
            val = address.get(key)
            if val and val not in parts:
                # Avoid redundancy like "Kilifi" followed by "Kilifi County"
                if not any(val.lower().startswith(p.lower()) or p.lower().startswith(val.lower()) for p in parts):
                    parts.append(val)
                break

        # 4. Country
        country = address.get('country')
        if country and country not in parts:
            parts.append(country)

        if parts:
            return ", ".join(parts)

        # Fallback to truncated display_name if structured parse was empty
        display_name = data.get('display_name', '')
        if display_name:
            raw_parts = [p.strip() for p in display_name.split(',') if p.strip()]
            return ", ".join(raw_parts[:3])

        return f"Location ({lat:.4f}, {lon:.4f})"


class MockGeocodingProvider(BaseGeocodingProvider):
    """
    In-memory mock provider for testing and offline environments.
    """
    def __init__(self, default_label="Kilifi, Kenya"):
        self.default_label = default_label

    def reverse_geocode(self, latitude, longitude) -> str:
        return self.default_label


def get_geocoding_provider() -> BaseGeocodingProvider:
    """
    Factory resolving provider from settings.
    """
    provider_name = getattr(settings, 'GEOCODING_PROVIDER', 'nominatim').lower()
    if provider_name == 'nominatim':
        return NominatimGeocodingProvider()
    elif provider_name == 'mock':
        return MockGeocodingProvider()
    else:
        logger.warning(f"Unknown geocoding provider '{provider_name}', defaulting to Nominatim")
        return NominatimGeocodingProvider()


def reverse_geocode(latitude, longitude) -> str:
    """
    Public entry point for reverse geocoding coordinates to a human-readable location.
    """
    provider = get_geocoding_provider()
    return provider.reverse_geocode(latitude, longitude)
