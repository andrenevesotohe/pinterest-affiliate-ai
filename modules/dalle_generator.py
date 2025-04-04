"""
Enhanced DALL-E Prompt Generation for Beauty Sub-niches
"""

from typing import Dict, Any
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('dalle_generator.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class DalleBeautyGenerator:
    def __init__(self):
        self.subniche_templates = {
            # Skincare Subcategories
            "anti-aging": {
                "color": "soft gold and ivory",
                "props": "crystal roller, fresh roses",
                "lighting": "warm sunrise glow",
                "style": "luxury spa aesthetic"
            },
            "acne": {
                "color": "clinical blue and white",
                "props": "aloe vera plant, bamboo towel",
                "lighting": "bright natural light",
                "style": "clean medical look"
            },
            "glow": {
                "color": "peach and champagne",
                "props": "citrus slices, dewdrops",
                "lighting": "soft diffused light",
                "style": "ethereal glow"
            },
            
            # Haircare Subcategories
            "curly": {
                "color": "vibrant jewel tones",
                "props": "wide-tooth comb, silk scarf",
                "lighting": "studio lighting",
                "style": "textured close-up"
            },
            "repair": {
                "color": "deep emerald and gold",
                "props": "olive branches, ceramic vase",
                "lighting": "dramatic side light",
                "style": "salon professional"
            },
            
            # Makeup Subcategories
            "clean": {
                "color": "earth tones",
                "props": "recycled packaging, plants",
                "lighting": "natural daylight",
                "style": "minimalist flat lay"
            },
            "luxury": {
                "color": "black and rose gold",
                "props": "marble surface, pearls",
                "lighting": "moody ambiance",
                "style": "high-end editorial"
            }
        }
        
    def generate_niche_prompt(self, product: Dict[str, Any], trend: str) -> str:
        """Creates ultra-specific DALL-E prompts for beauty sub-niches"""
        subniche = self._identify_subniche(product, trend)
        template = self.subniche_templates.get(subniche, self._default_template())
        
        prompt = f"""
        Create a Pinterest-optimized vertical image (2:3 ratio) with these SPECIFIC requirements:
        
        1. PRODUCT DISPLAY:
        - {product['name']} as the focal point
        - Photorealistic detail showing texture
        - {template['lighting']} lighting
        - {template['style']} style
        
        2. STYLING:
        - Color palette: {template['color']}
        - Props: {template['props']}
        - {self._get_angle(subniche)} camera angle
        - Negative space for text overlay
        
        3. CONTEXT:
        - Trending on Pinterest: #{trend.replace(' ','')}
        - Target audience: {self._get_audience(subniche)}
        - Avoid AI artifacts, make it look authentic
        
        4. TEXT ELEMENTS:
        - Only show "{trend}" in subtle script font
        - Positioned at {self._get_text_position(subniche)}
        """
        
        logger.info(f"Generated DALL-E prompt for subniche: {subniche}")
        return prompt.strip()

    def _identify_subniche(self, product: Dict[str, Any], trend: str) -> str:
        """Detects the specific beauty subcategory"""
        keywords = {
            'anti-aging': ['wrinkle', 'aging', 'mature', 'anti-aging'],
            'acne': ['acne', 'blemish', 'breakout', 'clear skin'],
            'glow': ['glow', 'radiance', 'illuminating', 'glass skin'],
            'curly': ['curl', 'coily', 'frizz', 'natural hair'],
            'repair': ['repair', 'damage', 'split end', 'treatment'],
            'clean': ['clean', 'organic', 'non-toxic', 'natural'],
            'luxury': ['luxury', 'premium', 'high-end', 'gold']
        }
        
        search_text = f"{product.get('name', '')} {trend}".lower()
        for niche, terms in keywords.items():
            if any(term in search_text for term in terms):
                return niche
        return "glow"  # Default fallback

    def _get_angle(self, subniche: str) -> str:
        angles = {
            "anti-aging": "slightly elevated 3/4 view",
            "acne": "straight-on clinical angle",
            "glow": "soft focus close-up",
            "curly": "dynamic diagonal composition",
            "repair": "hero product shot from above",
            "clean": "flat lay with props",
            "luxury": "dramatic Dutch angle"
        }
        return angles.get(subniche, "slightly elevated 3/4 view")

    def _get_audience(self, subniche: str) -> str:
        audiences = {
            "anti-aging": "women 35+ seeking premium skincare",
            "acne": "teens and young adults with breakout concerns",
            "glow": "all ages wanting radiant skin",
            "curly": "natural hair enthusiasts",
            "repair": "those with chemically treated hair",
            "clean": "eco-conscious millennials",
            "luxury": "affluent beauty collectors"
        }
        return audiences.get(subniche, "beauty enthusiasts")

    def _get_text_position(self, subniche: str) -> str:
        positions = {
            "anti-aging": "bottom right in 10% opacity",
            "acne": "top left in clean sans-serif",
            "glow": "centered with light glow effect",
            "curly": "wrapped around product",
            "luxury": "discreet gold foil embossing"
        }
        return positions.get(subniche, "bottom center")

    def _default_template(self) -> Dict[str, str]:
        return {
            "color": "pastel tones",
            "props": "fresh flowers, linen texture",
            "lighting": "soft diffused light",
            "style": "lifestyle aesthetic"
        } 