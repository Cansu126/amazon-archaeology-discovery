#!/usr/bin/env python3
"""
Performance optimization module for the AI-Powered Archaeological Discovery pipeline.
Provides caching, parallel processing, and memory optimization utilities.
"""

import os
import logging
import numpy as np
from functools import lru_cache
from concurrent.futures import ProcessPoolExecutor
from typing import List, Dict, Any, Callable
import psutil
import gc

logger = logging.getLogger(__name__)

class PipelineOptimizer:
    def __init__(self, config: Dict[str, Any]):
        """Initialize pipeline optimizer with configuration."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.cache_dir = os.path.join(config.get('output_directories', {}).get('results', 'data/amazon/results'), 'cache')
        os.makedirs(self.cache_dir, exist_ok=True)

    @lru_cache(maxsize=128)
    def cached_processing(self, func: Callable, *args, **kwargs) -> Any:
        """Cache processing results to avoid redundant computations."""
        return func(*args, **kwargs)

    def parallel_process(self, func: Callable, data_chunks: List[Any], 
                        max_workers: int = None) -> List[Any]:
        """Process data chunks in parallel using multiple CPU cores."""
        if max_workers is None:
            max_workers = psutil.cpu_count(logical=False)
        
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(func, data_chunks))
        
        return results

    def optimize_memory(self):
        """Optimize memory usage by cleaning up unused resources."""
        gc.collect()
        if hasattr(np, 'clear_memory'):
            np.clear_memory()

    def chunk_data(self, data: np.ndarray, chunk_size: int = 1000) -> List[np.ndarray]:
        """Split large datasets into manageable chunks."""
        return np.array_split(data, max(1, len(data) // chunk_size))

    def monitor_resources(self) -> Dict[str, float]:
        """Monitor system resources usage."""
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            'cpu_percent': process.cpu_percent(),
            'memory_percent': process.memory_percent(),
            'memory_used': memory_info.rss / 1024 / 1024,  # MB
            'disk_usage': psutil.disk_usage('/').percent
        }

    def optimize_visualization(self, data: np.ndarray) -> np.ndarray:
        """Optimize data for visualization by reducing resolution if needed."""
        if data.size > 1e6:  # If data is too large
            scale_factor = int(np.sqrt(data.size / 1e6))
            return data[::scale_factor, ::scale_factor]
        return data

    def save_optimized_data(self, data: Any, filename: str):
        """Save optimized data to cache."""
        cache_path = os.path.join(self.cache_dir, filename)
        np.save(cache_path, data)

    def load_optimized_data(self, filename: str) -> Any:
        """Load optimized data from cache."""
        cache_path = os.path.join(self.cache_dir, filename)
        if os.path.exists(cache_path):
            return np.load(cache_path)
        return None

def optimize_pipeline(config: Dict[str, Any]):
    """Apply optimizations to the entire pipeline."""
    optimizer = PipelineOptimizer(config)
    
    # Monitor initial resource usage
    initial_resources = optimizer.monitor_resources()
    logger.info(f"Initial resource usage: {initial_resources}")
    
    # Optimize memory
    optimizer.optimize_memory()
    
    # Monitor final resource usage
    final_resources = optimizer.monitor_resources()
    logger.info(f"Final resource usage: {final_resources}")
    
    return optimizer 