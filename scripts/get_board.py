#!/usr/bin/env python3
import os
import json
import logging
import argparse
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pinterest_boards.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PinterestBoardReader:
    """Class to handle Pinterest board operations"""
    
    def __init__(self):
        load_dotenv()
        self.token = os.getenv("PINTEREST_TOKEN")
        self.board_id = os.getenv("PINTEREST_BOARD_ID")
        
        if not self.token:
            raise ValueError("Pinterest token is required")
        
        self.api_base_url = "https://api.pinterest.com/v5"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def get_board(self, board_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get board information from Pinterest
        
        Args:
            board_id: Optional board ID. If not provided, uses the one from .env
            
        Returns:
            Dict containing the board information
        """
        try:
            # Use provided board_id or default from .env
            board_id = board_id or self.board_id
            if not board_id:
                raise ValueError("Board ID is required")

            logger.info(f"Fetching board information for: {board_id}")
            
            # Make the API request
            response = requests.get(
                f"{self.api_base_url}/boards/{board_id}",
                headers=self.headers,
                timeout=30
            )
            
            # Check response
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"Successfully retrieved board: {result.get('name', 'Unknown board')}")
            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get board: {str(e)}")
            if hasattr(e.response, 'text'):
                logger.error(f"API Response: {e.response.text}")
            raise

    def get_board_sections(self, board_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get sections of a board
        
        Args:
            board_id: Optional board ID. If not provided, uses the one from .env
            
        Returns:
            Dict containing the board sections
        """
        try:
            # Use provided board_id or default from .env
            board_id = board_id or self.board_id
            if not board_id:
                raise ValueError("Board ID is required")

            logger.info(f"Fetching sections for board: {board_id}")
            
            # Make the API request
            response = requests.get(
                f"{self.api_base_url}/boards/{board_id}/sections",
                headers=self.headers,
                timeout=30
            )
            
            # Check response
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"Successfully retrieved {len(result.get('items', []))} board sections")
            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get board sections: {str(e)}")
            if hasattr(e.response, 'text'):
                logger.error(f"API Response: {e.response.text}")
            raise

def main(args):
    """Main function to get board information"""
    try:
        reader = PinterestBoardReader()
        
        # Get board information
        if args.sections:
            result = reader.get_board_sections(args.board_id)
            print("\nBoard Sections:")
            for section in result.get('items', []):
                print(f"- {section.get('name')} (ID: {section.get('id')})")
        else:
            result = reader.get_board(args.board_id)
            print("\nBoard Information:")
            print(f"Name: {result.get('name')}")
            print(f"Description: {result.get('description', 'No description')}")
            print(f"Privacy: {result.get('privacy')}")
            print(f"Pin Count: {result.get('pin_count', 0)}")
            print(f"Follower Count: {result.get('follower_count', 0)}")
            print(f"Owner: {result.get('owner', {}).get('username', 'Unknown')}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Get Pinterest board information')
    parser.add_argument('--board-id', help='Board ID (username/board-name/). If not provided, uses PINTEREST_BOARD_ID from .env')
    parser.add_argument('--sections', action='store_true', help='Get board sections instead of board details')
    parser.add_argument('--json', action='store_true', help='Output in JSON format')
    
    args = parser.parse_args()
    exit(main(args)) 