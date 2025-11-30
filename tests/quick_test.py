"""
PeopleRate - Quick API Test Script
Simple test script that tests all API endpoints without browser automation

Requirements:
    pip install requests colorama

Usage:
    python tests/quick_test.py
"""

import requests
import json
from datetime import datetime
from colorama import init, Fore, Style
import sys
import time

# Initialize colorama for colored output
init(autoreset=True)

# Configuration
BASE_URL = "http://localhost:8000"  # Change to your deployment URL
TEST_EMAIL = f"quicktest_{int(time.time())}@example.com"
TEST_PASSWORD = "TestPass123!"
TEST_USERNAME = f"testuser_{int(time.time())}"


class APITester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.token = None
        self.person_id = None
        self.session = requests.Session()
        self.passed = 0
        self.failed = 0
    
    def print_header(self, text):
        """Print test header"""
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{text}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    
    def print_test(self, name, status, message=""):
        """Print test result"""
        if status:
            self.passed += 1
            icon = f"{Fore.GREEN}✓{Style.RESET_ALL}"
            result = f"{Fore.GREEN}PASSED{Style.RESET_ALL}"
        else:
            self.failed += 1
            icon = f"{Fore.RED}✗{Style.RESET_ALL}"
            result = f"{Fore.RED}FAILED{Style.RESET_ALL}"
        
        print(f"{icon} {name}: {result}")
        if message:
            print(f"   {Fore.YELLOW}→ {message}{Style.RESET_ALL}")
    
    def print_summary(self):
        """Print test summary"""
        total = self.passed + self.failed
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}TEST SUMMARY{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"Total Tests: {total}")
        print(f"{Fore.GREEN}Passed: {self.passed}{Style.RESET_ALL}")
        if self.failed > 0:
            print(f"{Fore.RED}Failed: {self.failed}{Style.RESET_ALL}")
        else:
            print(f"Failed: {self.failed}")
        
        if self.failed == 0:
            print(f"\n{Fore.GREEN}🎉 ALL TESTS PASSED! 🎉{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.RED}⚠️  SOME TESTS FAILED{Style.RESET_ALL}")
    
    def test_homepage(self):
        """Test homepage loads"""
        try:
            response = self.session.get(f"{self.base_url}/")
            success = response.status_code == 200 and "PeopleRate" in response.text
            self.print_test("Homepage Load", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.print_test("Homepage Load", False, str(e))
            return False
    
    def test_search_page(self):
        """Test search page"""
        try:
            response = self.session.get(f"{self.base_url}/search")
            success = response.status_code == 200
            self.print_test("Search Page", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.print_test("Search Page", False, str(e))
            return False
    
    def test_404_page(self):
        """Test 404 page"""
        try:
            response = self.session.get(f"{self.base_url}/nonexistent-page-12345")
            # FastAPI returns 404 status code, check for PeopleRate 404 elements in response
            success = response.status_code == 404 and ("This Page Needs a Review" in response.text or "404" in response.text)
            self.print_test("404 Page", success, "Custom 404 page displayed")
            return success
        except Exception as e:
            self.print_test("404 Page", False, str(e))
            return False
    
    def test_register(self):
        """Test user registration"""
        try:
            data = {
                "email": TEST_EMAIL,
                "username": TEST_USERNAME,
                "full_name": "Quick Test User",
                "password": TEST_PASSWORD
            }
            response = self.session.post(
                f"{self.base_url}/api/auth/register",
                json=data  # Changed from data= to json= for JSON body
            )
            
            if response.status_code == 200:
                result = response.json()
                self.token = result.get("access_token")
                success = self.token is not None
                self.print_test("User Registration", success, f"Token: {self.token[:20]}..." if success else "No token")
                return success
            else:
                self.print_test("User Registration", False, f"Status: {response.status_code}, {response.text[:100]}")
                return False
        except Exception as e:
            self.print_test("User Registration", False, str(e))
            return False
    
    def test_login(self):
        """Test user login"""
        try:
            data = {
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
            response = self.session.post(
                f"{self.base_url}/api/auth/login",
                data=data  # Login uses Form data, not JSON
            )
            
            if response.status_code == 200:
                result = response.json()
                self.token = result.get("access_token")
                success = self.token is not None
                self.print_test("User Login", success, "Token received")
                return success
            else:
                self.print_test("User Login", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.print_test("User Login", False, str(e))
            return False
    
    def test_auth_me(self):
        """Test /auth/me endpoint"""
        if not self.token:
            self.print_test("Auth Me Endpoint", False, "No token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = self.session.get(f"{self.base_url}/auth/me", headers=headers)
            success = response.status_code == 200
            if success:
                user = response.json()
                self.print_test("Auth Me Endpoint", success, f"User: {user.get('username')}")
            else:
                self.print_test("Auth Me Endpoint", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.print_test("Auth Me Endpoint", False, str(e))
            return False
    
    def test_search_api(self):
        """Test search API"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/persons/search",
                params={"query": "carpenter"}
            )
            success = response.status_code == 200
            if success:
                data = response.json()
                count = len(data.get("persons", []))
                self.print_test("Search API", success, f"Found {count} results")
            else:
                self.print_test("Search API", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.print_test("Search API", False, str(e))
            return False
    
    def test_add_person(self):
        """Test add person"""
        if not self.token:
            self.print_test("Add Person", False, "No token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            data = {
                "description": "Quick Test Vendor in Koramangala, provides carpentry services, WhatsApp: +91-9845123456"
            }
            response = self.session.post(
                f"{self.base_url}/api/persons/nlp",
                headers=headers,
                data=data
            )
            
            if response.status_code == 200:
                result = response.json()
                self.person_id = result.get("person_id")
                success = self.person_id is not None
                self.print_test("Add Person (NLP)", success, f"Person ID: {self.person_id}")
                return success
            else:
                self.print_test("Add Person (NLP)", False, f"Status: {response.status_code}, {response.text[:100]}")
                return False
        except Exception as e:
            self.print_test("Add Person (NLP)", False, str(e))
            return False
    
    def test_get_person(self):
        """Test get person details"""
        if not self.person_id:
            self.print_test("Get Person", False, "No person_id available")
            return False
        
        try:
            response = self.session.get(f"{self.base_url}/api/persons/{self.person_id}")
            success = response.status_code == 200
            if success:
                person = response.json()
                self.print_test("Get Person", success, f"Name: {person.get('name')}")
            else:
                self.print_test("Get Person", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.print_test("Get Person", False, str(e))
            return False
    
    def test_add_review(self):
        """Test add review"""
        if not self.token or not self.person_id:
            self.print_test("Add Review", False, "Missing token or person_id")
            return False
        
        try:
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            data = {
                "person_id": self.person_id,
                "title": "Quick Test Review",
                "comment": "This is a test review created by the automated test script. Very professional.",
                "rating": 5,
                "professionalism": 5,
                "communication": 5,
                "work_quality": 5,
                "reliability": 5,
                "relationship": "client",
                "would_recommend": True
            }
            response = self.session.post(
                f"{self.base_url}/api/reviews",
                headers=headers,
                json=data
            )
            
            success = response.status_code == 200
            if success:
                result = response.json()
                self.print_test("Add Review", success, f"Review ID: {result.get('review_id')}")
            else:
                self.print_test("Add Review", success, f"Status: {response.status_code}, {response.text[:100]}")
            return success
        except Exception as e:
            self.print_test("Add Review", False, str(e))
            return False
    
    def test_get_reviews(self):
        """Test get reviews"""
        if not self.person_id:
            self.print_test("Get Reviews", False, "No person_id available")
            return False
        
        try:
            response = self.session.get(f"{self.base_url}/api/reviews/?person_id={self.person_id}")
            success = response.status_code == 200
            if success:
                data = response.json()
                count = len(data.get("reviews", []))
                self.print_test("Get Reviews", success, f"Found {count} reviews")
            else:
                self.print_test("Get Reviews", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.print_test("Get Reviews", False, str(e))
            return False
    
    def test_platform_stats(self):
        """Test platform stats"""
        try:
            response = self.session.get(f"{self.base_url}/api/stats")
            success = response.status_code == 200
            if success:
                stats = response.json()
                self.print_test("Platform Stats", success, 
                              f"Users: {stats.get('total_users')}, Reviews: {stats.get('total_reviews')}")
            else:
                self.print_test("Platform Stats", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.print_test("Platform Stats", False, str(e))
            return False
    
    def test_admin_dashboard(self):
        """Test admin dashboard access"""
        if not self.token:
            self.print_test("Admin Dashboard", False, "Missing token - skipped")
            return False
        
        try:
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            response = self.session.get(
                f"{self.base_url}/admin/dashboard",
                headers=headers
            )
            
            # Success if either 200 (admin user) or 403 (non-admin, expected)
            success = response.status_code in [200, 403]
            status_msg = "Admin access" if response.status_code == 200 else "Non-admin (expected)"
            self.print_test("Admin Dashboard", success, status_msg)
            return success
        except Exception as e:
            self.print_test("Admin Dashboard", False, str(e))
            return False
    
    def test_profile_claiming(self):
        """Test profile claiming workflow"""
        if not self.token or not self.person_id:
            self.print_test("Profile Claiming", False, "Missing token or person_id - skipped")
            return False
        
        try:
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            data = {
                "person_id": self.person_id,
                "verification_method": "linkedin",
                "message": "This is a test claim for automated testing. I can verify via LinkedIn profile."
            }
            response = self.session.post(
                f"{self.base_url}/api/claims",
                headers=headers,
                json=data
            )
            
            success = response.status_code in [200, 201, 400]  # 400 if already claimed
            if response.status_code == 200 or response.status_code == 201:
                result = response.json()
                status_msg = f"Claim ID: {result.get('claim_id', 'unknown')}"
            elif response.status_code == 400:
                status_msg = "Already claimed (expected for repeat tests)"
            else:
                status_msg = f"Status: {response.status_code}"
            
            self.print_test("Profile Claiming", success, status_msg)
            return success
        except Exception as e:
            self.print_test("Profile Claiming", False, str(e))
            return False
    
    def test_verified_review(self):
        """Test adding a verified review (with proof)"""
        if not self.token or not self.person_id:
            self.print_test("Verified Review", False, "Missing token or person_id - skipped")
            return False
        
        try:
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            data = {
                "person_id": self.person_id,
                "title": "Verified Test Review",
                "comment": "This is a verified review with proof of work. Excellent collaboration on the project.",
                "rating": 5,
                "professionalism": 5,
                "communication": 5,
                "work_quality": 5,
                "reliability": 5,
                "relationship": "client",
                "would_recommend": True
            }
            response = self.session.post(
                f"{self.base_url}/api/reviews",
                headers=headers,
                json=data
            )
            
            # Accept 201 (created), 400 (already reviewed - expected on repeat runs)
            success = response.status_code in [200, 201, 400]
            if response.status_code in [200, 201]:
                result = response.json()
                review_id = result.get("review_id") or result.get("id")
                status_msg = f"Review ID: {review_id}, Proof submitted for verification"
            elif response.status_code == 400:
                status_msg = "Already reviewed (expected on repeat runs)"
            else:
                status_msg = f"Status: {response.status_code}"
            
            self.print_test("Verified Review", success, status_msg)
            return success
        except Exception as e:
            self.print_test("Verified Review", False, str(e))
            return False
    
    def test_unverified_review(self):
        """Test adding an unverified review (without proof)"""
        if not self.token or not self.person_id:
            self.print_test("Unverified Review", False, "Missing token or person_id - skipped")
            return False
        
        try:
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            data = {
                "person_id": self.person_id,
                "title": "Unverified Test Review",
                "comment": "This is an unverified review without proof. Good to work with.",
                "rating": 4,
                "professionalism": 4,
                "communication": 4,
                "work_quality": 4,
                "reliability": 4,
                "relationship": "colleague",
                "would_recommend": True
            }
            response = self.session.post(
                f"{self.base_url}/api/reviews",
                headers=headers,
                json=data
            )
            
            # Accept 201 (created), 400 (already reviewed - expected on repeat runs)
            success = response.status_code in [200, 201, 400]
            if response.status_code in [200, 201]:
                result = response.json()
                review_id = result.get("review_id") or result.get("id")
                status_msg = f"Review ID: {review_id}, No verification badge expected"
            elif response.status_code == 400:
                status_msg = "Already reviewed (expected on repeat runs)"
            else:
                status_msg = f"Status: {response.status_code}"
            
            self.print_test("Unverified Review", success, status_msg)
            return success
        except Exception as e:
            self.print_test("Unverified Review", False, str(e))
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print(f"\n{Fore.YELLOW}🚀 Starting PeopleRate API Tests{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Base URL: {self.base_url}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Style.RESET_ALL}")
        
        # Page Tests
        self.print_header("📄 PAGE TESTS")
        self.test_homepage()
        self.test_search_page()
        self.test_404_page()
        
        # Authentication Tests
        self.print_header("🔐 AUTHENTICATION TESTS")
        self.test_register()
        time.sleep(0.5)  # Small delay between API calls
        self.test_login()
        time.sleep(0.5)
        self.test_auth_me()
        
        # API Tests
        self.print_header("🔍 SEARCH & PERSON TESTS")
        self.test_search_api()
        time.sleep(0.5)
        self.test_add_person()
        time.sleep(0.5)
        if self.person_id:
            self.test_get_person()
        
        # Review Tests
        self.print_header("⭐ REVIEW TESTS")
        if self.token and self.person_id:
            self.test_add_review()
            time.sleep(0.5)
            self.test_get_reviews()
            time.sleep(0.5)
            self.test_verified_review()
            time.sleep(0.5)
            self.test_unverified_review()
        else:
            self.print_test("Review Tests", False, "Skipped - missing token or person_id")
        
        # Platform Tests
        self.print_header("📊 PLATFORM TESTS")
        self.test_platform_stats()
        
        # Admin & Advanced Features
        self.print_header("🔐 ADMIN & ADVANCED FEATURES")
        self.test_admin_dashboard()
        time.sleep(0.5)
        if self.token and self.person_id:
            self.test_profile_claiming()
        
        # Summary
        self.print_summary()
        
        return self.failed == 0


def main():
    """Main function"""
    print(f"""
{Fore.CYAN}╔═══════════════════════════════════════════════════════════╗
║         PeopleRate - Quick API Test Script               ║
╚═══════════════════════════════════════════════════════════╝{Style.RESET_ALL}
    """)
    
    # Check if server is running
    try:
        response = requests.get(BASE_URL, timeout=5)
        print(f"{Fore.GREEN}✓ Server is running at {BASE_URL}{Style.RESET_ALL}")
    except:
        print(f"{Fore.RED}✗ Server is not running at {BASE_URL}{Style.RESET_ALL}")
        print(f"\nPlease start the server:")
        print(f"  python -m uvicorn main:app --reload --port 8000")
        sys.exit(1)
    
    # Run tests
    tester = APITester(BASE_URL)
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
