#!/usr/bin/env python3
import requests
import os
from datetime import datetime, timedelta
import logging
from dotenv import set_key
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('token_refresh.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def refresh_pinterest_token(test_mode=False):
    """Automatically refreshes Pinterest API token"""
    try:
        current_token = os.getenv("PINTEREST_TOKEN")
        if not current_token:
            raise ValueError("No current token found in .env")
        
        if test_mode:
            logger.info("TEST MODE: Simulating token refresh")
            # In test mode, we'll just simulate a successful refresh
            new_token = current_token
        else:
            # Make the actual API call to refresh the token
            response = requests.post(
                "https://api.pinterest.com/v5/oauth/token",
                headers={"Authorization": f"Bearer {current_token}"},
                params={"grant_type": "refresh_token"},
                timeout=10
            )
            response.raise_for_status()
            
            new_token = response.json().get("access_token")
            if not new_token:
                raise ValueError("No token in refresh response")
        
        # Update .env file
        env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
        set_key(env_path, "PINTEREST_TOKEN", new_token)
        
        logger.info("Successfully refreshed Pinterest token")
        return True
        
    except Exception as e:
        logger.error(f"Token refresh failed: {str(e)}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Refresh Pinterest API token')
    parser.add_argument('--test', action='store_true', help='Run in test mode (no actual API calls)')
    args = parser.parse_args()
    
    refresh_pinterest_token(test_mode=args.test) 