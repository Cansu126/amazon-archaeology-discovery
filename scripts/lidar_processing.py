#!/usr/bin/env python3
"""
LIDAR data processing module for the AI-Powered Archaeological Discovery in the Amazon project.
This module handles LIDAR data processing, including elevation anomaly detection, slope and aspect analysis, and confidence scoring.
"""

import os
import logging
import numpy as np
import rasterio
from rasterio.transform import from_origin
from scipy.ndimage import gaussian_filter
from rasterio.features import shapes
from skimage.feature import peak_local_max
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

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

def process_lidar_data(lidar_path):
    """
    Process LIDAR data to detect elevation anomalies, calculate slope and aspect, and score confidence.
    
    Args:
        lidar_path (str): Path to the directory containing LIDAR data files.
    
    Returns:
        dict: A dictionary containing processed LIDAR data, including elevation anomalies, slope, aspect, and confidence scores.
    """
    logger.info(f"Processing LIDAR data from {lidar_path}")
    
    try:
        # List all .tif files in the lidar_path
        lidar_files = [f for f in os.listdir(lidar_path) if f.endswith('.tif')]
        
        if not lidar_files:
            logger.warning(f"No LIDAR files found in {lidar_path}")
            return {'sites': []}
        
        # Process each LIDAR file
        all_sites = []
        for lidar_file in lidar_files:
            file_path = os.path.join(lidar_path, lidar_file)
            logger.info(f"Processing LIDAR file: {lidar_file}")
            
            with rasterio.open(file_path) as src:
                # Read elevation data
                elevation = src.read(1)
                
                # Detect elevation anomalies
                anomalies = detect_elevation_anomalies(elevation)
                
                # Calculate slope and aspect
                slope, aspect = calculate_slope_aspect(elevation, src.transform)
                
                # Score confidence
                confidence = score_confidence(anomalies, slope, aspect)
                
                # Extract site information
                sites = extract_sites(anomalies, slope, aspect, confidence, src.transform)
                all_sites.extend(sites)
        
        logger.info(f"Found {len(all_sites)} potential sites from LIDAR data")
        return {'sites': all_sites}
    
    except Exception as e:
        logger.error(f"Error processing LIDAR data: {str(e)}", exc_info=True)
        return {'sites': []}

def detect_elevation_anomalies(elevation):
    """
    Detect elevation anomalies using Gaussian filtering and thresholding.
    
    Args:
        elevation (numpy.ndarray): 2D array of elevation data.
    
    Returns:
        numpy.ndarray: Binary mask of detected anomalies.
    """
    # Apply Gaussian filter to smooth elevation data
    smoothed = gaussian_filter(elevation, sigma=1.0)
    
    # Calculate difference between original and smoothed data
    diff = elevation - smoothed
    
    # Threshold to detect anomalies (e.g., > 2 standard deviations)
    threshold = 2 * np.std(diff)
    anomalies = np.abs(diff) > threshold
    
    return anomalies

def calculate_slope_aspect(elevation, transform):
    """
    Calculate slope and aspect from elevation data.
    
    Args:
        elevation (numpy.ndarray): 2D array of elevation data.
        transform (rasterio.transform.Affine): Affine transform for the elevation data.
    
    Returns:
        tuple: (slope, aspect) as numpy arrays.
    """
    # Calculate gradients
    dy, dx = np.gradient(elevation)
    
    # Calculate slope (in radians)
    slope = np.arctan(np.sqrt(dx**2 + dy**2))
    
    # Calculate aspect (in radians)
    aspect = np.arctan2(dy, dx)
    
    return slope, aspect

def score_confidence(anomalies, slope, aspect):
    """
    Score confidence based on anomalies, slope, and aspect.
    
    Args:
        anomalies (numpy.ndarray): Binary mask of detected anomalies.
        slope (numpy.ndarray): Slope data.
        aspect (numpy.ndarray): Aspect data.
    
    Returns:
        numpy.ndarray: Confidence scores.
    """
    # Example confidence scoring logic
    # Higher confidence for anomalies with moderate slopes and specific aspects
    confidence = np.zeros_like(anomalies, dtype=float)
    
    # Anomalies with moderate slopes (e.g., 0.1 to 0.3 radians)
    moderate_slope = (slope > 0.1) & (slope < 0.3)
    
    # Anomalies with specific aspects (e.g., facing north or east)
    specific_aspect = (aspect > -np.pi/4) & (aspect < np.pi/4)
    
    # Combine conditions
    confidence[anomalies & moderate_slope & specific_aspect] = 0.8
    confidence[anomalies & moderate_slope] = 0.6
    confidence[anomalies] = 0.4
    
    return confidence

def extract_sites(anomalies, slope, aspect, confidence, transform):
    """
    Extract site information from processed LIDAR data.
    
    Args:
        anomalies (numpy.ndarray): Binary mask of detected anomalies.
        slope (numpy.ndarray): Slope data.
        aspect (numpy.ndarray): Aspect data.
        confidence (numpy.ndarray): Confidence scores.
        transform (rasterio.transform.Affine): Affine transform for the data.
    
    Returns:
        list: List of dictionaries containing site information.
    """
    sites = []
    
    # Find coordinates of anomalies
    y_indices, x_indices = np.where(anomalies)
    
    for y, x in zip(y_indices, x_indices):
        # Convert pixel coordinates to geographic coordinates
        lon, lat = rasterio.transform.xy(transform, y, x)
        
        site = {
            'coordinates': {
                'x': lon,
                'y': lat,
                'elevation': anomalies[y, x]
            },
            'confidence': float(confidence[y, x]),
            'features': {
                'slope': float(slope[y, x]),
                'aspect': float(aspect[y, x])
            }
        }
        sites.append(site)
    
    return sites