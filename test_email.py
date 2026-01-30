#!/usr/bin/env python3
"""Test script for the email generator."""

from datetime import datetime
from compensation_calculator import (
    FlightDetails, ClaimType, calculate_compensation, get_airport
)
from email_generator import (
    PassengerInfo, BankDetails, ClaimEmailData, generate_claim_email
)


def test_email_generation():
    """Test email generation."""
    print("=" * 60)
    print("Email Generator - Test")
    print("=" * 60)

    # Create test flight
    dep = get_airport('LHR')
    arr = get_airport('CDG')

    flight = FlightDetails(
        flight_number="BA304",
        airline_code="BA",
        airline_name="British Airways",
        departure_airport=dep,
        arrival_airport=arr,
        scheduled_departure=datetime(2024, 1, 15, 10, 0),
        scheduled_arrival=datetime(2024, 1, 15, 12, 30),
        actual_departure=datetime(2024, 1, 15, 14, 0),
        actual_arrival=datetime(2024, 1, 15, 16, 30),
        is_cancelled=False,
        is_eu_carrier=True
    )

    # Calculate compensation
    result = calculate_compensation(flight, ClaimType.DELAY)

    # Create passengers
    passengers = [
        PassengerInfo(
            first_name="John",
            last_name="Smith",
            date_of_birth="1985-06-15",
            email="john.smith@example.com",
            phone="+44 7700 900123",
            address="123 Example Street, London, W1A 1AA"
        ),
        PassengerInfo(
            first_name="Jane",
            last_name="Smith",
            date_of_birth="1987-03-22",
            email=None,
            phone=None,
            address=None
        )
    ]

    # Create bank details
    bank = BankDetails(
        account_holder="John Smith",
        iban="GB82 WEST 1234 5698 7654 32",
        bic_swift="WESTGB2L",
        bank_name="Example Bank"
    )

    # Create claim data
    claim_data = ClaimEmailData(
        passengers=passengers,
        flight=flight,
        compensation=result,
        booking_reference="ABC123",
        bank_details=bank,
        additional_notes="Please note I have also incurred meal expenses of €45 during the delay."
    )

    # Generate email
    email = generate_claim_email(claim_data)

    print("\nGenerated Email:")
    print("-" * 60)
    print(email[:2000])
    print("\n[... truncated for display ...]")
    print("-" * 60)

    # Verify key elements are present
    assert "EC261/2004" in email, "Should reference EC261/2004"
    assert "BA304" in email, "Should contain flight number"
    assert "€250" in email, "Should contain compensation amount"
    assert "John Smith" in email, "Should contain passenger name"
    assert "ABC123" in email, "Should contain booking reference"
    assert "GB82 WEST" in email, "Should contain IBAN"
    assert "London Heathrow" in email, "Should contain departure airport"
    assert "Paris Charles de Gaulle" in email, "Should contain arrival airport"

    print("\n✓ Email generated successfully with all required elements!")
    print("=" * 60)


if __name__ == "__main__":
    test_email_generation()
