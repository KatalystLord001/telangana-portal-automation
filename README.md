# Telangana Portal Automation

Standalone Python automation for Telangana CCLA and Registration & Stamps portals.

## Features

- **CCLA Portal**: Land Status / Pahani & ROR-1B search
- **Registration Portal**: EC (Encumbrance Certificate) search with login

## Requirements

- Python 3.8+
- Chrome/Chromium browser

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

## Configuration

Create a `.env` file:

```bash
GEMINI_API_KEY=your-gemini-api-key-here
```

## Usage

### CCLA Portal

```bash
# Basic search
python ccla_search.py --district 31 --division 67 --mandal 609 --village 3111005 --buyer "Kumar" --seller "Reddy"

# Survey number search
python ccla_search.py --district 31 --division 67 --mandal 609 --village 3111005 --mode survey

# Headless mode
python ccla_search.py --district 31 --division 67 --mandal 609 --village 3111005 --buyer "Kumar" --headless
```

### Registration Portal

```bash
# Document search
python registration_search.py --doc 1234 --year 2024 --sro "HYDERABAD (R.O)"

# With custom credentials
python registration_search.py --doc 1234 --year 2024 --sro "HYDERABAD" --username "7011590660" --password "Aarav@123"

# Headless mode
python registration_search.py --doc 1234 --year 2024 --sro "HYDERABAD" --headless
```

## Output

Both scripts generate:
- **PNG screenshots** - Full page captures
- **PDF files** - Printable reports (headless mode only)
- **HTML files** - Complete page source
- **JSON results** - Structured data

Files are saved in the `output/` directory with timestamps.

## Examples

```bash
# CCLA - Search by buyer/seller name
python ccla_search.py --district 31 --division 67 --mandal 609 --village 3111005 --buyer "Ramesh" --seller "Suresh"

# Registration - EC search
python registration_search.py --doc 5678 --year 2023 --sro "HYDERABAD (R.O)"
```

## Troubleshooting

### CAPTCHA Issues
- CCLA: Uses DOM extraction (no API key needed)
- Registration: Requires Gemini API key in `.env`

### Portal Down
If portal is unavailable, you'll see timeout errors. Try again later.

### Browser Not Found
Run: `playwright install chromium`

## Support

For issues, check:
1. Internet connection
2. Portal availability
3. Gemini API key (for Registration portal)
4. Chrome/Chromium installation
