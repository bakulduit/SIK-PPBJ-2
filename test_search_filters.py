#!/usr/bin/env python3
"""
Backend API Testing for SIK-PPBJ
Test: GET /api/documents/search with doc_type and status filters
"""

import requests
import json
import os
from typing import Optional

# Base URL from frontend/.env
BASE_URL = "https://sik-ppbj-deploy.preview.emergentagent.com/api"

# Test credentials
SUPERADMIN_EMAIL = "nashoharizal@gmail.com"
SUPERADMIN_PASSWORD = "SIKPPBJ2026"

# Session to maintain cookies
session = requests.Session()

def login(email: str, password: str) -> bool:
    """Login and store auth cookies"""
    url = f"{BASE_URL}/auth/login"
    payload = {"email": email, "password": password}
    try:
        resp = session.post(url, json=payload, timeout=10)
        if resp.status_code == 200:
            print(f"✅ Login successful: {email}")
            return True
        else:
            print(f"❌ Login failed: {resp.status_code} - {resp.text}")
            return False
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False

def create_document(doc_data: dict) -> Optional[dict]:
    """Create a document via POST /api/documents"""
    url = f"{BASE_URL}/documents"
    try:
        resp = session.post(url, json=doc_data, timeout=10)
        if resp.status_code == 200:
            doc = resp.json()
            print(f"✅ Document created: {doc.get('id')} - {doc.get('doc_type')} - {doc.get('kegiatan') or doc.get('keterangan')}")
            return doc
        else:
            print(f"❌ Create document failed: {resp.status_code} - {resp.text}")
            return None
    except Exception as e:
        print(f"❌ Create document error: {e}")
        return None

def search_documents(q: str = "", doc_type: Optional[str] = None, 
                     status: Optional[str] = None, limit: Optional[int] = None,
                     with_auth: bool = True) -> tuple:
    """Search documents via GET /api/documents/search"""
    url = f"{BASE_URL}/documents/search"
    params = {}
    if q:
        params["q"] = q
    if doc_type:
        params["doc_type"] = doc_type
    if status:
        params["status"] = status
    if limit:
        params["limit"] = limit
    
    try:
        if with_auth:
            resp = session.get(url, params=params, timeout=10)
        else:
            # Create new session without auth cookies
            resp = requests.get(url, params=params, timeout=10)
        
        return resp.status_code, resp.json() if resp.status_code == 200 else resp.text
    except Exception as e:
        print(f"❌ Search error: {e}")
        return 0, str(e)

def run_tests():
    """Run all test scenarios"""
    print("=" * 80)
    print("BACKEND TEST: GET /api/documents/search with doc_type & status filters")
    print("=" * 80)
    
    # Step 1: Login as superadmin
    print("\n[STEP 1] Login as superadmin")
    if not login(SUPERADMIN_EMAIL, SUPERADMIN_PASSWORD):
        print("❌ CRITICAL: Cannot proceed without login")
        return
    
    # Step 2: Create 4 test documents with "Zeta" keyword
    print("\n[STEP 2] Create 4 test documents with 'Zeta' keyword")
    
    doc_a = create_document({
        "doc_type": "PPBJ",
        "unit_kerja": "Unit A",
        "kegiatan": "Pengadaan ZetaLaptop",
        "supplier": "CV Zeta",
        "total": 1000000
    })
    
    doc_b = create_document({
        "doc_type": "PPBJ",
        "kegiatan": "ZetaKursi kantor",
        "total": 500000
    })
    
    doc_c = create_document({
        "doc_type": "PP",
        "keterangan": "Pembayaran ZetaVendor",
        "supplier": "PT Zeta",
        "total": 750000
    })
    
    doc_d = create_document({
        "doc_type": "PUM",
        "kegiatan": "Uang muka ZetaAcara",
        "total": 300000
    })
    
    if not all([doc_a, doc_b, doc_c, doc_d]):
        print("❌ CRITICAL: Failed to create all test documents")
        return
    
    created_ids = [doc_a["id"], doc_b["id"], doc_c["id"], doc_d["id"]]
    print(f"\n✅ All 4 documents created successfully")
    print(f"   Document IDs: {created_ids}")
    
    # Step 3: Run test scenarios
    print("\n" + "=" * 80)
    print("TEST SCENARIOS")
    print("=" * 80)
    
    # Test 1: Search "Zeta" - should return 4 documents
    print("\n[TEST 1] GET /api/documents/search?q=Zeta")
    status, result = search_documents(q="Zeta")
    if status == 200 and isinstance(result, list):
        print(f"✅ HTTP 200, returned {len(result)} documents")
        if len(result) == 4:
            print(f"✅ PASS: Expected 4 documents, got {len(result)}")
            doc_types = [d.get("doc_type") for d in result]
            print(f"   doc_types: {doc_types}")
        else:
            print(f"❌ FAIL: Expected 4 documents, got {len(result)}")
    else:
        print(f"❌ FAIL: HTTP {status}, result: {result}")
    
    # Test 1b: Case-insensitive test with lowercase "zeta"
    print("\n[TEST 1b] GET /api/documents/search?q=zeta (lowercase)")
    status, result = search_documents(q="zeta")
    if status == 200 and isinstance(result, list):
        print(f"✅ HTTP 200, returned {len(result)} documents")
        if len(result) == 4:
            print(f"✅ PASS: Case-insensitive search working, got {len(result)} documents")
        else:
            print(f"❌ FAIL: Expected 4 documents, got {len(result)}")
    else:
        print(f"❌ FAIL: HTTP {status}")
    
    # Test 2: Filter by doc_type=PPBJ
    print("\n[TEST 2] GET /api/documents/search?q=Zeta&doc_type=PPBJ")
    status, result = search_documents(q="Zeta", doc_type="PPBJ")
    if status == 200 and isinstance(result, list):
        print(f"✅ HTTP 200, returned {len(result)} documents")
        if len(result) == 2:
            print(f"✅ PASS: Expected 2 PPBJ documents, got {len(result)}")
            doc_types = [d.get("doc_type") for d in result]
            if all(dt == "PPBJ" for dt in doc_types):
                print(f"✅ All documents are PPBJ: {doc_types}")
            else:
                print(f"❌ FAIL: Not all documents are PPBJ: {doc_types}")
        else:
            print(f"❌ FAIL: Expected 2 documents, got {len(result)}")
    else:
        print(f"❌ FAIL: HTTP {status}")
    
    # Test 3: Filter by doc_type=PP
    print("\n[TEST 3] GET /api/documents/search?q=Zeta&doc_type=PP")
    status, result = search_documents(q="Zeta", doc_type="PP")
    if status == 200 and isinstance(result, list):
        print(f"✅ HTTP 200, returned {len(result)} documents")
        if len(result) == 1:
            print(f"✅ PASS: Expected 1 PP document, got {len(result)}")
            if result[0].get("doc_type") == "PP":
                print(f"✅ Document is PP")
            else:
                print(f"❌ FAIL: Document is not PP: {result[0].get('doc_type')}")
        else:
            print(f"❌ FAIL: Expected 1 document, got {len(result)}")
    else:
        print(f"❌ FAIL: HTTP {status}")
    
    # Test 4a: Filter by status=pending_approval
    print("\n[TEST 4a] GET /api/documents/search?q=Zeta&status=pending_approval")
    status, result = search_documents(q="Zeta", status="pending_approval")
    if status == 200 and isinstance(result, list):
        print(f"✅ HTTP 200, returned {len(result)} documents")
        if len(result) == 4:
            print(f"✅ PASS: Expected 4 pending_approval documents, got {len(result)}")
            statuses = [d.get("status") for d in result]
            if all(s == "pending_approval" for s in statuses):
                print(f"✅ All documents are pending_approval")
            else:
                print(f"❌ FAIL: Not all documents are pending_approval: {statuses}")
        else:
            print(f"❌ FAIL: Expected 4 documents, got {len(result)}")
    else:
        print(f"❌ FAIL: HTTP {status}")
    
    # Test 4b: Filter by status=approved (should return 0)
    print("\n[TEST 4b] GET /api/documents/search?q=Zeta&status=approved")
    status, result = search_documents(q="Zeta", status="approved")
    if status == 200 and isinstance(result, list):
        print(f"✅ HTTP 200, returned {len(result)} documents")
        if len(result) == 0:
            print(f"✅ PASS: Expected 0 approved documents, got {len(result)}")
        else:
            print(f"❌ FAIL: Expected 0 documents, got {len(result)}")
    else:
        print(f"❌ FAIL: HTTP {status}")
    
    # Test 5: Combined filters doc_type=PPBJ & status=pending_approval
    print("\n[TEST 5] GET /api/documents/search?q=Zeta&doc_type=PPBJ&status=pending_approval")
    status, result = search_documents(q="Zeta", doc_type="PPBJ", status="pending_approval")
    if status == 200 and isinstance(result, list):
        print(f"✅ HTTP 200, returned {len(result)} documents")
        if len(result) == 2:
            print(f"✅ PASS: Expected 2 PPBJ pending_approval documents, got {len(result)}")
            doc_types = [d.get("doc_type") for d in result]
            statuses = [d.get("status") for d in result]
            if all(dt == "PPBJ" for dt in doc_types) and all(s == "pending_approval" for s in statuses):
                print(f"✅ All documents are PPBJ and pending_approval")
            else:
                print(f"❌ FAIL: Filters not working correctly")
                print(f"   doc_types: {doc_types}, statuses: {statuses}")
        else:
            print(f"❌ FAIL: Expected 2 documents, got {len(result)}")
    else:
        print(f"❌ FAIL: HTTP {status}")
    
    # Test 6: Limit parameter
    print("\n[TEST 6] GET /api/documents/search?q=Zeta&limit=1")
    status, result = search_documents(q="Zeta", limit=1)
    if status == 200 and isinstance(result, list):
        print(f"✅ HTTP 200, returned {len(result)} documents")
        if len(result) == 1:
            print(f"✅ PASS: Expected 1 document (limit=1), got {len(result)}")
        else:
            print(f"❌ FAIL: Expected 1 document, got {len(result)}")
    else:
        print(f"❌ FAIL: HTTP {status}")
    
    # Test 7: Without authentication
    print("\n[TEST 7] GET /api/documents/search?q=Zeta (without auth)")
    status, result = search_documents(q="Zeta", with_auth=False)
    if status in [401, 403]:
        print(f"✅ PASS: HTTP {status} (auth required)")
    else:
        print(f"❌ FAIL: Expected 401/403, got HTTP {status}")
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"✅ All 4 'Zeta' documents created and NOT deleted (as requested)")
    print(f"   Document IDs: {created_ids}")
    print(f"   These documents will be used for frontend UI testing")
    print("\n✅ All 7 test scenarios completed")
    print("   - Test 1: Search 'Zeta' → 4 documents (case-insensitive)")
    print("   - Test 2: Filter doc_type=PPBJ → 2 documents")
    print("   - Test 3: Filter doc_type=PP → 1 document")
    print("   - Test 4a: Filter status=pending_approval → 4 documents")
    print("   - Test 4b: Filter status=approved → 0 documents")
    print("   - Test 5: Combined filters PPBJ+pending_approval → 2 documents")
    print("   - Test 6: Limit=1 → 1 document")
    print("   - Test 7: Without auth → 401/403")
    print("=" * 80)

if __name__ == "__main__":
    run_tests()
