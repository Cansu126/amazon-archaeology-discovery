import os
import logging
import datetime
import json
from typing import Dict, Any, List, Tuple

from lidar_processing import LidarProcessing
from satellite_processing import SatelliteProcessor
from historical_analysis import HistoricalAnalyzer
from data_fusion import DataFusion
from validation import ValidationSystem
from visualization import Visualizer
from config_loader import ConfigLoader
from logger import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

class ArchaeologicalResearch:
    def __init__(self, config_path: str = 'config.json'):
        """Initializes the archaeological research system."""
        logger.info("Initializing Archaeological Research System...")
        
        # Load configuration
        self.config_loader = ConfigLoader(config_path)
        self.config = self.config_loader.load_config()
        
        # Create output directories
        self._create_output_directories()
        
        # Initialize data processing modules
        self.lidar_processor = LidarProcessing(self.config)
        self.satellite_processor = SatelliteProcessor(self.config)
        self.historical_analyzer = HistoricalAnalyzer(self.config)
        self.data_fusion = DataFusion(self.config)
        self.validation_system = ValidationSystem()
        self.visualizer = Visualizer(self.config)
        
        logger.info("Archaeological Research System initialized.")
        
    def _create_output_directories(self):
        """Creates the necessary output directories."""
        for key, path in self.config['output_directories'].items():
            os.makedirs(path, exist_ok=True)
            logger.info(f"Created output directory: {path}")
            
    def process_lidar_data(self, lidar_files: List[str]) -> Dict[str, Any]:
        """Processes LIDAR data and returns findings."""
        logger.info("Processing LIDAR data...")
        try:
            findings = self.lidar_processor.process_lidar_data(lidar_files)
            logger.info(f"Found {len(findings['sites'])} potential sites from LIDAR data")
            return findings
        except Exception as e:
            logger.error(f"Error processing LIDAR data: {e}")
            return {'sites': []}

    def process_satellite_data(self, satellite_path: str) -> Dict[str, Any]:
        """Process satellite data."""
        logger.info("Processing satellite data...")
        try:
            findings = self.satellite_processor.process_satellite_data(satellite_path)
            logger.info(f"Found {len(findings['sites'])} potential sites from satellite data")
            return findings
        except Exception as e:
            logger.error(f"Error processing satellite data: {str(e)}")
            return {'sites': []}

    def analyze_historical_data(self, historical_path: str) -> Dict[str, Any]:
        """Analyze historical data."""
        logger.info("Analyzing historical data...")
        try:
            findings = self.historical_analyzer.analyze_historical_data(historical_path)
            logger.info(f"Found {len(findings['sites'])} potential sites from historical analysis")
            return findings
        except Exception as e:
            logger.error(f"Error analyzing historical data: {str(e)}")
            return {'sites': []}

    def generate_visualizations(self, findings: Dict[str, Any]):
        """Generate visualizations of findings."""
        logger.info("Generating visualizations...")
        try:
            # Create interactive map
            self.visualizer.create_site_map(findings)
            
            # Create LIDAR visualization
            lidar_file = os.path.join(self.config['data_dir'], 'amazon/lidar/output_SRTMGL3.tif')
            self.visualizer.create_lidar_visualization(lidar_file, findings)
            
            # Create satellite visualization
            satellite_file = os.path.join(self.config['data_dir'], 'amazon/satellite/sentinel2.tif')
            self.visualizer.create_satellite_visualization(satellite_file, findings)
            
            # Create confidence distribution
            self.visualizer.create_confidence_histogram(findings)
            
            # Create verification comparison
            self.visualizer.create_verification_comparison(findings)
            
            logger.info("Visualizations generated successfully")
        except Exception as e:
            logger.error(f"Error generating visualizations: {str(e)}")

def main():
    """Main function to run the archaeological research process."""
    try:
        # Initialize the research system
        research = ArchaeologicalResearch()
        
        # Process LIDAR data
        lidar_files = [os.path.join(research.config['data_dir'], 'amazon/lidar/output_SRTMGL3.tif')]
        lidar_findings = research.process_lidar_data(lidar_files)
        logger.info("LIDAR data processing completed")
        
        # Process satellite data
        satellite_path = os.path.join(research.config['data_dir'], 'amazon/satellite')
        satellite_findings = research.process_satellite_data(satellite_path)
        logger.info("Satellite data processing completed")
        
        # Analyze historical data
        historical_path = os.path.join(research.config['data_dir'], 'amazon/historical')
        historical_findings = research.analyze_historical_data(historical_path)
        logger.info("Historical data analysis completed")
        
        # Combine findings
        all_findings = {
            'sites': lidar_findings['sites'] + satellite_findings['sites'] + historical_findings['sites'],
            'metadata': {
                'total_sites': len(lidar_findings['sites']) + len(satellite_findings['sites']) + len(historical_findings['sites']),
                'lidar_sites': len(lidar_findings['sites']),
                'satellite_sites': len(satellite_findings['sites']),
                'historical_sites': len(historical_findings['sites'])
            }
        }
        
        # Generate visualizations
        research.generate_visualizations(all_findings)
        
        # Save results
        output_file = os.path.join(research.config['output_dir'], 'results', 'findings.json')
        with open(output_file, 'w') as f:
            json.dump(all_findings, f, indent=2)
        
        logger.info("Archaeological research process completed successfully")
        
    except Exception as e:
        logger.error(f"Error in archaeological research process: {e}")
        raise

if __name__ == "__main__":
    main() 