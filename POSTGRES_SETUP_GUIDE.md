# PostgreSQL Integration Setup Guide

## 🎯 What We've Done

✅ **Updated Firebase Configuration**
- Updated `.env` file with your new Firebase service account key
- Path: `D:\demo\getto-59778-firebase-adminsdk-fbsvc-3adfd31f8f.json`

✅ **Created PostgreSQL-Integrated Backend**
- New file: `app_with_postgres.py`
- Automatically creates database tables
- Stores notifications in PostgreSQL instead of memory
- Enhanced API endpoints for database operations

✅ **Added Database Schema**
- `notifications` table: stores title, body, metadata, priority, type
- `devices` table: for device management (ready for future use)
- Sample notifications automatically inserted

## 🚀 Next Steps

### Step 1: Update Database Credentials
Edit your `.env` file with your actual PostgreSQL credentials:
```env
# Update these with your actual database info
DB_HOST=localhost
DB_PORT=5433
DB_NAME=your_actual_database_name
DB_USER=your_username
DB_PASSWORD=your_password
```

### Step 2: Install Dependencies
```bash
pip install -r requirements_postgres.txt
```

### Step 3: Start the Enhanced Server
```bash
python app_with_postgres.py
```

### Step 4: Test the System
```bash
python test_with_postgres.py
```

## 📱 Getting Your FCM Token

### From Your Android App:
1. Open your Android app in Android Studio
2. Run the app on your device/emulator
3. Check the app logs for FCM token (usually logged on app start)
4. Copy the token - it should look like: `eX1mple_t0ken_h3re...`

### Quick Test with FCM Token:
1. Update `TEST_FCM_TOKEN` in `test_with_postgres.py`
2. Run the test script to verify notifications work

## 🔧 API Endpoints (New PostgreSQL Version)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Server status |
| GET | `/test-db` | Test database connection |
| GET | `/notifications` | Fetch notifications from DB |
| POST | `/notifications` | Create new notification in DB |
| POST | `/send-notification` | Send custom notification |
| POST | `/send-notification/<id>` | Send notification by DB ID |
| POST | `/register-device` | Register FCM token |
| GET | `/devices` | Show registered devices |

## 📊 Sample API Calls

### Test Database Connection:
```bash
curl http://localhost:5000/test-db
```

### Fetch Notifications:
```bash
curl http://localhost:5000/notifications
```

### Create Notification:
```bash
curl -X POST http://localhost:5000/notifications \
  -H "Content-Type: application/json" \
  -d '{
    "title": "New Alert",
    "body": "This is from PostgreSQL!",
    "priority": "high",
    "type": "alert"
  }'
```

### Register Device:
```bash
curl -X POST http://localhost:5000/register-device \
  -H "Content-Type: application/json" \
  -d '{
    "fcm_token": "YOUR_FCM_TOKEN_HERE",
    "device_id": "my_phone"
  }'
```

### Send Notification:
```bash
curl -X POST http://localhost:5000/send-notification \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Push",
    "body": "Hello from PostgreSQL server!",
    "target_token": "YOUR_FCM_TOKEN_HERE"
  }'
```

## 🎉 You're Ready!

Your push notification system now:
- ✅ Uses your new Firebase account
- ✅ Connects to PostgreSQL database
- ✅ Stores notifications persistently
- ✅ Sends real-time push notifications
- ✅ Has comprehensive testing tools

**Next:** Update your database credentials and test with your actual FCM token!