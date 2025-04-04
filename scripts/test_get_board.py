#!/usr/bin/env python3
import os
import json
import logging
from dotenv import load_dotenv
from get_board import PinterestBoardReader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_get_board():
    """Test getting Pinterest board information"""
    try:
        reader = PinterestBoardReader()
        
        # Get board information
        board_info = reader.get_board()
        logger.info("\nBoard Information:")
        logger.info(f"Name: {board_info.get('name')}")
        logger.info(f"Description: {board_info.get('description', 'No description')}")
        logger.info(f"Privacy: {board_info.get('privacy')}")
        logger.info(f"Pin Count: {board_info.get('pin_count', 0)}")
        logger.info(f"Follower Count: {board_info.get('follower_count', 0)}")
        logger.info(f"Owner: {board_info.get('owner', {}).get('username', 'Unknown')}")
        
        # Get board sections
        sections = reader.get_board_sections()
        logger.info("\nBoard Sections:")
        for section in sections.get('items', []):
            logger.info(f"- {section.get('name')} (ID: {section.get('id')})")
        
        # Save results to file for reference
        with open('board_info.json', 'w') as f:
            json.dump({
                'board': board_info,
                'sections': sections
            }, f, indent=2)
            logger.info("\nSaved board information to board_info.json")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to get board information: {str(e)}")
        return False

if __name__ == "__main__":
    load_dotenv()
    success = test_get_board()
    exit(0 if success else 1) 