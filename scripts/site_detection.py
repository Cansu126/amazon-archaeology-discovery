import logging
from typing import Dict, Any
from data_fusion import DataFusion

logger = logging.getLogger(__name__)

def detect_sites(lidar_results: Dict[str, Any], satellite_results: Dict[str, Any], historical_results: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fuse LIDAR, satellite, and historical results into a unified site list.
    """
    logger.info("Fusing LIDAR, satellite, and historical results into unified site list.")
    fusion = DataFusion(config)
    fused = fusion.fuse_data({
        'lidar': lidar_results,
        'satellite': satellite_results,
        'historical': historical_results
    })
    logger.info(f"Total sites after fusion: {len(fused['sites'])}")
    return fused 