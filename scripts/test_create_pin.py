#!/usr/bin/env python3
import os
import logging
from dotenv import load_dotenv
from create_pin import PinterestPinCreator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_create_pin():
    """Test creating a Pinterest pin"""
    try:
        # Create sample pin data
        test_data = {
            "title": "Test Beauty Product",
            "description": "This is a test pin for a beauty product. #beauty #skincare #test",
            "link": "https://www.amazon.com/dp/B07ZPKN6YR?tag=" + os.getenv("AMAZON_ASSOCIATE_TAG", ""),
            "image_url": "https://images.pexels.com/photos/3785147/pexels-photo-3785147.jpeg",
            "alt_text": "Beauty product on pink background"
        }
        
        # Create the pin
        creator = PinterestPinCreator()
        result = creator.create_pin(**test_data)
        
        # Log success
        logger.info("Test pin created successfully!")
        logger.info(f"Pin ID: {result.get('id')}")
        logger.info(f"Pin URL: {result.get('url', 'URL not available')}")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to create test pin: {str(e)}")
        return False

if __name__ == "__main__":
    load_dotenv()
    success = test_create_pin()
    exit(0 if success else 1) 