"""
Optimized GPT-4o-mini Text Generation Module with Cost Tracking
"""

import os
import logging
from typing import Dict, Optional
from openai import OpenAI
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('text_generator.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class OpenAICostManager:
    """Manages OpenAI API costs and usage tracking."""
    
    def __init__(self, monthly_budget: float = 10.0):
        """Initialize with monthly budget limit."""
        self.monthly_budget = monthly_budget
        self.used_cost = 0.0
        self.reset_time = datetime.now()
        self._check_reset()

    def can_make_call(self, tokens: int) -> bool:
        """Check if a call can be made within budget."""
        self._check_reset()
        estimated_cost = self._calculate_cost(tokens)
        return (self.used_cost + estimated_cost) <= self.monthly_budget

    def track_usage(self, tokens: int) -> None:
        """Track the cost of an API call."""
        self._check_reset()
        cost = self._calculate_cost(tokens)
        self.used_cost += cost

    def _calculate_cost(self, tokens: int) -> float:
        """Calculate cost for token usage."""
        # GPT-3.5 pricing: $0.002 per 1K tokens
        return (tokens / 1000.0) * 0.002

    def _check_reset(self) -> None:
        """Reset monthly usage if it's a new month."""
        now = datetime.now()
        if now.month != self.reset_time.month or now.year != self.reset_time.year:
            self.used_cost = 0.0
            self.reset_time = now

class GPT35TextGenerator:
    def __init__(self, cost_manager: OpenAICostManager):
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "test-key")
        self.client = OpenAI(api_key=self.openai_api_key)
        self.cost_manager = cost_manager
        self.template_overrides = {
            "benefits": """
            Create a compelling benefit statement for {product} in the {category} category.
            Focus on: {key_benefit}
            Style: {style}
            Keep it under 100 characters.
            """,
            "captions": """
            Write an engaging Pinterest caption for {product}.
            Include: {key_benefit}
            Style: {style}
            Add relevant emojis.
            Keep it under 200 characters.
            """,
            "hashtags": """
            Generate 5-7 relevant hashtags for {product} in {category}.
            Include: {key_benefit}
            Format: #Beauty #Skincare etc.
            """
        }

    def generate_text(self, template_type: str, context: Dict) -> Optional[str]:
        """Centralized GPT-3.5 text generation"""
        try:
            if not self.cost_manager.can_make_call(estimated_tokens=200):
                logger.warning("Budget exceeded, using fallback response")
                return self._fallback_response(template_type, context)

            prompt = self.template_overrides[template_type].format(**context)
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # Using GPT-3.5 Turbo
                messages=[
                    {"role": "system", "content": "You are a beauty and skincare expert."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.7
            )

            self.cost_manager.track_usage(response.usage.total_tokens)
            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"GPT-3.5 error: {str(e)}")
            return self._fallback_response(template_type, context)

    def _fallback_response(self, template_type: str, context: Dict) -> str:
        """Provide template-based fallback responses when API fails."""
        fallbacks = {
            "benefits": f"Transform your {context['category']} routine with {context['product']} for {context['key_benefit']} ✨",
            "captions": f"✨ Discover the secret to {context['key_benefit']} with {context['product']} 💫 #BeautyTips",
            "hashtags": f"#Beauty #Skincare #BeautyTips #{context['category'].capitalize()}"
        }
        return fallbacks.get(template_type, "Beauty transformation starts here ✨")