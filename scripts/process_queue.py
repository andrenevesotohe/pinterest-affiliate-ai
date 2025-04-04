#!/usr/bin/env python3
import json
import os
import argparse
from datetime import datetime
import logging
from modules.poster import PinterestPoster

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('queue_processor.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def process_fallback_queue(dry_run=False):
    """Processes failed posts from the fallback queue"""
    QUEUE_FILE = "fallback_queue.json"
    MAX_ATTEMPTS = 3
    
    if not os.path.exists(QUEUE_FILE):
        logger.info("No fallback queue file found")
        return 0
    
    logger.info("Processing fallback queue...")
    
    successful = []
    failed = []
    
    with open(QUEUE_FILE, "r+") as f:
        try:
            posts = [json.loads(line) for line in f]
        except json.JSONDecodeError:
            logger.error("Invalid JSON in fallback queue file")
            return 0
            
        f.seek(0)
        f.truncate(0)  # Clear the file for rewriting
        
        for post in posts:
            attempts = post.get("attempts", 0) + 1
            if attempts > MAX_ATTEMPTS:
                logger.warning(f"Post exceeded maximum attempts ({MAX_ATTEMPTS}): {post.get('caption', 'Unknown post')}")
                failed.append(post)
                continue
                
            try:
                if dry_run:
                    logger.info(f"DRY RUN: Would process post: {post.get('caption', 'Unknown post')}")
                    successful.append(post)
                else:
                    poster = PinterestPoster()
                    success = poster.post(
                        post["image_url"],
                        post["caption"],
                        post["link"]
                    )
                    
                    if success:
                        logger.info(f"Successfully processed post: {post.get('caption', 'Unknown post')}")
                        successful.append(post)
                    else:
                        logger.warning(f"Failed to process post: {post.get('caption', 'Unknown post')}")
                        post["attempts"] = attempts
                        post["last_attempt"] = datetime.now().isoformat()
                        f.write(json.dumps(post) + "\n")
                    
            except Exception as e:
                logger.error(f"Error processing post: {str(e)}")
                post["attempts"] = attempts
                post["last_attempt"] = datetime.now().isoformat()
                f.write(json.dumps(post) + "\n")
    
    logger.info(f"Processed queue: {len(successful)} succeeded, {len(failed)} failed")
    return len(successful)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process fallback queue')
    parser.add_argument('--dry-run', action='store_true', help='Run in dry run mode (no actual posts)')
    args = parser.parse_args()
    
    process_fallback_queue(dry_run=args.dry_run) 