"""
Pinterest Trend Analyzer Module
"""

import os
import requests
from typing import List, Dict, Optional
from ratelimit import limits, sleep_and_retry
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('trends.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class TrendAnalyzer:
    def __init__(self):
        self.pinterest_token = os.getenv("PINTEREST_ACCESS_TOKEN")
        self.beauty_keywords = {
            'skincare': {'serum', 'moisturizer', 'retinol', 'SPF', 'glow'},
            'haircare': {'shampoo', 'conditioner', 'mask', 'scalp', 'curls'},
            'makeup': {'lipstick', 'foundation', 'concealer', 'blush', 'mascara'}
        }
        self.last_fetch_time = None

    @sleep_and_retry
    @limits(calls=5, period=60)  # Pinterest API rate limit
    def get_pinterest_trends(self) -> List[Dict]:
        """Fetches raw trending data from Pinterest API"""
        if not self._check_token_valid():
            logger.error("Invalid Pinterest API token")
            return []

        url = "https://api.pinterest.com/v5/trending/topics"
        headers = {"Authorization": f"Bearer {self.pinterest_token}"}
        params = {
            "scope": "beauty",
            "region": "US",
            "limit": 50  # Get more for better filtering
        }

        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            self.last_fetch_time = datetime.now()
            return response.json().get('data', [])
        except Exception as e:
            logger.error(f"Pinterest API error: {str(e)}")
            return []

    def filter_beauty_trends(self, trends: List[Dict]) -> List[Dict]:
        """Filters trends to only beauty-related with keyword matching"""
        valid_trends = []

        for trend in trends:
            trend_query = trend.get('query', '').lower()
            for category, keywords in self.beauty_keywords.items():
                if any(keyword in trend_query for keyword in keywords):
                    valid_trends.append({
                        'query': trend_query,
                        'category': category,
                        'volume': trend.get('volume', 0)
                    })
                    break

        # Sort by descending popularity
        return sorted(valid_trends, key=lambda x: x['volume'], reverse=True)

    def get_daily_beauty_trends(self, max_trends: int = 5) -> List[Dict]:
        """Main method to get top beauty trends"""
        if not self._check_token_valid():
            logger.error("Invalid Pinterest API token")
            return []

        raw_trends = self.get_pinterest_trends()
        if not raw_trends:
            logger.warning("No trends fetched from API")
            return []

        beauty_trends = self.filter_beauty_trends(raw_trends)

        # Apply additional filters
        filtered = [
            t for t in beauty_trends
            if not self._is_blacklisted(t['query'])
        ][:max_trends]

        logger.info(f"Found {len(filtered)} beauty trends")
        return filtered

    def _check_token_valid(self) -> bool:
        """Validates API token format"""
        token = self.pinterest_token or ""
        return token.startswith("pina_") and len(token) > 30

    def _is_blacklisted(self, query: str) -> bool:
        """Filters out unwanted trends"""
        blacklist = {
            'sale', 'discount', 'free', 'cheap',
            'tutorial', 'how to', 'DIY'
        }
        query_words = set(query.split())
        return bool(query_words & blacklist)

# Example usage
if __name__ == "__main__":
    analyzer = TrendAnalyzer()

    try:
        trends = analyzer.get_daily_beauty_trends()
        print("Top Beauty Trends:")
        for i, trend in enumerate(trends, 1):
            print(f"{i}. {trend['query']} ({trend['category']}) - Volume: {trend['volume']}")
    except Exception as e:
        logger.error(f"Trend analysis failed: {str(e)}")
        raise
