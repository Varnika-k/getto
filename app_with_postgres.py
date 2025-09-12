from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, messaging
import os
from dotenv import load_dotenv
import json
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Database connection configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5433'),
    'database': os.getenv('DB_NAME', 'notifications_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'your_password')
}

# In-memory device storage (for demo, should use DB in production)
device_tokens = {}

def get_db_connection():
    """Create and return a database connection"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.Error as e:
        logger.error(f"Database connection failed: {e}")
        return None

def initialize_database():
    """Initialize database tables if they don't exist"""
    try:
        conn = get_db_connection()
        if not conn:
            return False
        
        cursor = conn.cursor()
        
        # Create notifications table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                body TEXT NOT NULL,
                metadata JSONB DEFAULT '{}',
                priority VARCHAR(50) DEFAULT 'medium',
                notification_type VARCHAR(100) DEFAULT 'general',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT true
            )
        """)
        
        # Create devices table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS devices (
                id SERIAL PRIMARY KEY,
                device_id VARCHAR(255) UNIQUE NOT NULL,
                fcm_token TEXT NOT NULL,
                registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT true
            )
        """)
        
        # Insert sample notifications if table is empty
        cursor.execute("SELECT COUNT(*) FROM notifications")
        if cursor.fetchone()[0] == 0:
            sample_notifications = [
                ("Welcome!", "Welcome to our FCM notification system!", 
                 '{"type": "welcome"}', "high", "welcome"),
                ("System Update", "Your system has been updated successfully.", 
                 '{"type": "system"}', "medium", "system"),
                ("Daily Reminder", "Don't forget to check your dashboard today.", 
                 '{"type": "reminder"}', "low", "reminder"),
                ("Security Alert", "New login detected from unknown device.", 
                 '{"type": "security"}', "high", "security"),
                ("Database Connected", "Successfully connected to PostgreSQL database!", 
                 '{"type": "database", "source": "postgresql"}', "medium", "system")
            ]
            
            for title, body, metadata, priority, ntype in sample_notifications:
                cursor.execute("""
                    INSERT INTO notifications (title, body, metadata, priority, notification_type)
                    VALUES (%s, %s, %s, %s, %s)
                """, (title, body, metadata, priority, ntype))
        
        conn.commit()
        cursor.close()
        conn.close()
        logger.info("Database initialized successfully")
        return True
        
    except psycopg2.Error as e:
        logger.error(f"Database initialization failed: {e}")
        return False

def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    try:
        service_account_path = os.getenv('FIREBASE_SERVICE_ACCOUNT_KEY', 'firebase-service-account.json')
        if not os.path.exists(service_account_path):
            logger.warning(f"Firebase service account key not found at: {service_account_path}")
            return False
        
        cred = credentials.Certificate(service_account_path)
        firebase_admin.initialize_app(cred)
        logger.info("Firebase initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Firebase initialization failed: {e}")
        return False

# Initialize components on startup
firebase_initialized = initialize_firebase()
database_initialized = initialize_database()

@app.route('/')
def home():
    return jsonify({
        "message": "FCM Push Notification Server with PostgreSQL",
        "status": "running",
        "firebase_status": "initialized" if firebase_initialized else "not initialized",
        "database_status": "connected" if database_initialized else "connection failed",
        "endpoints": [
            "/notifications - GET (fetch notifications from database)",
            "/notifications - POST (create new notification)",
            "/send-notification - POST (send push notification)",
            "/send-notification/<id> - POST (send specific notification by ID)",
            "/register-device - POST (register FCM token)",
            "/devices - GET (show registered devices)",
            "/test-db - GET (test database connection)"
        ]
    })

@app.route('/test-db', methods=['GET'])
def test_database():
    """Test database connection"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500
        
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        return jsonify({
            "status": "success",
            "message": "Database connection successful",
            "postgresql_version": version,
            "config": {
                "host": DB_CONFIG['host'],
                "port": DB_CONFIG['port'],
                "database": DB_CONFIG['database']
            }
        })
    except Exception as e:
        return jsonify({"error": f"Database test failed: {str(e)}"}), 500

@app.route('/notifications', methods=['GET'])
def get_notifications():
    """Fetch notifications from database"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500
        
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT id, title, body, metadata, priority, notification_type, 
                   created_at, is_active 
            FROM notifications 
            WHERE is_active = true 
            ORDER BY created_at DESC
        """)
        
        notifications = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Convert to JSON serializable format
        notifications_list = []
        for notification in notifications:
            notifications_list.append({
                "id": notification['id'],
                "title": notification['title'],
                "body": notification['body'],
                "metadata": notification['metadata'],
                "priority": notification['priority'],
                "type": notification['notification_type'],
                "created_at": notification['created_at'].isoformat()
            })
        
        return jsonify({
            "status": "success",
            "notifications": notifications_list,
            "count": len(notifications_list),
            "source": "postgresql_database"
        })
        
    except Exception as e:
        logger.error(f"Error fetching notifications: {e}")
        return jsonify({"error": f"Failed to fetch notifications: {str(e)}"}), 500

@app.route('/notifications', methods=['POST'])
def create_notification():
    """Create a new notification in database"""
    try:
        data = request.get_json()
        title = data.get('title')
        body = data.get('body')
        metadata = data.get('metadata', {})
        priority = data.get('priority', 'medium')
        notification_type = data.get('type', 'general')
        
        if not title or not body:
            return jsonify({"error": "Title and body are required"}), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500
        
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO notifications (title, body, metadata, priority, notification_type)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (title, body, json.dumps(metadata), priority, notification_type))
        
        notification_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "status": "success",
            "message": "Notification created successfully",
            "notification_id": notification_id
        })
        
    except Exception as e:
        logger.error(f"Error creating notification: {e}")
        return jsonify({"error": f"Failed to create notification: {str(e)}"}), 500

@app.route('/devices', methods=['GET'])
def get_devices():
    return jsonify({
        "status": "success",
        "devices": device_tokens,
        "count": len(device_tokens),
        "note": "Currently using in-memory storage. Consider moving to database for production."
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
    """Send notification using provided data"""
    if not firebase_initialized:
        return jsonify({"error": "Firebase not initialized"}), 500
    
    data = request.get_json()
    title = data.get('title', 'Test Notification')
    body = data.get('body', 'This is a test notification')
    metadata = data.get('metadata', {})
    target_token = data.get('target_token')
    
    return _send_notification_helper(title, body, metadata, target_token)

@app.route('/send-notification/<int:notification_id>', methods=['POST'])
def send_notification_by_id(notification_id):
    """Send notification by ID from database"""
    if not firebase_initialized:
        return jsonify({"error": "Firebase not initialized"}), 500
    
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500
        
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT title, body, metadata FROM notifications 
            WHERE id = %s AND is_active = true
        """, (notification_id,))
        
        notification = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not notification:
            return jsonify({"error": "Notification not found"}), 404
        
        data = request.get_json() or {}
        target_token = data.get('target_token')
        
        return _send_notification_helper(
            notification['title'], 
            notification['body'], 
            notification['metadata'], 
            target_token,
            notification_id
        )
        
    except Exception as e:
        logger.error(f"Error sending notification by ID: {e}")
        return jsonify({"error": f"Failed to send notification: {str(e)}"}), 500

def _send_notification_helper(title, body, metadata, target_token=None, notification_id=None):
    """Helper function to send notifications"""
    # Get target tokens
    tokens = []
    if target_token:
        tokens = [target_token]
    else:
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
            logger.info(f"Notification sent successfully: {response}")
            
        except Exception as e:
            failed_sends += 1
            error_msg = f"Failed to send to token {token[:10]}...: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)
    
    return jsonify({
        "status": "success" if successful_sends > 0 else "error",
        "message": f"Notification sending completed",
        "title": title,
        "body": body,
        "successful_sends": successful_sends,
        "failed_sends": failed_sends,
        "total_targets": len(tokens),
        "errors": errors if errors else None,
        "notification_id": notification_id
    })

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    print("=" * 60)
    print("FCM Push Notification Server with PostgreSQL Integration")
    print("=" * 60)
    print(f"Server running on: http://localhost:{port}")
    print(f"Debug mode: {debug}")
    print(f"Firebase status: {'✅ INITIALIZED' if firebase_initialized else '❌ NOT INITIALIZED'}")
    print(f"Database status: {'✅ CONNECTED' if database_initialized else '❌ CONNECTION FAILED'}")
    print("")
    
    if not firebase_initialized:
        print("🔧 TO FIX FIREBASE:")
        print(f"   Add Firebase service account JSON file")
        print(f"   Current path: {os.getenv('FIREBASE_SERVICE_ACCOUNT_KEY')}")
        print("")
    
    if not database_initialized:
        print("🔧 TO FIX DATABASE:")
        print("   Update .env file with correct PostgreSQL credentials")
        print("   Ensure PostgreSQL is running on port 5433")
        print("")
    
    print("🚀 Ready for testing!")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=port, debug=debug)