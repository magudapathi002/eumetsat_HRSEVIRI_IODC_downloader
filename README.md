# EUMETSAT HRSEVIRI IODC Downloader

A Python application that automatically downloads and processes EUMETSAT's High Rate SEVIRI (Indian Ocean Data Coverage) satellite data to generate cloud cover and rainfall probability visualizations for India, with a special focus on Tamil Nadu.

## Features

- Automatic downloading of latest HRSEVIRI-IODC satellite data from EUMETSAT
- Processing of raw .nat files into PNG visualizations
- Generation of two types of visualizations:
  1. Full India cloud cover map
  2. Detailed Tamil Nadu regional map with district boundaries
- Scheduled execution every 15 minutes for near real-time monitoring
- Cloud top temperature analysis for rainfall probability estimation
- Integration with GADM administrative boundary data

## Requirements

- Python 3.x
- EUMETSAT account credentials
- Required Python packages (see [Installation](#installation))

## Installation

1. Clone the repository:
```bash
git clone https://github.com/magudapathi002/eumetsat_HRSEVIRI_IODC_downloader.git
cd eumetsat_HRSEVIRI_IODC_downloader
```

2. Install required Python packages:
```bash
pip install -r requirements.txt
```

The following dependencies will be installed:
- eumdac - EUMETSAT Data Access Client
- satpy - Satellite data processing
- matplotlib - Plotting and visualization
- numpy - Numerical computations
- cartopy - Geospatial data processing
- apscheduler - Task scheduling

## Configuration

1. Create a `.env` file in the project root (you can copy from `.env.example`):
```bash
cp .env.example .env
```

2. Add your EUMETSAT credentials to the `.env` file:
```
EUMETSAT_KEY=your_key_here
EUMETSAT_SECRET=your_secret_here
```

The application uses the following directory structure:
- `input/` - Downloaded satellite data
- `frames/` - Generated visualizations for all India
- `output/frame_2/` - Generated visualizations for Tamil Nadu
- `data/gadm41_IND_shp/` - GADM shapefile data for India

## Usage

Run the application:
```bash
python main.py
```

The application will:
1. Start a scheduler that runs every 15 minutes
2. Check for the latest HRSEVIRI-IODC product
3. Download new data if available
4. Process the data and generate visualizations:
   - Full India cloud cover map showing areas with cloud top temperatures below 273.15K
   - Detailed Tamil Nadu map with district boundaries and cloud coverage
5. Save the visualizations in the specified output directories

### Visualization Details

The generated maps include:
- Cloud top temperature visualization (200K to 273.15K)
- Color-coded rainfall probability indicators
- State/district boundaries
- Timestamp in IST (Indian Standard Time)
- Temperature-based rainfall likelihood scale:
  - Below 230K: Heavy rain, very likely
  - Around 235K: Moderate rain
  - Above 265K: Little/no rain

## Project Structure

```
eumetsat_downloader/
├── config/
│   └── settings.py         # Configuration settings
├── downloader/
│   ├── eumdac_client.py   # EUMETSAT data download
│   └── file_manager.py    # File handling utilities
├── processor/
│   └── satpy_to_png.py    # Data processing and visualization
├── scheduler/
│   └── jobs.py            # Scheduling utilities
├── data/
│   └── gadm41_IND_shp/    # GADM shapefiles for India
├── .env.example           # Example environment variables
├── main.py               # Application entry point
└── requirements.txt      # Python dependencies
```

## Region Coverage

- Primary Coverage: India (Bounds: 68°E-98°E, 6°N-38°N)
- Detailed Coverage: Tamil Nadu with district-level visualization
