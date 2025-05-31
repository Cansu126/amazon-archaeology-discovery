#!/usr/bin/env python3
"""
Satellite data processing module for the AI-Powered Archaeological Discovery in the Amazon project.
This module handles satellite data processing, including NDVI calculation, pattern recognition, and texture analysis.
"""

import rasterio
import numpy as np
import matplotlib.pyplot as plt
import skimage.feature
from skimage import exposure
from skimage.segmentation import watershed
from scipy import ndimage as ndi
import cv2
import os
import glob
import logging
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from typing import Dict, List, Tuple, Any
from rasterio.transform import from_origin
from skimage.feature import local_binary_pattern
from skimage.filters import threshold_otsu
from skimage.measure import regionprops
from scipy.ndimage import gaussian_filter

logger = logging.getLogger(__name__)

class SatelliteProcessor:
    def __init__(self, config: Dict[str, Any]):
        """Initialize satellite processor with configuration."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        logger.info("Satellite processor initialized")

    def process_satellite_data(self, satellite_path: str) -> Dict[str, Any]:
        """Process satellite imagery to detect potential archaeological sites."""
        self.logger.info(f"Processing satellite data from {satellite_path}")
        
        try:
            # List all .tif files in the satellite_path
            satellite_files = [f for f in os.listdir(satellite_path) if f.endswith('.tif')]
            
            if not satellite_files:
                self.logger.warning(f"No satellite files found in {satellite_path}")
                return {'sites': []}
            
            # Process each satellite file
            all_sites = []
            for satellite_file in satellite_files:
                file_path = os.path.join(satellite_path, satellite_file)
                self.logger.info(f"Processing satellite file: {satellite_file}")
                
                with rasterio.open(file_path) as src:
                    # Read RGB bands
                    rgb = src.read([1, 2, 3])
                    
                    # Calculate NDVI
                    ndvi = self.calculate_ndvi(rgb)
                    
                    # Detect patterns
                    patterns = self.detect_patterns(ndvi)
                    
                    # Analyze texture
                    texture = self.analyze_texture(rgb)
                    
                    # Extract site information
                    sites = self.extract_sites(patterns, texture, ndvi, src.transform)
                    all_sites.extend(sites)
            
            self.logger.info(f"Found {len(all_sites)} potential sites from satellite data")
            return {'sites': all_sites}
        
        except Exception as e:
            self.logger.error(f"Error processing satellite data: {str(e)}", exc_info=True)
            return {'sites': []}

    def calculate_ndvi(self, rgb: np.ndarray) -> np.ndarray:
        """Calculate Normalized Difference Vegetation Index."""
        red = rgb[0].astype(float)
        nir = rgb[2].astype(float)  # Using blue band as approximation for NIR
        
        denominator = nir + red
        denominator[denominator == 0] = 1e-6  # Avoid division by zero
        ndvi = (nir - red) / denominator
        
        return ndvi

    def detect_patterns(self, ndvi: np.ndarray) -> np.ndarray:
        """Detect patterns in NDVI data that might indicate archaeological features."""
        # Apply Gaussian filter to reduce noise
        smoothed = gaussian_filter(ndvi, sigma=1.0)
        
        # Calculate local variance
        local_var = gaussian_filter(smoothed**2, sigma=1.0) - gaussian_filter(smoothed, sigma=1.0)**2
        
        # Threshold to detect patterns
        threshold = threshold_otsu(local_var)
        patterns = local_var > threshold
        
        return patterns

    def analyze_texture(self, rgb: np.ndarray) -> np.ndarray:
        """Analyze texture features in RGB imagery."""
        gray = np.mean(rgb, axis=0)
        
        radius = 3
        n_points = 8 * radius
        lbp = local_binary_pattern(gray, n_points, radius, method='uniform')
        
        texture = np.zeros_like(gray)
        for i in range(n_points + 2):
            texture[lbp == i] = i / (n_points + 1)
        
        return texture

    def extract_sites(self, patterns: np.ndarray, texture: np.ndarray, ndvi: np.ndarray, transform: from_origin) -> List[Dict[str, Any]]:
        """Extract site information from processed satellite data."""
        sites = []
        
        # Find regions of interest
        regions = regionprops(patterns.astype(int))
        
        for region in regions:
            # Get region properties
            y, x = region.centroid
            area = region.area
            
            # Convert pixel coordinates to geographic coordinates
            lon, lat = rasterio.transform.xy(transform, int(y), int(x))
            
            # Calculate confidence based on multiple factors
            ndvi_mean = np.mean(ndvi[region.coords[:, 0], region.coords[:, 1]])
            texture_mean = np.mean(texture[region.coords[:, 0], region.coords[:, 1]])
            
            confidence = self.calculate_confidence(ndvi_mean, texture_mean, area)
            
            site = {
                'type': 'potential_archaeological_site',
                'coordinates': {
                    'x': float(lon),
                    'y': float(lat)
                },
                'confidence': float(confidence),
                'features': {
                    'area': float(area),
                    'ndvi_mean': float(ndvi_mean),
                    'texture_mean': float(texture_mean)
                }
            }
            sites.append(site)
        
        return sites

    def calculate_confidence(self, ndvi_mean: float, texture_mean: float, area: float) -> float:
        """Calculate confidence score based on multiple factors."""
        # Normalize factors
        ndvi_score = (ndvi_mean + 1) / 2  # NDVI ranges from -1 to 1
        texture_score = texture_mean  # Already normalized
        area_score = min(area / 1000, 1)  # Normalize area
        
        # Weighted combination
        confidence = (0.4 * ndvi_score + 0.3 * texture_score + 0.3 * area_score)
        
        return min(max(confidence, 0), 1)  # Ensure between 0 and 1

    def _calculate_ndvi(self, bands: np.ndarray) -> np.ndarray:
        """Calculate Normalized Difference Vegetation Index."""
        nir = bands[3]  # Near Infrared band
        red = bands[2]  # Red band
        ndvi = (nir - red) / (nir + red + 1e-6)
        return ndvi

    def _detect_geometric_patterns(self, ndvi: np.ndarray) -> List[Dict[str, Any]]:
        """Detect geometric patterns in vegetation that might indicate archaeological features."""
        patterns = []
        
        # Edge detection
        edges = cv2.Canny(ndvi.astype(np.uint8), 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            # Calculate contour properties
            area = cv2.contourArea(contour)
            if area < 100:  # Filter small noise
                continue
                
            # Calculate shape features
            perimeter = cv2.arcLength(contour, True)
            circularity = 4 * np.pi * area / (perimeter * perimeter)
            
            # Check if shape is regular enough to be man-made
            if circularity > 0.6:
                M = cv2.moments(contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    
                    patterns.append({
                        'x': cx,
                        'y': cy,
                        'type': 'geometric_pattern',
                        'confidence': circularity,
                        'area': area,
                        'vegetation_anomaly': self._calculate_vegetation_anomaly(ndvi, cx, cy)
                    })
        
        return patterns

    def _analyze_texture(self, bands: np.ndarray) -> Dict[str, np.ndarray]:
        """Analyze texture features in the satellite imagery."""
        texture_features = {}
        
        # Convert to grayscale for texture analysis
        gray = np.mean(bands[:3], axis=0)
        
        # Calculate GLCM features
        texture_features['contrast'] = skimage.feature.greycomatrix(
            gray.astype(np.uint8), [1], [0, np.pi/4, np.pi/2, 3*np.pi/4], 
            symmetric=True, normed=True
        )
        
        return texture_features

    def _verify_pattern(self, pattern: Dict[str, Any], texture_features: Dict[str, np.ndarray]) -> bool:
        """Verify if a detected pattern is likely to be an archaeological feature."""
        # Check texture consistency
        texture_score = np.mean(texture_features['contrast'])
        pattern['texture_score'] = float(texture_score)
        
        # Combine multiple factors for verification
        verification_score = (
            pattern['confidence'] * 0.4 +  # Geometric regularity
            texture_score * 0.3 +          # Texture consistency
            pattern['vegetation_anomaly'] * 0.3  # Vegetation anomaly
        )
        
        return verification_score > 0.6

    def _calculate_vegetation_anomaly(self, ndvi: np.ndarray, x: int, y: int) -> float:
        """Calculate vegetation anomaly score for a location."""
        window_size = 10
        x1 = max(0, x - window_size)
        x2 = min(ndvi.shape[1], x + window_size)
        y1 = max(0, y - window_size)
        y2 = min(ndvi.shape[0], y + window_size)
        
        local_ndvi = ndvi[y1:y2, x1:x2]
        global_mean = np.mean(ndvi)
        local_mean = np.mean(local_ndvi)
        
        return float(abs(local_mean - global_mean) / global_mean) 