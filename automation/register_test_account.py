"""
register_test_account.py
Run ONCE before executing the test suite to create the test account.

Usage:
    python register_test_account.py
"""

import sys
import requests

BASE = "https://practice.expandtesting.com/notes/api"

EMAIL    = "capstone_tester@example.com"
PASSWORD = "Test@12345!"
NAME     = "Capstone Tester"

def register():
    resp = requests.post(
        f"{BASE}/users/register",
        json={"name": NAME, "email": EMAIL, "password": PASSWORD},
        timeout=10,
    )
    body = resp.json()
    if resp.status_code == 201 or (resp.status_code == 200 and body.get("success")):
        print(f"[OK] Registered: {EMAIL}")
    elif resp.status_code == 409 or "already exists" in str(body).lower():
        print(f"[OK] Account already exists: {EMAIL} - you are ready to run tests.")
    else:
        print(f"[FAIL] Registration failed: {resp.status_code} - {body}")
        sys.exit(1)

def verify_login():
    resp = requests.post(
        f"{BASE}/users/login",
        json={"email": EMAIL, "password": PASSWORD},
        timeout=10,
    )
    if resp.status_code == 200 and resp.json().get("data", {}).get("token"):
        print(f"[OK] Login verified - token acquired.")
    else:
        print(f"[FAIL] Login check failed: {resp.status_code} - {resp.text[:200]}")
        sys.exit(1)

if __name__ == "__main__":
    print("--- Notes App Test Account Setup ---")
    register()
    verify_login()
    print("\nSetup complete. Run: pytest")
