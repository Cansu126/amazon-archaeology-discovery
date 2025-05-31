import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class DataFusion:
    def __init__(self, config: Dict[str, Any]):
        """Initialize the data fusion system with configuration."""
        self.config = config
        logger.info("Data fusion system initialized")
        
    def fuse_data(self, data_sources: Dict[str, Any]) -> Dict[str, Any]:
        """Fuse data from multiple sources."""
        logger.info("Fusing data from multiple sources")
        all_sites: List[Dict[str, Any]] = []
        for source_name, source_data in data_sources.items():
            # Each source_data should be a dict with a 'sites' key (for lidar, satellite, historical)
            if isinstance(source_data, dict) and 'sites' in source_data:
                all_sites.extend(source_data['sites'])
            # If the data is a list (for sources that return a list of sites)
            elif isinstance(source_data, list):
                all_sites.extend(source_data)
        return {'sites': all_sites, 'metadata': {'sources': list(data_sources.keys())}} 