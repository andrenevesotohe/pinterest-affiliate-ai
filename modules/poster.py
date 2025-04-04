"""
Pinterest Affiliate AI Poster Module

This module handles the automated creation and posting of beauty content to Pinterest,
with integrated Amazon affiliate links.
"""

import os
from dotenv import load_dotenv
import openai
import requests
from PIL import Image
import logging
from ratelimit import limits, sleep_and_retry
from typing import Dict, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('poster.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class PinterestPoster:
    def __init__(self):
        """Initialize the Pinterest poster with API keys and tokens."""
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.pinterest_token = os.getenv('PINTEREST_ACCESS_TOKEN')
        self.amazon_tag = os.getenv('AMAZON_ASSOCIATE_TAG')
        self.board_id = os.getenv('PINTEREST_BOARD_ID')

        if not all([self.openai_api_key, self.pinterest_token, self.amazon_tag, self.board_id]):
            raise ValueError("Missing required environment variables")

        openai.api_key = self.openai_api_key

    def generate_content(self, topic):
        """Generate beauty content using OpenAI."""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a beauty content creator."},
                    {"role": "user", "content": f"Create a Pinterest post about {topic}"}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            raise

    @sleep_and_retry
    @limits(calls=5, period=60)  # Pinterest API rate limit
    def post(self, image_url: str, caption: str, link: str) -> bool:
        """Post content to Pinterest."""
        try:
            url = "https://api.pinterest.com/v5/pins"
            headers = {"Authorization": f"Bearer {self.pinterest_token}"}
            data = {
                "board_id": self.board_id,
                "media_source": {
                    "source_type": "image_url",
                    "url": image_url
                },
                "title": caption[:100],  # Pinterest title limit
                "description": caption,
                "link": link
            }

            response = requests.post(url, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            logger.info("Successfully posted to Pinterest")
            return True

        except Exception as e:
            logger.error(f"Error posting to Pinterest: {str(e)}")
            return False

    def create_pinterest_post(self, content, image_path):
        """Create a post on Pinterest with local image file."""
        try:
            # Pinterest API endpoint
            url = "https://api.pinterest.com/v5/pins"

            # Prepare the image
            with open(image_path, 'rb') as image_file:
                files = {'image': image_file}

                data = {
                    'title': content[:100],  # Pinterest title limit
                    'description': content,
                    'link': f"https://amazon.com/?tag={self.amazon_tag}"
                }

                headers = {
                    'Authorization': f'Bearer {self.pinterest_token}'
                }

                response = requests.post(url, headers=headers, data=data, files=files)
                response.raise_for_status()

                logger.info("Successfully created Pinterest post")
                return response.json()
        except Exception as e:
            logger.error(f"Error creating Pinterest post: {e}")
            raise

def main():
    """Main function to run the poster."""
    try:
        poster = PinterestPoster()
        content = poster.generate_content("natural skincare routine")
        # Example usage of the new post method
        success = poster.post(
            image_url="https://example.com/image.jpg",
            caption=content,
            link=f"https://amazon.com/?tag={poster.amazon_tag}"
        )
        if success:
            logger.info("Post created successfully")
        else:
            logger.error("Failed to create post")
    except Exception as e:
        logger.error(f"Error in main: {e}")
        raise

if __name__ == "__main__":
    main()
