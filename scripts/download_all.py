import os
import logging
from typing import Dict, Any
import json
from download_lidar import download_lidar_data
from download_satellite import download_satellite_data
from download_historical import download_historical_data

logger = logging.getLogger(__name__)

def download_all_data(config: Dict[str, Any]) -> Dict[str, str]:
    """Download all required data for archaeological research."""
    logger.info("Starting data download process...")
    
    downloaded_files = {}
    
    # Download LIDAR data
    try:
        lidar_file = download_lidar_data(config)
        if lidar_file:
            downloaded_files['lidar'] = lidar_file
    except Exception as e:
        logger.error(f"Error downloading LIDAR data: {e}")
    
    # Download satellite imagery
    try:
        satellite_file = download_satellite_data(config)
        if satellite_file:
            downloaded_files['satellite'] = satellite_file
    except Exception as e:
        logger.error(f"Error downloading satellite imagery: {e}")
    
    # Download historical data
    try:
        historical_files = download_historical_data(config)
        downloaded_files.update(historical_files)
    except Exception as e:
        logger.error(f"Error downloading historical data: {e}")
    
    logger.info("Data download process completed")
    return downloaded_files

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Load configuration
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    # Download all data
    downloaded_files = download_all_data(config)
    
    # Print summary
    print("\nDownload Summary:")
    for data_type, file_path in downloaded_files.items():
        print(f"{data_type}: {file_path}") 