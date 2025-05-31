#!/usr/bin/env python3
"""
Utility script to reorganize the scripts directory structure.
"""

import os
import shutil
from pathlib import Path

# Define the new structure
STRUCTURE = {
    'data_processing': [
        'lidar_processing.py',
        'satellite_processing.py',
        'download_lidar.py',
        'download_satellite.py',
        'download_srtm.py',
        'download_data.py',
        'data_fusion.py'
    ],
    'analysis': [
        'site_detection.py',
        'historical_analysis.py',
        'validation.py',
        'comparison.py'
    ],
    'utils': [
        'logger.py',
        'config_loader.py',
        'authenticate.py',
        'monitor_performance.py',
        'optimization.py'
    ],
    'visualization': [
        'visualization.py',
        'generate_visualizations.py',
        'generate_presentation.py'
    ]
}

def move_files():
    """Move files to their new locations."""
    base_dir = Path(__file__).parent.parent
    
    # Create directories if they don't exist
    for dir_name in STRUCTURE.keys():
        (base_dir / dir_name).mkdir(exist_ok=True)
    
    # Move files
    for dir_name, files in STRUCTURE.items():
        for file_name in files:
            src = base_dir / file_name
            dst = base_dir / dir_name / file_name
            if src.exists():
                shutil.move(str(src), str(dst))
                print(f"Moved {file_name} to {dir_name}/")

if __name__ == "__main__":
    move_files() 