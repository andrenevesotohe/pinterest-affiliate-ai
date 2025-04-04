"""
Content Generator for Pinterest posts

This module handles the generation of content including:
- DALL-E image generation
- GPT-3.5 caption generation
- Amazon affiliate link creation
"""

import os
import logging
from openai import OpenAI
from typing import Dict, Optional
from .text_generator import GPT35TextGenerator, OpenAICostManager
from .dalle_generator import DalleBeautyGenerator
from .budget_tracker import DalleBudgetTracker, BudgetExceededError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('content_generator.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class ContentGenerator:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.amazon_tag = os.getenv("AMAZON_ASSOCIATE_TAG")

        if not self.openai_api_key or not self.amazon_tag:
            raise ValueError("Missing required environment variables")

        self.client = OpenAI(api_key=self.openai_api_key)
        self.cost_manager = OpenAICostManager()
        self.text_generator = GPT35TextGenerator(self.cost_manager)
        self.dalle_generator = DalleBeautyGenerator()
        self.dalle_budget_tracker = DalleBudgetTracker()

    def create_post(self, trend: Dict) -> Optional[Dict]:
        """Create a complete post from a trend."""
        try:
            # Create product info for DALL-E
            product_info = {
                'name': trend['query'],
                'category': trend['category']
            }

            # Check DALL-E budget before generating image
            if not self.dalle_budget_tracker.can_generate():
                logger.warning(f"DALL-E budget exceeded, cannot generate image for {trend['query']}")
                return None

            # Generate image first since it's more likely to fail
            image_url = self._generate_dalle_image(product_info, trend)
            if not image_url:
                return None

            # Record DALL-E usage after successful generation
            self.dalle_budget_tracker.record_usage()

            # Generate caption using optimized GPT-3.5 generator
            caption_context = {
                'product': trend['query'],
                'trend': trend['query'],
                'key_benefit': self._get_key_benefit(trend),
                'style': 'conversational',
                'category': trend['category']
            }
            caption = self.text_generator.generate_text("captions", caption_context)
            if not caption:
                return None

            # Create affiliate link
            affiliate_link = self._get_affiliate_link(trend)

            return {
                'image_url': image_url,
                'caption': caption,
                'affiliate_link': affiliate_link
            }
        except BudgetExceededError as e:
            logger.error(f"Budget exceeded: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error creating post: {str(e)}")
            return None

    def _generate_dalle_image(self, product: Dict[str, str], trend: Dict[str, str]) -> str:
        """Generate an image using DALL-E based on product and trend."""
        # For testing purposes, return a fixed URL if using test key
        if self.openai_api_key == "test-key":
            return "https://test-image-url.com"

        try:
            # Check if we can afford to generate an image
            if not self.dalle_budget_tracker.can_generate():
                raise ValueError("Daily DALL-E budget exceeded")

            prompt = f"Create a beautiful product photo of {product['name']} for {trend['category']} enthusiasts. Make it look professional and appealing for Pinterest."
            
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1
            )

            # Record the usage in budget tracker
            self.dalle_budget_tracker.record_usage()
            
            return response.data[0].url
        except Exception as e:
            logger.error(f"Error generating image: {e}")
            raise

    def _get_key_benefit(self, trend: Dict) -> str:
        """Extract key benefit from trend for caption generation."""
        benefits = {
            'skincare': 'radiant, healthy skin',
            'haircare': 'stronger, shinier hair',
            'makeup': 'flawless, natural-looking beauty'
        }
        return benefits.get(trend['category'], 'amazing results')

    def _get_affiliate_link(self, trend: Dict) -> str:
        """Create an optimized Amazon affiliate link."""
        # Create search terms based on category
        category_terms = {
            'skincare': 'skincare+beauty',
            'haircare': 'hair+care+products',
            'makeup': 'makeup+cosmetics'
        }

        base_term = trend['query'].replace(' ', '+')
        category_term = category_terms.get(trend['category'], 'beauty')
        search_term = f"{base_term}+{category_term}"

        return f"https://www.amazon.com/s?k={search_term}&tag={self.amazon_tag}"
