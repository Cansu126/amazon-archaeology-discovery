import os
import logging
import json
from main import ArchaeologicalResearch
from visualization import Visualizer
from generate_presentation import PresentationGenerator

def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('pipeline.log'),
            logging.StreamHandler()
        ]
    )

def run_pipeline():
    """Run the complete archaeological research pipeline."""
    logger = logging.getLogger(__name__)
    logger.info("Starting archaeological research pipeline...")
    
    # Load configuration
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    # Initialize research system
    research = ArchaeologicalResearch(config)
    
    # Process LIDAR data
    logger.info("Processing LIDAR data...")
    lidar_findings = research.process_lidar_data()
    
    # Process satellite data
    logger.info("Processing satellite data...")
    satellite_findings = research.process_satellite_data()
    
    # Analyze historical data
    logger.info("Analyzing historical data...")
    historical_findings = research.analyze_historical_data()
    
    # Combine findings
    logger.info("Combining findings...")
    combined_findings = research.combine_findings(
        lidar_findings,
        satellite_findings,
        historical_findings
    )
    
    # Generate visualizations
    logger.info("Generating visualizations...")
    visualizer = Visualizer(config)
    visualizer.create_site_map(combined_findings)
    visualizer.create_lidar_visualization(combined_findings)
    visualizer.create_satellite_visualization(combined_findings)
    visualizer.create_confidence_histogram(combined_findings)
    visualizer.create_verification_comparison(combined_findings)
    
    # Generate presentation
    logger.info("Generating presentation...")
    presentation_generator = PresentationGenerator(config)
    presentation_generator.generate_presentation(combined_findings)
    
    # Save results
    logger.info("Saving results...")
    output_path = os.path.join(config['output_directories']['results'], 'findings.json')
    with open(output_path, 'w') as f:
        json.dump(combined_findings, f, indent=2)
    
    logger.info("Pipeline completed successfully!")
    logger.info(f"Results saved to {output_path}")
    logger.info(f"Visualizations saved to {config['output_directories']['visualizations']}")
    logger.info(f"Presentation saved to {os.path.join(config['output_directories']['visualizations'], 'findings_presentation.pptx')}")

if __name__ == "__main__":
    setup_logging()
    run_pipeline() 