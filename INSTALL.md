# Installation Guide

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Chrome or Chromium browser

## Step-by-Step Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `playwright` - Browser automation
- `python-dotenv` - Environment variable management
- `google-generativeai` - Gemini AI for CAPTCHA solving

### 2. Install Playwright Browsers

```bash
playwright install chromium
```

This downloads the Chromium browser that Playwright will use.

### 3. Configure Environment Variables

Create a `.env` file in the `telangana-automation` directory:

```bash
cp .env.example .env
```

Edit `.env` and add your Gemini API key:

```
GEMINI_API_KEY=your-actual-api-key-here
```

**Note:** The Gemini API key is only required for the Registration portal (for CAPTCHA solving). The CCLA portal works without it.

### 4. Verify Installation

Run the test script to verify everything works:

```bash
python test_both.py
```

This will test both portals and create output files in the `test_output/` directory.

## Troubleshooting

### "playwright: command not found"

Make sure Playwright is installed:
```bash
pip install playwright
playwright install chromium
```

### "GEMINI_API_KEY not found"

Create a `.env` file with your API key:
```bash
echo "GEMINI_API_KEY=your-key-here" > .env
```

### "Browser not found"

Install Chromium browser:
```bash
playwright install chromium
```

### Portal timeout errors

The portal might be temporarily down. Try again later or check your internet connection.

## Getting a Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and add it to your `.env` file

## System Requirements

- **OS**: Windows, macOS, or Linux
- **RAM**: 4GB minimum, 8GB recommended
- **Disk Space**: 500MB for dependencies and browsers
- **Internet**: Stable connection required

## Next Steps

Once installation is complete, see [README.md](README.md) for usage examples.
