#!/usr/bin/env python3
"""
Test suite for the AI-Powered Archaeological Discovery pipeline.
Tests all major components including data processing, site detection, and visualization.
"""

import unittest
import os
import json
import numpy as np
from pathlib import Path
import rasterio
from rasterio.transform import from_origin

from scripts.lidar_processing import process_lidar_data
from scripts.satellite_processing import SatelliteProcessor
from scripts.generate_visualizations import generate_visualizations

class TestPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test environment and create test data."""
        cls.test_dir = Path("tests/test_data")
        cls.test_dir.mkdir(parents=True, exist_ok=True)
        
        # Create test configuration
        cls.config = {
            'data_paths': {
                'lidar': str(cls.test_dir / 'lidar'),
                'satellite': str(cls.test_dir / 'satellite'),
                'visualizations': str(cls.test_dir / 'visualizations')
            },
            'region': {
                'min_lat': -13.5,
                'max_lat': -12.5,
                'min_lon': -54.5,
                'max_lon': -53.5
            }
        }
        
        # Create test directories
        for path in cls.config['data_paths'].values():
            Path(path).mkdir(parents=True, exist_ok=True)
        
        # Create sample test data
        cls._create_test_data()

    @classmethod
    def _create_test_data(cls):
        """Create sample test data files."""
        # Create sample LIDAR data
        lidar_data = np.random.rand(100, 100) * 100
        transform = from_origin(0, 0, 1, 1)
        with rasterio.open(
            cls.test_dir / 'lidar' / 'test_lidar.tif',
            'w',
            driver='GTiff',
            height=100,
            width=100,
            count=1,
            dtype=lidar_data.dtype,
            crs='+proj=latlong',
            transform=transform
        ) as dst:
            dst.write(lidar_data, 1)
        
        # Create sample satellite data
        satellite_data = np.random.rand(3, 100, 100) * 255
        with rasterio.open(
            cls.test_dir / 'satellite' / 'test_satellite.tif',
            'w',
            driver='GTiff',
            height=100,
            width=100,
            count=3,
            dtype=satellite_data.dtype,
            crs='+proj=latlong',
            transform=transform
        ) as dst:
            dst.write(satellite_data)

    def test_lidar_processing(self):
        """Test LIDAR data processing."""
        results = process_lidar_data(self.config['data_paths']['lidar'])
        self.assertIsInstance(results, dict)
        self.assertIn('sites', results)
        self.assertIsInstance(results['sites'], list)

    def test_satellite_processing(self):
        """Test satellite data processing."""
        processor = SatelliteProcessor(self.config)
        results = processor.process_satellite_data(self.config['data_paths']['satellite'])
        self.assertIsInstance(results, dict)
        self.assertIn('sites', results)
        self.assertIsInstance(results['sites'], list)

    def test_visualization_generation(self):
        """Test visualization generation."""
        # Create sample findings
        findings = {
            'sites': [
                {
                    'type': 'potential_archaeological_site',
                    'coordinates': {'x': -54.0, 'y': -13.0},
                    'confidence': 0.8,
                    'features': {
                        'area': 1000,
                        'ndvi_mean': 0.5,
                        'texture_mean': 0.6
                    }
                }
            ]
        }
        
        # Save findings
        findings_path = self.test_dir / 'findings.json'
        with open(findings_path, 'w') as f:
            json.dump(findings, f)
        
        # Test visualization generation
        generate_visualizations()
        self.assertTrue((self.test_dir / 'visualizations').exists())

    def test_data_validation(self):
        """Test data validation and error handling."""
        # Test with invalid data
        invalid_config = self.config.copy()
        invalid_config['data_paths']['lidar'] = 'nonexistent/path'
        
        with self.assertRaises(Exception):
            process_lidar_data(invalid_config['data_paths']['lidar'])

    def test_coordinate_conversion(self):
        """Test coordinate conversion accuracy."""
        processor = SatelliteProcessor(self.config)
        results = processor.process_satellite_data(self.config['data_paths']['satellite'])
        
        for site in results['sites']:
            self.assertIn('coordinates', site)
            self.assertIn('x', site['coordinates'])
            self.assertIn('y', site['coordinates'])
            self.assertIsInstance(site['coordinates']['x'], float)
            self.assertIsInstance(site['coordinates']['y'], float)

    def test_confidence_scoring(self):
        """Test confidence scoring system."""
        processor = SatelliteProcessor(self.config)
        results = processor.process_satellite_data(self.config['data_paths']['satellite'])
        
        for site in results['sites']:
            self.assertIn('confidence', site)
            self.assertIsInstance(site['confidence'], float)
            self.assertTrue(0 <= site['confidence'] <= 1)

    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(cls.test_dir)

if __name__ == '__main__':
    unittest.main() 