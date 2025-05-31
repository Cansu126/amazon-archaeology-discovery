#!/usr/bin/env python3
"""
Main entry point for the Amazon Archaeological Site Detection Pipeline.
This script orchestrates the entire pipeline process.
"""

import logging
from pathlib import Path
from scripts.utils.config_loader import load_config
from scripts.utils.logger import setup_logger
from scripts.data_processing.lidar_processing import process_lidar_data
from scripts.data_processing.satellite_processing import process_satellite_data
from scripts.analysis.site_detection import detect_sites
from scripts.analysis.historical_analysis import analyze_historical_data
from scripts.visualization.visualization import generate_visualizations

def main():
    # Setup logging
    setup_logger()
    logger = logging.getLogger(__name__)
    logger.info("Starting Amazon Archaeological Site Detection Pipeline")

    # Load configuration
    config = load_config()
    
    try:
        # Process LiDAR data
        logger.info("Processing LiDAR data...")
        lidar_results = process_lidar_data(config)
        
        # Process satellite imagery
        logger.info("Processing satellite imagery...")
        satellite_results = process_satellite_data(config)
        
        # Detect archaeological sites
        logger.info("Detecting archaeological sites...")
        sites = detect_sites(lidar_results, satellite_results, config)
        
        # Analyze historical data
        logger.info("Analyzing historical data...")
        historical_insights = analyze_historical_data(sites, config)
        
        # Generate visualizations
        logger.info("Generating visualizations...")
        generate_visualizations(sites, historical_insights, config)
        
        logger.info("Pipeline completed successfully!")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        raise

if __name__ == "__main__":
    main() 