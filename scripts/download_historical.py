import os
import logging
from typing import Dict, Any
import json
import requests
from datetime import datetime

logger = logging.getLogger(__name__)

def download_historical_data(config: Dict[str, Any]) -> Dict[str, str]:
    """Download historical maps and documents for the Xingu region."""
    logger.info("Downloading historical data...")
    
    # Create output directory if it doesn't exist
    output_dir = config['data_paths']['historical']
    os.makedirs(output_dir, exist_ok=True)
    
    downloaded_files = {}
    
    # Download FUNAI Indigenous Territories map
    try:
        funai_url = config['data_sources']['historical']['indigenous_maps']['url']
        funai_file = os.path.join(output_dir, f"funai_map_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
        
        response = requests.get(funai_url)
        response.raise_for_status()
        
        with open(funai_file, 'wb') as f:
            f.write(response.content)
            
        downloaded_files['funai_map'] = funai_file
        logger.info(f"FUNAI map downloaded successfully to {funai_file}")
        
    except Exception as e:
        logger.error(f"Error downloading FUNAI map: {e}")
    
    # Download Brazilian National Library documents
    try:
        bndigital_url = config['data_sources']['historical']['colonial_diaries']['url']
        bndigital_file = os.path.join(output_dir, f"colonial_diaries_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
        
        response = requests.get(bndigital_url)
        response.raise_for_status()
        
        with open(bndigital_file, 'wb') as f:
            f.write(response.content)
            
        downloaded_files['colonial_diaries'] = bndigital_file
        logger.info(f"Colonial diaries downloaded successfully to {bndigital_file}")
        
    except Exception as e:
        logger.error(f"Error downloading colonial diaries: {e}")
    
    return downloaded_files

if __name__ == "__main__":
    # Load configuration
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    # Download historical data
    download_historical_data(config) 