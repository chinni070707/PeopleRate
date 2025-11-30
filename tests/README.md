# PeopleRate - Test Automation

This directory contains automated tests for the PeopleRate platform.

## 📁 Test Files

### 1. `quick_test.py` - Quick API Testing ⚡
**Fast, comprehensive API testing without browser automation**

**Features:**
- ✅ Tests all API endpoints (16 tests)
- ✅ Tests page routes (homepage, search, 404)
- ✅ Tests authentication flow (register, login)
- ✅ Tests person creation with NLP
- ✅ Tests review submission (verified & unverified)
- ✅ Tests admin dashboard access
- ✅ Tests profile claiming workflow
- ✅ Colored console output
- ✅ Runs in ~10 seconds

**Test Coverage:**
- **Page Tests (3):** Homepage, Search, Custom 404
- **Authentication Tests (3):** Registration, Login, Auth verification
- **Search & Person Tests (3):** Search API, Add Person (NLP), Get Person
- **Review Tests (4):** Add Review, Get Reviews, Verified Review, Unverified Review
- **Platform Tests (1):** Platform statistics
- **Admin & Advanced Features (2):** Admin dashboard, Profile claiming

**Installation:**
```bash
pip install requests colorama
```

**Usage:**
```bash
# Make sure server is running
python -m uvicorn main:app --reload --port 8000

# Run tests (in another terminal)
python tests/quick_test.py
```

**Output Example:**
```
============================================================
📄 PAGE TESTS
============================================================
✓ Homepage Load: PASSED
✓ Search Page: PASSED
✓ 404 Page: PASSED

============================================================
🔐 AUTHENTICATION TESTS
============================================================
✓ User Registration: PASSED
✓ User Login: PASSED
✓ Auth Me Endpoint: PASSED

============================================================
🔍 SEARCH & PERSON TESTS
============================================================
✓ Search API: PASSED
✓ Add Person (NLP): PASSED
✓ Get Person: PASSED

============================================================
⭐ REVIEW TESTS
============================================================
✓ Add Review: PASSED
✓ Get Reviews: PASSED
✓ Verified Review: PASSED
✓ Unverified Review: PASSED

============================================================
📊 PLATFORM TESTS
============================================================
✓ Platform Stats: PASSED

============================================================
🔐 ADMIN & ADVANCED FEATURES
============================================================
✓ Admin Dashboard: PASSED
✓ Profile Claiming: PASSED

🎉 ALL TESTS PASSED! 🎉
```

---

### 2. `test_user_flow.py` - Complete Browser Automation 🌐
**Full end-to-end testing with real browser automation**

**Features:**
- ✅ Simulates real user interactions
- ✅ Tests complete user journey (12 tests)
- ✅ Tests UI elements and buttons
- ✅ Tests modals, forms, and JavaScript
- ✅ Visual testing with Playwright
- ✅ Parallel test execution

**Installation:**
```bash
pip install pytest pytest-asyncio httpx playwright pytest-playwright

# Install browser (first time only)
playwright install chromium
```

**Usage:**
```bash
# Run all tests
pytest tests/test_user_flow.py -v

# Run with visible browser (headed mode)
pytest tests/test_user_flow.py --headed -v

# Run specific test
pytest tests/test_user_flow.py::TestUserFlow::test_01_homepage_loads -v

# Run API tests only
pytest tests/test_user_flow.py::TestAPIEndpoints -v
```

**Tests Included:**
1. Homepage loads
2. Search functionality
3. User registration
4. User login
5. Add person (NLP)
6. Write review
7. Profile page
8. My reviews page
9. Search page
10. 404 page
11. Legal pages
12. User logout

---

## 🎯 Which Test to Use?

### Use `quick_test.py` when:
- ✅ You want fast API testing (~10 seconds)
- ✅ Testing backend endpoints
- ✅ Running in CI/CD pipeline
- ✅ Don't need browser testing
- ✅ Want colored console output

### Use `test_user_flow.py` when:
- ✅ Testing complete user experience
- ✅ Testing UI/UX interactions
- ✅ Testing JavaScript functionality
- ✅ Testing modals, dropdowns, forms
- ✅ Need visual confirmation
- ✅ Testing on different browsers

---

## 🚀 Quick Start

### Option 1: Quick API Test (Recommended for first test)
```bash
# Terminal 1: Start server
cd "C:\Users\mahchi01\OneDrive - Cadence Design Systems Inc\Documents\PeopleRate"
.\venv\Scripts\Activate.ps1
python -m uvicorn main:app --reload --port 8000

# Terminal 2: Run quick test
cd "C:\Users\mahchi01\OneDrive - Cadence Design Systems Inc\Documents\PeopleRate"
.\venv\Scripts\Activate.ps1
pip install requests colorama
python tests/quick_test.py
```

### Option 2: Full Browser Test
```bash
# Terminal 1: Start server (same as above)

# Terminal 2: Run Playwright tests
cd "C:\Users\mahchi01\OneDrive - Cadence Design Systems Inc\Documents\PeopleRate"
.\venv\Scripts\Activate.ps1
pip install pytest pytest-asyncio httpx playwright pytest-playwright
playwright install chromium
pytest tests/test_user_flow.py -v --headed
```

---

## 🐛 Troubleshooting

### Quick Test Issues

**Problem: "Server is not running"**
```bash
# Solution: Start the server first
python -m uvicorn main:app --reload --port 8000
```

**Problem: "Module not found: requests"**
```bash
# Solution: Install dependencies
pip install requests colorama
```

### Playwright Test Issues

**Problem: "Playwright not installed"**
```bash
# Solution: Install playwright and browser
pip install playwright pytest-playwright
playwright install chromium
```

**Problem: "Tests timing out"**
```bash
# Solution: Increase timeout in pytest.ini or command
pytest tests/test_user_flow.py -v --timeout=300
```

**Problem: "Can't see what's happening"**
```bash
# Solution: Run in headed mode (shows browser)
pytest tests/test_user_flow.py --headed -v
```

---

## 📊 Test Coverage

### API Endpoints Tested ✅
- `GET /` - Homepage
- `GET /search` - Search page
- `GET /auth` - Auth page
- `GET /profile` - Profile page
- `GET /my-reviews` - My reviews
- `GET /person/{id}` - Person detail
- `GET /legal/terms` - Terms of service
- `GET /legal/privacy` - Privacy policy
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /auth/me` - Current user
- `GET /api/persons/search` - Search persons
- `POST /api/persons/nlp` - Add person (NLP)
- `GET /api/persons/{id}` - Get person
- `POST /api/reviews` - Submit review
- `GET /api/reviews/` - Get reviews
- `GET /api/stats` - Platform stats

### Features Tested ✅
- ✅ User authentication (register, login, logout)
- ✅ NLP person creation
- ✅ Search functionality
- ✅ Review submission
- ✅ Profile management
- ✅ 404 error handling
- ✅ Legal pages
- ✅ Platform statistics

---

## 🔄 Continuous Integration

### GitHub Actions Example
```yaml
name: Run Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install requests colorama
      - name: Start server
        run: |
          python -m uvicorn main:app --host 0.0.0.0 --port 8000 &
          sleep 5
      - name: Run quick tests
        run: python tests/quick_test.py
```

---

## 📝 Adding New Tests

### Adding to quick_test.py
```python
def test_my_new_feature(self):
    """Test my new feature"""
    try:
        response = self.session.get(f"{self.base_url}/my-endpoint")
        success = response.status_code == 200
        self.print_test("My New Feature", success, "Description")
        return success
    except Exception as e:
        self.print_test("My New Feature", False, str(e))
        return False
```

### Adding to test_user_flow.py
```python
def test_13_my_new_feature(self, page: Page):
    """Test 13: My new feature"""
    print("\n🧪 TEST 13: My New Feature")
    
    page.goto(f"{BASE_URL}/my-page")
    page.wait_for_timeout(1000)
    
    # Your test logic
    expect(page.locator("#my-element")).to_be_visible()
    
    print("✅ My new feature working")
```

---

## 🎉 Success Criteria

All tests should pass with:
- ✅ HTTP 200 responses for all pages
- ✅ Successful authentication flow
- ✅ NLP person creation working
- ✅ Review submission successful
- ✅ No JavaScript errors
- ✅ All UI elements visible and clickable

---

**Happy Testing! 🚀**
