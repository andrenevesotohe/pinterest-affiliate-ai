#!/usr/bin/env python3
"""
Test Post Script

This script runs a test post to verify that the Pinterest API is working correctly.
"""

import os
import sys
import logging
import argparse
from dotenv import load_dotenv
from modules.poster import PinterestPoster
from modules.budget_tracker import DalleBudgetTracker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def test_post(dry_run=True, budget=None):
    """Run a test post to verify Pinterest API connectivity."""
    load_dotenv()
    
    # Initialize budget tracker if budget is specified
    dalle_budget = None
    if budget is not None:
        dalle_budget = DalleBudgetTracker(daily_limit=budget)
        logger.info(f"Using DALL-E budget: ${budget:.2f}")
    
    # Initialize poster
    poster = PinterestPoster()
    
    # Test image URL (using a placeholder)
    test_image_url = "https://example.com/test_image.jpg"
    test_caption = "Test post from Pinterest Affiliate AI #test #automation"
    test_link = "https://example.com/test_link"
    
    logger.info("Running test post...")
    logger.info(f"Image URL: {test_image_url}")
    logger.info(f"Caption: {test_caption}")
    logger.info(f"Link: {test_link}")
    
    if dry_run:
        logger.info("DRY RUN - Would post to Pinterest")
        logger.info("Test post successful (simulated)")
        return True
    
    try:
        # Attempt to post
        success = poster.post(
            image_url=test_image_url,
            caption=test_caption,
            link=test_link
        )
        
        if success:
            logger.info("✅ Test post successful")
            return True
        else:
            logger.error("❌ Test post failed")
            return False
    except Exception as e:
        logger.error(f"❌ Error during test post: {e}")
        return False

def main():
    """Parse arguments and run test post."""
    parser = argparse.ArgumentParser(description='Run a test post to Pinterest')
    parser.add_argument('--live', action='store_true', help='Actually post to Pinterest (not a dry run)')
    parser.add_argument('--budget', type=float, help='Maximum DALL-E budget to use in USD')
    args = parser.parse_args()
    
    dry_run = not args.live
    if dry_run:
        logger.info("Running in DRY RUN mode (no actual posts will be made)")
    else:
        logger.info("Running in LIVE mode (will actually post to Pinterest)")
    
    success = test_post(dry_run=dry_run, budget=args.budget)
    
    if success:
        logger.info("✅ Test completed successfully")
        sys.exit(0)
    else:
        logger.error("❌ Test failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 