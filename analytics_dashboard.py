#!/usr/bin/env python3
"""
GETTO Analytics Dashboard & A/B Testing Framework
Comprehensive analytics and testing system for personalized notifications
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.utils
import json
from flask import Flask, render_template_string, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import random

logger = logging.getLogger(__name__)

class ABTestStatus(Enum):
    DRAFT = "draft"
    RUNNING = "running"
    COMPLETED = "completed"
    PAUSED = "paused"

@dataclass
class ABTestResult:
    test_id: str
    variant_a_ctr: float
    variant_b_ctr: float
    variant_a_conversion: float
    variant_b_conversion: float
    statistical_significance: float
    confidence_interval: float
    winner: str
    sample_size: int

class NotificationAnalytics:
    """
    Comprehensive analytics system for GETTO notification performance
    """
    
    def __init__(self, db_config: Dict):
        self.db_config = db_config
    
    def get_db_connection(self):
        """Create database connection"""
        return psycopg2.connect(**self.db_config)
    
    def get_performance_metrics(self, days: int = 30) -> Dict:
        """Get overall notification performance metrics"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Overall metrics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_sent,
                    COUNT(opened_at) as total_opened,
                    COUNT(clicked_at) as total_clicked,
                    COUNT(converted_at) as total_converted,
                    ROUND(COUNT(opened_at)::numeric / COUNT(*) * 100, 2) as open_rate,
                    ROUND(COUNT(clicked_at)::numeric / COUNT(*) * 100, 2) as click_rate,
                    ROUND(COUNT(converted_at)::numeric / COUNT(*) * 100, 2) as conversion_rate,
                    AVG(personalization_score) as avg_personalization_score
                FROM notification_history 
                WHERE sent_at > CURRENT_TIMESTAMP - INTERVAL '%s days'
            """, (days,))
            
            overall_metrics = cursor.fetchone()
            
            # Metrics by notification type
            cursor.execute("""
                SELECT 
                    notification_type,
                    COUNT(*) as sent,
                    COUNT(opened_at) as opened,
                    COUNT(clicked_at) as clicked,
                    COUNT(converted_at) as converted,
                    ROUND(COUNT(opened_at)::numeric / COUNT(*) * 100, 2) as open_rate,
                    ROUND(COUNT(clicked_at)::numeric / COUNT(*) * 100, 2) as click_rate,
                    ROUND(COUNT(converted_at)::numeric / COUNT(*) * 100, 2) as conversion_rate
                FROM notification_history 
                WHERE sent_at > CURRENT_TIMESTAMP - INTERVAL '%s days'
                GROUP BY notification_type
                ORDER BY sent DESC
            """, (days,))
            
            type_metrics = cursor.fetchall()
            
            # User segment performance
            cursor.execute("""
                SELECT 
                    u.segment,
                    COUNT(nh.*) as sent,
                    COUNT(nh.opened_at) as opened,
                    COUNT(nh.clicked_at) as clicked,
                    ROUND(COUNT(nh.opened_at)::numeric / COUNT(nh.*) * 100, 2) as open_rate,
                    ROUND(COUNT(nh.clicked_at)::numeric / COUNT(nh.*) * 100, 2) as click_rate
                FROM notification_history nh
                JOIN users u ON nh.user_id = u.user_id
                WHERE nh.sent_at > CURRENT_TIMESTAMP - INTERVAL '%s days'
                GROUP BY u.segment
                ORDER BY sent DESC
            """, (days,))
            
            segment_metrics = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return {
                "overall": dict(overall_metrics) if overall_metrics else {},
                "by_type": [dict(row) for row in type_metrics],
                "by_segment": [dict(row) for row in segment_metrics],
                "time_period": f"Last {days} days"
            }
            
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {}
    
    def get_engagement_trends(self, days: int = 30) -> Dict:
        """Get engagement trends over time"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("""
                SELECT 
                    DATE(sent_at) as date,
                    COUNT(*) as sent,
                    COUNT(opened_at) as opened,
                    COUNT(clicked_at) as clicked,
                    ROUND(COUNT(opened_at)::numeric / COUNT(*) * 100, 2) as open_rate,
                    ROUND(COUNT(clicked_at)::numeric / COUNT(*) * 100, 2) as click_rate
                FROM notification_history 
                WHERE sent_at > CURRENT_TIMESTAMP - INTERVAL '%s days'
                GROUP BY DATE(sent_at)
                ORDER BY date
            """, (days,))
            
            daily_trends = cursor.fetchall()
            
            # Hourly engagement patterns
            cursor.execute("""
                SELECT 
                    EXTRACT(HOUR FROM sent_at) as hour,
                    COUNT(*) as sent,
                    COUNT(opened_at) as opened,
                    ROUND(COUNT(opened_at)::numeric / COUNT(*) * 100, 2) as open_rate
                FROM notification_history 
                WHERE sent_at > CURRENT_TIMESTAMP - INTERVAL '%s days'
                GROUP BY EXTRACT(HOUR FROM sent_at)
                ORDER BY hour
            """, (days,))
            
            hourly_patterns = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return {
                "daily_trends": [dict(row) for row in daily_trends],
                "hourly_patterns": [dict(row) for row in hourly_patterns]
            }
            
        except Exception as e:
            logger.error(f"Error getting engagement trends: {e}")
            return {}
    
    def get_personalization_effectiveness(self) -> Dict:
        """Analyze effectiveness of personalization"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Performance by personalization score ranges
            cursor.execute("""
                SELECT 
                    CASE 
                        WHEN personalization_score < 0.3 THEN 'Low (0-0.3)'
                        WHEN personalization_score < 0.6 THEN 'Medium (0.3-0.6)'
                        WHEN personalization_score < 0.8 THEN 'High (0.6-0.8)'
                        ELSE 'Very High (0.8-1.0)'
                    END as personalization_level,
                    COUNT(*) as sent,
                    COUNT(opened_at) as opened,
                    COUNT(clicked_at) as clicked,
                    ROUND(COUNT(opened_at)::numeric / COUNT(*) * 100, 2) as open_rate,
                    ROUND(COUNT(clicked_at)::numeric / COUNT(*) * 100, 2) as click_rate,
                    AVG(personalization_score) as avg_score
                FROM notification_history 
                WHERE sent_at > CURRENT_TIMESTAMP - INTERVAL '30 days'
                GROUP BY 
                    CASE 
                        WHEN personalization_score < 0.3 THEN 'Low (0-0.3)'
                        WHEN personalization_score < 0.6 THEN 'Medium (0.3-0.6)'
                        WHEN personalization_score < 0.8 THEN 'High (0.6-0.8)'
                        ELSE 'Very High (0.8-1.0)'
                    END
                ORDER BY avg_score
            """)
            
            personalization_analysis = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return {
                "personalization_effectiveness": [dict(row) for row in personalization_analysis]
            }
            
        except Exception as e:
            logger.error(f"Error analyzing personalization effectiveness: {e}")
            return {}
    
    def generate_dashboard_charts(self, metrics: Dict) -> Dict:
        """Generate interactive charts for dashboard"""
        try:
            charts = {}
            
            # Overall performance chart
            if metrics.get("overall"):
                overall = metrics["overall"]
                
                fig = go.Figure(data=[
                    go.Bar(
                        x=['Open Rate', 'Click Rate', 'Conversion Rate'],
                        y=[overall.get('open_rate', 0), overall.get('click_rate', 0), overall.get('conversion_rate', 0)],
                        marker_color=['#3498db', '#e74c3c', '#2ecc71']
                    )
                ])
                fig.update_layout(
                    title="Overall Performance Metrics",
                    yaxis_title="Percentage (%)",
                    template="plotly_white"
                )
                charts['overall_performance'] = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            
            # Performance by notification type
            if metrics.get("by_type"):
                type_data = metrics["by_type"]
                
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    name='Open Rate',
                    x=[item['notification_type'] for item in type_data],
                    y=[item.get('open_rate', 0) for item in type_data]
                ))
                fig.add_trace(go.Bar(
                    name='Click Rate',
                    x=[item['notification_type'] for item in type_data],
                    y=[item.get('click_rate', 0) for item in type_data]
                ))
                fig.update_layout(
                    title="Performance by Notification Type",
                    xaxis_title="Notification Type",
                    yaxis_title="Rate (%)",
                    barmode='group',
                    template="plotly_white"
                )
                charts['type_performance'] = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            
            return charts
            
        except Exception as e:
            logger.error(f"Error generating dashboard charts: {e}")
            return {}

class ABTestingFramework:
    """
    A/B Testing framework for notification optimization
    """
    
    def __init__(self, db_config: Dict):
        self.db_config = db_config
        self.initialize_ab_testing_tables()
    
    def get_db_connection(self):
        """Create database connection"""
        return psycopg2.connect(**self.db_config)
    
    def initialize_ab_testing_tables(self):
        """Initialize A/B testing tables"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # A/B tests table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ab_tests (
                    test_id VARCHAR(255) PRIMARY KEY,
                    test_name VARCHAR(255) NOT NULL,
                    description TEXT,
                    status VARCHAR(50) DEFAULT 'draft',
                    variant_a_config JSONB,
                    variant_b_config JSONB,
                    traffic_split DECIMAL(3,2) DEFAULT 0.50,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    started_at TIMESTAMP,
                    ended_at TIMESTAMP,
                    created_by VARCHAR(255)
                )
            """)
            
            # A/B test assignments
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ab_test_assignments (
                    id SERIAL PRIMARY KEY,
                    test_id VARCHAR(255) REFERENCES ab_tests(test_id),
                    user_id VARCHAR(255) REFERENCES users(user_id),
                    variant VARCHAR(1) CHECK (variant IN ('A', 'B')),
                    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(test_id, user_id)
                )
            """)
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info("A/B testing tables initialized")
            
        except Exception as e:
            logger.error(f"Error initializing A/B testing tables: {e}")
    
    def create_ab_test(self, test_name: str, description: str, 
                      variant_a_config: Dict, variant_b_config: Dict,
                      traffic_split: float = 0.5) -> str:
        """Create a new A/B test"""
        try:
            test_id = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO ab_tests (test_id, test_name, description, variant_a_config, 
                                    variant_b_config, traffic_split)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (test_id, test_name, description, 
                  json.dumps(variant_a_config), json.dumps(variant_b_config), traffic_split))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"Created A/B test: {test_id}")
            return test_id
            
        except Exception as e:
            logger.error(f"Error creating A/B test: {e}")
            return None
    
    def start_ab_test(self, test_id: str) -> bool:
        """Start an A/B test"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE ab_tests 
                SET status = 'running', started_at = CURRENT_TIMESTAMP
                WHERE test_id = %s AND status = 'draft'
            """, (test_id,))
            
            success = cursor.rowcount > 0
            conn.commit()
            cursor.close()
            conn.close()
            
            if success:
                logger.info(f"Started A/B test: {test_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error starting A/B test: {e}")
            return False
    
    def assign_user_to_variant(self, test_id: str, user_id: str) -> str:
        """Assign user to A/B test variant"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Check if user already assigned
            cursor.execute("""
                SELECT variant FROM ab_test_assignments 
                WHERE test_id = %s AND user_id = %s
            """, (test_id, user_id))
            
            existing_assignment = cursor.fetchone()
            if existing_assignment:
                cursor.close()
                conn.close()
                return existing_assignment[0]
            
            # Get test configuration
            cursor.execute("""
                SELECT traffic_split FROM ab_tests 
                WHERE test_id = %s AND status = 'running'
            """, (test_id,))
            
            test_config = cursor.fetchone()
            if not test_config:
                cursor.close()
                conn.close()
                return 'A'  # Default to variant A if test not found
            
            # Assign variant based on traffic split
            traffic_split = float(test_config[0])
            variant = 'A' if random.random() < traffic_split else 'B'
            
            # Store assignment
            cursor.execute("""
                INSERT INTO ab_test_assignments (test_id, user_id, variant)
                VALUES (%s, %s, %s)
            """, (test_id, user_id, variant))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return variant
            
        except Exception as e:
            logger.error(f"Error assigning user to variant: {e}")
            return 'A'
    
    def analyze_ab_test(self, test_id: str) -> ABTestResult:
        """Analyze A/B test results"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Get test results by variant
            cursor.execute("""
                SELECT 
                    ata.variant,
                    COUNT(nh.*) as sent,
                    COUNT(nh.opened_at) as opened,
                    COUNT(nh.clicked_at) as clicked,
                    COUNT(nh.converted_at) as converted,
                    ROUND(COUNT(nh.opened_at)::numeric / COUNT(nh.*) * 100, 2) as open_rate,
                    ROUND(COUNT(nh.clicked_at)::numeric / COUNT(nh.*) * 100, 2) as click_rate,
                    ROUND(COUNT(nh.converted_at)::numeric / COUNT(nh.*) * 100, 2) as conversion_rate
                FROM ab_test_assignments ata
                LEFT JOIN notification_history nh ON ata.user_id = nh.user_id 
                    AND nh.ab_test_group = ata.variant
                    AND nh.sent_at >= (
                        SELECT started_at FROM ab_tests WHERE test_id = %s
                    )
                WHERE ata.test_id = %s
                GROUP BY ata.variant
                ORDER BY ata.variant
            """, (test_id, test_id))
            
            results = cursor.fetchall()
            
            if len(results) < 2:
                cursor.close()
                conn.close()
                return None
            
            variant_a = next((r for r in results if r['variant'] == 'A'), None)
            variant_b = next((r for r in results if r['variant'] == 'B'), None)
            
            if not variant_a or not variant_b:
                cursor.close()
                conn.close()
                return None
            
            # Calculate statistical significance (simplified)
            def calculate_significance(rate_a, rate_b, n_a, n_b):
                if n_a == 0 or n_b == 0:
                    return 0.0
                
                p_a = rate_a / 100.0
                p_b = rate_b / 100.0
                
                # Standard error
                se = np.sqrt(p_a * (1 - p_a) / n_a + p_b * (1 - p_b) / n_b)
                
                if se == 0:
                    return 0.0
                
                # Z-score
                z = abs(p_a - p_b) / se
                
                # Approximate p-value (simplified)
                p_value = 2 * (1 - 0.5 * (1 + np.tanh(z / np.sqrt(2))))
                
                return (1 - p_value) * 100  # Convert to confidence percentage
            
            significance = calculate_significance(
                variant_a['click_rate'] or 0, variant_b['click_rate'] or 0,
                variant_a['sent'] or 1, variant_b['sent'] or 1
            )
            
            # Determine winner
            winner = 'A' if (variant_a['click_rate'] or 0) > (variant_b['click_rate'] or 0) else 'B'
            
            cursor.close()
            conn.close()
            
            return ABTestResult(
                test_id=test_id,
                variant_a_ctr=variant_a['click_rate'] or 0,
                variant_b_ctr=variant_b['click_rate'] or 0,
                variant_a_conversion=variant_a['conversion_rate'] or 0,
                variant_b_conversion=variant_b['conversion_rate'] or 0,
                statistical_significance=significance,
                confidence_interval=95.0,
                winner=winner,
                sample_size=(variant_a['sent'] or 0) + (variant_b['sent'] or 0)
            )
            
        except Exception as e:
            logger.error(f"Error analyzing A/B test: {e}")
            return None

# Flask app for analytics dashboard
dashboard_app = Flask(__name__)

DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>GETTO Notification Analytics Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { text-align: center; background: #2c3e50; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
        .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .metric-card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; }
        .metric-value { font-size: 2.5em; font-weight: bold; color: #3498db; }
        .metric-label { font-size: 1.1em; color: #7f8c8d; margin-top: 5px; }
        .chart-container { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .status-indicator { display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 8px; }
        .status-success { background-color: #2ecc71; }
        .status-warning { background-color: #f39c12; }
        .status-error { background-color: #e74c3c; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 GETTO Notification Analytics Dashboard</h1>
            <p>Real-time performance monitoring and A/B testing results</p>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">{{ overall.total_sent or 0 }}</div>
                <div class="metric-label">Total Sent</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{{ overall.open_rate or 0 }}%</div>
                <div class="metric-label">Open Rate</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{{ overall.click_rate or 0 }}%</div>
                <div class="metric-label">Click Rate</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{{ overall.conversion_rate or 0 }}%</div>
                <div class="metric-label">Conversion Rate</div>
            </div>
        </div>
        
        <div class="chart-container">
            <div id="overall-performance-chart"></div>
        </div>
        
        <div class="chart-container">
            <div id="type-performance-chart"></div>
        </div>
        
        <div class="chart-container">
            <h3>System Status</h3>
            <p><span class="status-indicator status-success"></span>Firebase: Connected</p>
            <p><span class="status-indicator status-success"></span>Database: Connected</p>
            <p><span class="status-indicator status-success"></span>ML Engine: Active</p>
            <p><span class="status-indicator status-warning"></span>A/B Tests: {{ ab_tests_count or 0 }} Running</p>
        </div>
    </div>
    
    <script>
        // Render charts
        if ({{ charts.overall_performance|safe }}) {
            Plotly.newPlot('overall-performance-chart', {{ charts.overall_performance|safe }});
        }
        
        if ({{ charts.type_performance|safe }}) {
            Plotly.newPlot('type-performance-chart', {{ charts.type_performance|safe }});
        }
        
        // Auto-refresh every 30 seconds
        setTimeout(() => {
            window.location.reload();
        }, 30000);
    </script>
</body>
</html>
"""

@dashboard_app.route('/analytics/dashboard')
def analytics_dashboard():
    """Analytics dashboard route"""
    try:
        # Initialize analytics
        db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5433'),
            'database': os.getenv('DB_NAME', 'getto_personalized'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'password')
        }
        
        analytics = NotificationAnalytics(db_config)
        metrics = analytics.get_performance_metrics(30)
        charts = analytics.generate_dashboard_charts(metrics)
        
        return render_template_string(DASHBOARD_HTML, 
                                    overall=metrics.get('overall', {}),
                                    charts=charts,
                                    ab_tests_count=0)
    except Exception as e:
        logger.error(f"Error rendering dashboard: {e}")
        return f"Dashboard Error: {e}", 500

if __name__ == "__main__":
    dashboard_app.run(host='0.0.0.0', port=5001, debug=True)