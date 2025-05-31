import os
import logging
from typing import Dict, Any
import json
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def download_satellite_data(config: Dict[str, Any]) -> str:
    """Download Sentinel-2 satellite imagery for the Xingu region."""
    logger.info("Downloading satellite imagery...")
    
    # Get region coordinates from config
    region = config['region']
    footprint = f"POLYGON(({region['min_lon']} {region['min_lat']}, {region['max_lon']} {region['min_lat']}, {region['max_lon']} {region['max_lat']}, {region['min_lon']} {region['max_lat']}, {region['min_lon']} {region['min_lat']}))"
    
    # Create output directory if it doesn't exist
    output_dir = config['data_paths']['satellite']
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize Sentinel API
    api = SentinelAPI(
        config['api_credentials']['sentinel_hub']['username'],
        config['api_credentials']['sentinel_hub']['password'],
        'https://scihub.copernicus.eu/dhus'
    )
    
    # Search for Sentinel-2 images
    products = api.query(
        footprint,
        date=(datetime.now() - timedelta(days=30), datetime.now()),
        platformname='Sentinel-2',
        cloudcoverpercentage=(0, 20)
    )
    
    if not products:
        logger.warning("No suitable satellite images found")
        return None
    
    # Download the most recent image
    product_id = list(products.keys())[0]
    output_file = os.path.join(output_dir, f"sentinel2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip")
    
    try:
        api.download(product_id, output_dir)
        logger.info(f"Satellite imagery downloaded successfully to {output_file}")
        return output_file
        
    except Exception as e:
        logger.error(f"Error downloading satellite imagery: {e}")
        raise

if __name__ == "__main__":
    # Load configuration
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    # Download satellite imagery
    download_satellite_data(config) 