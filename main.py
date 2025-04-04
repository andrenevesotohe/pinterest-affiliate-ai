"""
Pinterest Affiliate Automation AI

This script orchestrates the automated process of:
1. Finding beauty trends on Pinterest
2. Generating content for each trend
3. Posting to Pinterest with affiliate links
"""

import os
import logging
import argparse
from dotenv import load_dotenv
from modules import TrendAnalyzer, PinterestPoster, ContentGenerator
from unittest.mock import MagicMock, patch

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_mock_trends():
    """Return mock trends for test mode."""
    return [
        {
            'query': 'natural skincare routine',
            'category': 'skincare',
            'volume': 1000
        },
        {
            'query': 'curly hair care',
            'category': 'haircare',
            'volume': 800
        },
        {
            'query': 'minimal makeup look',
            'category': 'makeup',
            'volume': 600
        }
    ]

def daily_post(dry_run=False, test_mode=False):
    """Run the daily posting process."""
    try:
        # 1. Get trends
        logger.info("Fetching beauty trends...")
        if test_mode:
            analyzer = MagicMock()
            analyzer.get_daily_beauty_trends.return_value = get_mock_trends()
            trends = analyzer.get_daily_beauty_trends()
            logger.info("Using mock trends for testing")
        else:
            analyzer = TrendAnalyzer()
            trends = analyzer.get_daily_beauty_trends(max_trends=5)

        if not trends:
            logger.error("No trends found")
            return

        # 2. Generate content
        logger.info(f"Found {len(trends)} trends, generating content...")
        generator = ContentGenerator()
        poster = PinterestPoster()

        for trend in trends:
            logger.info(f"Processing trend: {trend['query']}")
            content = generator.create_post(trend)

            if content:
                if dry_run or test_mode:
                    logger.info("DRY RUN/TEST MODE - Would post:")
                    logger.info(f"Caption: {content['caption']}")
                    logger.info(f"Image URL: {content['image_url']}")
                    logger.info(f"Affiliate Link: {content['affiliate_link']}")
                else:
                    success = poster.post(
                        image_url=content['image_url'],
                        caption=content['caption'],
                        link=content['affiliate_link']
                    )
                    if success:
                        logger.info(f"Successfully posted about {trend['query']}")
                    else:
                        logger.error(f"Failed to post about {trend['query']}")
            else:
                logger.error(f"Failed to generate content for {trend['query']}")

    except Exception as e:
        logger.error(f"Error in daily post: {e}")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run Pinterest Affiliate Automation')
    parser.add_argument('--dry-run', action='store_true', help='Run without actually posting')
    parser.add_argument('--test-mode', action='store_true', help='Run with mock APIs for testing')
    args = parser.parse_args()

    daily_post(dry_run=args.dry_run, test_mode=args.test_mode)
