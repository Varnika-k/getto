#!/usr/bin/env python3
"""
Demo script to test FCM push notifications with real token
This script will help you test the complete flow
"""

import requests
import json
import time

# Configuration
SERVER_URL = "http://localhost:5000"

def test_with_real_token():
    """Test the FCM system with a real token"""
    
    print("🚀 FCM Push Notification System - Real Token Test")
    print("=" * 60)
    
    # Step 1: Get FCM token from user
    print("\n📱 To get a real FCM token, choose ONE of these methods:")
    print("   1. Firebase Console: https://console.firebase.google.com/project/getto-59778/messaging")
    print("   2. Open the FCM Token Generator: fcm_token_generator.html")
    print("   3. Use a mobile app with your Firebase project")
    print("\n💡 For DEMO purposes, I'll show you what happens with different token types:")
    
    # Test different scenarios
    test_scenarios = [
        {
            "name": "Invalid Demo Token",
            "token": "demo_token_12345",
            "device_id": "demo_device",
            "expected": "Should fail with 'not a valid FCM registration token'"
        },
        {
            "name": "Realistic Format Token (Still Invalid)", 
            "token": "fZ1234567890:APA91bE_xampleTokenThatLooksRealButIsNotWorkingForTestingPurposes123456789",
            "device_id": "test_device",
            "expected": "Should fail with FCM error but show proper format handling"
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n🧪 Testing: {scenario['name']}")
        print(f"📝 Expected: {scenario['expected']}")
        print("-" * 50)
        
        # Register device
        register_response = register_device(scenario['token'], scenario['device_id'])
        if register_response:
            print("✅ Device registration successful")
            
            # Send notification
            notification_response = send_notification(1, scenario['token'])
            if notification_response:
                if notification_response.get('successful_sends', 0) > 0:
                    print("🎉 NOTIFICATION SENT SUCCESSFULLY!")
                else:
                    print("⚠️ Firebase rejected token (expected for demo tokens)")
                    errors = notification_response.get('errors', [])
                    if errors:
                        print(f"🔍 Error details: {errors[0]}")
        
        print()
    
    print("\n" + "=" * 60)
    print("🎯 NEXT STEPS TO GET REAL NOTIFICATIONS:")
    print("=" * 60)
    print("1. Get a REAL FCM token using Firebase Console")
    print("2. Replace 'YOUR_REAL_TOKEN_HERE' in the code below")
    print("3. Run this script again with your real token")
    print("\n📋 Command to test with your real token:")
    print("""
# Register your real device
curl -X POST http://localhost:5000/register-device \\
  -H "Content-Type: application/json" \\
  -d '{
    "fcm_token": "YOUR_REAL_FCM_TOKEN_HERE",
    "device_id": "my_real_device"
  }'

# Send notification to your device
curl -X POST http://localhost:5000/send-notification \\
  -H "Content-Type: application/json" \\
  -d '{
    "notification_id": 1,
    "target_token": "YOUR_REAL_FCM_TOKEN_HERE"
  }'
    """)
    
    # If user wants to input real token
    print("\n🔧 Want to test with your real token now? (y/n)")
    user_input = input().strip().lower()
    if user_input == 'y':
        real_token = input("📱 Paste your real FCM token: ").strip()
        if real_token and len(real_token) > 50:  # FCM tokens are long
            print("\n🚀 Testing with your real token...")
            test_real_token(real_token)
        else:
            print("❌ Invalid token format. Please ensure you copied the full token.")

def register_device(fcm_token, device_id):
    """Register device with server"""
    try:
        response = requests.post(f"{SERVER_URL}/register-device", 
                               json={"fcm_token": fcm_token, "device_id": device_id})
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Device '{device_id}' registered successfully")
            return data
        else:
            print(f"❌ Registration failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return None

def send_notification(notification_id, target_token):
    """Send notification via server"""
    try:
        response = requests.post(f"{SERVER_URL}/send-notification",
                               json={"notification_id": notification_id, "target_token": target_token})
        if response.status_code == 200:
            data = response.json()
            print(f"📤 Notification sent - Success: {data['successful_sends']}, Failed: {data['failed_sends']}")
            return data
        else:
            print(f"❌ Send failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Send error: {e}")
        return None

def test_real_token(real_token):
    """Test with a real FCM token"""
    print(f"🔄 Testing real token: {real_token[:20]}...")
    
    # Register real device
    register_response = register_device(real_token, "real_device_test")
    if register_response:
        print("✅ Real device registered!")
        
        # Send welcome notification
        print("📤 Sending welcome notification...")
        notification_response = send_notification(1, real_token)
        
        if notification_response and notification_response.get('successful_sends', 0) > 0:
            print("🎉 SUCCESS! Check your device for the notification!")
        else:
            print("⚠️ Notification may not have reached device. Check token validity.")

def check_server_status():
    """Check if server is running"""
    try:
        response = requests.get(f"{SERVER_URL}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Server running - Firebase: {data['firebase_status']}")
            return True
        else:
            print(f"❌ Server responded with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Server connection failed: {e}")
        print(f"💡 Make sure the Flask server is running on {SERVER_URL}")
        return False

if __name__ == "__main__":
    # Check server first
    if check_server_status():
        test_with_real_token()
    else:
        print("\n🔧 Please start the Flask server first:")
        print("   python app_simple.py")