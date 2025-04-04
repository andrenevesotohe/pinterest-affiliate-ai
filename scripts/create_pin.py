#!/usr/bin/env python3
import os
import json
import logging
import argparse
import requests
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pinterest_pins.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PinterestPinCreator:
    """Class to handle Pinterest pin creation"""
    
    def __init__(self):
        load_dotenv()
        self.token = os.getenv("PINTEREST_TOKEN")
        self.board_id = os.getenv("PINTEREST_BOARD_ID")
        
        if not self.token or not self.board_id:
            raise ValueError("Pinterest token and board ID are required")
        
        self.api_url = "https://api.pinterest.com/v5/pins"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def create_pin(self, 
                  title: str,
                  description: str,
                  link: str,
                  image_url: str,
                  alt_text: Optional[str] = None,
                  board_section_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new pin on Pinterest
        
        Args:
            title: Pin title (max 100 characters)
            description: Pin description (max 500 characters)
            link: Destination link for the pin
            image_url: URL of the image to pin
            alt_text: Alternative text for the image
            board_section_id: Optional board section ID
            
        Returns:
            Dict containing the API response
        """
        try:
            # Prepare the pin data
            pin_data = {
                "title": title[:100],  # Enforce character limits
                "description": description[:500],
                "link": link,
                "board_id": self.board_id,
                "media_source": {
                    "source_type": "image_url",
                    "url": image_url
                }
            }
            
            # Add optional parameters if provided
            if alt_text:
                pin_data["media_source"]["alt_text"] = alt_text[:500]
            if board_section_id:
                pin_data["board_section_id"] = board_section_id

            logger.info(f"Creating pin: {title}")
            logger.debug(f"Pin data: {json.dumps(pin_data, indent=2)}")

            # Make the API request
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=pin_data,
                timeout=30
            )
            
            # Check response
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"Successfully created pin with ID: {result.get('id')}")
            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create pin: {str(e)}")
            if hasattr(e.response, 'text'):
                logger.error(f"API Response: {e.response.text}")
            raise

def main(args):
    """Main function to create a Pinterest pin"""
    try:
        creator = PinterestPinCreator()
        
        # Create the pin
        result = creator.create_pin(
            title=args.title,
            description=args.description,
            link=args.link,
            image_url=args.image_url,
            alt_text=args.alt_text
        )
        
        # Print the result
        print(json.dumps(result, indent=2))
        return 0
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create a Pinterest pin')
    parser.add_argument('--title', required=True, help='Pin title (max 100 chars)')
    parser.add_argument('--description', required=True, help='Pin description (max 500 chars)')
    parser.add_argument('--link', required=True, help='Destination link for the pin')
    parser.add_argument('--image-url', required=True, help='URL of the image to pin')
    parser.add_argument('--alt-text', help='Alternative text for the image')
    
    args = parser.parse_args()
    exit(main(args)) 