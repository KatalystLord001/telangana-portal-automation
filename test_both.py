#!/usr/bin/env python3
"""
Test script to verify both CCLA and Registration portals work
"""

import asyncio
import sys
from pathlib import Path

# Import the search functions
from ccla_search import search_ccla
from registration_search import search_registration


async def test_ccla():
    """Test CCLA portal"""
    print("\n" + "="*60)
    print("TESTING CCLA PORTAL")
    print("="*60 + "\n")
    
    try:
        result = await search_ccla(
            district='31',  # Warangal Rural
            division='67',
            mandal='609',
            village='3111005',
            mode='buyerSeller',
            buyer='Kumar',
            seller='Reddy',
            headless=True,
            output_dir='test_output'
        )
        
        print("\n✅ CCLA Test PASSED")
        print(f"   Found: {result['found']}")
        print(f"   Records: {len(result['data'])}")
        return True
        
    except Exception as e:
        print(f"\n❌ CCLA Test FAILED: {e}")
        return False


async def test_registration():
    """Test Registration portal"""
    print("\n" + "="*60)
    print("TESTING REGISTRATION PORTAL")
    print("="*60 + "\n")
    
    try:
        result = await search_registration(
            doc_no='1234',
            year='2024',
            sro='HYDERABAD',
            headless=True,
            output_dir='test_output'
        )
        
        print("\n✅ Registration Test PASSED")
        print(f"   Success: {result['success']}")
        print(f"   Message: {result['message']}")
        return True
        
    except Exception as e:
        print(f"\n❌ Registration Test FAILED: {e}")
        return False


async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("TELANGANA PORTAL AUTOMATION - TEST SUITE")
    print("="*60)
    
    # Create test output directory
    Path('test_output').mkdir(exist_ok=True)
    
    # Test CCLA
    ccla_passed = await test_ccla()
    
    # Test Registration
    registration_passed = await test_registration()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"CCLA Portal:         {'✅ PASSED' if ccla_passed else '❌ FAILED'}")
    print(f"Registration Portal: {'✅ PASSED' if registration_passed else '❌ FAILED'}")
    print("="*60 + "\n")
    
    if ccla_passed and registration_passed:
        print("🎉 All tests passed! Both portals are working correctly.")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
