🗺️ Karnataka Geospatial Data & Analysis
A comprehensive repository for Karnataka-specific spatial datasets, boundary mapping, and geographic insights.

🚀 Project Overview
This project serves as a centralized hub for Karnataka Geographic Information System (K-GIS) data processing. It provides tools to fetch, clean, and visualize administrative boundaries—ranging from State and District levels down to Taluks, Hoblis, and Village-level data.

🛠 Tech Stack
Languages: Python (Jupyter Notebooks)

GIS Libraries: GeoPandas, Folium, Shapely, RGDAL

Data Formats: Shapefiles (.shp), GeoPackage (.gpkg), KMZ/KML

Analysis: Coordinate Reference Systems (CRS) transformation, Spatial Joins, and Buffer Analysis.

🏗️ Data Architecture & Pipeline
This project implements an automated pipeline to transform raw government spatial data into developer-ready formats.

<img width="6978" height="1035" alt="image" src="https://github.com/user-attachments/assets/c9df8489-4884-43bd-8a3b-c6239b2e7618" />
Layer Level,Description,Formats
📍 State,High-level Karnataka state boundary.,".gpkg, .shp"
🏙️ District,"31 District boundaries, including newly formed regions like Vijayanagara.",".gpkg, .shp"
🏢 Taluk,Sub-district administrative divisions for regional planning.,".gpkg, .shp"
🗳️ Constituencies,Assembly (AC) and Parliament (PC) electoral boundaries.,".gpkg, .shp"
🏡 Village/Hobli,Micro-level local governance boundaries for hyper-local analysis.,".gpkg, .kml"

Key Technical Features
Automated Data Fetching: Custom Python scripts to programmatically retrieve data layers from the KGIS portal.

Spatial Transformation: Automated conversion of diverse coordinate systems into standardized Web Mercator (EPSG:3857) or WGS84 (EPSG:4326).

Interactive Mapping: Integration with Leaflet/Folium to generate heatmaps and boundary overlays directly in Jupyter environments.

Topology Cleaning: Logic to handle "Sliver Polygons" and overlapping boundaries ensuring 100% geometric accuracy for urban planning.

🚦 Getting Started
Clone the repository: git clone https://github.com/nuve-ra/Karnataka-Geospatial.git

Setup Environment: ```bash pip install -r requirements.txt

Ensure GDAL/Proj4 are installed on your system
Fetch Data: Run the fetch-kgis-data.py script to populate the /data/raw directory.

Run Notebooks: Open analysis.ipynb to visualize the boundaries using Folium.

📝 Strategic Impact
By providing a cleaned, open-source version of Karnataka's geospatial data, this project enables developers and urban planners to build:

Election Result Dashboards (Constituency-level mapping).

Healthcare Accessibility Analysis (Mapping hospital reach in rural districts).

Agricultural Insights (Soil and water mapping at the Hobli level).

