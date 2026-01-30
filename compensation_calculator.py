"""
EC261/2004 Compensation Calculator

Implements the EU flight compensation regulations for:
- Flight delays (3+ hours at final destination)
- Flight cancellations
- Denied boarding

Compensation tiers:
- €250: Flights ≤1,500 km, delayed 3+ hours
- €400: Intra-EU flights >1,500 km OR other flights 1,500-3,500 km, delayed 3+ hours
- €600: Flights >3,500 km, delayed 4+ hours (€300 if 3-4 hours delay)
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, Tuple
from math import radians, sin, cos, sqrt, atan2


class ClaimType(Enum):
    """Type of compensation claim."""
    DELAY = "delay"
    CANCELLATION = "cancellation"
    DENIED_BOARDING = "denied_boarding"
    MISSED_CONNECTION = "missed_connection"


class CompensationTier(Enum):
    """Compensation amount tiers under EC261/2004."""
    TIER_250 = 250
    TIER_300 = 300
    TIER_400 = 400
    TIER_600 = 600
    NOT_ELIGIBLE = 0


@dataclass
class Airport:
    """Airport information."""
    code: str
    name: str
    city: str
    country: str
    latitude: float
    longitude: float
    is_eu: bool


@dataclass
class FlightDetails:
    """Flight information for compensation calculation."""
    flight_number: str
    airline_code: str
    airline_name: str
    departure_airport: Airport
    arrival_airport: Airport
    scheduled_departure: datetime
    scheduled_arrival: datetime
    actual_departure: Optional[datetime] = None
    actual_arrival: Optional[datetime] = None
    is_cancelled: bool = False
    is_eu_carrier: bool = False


@dataclass
class CompensationResult:
    """Result of compensation eligibility calculation."""
    eligible: bool
    amount: int
    tier: CompensationTier
    claim_type: ClaimType
    delay_hours: float
    distance_km: int
    reason: str
    warnings: list[str]
    legal_basis: str


# EU/EEA countries (includes UK for flights before Brexit effective date)
EU_EEA_COUNTRIES = {
    'AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR',
    'DE', 'GR', 'HU', 'IS', 'IE', 'IT', 'LV', 'LI', 'LT', 'LU',
    'MT', 'NL', 'NO', 'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE',
    'CH',  # Switzerland (bilateral agreement)
}

# UK included for historical flights
UK_COUNTRIES = {'GB', 'UK'}

# Common airport data (subset - in production, use a complete database)
AIRPORT_DATA = {
    # Major EU airports
    'LHR': ('London Heathrow', 'London', 'GB', 51.4700, -0.4543),
    'CDG': ('Paris Charles de Gaulle', 'Paris', 'FR', 49.0097, 2.5479),
    'FRA': ('Frankfurt Airport', 'Frankfurt', 'DE', 50.0379, 8.5622),
    'AMS': ('Amsterdam Schiphol', 'Amsterdam', 'NL', 52.3105, 4.7683),
    'MAD': ('Madrid Barajas', 'Madrid', 'ES', 40.4983, -3.5676),
    'BCN': ('Barcelona El Prat', 'Barcelona', 'ES', 41.2971, 2.0785),
    'FCO': ('Rome Fiumicino', 'Rome', 'IT', 41.8003, 12.2389),
    'MUC': ('Munich Airport', 'Munich', 'DE', 48.3537, 11.7750),
    'LGW': ('London Gatwick', 'London', 'GB', 51.1537, -0.1821),
    'ORY': ('Paris Orly', 'Paris', 'FR', 48.7233, 2.3794),
    'DUB': ('Dublin Airport', 'Dublin', 'IE', 53.4264, -6.2499),
    'VIE': ('Vienna Airport', 'Vienna', 'AT', 48.1103, 16.5697),
    'ZRH': ('Zurich Airport', 'Zurich', 'CH', 47.4647, 8.5492),
    'CPH': ('Copenhagen Airport', 'Copenhagen', 'DK', 55.6180, 12.6508),
    'BRU': ('Brussels Airport', 'Brussels', 'BE', 50.9014, 4.4844),
    'LIS': ('Lisbon Airport', 'Lisbon', 'PT', 38.7756, -9.1354),
    'ATH': ('Athens Airport', 'Athens', 'GR', 37.9364, 23.9445),
    'PRG': ('Prague Airport', 'Prague', 'CZ', 50.1008, 14.2600),
    'WAW': ('Warsaw Chopin', 'Warsaw', 'PL', 52.1657, 20.9671),
    'BUD': ('Budapest Airport', 'Budapest', 'HU', 47.4369, 19.2556),
    'OSL': ('Oslo Gardermoen', 'Oslo', 'NO', 60.1939, 11.1004),
    'ARN': ('Stockholm Arlanda', 'Stockholm', 'SE', 59.6519, 17.9186),
    'HEL': ('Helsinki Vantaa', 'Helsinki', 'FI', 60.3172, 24.9633),
    'MXP': ('Milan Malpensa', 'Milan', 'IT', 45.6306, 8.7281),
    'STN': ('London Stansted', 'London', 'GB', 51.8850, 0.2350),
    'MAN': ('Manchester Airport', 'Manchester', 'GB', 53.3537, -2.2750),
    'EDI': ('Edinburgh Airport', 'Edinburgh', 'GB', 55.9500, -3.3725),
    # Major non-EU airports
    'JFK': ('John F Kennedy', 'New York', 'US', 40.6413, -73.7781),
    'LAX': ('Los Angeles International', 'Los Angeles', 'US', 33.9425, -118.4081),
    'ORD': ('Chicago O\'Hare', 'Chicago', 'US', 41.9742, -87.9073),
    'SFO': ('San Francisco International', 'San Francisco', 'US', 37.6213, -122.3790),
    'YYZ': ('Toronto Pearson', 'Toronto', 'CA', 43.6777, -79.6248),
    'DXB': ('Dubai International', 'Dubai', 'AE', 25.2532, 55.3657),
    'SIN': ('Singapore Changi', 'Singapore', 'SG', 1.3644, 103.9915),
    'HKG': ('Hong Kong International', 'Hong Kong', 'HK', 22.3080, 113.9185),
    'NRT': ('Tokyo Narita', 'Tokyo', 'JP', 35.7720, 140.3929),
    'SYD': ('Sydney Airport', 'Sydney', 'AU', -33.9399, 151.1753),
    'PEK': ('Beijing Capital', 'Beijing', 'CN', 40.0799, 116.6031),
    'ICN': ('Seoul Incheon', 'Seoul', 'KR', 37.4602, 126.4407),
    'BKK': ('Bangkok Suvarnabhumi', 'Bangkok', 'TH', 13.6900, 100.7501),
    'DEL': ('Delhi Indira Gandhi', 'Delhi', 'IN', 28.5562, 77.1000),
    'GRU': ('São Paulo Guarulhos', 'São Paulo', 'BR', -23.4356, -46.4731),
    'MEX': ('Mexico City International', 'Mexico City', 'MX', 19.4363, -99.0721),
    'JNB': ('Johannesburg O.R. Tambo', 'Johannesburg', 'ZA', -26.1392, 28.2460),
    'CAI': ('Cairo International', 'Cairo', 'EG', 30.1219, 31.4056),
    'IST': ('Istanbul Airport', 'Istanbul', 'TR', 41.2753, 28.7519),
    'DOH': ('Doha Hamad', 'Doha', 'QA', 25.2731, 51.6081),
}

# EU-based airlines (IATA codes)
EU_CARRIERS = {
    'LH', 'LX', 'OS', 'SN',  # Lufthansa Group
    'AF', 'KL',  # Air France-KLM
    'BA', 'IB', 'VY',  # IAG
    'FR',  # Ryanair
    'U2', 'EZY',  # easyJet
    'EW', 'DE',  # Eurowings
    'AZ', 'EN',  # ITA Airways
    'SK',  # SAS
    'AY',  # Finnair
    'TP',  # TAP Portugal
    'EI',  # Aer Lingus
    'A3',  # Aegean
    'DY',  # Norwegian
    'W6',  # Wizz Air
    'BT',  # Air Baltic
    'LO',  # LOT Polish
    'OK',  # Czech Airlines
    'RO',  # TAROM
    'JU',  # Air Serbia
    'OU',  # Croatia Airlines
    'JP',  # Adria Airways
    'KM',  # Air Malta
    'CY',  # Cyprus Airways
    'OA',  # Olympic Air
    'FB',  # Bulgaria Air
    'TK',  # Turkish Airlines (not EU but important)
}


def get_airport(code: str) -> Optional[Airport]:
    """Get airport information by IATA code."""
    code = code.upper().strip()
    if code not in AIRPORT_DATA:
        return None

    name, city, country, lat, lon = AIRPORT_DATA[code]
    is_eu = country in EU_EEA_COUNTRIES or country in UK_COUNTRIES

    return Airport(
        code=code,
        name=name,
        city=city,
        country=country,
        latitude=lat,
        longitude=lon,
        is_eu=is_eu
    )


def calculate_distance_km(airport1: Airport, airport2: Airport) -> int:
    """
    Calculate great-circle distance between two airports using Haversine formula.

    Returns distance in kilometers, rounded to nearest km.
    """
    R = 6371  # Earth's radius in kilometers

    lat1, lon1 = radians(airport1.latitude), radians(airport1.longitude)
    lat2, lon2 = radians(airport2.latitude), radians(airport2.longitude)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return round(R * c)


def calculate_delay_hours(scheduled: datetime, actual: datetime) -> float:
    """Calculate delay in hours (can be negative for early arrivals)."""
    delta = actual - scheduled
    return delta.total_seconds() / 3600


def is_eu_departure(flight: FlightDetails) -> bool:
    """Check if flight departs from an EU/EEA airport."""
    return flight.departure_airport.is_eu


def is_eu_arrival_on_eu_carrier(flight: FlightDetails) -> bool:
    """Check if flight arrives in EU on an EU carrier."""
    return flight.arrival_airport.is_eu and flight.is_eu_carrier


def check_claim_time_limit(flight_date: datetime, years_limit: int = 6) -> Tuple[bool, str]:
    """
    Check if flight is within the claim limitation period.

    Different countries have different limits:
    - UK, Ireland, Luxembourg: 6 years
    - Germany, Austria: 3 years
    - Belgium: 1 year
    - France, Netherlands, Spain, Italy: 5 years

    Returns (is_within_limit, warning_message)
    """
    now = datetime.now()
    years_since_flight = (now - flight_date).days / 365.25

    if years_since_flight > years_limit:
        return False, f"Flight occurred more than {years_limit} years ago. Claim may be time-barred."

    if years_since_flight > 3:
        return True, (
            "Warning: Some EU countries have shorter limitation periods "
            "(e.g., Germany: 3 years, Belgium: 1 year). Check local regulations."
        )

    return True, ""


def is_carrier_eu_based(airline_code: str) -> bool:
    """Check if airline is EU-based by IATA code."""
    return airline_code.upper() in EU_CARRIERS


def calculate_compensation(
    flight: FlightDetails,
    claim_type: ClaimType = ClaimType.DELAY,
    years_limit: int = 6
) -> CompensationResult:
    """
    Calculate compensation eligibility and amount under EC261/2004.

    Args:
        flight: Flight details including scheduled and actual times
        claim_type: Type of claim (delay, cancellation, denied boarding)
        years_limit: Limitation period in years

    Returns:
        CompensationResult with eligibility, amount, and legal basis
    """
    warnings = []

    # Check jurisdiction - must depart from EU OR arrive in EU on EU carrier
    eu_departure = is_eu_departure(flight)
    eu_arrival_eu_carrier = is_eu_arrival_on_eu_carrier(flight)

    if not eu_departure and not eu_arrival_eu_carrier:
        return CompensationResult(
            eligible=False,
            amount=0,
            tier=CompensationTier.NOT_ELIGIBLE,
            claim_type=claim_type,
            delay_hours=0,
            distance_km=0,
            reason=(
                "Flight does not fall under EC261/2004 jurisdiction. "
                "Regulation applies only to: (a) flights departing from EU/EEA airports, or "
                "(b) flights arriving in EU/EEA on an EU-based carrier."
            ),
            warnings=[],
            legal_basis=""
        )

    # Check time limitation
    within_limit, limit_warning = check_claim_time_limit(
        flight.scheduled_departure, years_limit
    )
    if limit_warning:
        warnings.append(limit_warning)

    if not within_limit:
        return CompensationResult(
            eligible=False,
            amount=0,
            tier=CompensationTier.NOT_ELIGIBLE,
            claim_type=claim_type,
            delay_hours=0,
            distance_km=0,
            reason=limit_warning,
            warnings=warnings,
            legal_basis=""
        )

    # Calculate distance
    distance_km = calculate_distance_km(
        flight.departure_airport,
        flight.arrival_airport
    )

    # Determine if intra-EU flight
    is_intra_eu = flight.departure_airport.is_eu and flight.arrival_airport.is_eu

    # Calculate delay at destination
    if claim_type == ClaimType.CANCELLATION:
        # For cancellations, full compensation applies unless rerouted within limits
        delay_hours = float('inf')  # Treat as maximum delay
    elif claim_type == ClaimType.DENIED_BOARDING:
        delay_hours = float('inf')  # Full compensation for denied boarding
    elif flight.actual_arrival and flight.scheduled_arrival:
        delay_hours = calculate_delay_hours(
            flight.scheduled_arrival,
            flight.actual_arrival
        )
    else:
        return CompensationResult(
            eligible=False,
            amount=0,
            tier=CompensationTier.NOT_ELIGIBLE,
            claim_type=claim_type,
            delay_hours=0,
            distance_km=distance_km,
            reason="Unable to calculate delay - actual arrival time not provided.",
            warnings=warnings,
            legal_basis=""
        )

    # Determine compensation tier based on distance and delay
    tier = CompensationTier.NOT_ELIGIBLE
    legal_articles = []

    if claim_type in (ClaimType.CANCELLATION, ClaimType.DENIED_BOARDING):
        # Full compensation for cancellations and denied boarding
        # (unless extraordinary circumstances for cancellations)
        if distance_km <= 1500:
            tier = CompensationTier.TIER_250
            legal_articles = ["Article 7(1)(a)"]
        elif is_intra_eu or distance_km <= 3500:
            tier = CompensationTier.TIER_400
            legal_articles = ["Article 7(1)(b)"]
        else:
            tier = CompensationTier.TIER_600
            legal_articles = ["Article 7(1)(c)"]

        if claim_type == ClaimType.CANCELLATION:
            legal_articles.insert(0, "Article 5")
        else:
            legal_articles.insert(0, "Article 4")

    else:  # DELAY or MISSED_CONNECTION
        if delay_hours < 3:
            return CompensationResult(
                eligible=False,
                amount=0,
                tier=CompensationTier.NOT_ELIGIBLE,
                claim_type=claim_type,
                delay_hours=delay_hours,
                distance_km=distance_km,
                reason=(
                    f"Delay of {delay_hours:.1f} hours does not meet the minimum threshold. "
                    "EC261/2004 requires at least 3 hours delay at final destination for compensation."
                ),
                warnings=warnings,
                legal_basis=""
            )

        # Determine tier based on distance and delay
        if distance_km <= 1500:
            if delay_hours >= 3:
                tier = CompensationTier.TIER_250
                legal_articles = ["Article 6", "Article 7(1)(a)"]
        elif is_intra_eu or distance_km <= 3500:
            if delay_hours >= 3:
                tier = CompensationTier.TIER_400
                legal_articles = ["Article 6", "Article 7(1)(b)"]
        else:  # > 3500 km non-EU
            if delay_hours >= 4:
                tier = CompensationTier.TIER_600
                legal_articles = ["Article 6", "Article 7(1)(c)"]
            elif delay_hours >= 3:
                tier = CompensationTier.TIER_300
                legal_articles = ["Article 6", "Article 7(2)(c)"]
                warnings.append(
                    "For flights over 3,500km with delays between 3-4 hours, "
                    "compensation may be reduced by 50% to €300."
                )

    if tier == CompensationTier.NOT_ELIGIBLE:
        return CompensationResult(
            eligible=False,
            amount=0,
            tier=tier,
            claim_type=claim_type,
            delay_hours=delay_hours,
            distance_km=distance_km,
            reason="Delay does not meet compensation thresholds under EC261/2004.",
            warnings=warnings,
            legal_basis=""
        )

    # Build legal basis string
    legal_basis = (
        f"Regulation (EC) No 261/2004 of the European Parliament and of the Council, "
        f"{', '.join(legal_articles)}"
    )

    # Determine reason message based on claim type
    if claim_type == ClaimType.DELAY:
        reason = (
            f"Flight delayed by {delay_hours:.1f} hours at final destination. "
            f"Distance: {distance_km:,} km. Eligible for €{tier.value} compensation."
        )
    elif claim_type == ClaimType.CANCELLATION:
        reason = (
            f"Flight cancelled. Distance: {distance_km:,} km. "
            f"Eligible for €{tier.value} compensation."
        )
    elif claim_type == ClaimType.DENIED_BOARDING:
        reason = (
            f"Denied boarding. Distance: {distance_km:,} km. "
            f"Eligible for €{tier.value} compensation."
        )
    else:  # MISSED_CONNECTION
        reason = (
            f"Missed connection due to delay. Final delay: {delay_hours:.1f} hours. "
            f"Distance: {distance_km:,} km. Eligible for €{tier.value} compensation."
        )

    return CompensationResult(
        eligible=True,
        amount=tier.value,
        tier=tier,
        claim_type=claim_type,
        delay_hours=delay_hours if delay_hours != float('inf') else 0,
        distance_km=distance_km,
        reason=reason,
        warnings=warnings,
        legal_basis=legal_basis
    )


def get_distance_category(distance_km: int, is_intra_eu: bool) -> str:
    """Get human-readable distance category for the flight."""
    if distance_km <= 1500:
        return "Short-haul (≤1,500 km)"
    elif is_intra_eu or distance_km <= 3500:
        return "Medium-haul (1,500-3,500 km or intra-EU)"
    else:
        return "Long-haul (>3,500 km)"
