"""
Flight Data Service

Provides flight information retrieval from:
1. AviationStack API (primary)
2. FlightAware AeroAPI (secondary)
3. Manual data entry fallback

Used to retrieve flight details for compensation claims.
"""

import requests
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional, List, Tuple
from abc import ABC, abstractmethod

from config import get_config
from compensation_calculator import (
    FlightDetails, Airport, get_airport, is_carrier_eu_based,
    EU_CARRIERS, AIRPORT_DATA
)


@dataclass
class FlightSearchResult:
    """Result from flight search."""
    flight_number: str
    airline_code: str
    airline_name: str
    departure_code: str
    departure_name: str
    arrival_code: str
    arrival_name: str
    scheduled_departure: datetime
    scheduled_arrival: datetime
    actual_departure: Optional[datetime]
    actual_arrival: Optional[datetime]
    status: str  # scheduled, active, landed, cancelled, diverted
    delay_minutes: Optional[int]


class FlightDataProvider(ABC):
    """Abstract base class for flight data providers."""

    @abstractmethod
    def search_flight(
        self,
        flight_number: str,
        date: datetime
    ) -> Optional[FlightSearchResult]:
        """Search for a flight by number and date."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this provider is available (API key configured)."""
        pass


class AviationStackProvider(FlightDataProvider):
    """AviationStack API provider."""

    BASE_URL = "http://api.aviationstack.com/v1"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def is_available(self) -> bool:
        return bool(self.api_key)

    def search_flight(
        self,
        flight_number: str,
        date: datetime
    ) -> Optional[FlightSearchResult]:
        """Search for flight using AviationStack API."""
        if not self.is_available():
            return None

        try:
            # Parse airline code and flight number
            airline_code = flight_number[:2].upper()
            flight_num = flight_number[2:].strip()

            params = {
                'access_key': self.api_key,
                'flight_iata': f"{airline_code}{flight_num}",
                'flight_date': date.strftime('%Y-%m-%d'),
            }

            response = requests.get(
                f"{self.BASE_URL}/flights",
                params=params,
                timeout=30
            )
            response.raise_for_status()

            data = response.json()

            if 'data' not in data or not data['data']:
                return None

            flight = data['data'][0]

            # Parse departure info
            dep = flight.get('departure', {})
            arr = flight.get('arrival', {})
            airline = flight.get('airline', {})

            # Parse datetime strings
            def parse_dt(dt_str: Optional[str]) -> Optional[datetime]:
                if not dt_str:
                    return None
                try:
                    # Handle various formats
                    for fmt in ['%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S']:
                        try:
                            return datetime.strptime(dt_str[:19], fmt[:fmt.rfind('%')+2] if '%z' in fmt else fmt)
                        except ValueError:
                            continue
                    return datetime.fromisoformat(dt_str.replace('Z', '+00:00').replace('+00:00', ''))
                except Exception:
                    return None

            return FlightSearchResult(
                flight_number=f"{airline_code}{flight_num}",
                airline_code=airline_code,
                airline_name=airline.get('name', 'Unknown'),
                departure_code=dep.get('iata', ''),
                departure_name=dep.get('airport', ''),
                arrival_code=arr.get('iata', ''),
                arrival_name=arr.get('airport', ''),
                scheduled_departure=parse_dt(dep.get('scheduled')),
                scheduled_arrival=parse_dt(arr.get('scheduled')),
                actual_departure=parse_dt(dep.get('actual')),
                actual_arrival=parse_dt(arr.get('actual')),
                status=flight.get('flight_status', 'unknown'),
                delay_minutes=arr.get('delay')
            )

        except requests.RequestException as e:
            print(f"AviationStack API error: {e}")
            return None
        except Exception as e:
            print(f"Error parsing AviationStack response: {e}")
            return None


class FlightAwareProvider(FlightDataProvider):
    """FlightAware AeroAPI provider."""

    BASE_URL = "https://aeroapi.flightaware.com/aeroapi"

    def __init__(self, api_key: str, username: str = None):
        self.api_key = api_key
        self.username = username

    def is_available(self) -> bool:
        return bool(self.api_key)

    def search_flight(
        self,
        flight_number: str,
        date: datetime
    ) -> Optional[FlightSearchResult]:
        """Search for flight using FlightAware AeroAPI."""
        if not self.is_available():
            return None

        try:
            airline_code = flight_number[:2].upper()
            flight_num = flight_number[2:].strip()

            headers = {
                'x-apikey': self.api_key,
                'Accept': 'application/json'
            }

            # Format dates for API
            start = date.strftime('%Y-%m-%dT00:00:00Z')
            end = (date + timedelta(days=1)).strftime('%Y-%m-%dT23:59:59Z')

            params = {
                'start': start,
                'end': end
            }

            response = requests.get(
                f"{self.BASE_URL}/flights/{airline_code}{flight_num}",
                headers=headers,
                params=params,
                timeout=30
            )
            response.raise_for_status()

            data = response.json()

            if 'flights' not in data or not data['flights']:
                return None

            flight = data['flights'][0]

            def parse_dt(dt_str: Optional[str]) -> Optional[datetime]:
                if not dt_str:
                    return None
                try:
                    return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
                except Exception:
                    return None

            return FlightSearchResult(
                flight_number=f"{airline_code}{flight_num}",
                airline_code=airline_code,
                airline_name=flight.get('operator', {}).get('name', 'Unknown'),
                departure_code=flight.get('origin', {}).get('code_iata', ''),
                departure_name=flight.get('origin', {}).get('name', ''),
                arrival_code=flight.get('destination', {}).get('code_iata', ''),
                arrival_name=flight.get('destination', {}).get('name', ''),
                scheduled_departure=parse_dt(flight.get('scheduled_out')),
                scheduled_arrival=parse_dt(flight.get('scheduled_in')),
                actual_departure=parse_dt(flight.get('actual_out')),
                actual_arrival=parse_dt(flight.get('actual_in')),
                status=flight.get('status', 'unknown'),
                delay_minutes=flight.get('arrival_delay')
            )

        except requests.RequestException as e:
            print(f"FlightAware API error: {e}")
            return None
        except Exception as e:
            print(f"Error parsing FlightAware response: {e}")
            return None


class FlightService:
    """
    Main flight data service that orchestrates multiple providers.

    Attempts to fetch data from available APIs, falls back to manual entry
    if no APIs are configured or all fail.
    """

    def __init__(self):
        config = get_config()
        self.providers: List[FlightDataProvider] = []

        # Initialize available providers
        if config.api.aviationstack_key:
            self.providers.append(
                AviationStackProvider(config.api.aviationstack_key)
            )

        if config.api.flightaware_key:
            self.providers.append(
                FlightAwareProvider(
                    config.api.flightaware_key,
                    config.api.flightaware_username
                )
            )

    def has_api_access(self) -> bool:
        """Check if any flight API is configured."""
        return any(p.is_available() for p in self.providers)

    def search_flight(
        self,
        flight_number: str,
        date: datetime
    ) -> Tuple[Optional[FlightSearchResult], str]:
        """
        Search for a flight across all available providers.

        Returns:
            Tuple of (result, source) where source indicates which provider
            returned the data, or "manual" if APIs failed.
        """
        # Normalize flight number
        flight_number = flight_number.upper().replace(' ', '').replace('-', '')

        for provider in self.providers:
            if provider.is_available():
                result = provider.search_flight(flight_number, date)
                if result:
                    source = provider.__class__.__name__.replace('Provider', '')
                    return result, source

        return None, "manual"

    def convert_to_flight_details(
        self,
        result: FlightSearchResult
    ) -> Optional[FlightDetails]:
        """Convert search result to FlightDetails for compensation calculation."""
        dep_airport = get_airport(result.departure_code)
        arr_airport = get_airport(result.arrival_code)

        # If airports not in our database, create basic entries
        if not dep_airport:
            dep_airport = Airport(
                code=result.departure_code,
                name=result.departure_name,
                city="Unknown",
                country="XX",
                latitude=0,
                longitude=0,
                is_eu=False
            )

        if not arr_airport:
            arr_airport = Airport(
                code=result.arrival_code,
                name=result.arrival_name,
                city="Unknown",
                country="XX",
                latitude=0,
                longitude=0,
                is_eu=False
            )

        if not result.scheduled_departure or not result.scheduled_arrival:
            return None

        return FlightDetails(
            flight_number=result.flight_number,
            airline_code=result.airline_code,
            airline_name=result.airline_name,
            departure_airport=dep_airport,
            arrival_airport=arr_airport,
            scheduled_departure=result.scheduled_departure,
            scheduled_arrival=result.scheduled_arrival,
            actual_departure=result.actual_departure,
            actual_arrival=result.actual_arrival,
            is_cancelled=result.status.lower() == 'cancelled',
            is_eu_carrier=is_carrier_eu_based(result.airline_code)
        )


def create_flight_details_manual(
    flight_number: str,
    airline_name: str,
    departure_code: str,
    arrival_code: str,
    scheduled_departure: datetime,
    scheduled_arrival: datetime,
    actual_departure: Optional[datetime] = None,
    actual_arrival: Optional[datetime] = None,
    is_cancelled: bool = False
) -> Optional[FlightDetails]:
    """
    Create FlightDetails from manual data entry.

    Used when API lookup fails or is not available.
    """
    dep_airport = get_airport(departure_code)
    arr_airport = get_airport(arrival_code)

    if not dep_airport or not arr_airport:
        return None

    airline_code = flight_number[:2].upper() if len(flight_number) >= 2 else "XX"

    return FlightDetails(
        flight_number=flight_number.upper(),
        airline_code=airline_code,
        airline_name=airline_name,
        departure_airport=dep_airport,
        arrival_airport=arr_airport,
        scheduled_departure=scheduled_departure,
        scheduled_arrival=scheduled_arrival,
        actual_departure=actual_departure,
        actual_arrival=actual_arrival,
        is_cancelled=is_cancelled,
        is_eu_carrier=is_carrier_eu_based(airline_code)
    )


def get_supported_airports() -> List[Tuple[str, str, str]]:
    """Get list of supported airports (code, name, country)."""
    airports = []
    for code, (name, city, country, _, _) in AIRPORT_DATA.items():
        airports.append((code, f"{name} ({city})", country))
    return sorted(airports, key=lambda x: x[0])


# Airline names for display
AIRLINE_NAMES = {
    'LH': 'Lufthansa',
    'LX': 'Swiss International Air Lines',
    'OS': 'Austrian Airlines',
    'SN': 'Brussels Airlines',
    'AF': 'Air France',
    'KL': 'KLM Royal Dutch Airlines',
    'BA': 'British Airways',
    'IB': 'Iberia',
    'VY': 'Vueling',
    'FR': 'Ryanair',
    'U2': 'easyJet',
    'EZY': 'easyJet',
    'EW': 'Eurowings',
    'AZ': 'ITA Airways',
    'SK': 'SAS Scandinavian Airlines',
    'AY': 'Finnair',
    'TP': 'TAP Air Portugal',
    'EI': 'Aer Lingus',
    'A3': 'Aegean Airlines',
    'DY': 'Norwegian Air Shuttle',
    'W6': 'Wizz Air',
    'BT': 'Air Baltic',
    'LO': 'LOT Polish Airlines',
    'OK': 'Czech Airlines',
    'RO': 'TAROM',
    'TK': 'Turkish Airlines',
    'EK': 'Emirates',
    'QR': 'Qatar Airways',
    'EY': 'Etihad Airways',
    'AA': 'American Airlines',
    'UA': 'United Airlines',
    'DL': 'Delta Air Lines',
    'AC': 'Air Canada',
    'SQ': 'Singapore Airlines',
    'CX': 'Cathay Pacific',
    'QF': 'Qantas',
}


def get_airline_name(code: str) -> str:
    """Get airline name from IATA code."""
    return AIRLINE_NAMES.get(code.upper(), f"Airline {code.upper()}")
