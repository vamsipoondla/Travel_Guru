"""
Email Generator for EC261/2004 Compensation Claims

Generates professional compensation claim emails with:
- Proper legal references
- Flight details
- Calculated compensation amounts
- Regulatory deadline references
- Bank details for payment
"""

from dataclasses import dataclass
from datetime import datetime
from string import Template
from typing import Optional, List
from pathlib import Path

from compensation_calculator import (
    CompensationResult, FlightDetails, ClaimType,
    get_distance_category
)


@dataclass
class PassengerInfo:
    """Passenger information for claim."""
    first_name: str
    last_name: str
    date_of_birth: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


@dataclass
class BankDetails:
    """Bank account details for compensation payment."""
    account_holder: str
    iban: str
    bic_swift: Optional[str] = None
    bank_name: Optional[str] = None


@dataclass
class ClaimEmailData:
    """All data needed to generate a claim email."""
    passengers: List[PassengerInfo]
    flight: FlightDetails
    compensation: CompensationResult
    booking_reference: str
    bank_details: Optional[BankDetails] = None
    additional_notes: Optional[str] = None


# Email templates
DELAY_TEMPLATE = """Subject: EC261/2004 Compensation Claim - Flight $flight_number on $flight_date - Booking Ref: $booking_reference

Dear Sir/Madam,

RE: FORMAL CLAIM FOR COMPENSATION UNDER REGULATION (EC) NO. 261/2004
Booking Reference: $booking_reference
Flight Number: $flight_number
Date of Travel: $flight_date

I am writing to formally claim compensation under Regulation (EC) No. 261/2004 of the European Parliament and of the Council of 11 February 2004 establishing common rules on compensation and assistance to passengers in the event of denied boarding and of cancellation or long delay of flights.

FLIGHT DETAILS:
- Flight Number: $flight_number
- Date: $flight_date
- Route: $departure_airport ($departure_code) → $arrival_airport ($arrival_code)
- Scheduled Departure: $scheduled_departure
- Scheduled Arrival: $scheduled_arrival
- Actual Arrival: $actual_arrival
- Delay at Destination: $delay_hours hours
- Distance: $distance_km km ($distance_category)

PASSENGER DETAILS:
$passenger_details

LEGAL BASIS:
Under $legal_basis, passengers are entitled to compensation when their flight arrives at the final destination with a delay of three hours or more, unless the delay was caused by extraordinary circumstances.

The flight distance of $distance_km km and the delay of $delay_hours hours entitles each passenger to compensation of €$compensation_amount.

TOTAL COMPENSATION CLAIMED: €$total_compensation for $passenger_count passenger(s)

PAYMENT DETAILS:
$payment_details

REGULATORY REQUIREMENTS:
Under Article 14 of Regulation (EC) No. 261/2004, I remind you of your obligation to inform passengers of their rights. I expect a substantive response within 7 days in accordance with good industry practice, failing which I reserve the right to:

1. Submit a complaint to the relevant National Enforcement Body
2. Pursue the matter through the Alternative Dispute Resolution (ADR) scheme
3. Initiate court proceedings for recovery of the compensation, plus interest and costs

I also request written confirmation of:
1. Receipt of this claim
2. The reason for the delay
3. The timeline for processing this compensation claim

I trust you will handle this matter promptly and in accordance with European law.

Yours faithfully,

$primary_passenger_name
$contact_details

$additional_notes

---
Enclosures:
- Copy of booking confirmation
- Copy of boarding pass(es)
- Copy of passport/ID (if required)

Claim Reference: EC261-$claim_reference
Date of Claim: $claim_date
"""

CANCELLATION_TEMPLATE = """Subject: EC261/2004 Compensation Claim - CANCELLED Flight $flight_number on $flight_date - Booking Ref: $booking_reference

Dear Sir/Madam,

RE: FORMAL CLAIM FOR COMPENSATION UNDER REGULATION (EC) NO. 261/2004 - FLIGHT CANCELLATION
Booking Reference: $booking_reference
Flight Number: $flight_number
Date of Scheduled Travel: $flight_date

I am writing to formally claim compensation under Regulation (EC) No. 261/2004 of the European Parliament and of the Council of 11 February 2004 following the cancellation of my flight.

CANCELLED FLIGHT DETAILS:
- Flight Number: $flight_number
- Scheduled Date: $flight_date
- Route: $departure_airport ($departure_code) → $arrival_airport ($arrival_code)
- Scheduled Departure: $scheduled_departure
- Scheduled Arrival: $scheduled_arrival
- Distance: $distance_km km ($distance_category)
- Status: CANCELLED

PASSENGER DETAILS:
$passenger_details

LEGAL BASIS:
Under Article 5 and Article 7 of Regulation (EC) No. 261/2004, passengers are entitled to compensation when their flight is cancelled, unless:
(a) They were informed of the cancellation at least 14 days before the scheduled departure; or
(b) The cancellation was caused by extraordinary circumstances which could not have been avoided even if all reasonable measures had been taken.

Based on the flight distance of $distance_km km, each passenger is entitled to compensation of €$compensation_amount under $legal_basis.

TOTAL COMPENSATION CLAIMED: €$total_compensation for $passenger_count passenger(s)

PAYMENT DETAILS:
$payment_details

I hereby confirm that:
1. I was not informed of this cancellation at least 14 days prior to the scheduled departure
2. I was not offered re-routing that would have allowed me to depart no more than one hour before the originally scheduled departure and reach my final destination less than two hours after the originally scheduled arrival

REQUEST FOR INFORMATION:
Under Article 5(3), please provide documentary evidence if you intend to claim this cancellation was due to extraordinary circumstances. I remind you that operational issues, technical problems, and crew shortages do not constitute extraordinary circumstances under established ECJ case law.

I expect a substantive response within 7 days. Failing a satisfactory response, I reserve the right to pursue this matter through the relevant National Enforcement Body, ADR schemes, or court proceedings.

Yours faithfully,

$primary_passenger_name
$contact_details

$additional_notes

---
Enclosures:
- Copy of booking confirmation
- Evidence of cancellation notification (if any)
- Copy of passport/ID (if required)

Claim Reference: EC261-$claim_reference
Date of Claim: $claim_date
"""

DENIED_BOARDING_TEMPLATE = """Subject: EC261/2004 Compensation Claim - DENIED BOARDING - Flight $flight_number on $flight_date - Booking Ref: $booking_reference

Dear Sir/Madam,

RE: FORMAL CLAIM FOR COMPENSATION UNDER REGULATION (EC) NO. 261/2004 - DENIED BOARDING
Booking Reference: $booking_reference
Flight Number: $flight_number
Date of Travel: $flight_date

I am writing to formally claim compensation under Regulation (EC) No. 261/2004 following my denial of boarding on the above flight.

FLIGHT DETAILS:
- Flight Number: $flight_number
- Date: $flight_date
- Route: $departure_airport ($departure_code) → $arrival_airport ($arrival_code)
- Scheduled Departure: $scheduled_departure
- Distance: $distance_km km ($distance_category)
- Status: DENIED BOARDING

PASSENGER DETAILS:
$passenger_details

CIRCUMSTANCES OF DENIED BOARDING:
I presented myself for check-in/boarding in compliance with the conditions indicated in my booking confirmation and within the required time limits. Despite having a valid, confirmed booking, I was denied boarding against my will.

I hereby confirm that I:
1. Had a valid, confirmed booking for this flight
2. Presented myself at check-in/the boarding gate by the deadline specified
3. Was not under the influence of alcohol or drugs
4. Had valid travel documentation
5. Did not voluntarily surrender my seat in exchange for benefits

LEGAL BASIS:
Under Article 4 and Article 7 of Regulation (EC) No. 261/2004, passengers who are denied boarding against their will are entitled to immediate compensation, regardless of the reason for overbooking.

Based on the flight distance of $distance_km km, each passenger is entitled to compensation of €$compensation_amount under $legal_basis.

TOTAL COMPENSATION CLAIMED: €$total_compensation for $passenger_count passenger(s)

In addition to the above compensation, I also claim reimbursement for the following additional costs incurred as a result of the denied boarding:
[Please itemize any additional expenses such as meals, accommodation, transport]

PAYMENT DETAILS:
$payment_details

I expect immediate payment of the compensation as required under the Regulation. Please respond within 7 days confirming payment arrangements.

Yours faithfully,

$primary_passenger_name
$contact_details

$additional_notes

---
Enclosures:
- Copy of booking confirmation
- Copy of boarding pass (if issued)
- Receipts for additional expenses (if applicable)
- Copy of passport/ID

Claim Reference: EC261-$claim_reference
Date of Claim: $claim_date
"""

MISSED_CONNECTION_TEMPLATE = """Subject: EC261/2004 Compensation Claim - MISSED CONNECTION - Flight $flight_number on $flight_date - Booking Ref: $booking_reference

Dear Sir/Madam,

RE: FORMAL CLAIM FOR COMPENSATION UNDER REGULATION (EC) NO. 261/2004 - MISSED CONNECTION
Booking Reference: $booking_reference
Original Flight Number: $flight_number
Date of Travel: $flight_date

I am writing to formally claim compensation under Regulation (EC) No. 261/2004 following a missed connection caused by the delay of my initial flight.

DELAYED FLIGHT DETAILS:
- Flight Number: $flight_number
- Date: $flight_date
- Route: $departure_airport ($departure_code) → $arrival_airport ($arrival_code)
- Scheduled Departure: $scheduled_departure
- Scheduled Arrival: $scheduled_arrival
- Actual Arrival: $actual_arrival
- Delay: $delay_hours hours

Due to this delay, I missed my connecting flight and arrived at my final destination with a delay of $delay_hours hours.

PASSENGER DETAILS:
$passenger_details

LEGAL BASIS:
Under the ECJ ruling in Case C-11/11 (Folkerts v Air France) and subsequent case law, passengers on connecting flights booked under a single booking who arrive at their final destination with a delay of three hours or more are entitled to compensation under Regulation (EC) No. 261/2004.

The combined flight distance to my final destination is $distance_km km, and the delay at final destination of $delay_hours hours entitles each passenger to compensation of €$compensation_amount under $legal_basis.

TOTAL COMPENSATION CLAIMED: €$total_compensation for $passenger_count passenger(s)

PAYMENT DETAILS:
$payment_details

I expect a substantive response within 7 days. Should you dispute this claim or fail to respond, I reserve the right to pursue the matter through the relevant National Enforcement Body, ADR schemes, or court proceedings.

Yours faithfully,

$primary_passenger_name
$contact_details

$additional_notes

---
Enclosures:
- Copy of booking confirmation showing all flight segments
- Copies of boarding passes
- Copy of passport/ID

Claim Reference: EC261-$claim_reference
Date of Claim: $claim_date
"""


def get_template(claim_type: ClaimType) -> str:
    """Get the appropriate email template for the claim type."""
    templates = {
        ClaimType.DELAY: DELAY_TEMPLATE,
        ClaimType.CANCELLATION: CANCELLATION_TEMPLATE,
        ClaimType.DENIED_BOARDING: DENIED_BOARDING_TEMPLATE,
        ClaimType.MISSED_CONNECTION: MISSED_CONNECTION_TEMPLATE,
    }
    return templates.get(claim_type, DELAY_TEMPLATE)


def format_passenger_details(passengers: List[PassengerInfo]) -> str:
    """Format passenger list for email."""
    lines = []
    for i, p in enumerate(passengers, 1):
        line = f"{i}. {p.first_name} {p.last_name}"
        if p.date_of_birth:
            line += f" (DOB: {p.date_of_birth})"
        lines.append(line)
    return '\n'.join(lines)


def format_payment_details(bank: Optional[BankDetails]) -> str:
    """Format bank details for email."""
    if not bank:
        return "Please transfer the compensation to the following account:\n[Please provide bank details]"

    lines = [
        "Please transfer the compensation to the following account:",
        f"Account Holder: {bank.account_holder}",
        f"IBAN: {bank.iban}",
    ]
    if bank.bic_swift:
        lines.append(f"BIC/SWIFT: {bank.bic_swift}")
    if bank.bank_name:
        lines.append(f"Bank: {bank.bank_name}")

    return '\n'.join(lines)


def format_contact_details(passenger: PassengerInfo) -> str:
    """Format contact details for email signature."""
    lines = []
    if passenger.email:
        lines.append(f"Email: {passenger.email}")
    if passenger.phone:
        lines.append(f"Phone: {passenger.phone}")
    if passenger.address:
        lines.append(f"Address: {passenger.address}")
    return '\n'.join(lines) if lines else ""


def generate_claim_reference(flight: FlightDetails, booking_ref: str) -> str:
    """Generate a unique claim reference."""
    date_str = flight.scheduled_departure.strftime('%Y%m%d')
    return f"{flight.flight_number}-{date_str}-{booking_ref[:6].upper()}"


def generate_claim_email(data: ClaimEmailData) -> str:
    """
    Generate a complete compensation claim email.

    Args:
        data: ClaimEmailData containing all necessary information

    Returns:
        Formatted email text ready to send
    """
    template = Template(get_template(data.compensation.claim_type))

    # Calculate total compensation
    total_compensation = data.compensation.amount * len(data.passengers)

    # Format dates and times
    flight_date = data.flight.scheduled_departure.strftime('%d %B %Y')
    scheduled_departure = data.flight.scheduled_departure.strftime('%H:%M')
    scheduled_arrival = data.flight.scheduled_arrival.strftime('%H:%M')

    actual_arrival = "N/A"
    if data.flight.actual_arrival:
        actual_arrival = data.flight.actual_arrival.strftime('%H:%M on %d %B %Y')

    # Determine distance category
    is_intra_eu = (
        data.flight.departure_airport.is_eu and
        data.flight.arrival_airport.is_eu
    )
    distance_category = get_distance_category(
        data.compensation.distance_km, is_intra_eu
    )

    # Primary passenger for signature
    primary = data.passengers[0]

    # Build substitution dictionary
    substitutions = {
        'flight_number': data.flight.flight_number,
        'flight_date': flight_date,
        'booking_reference': data.booking_reference,
        'departure_airport': data.flight.departure_airport.name,
        'departure_code': data.flight.departure_airport.code,
        'arrival_airport': data.flight.arrival_airport.name,
        'arrival_code': data.flight.arrival_airport.code,
        'scheduled_departure': scheduled_departure,
        'scheduled_arrival': scheduled_arrival,
        'actual_arrival': actual_arrival,
        'delay_hours': f"{data.compensation.delay_hours:.1f}",
        'distance_km': f"{data.compensation.distance_km:,}",
        'distance_category': distance_category,
        'passenger_details': format_passenger_details(data.passengers),
        'passenger_count': len(data.passengers),
        'legal_basis': data.compensation.legal_basis,
        'compensation_amount': data.compensation.amount,
        'total_compensation': total_compensation,
        'payment_details': format_payment_details(data.bank_details),
        'primary_passenger_name': f"{primary.first_name} {primary.last_name}",
        'contact_details': format_contact_details(primary),
        'claim_reference': generate_claim_reference(
            data.flight, data.booking_reference
        ),
        'claim_date': datetime.now().strftime('%d %B %Y'),
        'additional_notes': data.additional_notes or "",
    }

    return template.safe_substitute(substitutions)


def generate_subject_line(data: ClaimEmailData) -> str:
    """Generate email subject line."""
    claim_type_labels = {
        ClaimType.DELAY: "Delay",
        ClaimType.CANCELLATION: "Cancellation",
        ClaimType.DENIED_BOARDING: "Denied Boarding",
        ClaimType.MISSED_CONNECTION: "Missed Connection",
    }

    claim_label = claim_type_labels.get(
        data.compensation.claim_type, "Compensation"
    )
    flight_date = data.flight.scheduled_departure.strftime('%d %b %Y')

    return (
        f"EC261/2004 Compensation Claim - {claim_label} - "
        f"Flight {data.flight.flight_number} on {flight_date} - "
        f"Booking Ref: {data.booking_reference}"
    )


def get_email_body_only(data: ClaimEmailData) -> str:
    """Get email body without subject line (for use in email clients)."""
    full_email = generate_claim_email(data)
    # Remove the subject line (first two lines)
    lines = full_email.split('\n')
    # Find where the body starts (after "Subject:" line and blank line)
    body_start = 0
    for i, line in enumerate(lines):
        if line.startswith('Dear'):
            body_start = i
            break
    return '\n'.join(lines[body_start:])
