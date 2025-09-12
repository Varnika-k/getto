# 📱 Android FCM Demo - Quick Setup Guide

## ✅ Status: Backend Ready!
- Server running on: http://localhost:5000 ✅
- Firebase initialized successfully ✅
- Sample notifications loaded ✅

## 🎯 Android Setup (3 simple steps)

### Step 1: Get google-services.json
1. **Firebase Console**: https://console.firebase.google.com/
2. **Select your project** (the same one where you got firebase-key.json)
3. **Add Android App** (if not done):
   - Package name: `com.example.fcmdemo`
   - App nickname: `FCM Demo`
4. **Download google-services.json**
5. **Place it in**: `android_app/app/google-services.json`

### Step 2: Open in Android Studio
1. **Open Android Studio**
2. **Open project**: Navigate to `C:\Users\VarnikaK\android_app`
3. **Let Gradle sync** (this will take a few minutes first time)
4. **Wait for "Gradle sync finished"**

### Step 3: Build and Run
1. **Connect device** or **start emulator**
2. **Click Run button** (green play button)
3. **Install app on device**

## 🔧 Server URLs to Use

### If using Android Emulator:
- URL is already set correctly: `http://10.0.2.2:5000`

### If using Real Android Device:
- Update MainActivity.java line 42:
- Change to: `http://192.168.0.105:5000`

## 🎪 Demo Flow

Once app is running:

1. **Click "Get FCM Token"** 
   - Should show token preview

2. **Click "Register with Server"**
   - Should show "Device registered successfully!"

3. **Click "Send Test Notification"**
   - Notification should appear in your notification tray!

## 🚨 If you need google-services.json:

**Template created at**: `android_app/app/google-services.json.template`

**To get the real one:**
1. Firebase Console → Your Project
2. Project Settings (gear icon)
3. Your apps → Android app
4. Download google-services.json
5. Replace the template file

## 📂 Project Structure (Already Created)

```
android_app/
├── app/
│   ├── build.gradle ✅
│   ├── google-services.json ❌ (YOU NEED TO ADD THIS)
│   ├── src/main/
│   │   ├── AndroidManifest.xml ✅
│   │   ├── java/com/example/fcmdemo/
│   │   │   ├── MainActivity.java ✅
│   │   │   └── FCMService.java ✅
│   │   └── res/
│   │       ├── layout/activity_main.xml ✅
│   │       ├── values/strings.xml ✅
│   │       ├── values/colors.xml ✅
│   │       └── values/themes.xml ✅
├── build.gradle ✅
├── settings.gradle ✅
├── gradle.properties ✅
└── local.properties ✅
```

## 🎉 Ready to Demo!

**Current Status:**
- ✅ Backend server running with Firebase
- ✅ Android project files ready
- ❌ Missing: google-services.json (you need to add this)

**Once you add google-services.json:**
1. Open in Android Studio
2. Build and run
3. Test the complete FCM flow!

**The demo will show:**
- FCM token generation
- Device registration with server
- Push notifications from server to device
- Real-time notification delivery!

---

**Need help?** The backend is running and ready to receive your FCM tokens!