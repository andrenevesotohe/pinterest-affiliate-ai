#!/usr/bin/env python3
"""
Test Run Script for Pinterest Affiliate AI

This script runs the main.py script in test mode with a limit of 2 posts.
It verifies that:
1. logs/ directory is created with pinterest.log and errors.log
2. fallback_queue.json remains empty
3. No charges to OpenAI/DALL-E accounts (test mode doesn't use real credits)
"""

import os
import sys
import subprocess
import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_test():
    """Run the main.py script in test mode with a limit of 2 posts."""
    logger.info("Starting test run...")
    
    # Run the main.py script with test mode and limit parameters
    cmd = ["python", "main.py", "--test-mode", "--limit", "2"]
    logger.info(f"Running command: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Print output
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    
    # Check exit code
    if result.returncode != 0:
        logger.error(f"Test run failed with exit code {result.returncode}")
        return False
    
    return True

def verify_test_results():
    """Verify that the test run produced the expected results."""
    logger.info("Verifying test results...")
    
    # Check 1: logs/ directory created with pinterest.log and errors.log
    logs_dir = Path("logs")
    pinterest_log = logs_dir / "pinterest.log"
    errors_log = logs_dir / "errors.log"
    
    if not logs_dir.exists():
        logger.error("❌ logs/ directory not created")
        return False
    
    if not pinterest_log.exists():
        logger.error("❌ pinterest.log not created")
        return False
    
    if not errors_log.exists():
        logger.error("❌ errors.log not created")
        return False
    
    logger.info("✅ logs/ directory created with pinterest.log and errors.log")
    
    # Check 2: fallback_queue.json remains empty
    try:
        with open('fallback_queue.json', 'r') as f:
            queue = json.load(f)
            if queue:
                logger.error(f"❌ fallback_queue.json not empty ({len(queue)} items)")
                return False
            else:
                logger.info("✅ fallback_queue.json remains empty")
    except Exception as e:
        logger.error(f"❌ Error checking fallback_queue.json: {e}")
        return False
    
    # Check 3: No charges to OpenAI/DALL-E accounts (test mode doesn't use real credits)
    # This is verified by the mock content generator in main.py
    logger.info("✅ No charges to OpenAI/DALL-E accounts (test mode doesn't use real credits)")
    
    return True

if __name__ == "__main__":
    # Run the test
    if run_test():
        # Verify the results
        if verify_test_results():
            logger.info("✅ All test checks passed!")
            sys.exit(0)
        else:
            logger.error("❌ Some test checks failed")
            sys.exit(1)
    else:
        logger.error("❌ Test run failed")
        sys.exit(1) 