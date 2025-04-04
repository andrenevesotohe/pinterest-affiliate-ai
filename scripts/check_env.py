#!/usr/bin/env python3
from dotenv import load_dotenv
import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

REQUIRED_KEYS = [
    "OPENAI_API_KEY",
    "PINTEREST_TOKEN",
    "AMAZON_ASSOCIATE_TAG",
    "PINTEREST_BOARD_ID"
]

def validate_env():
    """Validate that all required environment variables are present"""
    load_dotenv()
    
    missing = [k for k in REQUIRED_KEYS if not os.getenv(k)]
    if missing:
        logger.error(f"Missing environment variables: {', '.join(missing)}")
        return False
    
    logger.info("✅ All required environment variables are present")
    return True

def test_api_connectivity():
    """Test connectivity to external APIs"""
    import requests
    
    # Test Pinterest API
    try:
        pinterest_token = os.getenv("PINTEREST_TOKEN")
        response = requests.get(
            "https://api.pinterest.com/v5/user_account",
            headers={"Authorization": f"Bearer {pinterest_token}"},
            timeout=10
        )
        if response.status_code == 200:
            logger.info("✅ Pinterest API connection successful")
        else:
            logger.error(f"❌ Pinterest API connection failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logger.error(f"❌ Pinterest API connection error: {str(e)}")
        return False
    
    # Test OpenAI API
    try:
        import openai
        openai.api_key = os.getenv("OPENAI_API_KEY")
        models = openai.Model.list()
        logger.info("✅ OpenAI API connection successful")
    except Exception as e:
        logger.error(f"❌ OpenAI API connection error: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    if not validate_env():
        sys.exit(1)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test-connectivity":
        if not test_api_connectivity():
            sys.exit(1)
    
    logger.info("Environment validation complete") 