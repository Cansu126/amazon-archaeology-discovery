import os
import json
import logging
from scripts.visualization import Visualizer, Visualization
from scripts.lidar_processing import LidarProcessing

def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def main():
    """Main function to run the archaeological site detection pipeline."""
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting archaeological site detection pipeline...")

    # Load configuration
    config = {
        'output_dir': 'data/amazon',
        'region': {
            'min_lat': -13.5,
            'max_lat': -12.5,
            'min_lon': -54.5,
            'max_lon': -53.5
        }
    }

    # Create output directories
    os.makedirs('data/amazon/visualizations', exist_ok=True)

    try:
        # Initialize processors
        lidar_processor = LidarProcessing(config)
        visualizer = Visualizer(config)
        visualization = Visualization(config)

        # Load findings
        with open('data/amazon/findings.json', 'r') as f:
            findings = json.load(f)

        # Generate visualizations
        logger.info("Generating visualizations...")
        visualizer.create_site_map(findings)
        visualizer.create_confidence_histogram(findings)
        visualizer.create_verification_comparison(findings)
        visualization._create_elevation_profile(findings)
        visualization._create_site_distribution_map(findings)
        visualization._create_feature_analysis_plots(findings)
        visualization._create_interactive_map(findings)
        visualization._create_3d_visualization(findings)
        visualization._create_summary_plots(findings)

        logger.info("Pipeline completed successfully!")
        logger.info(f"Visualizations saved in: {os.path.abspath('data/amazon/visualizations')}")

    except Exception as e:
        logger.error(f"Error in pipeline: {str(e)}")
        raise

if __name__ == "__main__":
    main() 