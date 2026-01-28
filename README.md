# 🏛️ Telangana Portal Automation

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Playwright](https://img.shields.io/badge/playwright-1.40+-green.svg)](https://playwright.dev/python/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Standalone Python automation for Telangana government portals using Playwright browser automation.

## ✨ Features

### 🌾 CCLA Portal (Land Status)
- **URL**: https://ccla.telangana.gov.in/landStatus.done
- Pahani & ROR-1B search automation
- Multiple search modes: Khata No, Survey No, Buyer/Seller Name, Mutation Date
- **Automatic CAPTCHA solving** (DOM extraction - no API key needed!)
- Cascading dropdown navigation (District → Division → Mandal → Village)
- Outputs: PNG screenshots, HTML source, JSON structured data

### 📜 Registration & Stamps Portal (EC Search)
- **URL**: https://registration.telangana.gov.in/
- Encumbrance Certificate (EC) search automation
- Automatic login with credentials
- CAPTCHA solving using Gemini AI
- Complete 5-step EC search flow
- Document number search
- Outputs: PNG, PDF, HTML, JSON with step-by-step debug screenshots

## 🚀 Quick Start

### Option 1: One-Command Setup (Recommended)

**Linux/Mac:**
```bash
git clone https://github.com/KatalystLord001/telangana-portal-automation.git
cd telangana-portal-automation
chmod +x quick_start.sh
./quick_start.sh
```

**Windows:**
```cmd
git clone https://github.com/KatalystLord001/telangana-portal-automation.git
cd telangana-portal-automation
quick_start.bat
```

### Option 2: Manual Setup

```bash
# 1. Clone repository
git clone https://github.com/KatalystLord001/telangana-portal-automation.git
cd telangana-portal-automation

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install Playwright browsers
playwright install chromium

# 4. Configure API key (for Registration portal only)
cp .env.example .env
# Edit .env and add: GEMINI_API_KEY=your-key-here

# 5. Test both portals
python test_both.py
```

## 📋 Requirements

- **Python**: 3.8 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Internet**: Stable connection required
- **OS**: Windows, macOS, or Linux

## ⚙️ Configuration

### For Registration Portal (Required)
Create a `.env` file with your Gemini API key:

```bash
GEMINI_API_KEY=your-gemini-api-key-here
```

**Get your API key**: https://makersuite.google.com/app/apikey

### For CCLA Portal
No API key needed! CAPTCHA is solved using DOM extraction.

## 📖 Usage Examples

### CCLA Portal

```bash
# Search by buyer/seller name
python ccla_search.py \
  --district 31 \
  --division 67 \
  --mandal 609 \
  --village 3111005 \
  --buyer "Ramesh Kumar" \
  --seller "Suresh Reddy"

# Search by survey number
python ccla_search.py \
  --district 31 \
  --division 67 \
  --mandal 609 \
  --village 3111005 \
  --mode surveyNo

# Headless mode (no browser window)
python ccla_search.py \
  --district 31 \
  --division 67 \
  --mandal 609 \
  --village 3111005 \
  --buyer "Kumar" \
  --headless
```

### Registration Portal

```bash
# Document search
python registration_search.py \
  --doc 1234 \
  --year 2024 \
  --sro "HYDERABAD (R.O)"

# With custom credentials
python registration_search.py \
  --doc 5678 \
  --year 2023 \
  --sro "HYDERABAD" \
  --username "your-username" \
  --password "your-password"

# Headless mode
python registration_search.py \
  --doc 1234 \
  --year 2024 \
  --sro "HYDERABAD" \
  --headless
```

## 📂 Output Files

All results are saved in the `output/` directory with timestamps:

### CCLA Output:
- `ccla_YYYYMMDD_HHMMSS.png` - Full page screenshot
- `ccla_YYYYMMDD_HHMMSS.html` - Complete HTML source
- `ccla_YYYYMMDD_HHMMSS.json` - Structured results data

### Registration Output:
- `ts_reg_ec_report_YYYYMMDD_HHMMSS.png` - Screenshot
- `ts_reg_ec_report_YYYYMMDD_HHMMSS.pdf` - PDF report (headless only)
- `ts_reg_ec_report_YYYYMMDD_HHMMSS.html` - HTML source
- `ts_reg_ec_report_YYYYMMDD_HHMMSS.json` - Structured data
- Plus step-by-step screenshots for debugging

## 🧪 Testing

Run the test suite to verify both portals work:

```bash
python test_both.py
```

This will:
- Test CCLA portal with sample search
- Test Registration portal with sample search
- Create output files in `test_output/` directory
- Report success/failure for each portal

## 🔧 Troubleshooting

### CAPTCHA Issues
- **CCLA**: Uses DOM extraction (no API key needed)
- **Registration**: Requires Gemini API key in `.env`

### Portal Down
If portal is unavailable, you'll see timeout errors. Try again later.

### Browser Not Found
```bash
playwright install chromium
```

### Import Errors
```bash
pip install -r requirements.txt
```

## 📚 Documentation

- **README.md** - This file (main user guide)
- **INSTALL.md** - Detailed installation instructions
- **PACKAGE_INFO.md** - Complete technical documentation
- **DELIVERY_NOTES.md** - Package highlights and delivery checklist
- **HANDOVER.md** - Quick handover summary

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This automation tool is for educational and research purposes only. Users are responsible for complying with the terms of service of the respective government portals.

## 🙏 Acknowledgments

- Built with [Playwright](https://playwright.dev/python/) for browser automation
- CAPTCHA solving powered by [Google Gemini AI](https://ai.google.dev/)
- Developed for efficient land record and registration searches

## 📞 Support

For issues or questions:
1. Check the documentation files
2. Run `python test_both.py` to verify installation
3. Use `--help` flag with any script for command options
4. Open an issue on GitHub

---

**Made with ❤️ for efficient government portal automation**
