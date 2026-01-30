"""
Airline Contact Information

Contact details for major airlines for filing EC261/2004 compensation claims.
Includes customer service emails, claim portals, and mailing addresses.
"""

from dataclasses import dataclass
from typing import Optional, List


@dataclass
class AirlineContact:
    """Airline contact information for claims."""
    code: str
    name: str
    email: Optional[str]
    claims_url: Optional[str]
    address: Optional[str]
    phone: Optional[str]
    country: str
    notes: Optional[str] = None


# Airline contact database
AIRLINE_CONTACTS = {
    # Lufthansa Group
    'LH': AirlineContact(
        code='LH',
        name='Lufthansa',
        email='customer.relations@lufthansa.com',
        claims_url='https://www.lufthansa.com/feedback',
        address='Lufthansa German Airlines, Customer Relations, PO Box 710234, 60492 Frankfurt, Germany',
        phone='+49 69 86 799 799',
        country='Germany',
        notes='Online form preferred. Response typically within 4-6 weeks.'
    ),
    'LX': AirlineContact(
        code='LX',
        name='Swiss International Air Lines',
        email='customer.relations@swiss.com',
        claims_url='https://www.swiss.com/feedback',
        address='Swiss International Air Lines Ltd., Customer Relations, P.O. Box, 4002 Basel, Switzerland',
        phone='+41 848 700 700',
        country='Switzerland'
    ),
    'OS': AirlineContact(
        code='OS',
        name='Austrian Airlines',
        email='customer.relations@austrian.com',
        claims_url='https://www.austrian.com/feedback',
        address='Austrian Airlines, Customer Relations, P.O. Box 50, 1300 Vienna Airport, Austria',
        phone='+43 5 1766 1000',
        country='Austria'
    ),
    'SN': AirlineContact(
        code='SN',
        name='Brussels Airlines',
        email='customerrelations@brusselsairlines.com',
        claims_url='https://www.brusselsairlines.com/feedback',
        address='Brussels Airlines, Customer Relations, Airport Building 26, 1820 Steenokkerzeel, Belgium',
        phone='+32 2 723 2323',
        country='Belgium'
    ),

    # Air France-KLM Group
    'AF': AirlineContact(
        code='AF',
        name='Air France',
        email='mail.customercare@airfrance.fr',
        claims_url='https://www.airfrance.com/claim',
        address='Air France, Customer Relations, 45 rue de Paris, 95747 Roissy CDG Cedex, France',
        phone='+33 9 69 39 02 15',
        country='France',
        notes='Claims can be filed online. 28-day response requirement under French law.'
    ),
    'KL': AirlineContact(
        code='KL',
        name='KLM Royal Dutch Airlines',
        email='customercare@klm.com',
        claims_url='https://www.klm.com/feedback',
        address='KLM Customer Care, P.O. Box 7700, 1117 ZL Schiphol, Netherlands',
        phone='+31 20 474 7747',
        country='Netherlands'
    ),

    # IAG Group
    'BA': AirlineContact(
        code='BA',
        name='British Airways',
        email='customer.relations@ba.com',
        claims_url='https://www.britishairways.com/travel/customerservice',
        address='British Airways Customer Relations, PO Box 5619, Sudbury, Suffolk CO10 2PG, United Kingdom',
        phone='+44 344 493 0787',
        country='United Kingdom',
        notes='UK261 applies for post-Brexit flights. Online claim form available.'
    ),
    'IB': AirlineContact(
        code='IB',
        name='Iberia',
        email='customer.relations@iberia.com',
        claims_url='https://www.iberia.com/claims',
        address='Iberia, Customer Relations, C/ Martinez Villergas 49, 28027 Madrid, Spain',
        phone='+34 901 111 500',
        country='Spain'
    ),
    'VY': AirlineContact(
        code='VY',
        name='Vueling',
        email='customercare@vueling.com',
        claims_url='https://www.vueling.com/en/we-are-vueling/contact-us',
        address='Vueling Airlines S.A., Customer Relations, Parque de Negocios Mas Blau II, Pla de lEstany 5, 08820 El Prat de Llobregat, Spain',
        phone='+34 931 518 158',
        country='Spain'
    ),

    # Low-cost carriers
    'FR': AirlineContact(
        code='FR',
        name='Ryanair',
        email='customerqueries@ryanair.com',
        claims_url='https://www.ryanair.com/eu261',
        address='Ryanair Customer Service, PO Box 11451, Swords, Co Dublin, Ireland',
        phone='+353 1 249 7791',
        country='Ireland',
        notes='Online claim form required. Known for lengthy dispute process.'
    ),
    'U2': AirlineContact(
        code='U2',
        name='easyJet',
        email='customerservice@easyjet.com',
        claims_url='https://www.easyjet.com/en/claim',
        address='easyJet Customer Services, Hangar 89, London Luton Airport, Luton LU2 9PF, United Kingdom',
        phone='+44 330 365 5000',
        country='United Kingdom',
        notes='Online claim portal available. Response within 28 days.'
    ),
    'EZY': AirlineContact(
        code='EZY',
        name='easyJet',
        email='customerservice@easyjet.com',
        claims_url='https://www.easyjet.com/en/claim',
        address='easyJet Customer Services, Hangar 89, London Luton Airport, Luton LU2 9PF, United Kingdom',
        phone='+44 330 365 5000',
        country='United Kingdom'
    ),
    'W6': AirlineContact(
        code='W6',
        name='Wizz Air',
        email='complaints@wizzair.com',
        claims_url='https://wizzair.com/en-gb/information-and-services/complaints',
        address='Wizz Air Hungary Ltd., Budapest Airport, Building 221, 1185 Budapest, Hungary',
        phone='+36 1 777 9444',
        country='Hungary'
    ),

    # Scandinavian carriers
    'SK': AirlineContact(
        code='SK',
        name='SAS Scandinavian Airlines',
        email='customer.relations@sas.se',
        claims_url='https://www.flysas.com/en/customer-service/claims/',
        address='SAS Customer Relations, SE-195 87 Stockholm, Sweden',
        phone='+46 770 727 727',
        country='Sweden'
    ),
    'AY': AirlineContact(
        code='AY',
        name='Finnair',
        email='customer.relations@finnair.com',
        claims_url='https://www.finnair.com/feedback',
        address='Finnair Customer Care, P.O. Box 15, 01053 FINNAIR, Finland',
        phone='+358 9 818 0800',
        country='Finland'
    ),
    'DY': AirlineContact(
        code='DY',
        name='Norwegian Air Shuttle',
        email='customer@norwegian.com',
        claims_url='https://www.norwegian.com/en/customer-service/',
        address='Norwegian Air Shuttle ASA, P.O. Box 115, 1330 Fornebu, Norway',
        phone='+47 21 49 00 15',
        country='Norway'
    ),

    # Southern European carriers
    'AZ': AirlineContact(
        code='AZ',
        name='ITA Airways',
        email='customercare@ita-airways.com',
        claims_url='https://www.ita-airways.com/en/contacts',
        address='ITA Airways, Customer Relations, Via Alberto Nassetti, Palazzina Alfa, 00054 Fiumicino (RM), Italy',
        phone='+39 06 8560 8560',
        country='Italy'
    ),
    'TP': AirlineContact(
        code='TP',
        name='TAP Air Portugal',
        email='customercare@tap.pt',
        claims_url='https://www.flytap.com/en-pt/support/complaints',
        address='TAP Portugal, Customer Relations, Aeroporto de Lisboa, 1704-801 Lisboa, Portugal',
        phone='+351 211 234 400',
        country='Portugal'
    ),
    'A3': AirlineContact(
        code='A3',
        name='Aegean Airlines',
        email='customercare@aegeanair.com',
        claims_url='https://www.aegeanair.com/contact-us/',
        address='Aegean Airlines, Customer Relations, 31 Viltanioti Street, 145 64 Kifisia, Greece',
        phone='+30 210 626 1000',
        country='Greece'
    ),

    # Irish carrier
    'EI': AirlineContact(
        code='EI',
        name='Aer Lingus',
        email='customerrelations@aerlingus.com',
        claims_url='https://www.aerlingus.com/support/contact-us/',
        address='Aer Lingus, Customer Relations, Dublin Airport, Dublin, Ireland',
        phone='+353 1 886 8989',
        country='Ireland'
    ),

    # Eastern European carriers
    'LO': AirlineContact(
        code='LO',
        name='LOT Polish Airlines',
        email='customer@lot.pl',
        claims_url='https://www.lot.com/contact-center',
        address='LOT Polish Airlines, Customer Relations, ul. Komitetu Obrony Robotnikow 43, 02-146 Warsaw, Poland',
        phone='+48 22 577 7755',
        country='Poland'
    ),
    'BT': AirlineContact(
        code='BT',
        name='Air Baltic',
        email='feedback@airbaltic.com',
        claims_url='https://www.airbaltic.com/feedback',
        address='Air Baltic Corporation, Tehnikas iela 3, Marupe, LV-2167, Latvia',
        phone='+371 67 006 006',
        country='Latvia'
    ),
    'OK': AirlineContact(
        code='OK',
        name='Czech Airlines',
        email='customer.relations@csa.cz',
        claims_url='https://www.csa.cz/en/contact/',
        address='Czech Airlines, Customer Relations, K letišti 1068/30, 160 08 Prague 6, Czech Republic',
        phone='+420 239 007 007',
        country='Czech Republic'
    ),

    # German carriers
    'EW': AirlineContact(
        code='EW',
        name='Eurowings',
        email='kundenservice@eurowings.com',
        claims_url='https://www.eurowings.com/en/contact.html',
        address='Eurowings GmbH, Customer Relations, Germanwingsstraße 2, 51147 Cologne, Germany',
        phone='+49 221 599 888 99',
        country='Germany'
    ),

    # Turkish carrier (important for EU routes)
    'TK': AirlineContact(
        code='TK',
        name='Turkish Airlines',
        email='customer@thy.com',
        claims_url='https://www.turkishairlines.com/en-int/any-questions/feedback/',
        address='Turkish Airlines, Customer Relations, Ataturk Havalimani, Yesilkoy 34149, Istanbul, Turkey',
        phone='+90 212 444 0 849',
        country='Turkey',
        notes='EC261 applies only for EU departures. Different rules for Turkey departures.'
    ),

    # Major non-EU carriers (for EU departures)
    'EK': AirlineContact(
        code='EK',
        name='Emirates',
        email='customeraffairs@emirates.com',
        claims_url='https://www.emirates.com/feedback',
        address='Emirates Customer Affairs, P.O. Box 686, Dubai, United Arab Emirates',
        phone='+971 600 555 555',
        country='UAE',
        notes='EC261 applies only for EU departures.'
    ),
    'QR': AirlineContact(
        code='QR',
        name='Qatar Airways',
        email='qrmediapersonaldata@qatarairways.com.qa',
        claims_url='https://www.qatarairways.com/en/contact.html',
        address='Qatar Airways, Customer Relations, P.O. Box 22550, Doha, Qatar',
        phone='+974 4449 6666',
        country='Qatar',
        notes='EC261 applies only for EU departures.'
    ),
    'AA': AirlineContact(
        code='AA',
        name='American Airlines',
        email='customer.relations@aa.com',
        claims_url='https://www.aa.com/contact/forms',
        address='American Airlines Customer Relations, 4000 E. Sky Harbor Blvd., Phoenix, AZ 85034, USA',
        phone='+1 800 433 7300',
        country='USA',
        notes='EC261 applies only for EU departures.'
    ),
    'UA': AirlineContact(
        code='UA',
        name='United Airlines',
        email='customercare@united.com',
        claims_url='https://www.united.com/contact',
        address='United Airlines Customer Care, 900 Grand Plaza Drive, Houston, TX 77067, USA',
        phone='+1 800 864 8331',
        country='USA',
        notes='EC261 applies only for EU departures.'
    ),
    'DL': AirlineContact(
        code='DL',
        name='Delta Air Lines',
        email='delta.feedback@delta.com',
        claims_url='https://www.delta.com/contactus',
        address='Delta Air Lines Customer Care, P.O. Box 20980, Atlanta, GA 30320-2980, USA',
        phone='+1 800 221 1212',
        country='USA',
        notes='EC261 applies only for EU departures.'
    ),
}


def get_airline_contact(airline_code: str) -> Optional[AirlineContact]:
    """Get contact information for an airline by IATA code."""
    return AIRLINE_CONTACTS.get(airline_code.upper())


def get_all_airlines() -> List[AirlineContact]:
    """Get list of all airlines in the database."""
    return list(AIRLINE_CONTACTS.values())


def search_airlines(query: str) -> List[AirlineContact]:
    """Search airlines by name or code."""
    query = query.upper()
    results = []
    for contact in AIRLINE_CONTACTS.values():
        if query in contact.code or query in contact.name.upper():
            results.append(contact)
    return results


def format_contact_for_display(contact: AirlineContact) -> str:
    """Format airline contact information for display."""
    lines = [
        f"Airline: {contact.name} ({contact.code})",
        f"Country: {contact.country}",
    ]

    if contact.email:
        lines.append(f"Email: {contact.email}")

    if contact.claims_url:
        lines.append(f"Claims Portal: {contact.claims_url}")

    if contact.phone:
        lines.append(f"Phone: {contact.phone}")

    if contact.address:
        lines.append(f"Address: {contact.address}")

    if contact.notes:
        lines.append(f"Notes: {contact.notes}")

    return '\n'.join(lines)
