# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel, Field
# from typing import Any, Dict

# from satellite_engine import analyze_farm_polygon

# app = FastAPI(
#     title="VyomDrishti API",
#     description="Tri-Satellite (Resourcesat-2A + EOS-04 + NISAR) Crop Health & Soil Moisture Engine",
#     version="2.0.0",
# )

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# SATELLITE_CATALOG = [
#     {
#         "id": "resourcesat-2a",
#         "name": "Resourcesat-2A",
#         "full_form": "Indian Remote Sensing Satellite — Resourcesat-2A",
#         "badge": "OPTICAL MULTISPECTRAL",
#         "accent_color": "#10b981",
#         "agency": "ISRO (Indian Space Research Organisation)",
#         "launch_date": "December 7, 2016 (PSLV-C36 from Sriharikota)",
#         "orbit": "Sun-Synchronous Polar Orbit (817 km altitude)",
#         "objectives": [
#             "Ensure continuity of global and national multispectral land and water resource monitoring.",
#             "Provide high-radiometry visible, near-infrared (NIR), and short-wave infrared (SWIR) imagery for crop acreage and vegetation vigor estimation.",
#         ],
#         "sensors": [
#             "LISS-IV (Linear Imaging Self-Scanning Sensor-4) — High-resolution VNIR camera",
#             "LISS-III — Medium-resolution 4-band multispectral sensor (Green, Red, NIR, SWIR)",
#             "AWiFS (Advanced Wide Field Sensor) — Wide-swath regional agricultural monitoring",
#         ],
#         "data_and_resolution": {
#             "data_type": "Optical Multispectral Surface Reflectance (GeoTIFF)",
#             "spatial_resolution": "5.8 m (LISS-IV) | 23.5 m (LISS-III) | 56 m (AWiFS)",
#             "revisit_time": "5 days (AWiFS) / 24 days (LISS-III)",
#         },
#         "applications": [
#             "Crop health & chlorophyll assessment via NDVI",
#             "Crop type classification and acreage forecasting",
#             "Drought assessment, watershed mapping, and forest cover monitoring",
#         ],
#         "project_utilization": "Provides Red (Band 1) and Near-Infrared (Band 2) surface reflectance to compute pixel-level NDVI ((NIR - Red) / (NIR + Red)) for leaf greenness and chlorophyll health.",
#     },
#     {
#         "id": "eos-04",
#         "name": "EOS-04 (RISAT-1A)",
#         "full_form": "Earth Observation Satellite-04 (Radar Imaging Satellite-1A)",
#         "badge": "C-BAND SAR RADAR",
#         "accent_color": "#38bdf8",
#         "agency": "ISRO (Indian Space Research Organisation)",
#         "launch_date": "February 14, 2022 (PSLV-C52 from Sriharikota)",
#         "orbit": "Sun-Synchronous Polar Orbit (529 km altitude)",
#         "objectives": [
#             "Provide all-weather, day-and-night high-resolution radar imaging unaffected by monsoon cloud cover or darkness.",
#             "Support precision agriculture, forestry, surface soil moisture mapping, and flood hydrology.",
#         ],
#         "sensors": [
#             "C-Band Synthetic Aperture Radar (SAR) operating at 5.35 GHz frequency",
#             "Multi-polarization imaging modes (HH, HV, VV, VH) with Coarse, Medium, and Fine resolution scan modes",
#         ],
#         "data_and_resolution": {
#             "data_type": "C-Band Microwave Backscatter Sigma-Naught in decibels (dB GeoTIFF)",
#             "spatial_resolution": "1 m to 50 m (depending on Spotlight / Stripmap / ScanSAR mode)",
#             "revisit_time": "12 to 17 days",
#         },
#         "applications": [
#             "All-weather Kharif (monsoon) crop monitoring through thick clouds",
#             "Surface topsoil moisture (0–5 cm) estimation",
#             "Flood inundation mapping and disaster management",
#         ],
#         "project_utilization": "Supplies cloud-piercing C-band VV backscatter (dB) converted into Topsoil Moisture (0–100%), solving the monsoon cloud blindspot and separating dry-soil water stress from wet-soil pest/nutrient issues.",
#     },
#     {
#         "id": "nisar",
#         "name": "NISAR",
#         "full_form": "NASA-ISRO Synthetic Aperture Radar",
#         "badge": "L + S DUAL-BAND SAR",
#         "accent_color": "#a855f7",
#         "agency": "NASA (USA) & ISRO (India) — Joint Earth Observation Mission",
#         "launch_date": "July 30, 2025 (GSLV Mk II / F16 from Satish Dhawan Space Centre, Sriharikota)",
#         "orbit": "Sun-Synchronous Dawn-Dusk Polar Orbit (747 km altitude)",
#         "objectives": [
#             "First satellite mission to carry dual-frequency L-band (24 cm) and S-band (10 cm) SweepSAR radars simultaneously.",
#             "Measure millimeter-scale Earth surface deformation, ecosystem biomass, crop structure, and deep root-zone soil moisture globally every 12 days.",
#         ],
#         "sensors": [
#             "L-Band SweepSAR (1.25 GHz / 24 cm wavelength, provided by NASA JPL) — penetrates dense crop canopies",
#             "S-Band SweepSAR (3.20 GHz / 9.3 cm wavelength, provided by ISRO SAC) — sensitive to leaf and surface roughness",
#             "12-meter deployable gold-plated wire-mesh reflector antenna",
#         ],
#         "data_and_resolution": {
#             "data_type": "Dual-Frequency Polarimetric SAR Backscatter (HH, HV, VV, VH GeoTIFF / HDF5)",
#             "spatial_resolution": "3 m to 10 m (240 km wide imaging swath)",
#             "revisit_time": "12 days exact repeat cycle (6-day ascending/descending passes)",
#         },
#         "applications": [
#             "Sub-canopy root-zone soil moisture (10–20 cm depth) and irrigation scheduling",
#             "Above-ground crop biomass, stem volume, and structural lodging detection",
#             "Landslide, earthquake, glacier, and groundwater subsidence tracking",
#         ],
#         "project_utilization": "Fuses L-Band HH backscatter (deep root-zone moisture) and L-Band HV backscatter (all-weather Radar Biomass Vigor Index) with EOS-04 and Resourcesat-2A so farmers never over-irrigate when root moisture is adequate.",
#     },
# ]


# class AnalyzeRequest(BaseModel):
#     geometry: Dict[str, Any] = Field(..., description="GeoJSON Polygon geometry")
#     cloud_cover_pct: float = Field(default=15.0, ge=0.0, le=100.0)


# @app.get("/")
# def health_check():
#     return {
#         "status": "online",
#         "project": "VyomDrishti",
#         "satellites": [
#             "ISRO Resourcesat-2A (Optical)",
#             "ISRO EOS-04 (C-Band SAR)",
#             "NASA-ISRO NISAR (L-Band & S-Band SAR)",
#         ],
#         "coverage_bounds": {
#             "region": "Sehore / Kothri Kalan, Madhya Pradesh",
#             "west": 76.95,
#             "south": 23.00,
#             "east": 77.05,
#             "north": 23.10,
#         },
#     }


# @app.get("/api/satellites")
# def get_satellites():
#     return {"count": len(SATELLITE_CATALOG), "satellites": SATELLITE_CATALOG}


# @app.post("/api/analyze")
# def analyze_farm(payload: AnalyzeRequest):
#     try:
#         return analyze_farm_polygon(
#             geojson_geometry=payload.geometry,
#             cloud_cover_pct=payload.cloud_cover_pct,
#         )
#     except ValueError as ve:
#         raise HTTPException(status_code=400, detail=str(ve))
#     except Exception as exc:
#         raise HTTPException(status_code=500, detail=f"Satellite processing error: {str(exc)}")
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Any, Dict, Optional

from satellite_engine import analyze_india_location

app = FastAPI(
    title="VyomDrishti Pan-India Satellite Intelligence API",
    description="Real-time multi-satellite Earth observation (Optical + C-Band SAR + NISAR L/S-Band) across India",
    version="3.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SATELLITE_CATALOG = [
    {
        "id": "resourcesat-2a",
        "name": "Resourcesat-2A",
        "full_form": "Indian Remote Sensing Satellite — Resourcesat-2A",
        "badge": "OPTICAL MULTISPECTRAL",
        "accent_color": "#10b981",
        "agency": "ISRO (Indian Space Research Organisation)",
        "launch_date": "December 7, 2016 (PSLV-C36 from Sriharikota)",
        "orbit": "Sun-Synchronous Polar Orbit (817 km altitude)",
        "objectives": [
            "Ensure continuity of global and national multispectral land and water resource monitoring.",
            "Provide high-radiometry visible, near-infrared (NIR), and short-wave infrared (SWIR) imagery for crop acreage and vegetation vigor estimation.",
        ],
        "sensors": [
            "LISS-IV (Linear Imaging Self-Scanning Sensor-4) — 5.8 m VNIR camera",
            "LISS-III — 23.5 m 4-band multispectral sensor (Green, Red, NIR, SWIR)",
            "AWiFS (Advanced Wide Field Sensor) — 56 m wide-swath agricultural monitoring",
        ],
        "data_and_resolution": {
            "data_type": "Optical Multispectral Surface Reflectance (GeoTIFF)",
            "spatial_resolution": "5.8 m (LISS-IV) | 23.5 m (LISS-III) | 56 m (AWiFS)",
            "revisit_time": "5 days (AWiFS) / 24 days (LISS-III)",
        },
        "applications": [
            "Crop health & chlorophyll assessment via NDVI",
            "Crop type classification and acreage forecasting",
            "Drought assessment, watershed mapping, and forest cover monitoring",
        ],
        "project_utilization": "Paired with live Sentinel-2 L2A (10 m Red & NIR COG bands) to compute real pixel-level NDVI ((NIR - Red) / (NIR + Red)) across any farm in India.",
    },
    {
        "id": "eos-04",
        "name": "EOS-04 (RISAT-1A)",
        "full_form": "Earth Observation Satellite-04 (Radar Imaging Satellite-1A)",
        "badge": "C-BAND SAR RADAR",
        "accent_color": "#38bdf8",
        "agency": "ISRO (Indian Space Research Organisation)",
        "launch_date": "February 14, 2022 (PSLV-C52 from Sriharikota)",
        "orbit": "Sun-Synchronous Polar Orbit (529 km altitude)",
        "objectives": [
            "Provide all-weather, day-and-night high-resolution radar imaging unaffected by monsoon cloud cover or darkness.",
            "Support precision agriculture, forestry, surface soil moisture mapping, and flood hydrology.",
        ],
        "sensors": [
            "C-Band Synthetic Aperture Radar (SAR) operating at 5.35 GHz frequency",
            "Multi-polarization imaging modes (HH, HV, VV, VH)",
        ],
        "data_and_resolution": {
            "data_type": "C-Band Microwave Backscatter Sigma-Naught in dB (GeoTIFF)",
            "spatial_resolution": "1 m to 50 m (Spotlight / Stripmap / ScanSAR)",
            "revisit_time": "12 to 17 days",
        },
        "applications": [
            "All-weather Kharif (monsoon) crop monitoring through thick clouds",
            "Surface topsoil moisture (0–5 cm) estimation",
            "Flood inundation mapping and disaster management",
        ],
        "project_utilization": "Paired with live C-Band SAR RTC (VV/VH backscatter in dB) to compute Radar Vegetation Index (RVI) and surface backscatter when optical imagery is cloud-covered.",
    },
    {
        "id": "nisar",
        "name": "NISAR",
        "full_form": "NASA-ISRO Synthetic Aperture Radar",
        "badge": "L + S DUAL-BAND SAR",
        "accent_color": "#a855f7",
        "agency": "NASA (USA) & ISRO (India) — Joint Earth Observation Mission",
        "launch_date": "July 30, 2025 (GSLV Mk II / F16 from Sriharikota)",
        "orbit": "Sun-Synchronous Dawn-Dusk Polar Orbit (747 km altitude)",
        "objectives": [
            "First satellite mission carrying dual-frequency L-band (24 cm) and S-band (10 cm) SweepSAR radars simultaneously.",
            "Measure Earth surface deformation, ecosystem biomass, crop structure, and sub-canopy root-zone soil moisture every 12 days.",
        ],
        "sensors": [
            "L-Band SweepSAR (1.25 GHz / 24 cm wavelength, NASA JPL) — penetrates dense crop canopies",
            "S-Band SweepSAR (3.20 GHz / 9.3 cm wavelength, ISRO SAC) — sensitive to leaf and surface roughness",
            "12-meter deployable gold-plated wire-mesh reflector antenna",
        ],
        "data_and_resolution": {
            "data_type": "Dual-Frequency Polarimetric SAR Backscatter (GeoTIFF / HDF5)",
            "spatial_resolution": "3 m to 10 m (240 km wide imaging swath)",
            "revisit_time": "12 days exact repeat cycle (6-day ascending/descending passes)",
        },
        "applications": [
            "Sub-canopy root-zone soil moisture (10–20 cm depth) and irrigation scheduling",
            "Above-ground crop biomass, stem volume, and lodging detection",
            "Landslide, earthquake, glacier, and groundwater subsidence tracking",
        ],
        "project_utilization": "Queried live via NASA CMR / ASF STAC for granule coverage over any clicked Indian location and integrated with root-zone moisture (9–27 cm) diagnostics.",
    },
]


class AnalyzeRequest(BaseModel):
    geometry: Dict[str, Any] = Field(..., description="GeoJSON Point or Polygon anywhere in India")
    start_date: Optional[str] = Field(default=None, description="YYYY-MM-DD start date")
    end_date: Optional[str] = Field(default=None, description="YYYY-MM-DD end date")
    satellite_filter: str = Field(default="all", description="all | optical | eos04 | nisar")


@app.get("/")
def health_check():
    return {
        "status": "online",
        "project": "VyomDrishti Pan-India",
        "coverage": "All India (6.0°N–38.0°N, 68.0°E–98.0°E)",
        "satellites": ["Resourcesat-2A / Sentinel-2 L2A", "EOS-04 / C-Band SAR", "NASA-ISRO NISAR"],
    }


@app.get("/api/satellites")
def get_satellites():
    return {"count": len(SATELLITE_CATALOG), "satellites": SATELLITE_CATALOG}


@app.post("/api/analyze")
def analyze_location(payload: AnalyzeRequest):
    try:
        return analyze_india_location(
            geojson_geometry=payload.geometry,
            start_date=payload.start_date,
            end_date=payload.end_date,
            satellite_filter=payload.satellite_filter,
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Satellite retrieval error: {str(exc)}")