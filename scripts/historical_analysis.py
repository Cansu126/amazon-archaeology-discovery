import os
import logging
import json
from typing import Dict, Any, List
import openai
from datetime import datetime

logger = logging.getLogger(__name__)

class HistoricalAnalyzer:
    def __init__(self, config: Dict[str, Any]):
        """Initialize historical analyzer with configuration."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        openai.api_key = config.get('openai_api_key', os.getenv('OPENAI_API_KEY'))
        logger.info("Historical analyzer initialized")

    def analyze_historical_data(self, historical_path: str) -> Dict[str, Any]:
        """Analyze historical documents and maps for archaeological insights."""
        self.logger.info(f"Analyzing historical data from: {historical_path}")
        
        findings = {
            'sites': [],
            'metadata': {
                'source': 'Historical Documents',
                'region': 'Amazon',
                'analysis_method': 'AI-Powered Text Analysis'
            }
        }

        try:
            # Process historical documents
            documents = self._load_historical_documents(historical_path)
            
            # Analyze each document
            for doc in documents:
                # Extract location mentions using OpenAI
                locations = self._extract_locations(doc['content'])
                
                # Analyze historical context
                context = self._analyze_historical_context(doc['content'])
                
                # Cross-reference with known sites
                for location in locations:
                    if self._verify_historical_mention(location, context):
                        site = {
                            'type': 'potential_archaeological_site',
                            'coordinates': {
                                'x': float(location['longitude']),
                                'y': float(location['latitude']),
                                'elevation': float(location.get('elevation', 0))
                            },
                            'confidence': location['confidence'],
                            'features': {
                                'historical_context': context['summary'],
                                'time_period': context['time_period'],
                                'cultural_significance': context['significance']
                            },
                            'verification_method': 'historical_text_analysis'
                        }
                        findings['sites'].append(site)

            self.logger.info(f"Found {len(findings['sites'])} potential sites from historical analysis")
            return findings

        except Exception as e:
            self.logger.error(f"Error analyzing historical data: {str(e)}")
            return findings

    def _load_historical_documents(self, path: str) -> List[Dict[str, Any]]:
        """Load and preprocess historical documents."""
        documents = []
        
        # Load colonial diaries
        diary_path = os.path.join(path, 'colonial_diaries')
        if os.path.exists(diary_path):
            for file in os.listdir(diary_path):
                if file.endswith('.txt'):
                    with open(os.path.join(diary_path, file), 'r', encoding='utf-8') as f:
                        documents.append({
                            'type': 'colonial_diary',
                            'content': f.read(),
                            'date': self._extract_date(file)
                        })
        
        # Load indigenous oral maps
        map_path = os.path.join(path, 'indigenous_maps')
        if os.path.exists(map_path):
            for file in os.listdir(map_path):
                if file.endswith('.json'):
                    with open(os.path.join(map_path, file), 'r', encoding='utf-8') as f:
                        documents.append({
                            'type': 'indigenous_map',
                            'content': json.load(f),
                            'date': self._extract_date(file)
                        })
        
        return documents

    def _extract_locations(self, content: str) -> List[Dict[str, Any]]:
        """Extract location mentions from text using OpenAI."""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert in historical geography and archaeology. Extract potential archaeological site locations from the following text. For each location, provide coordinates, confidence level, and brief description."},
                    {"role": "user", "content": content}
                ]
            )
            
            # Parse the response to extract locations
            locations = []
            for line in response.choices[0].message.content.split('\n'):
                if 'latitude' in line and 'longitude' in line:
                    try:
                        # Extract coordinates and confidence
                        lat = float(line.split('latitude:')[1].split(',')[0].strip())
                        lon = float(line.split('longitude:')[1].split(',')[0].strip())
                        conf = float(line.split('confidence:')[1].split(',')[0].strip())
                        
                        locations.append({
                            'latitude': lat,
                            'longitude': lon,
                            'confidence': conf,
                            'description': line.split('description:')[1].strip() if 'description:' in line else ''
                        })
                    except:
                        continue
            
            return locations
            
        except Exception as e:
            self.logger.error(f"Error extracting locations: {str(e)}")
            return []

    def _analyze_historical_context(self, content: str) -> Dict[str, Any]:
        """Analyze historical context using OpenAI."""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert in Amazonian archaeology. Analyze the following text for historical context, time period, and cultural significance."},
                    {"role": "user", "content": content}
                ]
            )
            
            # Parse the response
            analysis = response.choices[0].message.content
            
            return {
                'summary': analysis,
                'time_period': self._extract_time_period(analysis),
                'significance': self._extract_significance(analysis)
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing historical context: {str(e)}")
            return {
                'summary': '',
                'time_period': 'unknown',
                'significance': 'unknown'
            }

    def _verify_historical_mention(self, location: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Verify if a historical mention is likely to be an archaeological site."""
        # Combine multiple factors for verification
        verification_score = (
            location['confidence'] * 0.4 +  # Location confidence
            self._score_time_period(context['time_period']) * 0.3 +  # Time period relevance
            self._score_significance(context['significance']) * 0.3  # Cultural significance
        )
        
        return verification_score > 0.6

    def _extract_date(self, filename: str) -> str:
        """Extract date from filename."""
        try:
            # Look for date pattern in filename
            date_str = filename.split('_')[-1].split('.')[0]
            return datetime.strptime(date_str, '%Y%m%d').strftime('%Y-%m-%d')
        except:
            return 'unknown'

    def _extract_time_period(self, analysis: str) -> str:
        """Extract time period from analysis."""
        # Simple keyword matching
        if 'pre-colonial' in analysis.lower():
            return 'pre-colonial'
        elif 'colonial' in analysis.lower():
            return 'colonial'
        elif 'modern' in analysis.lower():
            return 'modern'
        return 'unknown'

    def _extract_significance(self, analysis: str) -> str:
        """Extract cultural significance from analysis."""
        # Simple keyword matching
        if 'major' in analysis.lower() or 'significant' in analysis.lower():
            return 'high'
        elif 'minor' in analysis.lower() or 'small' in analysis.lower():
            return 'low'
        return 'medium'

    def _score_time_period(self, period: str) -> float:
        """Score time period relevance."""
        scores = {
            'pre-colonial': 0.9,
            'colonial': 0.7,
            'modern': 0.3,
            'unknown': 0.5
        }
        return scores.get(period, 0.5)

    def _score_significance(self, significance: str) -> float:
        """Score cultural significance."""
        scores = {
            'high': 0.9,
            'medium': 0.6,
            'low': 0.3
        }
        return scores.get(significance, 0.5) 