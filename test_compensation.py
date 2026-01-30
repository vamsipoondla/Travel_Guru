#!/usr/bin/env python3
"""Test script for the compensation calculator."""

from datetime import datetime, timedelta
from compensation_calculator import (
    FlightDetails, Airport, ClaimType,
    calculate_compensation, get_airport, calculate_distance_km
)


def test_compensation_calculation():
    """Run tests on the compensation calculator."""
    print("=" * 60)
    print("EU Flight Compensation Calculator - Test Suite")
    print("=" * 60)

    # Test 1: Short-haul EU flight with 4 hour delay (should get €250)
    print("\nTest 1: Short-haul EU flight (LHR → CDG) with 4 hour delay")
    dep = get_airport('LHR')
    arr = get_airport('CDG')
    distance = calculate_distance_km(dep, arr)
    print(f"  Distance: {distance} km")

    flight1 = FlightDetails(
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

    result1 = calculate_compensation(flight1, ClaimType.DELAY)
    print(f"  Eligible: {result1.eligible}")
    print(f"  Amount: €{result1.amount}")
    print(f"  Delay: {result1.delay_hours:.1f} hours")
    assert result1.eligible == True, "Should be eligible"
    assert result1.amount == 250, f"Should be €250, got €{result1.amount}"
    print("  ✓ PASSED")

    # Test 2: Medium-haul EU flight with 3.5 hour delay (should get €400)
    print("\nTest 2: Medium-haul EU flight (LHR → ATH) with 3.5 hour delay")
    arr2 = get_airport('ATH')
    distance2 = calculate_distance_km(dep, arr2)
    print(f"  Distance: {distance2} km")

    flight2 = FlightDetails(
        flight_number="BA640",
        airline_code="BA",
        airline_name="British Airways",
        departure_airport=dep,
        arrival_airport=arr2,
        scheduled_departure=datetime(2024, 1, 15, 8, 0),
        scheduled_arrival=datetime(2024, 1, 15, 14, 0),
        actual_departure=datetime(2024, 1, 15, 11, 30),
        actual_arrival=datetime(2024, 1, 15, 17, 30),
        is_cancelled=False,
        is_eu_carrier=True
    )

    result2 = calculate_compensation(flight2, ClaimType.DELAY)
    print(f"  Eligible: {result2.eligible}")
    print(f"  Amount: €{result2.amount}")
    print(f"  Delay: {result2.delay_hours:.1f} hours")
    assert result2.eligible == True, "Should be eligible"
    assert result2.amount == 400, f"Should be €400, got €{result2.amount}"
    print("  ✓ PASSED")

    # Test 3: Long-haul non-EU flight with 4.5 hour delay (should get €600)
    print("\nTest 3: Long-haul flight (LHR → JFK) with 4.5 hour delay")
    arr3 = get_airport('JFK')
    distance3 = calculate_distance_km(dep, arr3)
    print(f"  Distance: {distance3} km")

    flight3 = FlightDetails(
        flight_number="BA175",
        airline_code="BA",
        airline_name="British Airways",
        departure_airport=dep,
        arrival_airport=arr3,
        scheduled_departure=datetime(2024, 1, 15, 9, 0),
        scheduled_arrival=datetime(2024, 1, 15, 12, 0),
        actual_departure=datetime(2024, 1, 15, 13, 0),
        actual_arrival=datetime(2024, 1, 15, 16, 30),
        is_cancelled=False,
        is_eu_carrier=True
    )

    result3 = calculate_compensation(flight3, ClaimType.DELAY)
    print(f"  Eligible: {result3.eligible}")
    print(f"  Amount: €{result3.amount}")
    print(f"  Delay: {result3.delay_hours:.1f} hours")
    assert result3.eligible == True, "Should be eligible"
    assert result3.amount == 600, f"Should be €600, got €{result3.amount}"
    print("  ✓ PASSED")

    # Test 4: Long-haul with 3.5 hour delay (should get €300 - reduced)
    print("\nTest 4: Long-haul flight (LHR → JFK) with 3.5 hour delay (reduced)")
    flight4 = FlightDetails(
        flight_number="BA175",
        airline_code="BA",
        airline_name="British Airways",
        departure_airport=dep,
        arrival_airport=arr3,
        scheduled_departure=datetime(2024, 1, 15, 9, 0),
        scheduled_arrival=datetime(2024, 1, 15, 12, 0),
        actual_departure=datetime(2024, 1, 15, 12, 0),
        actual_arrival=datetime(2024, 1, 15, 15, 30),
        is_cancelled=False,
        is_eu_carrier=True
    )

    result4 = calculate_compensation(flight4, ClaimType.DELAY)
    print(f"  Eligible: {result4.eligible}")
    print(f"  Amount: €{result4.amount}")
    print(f"  Delay: {result4.delay_hours:.1f} hours")
    assert result4.eligible == True, "Should be eligible"
    assert result4.amount == 300, f"Should be €300 (reduced), got €{result4.amount}"
    print("  ✓ PASSED")

    # Test 5: Not eligible - less than 3 hour delay
    print("\nTest 5: Short-haul with 2.5 hour delay (not eligible)")
    flight5 = FlightDetails(
        flight_number="BA304",
        airline_code="BA",
        airline_name="British Airways",
        departure_airport=dep,
        arrival_airport=arr,
        scheduled_departure=datetime(2024, 1, 15, 10, 0),
        scheduled_arrival=datetime(2024, 1, 15, 12, 30),
        actual_departure=datetime(2024, 1, 15, 12, 0),
        actual_arrival=datetime(2024, 1, 15, 15, 0),
        is_cancelled=False,
        is_eu_carrier=True
    )

    result5 = calculate_compensation(flight5, ClaimType.DELAY)
    print(f"  Eligible: {result5.eligible}")
    print(f"  Delay: {result5.delay_hours:.1f} hours")
    assert result5.eligible == False, "Should NOT be eligible"
    print("  ✓ PASSED")

    # Test 6: Not eligible - non-EU origin, non-EU carrier
    print("\nTest 6: Non-EU origin, non-EU carrier (JFK → LHR on AA)")
    flight6 = FlightDetails(
        flight_number="AA100",
        airline_code="AA",
        airline_name="American Airlines",
        departure_airport=arr3,  # JFK
        arrival_airport=dep,     # LHR
        scheduled_departure=datetime(2024, 1, 15, 18, 0),
        scheduled_arrival=datetime(2024, 1, 16, 6, 0),
        actual_departure=datetime(2024, 1, 15, 22, 0),
        actual_arrival=datetime(2024, 1, 16, 10, 0),
        is_cancelled=False,
        is_eu_carrier=False
    )

    result6 = calculate_compensation(flight6, ClaimType.DELAY)
    print(f"  Eligible: {result6.eligible}")
    assert result6.eligible == False, "Should NOT be eligible (non-EU origin, non-EU carrier)"
    print("  ✓ PASSED")

    # Test 7: Cancellation
    print("\nTest 7: Flight cancellation (LHR → FRA)")
    arr7 = get_airport('FRA')
    distance7 = calculate_distance_km(dep, arr7)
    print(f"  Distance: {distance7} km")

    flight7 = FlightDetails(
        flight_number="LH901",
        airline_code="LH",
        airline_name="Lufthansa",
        departure_airport=dep,
        arrival_airport=arr7,
        scheduled_departure=datetime(2024, 1, 15, 10, 0),
        scheduled_arrival=datetime(2024, 1, 15, 12, 30),
        actual_departure=None,
        actual_arrival=None,
        is_cancelled=True,
        is_eu_carrier=True
    )

    result7 = calculate_compensation(flight7, ClaimType.CANCELLATION)
    print(f"  Eligible: {result7.eligible}")
    print(f"  Amount: €{result7.amount}")
    assert result7.eligible == True, "Should be eligible for cancellation"
    assert result7.amount == 250, f"Should be €250, got €{result7.amount}"
    print("  ✓ PASSED")

    print("\n" + "=" * 60)
    print("All tests passed! ✓")
    print("=" * 60)


if __name__ == "__main__":
    test_compensation_calculation()
