from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, messaging
import os
from dotenv import load_dotenv
import json
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Sample notifications (without database)
SAMPLE_NOTIFICATIONS = [
    {
        "id": 1,
        "title": "Welcome!",
        "body": "Welcome to our FCM notification system!",
        "metadata": {"type": "welcome", "priority": "high"}
    },
    {
        "id": 2,
        "title": "System Update",
        "body": "Your system has been updated successfully.",
        "metadata": {"type": "system", "priority": "medium"}
    },
    {
        "id": 3,
        "title": "Daily Reminder",
        "body": "Don't forget to check your dashboard today.",
        "metadata": {"type": "reminder", "priority": "low"}
    },
    {
        "id": 4,
        "title": "Security Alert",
        "body": "New login detected from unknown device.",
        "metadata": {"type": "security", "priority": "high"}
    }
]

# In-memory device storage (for demo)
device_tokens = {}

# Initialize Firebase Admin SDK
def initialize_firebase():
    try:
        service_account_path = os.getenv('FIREBASE_SERVICE_ACCOUNT_KEY', 'firebase-service-account.json')
        if not os.path.exists(service_account_path):
            print(f"WARNING: Firebase service account key not found at: {service_account_path}")
            print("To fix this:")
            print("  1. Go to Firebase Console")
            print("  2. Project Settings -> Service accounts")
            print("  3. Generate new private key")
            print("  4. Save as firebase-service-account.json")
            return False
        
        cred = credentials.Certificate(service_account_path)
        firebase_admin.initialize_app(cred)
        print("SUCCESS: Firebase initialized successfully")
        return True
    except Exception as e:
        print(f"ERROR: Firebase initialization failed: {e}")
        return False

# Initialize Firebase on startup
firebase_initialized = initialize_firebase()

@app.route('/')
def home():
    return jsonify({
        "message": "FCM Push Notification Server (Simple Version)",
        "status": "running",
        "firebase_status": "initialized" if firebase_initialized else "not initialized",
        "note": "This version uses in-memory storage for demo purposes",
        "endpoints": [
            "/notifications - GET (fetch sample notifications)",
            "/send-notification - POST (send push notification)",
            "/register-device - POST (register FCM token)",
            "/devices - GET (show registered devices)"
        ]
    })

@app.route('/notifications', methods=['GET'])
def get_notifications():
    return jsonify({
        "status": "success",
        "notifications": SAMPLE_NOTIFICATIONS,
        "count": len(SAMPLE_NOTIFICATIONS),
        "note": "Sample notifications (no database required)"
    })

@app.route('/devices', methods=['GET'])
def get_devices():
    return jsonify({
        "status": "success",
        "devices": device_tokens,
        "count": len(device_tokens)
    })

@app.route('/register-device', methods=['POST'])
def register_device():
    data = request.get_json()
    fcm_token = data.get('fcm_token')
    device_id = data.get('device_id', 'unknown')
    
    if not fcm_token:
        return jsonify({"error": "FCM token is required"}), 400
    
    # Store in memory (for demo)
    device_tokens[device_id] = {
        "fcm_token": fcm_token,
        "registered_at": datetime.now().isoformat(),
        "active": True
    }
    
    return jsonify({
        "status": "success",
        "message": "Device registered successfully",
        "device_id": device_id,
        "total_devices": len(device_tokens)
    })

@app.route('/send-notification', methods=['POST'])
def send_notification():
    if not firebase_initialized:
        return jsonify({"error": "Firebase not initialized. Please add firebase-service-account.json"}), 500
    
    data = request.get_json()
    notification_id = data.get('notification_id')
    target_token = data.get('target_token')  # Optional: specific device token
    
    # Get notification data
    if notification_id:
        notification_data = next((n for n in SAMPLE_NOTIFICATIONS if n['id'] == notification_id), None)
        if not notification_data:
            return jsonify({"error": "Notification not found"}), 404
        title, body, metadata = notification_data['title'], notification_data['body'], notification_data['metadata']
    else:
        # Use provided data
        title = data.get('title', 'Test Notification')
        body = data.get('body', 'This is a test notification')
        metadata = data.get('metadata', {})
    
    # Get target tokens
    tokens = []
    if target_token:
        tokens = [target_token]
    else:
        # Get all registered device tokens
        tokens = [device['fcm_token'] for device in device_tokens.values() if device['active']]
    
    if not tokens:
        return jsonify({
            "error": "No target devices found",
            "suggestion": "Register a device first using /register-device"
        }), 400
    
    # Send notifications
    successful_sends = 0
    failed_sends = 0
    errors = []
    
    for token in tokens:
        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data={
                    "notification_id": str(notification_id) if notification_id else "",
                    "metadata": json.dumps(metadata) if metadata else "{}"
                },
                token=token
            )
            
            response = messaging.send(message)
            successful_sends += 1
            print(f"SUCCESS: Notification sent: {response}")
            
        except Exception as e:
            failed_sends += 1
            error_msg = f"Failed to send to token {token[:10]}...: {str(e)}"
            print(f"ERROR: {error_msg}")
            errors.append(error_msg)
    
    return jsonify({
        "status": "success" if successful_sends > 0 else "error",
        "message": f"Notification sending completed",
        "title": title,
        "body": body,
        "successful_sends": successful_sends,
        "failed_sends": failed_sends,
        "total_targets": len(tokens),
        "errors": errors if errors else None
    })

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    print("FCM Push Notification Server (Simple Version)")
    print("=" * 50)
    print(f"Server running on port {port}")
    print(f"Debug mode: {debug}")
    print(f"Firebase status: {'INITIALIZED' if firebase_initialized else 'NOT INITIALIZED'}")
    print("Using in-memory storage (no database required)")
    print("")
    if not firebase_initialized:
        print("TO FIX: Add firebase-service-account.json file")
    print("Ready for testing!")
    
    app.run(host='0.0.0.0', port=port, debug=debug)