import os
import requests
import json
import logging
import rasterio
from rasterio.warp import transform_bounds
import geopandas as gpd
from shapely.geometry import box
import numpy as np
from datetime import datetime, timedelta
import sentinelsat
from sentinelsat import SentinelAPI
import ee
import geemap
import laspy
import json
import zipfile
import io
from tqdm import tqdm
from pathlib import Path
import pandas as pd
from typing import Dict, Any, List

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataDownloader:
    def __init__(self, config_path: str = 'config.json'):
        """Initialize the data downloader with configuration."""
        self.config = self._load_config(config_path)
        self._create_directories()
        self._initialize_apis()
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        with open(config_path, 'r') as f:
            return json.load(f)
            
    def _create_directories(self):
        """Create necessary directories if they don't exist."""
        directories = [
            self.config['data_paths']['lidar'],
            self.config['data_paths']['satellite'],
            self.config['data_paths']['historical'],
            self.config['output_directories']['results'],
            self.config['output_directories']['visualizations'],
            self.config['output_directories']['logs']
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Created directory: {directory}")
            
    def _initialize_apis(self):
        """Initialize APIs for data access."""
        try:
            # Initialize Sentinel API
            self.sentinel_api = SentinelAPI(
                self.config['api_credentials']['sentinel_hub']['username'],
                self.config['api_credentials']['sentinel_hub']['password'],
                'https://scihub.copernicus.eu/dhus'
            )
            
            # Initialize Earth Engine
            ee.Initialize()
            
            logger.info("Successfully initialized APIs")
            
        except Exception as e:
            logger.error(f"Error initializing APIs: {e}")
            raise
            
    def download_lidar_data(self):
        """Download LIDAR data from OpenTopography GEDI mission."""
        logger.info("Downloading LIDAR data...")
        
        # Xingu region coordinates (focusing on Kuhikugu area)
        bounds = {
            'min_lat': -12.5,  # Southern boundary
            'max_lat': -12.0,  # Northern boundary
            'min_lon': -53.5,  # Western boundary
            'max_lon': -53.0   # Eastern boundary
        }
        
        # OpenTopography API endpoint for GEDI data
        api_url = "https://portal.opentopography.org/API/gedi"
        
        # Parameters for the request
        params = {
            'south': bounds['min_lat'],
            'north': bounds['max_lat'],
            'west': bounds['min_lon'],
            'east': bounds['max_lon'],
            'outputFormat': 'GTiff',
            'demtype': 'GEDI'
        }
        
        try:
            response = requests.get(api_url, params=params)
            response.raise_for_status()
            
            # Save the LIDAR data
            output_path = os.path.join(
                self.config['data_paths']['lidar'],
                f'xingu_lidar_{datetime.now().strftime("%Y%m%d")}.tif'
            )
            
            with open(output_path, 'wb') as f:
                f.write(response.content)
                
            logger.info(f"LIDAR data downloaded successfully to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error downloading LIDAR data: {e}")
            raise
            
    def download_satellite_data(self):
        """Download satellite imagery from Sentinel-2."""
        logger.info("Downloading satellite imagery...")
        
        # Initialize Sentinel API
        api = SentinelAPI(
            self.config['api_credentials']['sentinel_hub']['username'],
            self.config['api_credentials']['sentinel_hub']['password'],
            'https://scihub.copernicus.eu/dhus'
        )
        
        # Search parameters for Sentinel-2
        search_params = {
            'platformname': 'Sentinel-2',
            'producttype': 'S2MSI2A',
            'date': ('20240101', '20240528'),
            'cloudcoverpercentage': (0, 20)
        }
        
        # Xingu region footprint
        footprint = f'POLYGON(({self.config["region"]["min_lon"]} {self.config["region"]["min_lat"]}, \
                                {self.config["region"]["max_lon"]} {self.config["region"]["min_lat"]}, \
                                {self.config["region"]["max_lon"]} {self.config["region"]["max_lat"]}, \
                                {self.config["region"]["min_lon"]} {self.config["region"]["max_lat"]}, \
                                {self.config["region"]["min_lon"]} {self.config["region"]["min_lat"]}))'
        
        try:
            # Search for products
            products = api.query(footprint, **search_params)
            
            # Download the most recent product
            if products:
                product_id = list(products.keys())[0]
                api.download(product_id, self.config['data_paths']['satellite'])
                logger.info(f"Satellite imagery downloaded successfully: {product_id}")
            else:
                logger.warning("No suitable satellite imagery found")
                
        except Exception as e:
            logger.error(f"Error downloading satellite imagery: {e}")
            raise
            
    def download_historical_data(self):
        """Download historical data from FUNAI and Brazilian National Library."""
        logger.info("Downloading historical data...")
        
        # FUNAI historical maps
        funai_url = "https://www.gov.br/funai/pt-br/atuacao/terras-indigenas/geoprocessamento-e-mapas"
        
        # Brazilian National Library colonial diaries
        bnb_url = "http://bndigital.bn.gov.br/artigos/periodicos-coloniais/"
        
        try:
            # Download FUNAI maps
            response = requests.get(funai_url)
            response.raise_for_status()
            
            # Save FUNAI data
            funai_path = os.path.join(
                self.config['data_paths']['historical'],
                'indigenous_maps',
                f'funai_maps_{datetime.now().strftime("%Y%m%d")}.pdf'
            )
            
            with open(funai_path, 'wb') as f:
                f.write(response.content)
                
            # Download BNB diaries
            response = requests.get(bnb_url)
            response.raise_for_status()
            
            # Save BNB data
            bnb_path = os.path.join(
                self.config['data_paths']['historical'],
                'colonial_diaries',
                f'bnb_diaries_{datetime.now().strftime("%Y%m%d")}.pdf'
            )
            
            with open(bnb_path, 'wb') as f:
                f.write(response.content)
                
            logger.info("Historical data downloaded successfully")
            
        except Exception as e:
            logger.error(f"Error downloading historical data: {e}")
            raise
            
    def download_all_data(self):
        """Download all required data."""
        self.download_lidar_data()
        self.download_satellite_data()
        self.download_historical_data()
        logger.info("All data download completed.")

def main():
    """Main function to run the data download process."""
    try:
        downloader = DataDownloader()
        downloader.download_all_data()
        logger.info("Data download process completed successfully")
    except Exception as e:
        logger.error(f"Error in data download process: {e}")
        raise

if __name__ == "__main__":
    main() 