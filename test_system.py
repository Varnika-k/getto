#!/usr/bin/env python3
"""
FCM Push Notification System - Test Script
Tests the complete flow: Database → Firebase → Android Device
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Server configuration
SERVER_URL = "http://localhost:5000"

def test_server_status():
    """Test if the Flask server is running"""
    print("🔍 Testing server status...")
    try:
        response = requests.get(f"{SERVER_URL}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Server is running: {data['message']}")
            print(f"🔥 Firebase status: {data['firebase_status']}")
            return True
        else:
            print(f"❌ Server error: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure 'python app.py' is running.")
        return False

def test_database_connection():
    """Test PostgreSQL database connection"""
    print("\n🗄️ Testing database connection...")
    try:
        response = requests.get(f"{SERVER_URL}/test-db")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Database connected: {data['message']}")
            print(f"📊 PostgreSQL version: {data.get('postgres_version', 'Unknown')}")
            return True
        else:
            print(f"❌ Database error: {response.json()}")
            return False
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def get_sample_notifications():
    """Fetch sample notifications from database"""
    print("\n📬 Fetching sample notifications...")
    try:
        response = requests.get(f"{SERVER_URL}/notifications")
        if response.status_code == 200:
            data = response.json()
            notifications = data['notifications']
            print(f"✅ Found {data['count']} notifications in database:")
            for i, notif in enumerate(notifications[:3], 1):  # Show first 3
                print(f"  {i}. {notif['title']}: {notif['body'][:50]}...")
            return notifications
        else:
            print(f"❌ Failed to fetch notifications: {response.json()}")
            return []
    except Exception as e:
        print(f"❌ Error fetching notifications: {e}")
        return []

def simulate_device_registration():
    """Simulate Android device registration"""
    print("\n📱 Simulating device registration...")
    
    # Dummy FCM token for testing (replace with real token from Android app)
    dummy_token = "dummy_fcm_token_for_testing_replace_with_real_token"
    
    data = {
        "fcm_token": dummy_token,
        "device_id": "test_android_device"
    }
    
    try:
        response = requests.post(f"{SERVER_URL}/register-device", json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Device registered: {result['message']}")
            return True
        else:
            print(f"❌ Registration failed: {response.json()}")
            return False
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return False

def test_notification_sending():
    """Test sending notification using database content"""
    print("\n🔔 Testing notification sending...")
    
    # Send notification using stored database content
    data = {
        "notification_id": 1,  # Use first notification from database
        "target_token": "dummy_fcm_token_for_testing_replace_with_real_token"
    }
    
    try:
        response = requests.post(f"{SERVER_URL}/send-notification", json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Notification sent: {result['message']}")
            print(f"📊 Successful sends: {result['successful_sends']}")
            print(f"❌ Failed sends: {result['failed_sends']}")
            return True
        else:
            print(f"❌ Send failed: {response.json()}")
            return False
    except Exception as e:
        print(f"❌ Send error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 FCM Push Notification System - Test Suite")
    print("=" * 50)
    
    # Test server
    if not test_server_status():
        print("\n❌ Server test failed. Please start the server first:")
        print("   python app.py")
        return
    
    # Test database
    if not test_database_connection():
        print("\n❌ Database test failed. Check your .env file and ensure PostgreSQL is running.")
        return
    
    # Get notifications
    notifications = get_sample_notifications()
    if not notifications:
        print("\n❌ No notifications found. Run setup_database.py first.")
        return
    
    # Test device registration
    simulate_device_registration()
    
    # Test notification sending
    test_notification_sending()
    
    print("\n" + "=" * 50)
    print("🎉 System test complete!")
    print("\n📱 Next Steps:")
    print("1. Open Android app in Android Studio")
    print("2. Add google-services.json to app folder")
    print("3. Run the app on your device")
    print("4. Get FCM token and register device")
    print("5. Send real notifications to your device!")

if __name__ == "__main__":
    main()