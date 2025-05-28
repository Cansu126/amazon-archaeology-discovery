import os
import logging
import numpy as np
import rasterio
from rasterio.features import shapes
from skimage.feature import peak_local_max
from typing import Dict, Any, List

class LidarProcessing:
    def __init__(self, config: Dict[str, Any]):
        """Initialize LiDAR Processing with configuration."""
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing LiDAR Processing...")
        self.config = config
        self.logger.info("LiDAR Processing initialized.")

    def process_lidar_data(self, lidar_files: List[str]) -> Dict[str, Any]:
        """Process LiDAR data and return findings."""
        self.logger.info("Processing LIDAR data...")
        findings = {
            'sites': [],
            'metadata': {
                'source': 'SRTM',
                'region': 'Amazon',
                'coordinates': self.config.get('region', {}).get('coordinates', {})
            }
        }

        for file_path in lidar_files:
            try:
                # Check if file exists
                if not os.path.exists(file_path):
                    self.logger.error(f"File not found: {file_path}")
                    continue

                # Try to open the file with rasterio
                with rasterio.open(file_path) as src:
                    # Read the elevation data
                    elevation = src.read(1)
                    
                    # Normalize elevation data
                    elevation = np.nan_to_num(elevation, nan=0.0)
                    
                    # Find local maxima (potential archaeological sites)
                    # Adjusted parameters for SRTM data
                    coordinates = peak_local_max(
                        elevation,
                        min_distance=10,  # Reduced for SRTM resolution
                        threshold_abs=5    # Adjusted for SRTM elevation range
                    )

                    # Convert coordinates to real-world coordinates
                    for coord in coordinates:
                        row, col = coord
                        x, y = rasterio.transform.xy(src.transform, row, col)
                        z = elevation[row, col]

                        # Only include points with valid elevation
                        if not np.isnan(z) and z > 0:
                            site = {
                                'type': 'potential_archaeological_site',
                                'coordinates': {
                                    'x': float(x),
                                    'y': float(y),
                                    'elevation': float(z)
                                },
                                'confidence': 0.7,
                                'features': {
                                    'elevation': float(z),
                                    'slope': self._calculate_slope(elevation, row, col),
                                    'aspect': self._calculate_aspect(elevation, row, col)
                                }
                            }
                            findings['sites'].append(site)

            except Exception as e:
                self.logger.error(f"Error processing LIDAR file {file_path}: {str(e)}")
                continue

        self.logger.info(f"Found {len(findings['sites'])} potential archaeological sites")
        return findings

    def _calculate_slope(self, elevation: np.ndarray, row: int, col: int) -> float:
        """Calculate slope at a given point."""
        try:
            # Simple slope calculation using neighboring cells
            dx = elevation[row, col+1] - elevation[row, col-1]
            dy = elevation[row+1, col] - elevation[row-1, col]
            return float(np.arctan(np.sqrt(dx*dx + dy*dy)))
        except:
            return 0.0

    def _calculate_aspect(self, elevation: np.ndarray, row: int, col: int) -> float:
        """Calculate aspect at a given point."""
        try:
            # Simple aspect calculation using neighboring cells
            dx = elevation[row, col+1] - elevation[row, col-1]
            dy = elevation[row+1, col] - elevation[row-1, col]
            return float(np.arctan2(dy, dx))
        except:
            return 0.0