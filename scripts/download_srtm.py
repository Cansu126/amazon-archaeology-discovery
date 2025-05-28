import os
import requests
import tarfile
import logging

def download_and_extract_srtm():
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Create directory if it doesn't exist
    os.makedirs('data/amazon/lidar', exist_ok=True)

    # URL and local path
    url = "https://ot-data2.sdsc.edu/appRasterSelectService17484504598291946589777/rasters_SRTMGL3.tar.gz"
    tar_path = "data/amazon/lidar/srtm_data.tar.gz"

    try:
        # Download the file
        logger.info("Downloading SRTM data...")
        response = requests.get(url, stream=True)
        response.raise_for_status()

        with open(tar_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        # Extract the tar.gz file
        logger.info("Extracting SRTM data...")
        with tarfile.open(tar_path, 'r:gz') as tar:
            tar.extractall(path='data/amazon/lidar')

        logger.info("SRTM data downloaded and extracted successfully!")
        
        # List extracted files
        extracted_files = os.listdir('data/amazon/lidar')
        logger.info(f"Extracted files: {extracted_files}")

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise

if __name__ == "__main__":
    download_and_extract_srtm() 