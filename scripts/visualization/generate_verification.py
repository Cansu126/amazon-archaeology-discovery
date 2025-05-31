#!/usr/bin/env python3
"""
Generate verification comparison visualization for archaeological sites.
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

def generate_verification_comparison(sites_data, output_path):
    """
    Generate a verification comparison plot showing LIDAR vs Satellite evidence.
    
    Args:
        sites_data (dict): Dictionary containing site data
        output_path (str): Path to save the visualization
    """
    # Create figure
    plt.figure(figsize=(12, 8))
    
    # Generate sample data if none provided
    if not sites_data:
        n_sites = 100
        sites_data = {
            'lidar_confidence': np.random.normal(0.7, 0.15, n_sites),
            'satellite_confidence': np.random.normal(0.65, 0.2, n_sites),
            'confidence_score': np.random.normal(0.68, 0.1, n_sites)
        }
    
    # Create scatter plot
    scatter = plt.scatter(
        sites_data['lidar_confidence'],
        sites_data['satellite_confidence'],
        c=sites_data['confidence_score'],
        cmap='viridis',
        alpha=0.6,
        s=100
    )
    
    # Add colorbar
    cbar = plt.colorbar(scatter)
    cbar.set_label('Overall Confidence Score')
    
    # Add diagonal line
    plt.plot([0, 1], [0, 1], 'k--', alpha=0.3, label='Equal Confidence')
    
    # Customize plot
    plt.title('Site Verification: LIDAR vs Satellite Evidence', fontsize=14, pad=20)
    plt.xlabel('LIDAR Confidence Score', fontsize=12)
    plt.ylabel('Satellite Confidence Score', fontsize=12)
    
    # Add grid
    plt.grid(True, alpha=0.3)
    
    # Add legend
    plt.legend()
    
    # Save plot
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    # Create output directory if it doesn't exist
    output_dir = Path("../../img")
    output_dir.mkdir(exist_ok=True)
    
    # Generate and save visualization
    generate_verification_comparison(
        sites_data=None,  # Will use sample data
        output_path=output_dir / "verification_comparison.png"
    ) 