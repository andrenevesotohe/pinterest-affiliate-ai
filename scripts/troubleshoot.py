#!/usr/bin/env python3
"""
Troubleshooting Script

This script runs all the troubleshooting steps to resolve issues and prepare for testing.
"""

import os
import sys
import logging
import argparse
import subprocess
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def run_command(command, description):
    """Run a command and log the output."""
    logger.info(f"Running: {description}")
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            logger.info(f"✅ {description} successful")
            logger.info(result.stdout)
            return True
        else:
            logger.error(f"❌ {description} failed")
            logger.error(result.stdout)
            logger.error(result.stderr)
            return False
    except Exception as e:
        logger.error(f"❌ Error running {description}: {e}")
        return False

def verify_pinterest_token():
    """Verify the Pinterest API token."""
    return run_command(
        "python scripts/verify_pinterest_token.py",
        "Verifying Pinterest API token"
    )

def refresh_pinterest_token():
    """Refresh the Pinterest API token."""
    return run_command(
        "python scripts/refresh_token.py",
        "Refreshing Pinterest API token"
    )

def clear_fallback_queue():
    """Clear the fallback queue."""
    return run_command(
        "python scripts/clear_queue.py",
        "Clearing fallback queue"
    )

def reset_budget():
    """Reset the budget tracker."""
    return run_command(
        "python scripts/reset_budget.py",
        "Resetting budget tracker"
    )

def verify_environment():
    """Verify the environment."""
    return run_command(
        "python scripts/verify_environment.py",
        "Verifying environment"
    )

def run_dry_run_test(limit=None, budget=None):
    """Run a dry run test."""
    command = "python scripts/dry_run.py"
    if limit is not None:
        command += f" --limit {limit}"
    if budget is not None:
        command += f" --budget {budget}"
    
    return run_command(
        command,
        "Running dry run test"
    )

def run_live_test(limit=None, budget=None):
    """Run a live test."""
    command = "python scripts/live_test.py"
    if limit is not None:
        command += f" --limit {limit}"
    if budget is not None:
        command += f" --budget {budget}"
    
    return run_command(
        command,
        "Running live test"
    )

def troubleshoot(limit=None, budget=None, live=False):
    """Run all troubleshooting steps."""
    logger.info("Starting troubleshooting process...")
    
    # 1. Verify Pinterest token
    if not verify_pinterest_token():
        logger.info("Pinterest token verification failed, attempting to refresh...")
        if not refresh_pinterest_token():
            logger.error("Failed to refresh Pinterest token. Please check your token manually.")
            return False
    
    # 2. Clear fallback queue
    clear_fallback_queue()
    
    # 3. Reset budget
    reset_budget()
    
    # 4. Verify environment
    if not verify_environment():
        logger.error("Environment verification failed. Please fix the issues above.")
        return False
    
    # 5. Run dry run test
    if not run_dry_run_test(limit=limit, budget=budget):
        logger.error("Dry run test failed. Please fix the issues above.")
        return False
    
    # 6. Run live test if requested
    if live:
        if not run_live_test(limit=limit, budget=budget):
            logger.error("Live test failed. Please fix the issues above.")
            return False
    
    logger.info("✅ Troubleshooting completed successfully!")
    return True

def main():
    """Parse arguments and run troubleshooting."""
    parser = argparse.ArgumentParser(description='Run troubleshooting steps')
    parser.add_argument('--limit', type=int, help='Maximum number of posts to create')
    parser.add_argument('--budget', type=float, help='Maximum DALL-E budget to use in USD')
    parser.add_argument('--live', action='store_true', help='Run live test after dry run')
    args = parser.parse_args()
    
    success = troubleshoot(
        limit=args.limit,
        budget=args.budget,
        live=args.live
    )
    
    if success:
        logger.info("✅ All troubleshooting steps completed successfully")
        sys.exit(0)
    else:
        logger.error("❌ Troubleshooting failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 