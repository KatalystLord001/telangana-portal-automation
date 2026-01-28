#!/bin/bash
# Quick Start Script for Telangana Portal Automation

echo "=========================================="
echo "Telangana Portal Automation - Quick Start"
echo "=========================================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Install dependencies
echo ""
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

# Install Playwright browsers
echo ""
echo "🌐 Installing Playwright browsers..."
playwright install chromium

# Check for .env file
if [ ! -f .env ]; then
    echo ""
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo ""
    echo "📝 Please edit .env and add your GEMINI_API_KEY"
    echo "   Get your key from: https://makersuite.google.com/app/apikey"
    echo ""
    read -p "Press Enter after you've added your API key to .env..."
fi

# Create output directory
mkdir -p output

# Run test
echo ""
echo "🧪 Running tests..."
python3 test_both.py

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Usage examples:"
echo ""
echo "CCLA Portal:"
echo "  python3 ccla_search.py --district 31 --division 67 --mandal 609 --village 3111005 --buyer Kumar --seller Reddy"
echo ""
echo "Registration Portal:"
echo "  python3 registration_search.py --doc 1234 --year 2024 --sro \"HYDERABAD (R.O)\""
echo ""
echo "For more options, see README.md"
echo ""
