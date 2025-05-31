import os
import json
import getpass
import logging
import ee
from sentinelsat import SentinelAPI

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def authenticate_services():
    """Authenticate with Sentinel Hub and Google Earth Engine."""
    try:
        # Load configuration
        with open('config.json', 'r') as f:
            config = json.load(f)
            
        # Sentinel Hub authentication
        logger.info("Setting up Sentinel Hub authentication...")
        sentinel_username = input("Enter your Sentinel Hub username: ")
        sentinel_password = getpass.getpass("Enter your Sentinel Hub password: ")
        
        # Test Sentinel Hub connection
        api = SentinelAPI(sentinel_username, sentinel_password, 'https://scihub.copernicus.eu/dhus')
        api.query(area='POLYGON((0 0, 0 1, 1 1, 1 0, 0 0))', limit=1)
        logger.info("Sentinel Hub authentication successful!")
        
        # Update config with credentials
        config['api_credentials']['sentinel_hub']['username'] = sentinel_username
        config['api_credentials']['sentinel_hub']['password'] = sentinel_password
        
        # Google Earth Engine authentication
        logger.info("Setting up Google Earth Engine authentication...")
        ee.Authenticate()
        ee.Initialize()
        logger.info("Google Earth Engine authentication successful!")
        
        # Save updated configuration
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=4)
            
        logger.info("Authentication completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        return False

def main():
    """Main function to run authentication process."""
    if authenticate_services():
        logger.info("All services authenticated successfully!")
    else:
        logger.error("Authentication process failed!")

if __name__ == "__main__":
    main() 