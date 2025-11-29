"""Simple Chromium browser test for PeopleRate"""
from playwright.sync_api import sync_playwright
import time

def test_peopleRate():
    print("🚀 Starting Chromium browser test...")
    
    with sync_playwright() as p:
        # Launch Chromium in visible mode
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()
        
        try:
            # Test 1: Homepage
            print("\n📄 Test 1: Loading homepage...")
            page.goto("http://localhost:8080", timeout=10000)
            page.wait_for_load_state("networkidle")
            
            title = page.title()
            print(f"   ✅ Page title: {title}")
            
            # Check for main elements
            if page.locator('input[type="text"]').count() > 0:
                print("   ✅ Search box found")
            
            # Screenshot
            page.screenshot(path="screenshots/homepage.png")
            print("   📸 Screenshot saved: screenshots/homepage.png")
            
            # Test 2: Search functionality
            print("\n🔍 Test 2: Testing search...")
            search_input = page.locator('input[type="text"]').first
            search_input.fill("Alice")
            search_input.press("Enter")
            page.wait_for_timeout(2000)
            
            # Check URL changed
            current_url = page.url
            print(f"   ✅ Current URL: {current_url}")
            
            # Count results
            results = page.locator('.person-card, .search-result, a[href*="/person/"]').count()
            print(f"   ✅ Found {results} elements on search page")
            
            page.screenshot(path="screenshots/search_results.png")
            print("   📸 Screenshot saved: screenshots/search_results.png")
            
            # Test 3: Click first result if available
            if results > 0:
                print("\n👤 Test 3: Opening first person profile...")
                page.locator('.person-card, .search-result, a[href*="/person/"]').first.click()
                page.wait_for_timeout(2000)
                
                profile_url = page.url
                print(f"   ✅ Profile URL: {profile_url}")
                
                page.screenshot(path="screenshots/person_profile.png")
                print("   📸 Screenshot saved: screenshots/person_profile.png")
            
            print("\n✅ All tests completed!")
            print("⏰ Keeping browser open for 15 seconds...")
            time.sleep(15)
            
        except Exception as e:
            print(f"\n❌ Error during testing: {e}")
            page.screenshot(path="screenshots/error.png")
            print("   📸 Error screenshot saved")
        
        finally:
            browser.close()
            print("👋 Browser closed")

if __name__ == "__main__":
    test_peopleRate()
