"""
Scheduler for Pinterest Affiliate Automation AI

This script reads the scheduler.json configuration and runs the tasks
according to the defined schedule.
"""

import json
import os
import time
import logging
import subprocess
import schedule
from datetime import datetime
import pytz
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_tasks():
    """Load tasks from scheduler.json."""
    try:
        with open('scheduler.json', 'r') as f:
            config = json.load(f)
        return config.get('tasks', [])
    except Exception as e:
        logger.error(f"Error loading tasks: {e}")
        return []

def run_task(task):
    """Run a scheduled task."""
    logger.info(f"Running task: {task['name']}")
    try:
        # Set environment variables if needed
        env = os.environ.copy()

        # Run the command
        process = subprocess.Popen(
            task['command'],
            shell=True,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Get output
        stdout, stderr = process.communicate()

        if process.returncode == 0:
            logger.info(f"Task {task['name']} completed successfully")
            if stdout:
                logger.info(f"Output: {stdout.decode('utf-8')}")
        else:
            logger.error(f"Task {task['name']} failed with code {process.returncode}")
            if stderr:
                logger.error(f"Error: {stderr.decode('utf-8')}")

    except Exception as e:
        logger.error(f"Error running task {task['name']}: {e}")

def setup_schedule():
    """Set up the schedule for all tasks."""
    tasks = load_tasks()

    for task in tasks:
        if not task.get('enabled', True):
            logger.info(f"Task {task['name']} is disabled, skipping")
            continue

        schedule_time = task.get('schedule')
        if not schedule_time:
            logger.warning(f"Task {task['name']} has no schedule, skipping")
            continue

        # Parse cron-style schedule
        if schedule_time == "0 9 * * *":  # Daily at 9AM
            schedule.every().day.at("09:00").do(run_task, task)
            logger.info(f"Scheduled task {task['name']} to run daily at 9AM UTC")
        else:
            logger.warning(f"Unsupported schedule format: {schedule_time}")

    logger.info("Schedule setup complete")

def main():
    """Main function to run the scheduler."""
    logger.info("Starting Pinterest Affiliate Automation AI scheduler")
    setup_schedule()

    # Run the scheduler loop
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main()
