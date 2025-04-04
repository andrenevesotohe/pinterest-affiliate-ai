#!/usr/bin/env python3
import os
import re
import time
import requests
import argparse
from typing import Dict, Optional, Tuple, List
from urllib.parse import urlparse, parse_qs
import logging
from dotenv import load_dotenv
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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

def send_notification(invalid_links: List[Dict]) -> None:
    """Send email notification about invalid affiliate links."""
    if not invalid_links:
        return
        
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    recipient_email = os.getenv("NOTIFICATION_EMAIL")
    
    if not all([smtp_username, smtp_password, recipient_email]):
        logger.warning("Missing email configuration, cannot send notification")
        return
    
    try:
        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = recipient_email
        msg['Subject'] = "Affiliate Link Validation Alert"
        
        body = "The following affiliate links failed validation:\n\n"
        for link in invalid_links:
            body += f"- {link['name']}: {link['url']} (Network: {link['network']})\n"
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(msg)
        server.quit()
        
        logger.info(f"Notification sent to {recipient_email}")
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")

def load_links_from_file(file_path: str) -> Dict[str, str]:
    """Load affiliate links from a JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading links from {file_path}: {e}")
        return {}

def main():
    parser = argparse.ArgumentParser(description='Validate affiliate links')
    parser.add_argument('--notify', action='store_true', help='Send notification for invalid links')
    parser.add_argument('--full-scan', action='store_true', help='Perform a full scan of all links')
    parser.add_argument('--file', type=str, help='JSON file containing links to validate')
    args = parser.parse_args()

    validator = AffiliateLinkValidator()

    # Load links from file or use example links
    if args.file:
        links = load_links_from_file(args.file)
    else:
        # Example links - replace with your actual links
        links = {
            "amazon_good": "https://www.amazon.com/dp/B08N5KWB9H/?tag=yourtag-20",
            "amazon_bad": "https://www.amazon.com/dp/B08N5KWB9H/?tag=competitor-21",
            "cj_good": "https://www.anrdoezrs.net/click?pid=123456&offerid=123",
            "shareasale_bad": "https://www.shareasale.com/r.cfm?aff=999"
        }

    results = validator.check_batch(links)

    # Print results
    print("\nAffiliate Link Validation Results:")
    invalid_links = []
    for name, (is_valid, network) in results.items():
        status = "[OK]" if is_valid else "[X]"
        print(f"{status} {name.ljust(15)} {network.ljust(10)} {links[name]}")
        
        if not is_valid:
            invalid_links.append({
                "name": name,
                "url": links[name],
                "network": network
            })

    # Send notification if requested and there are invalid links
    if args.notify and invalid_links:
        send_notification(invalid_links)
        
    # Log summary
    logger.info(f"Validation complete: {len(links) - len(invalid_links)} valid, {len(invalid_links)} invalid")

if __name__ == "__main__":
    main()
