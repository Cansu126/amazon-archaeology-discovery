import os
import json
from visualization import Visualizer, Visualization

def generate_visualizations():
    # Load configuration
    config = {
        'output_dir': 'data/amazon',
        'region': {
            'min_lat': -12.5,
            'max_lat': -13.5,
            'min_lon': -53.5,
            'max_lon': -54.5
        }
    }
    
    # Create output directory
    os.makedirs('data/amazon/visualizations', exist_ok=True)
    
    # Load findings
    with open('data/amazon/findings.json', 'r') as f:
        findings = json.load(f)
    
    # Initialize visualizers
    visualizer = Visualizer(config)
    visualization = Visualization(config)
    
    # Generate all visualizations
    print("Generating site map...")
    visualizer.create_site_map(findings)
    
    print("Generating confidence histogram...")
    visualizer.create_confidence_histogram(findings)
    
    print("Generating verification comparison...")
    visualizer.create_verification_comparison(findings)
    
    print("Generating elevation profile...")
    visualization._create_elevation_profile(findings)
    
    print("Generating site distribution map...")
    visualization._create_site_distribution_map(findings)
    
    print("Generating feature analysis plots...")
    visualization._create_feature_analysis_plots(findings)
    
    print("Generating interactive map...")
    visualization._create_interactive_map(findings)
    
    print("Generating 3D visualization...")
    visualization._create_3d_visualization(findings)
    
    print("Generating summary plots...")
    visualization._create_summary_plots(findings)
    
    # New enhanced visualizations
    print("Generating detailed confidence intervals...")
    visualization._create_detailed_confidence_intervals(findings)
    
    print("Generating indigenous knowledge analysis...")
    visualization._create_indigenous_knowledge_visualization(findings)
    
    print("Generating temporal development analysis...")
    visualization._create_temporal_development_analysis(findings)
    
    print("Generating known site comparison...")
    visualization._create_known_site_comparison(findings)
    
    print("All visualizations generated successfully!")

if __name__ == "__main__":
    generate_visualizations() 