"""
Test script for Text Humanizer API
Make sure the server is running before running this script
"""

import requests
import json

BASE_URL = "http://localhost:8000"

# Test text
test_text = """Born into a wealthy family in Pretoria, South Africa, Musk emigrated in 1989 to Canada; he had obtained Canadian citizenship at birth through his Canadian-born mother."""

# Test user ID
test_user_id = "test_user_123"

print("=" * 80)
print("Testing Text Humanizer API")
print("=" * 80)

# Test 1: Detect AI
print("\n[Test 1] Detecting AI content...")
print("-" * 80)

detect_response = requests.post(
    f"{BASE_URL}/detect-ai",
    json={
        "text": test_text,
        "user_id": test_user_id
    }
)

if detect_response.status_code == 200:
    result = detect_response.json()
    print(f"\n✓ AI Detection Results:")
    print(f"  - Score: {result.get('score')}")
    print(f"  - Length: {result.get('length')}")
    print(f"  - Readability: {result.get('readability_score')}")
    print(f"  - Credits Remaining: {result.get('credits_remaining')}")
    
    # Show usage info if available
    if 'usage_info' in result:
        usage = result['usage_info']
        print(f"\nUsage Info:")
        print(f"  - Word Count: {usage.get('word_count')}")
        print(f"  - Total Usage: {usage.get('total_usage')}/{usage.get('usage_limit')}")
        print(f"  - Remaining: {usage.get('remaining_usage')}")
else:
    print(f"✗ Error: {detect_response.status_code}")
    print(detect_response.text)

# Test 2: Humanize Text
print("\n[Test 2] Humanizing text...")
print("-" * 80)

humanize_response = requests.post(
    f"{BASE_URL}/humanize",
    json={
        "text": test_text,
        "user_id": test_user_id
    }
)

if humanize_response.status_code == 200:
    result = humanize_response.json()
    print(f"\n✓ Humanization Results:")
    print(f"\nOriginal:")
    print(result.get('original_text'))
    print(f"\nHumanized:")
    print(result.get('humanized_text'))
    print(f"\nUsage Stats:")
    print(f"  - Word Count: {result.get('word_count')}")
    print(f"  - Total Usage: {result.get('total_usage')}/{result.get('usage_limit')}")
    print(f"  - Remaining: {result.get('remaining_usage')}")
    print(f"\nProcessed {len(result.get('sentences', []))} sentences")
else:
    print(f"✗ Error: {humanize_response.status_code}")
    print(humanize_response.text)

# Test 3: Get User Usage
print("\n[Test 3] Getting user usage...")
print("-" * 80)

usage_response = requests.get(f"{BASE_URL}/user-usage/{test_user_id}")

if usage_response.status_code == 200:
    result = usage_response.json()
    print(f"\n✓ User Usage Stats:")
    print(f"  - User ID: {result.get('user_id')}")
    print(f"  - Word Count: {result.get('word_count')}")
    print(f"  - Token Usage: {result.get('token_usage')}")
    print(f"  - Usage Limit: {result.get('usage_limit')}")
    print(f"  - Remaining: {result.get('remaining_usage')}")
    print(f"  - Usage Percentage: {result.get('usage_percentage'):.2f}%")
else:
    print(f"✗ Error: {usage_response.status_code}")
    print(usage_response.text)

# Test 4: Update Usage Limit (Admin only)
print("\n[Test 4] Updating usage limit...")
print("-" * 80)

ADMIN_TOKEN = input("Enter your admin token (or press Enter to skip): ")

if ADMIN_TOKEN:
    update_response = requests.post(
        f"{BASE_URL}/update-limit",
        json={
            "user_id": test_user_id,
            "credits_to_add": 50,
            "admin_token": ADMIN_TOKEN
        }
    )
    
    if update_response.status_code == 200:
        result = update_response.json()
        print(f"\n✓ Credits Added:")
        print(f"  - User ID: {result.get('user_id')}")
        print(f"  - Credits Added: {result.get('credits_added')}")
        print(f"  - Old Limit: {result.get('old_limit')}")
        print(f"  - New Limit: {result.get('new_limit')}")
        print(f"  - Current Usage: {result.get('current_usage')}")
        print(f"  - Message: {result.get('message')}")
    else:
        print(f"✗ Error: {update_response.status_code}")
        print(update_response.text)
else:
    print("Skipping limit update test (no admin token provided)")

print("\n" + "=" * 80)
print("Testing complete!")
print("=" * 80)
