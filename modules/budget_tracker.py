import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('budget_tracker.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class BudgetExceededError(Exception):
    """Exception raised when budget is exceeded."""
    pass

class DalleBudgetTracker:
    def __init__(self, daily_limit: float = 0.20):
        """Initialize the DALL-E budget tracker.
        
        Args:
            daily_limit: Maximum daily budget in USD (default: $0.20)
        """
        self.daily_limit = daily_limit
        self.reset_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        self.used_today = 0.0
        self.cost_per_image = 0.04  # $0.04 per DALL-E image
        self._load_state()

    def can_generate(self, estimated_cost: Optional[float] = None) -> bool:
        """Check if generation is allowed within budget.
        
        Args:
            estimated_cost: Optional override for estimated cost (default: self.cost_per_image)
            
        Returns:
            bool: True if generation is allowed, False otherwise
        """
        self._check_reset()
        cost = estimated_cost if estimated_cost is not None else self.cost_per_image
        can_generate = (self.used_today + cost) <= self.daily_limit
        
        if not can_generate:
            logger.warning(f"Budget exceeded: ${self.used_today:.2f} used of ${self.daily_limit:.2f} daily limit")
        
        return can_generate

    def record_usage(self, cost: Optional[float] = None):
        """Deduct from budget.
        
        Args:
            cost: Optional override for cost (default: self.cost_per_image)
            
        Raises:
            BudgetExceededError: If recording would exceed daily limit
        """
        self._check_reset()
        cost = cost if cost is not None else self.cost_per_image
        
        if not self.can_generate(cost):
            raise BudgetExceededError(f"Daily DALL-E budget of ${self.daily_limit:.2f} would be exceeded")
        
        self.used_today += cost
        logger.info(f"Recorded DALL-E usage: ${cost:.2f}, total today: ${self.used_today:.2f}")
        self._save_state()
        
        if self.used_today >= self.daily_limit:
            logger.warning("Daily DALL-E budget reached")

    def get_remaining_budget(self) -> float:
        """Get remaining budget for today.
        
        Returns:
            float: Remaining budget in USD
        """
        self._check_reset()
        return max(0, self.daily_limit - self.used_today)

    def _check_reset(self):
        """Reset budget at midnight."""
        now = datetime.now()
        if now > self.reset_time + timedelta(days=1):
            logger.info(f"Resetting budget from ${self.used_today:.2f} to $0.00")
            self.used_today = 0
            self.reset_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
            self._save_state()
    
    def _save_state(self) -> None:
        """Save current state to file."""
        state = {
            "used_today": float(self.used_today),
            "reset_time": self.reset_time.isoformat(),
            "daily_limit": float(self.daily_limit)
        }
        with open("dalle_budget_state.json", "w") as f:
            json.dump(state, f)
    
    def _load_state(self) -> None:
        """Load state from file if it exists and is from today."""
        if not os.path.exists("dalle_budget_state.json"):
            return

        try:
            with open("dalle_budget_state.json", "r") as f:
                state = json.load(f)
                saved_time = datetime.fromisoformat(state["reset_time"])
                
                # Only load state if it's from today
                if saved_time.date() == datetime.now().date():
                    self.used_today = float(state["used_today"])
                    self.daily_limit = float(state.get("daily_limit", self.daily_limit))
                    self.reset_time = saved_time
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"Error loading state: {e}")
            return 