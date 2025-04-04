#!/usr/bin/env python3
import os
import re
import time
import requests
from typing import Dict, Optional, Tuple
from urllib.parse import urlparse, parse_qs
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('affiliate_checks.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class AffiliateLinkValidator:
    def __init__(self):
        self.required_tags = {
            "amazon": os.getenv("AMAZON_ASSOCIATE_TAG"),
            "cj": os.getenv("CJ_AFFILIATE_ID"),
            "shareasale": os.getenv("SHAREASALE_AFFID")
        }

        # Network-specific patterns
        self.validation_rules = {
            "amazon": {
                "domain": r"amazon\.(com|co\.uk|de|fr|ca|jp)",
                "param": "tag",
                "pattern": r"^[a-zA-Z0-9\-]+-\d{2}$"
            },
            "cj": {
                "domain": r"(\w+\.)?cj\.com",
                "param": "pid",
                "pattern": r"^\d+$"
            },
            "shareasale": {
                "domain": r"shareasale\.com",
                "param": "aff",
                "pattern": r"^\d+$"
            }
        }

    def validate_link(self, url: str) -> Tuple[bool, str]:
        """Validates an affiliate link and returns (is_valid, network)"""
        if not url:
            return False, "empty"

        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()

            # Check each network's rules
            for network, rules in self.validation_rules.items():
                if re.search(rules["domain"], domain):
                    params = parse_qs(parsed.query)
                    tag_param = rules["param"]

                    # Validate tag exists and matches pattern
                    if tag_param in params:
                        tag_value = params[tag_param][0]
                        if re.fullmatch(rules["pattern"], tag_value):
                            if self._verify_network_tag(network, tag_value):
                                return True, network
                    return False, network

            return False, "unknown"
        except Exception as e:
            logger.error(f"Validation error for {url}: {str(e)}")
            return False, "error"

    def _verify_network_tag(self, network: str, tag: str) -> bool:
        """Verifies tag matches our registered ID"""
        our_tag = self.required_tags.get(network)
        if not our_tag:
            logger.warning(f"No {network} tag configured")
            return False
        return tag == our_tag

    def check_batch(self, links: Dict[str, str]) -> Dict[str, Tuple[bool, str]]:
        """Validates multiple links with rate limiting"""
        results = {}
        for name, url in links.items():
            results[name] = self.validate_link(url)
            time.sleep(0.5)  # Rate limiting
        return results

def main():
    validator = AffiliateLinkValidator()

    # Example links - replace with your actual links
    test_links = {
        "amazon_good": "https://www.amazon.com/dp/B08N5KWB9H/?tag=yourtag-20",
        "amazon_bad": "https://www.amazon.com/dp/B08N5KWB9H/?tag=competitor-21",
        "cj_good": "https://www.anrdoezrs.net/click?pid=123456&offerid=123",
        "shareasale_bad": "https://www.shareasale.com/r.cfm?aff=999"
    }

    results = validator.check_batch(test_links)

    # Print results
    print("\nAffiliate Link Validation Results:")
    for name, (is_valid, network) in results.items():
        status = "[OK]" if is_valid else "[X]"
        print(f"{status} {name.ljust(15)} {network.ljust(10)} {test_links[name]}")

if __name__ == "__main__":
    main()
