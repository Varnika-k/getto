#!/usr/bin/env python3
"""
GETTO ML-Based Recommendation Engine
Advanced machine learning system for personalized product recommendations and notification timing
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Tuple, Optional
import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)

class MLRecommendationEngine:
    """
    Advanced ML-based recommendation engine for GETTO personalized notifications
    """
    
    def __init__(self, db_config: Dict):
        self.db_config = db_config
        self.user_item_matrix = None
        self.product_features = None
        self.user_clusters = None
        self.engagement_model = None
        self.timing_model = None
        self.scaler = StandardScaler()
        
        # Initialize models
        self.initialize_models()
    
    def get_db_connection(self):
        """Create database connection"""
        return psycopg2.connect(**self.db_config)
    
    def initialize_models(self):
        """Initialize and train ML models"""
        try:
            self.load_data()
            self.build_collaborative_filtering_model()
            self.build_content_based_model()
            self.build_user_clustering_model()
            self.build_engagement_prediction_model()
            self.build_timing_optimization_model()
            logger.info("All ML models initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing ML models: {e}")
    
    def load_data(self):
        """Load data from database for training"""
        try:
            conn = self.get_db_connection()
            
            # Load user-item interactions
            user_items_df = pd.read_sql("""
                SELECT u.user_id, p.product_id, p.name, p.category, p.price,
                       COUNT(pur.id) as purchase_count,
                       AVG(pur.price) as avg_price,
                       MAX(pur.purchase_date) as last_purchase
                FROM users u
                LEFT JOIN purchases pur ON u.user_id = pur.user_id
                LEFT JOIN products p ON pur.product_id = p.product_id
                WHERE p.product_id IS NOT NULL
                GROUP BY u.user_id, p.product_id, p.name, p.category, p.price
            """, conn)
            
            # Load user features
            user_features_df = pd.read_sql("""
                SELECT u.user_id, u.total_purchases, u.total_spent, u.avg_order_value,
                       u.engagement_score, u.segment, u.preferred_categories,
                       EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - u.last_activity))/86400 as days_inactive,
                       EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - u.created_at))/86400 as account_age
                FROM users u
            """, conn)
            
            # Load product features
            products_df = pd.read_sql("""
                SELECT product_id, name, category, subcategory, price, tags
                FROM products WHERE is_active = true
            """, conn)
            
            # Load notification history for training
            notifications_df = pd.read_sql("""
                SELECT nh.user_id, nh.notification_type, nh.sent_at, nh.opened_at, 
                       nh.clicked_at, nh.converted_at, nh.personalization_score,
                       CASE WHEN nh.opened_at IS NOT NULL THEN 1 ELSE 0 END as opened,
                       CASE WHEN nh.clicked_at IS NOT NULL THEN 1 ELSE 0 END as clicked,
                       CASE WHEN nh.converted_at IS NOT NULL THEN 1 ELSE 0 END as converted,
                       EXTRACT(HOUR FROM nh.sent_at) as sent_hour,
                       EXTRACT(DOW FROM nh.sent_at) as sent_day_of_week
                FROM notification_history nh
                WHERE nh.sent_at > CURRENT_TIMESTAMP - INTERVAL '30 days'
            """, conn)
            
            conn.close()
            
            self.user_items_df = user_items_df
            self.user_features_df = user_features_df
            self.products_df = products_df
            self.notifications_df = notifications_df
            
            logger.info(f"Loaded data: {len(user_items_df)} interactions, {len(user_features_df)} users, {len(products_df)} products")
            
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise
    
    def build_collaborative_filtering_model(self):
        """Build collaborative filtering recommendation model"""
        try:
            if self.user_items_df.empty:
                logger.warning("No user-item data available for collaborative filtering")
                return
            
            # Create user-item matrix
            self.user_item_matrix = self.user_items_df.pivot_table(
                index='user_id', 
                columns='product_id', 
                values='purchase_count', 
                fill_value=0
            )
            
            # Calculate user similarity matrix
            user_similarity = cosine_similarity(self.user_item_matrix)
            self.user_similarity_df = pd.DataFrame(
                user_similarity, 
                index=self.user_item_matrix.index, 
                columns=self.user_item_matrix.index
            )
            
            logger.info(f"Built collaborative filtering model with {self.user_item_matrix.shape[0]} users and {self.user_item_matrix.shape[1]} products")
            
        except Exception as e:
            logger.error(f"Error building collaborative filtering model: {e}")
    
    def build_content_based_model(self):
        """Build content-based recommendation model"""
        try:
            if self.products_df.empty:
                logger.warning("No product data available for content-based filtering")
                return
            
            # Create product feature matrix
            products_text = self.products_df['name'] + ' ' + \
                          self.products_df['category'] + ' ' + \
                          self.products_df['subcategory'].fillna('')
            
            # TF-IDF vectorization
            self.tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
            self.product_tfidf_matrix = self.tfidf_vectorizer.fit_transform(products_text)
            
            # Calculate product similarity matrix
            product_similarity = cosine_similarity(self.product_tfidf_matrix)
            self.product_similarity_df = pd.DataFrame(
                product_similarity,
                index=self.products_df['product_id'],
                columns=self.products_df['product_id']
            )
            
            logger.info(f"Built content-based model with {len(self.products_df)} products")
            
        except Exception as e:
            logger.error(f"Error building content-based model: {e}")
    
    def build_user_clustering_model(self):
        """Build user clustering model for segmentation"""
        try:
            if self.user_features_df.empty:
                logger.warning("No user data available for clustering")
                return
            
            # Prepare features for clustering
            clustering_features = ['total_purchases', 'total_spent', 'avg_order_value', 
                                 'engagement_score', 'days_inactive', 'account_age']
            
            X = self.user_features_df[clustering_features].fillna(0)
            X_scaled = self.scaler.fit_transform(X)
            
            # K-means clustering
            self.kmeans = KMeans(n_clusters=5, random_state=42)
            user_clusters = self.kmeans.fit_predict(X_scaled)
            
            self.user_features_df['ml_cluster'] = user_clusters
            
            logger.info(f"Built user clustering model with 5 clusters for {len(self.user_features_df)} users")
            
        except Exception as e:
            logger.error(f"Error building user clustering model: {e}")
    
    def build_engagement_prediction_model(self):
        """Build model to predict notification engagement"""
        try:
            if self.notifications_df.empty:
                logger.warning("No notification data available for engagement prediction")
                return
            
            # Prepare features
            feature_cols = ['personalization_score', 'sent_hour', 'sent_day_of_week']
            X = self.notifications_df[feature_cols].fillna(0)
            y = self.notifications_df['opened'].fillna(0)
            
            if len(X) < 10:
                logger.warning("Insufficient data for engagement model training")
                return
            
            # Train random forest model
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            self.engagement_model = RandomForestClassifier(n_estimators=100, random_state=42)
            self.engagement_model.fit(X_train, y_train)
            
            # Calculate accuracy
            accuracy = self.engagement_model.score(X_test, y_test)
            logger.info(f"Built engagement prediction model with accuracy: {accuracy:.3f}")
            
        except Exception as e:
            logger.error(f"Error building engagement prediction model: {e}")
    
    def build_timing_optimization_model(self):
        """Build model to optimize notification timing"""
        try:
            if self.notifications_df.empty:
                return
            
            # Group by hour to find optimal sending times
            hourly_engagement = self.notifications_df.groupby('sent_hour').agg({
                'opened': 'mean',
                'clicked': 'mean',
                'converted': 'mean'
            }).reset_index()
            
            # Find best hours for each metric
            self.optimal_hours = {
                'opens': hourly_engagement.loc[hourly_engagement['opened'].idxmax(), 'sent_hour'],
                'clicks': hourly_engagement.loc[hourly_engagement['clicked'].idxmax(), 'sent_hour'],
                'conversions': hourly_engagement.loc[hourly_engagement['converted'].idxmax(), 'sent_hour']
            }
            
            logger.info(f"Built timing optimization model. Best hours: {self.optimal_hours}")
            
        except Exception as e:
            logger.error(f"Error building timing optimization model: {e}")
    
    def get_collaborative_recommendations(self, user_id: str, n_recommendations: int = 5) -> List[str]:
        """Get collaborative filtering recommendations"""
        try:
            if self.user_item_matrix is None or user_id not in self.user_item_matrix.index:
                return []
            
            # Get similar users
            user_similarities = self.user_similarity_df.loc[user_id].sort_values(ascending=False)[1:6]
            
            # Get products purchased by similar users
            similar_users = user_similarities.index.tolist()
            recommendations = []
            
            for similar_user in similar_users:
                user_purchases = self.user_item_matrix.loc[similar_user]
                # Get products this user hasn't purchased
                current_user_purchases = self.user_item_matrix.loc[user_id]
                new_products = user_purchases[current_user_purchases == 0]
                recommendations.extend(new_products[new_products > 0].index.tolist())
            
            # Return unique recommendations
            return list(set(recommendations))[:n_recommendations]
            
        except Exception as e:
            logger.error(f"Error getting collaborative recommendations: {e}")
            return []
    
    def get_content_based_recommendations(self, user_id: str, n_recommendations: int = 5) -> List[str]:
        """Get content-based recommendations"""
        try:
            if self.product_similarity_df is None:
                return []
            
            # Get user's purchase history
            user_purchases = self.user_items_df[self.user_items_df['user_id'] == user_id]['product_id'].tolist()
            
            if not user_purchases:
                return []
            
            # Find similar products
            recommendations = []
            for product_id in user_purchases:
                if product_id in self.product_similarity_df.index:
                    similar_products = self.product_similarity_df.loc[product_id].sort_values(ascending=False)[1:4]
                    recommendations.extend(similar_products.index.tolist())
            
            # Return unique recommendations
            return list(set(recommendations))[:n_recommendations]
            
        except Exception as e:
            logger.error(f"Error getting content-based recommendations: {e}")
            return []
    
    def get_hybrid_recommendations(self, user_id: str, n_recommendations: int = 5) -> List[Dict]:
        """Get hybrid recommendations combining collaborative and content-based"""
        try:
            # Get recommendations from both approaches
            collab_recs = self.get_collaborative_recommendations(user_id, n_recommendations)
            content_recs = self.get_content_based_recommendations(user_id, n_recommendations)
            
            # Combine and weight recommendations
            all_recs = {}
            
            # Weight collaborative filtering recommendations higher
            for i, product_id in enumerate(collab_recs):
                score = (len(collab_recs) - i) / len(collab_recs) * 0.7
                all_recs[product_id] = all_recs.get(product_id, 0) + score
            
            # Weight content-based recommendations
            for i, product_id in enumerate(content_recs):
                score = (len(content_recs) - i) / len(content_recs) * 0.3
                all_recs[product_id] = all_recs.get(product_id, 0) + score
            
            # Sort by score and get product details
            sorted_recs = sorted(all_recs.items(), key=lambda x: x[1], reverse=True)
            
            recommendations = []
            for product_id, score in sorted_recs[:n_recommendations]:
                product_info = self.products_df[self.products_df['product_id'] == product_id]
                if not product_info.empty:
                    recommendations.append({
                        'product_id': product_id,
                        'name': product_info.iloc[0]['name'],
                        'category': product_info.iloc[0]['category'],
                        'price': float(product_info.iloc[0]['price']),
                        'recommendation_score': score
                    })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting hybrid recommendations: {e}")
            return []
    
    def predict_engagement(self, personalization_score: float, hour: int, day_of_week: int) -> float:
        """Predict notification engagement probability"""
        try:
            if self.engagement_model is None:
                return 0.5  # Default probability
            
            features = np.array([[personalization_score, hour, day_of_week]])
            probability = self.engagement_model.predict_proba(features)[0][1]
            return probability
            
        except Exception as e:
            logger.error(f"Error predicting engagement: {e}")
            return 0.5
    
    def get_optimal_send_time(self, user_id: str, metric: str = 'opens') -> int:
        """Get optimal hour to send notification for maximum engagement"""
        try:
            if hasattr(self, 'optimal_hours') and metric in self.optimal_hours:
                return self.optimal_hours[metric]
            
            # Default optimal hours based on general patterns
            default_hours = {'opens': 10, 'clicks': 14, 'conversions': 19}
            return default_hours.get(metric, 10)
            
        except Exception as e:
            logger.error(f"Error getting optimal send time: {e}")
            return 10
    
    def update_user_engagement_score(self, user_id: str, interaction_type: str):
        """Update user engagement score based on interaction"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Calculate engagement boost based on interaction type
            engagement_boost = {
                'opened': 0.05,
                'clicked': 0.10,
                'converted': 0.20,
                'unsubscribed': -0.30
            }
            
            boost = engagement_boost.get(interaction_type, 0)
            
            cursor.execute("""
                UPDATE users 
                SET engagement_score = LEAST(1.0, GREATEST(0.0, engagement_score + %s))
                WHERE user_id = %s
            """, (boost, user_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"Updated engagement score for user {user_id} with {interaction_type}")
            
        except Exception as e:
            logger.error(f"Error updating engagement score: {e}")
    
    def retrain_models(self):
        """Retrain all ML models with latest data"""
        try:
            logger.info("Starting model retraining...")
            self.load_data()
            self.build_collaborative_filtering_model()
            self.build_content_based_model()
            self.build_user_clustering_model()
            self.build_engagement_prediction_model()
            self.build_timing_optimization_model()
            logger.info("Model retraining completed successfully")
            
        except Exception as e:
            logger.error(f"Error retraining models: {e}")
    
    def save_models(self, model_path: str = "ml_models/"):
        """Save trained models to disk"""
        try:
            import os
            os.makedirs(model_path, exist_ok=True)
            
            # Save models that can be serialized
            if self.engagement_model is not None:
                joblib.dump(self.engagement_model, f"{model_path}/engagement_model.pkl")
            
            if self.kmeans is not None:
                joblib.dump(self.kmeans, f"{model_path}/user_clustering_model.pkl")
            
            if self.scaler is not None:
                joblib.dump(self.scaler, f"{model_path}/scaler.pkl")
            
            logger.info(f"Models saved to {model_path}")
            
        except Exception as e:
            logger.error(f"Error saving models: {e}")
    
    def load_models(self, model_path: str = "ml_models/"):
        """Load trained models from disk"""
        try:
            import os
            
            if os.path.exists(f"{model_path}/engagement_model.pkl"):
                self.engagement_model = joblib.load(f"{model_path}/engagement_model.pkl")
            
            if os.path.exists(f"{model_path}/user_clustering_model.pkl"):
                self.kmeans = joblib.load(f"{model_path}/user_clustering_model.pkl")
            
            if os.path.exists(f"{model_path}/scaler.pkl"):
                self.scaler = joblib.load(f"{model_path}/scaler.pkl")
            
            logger.info(f"Models loaded from {model_path}")
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")

# Usage example
if __name__ == "__main__":
    # Example usage
    db_config = {
        'host': 'localhost',
        'port': '5433',
        'database': 'getto_personalized',
        'user': 'postgres',
        'password': 'password'
    }
    
    # Initialize ML engine
    ml_engine = MLRecommendationEngine(db_config)
    
    # Get recommendations for a user
    recommendations = ml_engine.get_hybrid_recommendations("user_001", n_recommendations=5)
    print("Recommendations:", recommendations)
    
    # Predict engagement
    engagement_prob = ml_engine.predict_engagement(0.8, 14, 1)  # High personalization, 2 PM, Tuesday
    print("Engagement probability:", engagement_prob)
    
    # Get optimal send time
    optimal_hour = ml_engine.get_optimal_send_time("user_001", "clicks")
    print("Optimal send time:", optimal_hour)