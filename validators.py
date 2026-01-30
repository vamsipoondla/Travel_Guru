"""
Input Validators for Flight Compensation Application

Validates user inputs including:
- Flight numbers
- Airport codes
- Dates
- Booking references
- Personal information
- Bank details
"""

import re
from datetime import datetime, date
from typing import Tuple, Optional


def validate_flight_number(flight_number: str) -> Tuple[bool, str]:
    """
    Validate flight number format.

    Valid formats:
    - BA123, BA1234, BA12345
    - BA 123, BA-123
    - 2-3 letter airline code + 1-5 digit number

    Returns:
        Tuple of (is_valid, error_message or normalized flight number)
    """
    if not flight_number:
        return False, "Flight number is required"

    # Normalize: remove spaces and hyphens, uppercase
    normalized = flight_number.upper().replace(' ', '').replace('-', '')

    # Check format: 2-3 letters followed by 1-5 digits
    pattern = r'^[A-Z]{2,3}\d{1,5}$'

    if not re.match(pattern, normalized):
        return False, (
            "Invalid flight number format. "
            "Expected format: AA123 (2-3 letter airline code + flight number)"
        )

    return True, normalized


def validate_airport_code(code: str) -> Tuple[bool, str]:
    """
    Validate IATA airport code.

    Returns:
        Tuple of (is_valid, error_message or normalized code)
    """
    if not code:
        return False, "Airport code is required"

    normalized = code.upper().strip()

    if len(normalized) != 3:
        return False, "Airport code must be 3 letters (IATA code)"

    if not normalized.isalpha():
        return False, "Airport code must contain only letters"

    return True, normalized


def validate_date(
    date_str: str,
    allow_past: bool = True,
    allow_future: bool = True,
    max_years_past: int = 10
) -> Tuple[bool, str]:
    """
    Validate date string.

    Accepts formats:
    - YYYY-MM-DD
    - DD/MM/YYYY
    - DD-MM-YYYY
    - DD.MM.YYYY

    Returns:
        Tuple of (is_valid, error_message or ISO format date string)
    """
    if not date_str:
        return False, "Date is required"

    date_str = date_str.strip()

    # Try different formats
    formats = [
        '%Y-%m-%d',
        '%d/%m/%Y',
        '%d-%m-%Y',
        '%d.%m.%Y',
        '%m/%d/%Y',
    ]

    parsed_date = None
    for fmt in formats:
        try:
            parsed_date = datetime.strptime(date_str, fmt).date()
            break
        except ValueError:
            continue

    if not parsed_date:
        return False, (
            "Invalid date format. Accepted formats: "
            "YYYY-MM-DD, DD/MM/YYYY, DD-MM-YYYY"
        )

    today = date.today()

    if not allow_past and parsed_date < today:
        return False, "Date cannot be in the past"

    if not allow_future and parsed_date > today:
        return False, "Date cannot be in the future"

    if max_years_past:
        min_date = date(today.year - max_years_past, today.month, today.day)
        if parsed_date < min_date:
            return False, f"Date cannot be more than {max_years_past} years ago"

    return True, parsed_date.isoformat()


def validate_time(time_str: str) -> Tuple[bool, str]:
    """
    Validate time string.

    Accepts formats:
    - HH:MM
    - HH:MM:SS
    - HH.MM

    Returns:
        Tuple of (is_valid, error_message or HH:MM format time string)
    """
    if not time_str:
        return False, "Time is required"

    time_str = time_str.strip().replace('.', ':')

    # Try different formats
    formats = ['%H:%M', '%H:%M:%S']

    for fmt in formats:
        try:
            parsed_time = datetime.strptime(time_str, fmt).time()
            return True, parsed_time.strftime('%H:%M')
        except ValueError:
            continue

    return False, "Invalid time format. Expected HH:MM (24-hour format)"


def validate_booking_reference(ref: str) -> Tuple[bool, str]:
    """
    Validate booking/confirmation reference.

    Typically 5-8 alphanumeric characters.

    Returns:
        Tuple of (is_valid, error_message or normalized reference)
    """
    if not ref:
        return False, "Booking reference is required"

    normalized = ref.upper().strip().replace(' ', '')

    if len(normalized) < 4:
        return False, "Booking reference seems too short (minimum 4 characters)"

    if len(normalized) > 12:
        return False, "Booking reference seems too long (maximum 12 characters)"

    if not re.match(r'^[A-Z0-9]+$', normalized):
        return False, "Booking reference should contain only letters and numbers"

    return True, normalized


def validate_name(name: str, field_name: str = "Name") -> Tuple[bool, str]:
    """
    Validate person name.

    Returns:
        Tuple of (is_valid, error_message or normalized name)
    """
    if not name:
        return False, f"{field_name} is required"

    normalized = name.strip()

    if len(normalized) < 2:
        return False, f"{field_name} must be at least 2 characters"

    if len(normalized) > 50:
        return False, f"{field_name} is too long (maximum 50 characters)"

    # Allow letters, spaces, hyphens, apostrophes
    if not re.match(r"^[A-Za-z\s\-']+$", normalized):
        return False, (
            f"{field_name} should contain only letters, spaces, "
            "hyphens, and apostrophes"
        )

    return True, normalized.title()


def validate_email(email: str) -> Tuple[bool, str]:
    """
    Validate email address.

    Returns:
        Tuple of (is_valid, error_message or normalized email)
    """
    if not email:
        return True, ""  # Email is optional

    email = email.strip().lower()

    # Basic email pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if not re.match(pattern, email):
        return False, "Invalid email address format"

    return True, email


def validate_phone(phone: str) -> Tuple[bool, str]:
    """
    Validate phone number.

    Returns:
        Tuple of (is_valid, error_message or normalized phone)
    """
    if not phone:
        return True, ""  # Phone is optional

    # Remove common separators for validation
    cleaned = re.sub(r'[\s\-\.\(\)]', '', phone.strip())

    # Should start with + or digit, contain 7-15 digits
    if not re.match(r'^\+?\d{7,15}$', cleaned):
        return False, (
            "Invalid phone number. Include country code (e.g., +44 123 456 7890)"
        )

    return True, phone.strip()


def validate_iban(iban: str) -> Tuple[bool, str]:
    """
    Validate IBAN (International Bank Account Number).

    Basic format validation - does not verify checksum.

    Returns:
        Tuple of (is_valid, error_message or normalized IBAN)
    """
    if not iban:
        return False, "IBAN is required"

    # Remove spaces and convert to uppercase
    normalized = iban.upper().replace(' ', '')

    # IBAN length by country (subset of common ones)
    iban_lengths = {
        'DE': 22, 'FR': 27, 'GB': 22, 'ES': 24, 'IT': 27,
        'NL': 18, 'BE': 16, 'AT': 20, 'PT': 25, 'IE': 22,
        'CH': 21, 'PL': 28, 'SE': 24, 'NO': 15, 'DK': 18,
        'FI': 18, 'GR': 27, 'CZ': 24, 'HU': 28, 'RO': 24,
    }

    # Basic format check: 2 letters + 2 digits + up to 30 alphanumeric
    if not re.match(r'^[A-Z]{2}\d{2}[A-Z0-9]{1,30}$', normalized):
        return False, (
            "Invalid IBAN format. Expected: country code (2 letters) + "
            "check digits (2 digits) + account number"
        )

    country_code = normalized[:2]
    if country_code in iban_lengths:
        expected_length = iban_lengths[country_code]
        if len(normalized) != expected_length:
            return False, (
                f"Invalid IBAN length for {country_code}. "
                f"Expected {expected_length} characters, got {len(normalized)}"
            )

    # Format with spaces for display
    formatted = ' '.join(
        normalized[i:i+4] for i in range(0, len(normalized), 4)
    )

    return True, formatted


def validate_bic_swift(bic: str) -> Tuple[bool, str]:
    """
    Validate BIC/SWIFT code.

    Returns:
        Tuple of (is_valid, error_message or normalized BIC)
    """
    if not bic:
        return True, ""  # BIC is optional

    normalized = bic.upper().replace(' ', '')

    # BIC is 8 or 11 characters
    if len(normalized) not in (8, 11):
        return False, "BIC/SWIFT code must be 8 or 11 characters"

    # Format: 4 letters (bank) + 2 letters (country) + 2 alphanumeric (location)
    # + optional 3 alphanumeric (branch)
    if not re.match(r'^[A-Z]{4}[A-Z]{2}[A-Z0-9]{2}([A-Z0-9]{3})?$', normalized):
        return False, "Invalid BIC/SWIFT code format"

    return True, normalized


def validate_date_of_birth(dob_str: str) -> Tuple[bool, str]:
    """
    Validate date of birth.

    Must be in the past and person must be at least 0 years old
    and less than 120 years old.

    Returns:
        Tuple of (is_valid, error_message or ISO format date string)
    """
    is_valid, result = validate_date(
        dob_str,
        allow_past=True,
        allow_future=False,
        max_years_past=120
    )

    if not is_valid:
        return False, result

    # Additional check: must be in the past
    dob = datetime.strptime(result, '%Y-%m-%d').date()
    if dob >= date.today():
        return False, "Date of birth must be in the past"

    return True, result


def validate_delay_hours(hours_str: str) -> Tuple[bool, float]:
    """
    Validate delay hours input.

    Returns:
        Tuple of (is_valid, error_message or hours as float)
    """
    if not hours_str:
        return False, "Delay hours is required"

    try:
        hours = float(hours_str.strip())
    except ValueError:
        return False, "Invalid number format for delay hours"

    if hours < 0:
        return False, "Delay cannot be negative"

    if hours > 72:
        return False, "Delay seems unreasonably long (maximum 72 hours)"

    return True, hours
