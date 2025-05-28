import os
import logging
import json
import numpy as np
import matplotlib.pyplot as plt
import folium
from folium.plugins import HeatMap
import rasterio
from rasterio.plot import show
from typing import Dict, Any, List
import plotly.graph_objects as go
from datetime import datetime
from folium import plugins

logger = logging.getLogger(__name__)

class Visualizer:
    def __init__(self, config: Dict[str, Any]):
        """Initialize visualizer with configuration."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.output_dir = os.path.join(config['output_dir'], 'visualizations')
        os.makedirs(self.output_dir, exist_ok=True)

    def create_site_map(self, findings: Dict[str, Any], output_file: str = 'site_map.html'):
        """Create an interactive map of discovered sites."""
        # Create base map centered on Xingu River Basin
        m = folium.Map(location=[-12.5, -53.5], zoom_start=8)
        
        # Add satellite layer
        folium.TileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                        attr='Esri',
                        name='Satellite').add_to(m)
        
        # Add sites with different colors based on confidence
        for site in findings['sites']:
            confidence = site['confidence']
            color = 'red' if confidence > 0.8 else 'orange' if confidence > 0.6 else 'yellow'
            
            folium.CircleMarker(
                location=[site['coordinates']['y'], site['coordinates']['x']],
                radius=5,
                color=color,
                fill=True,
                popup=f"Confidence: {confidence:.2f}<br>Type: {site['type']}"
            ).add_to(m)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        # Save map
        m.save(os.path.join(self.output_dir, output_file))

    def create_lidar_visualization(self, lidar_file: str, findings: Dict[str, Any], output_file: str = 'lidar_evidence.png'):
        """Create visualization of LIDAR data with discovered sites."""
        with rasterio.open(lidar_file) as src:
            elevation = src.read(1)
            
            # Create figure
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # Plot elevation data
            im = ax.imshow(elevation, cmap='terrain')
            plt.colorbar(im, ax=ax, label='Elevation (m)')
            
            # Plot discovered sites
            for site in findings['sites']:
                if site.get('verification_method') == 'lidar':
                    ax.plot(site['coordinates']['x'], site['coordinates']['y'], 'r*', markersize=10)
            
            ax.set_title('LIDAR Data with Archaeological Sites')
            plt.savefig(os.path.join(self.output_dir, output_file))
            plt.close()

    def create_satellite_visualization(self, satellite_file: str, findings: Dict[str, Any], output_file: str = 'satellite_evidence.png'):
        """Create visualization of satellite data with discovered patterns."""
        with rasterio.open(satellite_file) as src:
            # Read RGB bands
            rgb = src.read([1, 2, 3])
            
            # Create figure
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # Plot satellite image
            show(rgb, ax=ax)
            
            # Plot discovered patterns
            for site in findings['sites']:
                if site.get('verification_method') == 'satellite_pattern_recognition':
                    ax.plot(site['coordinates']['x'], site['coordinates']['y'], 'g*', markersize=10)
            
            ax.set_title('Satellite Imagery with Archaeological Patterns')
            plt.savefig(os.path.join(self.output_dir, output_file))
            plt.close()

    def create_confidence_histogram(self, findings: Dict[str, Any], output_file: str = 'confidence_distribution.png'):
        """Create histogram of site confidence scores."""
        confidences = [site['confidence'] for site in findings['sites']]
        
        plt.figure(figsize=(10, 6))
        plt.hist(confidences, bins=20, color='blue', alpha=0.7)
        plt.xlabel('Confidence Score')
        plt.ylabel('Number of Sites')
        plt.title('Distribution of Site Confidence Scores')
        plt.grid(True, alpha=0.3)
        plt.savefig(os.path.join(self.output_dir, output_file))
        plt.close()

    def create_verification_comparison(self, findings: Dict[str, Any], output_file: str = 'verification_comparison.png'):
        """Create comparison of verification methods."""
        lidar_sites = [s for s in findings['sites'] if s.get('verification_method') == 'lidar']
        satellite_sites = [s for s in findings['sites'] if s.get('verification_method') == 'satellite_pattern_recognition']
        
        methods = ['LIDAR', 'Satellite', 'Both']
        counts = [
            len(lidar_sites),
            len(satellite_sites),
            len([s for s in findings['sites'] if s.get('verification_method') == 'both'])
        ]
        
        plt.figure(figsize=(10, 6))
        plt.bar(methods, counts, color=['blue', 'green', 'purple'])
        plt.xlabel('Verification Method')
        plt.ylabel('Number of Sites')
        plt.title('Site Distribution by Verification Method')
        plt.grid(True, alpha=0.3)
        plt.savefig(os.path.join(self.output_dir, output_file))
        plt.close()

class Visualization:
    def __init__(self, config: Dict[str, Any]):
        """Initialize visualization system with configuration."""
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.output_dir = config.get('output_directories', {}).get('visualizations', 'data/amazon/visualizations')
        os.makedirs(self.output_dir, exist_ok=True)
        self.region = config.get('region', {})
        
    def create_visualization(self, findings: Dict[str, Any]) -> Dict[str, str]:
        """Create visualizations from the findings."""
        self.logger.info("Creating visualizations...")
        try:
            # Create elevation profile
            elevation_profile = self._create_elevation_profile(findings)
            
            # Create site distribution map
            site_map = self._create_site_distribution_map(findings)
            
            # Create feature analysis plots
            feature_plots = self._create_feature_analysis_plots(findings)
            
            return {
                'elevation_profile': elevation_profile,
                'site_distribution': site_map,
                'feature_analysis': feature_plots
            }
        except Exception as e:
            self.logger.error(f"Error creating visualizations: {str(e)}")
            raise

    def _create_elevation_profile(self, findings: Dict[str, Any]) -> str:
        """Create elevation profile visualization."""
        try:
            # Extract elevations from sites
            elevations = [site['coordinates']['elevation'] for site in findings['sites']]
            
            # Create plot
            plt.figure(figsize=(10, 6))
            plt.hist(elevations, bins=20, alpha=0.7)
            plt.title('Elevation Distribution of Potential Archaeological Sites')
            plt.xlabel('Elevation (meters)')
            plt.ylabel('Number of Sites')
            
            # Save plot
            output_file = os.path.join(self.output_dir, 'elevation_profile.png')
            plt.savefig(output_file)
            plt.close()
            
            return output_file
        except Exception as e:
            self.logger.error(f"Error creating elevation profile: {str(e)}")
            return ""

    def _create_site_distribution_map(self, findings: Dict[str, Any]) -> str:
        """Create site distribution map visualization."""
        try:
            # Extract coordinates
            x_coords = [site['coordinates']['x'] for site in findings['sites']]
            y_coords = [site['coordinates']['y'] for site in findings['sites']]
            
            # Create plot
            plt.figure(figsize=(12, 8))
            plt.scatter(x_coords, y_coords, c='red', alpha=0.6)
            plt.title('Distribution of Potential Archaeological Sites')
            plt.xlabel('Longitude')
            plt.ylabel('Latitude')
            
            # Save plot
            output_file = os.path.join(self.output_dir, 'site_distribution.png')
            plt.savefig(output_file)
            plt.close()
            
            return output_file
        except Exception as e:
            self.logger.error(f"Error creating site distribution map: {str(e)}")
            return ""

    def _create_feature_analysis_plots(self, findings: Dict[str, Any]) -> str:
        """Create feature analysis plots."""
        try:
            # Extract features
            slopes = [site['features']['slope'] for site in findings['sites']]
            aspects = [site['features']['aspect'] for site in findings['sites']]
            
            # Create subplots
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # Slope distribution
            ax1.hist(slopes, bins=20, alpha=0.7)
            ax1.set_title('Slope Distribution')
            ax1.set_xlabel('Slope (radians)')
            ax1.set_ylabel('Number of Sites')
            
            # Aspect distribution
            ax2.hist(aspects, bins=20, alpha=0.7)
            ax2.set_title('Aspect Distribution')
            ax2.set_xlabel('Aspect (radians)')
            ax2.set_ylabel('Number of Sites')
            
            # Save plot
            output_file = os.path.join(self.output_dir, 'feature_analysis.png')
            plt.savefig(output_file)
            plt.close()
            
            return output_file
        except Exception as e:
            self.logger.error(f"Error creating feature analysis plots: {str(e)}")
            return ""

    def _create_interactive_map(self, findings: Dict[str, Any]) -> str:
        """Create an interactive map with Folium."""
        # Create base map centered on region
        center_lat = (self.region['min_lat'] + self.region['max_lat']) / 2
        center_lon = (self.region['min_lon'] + self.region['max_lon']) / 2
        
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=10,
            tiles='OpenStreetMap',
            attr='© OpenStreetMap contributors'
        )
        
        # Add satellite layer
        folium.TileLayer(
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr='© Esri',
            name='Satellite'
        ).add_to(m)
        
        # Add findings as markers
        for site in findings.get('sites', []):
            folium.Marker(
                location=[site['coordinates']['y'], site['coordinates']['x']],
                popup=f"Confidence: {site['confidence']:.2f}",
                icon=folium.Icon(color='red', icon='info-sign')
            ).add_to(m)
        
        # Save map
        map_file = os.path.join(self.output_dir, f'map_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html')
        m.save(map_file)
        
        return map_file
        
    def _create_elevation_profile_plot(self, findings: Dict[str, Any]) -> str:
        """Create elevation profile plot."""
        plt.figure(figsize=(12, 6))
        
        # Plot elevation profile
        elevations = [site['coordinates']['elevation'] for site in findings['sites']]
        confidences = [site['confidence'] for site in findings['sites']]
        
        plt.scatter(range(len(elevations)), elevations, c=confidences, cmap='viridis')
        plt.colorbar(label='Confidence')
        plt.xlabel('Site Index')
        plt.ylabel('Elevation (m)')
        plt.title('Elevation Profile of Potential Archaeological Sites')
        
        # Save plot
        output_path = os.path.join(self.output_dir, f'elevation_profile_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
        plt.savefig(output_path)
        plt.close()
        
        return output_path
        
    def _create_3d_visualization(self, findings: Dict[str, Any]) -> str:
        """Create 3D visualization using Plotly."""
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # Plot each site
        for site in findings.get('sites', []):
            ax.scatter(
                site['coordinates']['x'],
                site['coordinates']['y'],
                site['coordinates']['elevation'],
                c='r',
                marker='^'
            )
        
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        ax.set_zlabel('Elevation (m)')
        ax.set_title('3D Visualization of Archaeological Sites')
        
        # Save plot
        plot_file = os.path.join(self.output_dir, f'plot_3d_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
        plt.savefig(plot_file)
        plt.close()
        
        return plot_file
        
    def _create_summary_plots(self, findings: Dict[str, Any]) -> str:
        """Create summary plots of findings."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
        
        # Plot confidence distribution
        confidences = [site['confidence'] for site in findings.get('sites', [])]
        ax1.hist(confidences, bins=10)
        ax1.set_xlabel('Confidence Score')
        ax1.set_ylabel('Number of Sites')
        ax1.set_title('Distribution of Site Confidence Scores')
        
        # Plot elevation vs area
        elevations = [site['coordinates']['elevation'] for site in findings.get('sites', [])]
        areas = [site['area'] for site in findings.get('sites', [])]
        ax2.scatter(areas, elevations, c=confidences, cmap='viridis')
        ax2.set_xlabel('Area (m²)')
        ax2.set_ylabel('Elevation (m)')
        ax2.set_title('Site Characteristics')
        
        plt.tight_layout()
        
        # Save plot
        summary_file = os.path.join(self.output_dir, f'summary_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
        plt.savefig(summary_file)
        plt.close()
        
        return summary_file 