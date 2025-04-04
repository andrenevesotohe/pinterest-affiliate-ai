#!/usr/bin/env python3
"""
Diagnostic Script

This script helps diagnose issues with the Pinterest Affiliate AI system by
analyzing logs, checking API connectivity, and verifying configuration.
"""

import os
import sys
import json
import argparse
import logging
import requests
import subprocess
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def check_api_connectivity():
    """Check connectivity to external APIs."""
    logger.info("Checking API connectivity...")
    
    results = {
        "openai": False,
        "pinterest": False
    }
    
    # Check OpenAI API
    try:
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            logger.error("OpenAI API key not found")
        else:
            # Simple test request
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {openai_key}"},
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [{"role": "user", "content": "Hello"}],
                    "max_tokens": 5
                },
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("OpenAI API connection successful")
                results["openai"] = True
            else:
                logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
    except Exception as e:
        logger.error(f"OpenAI API connection error: {e}")
    
    # Check Pinterest API
    try:
        pinterest_token = os.getenv("PINTEREST_TOKEN")
        if not pinterest_token:
            logger.error("Pinterest API token not found")
        else:
            # Simple test request
            response = requests.get(
                "https://api.pinterest.com/v5/user_account",
                headers={"Authorization": f"Bearer {pinterest_token}"},
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("Pinterest API connection successful")
                results["pinterest"] = True
            else:
                logger.error(f"Pinterest API error: {response.status_code} - {response.text}")
    except Exception as e:
        logger.error(f"Pinterest API connection error: {e}")
    
    return results

def analyze_logs(log_file, hours=24):
    """Analyze log files for errors and patterns."""
    if not os.path.exists(log_file):
        logger.error(f"Log file not found: {log_file}")
        return None
    
    logger.info(f"Analyzing {log_file} for the last {hours} hours...")
    
    try:
        # Get log entries from the last X hours
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        with open(log_file, 'r') as f:
            lines = f.readlines()
        
        # Filter for recent entries
        recent_entries = []
        for line in lines:
            try:
                # Extract timestamp from log line
                timestamp_str = line.split(' - ')[0]
                timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
                
                if timestamp >= cutoff_time:
                    recent_entries.append(line)
            except:
                # Skip lines that don't match the expected format
                continue
        
        # Count log levels
        error_count = sum(1 for line in recent_entries if "ERROR" in line)
        warning_count = sum(1 for line in recent_entries if "WARNING" in line)
        info_count = sum(1 for line in recent_entries if "INFO" in line)
        
        # Extract error messages
        errors = [line for line in recent_entries if "ERROR" in line]
        
        return {
            "total_entries": len(recent_entries),
            "error_count": error_count,
            "warning_count": warning_count,
            "info_count": info_count,
            "errors": errors[:10]  # Limit to 10 errors
        }
    except Exception as e:
        logger.error(f"Error analyzing logs: {e}")
        return None

def check_budget_state():
    """Check the current state of the budget tracker."""
    logger.info("Checking budget state...")
    
    try:
        if not os.path.exists("dalle_budget_state.json"):
            logger.warning("Budget state file not found")
            return None
        
        with open("dalle_budget_state.json", 'r') as f:
            state = json.load(f)
        
        used_today = state.get("used_today", 0)
        daily_limit = state.get("daily_limit", 0.20)
        reset_time = state.get("reset_time", "")
        
        logger.info(f"Budget used today: ${used_today:.2f} of ${daily_limit:.2f}")
        logger.info(f"Reset time: {reset_time}")
        
        return {
            "used_today": used_today,
            "daily_limit": daily_limit,
            "reset_time": reset_time,
            "remaining": max(0, daily_limit - used_today)
        }
    except Exception as e:
        logger.error(f"Error checking budget state: {e}")
        return None

def check_fallback_queue():
    """Check the state of the fallback queue."""
    logger.info("Checking fallback queue...")
    
    try:
        if not os.path.exists("fallback_queue.json"):
            logger.info("Fallback queue is empty")
            return {"count": 0, "items": []}
        
        with open("fallback_queue.json", 'r') as f:
            queue = json.load(f)
        
        count = len(queue)
        logger.info(f"Fallback queue contains {count} items")
        
        # Get the most recent items
        recent_items = queue[-5:] if count > 5 else queue
        
        return {
            "count": count,
            "items": recent_items
        }
    except Exception as e:
        logger.error(f"Error checking fallback queue: {e}")
        return None

def run_last_run_diagnostic():
    """Run diagnostics on the last execution."""
    logger.info("Running diagnostics on last execution...")
    
    # Check API connectivity
    api_results = check_api_connectivity()
    
    # Analyze logs
    log_files = [
        "content_generator.log",
        "poster.log",
        "budget_tracker.log",
        "affiliate_checks.log"
    ]
    
    log_results = {}
    for log_file in log_files:
        result = analyze_logs(log_file, hours=24)
        if result:
            log_results[log_file] = result
    
    # Check budget state
    budget_state = check_budget_state()
    
    # Check fallback queue
    fallback_queue = check_fallback_queue()
    
    # Print summary
    logger.info("\n=== DIAGNOSTIC SUMMARY ===")
    
    logger.info("\nAPI Connectivity:")
    for api, status in api_results.items():
        logger.info(f"  {api}: {'✓' if status else '✗'}")
    
    logger.info("\nLog Analysis:")
    for log_file, result in log_results.items():
        logger.info(f"  {log_file}: {result['total_entries']} entries, {result['error_count']} errors")
    
    if budget_state:
        logger.info("\nBudget State:")
        logger.info(f"  Used: ${budget_state['used_today']:.2f} of ${budget_state['daily_limit']:.2f}")
        logger.info(f"  Remaining: ${budget_state['remaining']:.2f}")
    
    if fallback_queue:
        logger.info("\nFallback Queue:")
        logger.info(f"  Items: {fallback_queue['count']}")
    
    # Return overall status
    api_ok = all(api_results.values())
    logs_ok = all(result['error_count'] == 0 for result in log_results.values() if result)
    
    return api_ok and logs_ok

def main():
    parser = argparse.ArgumentParser(description='Diagnose Pinterest Affiliate AI issues')
    parser.add_argument('--last-run', action='store_true', help='Diagnose the last execution')
    parser.add_argument('--hours', type=int, default=24, help='Hours of logs to analyze')
    args = parser.parse_args()
    
    if args.last_run:
        success = run_last_run_diagnostic()
        if success:
            logger.info("\nDiagnostic completed successfully. No issues found.")
            sys.exit(0)
        else:
            logger.error("\nDiagnostic completed with issues. See above for details.")
            sys.exit(1)
    else:
        # Run individual checks
        check_api_connectivity()
        for log_file in ["content_generator.log", "poster.log", "budget_tracker.log", "affiliate_checks.log"]:
            analyze_logs(log_file, args.hours)
        check_budget_state()
        check_fallback_queue()

if __name__ == "__main__":
    main() 