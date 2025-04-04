#!/usr/bin/env python3
import os
import sys
import logging
import requests
import argparse
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def test_pinterest_api():
    """Test connectivity to Pinterest API"""
    load_dotenv()
    
    pinterest_token = os.getenv("PINTEREST_TOKEN")
    if not pinterest_token:
        logger.error("❌ Pinterest token not found in .env file")
        return False
    
    logger.info("🔄 Testing Pinterest API connection...")
    
    try:
        response = requests.get(
            "https://api.pinterest.com/v5/user_account",
            headers={"Authorization": f"Bearer {pinterest_token}"},
            timeout=10
        )
        
        if response.status_code == 200:
            logger.info("✅ Pinterest API connection successful")
            logger.info(f"User account: {response.json()}")
            return True
        else:
            logger.error(f"❌ Pinterest API connection failed: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
    except Exception as e:
        logger.error(f"❌ Pinterest API connection error: {str(e)}")
        return False

def test_openai_api():
    """Test connectivity to OpenAI API"""
    load_dotenv()
    
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        logger.error("❌ OpenAI API key not found in .env file")
        return False
    
    logger.info("🔄 Testing OpenAI API connection...")
    
    try:
        # Using the newer OpenAI API client
        from openai import OpenAI
        client = OpenAI(api_key=openai_key)
        
        # List models using the new API
        models = client.models.list()
        logger.info("✅ OpenAI API connection successful")
        logger.info(f"Available models: {len(models.data)}")
        return True
    except Exception as e:
        logger.error(f"❌ OpenAI API connection error: {str(e)}")
        return False

def test_amazon_affiliate():
    """Test Amazon affiliate link generation"""
    load_dotenv()
    
    associate_tag = os.getenv("AMAZON_ASSOCIATE_TAG")
    if not associate_tag:
        logger.error("❌ Amazon associate tag not found in .env file")
        return False
    
    logger.info("🔄 Testing Amazon affiliate link generation...")
    
    try:
        # Test with a sample product
        product_id = "B07ZPKN6YR"  # Example product ID
        affiliate_link = f"https://www.amazon.com/dp/{product_id}?tag={associate_tag}"
        
        logger.info(f"✅ Amazon affiliate link generated: {affiliate_link}")
        return True
    except Exception as e:
        logger.error(f"❌ Amazon affiliate link generation error: {str(e)}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test API connectivity')
    parser.add_argument('--pinterest', action='store_true', help='Test Pinterest API')
    parser.add_argument('--openai', action='store_true', help='Test OpenAI API')
    parser.add_argument('--amazon', action='store_true', help='Test Amazon affiliate')
    parser.add_argument('--all', action='store_true', help='Test all APIs')
    args = parser.parse_args()
    
    # If no specific API is selected, test all
    if not any([args.pinterest, args.openai, args.amazon, args.all]):
        args.all = True
    
    success = True
    
    if args.pinterest or args.all:
        if not test_pinterest_api():
            success = False
    
    if args.openai or args.all:
        if not test_openai_api():
            success = False
    
    if args.amazon or args.all:
        if not test_amazon_affiliate():
            success = False
    
    if success:
        logger.info("✅ All API tests passed")
        sys.exit(0)
    else:
        logger.error("❌ Some API tests failed")
        sys.exit(1) 