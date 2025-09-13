# 🔥 How to Get a Real FCM Token - Multiple Methods

## 🎯 **Current Status:**
✅ Firebase initialized successfully  
❌ PostgreSQL not running (need to start it)  
✅ Server ready to receive FCM tokens  

---

## 📱 **Method 1: Firebase Console (Easiest)**

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Select your project: **getto-59778**
3. Go to **Cloud Messaging** → **Send your first message**
4. Click **Send test message**
5. Enter any title and body
6. In **Target** section, you'll see options to get test tokens
7. Use Firebase's built-in testing tools to generate tokens

---

## 🌐 **Method 2: Web App FCM Token (Quick)**

Create a simple HTML file to generate FCM token:

```html
<!DOCTYPE html>
<html>
<head>
    <title>FCM Token Generator</title>
    <script src="https://www.gstatic.com/firebasejs/9.0.0/firebase-app.js"></script>
    <script src="https://www.gstatic.com/firebasejs/9.0.0/firebase-messaging.js"></script>
</head>
<body>
    <h1>FCM Token Generator</h1>
    <button onclick="getToken()">Get FCM Token</button>
    <div id="token"></div>

    <script>
        const firebaseConfig = {
            apiKey: "YOUR_API_KEY",
            authDomain: "getto-59778.firebaseapp.com",
            projectId: "getto-59778",
            storageBucket: "getto-59778.appspot.com",
            messagingSenderId: "59778",
            appId: "YOUR_APP_ID"
        };

        firebase.initializeApp(firebaseConfig);
        const messaging = firebase.messaging();

        async function getToken() {
            try {
                const token = await messaging.getToken({
                    vapidKey: 'YOUR_VAPID_KEY'
                });
                document.getElementById('token').innerHTML = '<h3>Your FCM Token:</h3><p style="word-break: break-all;">' + token + '</p>';
                console.log('FCM Token:', token);
            } catch (err) {
                console.log('Error getting token: ', err);
                document.getElementById('token').innerHTML = '<p>Error: ' + err + '</p>';
            }
        }
    </script>
</body>
</html>
```

---

## 💻 **Method 3: Online FCM Token Generators**

Use online tools:
1. Search for "Firebase FCM token generator online"
2. Use your Firebase project credentials
3. Generate a test token

---

## 🔧 **Method 4: Firebase CLI (Advanced)**

```bash
# Install Firebase CLI
npm install -g firebase-tools

# Login to Firebase
firebase login

# Get project info
firebase projects:list

# Use Firebase console to get tokens
firebase open
```

---

## 📋 **Quick Test - Use These Sample Tokens**

For testing purposes, you can try these common test patterns (they won't work but will show proper server response):

```bash
# Test with realistic looking token format
curl -X POST http://localhost:5000/register-device \
  -H "Content-Type: application/json" \
  -d '{
    "fcm_token": "fZ1234567890:APA91bE_xampleTokenThatLooksRealButIsNotWorkingForTestingPurposes123456789",
    "device_id": "test_web_device"
  }'
```

---

## 🎯 **Next Steps:**

1. **Get a real FCM token** using any method above
2. **Start PostgreSQL** on port 5433 (or use different port)
3. **Test complete system** with real token

**The server is ready - just need the FCM token!** 🚀