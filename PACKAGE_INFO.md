# Telangana Portal Automation Package

## 📦 Package Contents

This standalone Python package provides complete automation for two Telangana government portals:

### 1. CCLA Portal (Land Status / Pahani & ROR-1B)
- **URL**: https://ccla.telangana.gov.in/landStatus.done
- **Features**:
  - Cascading dropdown navigation (District → Division → Mandal → Village)
  - Multiple search modes: Khata No, Survey No, Buyer/Seller Name, Mutation Date
  - Automatic CAPTCHA solving (DOM extraction - no API key needed)
  - Full page screenshots, HTML export
  - JSON structured results

### 2. Registration & Stamps Portal (EC Search)
- **URL**: https://registration.telangana.gov.in/
- **Features**:
  - Automatic login with credentials
  - CAPTCHA solving using Gemini AI
  - Complete 5-step EC search flow
  - Document number search
  - Downloadable results: PNG, PDF, HTML, JSON
  - Session management with cookie persistence

## 📁 File Structure

```
telangana-automation/
├── README.md                    # Main documentation
├── INSTALL.md                   # Installation guide
├── PACKAGE_INFO.md             # This file
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
├── quick_start.sh              # Quick setup script (Linux/Mac)
├── quick_start.bat             # Quick setup script (Windows)
├── ccla_search.py              # CCLA portal automation
├── registration_search.py      # Registration portal automation
├── test_both.py                # Test script for both portals
└── output/                     # Results directory (created automatically)
```

## 🚀 Quick Start

### Linux/Mac:
```bash
chmod +x quick_start.sh
./quick_start.sh
```

### Windows:
```cmd
quick_start.bat
```

### Manual Setup:
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Install browsers
playwright install chromium

# 3. Configure environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# 4. Test
python test_both.py
```

## 💡 Usage Examples

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

## 📊 Output Files

Both scripts generate timestamped files in the `output/` directory:

### CCLA Output:
- `ccla_YYYYMMDD_HHMMSS.png` - Full page screenshot
- `ccla_YYYYMMDD_HHMMSS.html` - Complete HTML source
- `ccla_YYYYMMDD_HHMMSS.json` - Structured results

### Registration Output:
- `ts_reg_ec_report_YYYYMMDD_HHMMSS.png` - Screenshot
- `ts_reg_ec_report_YYYYMMDD_HHMMSS.pdf` - PDF report (headless only)
- `ts_reg_ec_report_YYYYMMDD_HHMMSS.html` - HTML source
- `ts_reg_ec_report_YYYYMMDD_HHMMSS.json` - Structured data
- `ts_reg_step1_form_*.png` - Step-by-step screenshots
- `ts_reg_step2_dates_*.png`
- `ts_reg_step3_documents_*.png`
- `ts_reg_step4_selected_*.png`

## 🔑 API Keys

### Gemini API Key (Required for Registration Portal)

1. Visit: https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy key to `.env` file:
   ```
   GEMINI_API_KEY=your-key-here
   ```

**Note**: CCLA portal doesn't need an API key (uses DOM extraction for CAPTCHA).

## ⚙️ Configuration

### Environment Variables (.env)

```bash
# Required for Registration portal
GEMINI_API_KEY=your-gemini-api-key

# Optional: Default credentials for Registration portal
TS_REG_USERNAME=7011590660
TS_REG_PASSWORD=Aarav@123
```

### Command Line Options

#### CCLA Portal:
```
--district    District code (required)
--division    Division code (required)
--mandal      Mandal code (required)
--village     Village code (required)
--mode        Search mode: khataNo, surveyNo, buyerSeller, mutationDate
--buyer       Buyer name (for buyerSeller mode)
--seller      Seller name (for buyerSeller mode)
--headless    Run without browser window
--output      Output directory (default: output)
```

#### Registration Portal:
```
--doc         Document number (required)
--year        Year of registration (required)
--sro         SRO name (required)
--username    Login username (optional)
--password    Login password (optional)
--headless    Run without browser window
--output      Output directory (default: output)
```

## 🐛 Troubleshooting

### Common Issues

1. **"playwright: command not found"**
   ```bash
   pip install playwright
   playwright install chromium
   ```

2. **"GEMINI_API_KEY not found"**
   - Create `.env` file with your API key
   - Only needed for Registration portal

3. **Portal timeout**
   - Portal might be temporarily down
   - Check internet connection
   - Try again later

4. **CAPTCHA solving fails**
   - Registration: Check Gemini API key is valid
   - CCLA: Should work automatically (DOM extraction)

5. **Login fails**
   - Check credentials in `.env` or command line
   - Portal might have changed login flow

### Debug Mode

Run with browser visible (remove `--headless`) to see what's happening:

```bash
# CCLA
python ccla_search.py --district 31 --division 67 --mandal 609 --village 3111005 --buyer Kumar

# Registration
python registration_search.py --doc 1234 --year 2024 --sro "HYDERABAD"
```

## 📋 Requirements

- **Python**: 3.8 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Disk**: 500MB for dependencies
- **Internet**: Stable connection required
- **OS**: Windows, macOS, or Linux

## 🔒 Security Notes

- Store API keys in `.env` file (never commit to git)
- `.env` is in `.gitignore` by default
- Credentials are only used for portal login
- No data is sent to third parties except:
  - Gemini AI (for CAPTCHA solving in Registration portal)
  - Government portals (for searches)

## 📝 License

This automation tool is provided as-is for legitimate use with Telangana government portals. Users are responsible for complying with portal terms of service.

## 🤝 Support

For issues:
1. Check INSTALL.md for setup help
2. Review troubleshooting section above
3. Verify portal is accessible in browser
4. Check Python and dependency versions

## 🎯 Testing

Run the test suite to verify everything works:

```bash
python test_both.py
```

This will:
- Test CCLA portal with sample search
- Test Registration portal with sample search
- Create output files in `test_output/` directory
- Report success/failure for each portal

## 📦 Dependencies

- `playwright==1.40.0` - Browser automation
- `python-dotenv==1.0.0` - Environment variables
- `google-generativeai==0.3.2` - Gemini AI for CAPTCHA

All dependencies are listed in `requirements.txt`.

## 🚀 Production Use

For production/automated use:

1. **Use headless mode**: Add `--headless` flag
2. **Set timeouts**: Portals can be slow, allow 60-90 seconds
3. **Handle errors**: Both scripts return structured results
4. **Rate limiting**: Don't hammer portals, add delays between searches
5. **Logging**: Redirect output to log files for monitoring

Example production command:
```bash
python ccla_search.py \
  --district 31 \
  --division 67 \
  --mandal 609 \
  --village 3111005 \
  --buyer "Kumar" \
  --seller "Reddy" \
  --headless \
  --output /var/log/ccla_results \
  >> /var/log/ccla.log 2>&1
```

## 📈 Performance

- **CCLA**: ~15-30 seconds per search
- **Registration**: ~30-60 seconds per search (includes login)
- **Headless mode**: Slightly faster than headed mode
- **Concurrent searches**: Not recommended (may trigger rate limiting)

## ✅ Verification

To verify the package is working:

1. Run quick start script
2. Check `output/` directory for generated files
3. Open PNG screenshots to verify results
4. Check JSON files for structured data

Both portals should complete successfully if:
- Dependencies are installed
- Gemini API key is configured (for Registration)
- Internet connection is stable
- Portals are accessible
