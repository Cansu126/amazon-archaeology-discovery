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

    def _create_temporal_analysis(self, findings: Dict[str, Any]) -> str:
        """Create temporal analysis visualization showing potential age distribution of sites."""
        try:
            # Extract temporal indicators
            temporal_data = []
            for site in findings['sites']:
                if 'temporal_indicators' in site:
                    temporal_data.append({
                        'age_estimate': site['temporal_indicators'].get('estimated_age', 0),
                        'confidence': site['confidence'],
                        'location': [site['coordinates']['x'], site['coordinates']['y']]
                    })
            
            # Create figure
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # Age distribution plot
            ages = [d['age_estimate'] for d in temporal_data]
            ax1.hist(ages, bins=20, alpha=0.7)
            ax1.set_title('Estimated Age Distribution of Sites')
            ax1.set_xlabel('Estimated Age (years)')
            ax1.set_ylabel('Number of Sites')
            
            # Age vs Confidence scatter
            ax2.scatter(ages, [d['confidence'] for d in temporal_data], alpha=0.6)
            ax2.set_title('Age Estimate vs Confidence')
            ax2.set_xlabel('Estimated Age (years)')
            ax2.set_ylabel('Confidence Score')
            
            plt.tight_layout()
            
            # Save plot
            output_file = os.path.join(self.output_dir, 'temporal_analysis.png')
            plt.savefig(output_file)
            plt.close()
            
            return output_file
        except Exception as e:
            self.logger.error(f"Error creating temporal analysis: {str(e)}")
            return ""

    def _create_detailed_confidence_analysis(self, findings: Dict[str, Any]) -> str:
        """Create detailed confidence analysis visualization."""
        try:
            # Extract confidence data
            confidence_data = []
            for site in findings['sites']:
                confidence_data.append({
                    'overall': site['confidence'],
                    'lidar': site.get('verification_scores', {}).get('lidar', 0),
                    'satellite': site.get('verification_scores', {}).get('satellite', 0),
                    'historical': site.get('verification_scores', {}).get('historical', 0)
                })
            
            # Create figure
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
            
            # Overall confidence distribution
            ax1.hist([d['overall'] for d in confidence_data], bins=20, alpha=0.7)
            ax1.set_title('Overall Confidence Distribution')
            ax1.set_xlabel('Confidence Score')
            ax1.set_ylabel('Number of Sites')
            
            # Method-specific confidence distributions
            ax2.hist([d['lidar'] for d in confidence_data], bins=20, alpha=0.7, label='LIDAR')
            ax2.hist([d['satellite'] for d in confidence_data], bins=20, alpha=0.7, label='Satellite')
            ax2.set_title('Method-Specific Confidence Distribution')
            ax2.set_xlabel('Confidence Score')
            ax2.set_ylabel('Number of Sites')
            ax2.legend()
            
            # Confidence correlation
            ax3.scatter([d['lidar'] for d in confidence_data], 
                       [d['satellite'] for d in confidence_data], 
                       alpha=0.6)
            ax3.set_title('LIDAR vs Satellite Confidence Correlation')
            ax3.set_xlabel('LIDAR Confidence')
            ax3.set_ylabel('Satellite Confidence')
            
            # Confidence heatmap
            confidence_matrix = np.array([[d['lidar'], d['satellite'], d['historical']] 
                                        for d in confidence_data])
            im = ax4.imshow(confidence_matrix.mean(axis=0).reshape(1, -1), 
                          cmap='viridis', aspect='auto')
            ax4.set_title('Average Confidence by Method')
            ax4.set_xticks([0, 1, 2])
            ax4.set_xticklabels(['LIDAR', 'Satellite', 'Historical'])
            plt.colorbar(im, ax=ax4)
            
            plt.tight_layout()
            
            # Save plot
            output_file = os.path.join(self.output_dir, 'detailed_confidence_analysis.png')
            plt.savefig(output_file)
            plt.close()
            
            return output_file
        except Exception as e:
            self.logger.error(f"Error creating detailed confidence analysis: {str(e)}")
            return ""

    def _create_discovery_case_studies(self, findings: Dict[str, Any]) -> str:
        """Create detailed case study visualizations for 2-3 significant discoveries."""
        try:
            # Select top 3 discoveries by confidence
            top_sites = sorted(findings['sites'], 
                             key=lambda x: x['confidence'], 
                             reverse=True)[:3]
            
            # Create figure for each case study
            for i, site in enumerate(top_sites):
                fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
                
                # LIDAR evidence
                if 'lidar_evidence' in site:
                    ax1.imshow(site['lidar_evidence'], cmap='terrain')
                    ax1.set_title('LIDAR Evidence')
                    ax1.axis('off')
                
                # Satellite evidence
                if 'satellite_evidence' in site:
                    ax2.imshow(site['satellite_evidence'])
                    ax2.set_title('Satellite Evidence')
                    ax2.axis('off')
                
                # Feature analysis
                if 'features' in site:
                    features = site['features']
                    ax3.bar(features.keys(), features.values())
                    ax3.set_title('Site Features')
                    ax3.tick_params(axis='x', rotation=45)
                
                # Confidence breakdown
                if 'verification_scores' in site:
                    scores = site['verification_scores']
                    ax4.bar(scores.keys(), scores.values())
                    ax4.set_title('Verification Scores')
                    ax4.tick_params(axis='x', rotation=45)
                
                plt.tight_layout()
                
                # Save plot
                output_file = os.path.join(self.output_dir, f'case_study_{i+1}.png')
                plt.savefig(output_file)
                plt.close()
            
            return "Case studies generated successfully"
        except Exception as e:
            self.logger.error(f"Error creating discovery case studies: {str(e)}")
            return ""

    def _create_detailed_confidence_intervals(self, findings: Dict[str, Any]) -> str:
        """Create detailed confidence interval analysis with statistical validation."""
        try:
            # Extract confidence data with method-specific scores
            confidence_data = []
            for site in findings['sites']:
                confidence_data.append({
                    'overall': site['confidence'],
                    'lidar': site.get('verification_scores', {}).get('lidar', 0),
                    'satellite': site.get('verification_scores', {}).get('satellite', 0),
                    'historical': site.get('verification_scores', {}).get('historical', 0),
                    'indigenous': site.get('verification_scores', {}).get('indigenous', 0),
                    'temporal': site.get('verification_scores', {}).get('temporal', 0)
                })
            
            # Create figure
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
            
            # Confidence intervals by method
            methods = ['LIDAR', 'Satellite', 'Historical', 'Indigenous', 'Temporal']
            data = np.array([[d['lidar'], d['satellite'], d['historical'], 
                            d['indigenous'], d['temporal']] for d in confidence_data])
            
            # Calculate confidence intervals (95%)
            means = np.mean(data, axis=0)
            stds = np.std(data, axis=0)
            ci = 1.96 * stds / np.sqrt(len(data))
            
            # Plot confidence intervals
            ax1.errorbar(methods, means, yerr=ci, fmt='o', capsize=5)
            ax1.set_title('95% Confidence Intervals by Method')
            ax1.set_ylabel('Confidence Score')
            ax1.grid(True, alpha=0.3)
            
            # Method correlation matrix
            corr_matrix = np.corrcoef(data.T)
            im = ax2.imshow(corr_matrix, cmap='coolwarm')
            ax2.set_xticks(range(len(methods)))
            ax2.set_yticks(range(len(methods)))
            ax2.set_xticklabels(methods, rotation=45)
            ax2.set_yticklabels(methods)
            plt.colorbar(im, ax=ax2)
            ax2.set_title('Method Correlation Matrix')
            
            # Confidence distribution by site type
            site_types = set(site.get('type', 'Unknown') for site in findings['sites'])
            type_confidences = {t: [] for t in site_types}
            
            for site in findings['sites']:
                site_type = site.get('type', 'Unknown')
                type_confidences[site_type].append(site['confidence'])
            
            # Box plot of confidence by site type
            ax3.boxplot([type_confidences[t] for t in site_types], 
                       labels=list(site_types))
            ax3.set_title('Confidence Distribution by Site Type')
            ax3.set_ylabel('Confidence Score')
            ax3.tick_params(axis='x', rotation=45)
            
            # Statistical summary
            stats_text = f"""
            Statistical Summary:
            Total Sites: {len(findings['sites'])}
            Mean Confidence: {np.mean([d['overall'] for d in confidence_data]):.3f}
            Std Dev: {np.std([d['overall'] for d in confidence_data]):.3f}
            Min Confidence: {min([d['overall'] for d in confidence_data]):.3f}
            Max Confidence: {max([d['overall'] for d in confidence_data]):.3f}
            """
            ax4.text(0.1, 0.5, stats_text, fontsize=10)
            ax4.axis('off')
            
            plt.tight_layout()
            
            # Save plot
            output_file = os.path.join(self.output_dir, 'detailed_confidence_intervals.png')
            plt.savefig(output_file)
            plt.close()
            
            return output_file
        except Exception as e:
            self.logger.error(f"Error creating detailed confidence intervals: {str(e)}")
            return ""

    def _create_indigenous_knowledge_visualization(self, findings: Dict[str, Any]) -> str:
        """Create visualization integrating indigenous knowledge and traditional data."""
        try:
            # Extract indigenous knowledge data
            indigenous_data = []
            for site in findings['sites']:
                if 'indigenous_knowledge' in site:
                    indigenous_data.append({
                        'site': site,
                        'knowledge': site['indigenous_knowledge'],
                        'confidence': site['confidence']
                    })
            
            # Create figure
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
            
            # Indigenous knowledge sources
            sources = {}
            for data in indigenous_data:
                for source in data['knowledge'].get('sources', []):
                    sources[source] = sources.get(source, 0) + 1
            
            # Plot knowledge sources
            ax1.bar(sources.keys(), sources.values())
            ax1.set_title('Indigenous Knowledge Sources')
            ax1.tick_params(axis='x', rotation=45)
            
            # Knowledge type distribution
            knowledge_types = {}
            for data in indigenous_data:
                for k_type in data['knowledge'].get('types', []):
                    knowledge_types[k_type] = knowledge_types.get(k_type, 0) + 1
            
            # Plot knowledge types
            ax2.pie(knowledge_types.values(), labels=knowledge_types.keys(), autopct='%1.1f%%')
            ax2.set_title('Types of Indigenous Knowledge')
            
            # Confidence vs Indigenous Knowledge
            confidences = [d['confidence'] for d in indigenous_data]
            knowledge_scores = [len(d['knowledge'].get('sources', [])) for d in indigenous_data]
            ax3.scatter(knowledge_scores, confidences)
            ax3.set_title('Confidence vs Indigenous Knowledge Support')
            ax3.set_xlabel('Number of Indigenous Sources')
            ax3.set_ylabel('Confidence Score')
            
            # Timeline of indigenous knowledge
            if 'timeline' in indigenous_data[0]['knowledge']:
                timeline = indigenous_data[0]['knowledge']['timeline']
                ax4.plot(timeline['dates'], timeline['events'], 'o-')
                ax4.set_title('Indigenous Knowledge Timeline')
                ax4.tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            
            # Save plot
            output_file = os.path.join(self.output_dir, 'indigenous_knowledge_analysis.png')
            plt.savefig(output_file)
            plt.close()
            
            return output_file
        except Exception as e:
            self.logger.error(f"Error creating indigenous knowledge visualization: {str(e)}")
            return ""

    def _create_temporal_development_analysis(self, findings: Dict[str, Any]) -> str:
        """Create analysis of historical development and periods of use."""
        try:
            # Extract temporal data
            temporal_data = []
            for site in findings['sites']:
                if 'temporal_indicators' in site:
                    temporal_data.append({
                        'site': site,
                        'age': site['temporal_indicators'].get('estimated_age', 0),
                        'period': site['temporal_indicators'].get('period', 'Unknown'),
                        'confidence': site['confidence']
                    })
            
            # Create figure
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
            
            # Age distribution by period
            periods = set(d['period'] for d in temporal_data)
            period_data = {p: [] for p in periods}
            
            for data in temporal_data:
                period_data[data['period']].append(data['age'])
            
            # Box plot of ages by period
            ax1.boxplot([period_data[p] for p in periods], labels=list(periods))
            ax1.set_title('Age Distribution by Period')
            ax1.set_ylabel('Estimated Age (years)')
            ax1.tick_params(axis='x', rotation=45)
            
            # Temporal development map
            if 'temporal_development' in findings:
                development = findings['temporal_development']
                ax2.plot(development['dates'], development['sites'], 'o-')
                ax2.set_title('Temporal Development of Sites')
                ax2.set_xlabel('Time Period')
                ax2.set_ylabel('Number of Sites')
                ax2.tick_params(axis='x', rotation=45)
            
            # Period confidence analysis
            period_confidences = {p: [] for p in periods}
            for data in temporal_data:
                period_confidences[data['period']].append(data['confidence'])
            
            # Box plot of confidence by period
            ax3.boxplot([period_confidences[p] for p in periods], labels=list(periods))
            ax3.set_title('Confidence Distribution by Period')
            ax3.set_ylabel('Confidence Score')
            ax3.tick_params(axis='x', rotation=45)
            
            # Period overlap analysis
            if 'period_overlap' in findings:
                overlap = findings['period_overlap']
                im = ax4.imshow(overlap['matrix'], cmap='viridis')
                ax4.set_xticks(range(len(periods)))
                ax4.set_yticks(range(len(periods)))
                ax4.set_xticklabels(list(periods), rotation=45)
                ax4.set_yticklabels(list(periods))
                plt.colorbar(im, ax=ax4)
                ax4.set_title('Period Overlap Analysis')
            
            plt.tight_layout()
            
            # Save plot
            output_file = os.path.join(self.output_dir, 'temporal_development_analysis.png')
            plt.savefig(output_file)
            plt.close()
            
            return output_file
        except Exception as e:
            self.logger.error(f"Error creating temporal development analysis: {str(e)}")
            return ""

    def _create_known_site_comparison(self, findings: Dict[str, Any]) -> str:
        """Create detailed comparison with known archaeological sites."""
        try:
            # Extract comparison data
            comparison_data = []
            for site in findings['sites']:
                if 'known_site_comparison' in site:
                    comparison_data.append({
                        'site': site,
                        'comparison': site['known_site_comparison'],
                        'confidence': site['confidence']
                    })
            
            # Create figure
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
            
            # Feature comparison
            features = set()
            for data in comparison_data:
                features.update(data['comparison'].get('features', {}).keys())
            
            feature_similarities = {f: [] for f in features}
            for data in comparison_data:
                for feature in features:
                    similarity = data['comparison'].get('features', {}).get(feature, 0)
                    feature_similarities[feature].append(similarity)
            
            # Box plot of feature similarities
            ax1.boxplot([feature_similarities[f] for f in features], labels=list(features))
            ax1.set_title('Feature Similarity with Known Sites')
            ax1.set_ylabel('Similarity Score')
            ax1.tick_params(axis='x', rotation=45)
            
            # Overall similarity distribution
            similarities = [data['comparison'].get('overall_similarity', 0) 
                          for data in comparison_data]
            ax2.hist(similarities, bins=20)
            ax2.set_title('Overall Similarity Distribution')
            ax2.set_xlabel('Similarity Score')
            ax2.set_ylabel('Number of Sites')
            
            # Similarity vs Confidence
            ax3.scatter(similarities, [d['confidence'] for d in comparison_data])
            ax3.set_title('Similarity vs Confidence')
            ax3.set_xlabel('Similarity Score')
            ax3.set_ylabel('Confidence Score')
            
            # Known site types
            known_types = {}
            for data in comparison_data:
                k_type = data['comparison'].get('known_site_type', 'Unknown')
                known_types[k_type] = known_types.get(k_type, 0) + 1
            
            # Plot known site types
            ax4.pie(known_types.values(), labels=known_types.keys(), autopct='%1.1f%%')
            ax4.set_title('Distribution of Known Site Types')
            
            plt.tight_layout()
            
            # Save plot
            output_file = os.path.join(self.output_dir, 'known_site_comparison.png')
            plt.savefig(output_file)
            plt.close()
            
            return output_file
        except Exception as e:
            self.logger.error(f"Error creating known site comparison: {str(e)}")
            return "" 