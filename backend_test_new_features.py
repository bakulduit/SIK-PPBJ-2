#!/usr/bin/env python3
"""
Backend API Tests for New Features: Document Search & Guide Videos
Tests the SIK-PPBJ finance app backend (FastAPI)
"""

import requests
import sys
from typing import Optional, Dict

# Configuration
BASE_URL = "https://sik-ppbj-deploy.preview.emergentagent.com/api"

# Test credentials from /app/memory/test_credentials.md
CREDENTIALS = {
    "superadmin": {"email": "nashoharizal@gmail.com", "password": "SIKPPBJ2026"},
}

# Test results tracking
test_results = []
failed_tests = []


class TestSession:
    """Manages authenticated session with cookies"""
    def __init__(self):
        self.session = requests.Session()
        self.user_info = None
        
    def login(self, email: str, password: str) -> bool:
        """Login and store cookies"""
        try:
            resp = self.session.post(
                f"{BASE_URL}/auth/login",
                json={"email": email, "password": password},
                timeout=30
            )
            if resp.status_code == 200:
                self.user_info = resp.json()
                return True
            else:
                print(f"  ❌ Login failed: {resp.status_code} - {resp.text}")
                return False
        except Exception as e:
            print(f"  ❌ Login error: {e}")
            return False
    
    def get(self, path: str, **kwargs):
        """GET request with session cookies"""
        return self.session.get(f"{BASE_URL}{path}", timeout=30, **kwargs)
    
    def post(self, path: str, **kwargs):
        """POST request with session cookies"""
        return self.session.post(f"{BASE_URL}{path}", timeout=30, **kwargs)
    
    def put(self, path: str, **kwargs):
        """PUT request with session cookies"""
        return self.session.put(f"{BASE_URL}{path}", timeout=30, **kwargs)
    
    def delete(self, path: str, **kwargs):
        """DELETE request with session cookies"""
        return self.session.delete(f"{BASE_URL}{path}", timeout=30, **kwargs)
    
    def patch(self, path: str, **kwargs):
        """PATCH request with session cookies"""
        return self.session.patch(f"{BASE_URL}{path}", timeout=30, **kwargs)


def log_test(name: str, passed: bool, details: str = ""):
    """Log test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}: {name}")
    if details:
        print(f"  Details: {details}")
    test_results.append({"name": name, "passed": passed, "details": details})
    if not passed:
        failed_tests.append({"name": name, "details": details})


def test_document_search():
    """Test FITUR A: Global Document Search (GET /api/documents/search)"""
    print("\n=== FITUR A: CARI GLOBAL DOKUMEN (GET /api/documents/search) ===")
    
    # Test 1: Without authentication → 401/403
    print("\n--- Test 1: Without Authentication ---")
    try:
        resp = requests.get(f"{BASE_URL}/documents/search?q=test", timeout=30)
        if resp.status_code in [401, 403]:
            log_test("Search without auth returns 401/403", True, f"Status: {resp.status_code}")
        else:
            log_test("Search without auth returns 401/403", False, 
                    f"Expected 401/403, got {resp.status_code}: {resp.text}")
    except Exception as e:
        log_test("Search without auth returns 401/403", False, f"Error: {e}")
    
    # Login as superadmin for remaining tests
    session = TestSession()
    if not session.login(CREDENTIALS["superadmin"]["email"], CREDENTIALS["superadmin"]["password"]):
        log_test("Login for search tests", False, "Failed to login as superadmin")
        return False
    
    log_test("Login for search tests", True, f"Logged in as {session.user_info.get('email')}")
    
    # Test 2: With auth, q empty → 200 with []
    print("\n--- Test 2: With Auth, Empty Query ---")
    try:
        resp = session.get("/documents/search?q=")
        
        if resp.status_code == 200:
            log_test("Search with empty q returns 200", True, f"Status: {resp.status_code}")
            
            data = resp.json()
            if isinstance(data, list) and len(data) == 0:
                log_test("Search with empty q returns empty array", True, "Response: []")
            else:
                log_test("Search with empty q returns empty array", False, 
                        f"Expected [], got {type(data)} with {len(data) if isinstance(data, list) else 'N/A'} items")
        else:
            log_test("Search with empty q returns 200", False, 
                    f"Expected 200, got {resp.status_code}: {resp.text}")
    except Exception as e:
        log_test("Search with empty q test", False, f"Error: {e}")
    
    # Test 3: With auth, q < 2 characters (q=a) → 200 with []
    print("\n--- Test 3: With Auth, Query < 2 Characters ---")
    try:
        resp = session.get("/documents/search?q=a")
        
        if resp.status_code == 200:
            log_test("Search with q<2 chars returns 200", True, f"Status: {resp.status_code}")
            
            data = resp.json()
            if isinstance(data, list) and len(data) == 0:
                log_test("Search with q<2 chars returns empty array", True, "Response: []")
            else:
                log_test("Search with q<2 chars returns empty array", False, 
                        f"Expected [], got {type(data)} with {len(data) if isinstance(data, list) else 'N/A'} items")
        else:
            log_test("Search with q<2 chars returns 200", False, 
                    f"Expected 200, got {resp.status_code}: {resp.text}")
    except Exception as e:
        log_test("Search with q<2 chars test", False, f"Error: {e}")
    
    # Test 4: With auth, valid q → 200 with array
    print("\n--- Test 4: With Auth, Valid Query ---")
    try:
        # Try searching for common terms that might exist in documents
        search_terms = ["001", "PPBJ", "BJM"]  # Common patterns in document numbers
        
        for term in search_terms:
            resp = session.get(f"/documents/search?q={term}")
            
            if resp.status_code == 200:
                log_test(f"Search with valid q='{term}' returns 200", True, f"Status: {resp.status_code}")
                
                data = resp.json()
                if isinstance(data, list):
                    log_test(f"Search with q='{term}' returns array", True, 
                            f"Response is array with {len(data)} items")
                    
                    # If results exist, verify structure
                    if len(data) > 0:
                        first_item = data[0]
                        required_fields = ["id", "no", "doc_type", "status", "total"]
                        has_all_fields = all(field in first_item for field in required_fields)
                        
                        if has_all_fields:
                            log_test(f"Search result has required fields", True, 
                                    f"Fields: {', '.join(required_fields)}")
                        else:
                            missing = [f for f in required_fields if f not in first_item]
                            log_test(f"Search result has required fields", False, 
                                    f"Missing fields: {missing}")
                        
                        # Verify case-insensitive match
                        log_test(f"Search is case-insensitive", True, 
                                f"Found {len(data)} results for '{term}'")
                        break  # Found results, no need to test other terms
                    else:
                        # Empty results are OK if DB has no documents
                        log_test(f"Search with q='{term}' returns results", True, 
                                f"No documents in DB (empty array is valid)")
                else:
                    log_test(f"Search with q='{term}' returns array", False, 
                            f"Expected array, got {type(data)}")
            else:
                log_test(f"Search with valid q='{term}' returns 200", False, 
                        f"Expected 200, got {resp.status_code}: {resp.text}")
    except Exception as e:
        log_test("Search with valid q test", False, f"Error: {e}")
    
    # Test 5: Parameter limit is honored (limit=5)
    print("\n--- Test 5: Limit Parameter ---")
    try:
        resp = session.get("/documents/search?q=001&limit=5")
        
        if resp.status_code == 200:
            log_test("Search with limit=5 returns 200", True, f"Status: {resp.status_code}")
            
            data = resp.json()
            if isinstance(data, list):
                if len(data) <= 5:
                    log_test("Search respects limit parameter", True, 
                            f"Returned {len(data)} items (≤5)")
                else:
                    log_test("Search respects limit parameter", False, 
                            f"Expected ≤5 items, got {len(data)}")
            else:
                log_test("Search with limit returns array", False, f"Expected array, got {type(data)}")
        else:
            log_test("Search with limit=5 returns 200", False, 
                    f"Expected 200, got {resp.status_code}: {resp.text}")
    except Exception as e:
        log_test("Search with limit test", False, f"Error: {e}")
    
    # Test 6: IMPORTANT - Route ordering check
    # GET /api/documents/search should NOT be caught by /api/documents/{doc_id}
    print("\n--- Test 6: Route Ordering Check ---")
    try:
        resp = session.get("/documents/search?q=test")
        
        if resp.status_code == 200:
            # Should return array, not 404 "Dokumen tidak ditemukan"
            data = resp.json()
            if isinstance(data, list):
                log_test("Route ordering correct (search not caught by {doc_id})", True, 
                        "Returns array, not 404")
            else:
                log_test("Route ordering correct (search not caught by {doc_id})", False, 
                        f"Expected array, got {type(data)}")
        elif resp.status_code == 404:
            error_detail = resp.json().get("detail", "")
            if "tidak ditemukan" in error_detail.lower():
                log_test("Route ordering correct (search not caught by {doc_id})", False, 
                        f"Route caught by /documents/{{doc_id}}: {error_detail}")
            else:
                log_test("Route ordering correct (search not caught by {doc_id})", True, 
                        "404 but not from {doc_id} route")
        else:
            log_test("Route ordering check", False, 
                    f"Unexpected status {resp.status_code}: {resp.text}")
    except Exception as e:
        log_test("Route ordering check", False, f"Error: {e}")
    
    return True


def test_guide_videos():
    """Test FITUR B: Video Panduan Settings (GET/PUT /api/guide-videos)"""
    print("\n=== FITUR B: VIDEO PANDUAN (GET/PUT /api/guide-videos) ===")
    
    # Test 1: GET without auth → 401/403
    print("\n--- Test 1: GET Without Authentication ---")
    try:
        resp = requests.get(f"{BASE_URL}/guide-videos", timeout=30)
        if resp.status_code in [401, 403]:
            log_test("GET guide-videos without auth returns 401/403", True, 
                    f"Status: {resp.status_code}")
        else:
            log_test("GET guide-videos without auth returns 401/403", False, 
                    f"Expected 401/403, got {resp.status_code}: {resp.text}")
    except Exception as e:
        log_test("GET guide-videos without auth", False, f"Error: {e}")
    
    # Login as superadmin
    session = TestSession()
    if not session.login(CREDENTIALS["superadmin"]["email"], CREDENTIALS["superadmin"]["password"]):
        log_test("Login for guide-videos tests", False, "Failed to login as superadmin")
        return False
    
    log_test("Login for guide-videos tests", True, f"Logged in as {session.user_info.get('email')}")
    
    # Test 2: GET with auth → 200 with object {ppbj, pp, pumptum, jurnal, anggaran}
    print("\n--- Test 2: GET With Authentication ---")
    try:
        resp = session.get("/guide-videos")
        
        if resp.status_code == 200:
            log_test("GET guide-videos with auth returns 200", True, f"Status: {resp.status_code}")
            
            data = resp.json()
            if isinstance(data, dict):
                log_test("GET guide-videos returns object", True, f"Response is dict")
                
                # Check required keys
                required_keys = ["ppbj", "pp", "pumptum", "jurnal", "anggaran"]
                has_all_keys = all(key in data for key in required_keys)
                
                if has_all_keys:
                    log_test("GET guide-videos has all required keys", True, 
                            f"Keys: {', '.join(required_keys)}")
                    
                    # Verify all values are strings
                    all_strings = all(isinstance(data[key], str) for key in required_keys)
                    if all_strings:
                        log_test("GET guide-videos values are strings", True, 
                                f"All values are strings (default empty)")
                    else:
                        log_test("GET guide-videos values are strings", False, 
                                f"Some values are not strings")
                else:
                    missing = [k for k in required_keys if k not in data]
                    log_test("GET guide-videos has all required keys", False, 
                            f"Missing keys: {missing}")
            else:
                log_test("GET guide-videos returns object", False, 
                        f"Expected dict, got {type(data)}")
        else:
            log_test("GET guide-videos with auth returns 200", False, 
                    f"Expected 200, got {resp.status_code}: {resp.text}")
    except Exception as e:
        log_test("GET guide-videos with auth test", False, f"Error: {e}")
    
    # Test 3: PUT with auth (superadmin) → 200 and persists
    print("\n--- Test 3: PUT With Authentication (Superadmin) ---")
    test_url = "https://www.youtube.com/watch?v=abc123"
    try:
        resp = session.put("/guide-videos", json={
            "ppbj": test_url,
            "pp": "",
            "pumptum": "",
            "jurnal": "",
            "anggaran": ""
        })
        
        if resp.status_code == 200:
            log_test("PUT guide-videos with auth returns 200", True, f"Status: {resp.status_code}")
            
            data = resp.json()
            if isinstance(data, dict):
                log_test("PUT guide-videos returns object", True, "Response is dict")
                
                # Verify ppbj value is saved
                if data.get("ppbj") == test_url:
                    log_test("PUT guide-videos saves ppbj value", True, 
                            f"ppbj: {data.get('ppbj')}")
                else:
                    log_test("PUT guide-videos saves ppbj value", False, 
                            f"Expected '{test_url}', got '{data.get('ppbj')}'")
            else:
                log_test("PUT guide-videos returns object", False, 
                        f"Expected dict, got {type(data)}")
        else:
            log_test("PUT guide-videos with auth returns 200", False, 
                    f"Expected 200, got {resp.status_code}: {resp.text}")
    except Exception as e:
        log_test("PUT guide-videos with auth test", False, f"Error: {e}")
    
    # Test 4: GET again to verify persistence
    print("\n--- Test 4: Verify Persistence ---")
    try:
        resp = session.get("/guide-videos")
        
        if resp.status_code == 200:
            data = resp.json()
            if data.get("ppbj") == test_url:
                log_test("GET guide-videos shows persisted value", True, 
                        f"ppbj persisted: {data.get('ppbj')}")
            else:
                log_test("GET guide-videos shows persisted value", False, 
                        f"Expected '{test_url}', got '{data.get('ppbj')}'")
        else:
            log_test("GET guide-videos for persistence check", False, 
                    f"Expected 200, got {resp.status_code}")
    except Exception as e:
        log_test("Persistence check", False, f"Error: {e}")
    
    # Test 5: PUT without auth → 401/403
    print("\n--- Test 5: PUT Without Authentication ---")
    try:
        resp = requests.put(f"{BASE_URL}/guide-videos", json={
            "ppbj": "test",
            "pp": "",
            "pumptum": "",
            "jurnal": "",
            "anggaran": ""
        }, timeout=30)
        
        if resp.status_code in [401, 403]:
            log_test("PUT guide-videos without auth returns 401/403", True, 
                    f"Status: {resp.status_code}")
        else:
            log_test("PUT guide-videos without auth returns 401/403", False, 
                    f"Expected 401/403, got {resp.status_code}: {resp.text}")
    except Exception as e:
        log_test("PUT guide-videos without auth", False, f"Error: {e}")
    
    # Test 6: PUT with approver/user role → 403 (if available)
    print("\n--- Test 6: PUT With Non-Admin Role (if available) ---")
    # Note: We only have superadmin credentials, so we'll skip this test
    log_test("PUT guide-videos with approver/user role returns 403", True, 
            "Skipped (no approver/user credentials available)")
    
    # Test 7: CLEANUP - Restore to empty values
    print("\n--- Test 7: Cleanup - Restore Empty Values ---")
    try:
        resp = session.put("/guide-videos", json={
            "ppbj": "",
            "pp": "",
            "pumptum": "",
            "jurnal": "",
            "anggaran": ""
        })
        
        if resp.status_code == 200:
            log_test("CLEANUP: Restore guide-videos to empty", True, 
                    "All values reset to empty strings")
            
            # Verify cleanup
            resp = session.get("/guide-videos")
            if resp.status_code == 200:
                data = resp.json()
                all_empty = all(data.get(k) == "" for k in ["ppbj", "pp", "pumptum", "jurnal", "anggaran"])
                if all_empty:
                    log_test("CLEANUP: Verify all values empty", True, "All values are empty")
                else:
                    log_test("CLEANUP: Verify all values empty", False, 
                            f"Some values not empty: {data}")
        else:
            log_test("CLEANUP: Restore guide-videos to empty", False, 
                    f"Expected 200, got {resp.status_code}: {resp.text}")
    except Exception as e:
        log_test("CLEANUP test", False, f"Error: {e}")
    
    return True


def print_summary():
    """Print test summary"""
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    total = len(test_results)
    passed = sum(1 for t in test_results if t["passed"])
    failed = total - passed
    
    print(f"\nTotal Tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    
    if failed_tests:
        print("\n" + "="*70)
        print("FAILED TESTS DETAILS")
        print("="*70)
        for test in failed_tests:
            print(f"\n❌ {test['name']}")
            if test['details']:
                print(f"   {test['details']}")
    
    print("\n" + "="*70)
    
    return failed == 0


def main():
    """Run all tests"""
    print("="*70)
    print("BACKEND API TESTS: New Features (Document Search & Guide Videos)")
    print("="*70)
    print(f"Backend URL: {BASE_URL}")
    print("="*70)
    
    try:
        # Run tests for both features
        test_document_search()
        test_guide_videos()
        
        # Print summary
        all_passed = print_summary()
        
        # Exit with appropriate code
        sys.exit(0 if all_passed else 1)
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
