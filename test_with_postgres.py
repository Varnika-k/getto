#!/usr/bin/env python3
"""
Test script for FCM Push Notification System with PostgreSQL
Run this after starting the Flask server to test the functionality
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:5000"
TEST_FCM_TOKEN = "YOUR_FCM_TOKEN_HERE"  # Replace with actual FCM token from Android app

def test_server_status():
    """Test if server is running"""
    print("🔄 Testing server status...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print("✅ Server is running")
            print(f"   Firebase: {data['firebase_status']}")
            print(f"   Database: {data['database_status']}")
            return True
        else:
            print(f"❌ Server responded with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Server connection failed: {e}")
        return False

def test_database_connection():
    """Test database connection"""
    print("\n🔄 Testing database connection...")
    try:
        response = requests.get(f"{BASE_URL}/test-db")
        if response.status_code == 200:
            data = response.json()
            print("✅ Database connection successful")
            print(f"   PostgreSQL Version: {data.get('postgresql_version', 'Unknown')}")
            return True
        else:
            print(f"❌ Database test failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Database test error: {e}")
        return False

def test_fetch_notifications():
    """Test fetching notifications from database"""
    print("\n🔄 Testing notification fetching...")
    try:
        response = requests.get(f"{BASE_URL}/notifications")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Retrieved {data['count']} notifications from database")
            if data['notifications']:
                print("   Sample notifications:")
                for i, notif in enumerate(data['notifications'][:3], 1):
                    print(f"   {i}. {notif['title']}: {notif['body'][:50]}...")
            return True
        else:
            print(f"❌ Failed to fetch notifications: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Notification fetch error: {e}")
        return False

def test_create_notification():
    """Test creating a new notification"""
    print("\n🔄 Testing notification creation...")
    try:
        notification_data = {
            "title": "Test Notification",
            "body": "This is a test notification created via API",
            "metadata": {"test": True, "created_by": "test_script"},
            "priority": "high",
            "type": "test"
        }
        
        response = requests.post(f"{BASE_URL}/notifications", 
                               json=notification_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Created notification with ID: {data['notification_id']}")
            return data['notification_id']
        else:
            print(f"❌ Failed to create notification: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Notification creation error: {e}")
        return None

def test_device_registration():
    """Test device registration"""
    print("\n🔄 Testing device registration...")
    if TEST_FCM_TOKEN == "YOUR_FCM_TOKEN_HERE":
        print("⚠️  Please update TEST_FCM_TOKEN in the script with your actual FCM token")
        print("   You can get this from your Android app logs")
        return False
    
    try:
        device_data = {
            "fcm_token": TEST_FCM_TOKEN,
            "device_id": "test_device_1"
        }
        
        response = requests.post(f"{BASE_URL}/register-device", json=device_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Device registered successfully")
            print(f"   Total devices: {data['total_devices']}")
            return True
        else:
            print(f"❌ Device registration failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Device registration error: {e}")
        return False

def test_send_notification():
    """Test sending notification"""
    print("\n🔄 Testing notification sending...")
    if TEST_FCM_TOKEN == "YOUR_FCM_TOKEN_HERE":
        print("⚠️  Skipping notification send test - FCM token not configured")
        return False
    
    try:
        notification_data = {
            "title": "Test Push Notification",
            "body": "This notification was sent from the PostgreSQL-integrated server!",
            "metadata": {"sent_from": "test_script"},
            "target_token": TEST_FCM_TOKEN
        }
        
        response = requests.post(f"{BASE_URL}/send-notification", 
                               json=notification_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Notification sent successfully")
            print(f"   Status: {data['status']}")
            print(f"   Successful sends: {data['successful_sends']}")
            print(f"   Failed sends: {data['failed_sends']}")
            return True
        else:
            print(f"❌ Notification sending failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Notification sending error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("FCM Push Notification System - PostgreSQL Integration Test")
    print("=" * 60)
    
    # Test server status
    if not test_server_status():
        print("\n❌ Server is not running. Please start the Flask server first:")
        print("   python app_with_postgres.py")
        return
    
    # Test database
    test_database_connection()
    
    # Test notifications
    test_fetch_notifications()
    
    # Test notification creation
    new_notification_id = test_create_notification()
    
    # Test device registration and notification sending
    if test_device_registration():
        test_send_notification()
    
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("1. Update your .env file with correct database credentials")
    print("2. Make sure PostgreSQL is running on port 5433")
    print("3. Get your FCM token from the Android app and update TEST_FCM_TOKEN")
    print("4. Run this test script to verify everything works")
    print("\n🎉 PostgreSQL integration is ready for testing!")
    print("=" * 60)

if __name__ == "__main__":
    main()