#!/usr/bin/env python3
"""
Test Runner Script

This script provides functionality to run the Pinterest Affiliate AI in test mode
or live mode with budget constraints.
"""

import os
import sys
import argparse
import logging
import json
import time
from datetime import datetime
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_run.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def run_dry_run(limit: int = 3):
    """Run the system in test mode with a limited number of posts."""
    logger.info(f"Starting dry run with limit of {limit} posts")
    
    try:
        # Import here to avoid circular imports
        from modules.content_generator import ContentGenerator
        from modules.poster import PinterestPoster
        
        content_gen = ContentGenerator()
        poster = PinterestPoster()
        
        # Sample trends for testing
        test_trends = [
            {"query": "natural skincare routine", "category": "skincare"},
            {"query": "anti-aging serum", "category": "skincare"},
            {"query": "organic shampoo", "category": "haircare"},
            {"query": "vegan makeup", "category": "makeup"},
            {"query": "sustainable beauty", "category": "skincare"}
        ]
        
        successful_posts = 0
        failed_posts = 0
        
        for i, trend in enumerate(test_trends):
            if i >= limit:
                break
                
            logger.info(f"Processing test post {i+1}/{limit}: {trend['query']}")
            
            try:
                # Generate content
                post_data = content_gen.create_post(trend)
                
                if not post_data:
                    logger.warning(f"Failed to generate content for {trend['query']}")
                    failed_posts += 1
                    continue
                
                # In test mode, don't actually post to Pinterest
                logger.info(f"Test post generated successfully: {post_data['caption'][:50]}...")
                logger.info(f"Image URL: {post_data['image_url']}")
                logger.info(f"Affiliate link: {post_data['affiliate_link']}")
                
                successful_posts += 1
                
            except Exception as e:
                logger.error(f"Error processing test post: {e}")
                failed_posts += 1
        
        logger.info(f"Dry run completed: {successful_posts} successful, {failed_posts} failed")
        return successful_posts > 0
        
    except Exception as e:
        logger.error(f"Error in dry run: {e}")
        return False

def run_live_test(budget: float = 0.12):
    """Run the system in live mode with a budget constraint."""
    logger.info(f"Starting live test with budget of ${budget:.2f}")
    
    try:
        # Import here to avoid circular imports
        from modules.content_generator import ContentGenerator
        from modules.poster import PinterestPoster
        from modules.budget_tracker import DalleBudgetTracker
        
        # Override the daily budget for testing
        dalle_tracker = DalleBudgetTracker(daily_limit=budget)
        content_gen = ContentGenerator()
        content_gen.dalle_budget_tracker = dalle_tracker
        poster = PinterestPoster()
        
        # Sample trends for testing
        test_trends = [
            {"query": "natural skincare routine", "category": "skincare"},
            {"query": "anti-aging serum", "category": "skincare"},
            {"query": "organic shampoo", "category": "haircare"}
        ]
        
        successful_posts = 0
        failed_posts = 0
        
        for i, trend in enumerate(test_trends):
            logger.info(f"Processing live post {i+1}: {trend['query']}")
            
            try:
                # Check if we have enough budget
                if not dalle_tracker.can_generate():
                    logger.warning(f"Budget exceeded after {successful_posts} posts")
                    break
                
                # Generate content
                post_data = content_gen.create_post(trend)
                
                if not post_data:
                    logger.warning(f"Failed to generate content for {trend['query']}")
                    failed_posts += 1
                    continue
                
                # Post to Pinterest
                success = poster.post(
                    image_url=post_data['image_url'],
                    caption=post_data['caption'],
                    link=post_data['affiliate_link']
                )
                
                if success:
                    logger.info(f"Successfully posted to Pinterest: {post_data['caption'][:50]}...")
                    successful_posts += 1
                else:
                    logger.warning(f"Failed to post to Pinterest: {post_data['caption'][:50]}...")
                    failed_posts += 1
                
            except Exception as e:
                logger.error(f"Error processing live post: {e}")
                failed_posts += 1
        
        logger.info(f"Live test completed: {successful_posts} successful, {failed_posts} failed")
        logger.info(f"Budget used: ${dalle_tracker.used_today:.2f} of ${budget:.2f}")
        return successful_posts > 0
        
    except Exception as e:
        logger.error(f"Error in live test: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Run Pinterest Affiliate AI tests')
    parser.add_argument('--test-mode', action='store_true', help='Run in test mode (no actual posts)')
    parser.add_argument('--live', action='store_true', help='Run in live mode (actual posts)')
    parser.add_argument('--limit', type=int, default=3, help='Number of posts to generate in test mode')
    parser.add_argument('--budget', type=float, default=0.12, help='Budget in USD for live mode')
    args = parser.parse_args()
    
    if not (args.test_mode or args.live):
        parser.error("Either --test-mode or --live must be specified")
    
    if args.test_mode:
        success = run_dry_run(args.limit)
    elif args.live:
        success = run_live_test(args.budget)
    
    if success:
        logger.info("Test run completed successfully")
        sys.exit(0)
    else:
        logger.error("Test run failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 