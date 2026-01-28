#!/usr/bin/env python3
"""
Telangana CCLA Portal Automation
Land Status / Pahani & ROR-1B Search

URL: https://ccla.telangana.gov.in/landStatus.done
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path

from playwright.async_api import async_playwright, Page


# Selectors
SELECTORS = {
    'location': {
        'district': '#district',
        'division': '#division',
        'mandal': '#mandal',
        'village': '#village',
    },
    'searchType': {
        'khataNo': 'input[value="1"]',
        'surveyNo': 'input[value="2"]',
        'buyerSeller': 'input[value="3"]',
        'mutationDate': 'input[value="4"]',
    },
    'inputs': {
        'khataNoDropdown': '#khata',
        'surveyNoDropdown': '#survey',
        'buyerName': '#buyername',
        'sellerName': '#sellername',
        'mutationDate': '#mutation_date',
    },
    'captcha': {
        'hidden': '#captchaHidden',
        'text': '#captchaText',
        'input': '#captcha',
        'refresh': 'img[src*="refresh"]',
    },
    'buttons': {
        'getDetails': 'button:has-text("Get Details")',
    },
}


async def select_location(page: Page, district: str, division: str, mandal: str, village: str):
    """Select location from cascading dropdowns"""
    print(f"[CCLA] Selecting location: {district} → {division} → {mandal} → {village}")
    
    await page.select_option(SELECTORS['location']['district'], district)
    await page.wait_for_timeout(1500)
    print("[CCLA] ✓ District selected")
    
    await page.select_option(SELECTORS['location']['division'], division)
    await page.wait_for_timeout(1500)
    print("[CCLA] ✓ Division selected")
    
    await page.select_option(SELECTORS['location']['mandal'], mandal)
    await page.wait_for_timeout(1500)
    print("[CCLA] ✓ Mandal selected")
    
    await page.select_option(SELECTORS['location']['village'], village)
    await page.wait_for_timeout(1000)
    print("[CCLA] ✓ Village selected")


async def select_search_type(page: Page, mode: str, buyer: str = None, seller: str = None):
    """Select search type and fill inputs"""
    print(f"[CCLA] Search mode: {mode}")
    
    if mode == 'khataNo':
        await page.click(SELECTORS['searchType']['khataNo'])
        await page.wait_for_timeout(1000)
        # Select first available option from dropdown
        options = await page.locator(f"{SELECTORS['inputs']['khataNoDropdown']} option").all_text_contents()
        valid_options = [o for o in options if o and o not in ['--Select--', '---select---']]
        if valid_options:
            await page.select_option(SELECTORS['inputs']['khataNoDropdown'], label=valid_options[0])
            print(f"[CCLA] ✓ Khata No selected: {valid_options[0]}")
    
    elif mode == 'surveyNo':
        await page.click(SELECTORS['searchType']['surveyNo'])
        await page.wait_for_timeout(1000)
        # Select first available option from dropdown
        options = await page.locator(f"{SELECTORS['inputs']['surveyNoDropdown']} option").all_text_contents()
        valid_options = [o for o in options if o and o not in ['--Select--', '---select---']]
        if valid_options:
            await page.select_option(SELECTORS['inputs']['surveyNoDropdown'], label=valid_options[0])
            print(f"[CCLA] ✓ Survey No selected: {valid_options[0]}")
    
    elif mode == 'buyerSeller':
        await page.click(SELECTORS['searchType']['buyerSeller'])
        await page.wait_for_timeout(500)
        if buyer:
            await page.fill(SELECTORS['inputs']['buyerName'], buyer)
            print(f"[CCLA] ✓ Buyer Name entered: {buyer}")
        if seller:
            await page.fill(SELECTORS['inputs']['sellerName'], seller)
            print(f"[CCLA] ✓ Seller Name entered: {seller}")
    
    print("[CCLA] ✓ Search type selected")


async def solve_captcha(page: Page, max_retries: int = 3) -> bool:
    """Solve CAPTCHA using DOM extraction"""
    print("[CCLA] Solving CAPTCHA (DOM extraction)...")
    
    for attempt in range(1, max_retries + 1):
        print(f"[CCLA] CAPTCHA attempt {attempt}/{max_retries}")
        
        # Refresh CAPTCHA
        try:
            refresh_btn = page.locator(SELECTORS['captcha']['refresh']).first
            if await refresh_btn.is_visible(timeout=2000):
                await refresh_btn.click()
                print("[CCLA] ✓ CAPTCHA refreshed")
            else:
                await page.evaluate("window.refreshCaptcha?.()")
        except:
            pass
        
        await page.wait_for_timeout(1500)
        
        # Extract CAPTCHA from hidden field or text
        try:
            solution = await page.evaluate(f"""
                () => {{
                    const hidden = document.querySelector('{SELECTORS['captcha']['hidden']}');
                    if (hidden && hidden.value) return hidden.value;
                    const text = document.querySelector('{SELECTORS['captcha']['text']}');
                    if (text) return text.textContent;
                    return null;
                }}
            """)
            
            if solution and len(solution.strip()) > 1:
                solution = solution.strip()
                print(f"[CCLA] Extracted CAPTCHA: {solution}")
                
                captcha_input = page.locator(SELECTORS['captcha']['input']).first
                if await captcha_input.is_visible(timeout=3000):
                    await captcha_input.clear()
                    await captcha_input.fill(solution)
                    print(f"[CCLA] ✓ CAPTCHA filled: {solution}")
                    return True
        except Exception as e:
            print(f"[CCLA] ⚠️ CAPTCHA attempt {attempt} failed: {e}")
        
        await page.wait_for_timeout(1000)
    
    print(f"[CCLA] ⚠️ CAPTCHA solving failed after {max_retries} attempts")
    return False


async def submit_search(page: Page):
    """Submit search form"""
    print("[CCLA] Submitting search...")
    
    # Handle potential dialog
    page.on("dialog", lambda dialog: dialog.dismiss())
    
    await page.click(SELECTORS['buttons']['getDetails'])
    await page.wait_for_timeout(3000)
    
    print("[CCLA] ✓ Search submitted")


async def extract_results(page: Page, output_dir: str) -> dict:
    """Extract results and save files"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_path = f"{output_dir}/ccla_{timestamp}"
    
    # Screenshot
    screenshot_path = f"{base_path}.png"
    await page.screenshot(path=screenshot_path, full_page=True)
    print(f"[CCLA] 📸 Screenshot: {screenshot_path}")
    
    # HTML
    html_content = await page.content()
    html_path = f"{base_path}.html"
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"[CCLA] 📄 HTML: {html_path}")
    
    # Check for results
    has_results = await page.locator('th:has-text("Khata"), th:has-text("Survey"), th:has-text("Reason for Amendment")').is_visible(timeout=5000)
    
    results = {
        'portal': 'telangana-ccla',
        'timestamp': timestamp,
        'found': has_results,
        'screenshot': screenshot_path,
        'html': html_path,
        'data': []
    }
    
    if has_results:
        print("[CCLA] ✓ Results found")
        
        # Extract table data
        rows = await page.locator('table tbody tr').all()
        for row in rows:
            cells = await row.locator('td').all_text_contents()
            if cells:
                results['data'].append({
                    'khataNo': cells[0] if len(cells) > 0 else '',
                    'surveyNo': cells[1] if len(cells) > 1 else '',
                    'ownerName': cells[2] if len(cells) > 2 else '',
                    'extent': cells[3] if len(cells) > 3 else '',
                    'landType': cells[4] if len(cells) > 4 else '',
                    'reasonForAmendment': cells[5] if len(cells) > 5 else '',
                })
    else:
        page_text = await page.evaluate("() => document.body.innerText")
        if 'no record' in page_text.lower():
            results['message'] = 'No records found'
            print("[CCLA] ℹ️ No records found")
        else:
            results['message'] = 'Search completed but no results table found'
            print("[CCLA] ℹ️ No results table found")
    
    # Save JSON
    json_path = f"{base_path}.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"[CCLA] 📋 JSON: {json_path}")
    
    return results


async def search_ccla(
    district: str,
    division: str,
    mandal: str,
    village: str,
    mode: str = 'buyerSeller',
    buyer: str = None,
    seller: str = None,
    headless: bool = False,
    output_dir: str = 'output'
):
    """Main CCLA search function"""
    print("\n" + "="*50)
    print("Telangana CCLA Portal Automation")
    print("="*50)
    print(f"Mode: {'Headless' if headless else 'Headed'}")
    print(f"Search: {mode}")
    print(f"Location: District={district}, Division={division}, Mandal={mandal}, Village={village}")
    if buyer:
        print(f"Buyer: {buyer}")
    if seller:
        print(f"Seller: {seller}")
    print("="*50 + "\n")
    
    # Create output directory
    Path(output_dir).mkdir(exist_ok=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless, slow_mo=50 if not headless else 0)
        context = await browser.new_context(viewport={'width': 1280, 'height': 900})
        page = await context.new_page()
        
        try:
            # Navigate to portal
            print("[CCLA] Navigating to portal...")
            await page.goto('https://ccla.telangana.gov.in/landStatus.done', wait_until='domcontentloaded', timeout=60000)
            await page.wait_for_timeout(2000)
            print(f"[CCLA] Current URL: {page.url}")
            print("[CCLA] ✓ Portal initialized\n")
            
            # Select location
            await select_location(page, district, division, mandal, village)
            
            # Select search type
            await select_search_type(page, mode, buyer, seller)
            
            # Solve CAPTCHA
            captcha_solved = await solve_captcha(page, 3)
            if not captcha_solved:
                print("[CCLA] ⚠️ CAPTCHA may not be solved correctly")
            
            # Submit search
            await submit_search(page)
            
            # Extract results
            results = await extract_results(page, output_dir)
            
            print("\n" + "="*50)
            print("Search Complete")
            print("="*50)
            print(f"Found: {results['found']}")
            print(f"Records: {len(results['data'])}")
            print(f"Files saved in: {output_dir}/")
            print("="*50 + "\n")
            
            # Keep browser open for inspection if headed
            if not headless:
                print("[CCLA] Browser open for 30 seconds for inspection...")
                await page.wait_for_timeout(30000)
            
            return results
            
        except Exception as e:
            print(f"\n[CCLA] ❌ Error: {e}")
            error_screenshot = f"{output_dir}/ccla_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            await page.screenshot(path=error_screenshot, full_page=True)
            print(f"[CCLA] 📸 Error screenshot: {error_screenshot}")
            raise
        finally:
            await browser.close()


def main():
    parser = argparse.ArgumentParser(description='Telangana CCLA Portal Automation')
    parser.add_argument('--district', required=True, help='District code (e.g., 31 for Warangal Rural)')
    parser.add_argument('--division', required=True, help='Division code')
    parser.add_argument('--mandal', required=True, help='Mandal code')
    parser.add_argument('--village', required=True, help='Village code')
    parser.add_argument('--mode', choices=['khataNo', 'surveyNo', 'buyerSeller', 'mutationDate'], 
                       default='buyerSeller', help='Search mode')
    parser.add_argument('--buyer', help='Buyer name (for buyerSeller mode)')
    parser.add_argument('--seller', help='Seller name (for buyerSeller mode)')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    parser.add_argument('--output', default='output', help='Output directory')
    
    args = parser.parse_args()
    
    # Validate buyer/seller for buyerSeller mode
    if args.mode == 'buyerSeller' and not (args.buyer or args.seller):
        print("Error: --buyer or --seller required for buyerSeller mode")
        sys.exit(1)
    
    # Run search
    asyncio.run(search_ccla(
        district=args.district,
        division=args.division,
        mandal=args.mandal,
        village=args.village,
        mode=args.mode,
        buyer=args.buyer,
        seller=args.seller,
        headless=args.headless,
        output_dir=args.output
    ))


if __name__ == '__main__':
    main()
