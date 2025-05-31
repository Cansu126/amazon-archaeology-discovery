import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ConfigLoader:
    def __init__(self, config_path: str):
        """Initialize the config loader with the path to the config file."""
        self.config_path = config_path
        logger.info(f"Config loader initialized with path: {config_path}")
        
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            logger.info("Configuration loaded successfully")
            return config
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            # Return default configuration
            return {
                "data_paths": {
                    "lidar": "data/sample/lidar",
                    "satellite": "data/sample/satellite",
                    "historical": "data/sample/historical"
                },
                "output_directories": {
                    "results": "results",
                    "visualizations": "results/visualizations"
                }
            } 