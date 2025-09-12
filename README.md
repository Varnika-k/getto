# 🔔 FCM Push Notification System

A complete end-to-end Firebase Cloud Messaging (FCM) push notification system with Python Flask backend and Android client.

## 🎯 Features

- **Python Backend** with Flask and Firebase Admin SDK
- **Android App** with FCM integration and modern UI
- **Real-time Push Notifications** from server to device
- **RESTful API** for notification management
- **Device Token Management** with registration system
- **Sample Notification Content** for demonstration

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Android App   │◄──►│  Python Backend  │◄──►│ Firebase Cloud  │
│                 │    │   (Flask API)    │    │   Messaging     │
│ • FCM Token     │    │ • Admin SDK      │    │                 │
│ • Notifications │    │ • Device Tokens  │    │ • Push Service  │
│ • UI Interface  │    │ • Sample Data    │    │ • Delivery      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📱 Demo Flow

1. **Generate FCM Token** - Android app creates unique device identifier
2. **Register Device** - App sends token to backend server
3. **Send Notification** - Server uses Firebase Admin SDK to push notification
4. **Receive & Display** - Android app shows notification to user

## 🚀 Quick Start

### Prerequisites

- **Python 3.7+**
- **Android Studio**
- **Firebase Project** with Admin SDK key
- **Android device/emulator**

### Backend Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Varnika-k/fcm-push-notification-system.git
   cd fcm-push-notification-system
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements_simple.txt
   ```

3. **Configure Firebase:**
   - Get Firebase Admin SDK key from Firebase Console
   - Update `.env` file with path to your key:
     ```
     FIREBASE_SERVICE_ACCOUNT_KEY=path/to/your/firebase-key.json
     ```

4. **Start the server:**
   ```bash
   python app_simple.py
   ```
   Server runs on `http://localhost:5000`

### Android Setup

1. **Get Firebase configuration:**
   - In Firebase Console, add Android app with package `com.example.fcmdemo`
   - Download `google-services.json`
   - Place in `android_app/app/google-services.json`

2. **Open in Android Studio:**
   - Open `android_app` folder
   - Let Gradle sync complete
   - Build and run on device/emulator

3. **Test the flow:**
   - Click "Get FCM Token"
   - Click "Register with Server" 
   - Click "Send Test Notification"
   - Check notification tray! 🎉

## 📚 API Documentation

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Server status and available endpoints |
| `GET` | `/notifications` | Fetch sample notification content |
| `GET` | `/devices` | List registered devices |
| `POST` | `/register-device` | Register FCM token |
| `POST` | `/send-notification` | Send push notification |

### Register Device
```bash
curl -X POST http://localhost:5000/register-device \
  -H "Content-Type: application/json" \
  -d '{
    "fcm_token": "device_fcm_token_here",
    "device_id": "android_demo_device"
  }'
```

### Send Notification
```bash
curl -X POST http://localhost:5000/send-notification \
  -H "Content-Type: application/json" \
  -d '{
    "notification_id": 1,
    "title": "Custom Title",
    "body": "Custom message"
  }'
```

## 🗂️ Project Structure

```
fcm-push-notification-system/
├── README.md                           # This file
├── app_simple.py                       # Flask backend server
├── requirements_simple.txt             # Python dependencies
├── .env                               # Environment configuration
├── test_system.py                     # System testing script
├── .gitignore                         # Git ignore rules
├── START_HERE.md                      # Quick start guide
├── ANDROID_SETUP_GUIDE.md            # Android setup instructions
├── SETUP_INSTRUCTIONS.md             # Detailed setup guide
└── android_app/                      # Complete Android project
    ├── app/
    │   ├── build.gradle               # Android dependencies
    │   ├── google-services.json.template  # Firebase config template
    │   └── src/main/
    │       ├── AndroidManifest.xml
    │       ├── java/com/example/fcmdemo/
    │       │   ├── MainActivity.java      # Main app activity
    │       │   └── FCMService.java        # FCM service handler
    │       └── res/                       # Android resources
    ├── build.gradle                   # Project-level Gradle
    └── settings.gradle               # Gradle settings
```

## 🔧 Configuration

### Backend Configuration (.env)
```env
# Firebase Configuration
FIREBASE_SERVICE_ACCOUNT_KEY=path/to/firebase-key.json

# Server Configuration  
FLASK_PORT=5000
FLASK_DEBUG=True
```

### Android Configuration
- **Package Name:** `com.example.fcmdemo`
- **Firebase Config:** `google-services.json` in `app/` folder
- **Server URL:** Configure in `MainActivity.java`
  - Emulator: `http://10.0.2.2:5000`
  - Real device: `http://YOUR_IP:5000`

## 📱 Android App Features

- **Modern Material Design UI** with CardView components
- **FCM Token Generation** with error handling
- **Server Registration** with HTTP client
- **Push Notification Reception** with custom service
- **Permission Handling** for Android 13+ notifications
- **Real-time Status Updates** with user feedback

## 🖥️ Backend Features

- **Flask REST API** with CORS support
- **Firebase Admin SDK Integration** for FCM
- **In-memory Token Storage** (easily extendable to database)
- **Sample Notification Content** for demonstration
- **Error Handling** with detailed logging
- **Development Server** with hot reload

## 🔐 Security Features

- **Firebase Keys Protected** - Never committed to repository
- **Environment Variables** for sensitive configuration
- **Input Validation** on API endpoints
- **Error Handling** without exposing internals

## 🧪 Testing

**Test Backend:**
```bash
python test_system.py
```

**Test API Endpoints:**
```bash
# Server status
curl http://localhost:5000/

# Sample notifications
curl http://localhost:5000/notifications

# Registered devices
curl http://localhost:5000/devices
```

## 🚨 Troubleshooting

| Problem | Solution |
|---------|----------|
| Firebase not initialized | Check firebase key path in `.env` |
| Android app crashes | Ensure `google-services.json` exists |
| No notifications received | Check device notification permissions |
| Server connection failed | Update server URL in Android app |

## 📈 Future Enhancements

- [ ] **Database Integration** (PostgreSQL/MongoDB)
- [ ] **User Authentication** and authorization
- [ ] **Notification History** and analytics
- [ ] **Scheduled Notifications** with cron jobs
- [ ] **Notification Templates** and personalization
- [ ] **Web Dashboard** for notification management
- [ ] **Multiple Device Support** per user
- [ ] **Push Notification Analytics** and metrics

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Firebase** for Cloud Messaging service
- **Flask** for Python web framework
- **Android** Firebase SDK team
- **Material Design** for UI components

## 📞 Support

For support and questions:
- Open an [Issue](https://github.com/Varnika-k/fcm-push-notification-system/issues)
- Check [Documentation](https://github.com/Varnika-k/fcm-push-notification-system/wiki)
- Review [Setup Guides](./START_HERE.md)

---

**⭐ Star this repository if it helped you build FCM push notifications!**

**🚀 Ready to send your first push notification? Follow [START_HERE.md](./START_HERE.md)**