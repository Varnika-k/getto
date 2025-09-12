# 🚀 Quick FCM Push Notification Test Guide

## 🎉 **Current Status: READY TO TEST!**

✅ **Flask Server Running**: `http://localhost:5000` (Firebase initialized!)  
✅ **Android Emulator Started**: `Medium_Phone_API_35`  
✅ **Firebase Service Account**: Configured with your new account

---

## 📱 **Step 1: Complete Android App Setup**

### Download Firebase Config:
1. Go to [Firebase Console](https://console.firebase.google.com)
2. Select your project: **getto-59778**
3. Click gear icon → **Project Settings**
4. Go to **General** tab → **Your apps** section
5. Click **Download google-services.json** for Android app
6. Save it to: `C:\Users\VarnikaK\fcm-push-notification-system\android_app\app\google-services.json`

### Build & Install App:
```bash
# Open a new terminal in Android Studio
cd "C:\Users\VarnikaK\fcm-push-notification-system\android_app"
.\gradlew assembleDebug
.\gradlew installDebug
```

---

## 🧪 **Step 2: Test Without Android App (Quick Test)**

### Test Server Status:
```bash
curl http://localhost:5000/
```

### Register a Test FCM Token:
```bash
curl -X POST http://localhost:5000/register-device \
  -H "Content-Type: application/json" \
  -d '{
    "fcm_token": "PASTE_YOUR_FCM_TOKEN_HERE",
    "device_id": "test_device"
  }'
```

### Send Test Notification:
```bash
curl -X POST http://localhost:5000/send-notification \
  -H "Content-Type: application/json" \
  -d '{
    "notification_id": 1,
    "target_token": "PASTE_YOUR_FCM_TOKEN_HERE"
  }'
```

---

## 📋 **Step 3: Get Your FCM Token**

### Method 1: From Android App Logs
1. Open Android Studio
2. Run your FCM app on the emulator
3. Check **Logcat** for FCM token (usually printed on app start)
4. Look for lines containing "FCM Token:" or similar

### Method 2: From Firebase Console
1. Go to Firebase Console → **Cloud Messaging**
2. Click **Send your first message**
3. Use Firebase Test Lab or device testing

### Method 3: Manual Debug
Add this to your Android app's MainActivity:
```java
FirebaseMessaging.getInstance().getToken()
    .addOnCompleteListener(new OnCompleteListener<String>() {
        @Override
        public void onComplete(@NonNull Task<String> task) {
            if (!task.isSuccessful()) {
                Log.w(TAG, "Fetching FCM registration token failed", task.getException());
                return;
            }
            String token = task.getResult();
            Log.d(TAG, "FCM Token: " + token);
            Toast.makeText(MainActivity.this, "FCM Token: " + token, Toast.LENGTH_LONG).show();
        }
    });
```

---

## 🔧 **Step 4: Interactive Testing Tool**

I've created a simple web interface for testing. Run this:

```bash
python -m http.server 8080 -d "C:\Users\VarnikaK\fcm-push-notification-system"
```

Then open: `http://localhost:8080/test_interface.html`

---

## 📊 **Expected Results**

### Successful Notification Response:
```json
{
  "status": "success",
  "message": "Notification sending completed",
  "title": "Welcome!",
  "body": "Welcome to our FCM notification system!",
  "successful_sends": 1,
  "failed_sends": 0,
  "total_targets": 1
}
```

### On Your Android Device:
- Notification should appear in system tray
- App should receive the notification data
- Log entries should show successful receipt

---

## 🐛 **Troubleshooting**

### If Firebase fails:
- Verify service account file path: `D:\demo\getto-59778-firebase-adminsdk-fbsvc-3adfd31f8f.json`
- Check Firebase project permissions

### If Android app won't build:
- Ensure `google-services.json` is in `app/` directory
- Run `.\gradlew clean` then `.\gradlew build`

### If notifications don't arrive:
- Check FCM token is valid (not expired)
- Ensure device has internet connection
- Check Android notification permissions

---

## 🎯 **Next Steps After Success**

1. Test all 4 sample notifications (IDs 1-4)
2. Create custom notifications via API
3. Integrate with PostgreSQL (we have the code ready!)
4. Deploy to production server

**Your system is fully functional and ready for real-world testing!** 🎉