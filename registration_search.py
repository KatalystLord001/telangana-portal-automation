#!/usr/bin/env python3
"""
Telangana Registration & Stamps Portal Automation
EC (Encumbrance Certificate) Search

URL: https://registration.telangana.gov.in/
Requires: Login with credentials + CAPTCHA solving via Gemini AI
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path

from playwright.async_api import async_playwright, Page, BrowserContext
import google.generativeai as genai
from dotenv import load_dotenv


# Load environment variables
load_dotenv()

# URLs
LOGIN_URL = 'https://registration.telangana.gov.in/deptlogout.htm'
DASHBOARD_URL = 'https://registration.telangana.gov.in/outsideIgrsDashboard.htm'
EC_SEARCH_URL = 'https://registration.telangana.gov.in/EncumbranceCertificate/Search_Document.htm'

# Default credentials
DEFAULT_USERNAME = os.getenv('TS_REG_USERNAME', '7011590660')
DEFAULT_PASSWORD = os.getenv('TS_REG_PASSWORD', 'Aarav@123')

# Selectors
SELECTORS = {
    'login': {
        'userType': '#user_type',
        'username': '#username',
        'password': '#password',
        'captchaImage': 'img[src*="Captcha"], img[src*="captcha"]',
        'captchaInput': '#captcha',
        'loginButton': 'button[type="submit"], input[type="submit"]',
    },
    'searchMode': {
        'byDocumentNumber': 'input[name="docSel"][value="1"]',
    },
    'documentSearch': {
        'documentNo': '#doct',
        'yearOfRegistration': '#regyear',
        'sroAutocomplete': '#sroVal',
    },
    'buttons': {
        'submit': 'button[type="submit"]',
    },
}


async def solve_captcha_with_gemini(image_bytes: bytes) -> str:
    """Solve CAPTCHA using Gemini AI"""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    prompt = """This is a CAPTCHA image containing 6 alphanumeric characters (mix of uppercase letters A-Z and numbers 0-9).

IMPORTANT RULES:
1. Return EXACTLY 6 characters, nothing else
2. Characters are uppercase letters (A-Z) and numbers (0-9)
3. NO spaces, NO punctuation, NO explanations
4. Look carefully at each character - they may be distorted with lines through them

Common character confusions to watch for:
- 0 (zero) vs O (letter O) vs D
- 1 (one) vs I (letter I) vs L
- 5 vs S
- 6 vs G vs 8
- 8 vs B
- 2 vs Z
- 7 vs T vs Y

What are the 6 characters in this CAPTCHA?"""
    
    import base64
    image_b64 = base64.b64encode(image_bytes).decode('utf-8')
    
    response = model.generate_content([
        {'mime_type': 'image/png', 'data': image_b64},
        prompt
    ])
    
    solution = response.text.strip()
    # Clean up - only alphanumeric
    solution = ''.join(c for c in solution if c.isalnum())
    
    return solution


async def solve_captcha(page: Page, max_retries: int = 5) -> str:
    """Solve CAPTCHA with retry logic"""
    print("[TS-REG] Solving CAPTCHA...")
    
    for attempt in range(1, max_retries + 1):
        try:
            captcha_element = await page.query_selector(SELECTORS['login']['captchaImage'])
            if not captcha_element:
                await page.wait_for_timeout(2000)
                continue
            
            await page.wait_for_timeout(1000)
            screenshot = await captcha_element.screenshot(type='png')
            
            solution = await solve_captcha_with_gemini(screenshot)
            
            if solution and 4 <= len(solution) <= 8:
                print(f"[TS-REG] ✓ CAPTCHA solved: {solution}")
                return solution
            
            # Refresh CAPTCHA
            await captcha_element.click()
            await page.wait_for_timeout(2000)
            
        except Exception as e:
            print(f"[TS-REG] CAPTCHA attempt {attempt} failed: {e}")
    
    raise Exception("CAPTCHA solving failed after all retries")


async def login(page: Page, context: BrowserContext, username: str, password: str) -> bool:
    """Login to portal"""
    print("[TS-REG] Logging in...")
    
    # Clear old cookies
    await context.clear_cookies()
    
    # Go to login page
    await page.goto(LOGIN_URL, wait_until='domcontentloaded', timeout=60000)
    await page.wait_for_timeout(3000)
    
    # Check if already logged in
    if 'citizen_auth' in page.url or 'Dashboard' in page.url:
        print("[TS-REG] ✓ Already logged in")
        return True
    
    try:
        # Select user type: Citizen (value="2")
        await page.select_option(SELECTORS['login']['userType'], '2')
        await page.wait_for_timeout(500)
        
        # Fill credentials
        await page.fill(SELECTORS['login']['username'], username)
        await page.fill(SELECTORS['login']['password'], password)
        
        # Solve CAPTCHA
        captcha = await solve_captcha(page)
        await page.fill(SELECTORS['login']['captchaInput'], captcha)
        
        # Click login
        print("[TS-REG] Clicking login button...")
        await page.evaluate("""
            () => {
                const btn = document.querySelector('button[type="submit"], input[type="submit"]');
                if (btn) btn.click();
            }
        """)
        
        await page.wait_for_timeout(8000)
        
        # Check for invalid captcha
        page_text = await page.evaluate("() => document.body.innerText")
        if 'invalid captcha' in page_text.lower():
            print("[TS-REG] Invalid CAPTCHA, retrying...")
            await page.goto(LOGIN_URL, wait_until='domcontentloaded', timeout=60000)
            await page.wait_for_timeout(2000)
            return await login(page, context, username, password)
        
        # Check if login successful
        new_url = page.url
        is_logged_in = ('citizen_auth' in new_url or 'Dashboard' in new_url or 
                       'outsideIgrsDashboard' in new_url or 'Welcome' in page_text or 
                       'Encumbrance Search' in page_text)
        
        if is_logged_in:
            print("[TS-REG] ✓ Login successful")
            return True
        
        if 'deptlogout' in new_url:
            print("[TS-REG] ✗ Login failed")
            return False
        
        print("[TS-REG] ✓ Login appears successful")
        return True
        
    except Exception as e:
        print(f"[TS-REG] Login error: {e}")
        return False


async def navigate_to_ec_search(page: Page) -> Page:
    """Navigate to EC Search form"""
    print("[TS-REG] Navigating to EC Search...")
    
    # Go directly to EC Search URL
    await page.goto('https://registration.telangana.gov.in/EncumbranceSearch.htm', 
                   wait_until='domcontentloaded', timeout=60000)
    await page.wait_for_timeout(3000)
    
    # Check for unauthorized
    page_text = await page.evaluate("() => document.body.innerText")
    if 'Unauthorised Access' in page_text or 'Request denied' in page_text:
        raise Exception('Session expired - Unauthorised Access')
    
    # If on EC Statement page, click Submit
    if 'Encumbrance Statement' in page_text or 'EncumbranceSearch.htm' in page.url:
        print("[TS-REG] On EC Statement page, clicking Submit...")
        
        await page.evaluate("""
            () => {
                const links = Array.from(document.querySelectorAll('a'));
                for (const link of links) {
                    if (link.textContent?.includes('Submit') || link.href?.includes('Search_Document')) {
                        link.click();
                        return true;
                    }
                }
                return false;
            }
        """)
        
        await page.wait_for_timeout(5000)
        
        page_text = await page.evaluate("() => document.body.innerText")
        if 'Unauthorised Access' in page_text:
            raise Exception('Session expired after Submit')
    
    # Verify search form loaded
    has_form = await page.query_selector('input[name="docSel"]')
    if not has_form:
        print("[TS-REG] Search form not found, trying direct URL...")
        await page.goto(EC_SEARCH_URL, wait_until='domcontentloaded', timeout=60000)
        await page.wait_for_timeout(3000)
        
        page_text = await page.evaluate("() => document.body.innerText")
        if 'Unauthorised Access' in page_text:
            raise Exception('Session expired')
    
    print("[TS-REG] ✓ EC Search form loaded")
    return page


async def search_by_document_number(
    page: Page,
    doc_no: str,
    year: str,
    sro: str,
    output_dir: str
) -> dict:
    """Complete document number search flow"""
    print("\n" + "="*50)
    print("DOCUMENT NUMBER SEARCH")
    print("="*50)
    print(f"Document: {doc_no}, Year: {year}, SRO: {sro}")
    print("="*50 + "\n")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    try:
        # Step 1: Fill search form
        print("[TS-REG] Step 1: Filling search form...")
        await page.click(SELECTORS['searchMode']['byDocumentNumber'])
        await page.wait_for_timeout(1000)
        
        await page.fill(SELECTORS['documentSearch']['documentNo'], doc_no)
        await page.fill(SELECTORS['documentSearch']['yearOfRegistration'], year)
        
        # SRO autocomplete
        sro_input = page.locator(SELECTORS['documentSearch']['sroAutocomplete']).first
        await sro_input.click()
        await page.wait_for_timeout(500)
        await sro_input.fill('')
        await page.wait_for_timeout(300)
        await page.keyboard.type(sro, delay=30)
        await page.wait_for_timeout(2000)
        
        # Click first dropdown item
        dropdown_item = page.locator('.ui-autocomplete li').first
        if await dropdown_item.is_visible(timeout=3000):
            await dropdown_item.click()
        else:
            await sro_input.press('Enter')
        await page.wait_for_timeout(500)
        
        # Screenshot before submit
        await page.screenshot(path=f"{output_dir}/ts_reg_step1_form_{timestamp}.png", full_page=True)
        
        # Submit Step 1
        print("[TS-REG] Submitting Step 1...")
        await page.evaluate("() => { const btn = document.querySelector('button[type=\"submit\"]'); if (btn) btn.click(); }")
        await page.wait_for_timeout(8000)
        
        await page.screenshot(path=f"{output_dir}/ts_reg_step1_result_{timestamp}.png", full_page=True)
        
        # Check for errors
        page_text = await page.evaluate("() => document.body.innerText")
        if 'no record' in page_text.lower() or 'not found' in page_text.lower():
            return {
                'success': False,
                'message': 'No records found for this document',
                'timestamp': timestamp
            }
        
        # Step 2: Click NEXT
        print("[TS-REG] Step 2: Looking for NEXT button...")
        next_clicked = await page.evaluate("""
            () => {
                const links = Array.from(document.querySelectorAll('a, button, input'));
                for (const el of links) {
                    const text = el.textContent?.toUpperCase() || el.value?.toUpperCase() || '';
                    if (text.includes('NEXT')) {
                        el.click();
                        return true;
                    }
                }
                return false;
            }
        """)
        
        if next_clicked:
            print("[TS-REG] Clicked NEXT...")
            await page.wait_for_timeout(6000)
        else:
            print("[TS-REG] No NEXT button found")
        
        await page.screenshot(path=f"{output_dir}/ts_reg_step2_dates_{timestamp}.png", full_page=True)
        
        # Step 3: Submit date range
        print("[TS-REG] Step 3: Submitting date range...")
        await page.evaluate("() => { const btn = document.querySelector('button[type=\"submit\"]'); if (btn) btn.click(); }")
        await page.wait_for_timeout(8000)
        
        await page.screenshot(path=f"{output_dir}/ts_reg_step3_documents_{timestamp}.png", full_page=True)
        
        # Step 4: Select all checkboxes
        print("[TS-REG] Step 4: Selecting document checkboxes...")
        select_all_clicked = await page.evaluate("""
            () => {
                const selectAll = document.querySelector('#checkall2, input[name="checkall2"]');
                if (selectAll) {
                    selectAll.click();
                    return true;
                }
                const checkboxes = document.querySelectorAll('input[name="chkDocId"]');
                checkboxes.forEach(cb => { if (!cb.checked) cb.click(); });
                return checkboxes.length > 0;
            }
        """)
        print(f"[TS-REG] Checkboxes selected: {select_all_clicked}")
        await page.wait_for_timeout(1000)
        
        # Extract document IDs
        documents = await page.evaluate("""
            () => {
                const checkboxes = document.querySelectorAll('input[name="chkDocId"]');
                return Array.from(checkboxes).map(cb => cb.value).filter(v => v);
            }
        """)
        print(f"[TS-REG] Documents found: {len(documents)}")
        
        await page.screenshot(path=f"{output_dir}/ts_reg_step4_selected_{timestamp}.png", full_page=True)
        
        # Step 5: Final Submit
        print("[TS-REG] Step 5: Submitting for final EC Report...")
        await page.evaluate("() => { const btn = document.querySelector('button[type=\"submit\"]'); if (btn) btn.click(); }")
        await page.wait_for_timeout(10000)
        
        # Capture final EC Report
        return await capture_ec_report(page, output_dir, timestamp, documents)
        
    except Exception as e:
        print(f"[TS-REG] Search error: {e}")
        error_screenshot = f"{output_dir}/ts_reg_error_{timestamp}.png"
        await page.screenshot(path=error_screenshot, full_page=True)
        return {
            'success': False,
            'message': f'Search failed: {str(e)}',
            'screenshot': error_screenshot,
            'timestamp': timestamp
        }


async def capture_ec_report(page: Page, output_dir: str, timestamp: str, documents: list) -> dict:
    """Capture the final EC Report"""
    print("[TS-REG] Capturing EC Report...")
    
    base_path = f"{output_dir}/ts_reg_ec_report_{timestamp}"
    
    # Screenshot
    screenshot_path = f"{base_path}.png"
    await page.screenshot(path=screenshot_path, full_page=True)
    print(f"[TS-REG] 📸 Screenshot: {screenshot_path}")
    
    # PDF (headless only)
    pdf_path = None
    try:
        pdf_path = f"{base_path}.pdf"
        await page.pdf(path=pdf_path, format='A4', print_background=True,
                      margin={'top': '20px', 'bottom': '20px', 'left': '20px', 'right': '20px'})
        print(f"[TS-REG] 📄 PDF: {pdf_path}")
    except:
        print("[TS-REG] PDF skipped (headless only)")
        pdf_path = None
    
    # HTML
    html_path = f"{base_path}.html"
    html_content = await page.content()
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"[TS-REG] 📝 HTML: {html_path}")
    
    # Extract data
    page_text = await page.evaluate("() => document.body.innerText")
    request_match = None
    for line in page_text.split('\n'):
        if 'Request Number' in line or 'Application Number' in line:
            import re
            match = re.search(r'\d+', line)
            if match:
                request_match = match.group()
                break
    
    result = {
        'success': True,
        'message': f'EC Report generated with {len(documents)} documents',
        'documents': documents,
        'requestNumber': request_match,
        'screenshot': screenshot_path,
        'pdf': pdf_path,
        'html': html_path,
        'timestamp': timestamp
    }
    
    # Save JSON
    json_path = f"{base_path}.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)
    print(f"[TS-REG] 📋 JSON: {json_path}")
    
    print("[TS-REG] ========== EC REPORT CAPTURED ==========\n")
    
    return result


async def search_registration(
    doc_no: str,
    year: str,
    sro: str,
    username: str = DEFAULT_USERNAME,
    password: str = DEFAULT_PASSWORD,
    headless: bool = False,
    output_dir: str = 'output'
):
    """Main registration search function"""
    print("\n" + "="*50)
    print("Telangana Registration & Stamps Portal")
    print("="*50)
    print(f"Mode: {'Headless' if headless else 'Headed'}")
    print(f"Document: {doc_no}, Year: {year}, SRO: {sro}")
    print("="*50 + "\n")
    
    # Create output directory
    Path(output_dir).mkdir(exist_ok=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless, slow_mo=50 if not headless else 0)
        context = await browser.new_context(viewport={'width': 1400, 'height': 900})
        page = await context.new_page()
        
        try:
            # Login
            login_success = await login(page, context, username, password)
            if not login_success:
                return {'success': False, 'message': 'Login failed'}
            
            # Navigate to EC Search
            ec_page = await navigate_to_ec_search(page)
            
            # Perform search
            result = await search_by_document_number(ec_page, doc_no, year, sro, output_dir)
            
            print("\n" + "="*50)
            print("Search Complete")
            print("="*50)
            print(f"Success: {result['success']}")
            print(f"Message: {result['message']}")
            if result.get('documents'):
                print(f"Documents: {len(result['documents'])}")
            if result.get('screenshot'):
                print(f"Screenshot: {result['screenshot']}")
            if result.get('pdf'):
                print(f"PDF: {result['pdf']}")
            if result.get('html'):
                print(f"HTML: {result['html']}")
            print("="*50 + "\n")
            
            # Keep browser open for inspection if headed
            if not headless:
                print("[TS-REG] Browser open for 30 seconds for inspection...")
                await page.wait_for_timeout(30000)
            
            return result
            
        except Exception as e:
            print(f"\n[TS-REG] ❌ Error: {e}")
            error_screenshot = f"{output_dir}/ts_reg_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            await page.screenshot(path=error_screenshot, full_page=True)
            print(f"[TS-REG] 📸 Error screenshot: {error_screenshot}")
            raise
        finally:
            await browser.close()


def main():
    parser = argparse.ArgumentParser(description='Telangana Registration & Stamps Portal Automation')
    parser.add_argument('--doc', required=True, help='Document number')
    parser.add_argument('--year', required=True, help='Year of registration')
    parser.add_argument('--sro', required=True, help='SRO name (e.g., "HYDERABAD (R.O)")')
    parser.add_argument('--username', default=DEFAULT_USERNAME, help='Login username')
    parser.add_argument('--password', default=DEFAULT_PASSWORD, help='Login password')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    parser.add_argument('--output', default='output', help='Output directory')
    
    args = parser.parse_args()
    
    # Check for Gemini API key
    if not os.getenv('GEMINI_API_KEY'):
        print("Error: GEMINI_API_KEY not found in environment variables")
        print("Please create a .env file with: GEMINI_API_KEY=your-key-here")
        sys.exit(1)
    
    # Run search
    asyncio.run(search_registration(
        doc_no=args.doc,
        year=args.year,
        sro=args.sro,
        username=args.username,
        password=args.password,
        headless=args.headless,
        output_dir=args.output
    ))


if __name__ == '__main__':
    main()
