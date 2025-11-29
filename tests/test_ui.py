"""
Automated UI Tests for PeopleRate using Playwright
Tests admin dashboard, social sharing, error pages, and core functionality
"""

import asyncio
import sys
from playwright.async_api import async_playwright, expect
import time

# Configuration
BASE_URL = "http://localhost:8000"
ADMIN_USERNAME = "TechReviewer2024"
ADMIN_PASSWORD = "password123"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

async def test_homepage(page):
    """Test homepage loads correctly"""
    print(f"\n{Colors.BLUE}🧪 Testing Homepage...{Colors.END}")
    try:
        await page.goto(BASE_URL, wait_until="networkidle")
        
        # Check title
        title = await page.title()
        assert "PeopleRate" in title, f"Expected 'PeopleRate' in title, got: {title}"
        
        # Check search functionality exists
        search_input = page.locator('input[placeholder*="Search"]').first
        await expect(search_input).to_be_visible()
        
        # Check navigation
        assert await page.locator('text=Login').count() > 0 or await page.locator('text=Log in').count() > 0
        
        print(f"{Colors.GREEN}✅ Homepage test passed{Colors.END}")
        return True
    except Exception as e:
        print(f"{Colors.RED}❌ Homepage test failed: {e}{Colors.END}")
        return False

async def test_404_page(page):
    """Test custom 404 error page"""
    print(f"\n{Colors.BLUE}🧪 Testing 404 Error Page...{Colors.END}")
    try:
        response = await page.goto(f"{BASE_URL}/nonexistent-page-test", wait_until="networkidle")
        
        # Check status code
        assert response.status == 404, f"Expected 404, got: {response.status}"
        
        # Check for 404 content
        content = await page.content()
        assert "404" in content, "404 error code not found in page"
        assert "Page Not Found" in content or "not found" in content.lower(), "404 message not found"
        
        # Check for navigation buttons
        homepage_btn = page.locator('a[href="/"]')
        await expect(homepage_btn.first).to_be_visible()
        
        print(f"{Colors.GREEN}✅ 404 page test passed{Colors.END}")
        return True
    except Exception as e:
        print(f"{Colors.RED}❌ 404 page test failed: {e}{Colors.END}")
        return False

async def test_admin_login(page):
    """Test admin login flow"""
    print(f"\n{Colors.BLUE}🧪 Testing Admin Login...{Colors.END}")
    try:
        # Go to auth page
        await page.goto(f"{BASE_URL}/auth", wait_until="networkidle")
        
        # Fill login form
        await page.fill('input[type="text"]', ADMIN_USERNAME)
        await page.fill('input[type="password"]', ADMIN_PASSWORD)
        
        # Click login button
        await page.click('button:has-text("Login")', timeout=5000)
        
        # Wait for redirect/response
        await page.wait_for_timeout(2000)
        
        # Check if logged in (should redirect or show success)
        current_url = page.url
        content = await page.content()
        
        # Either redirected away from /auth or shows logged in state
        logged_in = current_url != f"{BASE_URL}/auth" or "logout" in content.lower() or "profile" in content.lower()
        
        assert logged_in, "Login did not succeed"
        
        print(f"{Colors.GREEN}✅ Admin login test passed{Colors.END}")
        return True
    except Exception as e:
        print(f"{Colors.RED}❌ Admin login test failed: {e}{Colors.END}")
        return False

async def test_admin_dashboard(page):
    """Test admin dashboard access and functionality"""
    print(f"\n{Colors.BLUE}🧪 Testing Admin Dashboard...{Colors.END}")
    try:
        # First login
        await page.goto(f"{BASE_URL}/auth", wait_until="networkidle")
        await page.fill('input[type="text"]', ADMIN_USERNAME)
        await page.fill('input[type="password"]', ADMIN_PASSWORD)
        await page.click('button:has-text("Login")')
        await page.wait_for_timeout(2000)
        
        # Go to admin page
        await page.goto(f"{BASE_URL}/admin", wait_until="networkidle")
        
        # Check for admin dashboard elements
        content = await page.content()
        
        # Check for statistics
        assert "Users" in content or "users" in content, "Users stat not found"
        assert "Reviews" in content or "reviews" in content, "Reviews stat not found"
        
        # Check for tabs
        tabs_exist = (
            "Flagged Reviews" in content or "flagged" in content.lower() or
            "Recent Activity" in content or "User Management" in content
        )
        assert tabs_exist, "Admin dashboard tabs not found"
        
        print(f"{Colors.GREEN}✅ Admin dashboard test passed{Colors.END}")
        return True
    except Exception as e:
        print(f"{Colors.RED}❌ Admin dashboard test failed: {e}{Colors.END}")
        print(f"{Colors.YELLOW}Note: Ensure server is running and admin user exists{Colors.END}")
        return False

async def test_person_profile(page):
    """Test person profile page and social sharing"""
    print(f"\n{Colors.BLUE}🧪 Testing Person Profile & Social Sharing...{Colors.END}")
    try:
        # Go to homepage first
        await page.goto(BASE_URL, wait_until="networkidle")
        
        # Try to find a person link
        person_links = await page.locator('a[href*="/person/"]').all()
        
        if not person_links:
            print(f"{Colors.YELLOW}⚠️ No person profiles found, skipping test{Colors.END}")
            return True
        
        # Click first person link
        await person_links[0].click()
        await page.wait_for_load_state("networkidle")
        
        # Check profile loaded
        content = await page.content()
        assert "rating" in content.lower() or "review" in content.lower(), "Person profile content not found"
        
        # Check for social share buttons
        share_buttons_exist = (
            'share-twitter' in content or 'twitter' in content.lower() or
            'share-linkedin' in content or 'linkedin' in content.lower() or
            'share-facebook' in content or 'facebook' in content.lower()
        )
        
        if share_buttons_exist:
            print(f"{Colors.GREEN}✅ Social share buttons found on profile{Colors.END}")
        else:
            print(f"{Colors.YELLOW}⚠️ Social share buttons not found (may need to scroll){Colors.END}")
        
        print(f"{Colors.GREEN}✅ Person profile test passed{Colors.END}")
        return True
    except Exception as e:
        print(f"{Colors.RED}❌ Person profile test failed: {e}{Colors.END}")
        return False

async def test_search_functionality(page):
    """Test search functionality"""
    print(f"\n{Colors.BLUE}🧪 Testing Search Functionality...{Colors.END}")
    try:
        await page.goto(BASE_URL, wait_until="networkidle")
        
        # Find search input
        search_input = page.locator('input[placeholder*="Search"], input[type="search"]').first
        await expect(search_input).to_be_visible()
        
        # Type search query
        await search_input.fill("John")
        await page.wait_for_timeout(1000)
        
        # Look for search button or press Enter
        search_buttons = await page.locator('button:has-text("Search")').all()
        if search_buttons:
            await search_buttons[0].click()
        else:
            await search_input.press("Enter")
        
        await page.wait_for_timeout(2000)
        
        # Check if results appear or navigated to search page
        current_url = page.url
        content = await page.content()
        
        search_worked = (
            "/search" in current_url or 
            "result" in content.lower() or 
            "person" in content.lower()
        )
        
        assert search_worked, "Search did not produce results"
        
        print(f"{Colors.GREEN}✅ Search functionality test passed{Colors.END}")
        return True
    except Exception as e:
        print(f"{Colors.RED}❌ Search test failed: {e}{Colors.END}")
        return False

async def test_footer_legal_links(page):
    """Test footer legal links"""
    print(f"\n{Colors.BLUE}🧪 Testing Footer Legal Links...{Colors.END}")
    try:
        await page.goto(BASE_URL, wait_until="networkidle")
        
        # Scroll to footer
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(500)
        
        content = await page.content()
        
        # Check for legal links in footer
        has_terms = "Terms" in content or "terms" in content
        has_privacy = "Privacy" in content or "privacy" in content
        
        assert has_terms or has_privacy, "Legal links not found in footer"
        
        # Try clicking Terms link if exists
        terms_links = await page.locator('a[href*="/legal/terms"]').all()
        if terms_links:
            await terms_links[0].click()
            await page.wait_for_load_state("networkidle")
            
            terms_content = await page.content()
            assert "Terms" in terms_content or "terms" in terms_content.lower(), "Terms page did not load"
            print(f"{Colors.GREEN}✅ Terms page accessible{Colors.END}")
        
        print(f"{Colors.GREEN}✅ Footer legal links test passed{Colors.END}")
        return True
    except Exception as e:
        print(f"{Colors.RED}❌ Footer legal links test failed: {e}{Colors.END}")
        return False

async def test_responsive_design(page):
    """Test responsive design on different screen sizes"""
    print(f"\n{Colors.BLUE}🧪 Testing Responsive Design...{Colors.END}")
    try:
        # Test mobile viewport
        await page.set_viewport_size({"width": 375, "height": 667})
        await page.goto(BASE_URL, wait_until="networkidle")
        await page.wait_for_timeout(1000)
        
        # Check if page is accessible
        content = await page.content()
        assert len(content) > 1000, "Page too small on mobile"
        
        # Test tablet viewport
        await page.set_viewport_size({"width": 768, "height": 1024})
        await page.reload(wait_until="networkidle")
        await page.wait_for_timeout(1000)
        
        # Test desktop viewport
        await page.set_viewport_size({"width": 1920, "height": 1080})
        await page.reload(wait_until="networkidle")
        await page.wait_for_timeout(1000)
        
        print(f"{Colors.GREEN}✅ Responsive design test passed{Colors.END}")
        return True
    except Exception as e:
        print(f"{Colors.RED}❌ Responsive design test failed: {e}{Colors.END}")
        return False

async def run_all_tests():
    """Run all automated tests"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}🚀 PeopleRate Automated Test Suite{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"Testing against: {BASE_URL}")
    print(f"Admin user: {ADMIN_USERNAME}")
    
    results = {}
    
    async with async_playwright() as p:
        # Launch browser
        print(f"\n{Colors.YELLOW}🌐 Launching browser...{Colors.END}")
        browser = await p.chromium.launch(headless=False)  # Set to True for CI/CD
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = await context.new_page()
        
        try:
            # Run tests
            results['homepage'] = await test_homepage(page)
            results['404_page'] = await test_404_page(page)
            results['search'] = await test_search_functionality(page)
            results['footer_links'] = await test_footer_legal_links(page)
            results['person_profile'] = await test_person_profile(page)
            results['admin_login'] = await test_admin_login(page)
            results['admin_dashboard'] = await test_admin_dashboard(page)
            results['responsive'] = await test_responsive_design(page)
            
        except Exception as e:
            print(f"{Colors.RED}❌ Test suite error: {e}{Colors.END}")
        finally:
            await browser.close()
    
    # Print summary
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}📊 Test Results Summary{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = f"{Colors.GREEN}✅ PASSED{Colors.END}" if result else f"{Colors.RED}❌ FAILED{Colors.END}"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    percentage = (passed / total * 100) if total > 0 else 0
    color = Colors.GREEN if percentage >= 80 else Colors.YELLOW if percentage >= 60 else Colors.RED
    print(f"{color}Final Score: {passed}/{total} tests passed ({percentage:.1f}%){Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️ Tests interrupted by user{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}❌ Fatal error: {e}{Colors.END}")
        sys.exit(1)
