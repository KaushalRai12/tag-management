"""
Test script for Flask Tag Management System endpoints
"""

import requests
import json
import os
import time
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000"
TEST_IMAGE_PATH = "test_image.jpg"

def test_health_check():
    """Test health check endpoint"""
    print("Testing health check endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_add_tag():
    """Test add tag endpoint"""
    print("\nTesting add tag endpoint...")
    try:
        data = {
            "tag_mac_address": "AA:BB:CC:DD:EE:FF"
        }
        response = requests.post(
            f"{BASE_URL}/add_tag",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 201:
            return response.json().get("tag_uuid")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_add_duplicate_tag():
    """Test adding duplicate tag"""
    print("\nTesting duplicate tag addition...")
    try:
        data = {
            "tag_mac_address": "AA:BB:CC:DD:EE:FF"
        }
        response = requests.post(
            f"{BASE_URL}/add_tag",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 400
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_update_tag_with_image(tag_uuid):
    """Test update tag with image"""
    print(f"\nTesting update tag with image for UUID: {tag_uuid}")
    
    # Create a simple test image if it doesn't exist
    if not os.path.exists(TEST_IMAGE_PATH):
        print("Creating test image...")
        # Create a proper 1x1 pixel JPEG using PIL
        try:
            from PIL import Image
            # Create a 1x1 pixel red image
            img = Image.new('RGB', (1, 1), color='red')
            img.save(TEST_IMAGE_PATH, 'JPEG')
        except ImportError:
            # Fallback: create a minimal JPEG if PIL is not available
            with open(TEST_IMAGE_PATH, "wb") as f:
                # More complete JPEG header
                f.write(b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9')
    
    try:
        with open(TEST_IMAGE_PATH, "rb") as f:
            files = {"image": (TEST_IMAGE_PATH, f, "image/jpeg")}
            response = requests.post(
                f"{BASE_URL}/update_tag/{tag_uuid}",
                files=files
            )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_update_nonexistent_tag():
    """Test updating non-existent tag"""
    print("\nTesting update non-existent tag...")
    try:
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        with open(TEST_IMAGE_PATH, "rb") as f:
            files = {"image": f}
            response = requests.post(
                f"{BASE_URL}/update_tag/{fake_uuid}",
                files=files
            )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 404
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_add_tag_different_mac():
    """Test adding tag with different MAC address"""
    print("\nTesting add tag with different MAC address...")
    try:
        data = {
            "tag_mac_address": "11:22:33:44:55:66"
        }
        response = requests.post(
            f"{BASE_URL}/add_tag",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 201:
            return response.json().get("tag_uuid")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def wait_for_service():
    """Wait for the service to be ready"""
    print("⏳ Waiting for service to be ready...")
    max_retries = 30
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                print("✅ Service is ready!")
                return True
        except:
            pass
        
        if attempt < max_retries - 1:
            print(f"⏳ Attempt {attempt + 1}/{max_retries}, retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
    
    print("❌ Service not ready after maximum retries")
    return False

def main():
    """Run all tests"""
    print("🚀 Starting Flask Tag Management System Tests")
    print("=" * 60)
    
    # Wait for service to be ready
    if not wait_for_service():
        print("❌ Cannot proceed with tests - service not available")
        return
    
    # Test health check
    health_ok = test_health_check()
    
    # Test add tag
    tag_uuid = test_add_tag()
    
    # Test duplicate tag
    duplicate_ok = test_add_duplicate_tag()
    
    # Test add different MAC
    tag_uuid2 = test_add_tag_different_mac()
    
    # Test update tag with image
    if tag_uuid2:  # Use the second tag UUID
        update_ok = test_update_tag_with_image(tag_uuid2)
    else:
        update_ok = False
    
    # Test update non-existent tag
    nonexistent_ok = test_update_nonexistent_tag()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Health Check: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"Add Tag: {'✅ PASS' if tag_uuid else '❌ FAIL'}")
    print(f"Duplicate Tag: {'✅ PASS' if duplicate_ok else '❌ FAIL'}")
    print(f"Add Different MAC: {'✅ PASS' if tag_uuid2 else '❌ FAIL'}")
    print(f"Update Tag: {'✅ PASS' if update_ok else '❌ FAIL'}")
    print(f"Non-existent Tag: {'✅ PASS' if nonexistent_ok else '❌ FAIL'}")
    
    # Overall result
    all_passed = all([health_ok, tag_uuid, duplicate_ok, tag_uuid2, update_ok, nonexistent_ok])
    print(f"\n🎯 Overall Result: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    # Cleanup
    if os.path.exists(TEST_IMAGE_PATH):
        try:
            os.remove(TEST_IMAGE_PATH)
        except:
            pass

if __name__ == "__main__":
    main()
