import os
import requests
from dotenv import load_dotenv

def verify_pinterest_token():
    """Verify the Pinterest API token and check connectivity."""
    load_dotenv()
    
    token = os.getenv("PINTEREST_TOKEN")
    if not token:
        print("❌ Pinterest token not found in .env file")
        return False
    
    print(f"✅ Token exists: {bool(token)}")
    
    # Test API connectivity
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(
            "https://api.pinterest.com/v5/user_account",
            headers=headers
        )
        
        if response.status_code == 200:
            print(f"✅ API Status: {response.status_code}")
            print("✅ Pinterest API connection successful")
            return True
        elif response.status_code == 401:
            print(f"❌ API Status: {response.status_code}")
            print("❌ Token is invalid or expired. Please refresh your token.")
            return False
        else:
            print(f"❌ API Status: {response.status_code}")
            print(f"❌ Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error connecting to Pinterest API: {e}")
        return False

if __name__ == "__main__":
    verify_pinterest_token() 