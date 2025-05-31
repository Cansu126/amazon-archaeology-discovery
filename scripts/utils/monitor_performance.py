#!/usr/bin/env python3
"""
Performance monitoring script for the AI-Powered Archaeological Discovery pipeline.
Monitors and logs system resources, processing times, and memory usage.
"""

import os
import time
import logging
import psutil
import numpy as np
from datetime import datetime
from typing import Dict, Any, List
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    def __init__(self, config: Dict[str, Any]):
        """Initialize performance monitor with configuration."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.metrics = []
        self.start_time = None
        self.log_dir = Path(config.get('output_directories', {}).get('logs', 'data/amazon/logs'))
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def start_monitoring(self):
        """Start performance monitoring."""
        self.start_time = time.time()
        self.logger.info("Performance monitoring started")

    def record_metrics(self, stage: str, additional_metrics: Dict[str, Any] = None):
        """Record performance metrics for a processing stage."""
        if self.start_time is None:
            self.start_monitoring()

        current_time = time.time()
        elapsed_time = current_time - self.start_time

        process = psutil.Process()
        memory_info = process.memory_info()

        metrics = {
            'timestamp': datetime.now().isoformat(),
            'stage': stage,
            'elapsed_time': elapsed_time,
            'cpu_percent': process.cpu_percent(),
            'memory_percent': process.memory_percent(),
            'memory_used_mb': memory_info.rss / 1024 / 1024,
            'disk_usage_percent': psutil.disk_usage('/').percent
        }

        if additional_metrics:
            metrics.update(additional_metrics)

        self.metrics.append(metrics)
        self.logger.info(f"Performance metrics recorded for stage: {stage}")

    def generate_report(self) -> Dict[str, Any]:
        """Generate a performance report."""
        if not self.metrics:
            return {}

        report = {
            'summary': {
                'total_stages': len(self.metrics),
                'total_time': self.metrics[-1]['elapsed_time'],
                'max_memory_used': max(m['memory_used_mb'] for m in self.metrics),
                'avg_cpu_usage': np.mean([m['cpu_percent'] for m in self.metrics])
            },
            'stages': self.metrics
        }

        return report

    def save_report(self):
        """Save performance report to file."""
        report = self.generate_report()
        if not report:
            return

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = self.log_dir / f'performance_report_{timestamp}.json'

        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        self.logger.info(f"Performance report saved to {report_path}")

    def plot_metrics(self):
        """Generate and save performance plots."""
        try:
            import matplotlib.pyplot as plt
            import seaborn as sns

            # Set style
            sns.set_style('whitegrid')
            plt.figure(figsize=(15, 10))

            # Plot memory usage
            plt.subplot(2, 1, 1)
            times = [m['elapsed_time'] for m in self.metrics]
            memory = [m['memory_used_mb'] for m in self.metrics]
            plt.plot(times, memory, 'b-', label='Memory Usage (MB)')
            plt.xlabel('Time (seconds)')
            plt.ylabel('Memory (MB)')
            plt.title('Memory Usage Over Time')
            plt.legend()

            # Plot CPU usage
            plt.subplot(2, 1, 2)
            cpu = [m['cpu_percent'] for m in self.metrics]
            plt.plot(times, cpu, 'r-', label='CPU Usage (%)')
            plt.xlabel('Time (seconds)')
            plt.ylabel('CPU (%)')
            plt.title('CPU Usage Over Time')
            plt.legend()

            # Save plot
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            plot_path = self.log_dir / f'performance_plot_{timestamp}.png'
            plt.savefig(plot_path)
            plt.close()

            self.logger.info(f"Performance plots saved to {plot_path}")

        except ImportError:
            self.logger.warning("Matplotlib or Seaborn not available for plotting")

def monitor_pipeline(config: Dict[str, Any]) -> PerformanceMonitor:
    """Create and return a performance monitor for the pipeline."""
    monitor = PerformanceMonitor(config)
    monitor.start_monitoring()
    return monitor 