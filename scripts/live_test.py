#!/usr/bin/env python3
"""
Live Test Script

This script runs a live test of the Pinterest Affiliate AI, actually posting to Pinterest.
"""

import os
import sys
import logging
import argparse
from dotenv import load_dotenv
from modules.trends import TrendAnalyzer
from modules.content_generator import ContentGenerator
from modules.poster import PinterestPoster
from modules.budget_tracker import DalleBudgetTracker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def live_test(limit=None, budget=None):
    """Run a live test of the Pinterest Affiliate AI, actually posting to Pinterest."""
    load_dotenv()
    
    # Initialize budget tracker if budget is specified
    dalle_budget = None
    if budget is not None:
        dalle_budget = DalleBudgetTracker(daily_limit=budget)
        logger.info(f"Using DALL-E budget: ${budget:.2f}")
    
    # 1. Get trends
    logger.info("Fetching beauty trends...")
    analyzer = TrendAnalyzer()
    trends = analyzer.get_daily_beauty_trends(max_trends=5)
    
    # Apply post limit if specified
    if limit is not None:
        trends = trends[:limit]
        logger.info(f"Limited to {limit} posts")
    
    if not trends:
        logger.error("No trends found")
        return False
    
    # 2. Generate content
    logger.info(f"Found {len(trends)} trends, generating content...")
    generator = ContentGenerator()
    poster = PinterestPoster()
    
    # Override budget tracker if specified
    if dalle_budget is not None:
        generator.dalle_budget_tracker = dalle_budget
    
    successful_posts = 0
    for trend in trends:
        logger.info(f"Processing trend: {trend['query']}")
        content = generator.create_post(trend)
        
        if content:
            logger.info("LIVE TEST - Posting:")
            logger.info(f"Caption: {content['caption']}")
            logger.info(f"Image URL: {content['image_url']}")
            logger.info(f"Affiliate Link: {content['affiliate_link']}")
            
            success = poster.post(
                image_url=content['image_url'],
                caption=content['caption'],
                link=content['affiliate_link']
            )
            
            if success:
                logger.info(f"✅ Successfully posted about {trend['query']}")
                successful_posts += 1
            else:
                logger.error(f"❌ Failed to post about {trend['query']}")
        else:
            logger.error(f"Failed to generate content for {trend['query']}")
    
    # Process fallback queue
    processed = poster.process_fallback_queue()
    if processed > 0:
        logger.info(f"Processed {processed} items from fallback queue")
    
    logger.info(f"Completed with {successful_posts} successful posts out of {len(trends)} trends")
    
    if successful_posts > 0:
        return True
    else:
        return False

def main():
    """Parse arguments and run live test."""
    parser = argparse.ArgumentParser(description='Run a live test of the Pinterest Affiliate AI')
    parser.add_argument('--limit', type=int, help='Maximum number of posts to create')
    parser.add_argument('--budget', type=float, help='Maximum DALL-E budget to use in USD')
    args = parser.parse_args()
    
    logger.info("Running LIVE test (will actually post to Pinterest)")
    
    # Confirm with user
    confirm = input("Are you sure you want to run a LIVE test? This will post to Pinterest. (y/n): ")
    if confirm.lower() != 'y':
        logger.info("Live test cancelled")
        sys.exit(0)
    
    success = live_test(limit=args.limit, budget=args.budget)
    
    if success:
        logger.info("✅ Live test completed successfully")
        sys.exit(0)
    else:
        logger.error("❌ Live test failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 