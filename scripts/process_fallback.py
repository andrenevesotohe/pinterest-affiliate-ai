#!/usr/bin/env python3
"""
Process Fallback Queue Script

This script processes posts that failed to be published to Pinterest
and were added to the fallback queue.
"""

import os
import sys
import logging
import argparse
from dotenv import load_dotenv
from modules.poster import PinterestPoster
import json

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('fallback_processor.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def process_fallback_queue(limit=None):
    """Process posts in the fallback queue.
    
    Args:
        limit: Maximum number of posts to process (None for all)
    """
    try:
        poster = PinterestPoster()
        
        # Check if fallback queue exists
        if not os.path.exists("fallback_queue.json"):
            logger.info("No fallback queue found")
            return 0
        
        # Read queue
        with open("fallback_queue.json", "r") as f:
            queue = json.load(f)
        
        if not queue:
            logger.info("Fallback queue is empty")
            return 0
        
        # Apply limit if specified
        if limit is not None:
            queue = queue[:limit]
        
        logger.info(f"Processing {len(queue)} items from fallback queue")
        
        # Process items
        processed = 0
        remaining = []
        
        for item in queue:
            try:
                success = poster.post(
                    image_url=item["image_url"],
                    caption=item["caption"],
                    link=item["link"]
                )
                if success:
                    processed += 1
                    logger.info(f"Successfully processed item: {item['caption'][:30]}...")
                else:
                    remaining.append(item)
            except Exception as e:
                logger.error(f"Failed to process item: {str(e)}")
                remaining.append(item)
        
        # Update queue with remaining items
        with open("fallback_queue.json", "w") as f:
            json.dump(remaining, f, indent=2)
        
        logger.info(f"Processed {processed} items, {len(remaining)} remaining")
        return processed
    
    except Exception as e:
        logger.error(f"Error processing fallback queue: {str(e)}")
        return 0

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Process Pinterest fallback queue')
    parser.add_argument('--limit', type=int, help='Maximum number of items to process')
    args = parser.parse_args()
    
    try:
        processed = process_fallback_queue(limit=args.limit)
        logger.info(f"Successfully processed {processed} items from fallback queue")
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 