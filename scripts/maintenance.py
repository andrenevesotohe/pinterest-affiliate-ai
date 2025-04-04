#!/usr/bin/env python3
"""
Maintenance Script

This script handles daily maintenance tasks for the Pinterest Affiliate AI system,
including log rotation, budget reset, and fallback queue processing.
"""

import os
import sys
import json
import shutil
import argparse
import logging
import subprocess
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('maintenance.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def rotate_logs():
    """Rotate log files to prevent them from growing too large."""
    logger.info("Rotating log files...")
    
    log_files = [
        "content_generator.log",
        "poster.log",
        "budget_tracker.log",
        "affiliate_checks.log",
        "test_run.log",
        "maintenance.log"
    ]
    
    for log_file in log_files:
        if not os.path.exists(log_file):
            continue
        
        # Check if log file is older than 7 days
        file_time = datetime.fromtimestamp(os.path.getmtime(log_file))
        if datetime.now() - file_time > timedelta(days=7):
            # Create backup with date
            backup_file = f"{log_file}.{file_time.strftime('%Y%m%d')}.bak"
            shutil.move(log_file, backup_file)
            logger.info(f"Rotated {log_file} to {backup_file}")
            
            # Create new empty log file
            with open(log_file, 'w') as f:
                f.write("")
            logger.info(f"Created new {log_file}")

def reset_budget():
    """Reset the DALL-E budget tracker."""
    logger.info("Resetting DALL-E budget tracker...")
    
    try:
        if not os.path.exists("dalle_budget_state.json"):
            logger.warning("Budget state file not found")
            return False
        
        with open("dalle_budget_state.json", 'r') as f:
            state = json.load(f)
        
        # Check if reset is needed
        reset_time = datetime.fromisoformat(state.get("reset_time", ""))
        if datetime.now().date() == reset_time.date():
            logger.info("Budget already reset today")
            return True
        
        # Reset budget
        state["used_today"] = 0.0
        state["reset_time"] = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        
        with open("dalle_budget_state.json", 'w') as f:
            json.dump(state, f, indent=2)
        
        logger.info("Budget reset successfully")
        return True
    except Exception as e:
        logger.error(f"Error resetting budget: {e}")
        return False

def process_fallback_queue():
    """Process the fallback queue to retry failed posts."""
    logger.info("Processing fallback queue...")
    
    try:
        result = subprocess.run(
            ["python", "scripts/process_fallback.py"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"Error processing fallback queue: {result.stderr}")
            return False
        
        logger.info("Fallback queue processed successfully")
        logger.info(result.stdout)
        return True
    except Exception as e:
        logger.error(f"Error processing fallback queue: {e}")
        return False

def check_affiliate_links():
    """Check affiliate links for validity."""
    logger.info("Checking affiliate links...")
    
    try:
        result = subprocess.run(
            ["python", "scripts/check_affiliate_links.py", "--notify"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"Error checking affiliate links: {result.stderr}")
            return False
        
        logger.info("Affiliate links checked successfully")
        logger.info(result.stdout)
        return True
    except Exception as e:
        logger.error(f"Error checking affiliate links: {e}")
        return False

def run_daily_maintenance():
    """Run all daily maintenance tasks."""
    logger.info("Starting daily maintenance...")
    
    # Rotate logs
    rotate_logs()
    
    # Reset budget
    reset_budget()
    
    # Process fallback queue
    process_fallback_queue()
    
    # Check affiliate links
    check_affiliate_links()
    
    logger.info("Daily maintenance completed")
    return True

def main():
    parser = argparse.ArgumentParser(description='Run Pinterest Affiliate AI maintenance tasks')
    parser.add_argument('--daily', action='store_true', help='Run all daily maintenance tasks')
    parser.add_argument('--rotate-logs', action='store_true', help='Rotate log files')
    parser.add_argument('--reset-budget', action='store_true', help='Reset DALL-E budget')
    parser.add_argument('--process-queue', action='store_true', help='Process fallback queue')
    parser.add_argument('--check-links', action='store_true', help='Check affiliate links')
    args = parser.parse_args()
    
    if args.daily:
        success = run_daily_maintenance()
    else:
        success = True
        
        if args.rotate_logs:
            rotate_logs()
        
        if args.reset_budget:
            success = success and reset_budget()
        
        if args.process_queue:
            success = success and process_fallback_queue()
        
        if args.check_links:
            success = success and check_affiliate_links()
    
    if success:
        logger.info("Maintenance completed successfully")
        sys.exit(0)
    else:
        logger.error("Maintenance completed with errors")
        sys.exit(1)

if __name__ == "__main__":
    main() 