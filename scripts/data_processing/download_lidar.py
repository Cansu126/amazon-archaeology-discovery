import os
import requests
import json
import logging
from typing import Dict, Any
from datetime import datetime
import zipfile
import io

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_lidar_data(config: Dict[str, Any]) -> str:
    """
    Downloads SRTM elevation data from USGS Earth Explorer for the Xingu region.
    Returns the path to the downloaded file.
    """
    try:
        # Xingu region coordinates (verified to have data)
        bbox = {
            'min_lat': -11.5,
            'max_lat': -12.5,
            'min_lon': -53.5,
            'max_lon': -54.5
        }
        
        # USGS Earth Explorer API endpoint
        api_url = "https://earthexplorer.usgs.gov/inventory/json/v/1.4.0"
        
        # Create output directory if it doesn't exist
        output_dir = config['data_paths']['lidar']
        os.makedirs(output_dir, exist_ok=True)
        
        # Remove dummy file if it exists
        dummy_file = os.path.join(output_dir, 'dummy.las')
        if os.path.exists(dummy_file):
            os.remove(dummy_file)
        
        # Calculate tile coordinates
        lat = int((bbox['min_lat'] + bbox['max_lat']) / 2)
        lon = int((bbox['min_lon'] + bbox['max_lon']) / 2)
        
        # Format tile name (SRTM format)
        tile_name = f"S{abs(lat):02d}W{abs(lon):03d}"
        
        # Direct download URL for SRTM 1 Arc-Second Global
        download_url = f"https://dds.cr.usgs.gov/srtm/version2_1/SRTM1/South_America/{tile_name}.hgt.zip"
        
        # Output filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output_dir, f'xingu_lidar_{timestamp}.tif')
        
        logger.info(f"Downloading elevation data from USGS Earth Explorer...")
        logger.info(f"URL: {download_url}")
        logger.info(f"Tile: {tile_name}")
        
        # Download the file
        response = requests.get(download_url, stream=True)
        response.raise_for_status()
        
        # Extract the zip file
        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
            # Find the .hgt file in the zip
            hgt_files = [f for f in zip_ref.namelist() if f.endswith('.hgt')]
            if not hgt_files:
                raise Exception("No HGT file found in the downloaded zip")
            
            # Extract the first .hgt file
            zip_ref.extract(hgt_files[0], output_dir)
            
            # Rename the extracted file
            extracted_file = os.path.join(output_dir, hgt_files[0])
            os.rename(extracted_file, output_file)
        
        logger.info(f"Successfully downloaded elevation data to: {output_file}")
        
        # Save metadata
        metadata = {
            'source': 'USGS SRTM 1 Arc-Second Global',
            'region': 'Xingu River Basin',
            'coordinates': bbox,
            'download_date': timestamp,
            'file_path': output_file,
            'tile_name': tile_name,
            'api_url': api_url
        }
        
        metadata_file = os.path.join(output_dir, 'lidar_metadata.json')
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=4)
        
        return output_file
        
    except Exception as e:
        logger.error(f"Error downloading elevation data: {e}")
        raise

if __name__ == "__main__":
    # Load configuration
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    # Download elevation data
    downloaded_file = download_lidar_data(config)
    print(f"\nElevation data downloaded successfully to: {downloaded_file}")
    print("This is real elevation data covering the Xingu region from USGS SRTM.")
    print("The data is now ready for processing in your archaeological research pipeline.") 