#!/usr/bin/env python3
"""
Main execution script for the AI-Powered Archaeological Discovery in the Amazon project.
This script orchestrates the entire pipeline: data collection, preprocessing, AI analysis,
site detection, validation, comparison, and visualization.
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path

# Import custom modules
from lidar_processing import process_lidar_data
from satellite_processing import SatelliteProcessor
from historical_analysis import HistoricalAnalyzer
from site_detection import detect_sites
from validation import validate_sites
from comparison import compare_with_known_sites
from generate_visualizations import generate_visualizations
from optimization import optimize_pipeline
from monitor_performance import monitor_pipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"data/amazon/logs/pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_config():
    """Load configuration from config.json."""
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("config.json not found. Please create it with your API keys and settings.")
        raise
    except json.JSONDecodeError:
        logger.error("config.json is not valid JSON. Please check its format.")
        raise

def ensure_directories(config):
    """Ensure all required directories exist."""
    for path in config['data_paths'].values():
        Path(path).mkdir(parents=True, exist_ok=True)
    Path("data/amazon/logs").mkdir(parents=True, exist_ok=True)

def main():
    """Main execution function."""
    logger.info("Starting the archaeological discovery pipeline.")
    
    # Load configuration
    config = load_config()
    ensure_directories(config)
    
    # Initialize performance monitoring and optimization
    monitor = monitor_pipeline(config)
    optimizer = optimize_pipeline(config)
    
    try:
        # Data Collection and Preprocessing
        logger.info("Processing LIDAR data...")
        monitor.record_metrics("lidar_processing_start")
        lidar_results = process_lidar_data(config['data_paths']['lidar'])
        monitor.record_metrics("lidar_processing_complete")
        
        logger.info("Processing satellite data...")
        monitor.record_metrics("satellite_processing_start")
        satellite_processor = SatelliteProcessor(config)
        satellite_results = satellite_processor.process_satellite_data(config['data_paths']['satellite'])
        monitor.record_metrics("satellite_processing_complete")
        
        logger.info("Analyzing historical documents...")
        monitor.record_metrics("historical_analysis_start")
        historical_analyzer = HistoricalAnalyzer(config)
        historical_results = historical_analyzer.analyze_historical_data(config['data_paths']['historical'])
        monitor.record_metrics("historical_analysis_complete")
        
        # Site Detection
        logger.info("Detecting potential archaeological sites...")
        monitor.record_metrics("site_detection_start")
        sites = detect_sites(lidar_results, satellite_results, historical_results)
        monitor.record_metrics("site_detection_complete")
        
        # Validation
        logger.info("Validating detected sites...")
        monitor.record_metrics("site_validation_start")
        validated_sites = validate_sites(sites)
        monitor.record_metrics("site_validation_complete")
        
        # Comparison with Known Sites
        logger.info("Comparing with known archaeological sites...")
        monitor.record_metrics("site_comparison_start")
        comparison_results = compare_with_known_sites(validated_sites)
        monitor.record_metrics("site_comparison_complete")
        
        # Visualization
        logger.info("Generating visualizations...")
        monitor.record_metrics("visualization_start")
        generate_visualizations(comparison_results)
        monitor.record_metrics("visualization_complete")
        
        # Generate and save performance report
        monitor.save_report()
        monitor.plot_metrics()
        
        logger.info("Pipeline completed successfully.")
        
    except Exception as e:
        logger.error(f"An error occurred during pipeline execution: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main() 