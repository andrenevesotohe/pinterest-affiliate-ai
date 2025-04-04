#!/usr/bin/env python3
import os
import argparse
import logging
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
from modules.budget_tracker import DalleBudgetTracker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('budget_alerts.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def send_alert(subject: str, body: str, test_mode=False):
    """Sends email alerts"""
    load_dotenv()
    
    # Check if email configuration is available
    if not all([os.getenv("ALERT_EMAIL_FROM"), os.getenv("ALERT_EMAIL_TO"), 
                os.getenv("SMTP_SERVER"), os.getenv("SMTP_USER"), os.getenv("SMTP_PASSWORD")]):
        logger.error("Email configuration incomplete. Please check your .env file.")
        return False
    
    try:
        msg = EmailMessage()
        msg.set_content(body)
        msg['Subject'] = subject
        msg['From'] = os.getenv("ALERT_EMAIL_FROM")
        msg['To'] = os.getenv("ALERT_EMAIL_TO")
        
        if test_mode:
            logger.info(f"TEST MODE: Would send email with subject: {subject}")
            logger.info(f"Email body: {body}")
            return True
        
        with smtplib.SMTP(os.getenv("SMTP_SERVER"), 587) as server:
            server.starttls()
            server.login(os.getenv("SMTP_USER"), os.getenv("SMTP_PASSWORD"))
            server.send_message(msg)
            
        logger.info(f"Alert email sent: {subject}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send alert email: {str(e)}")
        return False

def check_budgets(test_mode=False):
    """Checks all budget limits"""
    logger.info("Checking budget limits...")
    
    # Check DALL-E budget
    dalle = DalleBudgetTracker()
    remaining = dalle.daily_limit - dalle.used_today
    
    logger.info(f"DALL-E budget: ${remaining:.2f} remaining of ${dalle.daily_limit:.2f} daily limit")
    
    # Alert thresholds
    if remaining < 0.05:  # $0.05 left
        alert_sent = send_alert(
            "DALL-E Budget Alert",
            f"Only ${remaining:.2f} remaining in your DALL-E budget today!",
            test_mode
        )
        if alert_sent:
            logger.info("DALL-E budget alert sent")
        else:
            logger.warning("Failed to send DALL-E budget alert")
    
    # Add GPT-3.5 checks here if needed
    # This would be implemented when GPT-3.5 budget tracking is added
    
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Check budget limits and send alerts')
    parser.add_argument('--test', action='store_true', help='Run in test mode (no actual emails)')
    args = parser.parse_args()
    
    check_budgets(test_mode=args.test) 