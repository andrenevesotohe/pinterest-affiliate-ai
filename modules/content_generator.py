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

    def create_post(self, trend: Dict) -> Optional[Dict]:
        """Create a complete post from a trend."""
        try:
            # Generate image first since it's more likely to fail
            image_url = self._generate_dalle_image(trend)
            if not image_url:
                return None

            # Generate caption
            caption = self._generate_gpt_caption(trend)
            if not caption:
                return None

            # Create affiliate link
            affiliate_link = self._get_affiliate_link(trend)

            return {
                'image_url': image_url,
                'caption': caption,
                'affiliate_link': affiliate_link
            }
        except Exception as e:
            logger.error(f"Error creating post: {str(e)}")
            return None

    def _generate_dalle_image(self, trend: Dict) -> Optional[str]:
        """Generate an image using DALL-E."""
        try:
            # Create a detailed prompt for DALL-E
            prompt = self._create_image_prompt(trend)

            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1
            )

            return response.data[0].url
        except Exception as e:
            logger.error(f"Error generating image: {str(e)}")
            return None

    def _create_image_prompt(self, trend: Dict) -> str:
        """Create a detailed prompt for DALL-E based on the trend."""
        category = trend['category']
        query = trend['query']

        prompts = {
            'skincare': f"A beautiful, minimalist product photography of {query}, with soft natural lighting, clean background, and a luxurious feel. The image should focus on skincare products and results, styled like a high-end beauty advertisement.",
            'haircare': f"A stunning hair transformation showcasing {query}, with perfect lighting and a professional salon aesthetic. The image should highlight healthy, shiny hair and professional hair care products.",
            'makeup': f"A professional beauty photograph demonstrating {query}, with perfect lighting and a modern, editorial style. The image should focus on flawless makeup application and high-end cosmetics."
        }

        return prompts.get(category, f"A professional beauty photograph showcasing {query}, with perfect lighting and a modern, minimalist style.")

    def _generate_gpt_caption(self, trend: Dict) -> Optional[str]:
        """Generate a caption using GPT-3.5."""
        try:
            system_prompt = """You are a professional beauty influencer creating engaging Pinterest captions.
Your captions should be:
1. Short and engaging (max 200 characters)
2. Include relevant emojis
3. Use trending beauty terminology
4. Include 2-3 relevant hashtags
5. Focus on benefits and results
6. Maintain a positive, encouraging tone"""

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Create a Pinterest caption for a post about {trend['query']} in the {trend['category']} category."}
                ],
                max_tokens=150,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating caption: {str(e)}")
            return None

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
