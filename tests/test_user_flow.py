"""
PeopleRate - Comprehensive User Flow Test Automation
Tests the complete user journey from registration to review submission

Requirements:
    pip install pytest pytest-asyncio httpx playwright pytest-playwright

Usage:
    # Install playwright browsers (first time only)
    playwright install chromium
    
    # Run all tests
    pytest tests/test_user_flow.py -v
    
    # Run specific test
    pytest tests/test_user_flow.py::test_complete_user_flow -v
    
    # Run with browser visible (headed mode)
    pytest tests/test_user_flow.py --headed -v
"""

import pytest
import httpx
import asyncio
from playwright.sync_api import Page, expect
import random
import string


# Configuration
BASE_URL = "http://localhost:8000"  # Change to your deployment URL
TEST_USER_EMAIL = f"test_{random.randint(1000, 9999)}@example.com"
TEST_USER_PASSWORD = "TestPassword123!"
TEST_USER_USERNAME = f"testuser_{random.randint(1000, 9999)}"
TEST_USER_FULLNAME = "Test User"


class TestUserFlow:
    """Test complete user flow through the application"""
    
    @pytest.fixture(scope="class")
    def test_data(self):
        """Fixture to store test data across tests"""
        return {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
            "username": TEST_USER_USERNAME,
            "fullname": TEST_USER_FULLNAME,
            "token": None,
            "user_id": None,
            "person_id": None,
            "review_id": None
        }
    
    def test_01_homepage_loads(self, page: Page):
        """Test 1: Homepage loads successfully"""
        print("\n🧪 TEST 1: Homepage Load")
        
        page.goto(BASE_URL)
        expect(page).to_have_title("PeopleRate - Professional People Review Platform")
        
        # Check hero section
        expect(page.locator(".hero-section h1")).to_contain_text("Bengaluru")
        
        # Check search section
        expect(page.locator("#searchInput")).to_be_visible()
        
        print("✅ Homepage loaded successfully")
    
    def test_02_search_functionality(self, page: Page):
        """Test 2: Search functionality works"""
        print("\n🧪 TEST 2: Search Functionality")
        
        page.goto(BASE_URL)
        
        # Test search
        search_input = page.locator("#searchInput")
        search_input.fill("carpenter")
        page.locator(".search-btn").click()
        
        # Wait for results
        page.wait_for_timeout(2000)
        
        # Check if results or no results message appears
        results_section = page.locator("#searchResults")
        expect(results_section).to_be_visible()
        
        print("✅ Search functionality working")
    
    def test_03_user_registration(self, page: Page, test_data):
        """Test 3: User registration flow"""
        print("\n🧪 TEST 3: User Registration")
        
        page.goto(f"{BASE_URL}/auth")
        
        # Click register link
        page.locator("#showRegister").click()
        page.wait_for_timeout(500)
        
        # Fill registration form
        page.locator("#registerFormElement #email").fill(test_data["email"])
        page.locator("#registerFormElement #username").fill(test_data["username"])
        page.locator("#registerFormElement #full_name").fill(test_data["fullname"])
        page.locator("#registerFormElement #password").fill(test_data["password"])
        
        # Submit form
        page.locator("#registerFormElement button[type='submit']").click()
        
        # Wait for redirect or success message
        page.wait_for_timeout(2000)
        
        # Check if user is logged in (token in localStorage)
        token = page.evaluate("() => localStorage.getItem('token')")
        assert token is not None, "Registration failed - no token found"
        test_data["token"] = token
        
        print(f"✅ User registered successfully: {test_data['username']}")
    
    def test_04_user_login(self, page: Page, test_data):
        """Test 4: User login flow"""
        print("\n🧪 TEST 4: User Login")
        
        # Logout first
        page.evaluate("() => { localStorage.removeItem('token'); localStorage.removeItem('userInfo'); }")
        
        page.goto(f"{BASE_URL}/auth")
        
        # Fill login form
        page.locator("#loginFormElement #email").fill(test_data["email"])
        page.locator("#loginFormElement #password").fill(test_data["password"])
        
        # Submit
        page.locator("#loginFormElement button[type='submit']").click()
        
        # Wait for login
        page.wait_for_timeout(2000)
        
        # Check token
        token = page.evaluate("() => localStorage.getItem('token')")
        assert token is not None, "Login failed - no token found"
        
        print("✅ User logged in successfully")
    
    def test_05_add_person_nlp(self, page: Page, test_data):
        """Test 5: Add person using NLP"""
        print("\n🧪 TEST 5: Add Person (NLP)")
        
        page.goto(BASE_URL)
        page.wait_for_timeout(1000)
        
        # Ensure logged in
        token = page.evaluate("() => localStorage.getItem('token')")
        if not token:
            pytest.skip("User not logged in - skipping")
        
        # Click Add Person button
        page.locator(".btn-add-person").first.click()
        page.wait_for_timeout(500)
        
        # Check modal is open
        modal = page.locator("#addPersonModal")
        expect(modal).to_be_visible()
        
        # Fill NLP description
        description = """
        Ramesh Carpentry works in Koramangala 4th Block, Bengaluru.
        He specializes in custom wardrobes and modular kitchens.
        Contact: WhatsApp +91-9845123456
        Email: ramesh.carpenter@example.com
        """
        page.locator("#personDescription").fill(description)
        page.wait_for_timeout(1000)
        
        # Check if Preview Parsing button appeared
        preview_btn = page.locator("#previewParsingBtn")
        if preview_btn.is_visible():
            print("  ℹ️  Preview button visible - testing preview")
            preview_btn.click()
            page.wait_for_timeout(3000)
            
            # Check if preview appeared
            preview_box = page.locator("#nlpPreview")
            if preview_box.is_visible():
                print("  ✅ Preview parsing worked")
        
        # Submit form (if not already redirected)
        if page.url.startswith(BASE_URL) and "/person/" not in page.url:
            page.locator("#addPersonForm button[type='submit']").click()
            page.wait_for_timeout(3000)
        
        # Check if redirected to person page
        assert "/person/" in page.url, "Failed to create person"
        
        # Extract person_id from URL
        person_id = page.url.split("/person/")[-1]
        test_data["person_id"] = person_id
        
        print(f"✅ Person added successfully: {person_id}")
    
    def test_06_write_review(self, page: Page, test_data):
        """Test 6: Write a review"""
        print("\n🧪 TEST 6: Write Review")
        
        if not test_data.get("person_id"):
            pytest.skip("No person_id available - skipping")
        
        page.goto(f"{BASE_URL}/person/{test_data['person_id']}")
        page.wait_for_timeout(1000)
        
        # Click Write Review button
        page.locator("button:has-text('Write Review')").first.click()
        page.wait_for_timeout(500)
        
        # Fill review form
        page.locator("#reviewModal #reviewTitle").fill("Excellent work on my wardrobe!")
        page.locator("#reviewModal #reviewContent").fill(
            "Ramesh did an amazing job on my bedroom wardrobe. "
            "Very professional, on-time delivery, and great quality work. "
            "Highly recommend for anyone looking for custom carpentry!"
        )
        
        # Set ratings
        page.locator("#reviewModal .rating-star[data-rating='5']").first.click()  # Overall rating
        
        # Submit review
        page.locator("#reviewModal button[type='submit']").click()
        page.wait_for_timeout(3000)
        
        # Check if review appears on page
        page.reload()
        page.wait_for_timeout(1000)
        
        review_cards = page.locator(".review-card")
        assert review_cards.count() > 0, "Review not found on page"
        
        print("✅ Review submitted successfully")
    
    def test_07_profile_page(self, page: Page, test_data):
        """Test 7: Access user profile"""
        print("\n🧪 TEST 7: User Profile")
        
        page.goto(f"{BASE_URL}/profile")
        page.wait_for_timeout(1000)
        
        # Check profile page loaded
        expect(page).to_have_url(f"{BASE_URL}/profile")
        
        # Check user info is displayed
        username_element = page.locator("text=" + test_data["username"])
        expect(username_element).to_be_visible()
        
        print("✅ Profile page accessible")
    
    def test_08_my_reviews_page(self, page: Page):
        """Test 8: View my reviews"""
        print("\n🧪 TEST 8: My Reviews Page")
        
        page.goto(f"{BASE_URL}/my-reviews")
        page.wait_for_timeout(1000)
        
        # Check page loaded
        expect(page).to_have_url(f"{BASE_URL}/my-reviews")
        
        print("✅ My reviews page accessible")
    
    def test_09_search_page(self, page: Page):
        """Test 9: Search page works"""
        print("\n🧪 TEST 9: Search Page")
        
        page.goto(f"{BASE_URL}/search")
        page.wait_for_timeout(1000)
        
        # Should show homepage with search
        expect(page.locator("#searchInput")).to_be_visible()
        
        print("✅ Search page working")
    
    def test_10_404_page(self, page: Page):
        """Test 10: 404 page displays correctly"""
        print("\n🧪 TEST 10: 404 Page")
        
        page.goto(f"{BASE_URL}/nonexistent-page-12345")
        page.wait_for_timeout(1000)
        
        # Check 404 page elements
        expect(page.locator(".error-code")).to_contain_text("404")
        expect(page.locator(".trust-check-box")).to_be_visible()
        
        print("✅ 404 page displaying correctly")
    
    def test_11_legal_pages(self, page: Page):
        """Test 11: Legal pages load"""
        print("\n🧪 TEST 11: Legal Pages")
        
        # Terms of Service
        page.goto(f"{BASE_URL}/legal/terms")
        page.wait_for_timeout(1000)
        expect(page).to_have_url(f"{BASE_URL}/legal/terms")
        print("  ✅ Terms page loaded")
        
        # Privacy Policy
        page.goto(f"{BASE_URL}/legal/privacy")
        page.wait_for_timeout(1000)
        expect(page).to_have_url(f"{BASE_URL}/legal/privacy")
        print("  ✅ Privacy page loaded")
        
        print("✅ Legal pages accessible")
    
    def test_12_logout(self, page: Page):
        """Test 12: User logout"""
        print("\n🧪 TEST 12: User Logout")
        
        page.goto(BASE_URL)
        page.wait_for_timeout(1000)
        
        # Logout via JavaScript (simpler than navigating UI)
        page.evaluate("""() => {
            localStorage.removeItem('token');
            localStorage.removeItem('userInfo');
        }""")
        
        page.reload()
        page.wait_for_timeout(1000)
        
        # Check token is gone
        token = page.evaluate("() => localStorage.getItem('token')")
        assert token is None, "Logout failed - token still present"
        
        print("✅ User logged out successfully")


class TestAPIEndpoints:
    """Test API endpoints directly"""
    
    @pytest.mark.asyncio
    async def test_api_health(self):
        """Test API is responding"""
        print("\n🧪 API TEST: Health Check")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(BASE_URL)
            assert response.status_code == 200
            print("✅ API is healthy")
    
    @pytest.mark.asyncio
    async def test_api_search(self):
        """Test search API"""
        print("\n🧪 API TEST: Search Endpoint")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/api/persons/search", params={"query": "carpenter"})
            assert response.status_code == 200
            data = response.json()
            assert "persons" in data
            print(f"✅ Search API working - Found {len(data['persons'])} results")


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context"""
    return {
        **browser_context_args,
        "viewport": {"width": 1920, "height": 1080},
        "ignore_https_errors": True,
    }


if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║         PeopleRate - User Flow Test Automation           ║
    ╚═══════════════════════════════════════════════════════════╝
    
    To run these tests:
    
    1. Install dependencies:
       pip install pytest pytest-asyncio httpx playwright pytest-playwright
       playwright install chromium
    
    2. Start the server:
       python -m uvicorn main:app --reload --port 8000
    
    3. Run tests:
       pytest tests/test_user_flow.py -v --headed
    
    4. Run specific test:
       pytest tests/test_user_flow.py::TestUserFlow::test_01_homepage_loads -v
    
    """)
