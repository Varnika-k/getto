# 🚀 FCM Push Notification Demo - START HERE

## Quick Setup Checklist

### ✅ Step 1: Firebase Setup (5 minutes)
1. Go to https://console.firebase.google.com/
2. Create/select project
3. Add Android app: `com.example.fcmdemo`
4. Download `google-services.json` → place in `android_app/app/`
5. Generate service account key → save as `firebase-service-account.json` in root

### ✅ Step 2: Database Setup (2 minutes)
1. Update `.env` with your PostgreSQL credentials
2. Run: `pip install -r requirements.txt`
3. Run: `python setup_database.py`

### ✅ Step 3: Test Backend (1 minute)
1. Run: `python app.py`
2. Run: `python test_system.py` (optional test)

### ✅ Step 4: Android Setup (3 minutes)
1. Open `android_app` in Android Studio
2. Ensure `google-services.json` is in `app/` folder
3. Build and run on your device

### ✅ Step 5: Demo Time! 🎉
1. In Android app: Get FCM Token
2. Register with Server
3. Send Test Notification
4. Check your notification tray!

---

## 🎯 Expected Results

**Backend Console:**
```
🚀 Starting FCM Push Notification Server on port 5000
📊 Debug mode: True
🔥 Firebase status: ✅ Initialized
✅ Firebase initialized successfully
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
```

**Android App Flow:**
1. **Get Token** → Shows FCM token preview
2. **Register** → "Device registered successfully!"
3. **Test Notification** → Notification appears in tray

**Database Content:**
Your notifications will use content from PostgreSQL:
- "Welcome!" - Welcome to our FCM notification system!
- "System Update" - Your system has been updated successfully
- "Daily Reminder" - Don't forget to check your dashboard today
- "Security Alert" - New login detected from unknown device

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| "Firebase not initialized" | Add `firebase-service-account.json` to root |
| "Database connection failed" | Check PostgreSQL running on port 5433 |
| "Can't reach server" | Update SERVER_URL in MainActivity.java |
| "No notifications received" | Enable notification permissions on device |

---

## 📱 Files You Need to Add

1. **firebase-service-account.json** (root directory)
   - Download from Firebase Console → Project Settings → Service accounts

2. **google-services.json** (android_app/app/ directory)
   - Download when adding Android app to Firebase project

3. **Update .env file** with your database credentials:
   ```
   DB_HOST=localhost
   DB_PORT=5433
   DB_NAME=your_actual_db_name
   DB_USER=your_username
   DB_PASSWORD=your_password
   ```

---

## 🎪 Demo Script

**For Presentation:**

1. **Show Backend**: 
   - "Server running with Firebase initialized"
   - "Database connected with sample notifications"

2. **Show Android App**:
   - "Get FCM token from device"
   - "Register device with our server"

3. **Demo Push Notification**:
   - "Send notification using database content"
   - "Notification appears on device immediately"

4. **Show Database Integration**:
   - "Content comes from PostgreSQL"
   - "Can send to specific device or all users"

**Perfect for showing the complete flow!** 🚀

---

Ready to start? Just follow the 5 steps above and you'll have push notifications working in under 15 minutes!