# AI-Powered Archaeological Discovery in the Amazon

## 🖼️ Media Gallery (Key Visualizations)

| Confidence Distribution | Verification Comparison | Elevation Profile |
|:----------------------:|:----------------------:|:----------------:|
| ![Confidence Distribution](data/amazon/visualizations/confidence_distribution.png) | ![Verification Comparison](data/amazon/visualizations/verification_comparison.png) | ![Elevation Profile](data/amazon/visualizations/elevation_profile.png) |

| Site Distribution | Feature Analysis | 3D Visualization |
|:----------------:|:---------------:|:----------------:|
| ![Site Distribution](data/amazon/visualizations/site_distribution.png) | ![Feature Analysis](data/amazon/visualizations/feature_analysis.png) | ![3D Plot](data/amazon/visualizations/plot_3d_20250528_232819.png) |

| Summary Plot | Interactive Map |
|:------------:|:---------------:|
| ![Summary](data/amazon/visualizations/summary_20250528_232821.png) | [Interactive Site Map (HTML)](data/amazon/visualizations/site_map.html) |

---

## Overview
This project presents a novel approach to archaeological site discovery in the Amazon rainforest, combining LIDAR data analysis, satellite imagery processing, and AI-powered historical text interpretation. Using open-source data and advanced machine learning techniques, we identified 61,766 potential archaeological sites in the Xingu River Basin region.

## Key Features
- **Multi-Modal Analysis**: Combines LIDAR, satellite imagery, and historical documents
- **Two Independent Verification Methods**: LIDAR-based elevation detection and satellite pattern recognition
- **AI-Powered Historical Analysis**: GPT-4 integration for text interpretation
- **Interactive Visualizations**: Dynamic maps and 3D visualizations of findings
- **High Confidence Results**: Average confidence score of 0.65 across all sites

## Installation
1. Clone the repository:
```bash
git clone https://github.com/Cansu126/amazon-archaeology-discovery.git
cd amazon-archaeology-discovery
```

2. Create and activate virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure API keys:
- Add your OpenAI API key to `config.json`
- Add Sentinel Hub credentials if using satellite data

## Usage
1. Run the main analysis:
```bash
python scripts/main.py
```

2. View results:
- Interactive map: `data/amazon/visualizations/site_map.html`
- LIDAR evidence: `data/amazon/visualizations/lidar_evidence.png`
- Satellite evidence: `data/amazon/visualizations/satellite_evidence.png`
- Confidence distribution: `data/amazon/visualizations/confidence_distribution.png`

## Project Structure
```
amazon-archaeology-discovery/
├── scripts/
│   ├── main.py                 # Main execution script
│   ├── lidar_processing.py     # LIDAR data analysis
│   ├── satellite_processing.py # Satellite imagery analysis
│   ├── historical_analysis.py  # Historical document analysis
│   └── visualization.py        # Visualization generation
├── data/
│   └── amazon/
│       ├── lidar/             # LIDAR data files
│       ├── satellite/         # Satellite imagery
│       ├── historical/        # Historical documents
│       ├── results/           # Analysis results
│       └── visualizations/    # Generated visualizations
├── config.json                # Configuration file
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Methodology
1. **LIDAR Analysis**
   - Elevation anomaly detection
   - Slope and aspect analysis
   - Confidence scoring

2. **Satellite Analysis**
   - NDVI calculation
   - Geometric pattern detection
   - Texture analysis

3. **Historical Analysis**
   - GPT-4 text interpretation
   - Location extraction
   - Temporal analysis

## Results
- Total sites identified: 61,766
- Key discoveries:
  1. Large Settlement Complex (-12.5°N, -53.5°W)
  2. Agricultural Terraces (-12.3°N, -53.7°W)
  3. Ritual Center (-12.4°N, -53.6°W)

## Future Work
1. Ground verification with local archaeologists
2. High-resolution LIDAR survey of key sites
3. Expanded historical document analysis
4. Integration with indigenous knowledge

## References
1. SRTM Data: USGS Earth Explorer
2. Satellite Imagery: Copernicus Open Access Hub
3. Historical Documents: Brazilian National Library
4. Archaeological Surveys: FUNAI Archives

## License
MIT License - See LICENSE file for details

## Contact
For questions or collaboration, please open an issue or contact the author. 