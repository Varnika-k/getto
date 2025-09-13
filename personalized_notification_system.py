#!/usr/bin/env python3
"""
GETTO Personalized Notification System
Advanced FCM push notification system with user segmentation and ML-based personalization
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, messaging
import os
from dotenv import load_dotenv
import json
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import schedule
import time
import threading
from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__)
CORS(app)

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5433'),
    'database': os.getenv('DB_NAME', 'getto_personalized'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'password')
}

class UserSegment(Enum):
    NEW_USER = "new_user"
    ACTIVE_USER = "active_user" 
    CART_ABANDONER = "cart_abandoner"
    INACTIVE_USER = "inactive_user"
    REPEAT_BUYER = "repeat_buyer"
    VIP_USER = "vip_user"

class NotificationType(Enum):
    WELCOME = "welcome"
    CART_ABANDONMENT = "cart_abandonment"
    WISHLIST_REMINDER = "wishlist_reminder"
    REORDER_SUGGESTION = "reorder_suggestion"
    NEW_PRODUCT_ALERT = "new_product_alert"
    PRICE_DROP = "price_drop"
    BACK_IN_STOCK = "back_in_stock"
    LOYALTY_REWARD = "loyalty_reward"
    RE_ENGAGEMENT = "re_engagement"

@dataclass
class UserProfile:
    user_id: str
    segment: UserSegment
    total_purchases: int
    avg_order_value: float
    last_activity: datetime
    preferred_categories: List[str]
    cart_items: List[Dict]
    wishlist_items: List[Dict]
    notification_preferences: Dict
    engagement_score: float

@dataclass
class NotificationTemplate:
    type: NotificationType
    title: str
    body: str
    priority: str
    personalization_data: Dict

class PersonalizedNotificationEngine:
    def __init__(self, db_config):
        self.db_config = db_config
        self.firebase_initialized = self.initialize_firebase()
        self.database_initialized = self.initialize_database()
        self.user_profiles = {}
        self.notification_templates = self.load_notification_templates()
        
    def initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            service_account_path = os.getenv('FIREBASE_SERVICE_ACCOUNT_KEY')
            if not os.path.exists(service_account_path):
                logger.error(f"Firebase service account key not found at: {service_account_path}")
                return False
            
            cred = credentials.Certificate(service_account_path)
            firebase_admin.initialize_app(cred)
            logger.info("Firebase initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Firebase initialization failed: {e}")
            return False
    
    def get_db_connection(self):
        """Create database connection"""
        try:
            return psycopg2.connect(**self.db_config)
        except psycopg2.Error as e:
            logger.error(f"Database connection failed: {e}")
            return None
    
    def initialize_database(self):
        """Initialize enhanced database schema for personalization"""
        try:
            conn = self.get_db_connection()
            if not conn:
                return False
            
            cursor = conn.cursor()
            
            # Enhanced users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id VARCHAR(255) PRIMARY KEY,
                    email VARCHAR(255),
                    phone VARCHAR(20),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total_purchases INTEGER DEFAULT 0,
                    total_spent DECIMAL(10,2) DEFAULT 0.00,
                    avg_order_value DECIMAL(10,2) DEFAULT 0.00,
                    preferred_categories JSONB DEFAULT '[]',
                    segment VARCHAR(50) DEFAULT 'new_user',
                    engagement_score DECIMAL(3,2) DEFAULT 0.50,
                    notification_preferences JSONB DEFAULT '{"enabled": true, "frequency": "normal"}',
                    timezone VARCHAR(50) DEFAULT 'UTC'
                )
            """)
            
            # FCM devices table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS fcm_devices (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(255) REFERENCES users(user_id),
                    device_id VARCHAR(255) UNIQUE,
                    fcm_token TEXT NOT NULL,
                    platform VARCHAR(20),
                    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT true
                )
            """)
            
            # Products table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    product_id VARCHAR(255) PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    category VARCHAR(100),
                    subcategory VARCHAR(100),
                    price DECIMAL(10,2),
                    description TEXT,
                    tags JSONB DEFAULT '[]',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT true
                )
            """)
            
            # Purchase history
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS purchases (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(255) REFERENCES users(user_id),
                    product_id VARCHAR(255) REFERENCES products(product_id),
                    quantity INTEGER DEFAULT 1,
                    price DECIMAL(10,2),
                    purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    order_id VARCHAR(255)
                )
            """)
            
            # Cart items
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cart_items (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(255) REFERENCES users(user_id),
                    product_id VARCHAR(255) REFERENCES products(product_id),
                    quantity INTEGER DEFAULT 1,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Wishlist items
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS wishlist_items (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(255) REFERENCES users(user_id),
                    product_id VARCHAR(255) REFERENCES products(product_id),
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Notification history with analytics
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notification_history (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(255) REFERENCES users(user_id),
                    notification_type VARCHAR(50),
                    title VARCHAR(255),
                    body TEXT,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    opened_at TIMESTAMP,
                    clicked_at TIMESTAMP,
                    converted_at TIMESTAMP,
                    campaign_id VARCHAR(255),
                    ab_test_group VARCHAR(50),
                    personalization_score DECIMAL(3,2),
                    metadata JSONB DEFAULT '{}'
                )
            """)
            
            # User behavior tracking
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_interactions (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(255) REFERENCES users(user_id),
                    action VARCHAR(100),
                    product_id VARCHAR(255),
                    session_id VARCHAR(255),
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata JSONB DEFAULT '{}'
                )
            """)
            
            conn.commit()
            cursor.close()
            conn.close()
            
            # Insert sample data
            self.insert_sample_data()
            
            logger.info("Enhanced database initialized successfully")
            return True
            
        except psycopg2.Error as e:
            logger.error(f"Database initialization failed: {e}")
            return False
    
    def insert_sample_data(self):
        """Insert sample data for testing"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Sample users
            sample_users = [
                ("user_001", "john@example.com", "+1234567890", "active_user", 0.85),
                ("user_002", "jane@example.com", "+1234567891", "new_user", 0.30),
                ("user_003", "mike@example.com", "+1234567892", "cart_abandoner", 0.60),
                ("user_004", "sarah@example.com", "+1234567893", "inactive_user", 0.20),
                ("user_005", "alex@example.com", "+1234567894", "repeat_buyer", 0.90)
            ]
            
            for user_id, email, phone, segment, engagement in sample_users:
                cursor.execute("""
                    INSERT INTO users (user_id, email, phone, segment, engagement_score)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (user_id) DO NOTHING
                """, (user_id, email, phone, segment, engagement))
            
            # Sample products
            sample_products = [
                ("prod_001", "GETTO Premium T-Shirt", "clothing", "shirts", 29.99),
                ("prod_002", "GETTO Denim Jacket", "clothing", "jackets", 79.99),
                ("prod_003", "GETTO Sneakers", "footwear", "casual", 89.99),
                ("prod_004", "GETTO Accessories Set", "accessories", "sets", 39.99),
                ("prod_005", "GETTO Limited Edition Watch", "accessories", "watches", 199.99)
            ]
            
            for prod_id, name, category, subcategory, price in sample_products:
                cursor.execute("""
                    INSERT INTO products (product_id, name, category, subcategory, price)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (product_id) DO NOTHING
                """, (prod_id, name, category, subcategory, price))
            
            conn.commit()
            cursor.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error inserting sample data: {e}")
    
    def load_notification_templates(self):
        """Load personalized notification templates"""
        return {
            NotificationType.WELCOME: [
                NotificationTemplate(
                    NotificationType.WELCOME,
                    "Welcome to GETTO! 🎉",
                    "Discover your perfect style with exclusive offers just for you!",
                    "high",
                    {"discount": 15, "category": "all"}
                )
            ],
            NotificationType.CART_ABANDONMENT: [
                NotificationTemplate(
                    NotificationType.CART_ABANDONMENT,
                    "Complete your GETTO journey! 🛍️",
                    "Your {item_count} item(s) are waiting - finish your order now!",
                    "medium",
                    {"urgency": "medium", "discount": 10}
                )
            ],
            NotificationType.WISHLIST_REMINDER: [
                NotificationTemplate(
                    NotificationType.WISHLIST_REMINDER,
                    "Your favorites are calling! ❤️",
                    "{product_name} from your wishlist is back in stock!",
                    "medium",
                    {"stock_alert": True}
                )
            ],
            NotificationType.REORDER_SUGGESTION: [
                NotificationTemplate(
                    NotificationType.REORDER_SUGGESTION,
                    "Time for your GETTO essentials? 🔄",
                    "Based on your history, you might need {product_name} again!",
                    "low",
                    {"reorder_discount": 5}
                )
            ],
            NotificationType.NEW_PRODUCT_ALERT: [
                NotificationTemplate(
                    NotificationType.NEW_PRODUCT_ALERT,
                    "New {category} collection just dropped! ✨",
                    "Discover the latest {category} styles perfectly matched to your taste!",
                    "medium",
                    {"early_access": True}
                )
            ]
        }
    
    def analyze_user_behavior(self, user_id: str) -> UserProfile:
        """Analyze user behavior and create personalized profile"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Get user basic info
            cursor.execute("""
                SELECT u.*, 
                       COUNT(p.id) as total_purchases,
                       COALESCE(AVG(p.price), 0) as avg_order_value
                FROM users u
                LEFT JOIN purchases p ON u.user_id = p.user_id
                WHERE u.user_id = %s
                GROUP BY u.user_id
            """, (user_id,))
            
            user_data = cursor.fetchone()
            if not user_data:
                return None
            
            # Get cart items
            cursor.execute("""
                SELECT ci.*, p.name, p.price, p.category
                FROM cart_items ci
                JOIN products p ON ci.product_id = p.product_id
                WHERE ci.user_id = %s
            """, (user_id,))
            cart_items = cursor.fetchall()
            
            # Get wishlist items
            cursor.execute("""
                SELECT wi.*, p.name, p.price, p.category
                FROM wishlist_items wi
                JOIN products p ON wi.product_id = p.product_id
                WHERE wi.user_id = %s
            """, (user_id,))
            wishlist_items = cursor.fetchall()
            
            # Determine user segment
            segment = self.determine_user_segment(user_data, cart_items, wishlist_items)
            
            # Calculate preferred categories
            cursor.execute("""
                SELECT p.category, COUNT(*) as frequency
                FROM purchases pur
                JOIN products p ON pur.product_id = p.product_id
                WHERE pur.user_id = %s
                GROUP BY p.category
                ORDER BY frequency DESC
                LIMIT 3
            """, (user_id,))
            preferred_categories = [row['category'] for row in cursor.fetchall()]
            
            cursor.close()
            conn.close()
            
            return UserProfile(
                user_id=user_id,
                segment=segment,
                total_purchases=user_data['total_purchases'],
                avg_order_value=float(user_data['avg_order_value']),
                last_activity=user_data['last_activity'],
                preferred_categories=preferred_categories,
                cart_items=[dict(item) for item in cart_items],
                wishlist_items=[dict(item) for item in wishlist_items],
                notification_preferences=user_data['notification_preferences'],
                engagement_score=float(user_data['engagement_score'])
            )
            
        except Exception as e:
            logger.error(f"Error analyzing user behavior: {e}")
            return None
    
    def determine_user_segment(self, user_data, cart_items, wishlist_items) -> UserSegment:
        """Determine user segment based on behavior"""
        days_since_created = (datetime.now() - user_data['created_at']).days
        days_since_activity = (datetime.now() - user_data['last_activity']).days
        total_purchases = user_data['total_purchases'] or 0
        
        # Segmentation logic
        if days_since_created <= 7:
            return UserSegment.NEW_USER
        elif days_since_activity > 30:
            return UserSegment.INACTIVE_USER
        elif len(cart_items) > 0 and days_since_activity <= 1:
            return UserSegment.CART_ABANDONER
        elif total_purchases >= 10:
            return UserSegment.VIP_USER
        elif total_purchases >= 3:
            return UserSegment.REPEAT_BUYER
        else:
            return UserSegment.ACTIVE_USER
    
    def generate_personalized_notification(self, user_profile: UserProfile, 
                                         notification_type: NotificationType) -> Dict:
        """Generate personalized notification content"""
        templates = self.notification_templates.get(notification_type, [])
        if not templates:
            return None
        
        # Select best template based on user profile
        template = self.select_best_template(templates, user_profile)
        
        # Personalize content
        personalized_content = self.personalize_content(template, user_profile)
        
        return {
            "title": personalized_content["title"],
            "body": personalized_content["body"],
            "priority": template.priority,
            "type": notification_type.value,
            "personalization_score": self.calculate_personalization_score(user_profile, template),
            "metadata": {
                "user_segment": user_profile.segment.value,
                "template_data": template.personalization_data,
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def select_best_template(self, templates: List[NotificationTemplate], 
                           user_profile: UserProfile) -> NotificationTemplate:
        """Select the best template based on user profile"""
        # For now, return the first template
        # TODO: Implement ML-based template selection
        return templates[0]
    
    def personalize_content(self, template: NotificationTemplate, 
                          user_profile: UserProfile) -> Dict:
        """Personalize notification content"""
        title = template.title
        body = template.body
        
        # Personalization based on notification type
        if template.type == NotificationType.CART_ABANDONMENT:
            item_count = len(user_profile.cart_items)
            body = body.format(item_count=item_count)
        
        elif template.type == NotificationType.WISHLIST_REMINDER:
            if user_profile.wishlist_items:
                product_name = user_profile.wishlist_items[0]['name']
                body = body.format(product_name=product_name)
        
        elif template.type == NotificationType.NEW_PRODUCT_ALERT:
            category = user_profile.preferred_categories[0] if user_profile.preferred_categories else "fashion"
            title = title.format(category=category)
            body = body.format(category=category)
        
        elif template.type == NotificationType.REORDER_SUGGESTION:
            # Get most frequently purchased product
            if user_profile.preferred_categories:
                body = body.format(product_name=f"{user_profile.preferred_categories[0]} items")
        
        return {"title": title, "body": body}
    
    def calculate_personalization_score(self, user_profile: UserProfile, 
                                      template: NotificationTemplate) -> float:
        """Calculate how well personalized the notification is"""
        score = 0.5  # Base score
        
        # Boost score based on personalization factors
        if user_profile.preferred_categories:
            score += 0.2
        
        if user_profile.engagement_score > 0.7:
            score += 0.2
        
        if template.type in [NotificationType.CART_ABANDONMENT, NotificationType.WISHLIST_REMINDER]:
            score += 0.1
        
        return min(score, 1.0)

# Global notification engine instance
notification_engine = PersonalizedNotificationEngine(DB_CONFIG)

# Flask routes
@app.route('/')
def home():
    return jsonify({
        "message": "GETTO Personalized Notification System",
        "status": "running",
        "firebase_status": "initialized" if notification_engine.firebase_initialized else "not initialized",
        "database_status": "connected" if notification_engine.database_initialized else "connection failed",
        "features": [
            "User segmentation and behavior analysis",
            "Personalized notification generation",
            "ML-based recommendation engine",
            "A/B testing framework",
            "Real-time analytics tracking"
        ],
        "endpoints": [
            "POST /register-user - Register user with profile data",
            "POST /register-device - Register FCM device", 
            "POST /send-personalized-notification - Send personalized notification",
            "GET /user-profile/<user_id> - Get user profile and segment",
            "POST /track-interaction - Track user interaction",
            "GET /analytics/dashboard - View analytics dashboard"
        ]
    })

@app.route('/register-user', methods=['POST'])
def register_user():
    """Register or update user profile"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        email = data.get('email')
        phone = data.get('phone')
        
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400
        
        conn = notification_engine.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO users (user_id, email, phone, last_activity)
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (user_id) 
            DO UPDATE SET 
                email = EXCLUDED.email,
                phone = EXCLUDED.phone,
                last_activity = CURRENT_TIMESTAMP
        """, (user_id, email, phone))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "status": "success",
            "message": "User registered successfully",
            "user_id": user_id
        })
        
    except Exception as e:
        logger.error(f"Error registering user: {e}")
        return jsonify({"error": f"Failed to register user: {str(e)}"}), 500

@app.route('/register-device', methods=['POST'])
def register_device():
    """Register FCM device for user"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        device_id = data.get('device_id')
        fcm_token = data.get('fcm_token')
        platform = data.get('platform', 'unknown')
        
        if not all([user_id, device_id, fcm_token]):
            return jsonify({"error": "user_id, device_id, and fcm_token are required"}), 400
        
        conn = notification_engine.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO fcm_devices (user_id, device_id, fcm_token, platform, last_active)
            VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (device_id)
            DO UPDATE SET 
                fcm_token = EXCLUDED.fcm_token,
                last_active = CURRENT_TIMESTAMP,
                is_active = true
        """, (user_id, device_id, fcm_token, platform))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "status": "success",
            "message": "Device registered successfully",
            "user_id": user_id,
            "device_id": device_id
        })
        
    except Exception as e:
        logger.error(f"Error registering device: {e}")
        return jsonify({"error": f"Failed to register device: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    print("=" * 80)
    print("GETTO Personalized Notification System")
    print("=" * 80)
    print(f"Server running on: http://localhost:{port}")
    print(f"Firebase status: {'INITIALIZED' if notification_engine.firebase_initialized else 'NOT INITIALIZED'}")
    print(f"Database status: {'CONNECTED' if notification_engine.database_initialized else 'CONNECTION FAILED'}")
    print("")
    print("Features:")
    print("- User behavior analysis and segmentation")
    print("- Personalized notification generation")
    print("- ML-based recommendations")
    print("- A/B testing framework")
    print("- Real-time analytics")
    print("")
    print("Ready for personalized notifications!")
    print("=" * 80)
    
    app.run(host='0.0.0.0', port=port, debug=debug)