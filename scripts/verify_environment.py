#!/usr/bin/env python3
"""
Environment Verification Script

This script checks that all required environment variables and dependencies
are properly configured before running tests or production code.
"""

import os
import sys
import logging
import importlib
import subprocess
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Required environment variables
REQUIRED_ENV_VARS = [
    "OPENAI_API_KEY",
    "PINTEREST_TOKEN",
    "PINTEREST_BOARD_ID",
    "AMAZON_ASSOCIATE_TAG"
]

# Required Python packages
REQUIRED_PACKAGES = [
    "openai",
    "requests",
    "python-dotenv",
    "pillow",
    "tenacity",
    "ratelimit",
    "pytest",
    "pytest-cov"
]

def check_environment_variables():
    """Check that all required environment variables are set."""
    load_dotenv()
    
    missing_vars = []
    for var in REQUIRED_ENV_VARS:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    logger.info("All required environment variables are set")
    return True

def check_python_packages():
    """Check that all required Python packages are installed."""
    missing_packages = []
    
    for package in REQUIRED_PACKAGES:
        try:
            importlib.import_module(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"Missing required Python packages: {', '.join(missing_packages)}")
        logger.info("Install missing packages with: pip install " + " ".join(missing_packages))
        return False
    
    logger.info("All required Python packages are installed")
    return True

def run_pytest():
    """Run pytest with coverage."""
    try:
        logger.info("Running pytest with coverage...")
        result = subprocess.run(
            ["python", "-m", "pytest", "tests/", "-v", "--cov=modules", "--cov-report=html"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logger.error("Tests failed:")
            logger.error(result.stdout)
            logger.error(result.stderr)
            return False
        
        logger.info("All tests passed successfully")
        logger.info(result.stdout)
        return True
    except Exception as e:
        logger.error(f"Error running tests: {e}")
        return False

def check_affiliate_links():
    """Run affiliate link validation."""
    try:
        logger.info("Checking affiliate links...")
        result = subprocess.run(
            ["python", "scripts/check_affiliate_links.py", "--full-scan"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logger.error("Affiliate link check failed:")
            logger.error(result.stdout)
            logger.error(result.stderr)
            return False
        
        logger.info("Affiliate link check passed successfully")
        logger.info(result.stdout)
        return True
    except Exception as e:
        logger.error(f"Error checking affiliate links: {e}")
        return False

def main():
    """Run all verification checks."""
    logger.info("Starting environment verification...")
    
    env_vars_ok = check_environment_variables()
    packages_ok = check_python_packages()
    
    if not (env_vars_ok and packages_ok):
        logger.error("Environment verification failed. Please fix the issues above.")
        sys.exit(1)
    
    # Run tests
    tests_ok = run_pytest()
    if not tests_ok:
        logger.error("Tests failed. Please fix the issues above.")
        sys.exit(1)
    
    # Check affiliate links
    links_ok = check_affiliate_links()
    if not links_ok:
        logger.error("Affiliate link check failed. Please fix the issues above.")
        sys.exit(1)
    
    logger.info("✅ All verification checks passed successfully!")

if __name__ == "__main__":
    main() 