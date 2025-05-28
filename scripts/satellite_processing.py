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

logger = logging.getLogger(__name__)

class SatelliteProcessor:
    def __init__(self, config: Dict[str, Any]):
        """Initialize satellite processor with configuration."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        logger.info("Satellite processor initialized")

    def process_satellite_data(self, satellite_path: str) -> Dict[str, Any]:
        """Process satellite imagery to detect potential archaeological sites."""
        self.logger.info(f"Processing satellite image: {satellite_path}")
        
        findings = {
            'sites': [],
            'metadata': {
                'source': 'Sentinel-2',
                'region': 'Amazon',
                'processing_method': 'Multi-spectral Pattern Recognition'
            }
        }

        try:
            # Load satellite imagery
            with rasterio.open(satellite_path) as src:
                # Read all bands
                bands = src.read()
                
                # Calculate vegetation indices
                ndvi = self._calculate_ndvi(bands)
                
                # Detect geometric patterns
                patterns = self._detect_geometric_patterns(ndvi)
                
                # Analyze texture features
                texture_features = self._analyze_texture(bands)
                
                # Combine evidence
                for pattern in patterns:
                    # Verify pattern with texture analysis
                    if self._verify_pattern(pattern, texture_features):
                        site = {
                            'type': 'potential_archaeological_site',
                            'coordinates': {
                                'x': float(pattern['x']),
                                'y': float(pattern['y']),
                                'elevation': float(pattern.get('elevation', 0))
                            },
                            'confidence': pattern['confidence'],
                            'features': {
                                'pattern_type': pattern['type'],
                                'texture_score': pattern['texture_score'],
                                'vegetation_anomaly': pattern['vegetation_anomaly']
                            },
                            'verification_method': 'satellite_pattern_recognition'
                        }
                        findings['sites'].append(site)

            self.logger.info(f"Found {len(findings['sites'])} potential sites from satellite analysis")
            return findings

        except Exception as e:
            self.logger.error(f"Error processing satellite data: {str(e)}")
            return findings

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