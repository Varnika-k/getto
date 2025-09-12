package com.example.fcmdemo;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.NotificationManagerCompat;

import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.content.pm.PackageManager;
import android.os.Build;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;
import android.Manifest;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import com.google.android.gms.tasks.OnCompleteListener;
import com.google.android.gms.tasks.Task;
import com.google.firebase.messaging.FirebaseMessaging;

import java.io.IOException;

import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

import com.google.gson.Gson;
import com.google.gson.JsonObject;

public class MainActivity extends AppCompatActivity {

    private static final String TAG = "MainActivity";
    private static final int REQUEST_NOTIFICATION_PERMISSION = 100;
    private static final String SERVER_URL = "http://10.0.2.2:5000"; // For Android emulator
    // Use your actual server IP for real device: http://YOUR_IP:5000
    
    private TextView tokenTextView;
    private TextView statusTextView;
    private Button getTokenButton;
    private Button registerButton;
    private Button testNotificationButton;
    
    private String fcmToken;
    private OkHttpClient httpClient;
    private Gson gson;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        initializeViews();
        setupHttpClient();
        createNotificationChannel();
        requestNotificationPermission();
        
        // Set up button click listeners
        getTokenButton.setOnClickListener(v -> getFCMToken());
        registerButton.setOnClickListener(v -> registerDeviceWithServer());
        testNotificationButton.setOnClickListener(v -> sendTestNotification());
    }

    private void initializeViews() {
        tokenTextView = findViewById(R.id.tokenTextView);
        statusTextView = findViewById(R.id.statusTextView);
        getTokenButton = findViewById(R.id.getTokenButton);
        registerButton = findViewById(R.id.registerButton);
        testNotificationButton = findViewById(R.id.testNotificationButton);
        
        updateStatus("App initialized. Get FCM token first.");
    }

    private void setupHttpClient() {
        httpClient = new OkHttpClient();
        gson = new Gson();
    }

    private void requestNotificationPermission() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS) 
                != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(this, 
                    new String[]{Manifest.permission.POST_NOTIFICATIONS}, 
                    REQUEST_NOTIFICATION_PERMISSION);
            }
        }
    }

    private void createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            CharSequence name = getString(R.string.default_notification_channel_name);
            String description = "FCM Notifications";
            int importance = NotificationManager.IMPORTANCE_HIGH;
            NotificationChannel channel = new NotificationChannel(
                getString(R.string.default_notification_channel_id), name, importance);
            channel.setDescription(description);

            NotificationManager notificationManager = getSystemService(NotificationManager.class);
            notificationManager.createNotificationChannel(channel);
        }
    }

    private void getFCMToken() {
        updateStatus("Getting FCM token...");
        getTokenButton.setEnabled(false);
        
        FirebaseMessaging.getInstance().getToken()
            .addOnCompleteListener(new OnCompleteListener<String>() {
                @Override
                public void onComplete(@NonNull Task<String> task) {
                    if (!task.isSuccessful()) {
                        Log.w(TAG, "Fetching FCM registration token failed", task.getException());
                        updateStatus("Failed to get FCM token");
                        getTokenButton.setEnabled(true);
                        return;
                    }

                    // Get new FCM registration token
                    fcmToken = task.getResult();
                    Log.d(TAG, "FCM Token: " + fcmToken);
                    
                    tokenTextView.setText("FCM Token: " + fcmToken.substring(0, 20) + "...");
                    updateStatus("FCM token obtained successfully!");
                    
                    getTokenButton.setEnabled(true);
                    registerButton.setEnabled(true);
                }
            });
    }

    private void registerDeviceWithServer() {
        if (fcmToken == null || fcmToken.isEmpty()) {
            Toast.makeText(this, "Please get FCM token first", Toast.LENGTH_SHORT).show();
            return;
        }

        updateStatus("Registering device with server...");
        registerButton.setEnabled(false);

        JsonObject jsonObject = new JsonObject();
        jsonObject.addProperty("fcm_token", fcmToken);
        jsonObject.addProperty("device_id", "android_demo_device");

        RequestBody body = RequestBody.create(
            gson.toJson(jsonObject),
            MediaType.get("application/json; charset=utf-8")
        );

        Request request = new Request.Builder()
            .url(SERVER_URL + "/register-device")
            .post(body)
            .build();

        httpClient.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(@NonNull Call call, @NonNull IOException e) {
                runOnUiThread(() -> {
                    updateStatus("Failed to register device: " + e.getMessage());
                    registerButton.setEnabled(true);
                });
            }

            @Override
            public void onResponse(@NonNull Call call, @NonNull Response response) throws IOException {
                String responseBody = response.body().string();
                runOnUiThread(() -> {
                    if (response.isSuccessful()) {
                        updateStatus("Device registered successfully!");
                        testNotificationButton.setEnabled(true);
                    } else {
                        updateStatus("Registration failed: " + responseBody);
                    }
                    registerButton.setEnabled(true);
                });
            }
        });
    }

    private void sendTestNotification() {
        updateStatus("Sending test notification...");
        testNotificationButton.setEnabled(false);

        JsonObject jsonObject = new JsonObject();
        jsonObject.addProperty("title", "Test from Android App");
        jsonObject.addProperty("body", "This is a test notification sent from the Android app!");
        jsonObject.addProperty("target_token", fcmToken);

        RequestBody body = RequestBody.create(
            gson.toJson(jsonObject),
            MediaType.get("application/json; charset=utf-8")
        );

        Request request = new Request.Builder()
            .url(SERVER_URL + "/send-notification")
            .post(body)
            .build();

        httpClient.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(@NonNull Call call, @NonNull IOException e) {
                runOnUiThread(() -> {
                    updateStatus("Failed to send notification: " + e.getMessage());
                    testNotificationButton.setEnabled(true);
                });
            }

            @Override
            public void onResponse(@NonNull Call call, @NonNull Response response) throws IOException {
                String responseBody = response.body().string();
                runOnUiThread(() -> {
                    if (response.isSuccessful()) {
                        updateStatus("Test notification sent! Check your notification tray.");
                    } else {
                        updateStatus("Failed to send notification: " + responseBody);
                    }
                    testNotificationButton.setEnabled(true);
                });
            }
        });
    }

    private void updateStatus(String status) {
        statusTextView.setText("Status: " + status);
        Log.d(TAG, status);
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, 
                                         @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == REQUEST_NOTIFICATION_PERMISSION) {
            if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                updateStatus("Notification permission granted");
            } else {
                updateStatus("Notification permission denied");
            }
        }
    }
}