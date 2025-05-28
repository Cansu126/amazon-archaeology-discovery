#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name="archaeological-site-analysis",
    version="0.1.0",
    description="Archaeological Site Analysis System",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.21.0",
        "matplotlib>=3.4.0",
        "opencv-python>=4.5.0",
        "scikit-image>=0.18.0",
        "pytest>=6.2.0",
        "pytest-cov>=2.12.0",
        "pylint>=2.8.0",
        "black>=21.5b2",
        "mypy>=0.910",
        "pyyaml>=6.0",
        "python-dateutil>=2.8.2",
        "tqdm>=4.62.0",
        "pandas>=1.3.0",
        "scipy>=1.7.0",
        "pillow>=8.3.0",
        "shapely>=1.8.0",
        "geopandas>=0.9.0",
        "rasterio>=1.2.0",
        "pyproj>=3.1.0"
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "archaeo-analyze=scripts.main:main",
            "archaeo-generate-data=scripts.generate_sample_data:main"
        ]
    }
) 