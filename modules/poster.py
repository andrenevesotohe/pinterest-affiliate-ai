"""
Pinterest Affiliate AI Poster Module

This module handles the automated creation and posting of beauty content to Pinterest,
with integrated Amazon affiliate links.
"""

import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv
import openai
import requests
from PIL import Image
import logging
from ratelimit import limits, sleep_and_retry
from typing import Dict, Optional, List
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import re

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
    """Class to handle Pinterest posting operations."""
    
    def __init__(self, token: str = None, board_id: str = None):
        """Initialize with Pinterest API credentials."""
        self.token = token or os.getenv("PINTEREST_TOKEN", "test_token_123")
        self.board_id = board_id or os.getenv("PINTEREST_BOARD_ID", "test_board_456")
        self.base_url = "https://api.pinterest.com/v5/pins"
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.fallback_queue_file = "fallback_queue.json"

    def _validate_inputs(self, image_url: str, caption: str, link: str) -> None:
        """Validate input parameters."""
        if not image_url or not image_url.startswith('http'):
            raise ValueError("Invalid image URL format")
        if not caption or len(caption.strip()) == 0:
            raise ValueError("Caption cannot be empty")
        if not link or not link.startswith('http'):
            raise ValueError("Invalid link format")

    @sleep_and_retry
    @limits(calls=1000, period=3600)  # 1000 calls per hour
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((requests.exceptions.RequestException, ValueError))
    )
    def post(self, image_url: str, caption: str, link: str) -> bool:
        """Post a pin to Pinterest with retries and rate limiting."""
        try:
            self._validate_inputs(image_url, caption, link)
            
            data = {
                "title": "Beauty Find 🧴",
                "description": f"{caption}\n\n#AffiliateLink",
                "board_id": self.board_id,
                "media": {
                    "source_type": "image_url",
                    "url": image_url
                },
                "link": link
            }

            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=data,
                timeout=10
            )

            if response.status_code == 429:
                logger.warning("Rate limit hit, retrying...")
                raise requests.exceptions.RequestException("Rate limit exceeded")
            
            if response.status_code == 201:
                logger.info(f"Successfully posted to Pinterest: {link}")
                return True
                
            error_msg = response.json().get("message", "Unknown error")
            logger.error(f"Failed to post to Pinterest: {response.status_code} - {error_msg}")
            
            if response.status_code >= 500:
                raise requests.exceptions.RequestException(f"Server error: {error_msg}")
            
            # Add to fallback queue for non-500 errors
            self._add_to_fallback_queue({
                "image_url": image_url,
                "caption": caption,
                "link": link,
                "error": f"{response.status_code} - {error_msg}"
            })
            
            return False

        except Exception as e:
            logger.error(f"Error posting to Pinterest: {str(e)}")
            # Add to fallback queue for any exception
            self._add_to_fallback_queue({
                "image_url": image_url,
                "caption": caption,
                "link": link,
                "error": str(e)
            })
            raise

    def _add_to_fallback_queue(self, post_data: Dict) -> None:
        """Add failed post to fallback queue."""
        try:
            queue = []
            if os.path.exists(self.fallback_queue_file):
                with open(self.fallback_queue_file, 'r') as f:
                    try:
                        queue = json.load(f)
                    except json.JSONDecodeError:
                        logger.warning("Invalid JSON in fallback queue, starting fresh")
                        queue = []
            
            post_data['attempted_at'] = datetime.now().isoformat()
            queue.append(post_data)
            
            with open(self.fallback_queue_file, 'w') as f:
                json.dump(queue, f, indent=2)
                
            logger.info(f"Added post to fallback queue: {post_data.get('link', 'unknown link')}")
                
        except Exception as e:
            logger.error(f"Error adding to fallback queue: {e}")

    def process_fallback_queue(self, limit: Optional[int] = None) -> List[Dict]:
        """Process posts in the fallback queue."""
        if not os.path.exists(self.fallback_queue_file):
            return []

        try:
            with open(self.fallback_queue_file, 'r') as f:
                try:
                    queue = json.load(f)
                except json.JSONDecodeError:
                    logger.error("Invalid JSON in fallback queue")
                    return []

            successful_posts = []
            remaining_posts = []
            processed_count = 0

            for post in queue:
                if limit and processed_count >= limit:
                    remaining_posts.extend(queue[processed_count:])
                    break

                try:
                    success = self.post(
                        image_url=post['image_url'],
                        caption=post['caption'],
                        link=post['link']
                    )

                    if success:
                        successful_posts.append(post)
                        logger.info(f"Successfully processed fallback post: {post.get('link', 'unknown link')}")
                    else:
                        remaining_posts.append(post)
                        logger.warning(f"Failed to process fallback post: {post.get('link', 'unknown link')}")

                except Exception as e:
                    logger.error(f"Error processing post: {e}")
                    remaining_posts.append(post)

                processed_count += 1

            # Update queue with remaining posts
            with open(self.fallback_queue_file, 'w') as f:
                json.dump(remaining_posts, f, indent=2)

            logger.info(f"Processed {len(successful_posts)} fallback posts, {len(remaining_posts)} remaining")
            return successful_posts

        except Exception as e:
            logger.error(f"Error processing fallback queue: {e}")
            return []

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
                    'Authorization': f'Bearer {self.token}'
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
