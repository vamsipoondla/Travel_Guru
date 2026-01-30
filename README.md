# EU Flight Compensation Claim Generator

A Python application for generating professional compensation claim emails under EU Regulation EC261/2004 and similar regulations.

## Features

- **Compensation Eligibility Calculator**: Automatically determines if a flight qualifies for compensation based on:
  - Flight distance (short/medium/long-haul)
  - Delay duration at final destination
  - EU departure or EU arrival on EU carrier
  - Claim time limits

- **Compensation Tiers (EC261/2004)**:
  - €250 for flights ≤1,500 km with 3+ hour delay
  - €400 for intra-EU flights >1,500 km or other flights 1,500-3,500 km with 3+ hour delay
  - €600 for flights >3,500 km with 4+ hour delay (€300 if 3-4 hour delay)

- **Flight Data Lookup**: Optional integration with flight data APIs:
  - AviationStack API
  - FlightAware AeroAPI
  - Manual data entry fallback

- **Claim Types Supported**:
  - Flight delays (3+ hours)
  - Flight cancellations
  - Denied boarding
  - Missed connections

- **Professional Email Generation**:
  - Legally-formatted claim letters
  - Proper EC261/2004 article references
  - Multiple passenger support
  - Bank details for payment

- **Airline Contact Database**: Built-in contact information for 40+ airlines including:
  - Customer service emails
  - Claims portal URLs
  - Mailing addresses
  - Phone numbers

## Installation

### Prerequisites

- Python 3.8 or higher
- tkinter (usually included with Python, may need separate installation on Linux)

### Linux (Ubuntu/Debian)

```bash
# Install tkinter if not present
sudo apt-get install python3-tk

# Clone the repository
git clone https://github.com/yourusername/Travel_Guru.git
cd Travel_Guru

# Install dependencies
pip install -r requirements.txt
```

### macOS

```bash
# tkinter is included with Python on macOS
# Clone and install
git clone https://github.com/yourusername/Travel_Guru.git
cd Travel_Guru
pip install -r requirements.txt
```

### Windows

```bash
# tkinter is included with Python on Windows
# Clone and install
git clone https://github.com/yourusername/Travel_Guru.git
cd Travel_Guru
pip install -r requirements.txt
```

## Configuration

### API Keys (Optional)

To enable automatic flight data lookup, create a `config.yaml` file:

```bash
cp config.example.yaml config.yaml
```

Then edit `config.yaml` with your API keys:

```yaml
api:
  # AviationStack (https://aviationstack.com/)
  aviationstack_key: "your_api_key_here"

  # FlightAware AeroAPI (https://flightaware.com/aeroapi/)
  flightaware_key: "your_api_key_here"
  flightaware_username: "your_username_here"

# Optional settings
default_language: "en"
claim_years_limit: 6
```

Alternatively, set environment variables:

```bash
export AVIATIONSTACK_API_KEY="your_key"
export FLIGHTAWARE_API_KEY="your_key"
```

**Note**: The application works without API keys using manual data entry.

## Usage

### Running the Application

```bash
python main.py
```

### Step-by-Step Guide

1. **Flight Details Tab**:
   - Enter booking reference and travel date
   - Enter flight number (e.g., BA123)
   - Click "Look Up Flight" if API is configured, or enter details manually
   - Select departure and arrival airports
   - Enter scheduled and actual times
   - Select claim type (delay/cancellation/denied boarding)
   - Click "Calculate Compensation"

2. **Passengers Tab**:
   - Add all passengers from the booking
   - Enter name, date of birth, email, and contact details
   - Multiple passengers can be added to the same claim

3. **Exclusions Tab**:
   - Review extraordinary circumstances
   - Confirm the delay was not due to weather, ATC, strikes, etc.
   - Check the confirmation box to proceed

4. **Bank Details Tab** (Optional):
   - Enter IBAN and bank details for payment
   - Can be left blank and added to email manually

5. **Generate Email Tab**:
   - Click "Generate Claim Email"
   - Review the generated email
   - Copy to clipboard or save as text file
   - Open airline claims portal directly

## EC261/2004 Overview

### Eligibility Criteria

The regulation applies to:
- All flights departing from an EU/EEA airport (any airline)
- Flights arriving in EU/EEA on an EU-based carrier

### Compensation Amounts

| Distance | Delay | Amount |
|----------|-------|--------|
| ≤1,500 km | 3+ hours | €250 |
| 1,500-3,500 km or intra-EU >1,500 km | 3+ hours | €400 |
| >3,500 km | 3-4 hours | €300 |
| >3,500 km | 4+ hours | €600 |

### Extraordinary Circumstances (Exclusions)

Airlines may refuse compensation if caused by:
- Severe weather conditions
- Air traffic control restrictions
- Security threats
- Political instability
- Strikes (except airline staff)
- Medical emergencies

**Note**: Technical problems and crew shortages are generally NOT valid exclusions.

### Time Limits

Claim limitation periods vary by country:
- UK, Ireland, Luxembourg: 6 years
- France, Netherlands, Spain, Italy: 5 years
- Germany, Austria: 3 years
- Belgium: 1 year

## Project Structure

```
Travel_Guru/
├── main.py                    # Main application with Tkinter GUI
├── compensation_calculator.py # EC261/2004 compensation logic
├── flight_service.py          # Flight data API integration
├── email_generator.py         # Email template generation
├── airline_contacts.py        # Airline contact database
├── validators.py              # Input validation
├── config.py                  # Configuration management
├── config.example.yaml        # Example configuration file
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Supported Airlines

The application includes contact information for major airlines including:

**Lufthansa Group**: Lufthansa, Swiss, Austrian, Brussels Airlines
**Air France-KLM**: Air France, KLM
**IAG**: British Airways, Iberia, Vueling
**Low-cost**: Ryanair, easyJet, Wizz Air, Eurowings
**Scandinavian**: SAS, Finnair, Norwegian
**Others**: TAP Portugal, Aegean, Aer Lingus, LOT, and more

## Supported Airports

The application includes coordinates and country data for 40+ major airports including all major EU hubs and common international destinations.

## Troubleshooting

### "tkinter not found" Error

On Linux, install tkinter separately:

```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter

# Arch
sudo pacman -S tk
```

### Clipboard Not Working

Ensure `pyperclip` is installed:

```bash
pip install pyperclip
```

On Linux, you may also need `xclip` or `xsel`:

```bash
sudo apt-get install xclip
```

### API Lookup Not Working

- Verify API keys are correctly set in `config.yaml` or environment variables
- Check internet connection
- AviationStack free tier has daily request limits

## Legal Disclaimer

This application generates template claim letters based on EC261/2004 regulations. It is provided for informational purposes only and does not constitute legal advice. Users should verify:

- Their specific eligibility for compensation
- Current regulations and any updates
- Airline-specific procedures
- Local limitation periods

For complex cases or disputes, consider consulting a legal professional or using an established claims management service.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for:

- Additional airline contacts
- New airport data
- Bug fixes
- Feature enhancements
- Translation support

## License

This project is open source and available under the MIT License.

## Acknowledgments

- EU Regulation EC261/2004
- European Court of Justice case law (Sturgeon, Folkerts, etc.)
- Flight data provided by AviationStack and FlightAware APIs
