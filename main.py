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
import json
from pathlib import Path
from dotenv import load_dotenv
from modules import TrendAnalyzer, PinterestPoster, ContentGenerator
from modules.budget_tracker import DalleBudgetTracker
from unittest.mock import MagicMock, patch

# Load environment variables
load_dotenv()

# Create logs directory if it doesn't exist
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(logs_dir / "pinterest.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configure error logging
error_logger = logging.getLogger("errors")
error_handler = logging.FileHandler(logs_dir / "errors.log")
error_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
error_logger.addHandler(error_handler)
error_logger.setLevel(logging.ERROR)

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

def clear_fallback_queue():
    """Clear the fallback queue by writing an empty list to the file."""
    try:
        with open('fallback_queue.json', 'w') as f:
            json.dump([], f)
        logger.info("Fallback queue cleared")
    except Exception as e:
        error_logger.error(f"Failed to clear fallback queue: {e}")

def daily_post(dry_run=False, test_mode=False, limit=None, budget=None):
    """Run the daily posting process.
    
    Args:
        dry_run: If True, don't actually post to Pinterest
        test_mode: If True, use mock data instead of real API calls
        limit: Maximum number of posts to create (None for all)
        budget: Maximum DALL-E budget to use (None for default)
    """
    try:
        # Clear fallback queue in test mode
        if test_mode:
            clear_fallback_queue()
            logger.info("Test mode: Fallback queue cleared")
        
        # Initialize budget tracker if budget is specified
        dalle_budget = None
        if budget is not None:
            dalle_budget = DalleBudgetTracker(daily_limit=budget)
            logger.info(f"Using DALL-E budget: ${budget:.2f}")
        
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
        
        # Apply post limit if specified
        if limit is not None:
            trends = trends[:limit]
            logger.info(f"Limited to {limit} posts")

        if not trends:
            logger.error("No trends found")
            return

        # 2. Generate content
        logger.info(f"Found {len(trends)} trends, generating content...")
        
        # In test mode, use mock content generator to avoid API charges
        if test_mode:
            generator = MagicMock()
            generator.create_post.side_effect = lambda trend: {
                'caption': f"Test pin for {trend['query']} #beauty #test",
                'image_url': "https://example.com/test-image.jpg",
                'affiliate_link': "https://amazon.com/test-product?tag=test123"
            }
            logger.info("Using mock content generator to avoid API charges")
        else:
            generator = ContentGenerator()
            
        poster = PinterestPoster()
        
        # Override budget tracker if specified
        if dalle_budget is not None and not test_mode:
            generator.dalle_budget_tracker = dalle_budget

        successful_posts = 0
        for trend in trends:
            logger.info(f"Processing trend: {trend['query']}")
            content = generator.create_post(trend)

            if content:
                if dry_run or test_mode:
                    logger.info("DRY RUN/TEST MODE - Would post:")
                    logger.info(f"Caption: {content['caption']}")
                    logger.info(f"Image URL: {content['image_url']}")
                    logger.info(f"Affiliate Link: {content['affiliate_link']}")
                    successful_posts += 1
                else:
                    success = poster.post(
                        image_url=content['image_url'],
                        caption=content['caption'],
                        link=content['affiliate_link']
                    )
                    if success:
                        logger.info(f"Successfully posted about {trend['query']}")
                        successful_posts += 1
                    else:
                        logger.error(f"Failed to post about {trend['query']}")
            else:
                logger.error(f"Failed to generate content for {trend['query']}")
        
        # Process fallback queue if not in dry run or test mode
        if not dry_run and not test_mode:
            processed = poster.process_fallback_queue()
            if processed > 0:
                logger.info(f"Processed {processed} items from fallback queue")
        
        logger.info(f"Completed with {successful_posts} successful posts out of {len(trends)} trends")
        
        # Verify fallback queue is empty in test mode
        if test_mode:
            with open('fallback_queue.json', 'r') as f:
                queue = json.load(f)
                if queue:
                    logger.warning(f"Test mode: Fallback queue not empty ({len(queue)} items)")
                else:
                    logger.info("Test mode: Fallback queue verified empty")

    except Exception as e:
        error_logger.error(f"Error in daily post: {e}")
        logger.error(f"Error in daily post: {e}")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run Pinterest Affiliate Automation')
    parser.add_argument('--dry-run', action='store_true', help='Run without actually posting')
    parser.add_argument('--test-mode', action='store_true', help='Run with mock APIs for testing')
    parser.add_argument('--limit', type=int, help='Maximum number of posts to create')
    parser.add_argument('--budget', type=float, help='Maximum DALL-E budget to use in USD')
    args = parser.parse_args()

    daily_post(
        dry_run=args.dry_run, 
        test_mode=args.test_mode,
        limit=args.limit,
        budget=args.budget
    )
