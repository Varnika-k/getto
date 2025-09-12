# FCM Push Notification System - Setup Instructions

## Overview
Complete end-to-end FCM push notification system with PostgreSQL database backend and Android app.

## 🚀 Quick Start

### 1. Firebase Setup
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create/select your project
3. Add Android app with package name: `com.example.fcmdemo`
4. Download `google-services.json` and place in `android_app/app/`
5. Go to Project Settings → Service accounts
6. Click "Generate new private key"
7. Save as `firebase-service-account.json` in the root directory

### 2. Database Setup
1. Ensure PostgreSQL is running on port 5433
2. Update `.env` file with your database credentials:
   ```
   DB_HOST=localhost
   DB_PORT=5433
   DB_NAME=your_database_name
   DB_USER=your_username
   DB_PASSWORD=your_password
   ```

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Setup database tables:
   ```bash
   python setup_database.py
   ```

### 3. Backend Server
1. Start the Flask server:
   ```bash
   python app.py
   ```
   Server will run on `http://localhost:5000`

2. Test endpoints:
   - `GET /` - Server status
   - `GET /test-db` - Database connection test
   - `GET /notifications` - Fetch notifications from DB
   - `POST /register-device` - Register FCM token
   - `POST /send-notification` - Send push notification

### 4. Android App Setup
1. Open `android_app` in Android Studio
2. Ensure `google-services.json` is in `app/` folder
3. Sync project with Gradle files
4. Update server URL in MainActivity.java:
   - For emulator: `http://10.0.2.2:5000`
   - For real device: `http://YOUR_COMPUTER_IP:5000`

### 5. Testing the Flow

#### Step 1: Start Backend
```bash
python app.py
```

#### Step 2: Run Android App
1. Build and run the app on device/emulator
2. Click "Get FCM Token"
3. Click "Register with Server"
4. Click "Send Test Notification"

#### Step 3: Send from Database
Use POST request to send notification with database content:
```bash
curl -X POST http://localhost:5000/send-notification \
  -H "Content-Type: application/json" \
  -d '{"notification_id": 1}'
```

## 📋 API Endpoints

### Backend Server (Flask)

#### GET /
Returns server status and available endpoints.

#### GET /test-db
Tests PostgreSQL database connection.

#### GET /notifications
Fetches all notifications from database.

#### POST /register-device
Registers FCM token with server.
```json
{
  "fcm_token": "device_fcm_token_here",
  "device_id": "unique_device_identifier"
}
```

#### POST /send-notification
Sends push notification via FCM.
```json
{
  "notification_id": 1,  // Optional: use stored notification
  "title": "Custom Title",  // Optional: custom notification
  "body": "Custom message",
  "target_token": "specific_fcm_token"  // Optional: target specific device
}
```

## 🗃️ Database Schema

### notifications table
```sql
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    body TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sent_at TIMESTAMP NULL
);
```

### device_tokens table
```sql
CREATE TABLE device_tokens (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(255) UNIQUE NOT NULL,
    fcm_token TEXT NOT NULL,
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    active BOOLEAN DEFAULT TRUE
);
```

## 🛠️ Project Structure
```
/
├── app.py                    # Flask backend server
├── setup_database.py        # Database setup script
├── requirements.txt          # Python dependencies
├── .env                     # Environment configuration
├── firebase-service-account.json  # Firebase admin key (you need to add this)
└── android_app/
    ├── app/
    │   ├── build.gradle
    │   ├── google-services.json  # Firebase config (you need to add this)
    │   └── src/main/
    │       ├── AndroidManifest.xml
    │       ├── java/com/example/fcmdemo/
    │       │   ├── MainActivity.java
    │       │   └── FCMService.java
    │       └── res/
    │           ├── layout/activity_main.xml
    │           ├── values/strings.xml
    │           └── values/colors.xml
    └── build.gradle (project level)
```

## 🔧 Troubleshooting

### Common Issues:

1. **Firebase not initialized**: Ensure `firebase-service-account.json` exists
2. **Database connection failed**: Check PostgreSQL is running on port 5433
3. **Android app can't reach server**: Update SERVER_URL with correct IP
4. **Notifications not received**: Check notification permissions on device

### Testing Commands:

```bash
# Test server status
curl http://localhost:5000/

# Test database
curl http://localhost:5000/test-db

# Get notifications
curl http://localhost:5000/notifications

# Send test notification
curl -X POST http://localhost:5000/send-notification \
  -H "Content-Type: application/json" \
  -d '{"title": "Test", "body": "Hello from server!"}'
```

## ✅ Success Indicators

1. **Backend**: Server starts without errors, shows "Firebase initialized"
2. **Database**: `/test-db` endpoint returns success
3. **Android**: App gets FCM token and registers successfully
4. **End-to-end**: Notification appears in Android notification tray

## 🎯 Demo Flow

1. Start backend server
2. Run Android app
3. Generate and register FCM token
4. Send notification from server (using database content)
5. Notification appears on Android device
6. Demo complete! 🎉