# import os
# import numpy as np
# import rasterio
# from rasterio.mask import mask
# from shapely.geometry import shape, mapping, box

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# DATA_DIR = os.path.join(BASE_DIR, "data")

# OPTICAL_PATH = os.path.join(DATA_DIR, "resourcesat2a_optical.tif")
# EOS04_SAR_PATH = os.path.join(DATA_DIR, "eos04_sar.tif")
# NISAR_SAR_PATH = os.path.join(DATA_DIR, "nisar_lband_sar.tif")


# def normalize_soil_moisture(sar_db: np.ndarray, min_db: float = -22.0, max_db: float = -7.0) -> np.ndarray:
#     moisture_pct = ((sar_db - min_db) / (max_db - min_db)) * 100.0
#     return np.clip(moisture_pct, 0.0, 100.0)


# def normalize_nisar_biomass(hv_db: np.ndarray) -> np.ndarray:
#     vigor = (hv_db - (-24.0)) / (-11.0 - (-24.0))
#     return np.clip(vigor, 0.0, 1.0)


# def classify_pixel(ndvi: float, topsoil_moisture: float, root_moisture: float, radar_vigor: float) -> str:
#     combined_canopy_health = (0.6 * ndvi) + (0.4 * radar_vigor)
#     combined_moisture = (0.45 * topsoil_moisture) + (0.55 * root_moisture)

#     if combined_canopy_health >= 0.48 and ndvi >= 0.42:
#         return "healthy"
#     elif combined_moisture < 40.0:
#         return "water_stress"
#     else:
#         return "pest_nutrient_stress"


# def analyze_farm_polygon(geojson_geometry: dict, cloud_cover_pct: float = 15.0) -> dict:
#     farm_geom = shape(geojson_geometry)
#     if not farm_geom.is_valid:
#         farm_geom = farm_geom.buffer(0)

#     with rasterio.open(OPTICAL_PATH) as opt_src:
#         dataset_bounds = box(*opt_src.bounds)
#         if not farm_geom.intersects(dataset_bounds):
#             raise ValueError(
#                 "Selected farm is outside the loaded satellite scene bounds "
#                 "(76.95°E–77.05°E, 23.00°N–23.10°N in Sehore/Kothri Kalan, MP)."
#             )
#         opt_clipped, opt_transform = mask(opt_src, [mapping(farm_geom)], crop=True, nodata=np.nan)
#         red = opt_clipped[0].astype(np.float32)
#         nir = opt_clipped[1].astype(np.float32)

#     with rasterio.open(EOS04_SAR_PATH) as eos_src:
#         eos_clipped, _ = mask(eos_src, [mapping(farm_geom)], crop=True, nodata=np.nan)
#         eos_vv_db = eos_clipped[0].astype(np.float32)

#     with rasterio.open(NISAR_SAR_PATH) as nisar_src:
#         nisar_clipped, _ = mask(nisar_src, [mapping(farm_geom)], crop=True, nodata=np.nan)
#         nisar_hh_db = nisar_clipped[0].astype(np.float32)
#         nisar_hv_db = nisar_clipped[1].astype(np.float32)

#     ndvi_grid = (nir - red) / (nir + red + 1e-6)
#     topsoil_moisture_grid = normalize_soil_moisture(eos_vv_db)
#     root_moisture_grid = normalize_soil_moisture(nisar_hh_db)
#     radar_vigor_grid = normalize_nisar_biomass(nisar_hv_db)

#     valid_mask = (
#         ~np.isnan(ndvi_grid)
#         & ~np.isnan(topsoil_moisture_grid)
#         & ~np.isnan(root_moisture_grid)
#         & ~np.isnan(radar_vigor_grid)
#     )
#     if not np.any(valid_mask):
#         raise ValueError("Selected area is too small. Please draw a slightly larger farm polygon.")

#     mean_ndvi = float(np.mean(ndvi_grid[valid_mask]))
#     mean_topsoil = float(np.mean(topsoil_moisture_grid[valid_mask]))
#     mean_root = float(np.mean(root_moisture_grid[valid_mask]))
#     mean_radar_vigor = float(np.mean(radar_vigor_grid[valid_mask]))
#     fused_moisture = round((0.45 * mean_topsoil) + (0.55 * mean_root), 1)
#     optical_reliable = cloud_cover_pct < 50.0

#     rows, cols = ndvi_grid.shape
#     step = max(1, max(rows, cols) // 35)

#     heatmap_cells = []
#     counts = {"healthy": 0, "water_stress": 0, "pest_nutrient_stress": 0}

#     for r in range(0, rows, step):
#         for c in range(0, cols, step):
#             n_val = ndvi_grid[r, c]
#             t_val = topsoil_moisture_grid[r, c]
#             rt_val = root_moisture_grid[r, c]
#             rv_val = radar_vigor_grid[r, c]
#             if np.isnan(n_val) or np.isnan(t_val) or np.isnan(rt_val):
#                 continue

#             status = classify_pixel(float(n_val), float(t_val), float(rt_val), float(rv_val))
#             counts[status] += 1

#             lon_west, lat_north = rasterio.transform.xy(opt_transform, r, c, offset="ul")
#             lon_east, lat_south = rasterio.transform.xy(
#                 opt_transform, min(r + step, rows), min(c + step, cols), offset="ul"
#             )

#             heatmap_cells.append({
#                 "bounds": [[lat_south, lon_west], [lat_north, lon_east]],
#                 "status": status,
#                 "ndvi": round(float(n_val), 3),
#                 "moisture": round(float(t_val), 1),
#                 "root_moisture": round(float(rt_val), 1),
#                 "nisar_vigor": round(float(rv_val), 2),
#             })

#     total_cells = max(1, sum(counts.values()))
#     healthy_pct = round((counts["healthy"] / total_cells) * 100, 1)
#     water_stress_pct = round((counts["water_stress"] / total_cells) * 100, 1)
#     pest_stress_pct = round((counts["pest_nutrient_stress"] / total_cells) * 100, 1)

#     dominant_status = max(counts, key=counts.get)

#     if dominant_status == "water_stress":
#         diagnosis = {
#             "status": "water_stress",
#             "title_en": "Water Stress Detected (Topsoil & Root-Zone Dry)",
#             "title_hi": "पानी की कमी (ऊपरी और जड़-क्षेत्र की मिट्टी सूखी)",
#             "action_en": "Irrigate red zones within 24–48 hours. Both EOS-04 C-band (topsoil) and NISAR L-band (root-zone) confirm moisture depletion.",
#             "action_hi": "अगले 24–48 घंटों में लाल हिस्सों की सिंचाई करें। EOS-04 (ऊपरी मिट्टी) और NISAR L-बैंड (गहरी जड़ नमी) दोनों पानी की कमी दिखाते हैं।",
#         }
#     elif dominant_status == "pest_nutrient_stress":
#         diagnosis = {
#             "status": "pest_nutrient_stress",
#             "title_en": "Nutrient / Pest Stress (Adequate Root Moisture + Low Canopy Vigor)",
#             "title_hi": "पोषक तत्व या कीट तनाव (पर्याप्त जड़ नमी + कमजोर फसल संरचना)",
#             "action_en": "Do NOT over-irrigate—NISAR L-band confirms healthy root-zone moisture. Inspect leaves for pests/blight and apply balanced NPK.",
#             "action_hi": "अतिरिक्त सिंचाई न करें—NISAR L-बैंड जड़ों में पर्याप्त नमी की पुष्टि करता है। पत्तियों पर कीट/रोग की जाँच करें और संतुलित खाद दें।",
#         }
#     else:
#         diagnosis = {
#             "status": "healthy",
#             "title_en": "Healthy Crop Canopy & Balanced Root-Zone Moisture",
#             "title_hi": "स्वस्थ फसल संरचना और संतुलित जड़-क्षेत्र नमी",
#             "action_en": "Maintain current irrigation schedule. Resourcesat-2A, EOS-04, and NISAR L-band all confirm strong crop vigor.",
#             "action_hi": "वर्तमान सिंचाई कार्यक्रम बनाए रखें। Resourcesat-2A, EOS-04 और NISAR L-बैंड तीनों स्वस्थ फसल की पुष्टि करते हैं।",
#         }

#     seasonal_trend = [
#         {"week": "Week 1", "ndvi": round(max(0.15, mean_ndvi - 0.08), 2), "moisture": round(min(95, mean_topsoil + 10), 1), "root_moisture": round(min(95, mean_root + 8), 1)},
#         {"week": "Week 2", "ndvi": round(max(0.15, mean_ndvi - 0.05), 2), "moisture": round(min(95, mean_topsoil + 6), 1), "root_moisture": round(min(95, mean_root + 5), 1)},
#         {"week": "Week 3", "ndvi": round(max(0.15, mean_ndvi - 0.03), 2), "moisture": round(min(95, mean_topsoil + 2), 1), "root_moisture": round(min(95, mean_root + 2), 1)},
#         {"week": "Week 4", "ndvi": round(max(0.15, mean_ndvi - 0.01), 2), "moisture": round(mean_topsoil, 1), "root_moisture": round(mean_root, 1)},
#         {"week": "Current", "ndvi": round(mean_ndvi, 2), "moisture": round(mean_topsoil, 1), "root_moisture": round(mean_root, 1)},
#     ]

#     return {
#         "metrics": {
#             "mean_ndvi": round(mean_ndvi, 3),
#             "mean_soil_moisture_pct": fused_moisture,
#             "topsoil_moisture_pct": round(mean_topsoil, 1),
#             "root_zone_moisture_pct": round(mean_root, 1),
#             "nisar_biomass_vigor": round(mean_radar_vigor, 2),
#             "cloud_cover_pct": cloud_cover_pct,
#             "optical_reliable": optical_reliable,
#             "sar_status": "EOS-04 (C-Band) + NISAR (L-Band) Active",
#         },
#         "zone_breakdown": {
#             "healthy_pct": healthy_pct,
#             "water_stress_pct": water_stress_pct,
#             "pest_nutrient_stress_pct": pest_stress_pct,
#         },
#         "diagnosis": diagnosis,
#         "heatmap_cells": heatmap_cells,
#         "seasonal_trend": seasonal_trend,
#     }
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple
import math
import numpy as np
import requests
import rasterio
from rasterio.warp import transform as warp_transform
from shapely.geometry import shape, Point, box
import pystac_client
import planetary_computer

PC_STAC_URL = "https://planetarycomputer.microsoft.com/api/stac/v1"
NASA_CMR_STAC_URL = "https://cmr.earthdata.nasa.gov/stac/ASF/search"
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

# India bounding box (including Andaman & Nicobar and Lakshadweep)
INDIA_BBOX = (6.0, 68.0, 38.0, 98.0)  # (min_lat, min_lon, max_lat, max_lon)


def extract_centroid_and_bbox(geojson_geometry: dict) -> Tuple[float, float, List[float]]:
    """Extracts (lat, lon) centroid and [west, south, east, north] bbox from GeoJSON Point or Polygon."""
    geom = shape(geojson_geometry)
    if not geom.is_valid:
        geom = geom.buffer(0)

    centroid = geom.centroid
    lat, lon = float(centroid.y), float(centroid.x)

    if geom.geom_type == "Point":
        pad = 0.015  # ~1.6 km analysis window around clicked point
        bbox = [lon - pad, lat - pad, lon + pad, lat + pad]
    else:
        minx, miny, maxx, maxy = geom.bounds
        bbox = [float(minx), float(miny), float(maxx), float(maxy)]

    return lat, lon, bbox


def is_within_india(lat: float, lon: float) -> bool:
    min_lat, min_lon, max_lat, max_lon = INDIA_BBOX
    return (min_lat <= lat <= max_lat) and (min_lon <= lon <= max_lon)


def sample_cog_window(href: str, lon: float, lat: float, half_size_px: int = 8) -> Optional[np.ndarray]:
    """
    Reads a small real pixel patch around (lon, lat) from a Cloud-Optimized GeoTIFF (COG)
    without downloading the entire multi-hundred-MB satellite scene.
    """
    try:
        with rasterio.open(href) as src:
            xs, ys = warp_transform("EPSG:4326", src.crs, [lon], [lat])
            row, col = src.index(xs[0], ys[0])
            if row < 0 or col < 0 or row >= src.height or col >= src.width:
                return None

            r_start = max(0, row - half_size_px)
            r_stop = min(src.height, row + half_size_px + 1)
            c_start = max(0, col - half_size_px)
            c_stop = min(src.width, col + half_size_px + 1)

            window = rasterio.windows.Window.from_slices((r_start, r_stop), (c_start, c_stop))
            patch = src.read(1, window=window).astype(np.float32)
            if src.nodata is not None:
                patch[patch == src.nodata] = np.nan
            return patch
    except Exception:
        return None


def fetch_real_sentinel2_optical(
    bbox: List[float], lat: float, lon: float, start_date: str, end_date: str
) -> Dict[str, Any]:
    """Queries Microsoft Planetary Computer STAC for real Sentinel-2 L2A imagery and computes real NDVI."""
    try:
        catalog = pystac_client.Client.open(PC_STAC_URL, modifier=planetary_computer.sign_inplace)
        search = catalog.search(
            collections=["sentinel-2-l2a"],
            bbox=bbox,
            datetime=f"{start_date}/{end_date}",
            query={"eo:cloud_cover": {"lt": 85}},
            max_items=5,
        )
        items = list(search.items())
        if not items:
            return {"available": False, "reason": "No Sentinel-2 optical pass found in selected date window."}

        # Pick least cloudy recent scene
        items.sort(key=lambda x: x.properties.get("eo:cloud_cover", 100.0))
        best = items[0]
        cloud_pct = round(float(best.properties.get("eo:cloud_cover", 0.0)), 1)
        obs_date = best.datetime.strftime("%Y-%m-%d %H:%M UTC") if best.datetime else "Unknown"

        red_patch = sample_cog_window(best.assets["B04"].href, lon, lat)
        nir_patch = sample_cog_window(best.assets["B08"].href, lon, lat)

        if red_patch is None or nir_patch is None:
            return {
                "available": True,
                "scene_id": best.id,
                "observation_date": obs_date,
                "cloud_cover_pct": cloud_pct,
                "ndvi_mean": None,
                "ndvi_grid": None,
                "provenance": "REAL SATELLITE METADATA (COG Pixel Read Timed Out)",
            }

        # Sentinel-2 L2A reflectance scale factor is 10000
        red = red_patch / 10000.0
        nir = nir_patch / 10000.0
        ndvi_grid = (nir - red) / (nir + red + 1e-6)
        ndvi_grid = np.clip(ndvi_grid, -1.0, 1.0)
        valid = ~np.isnan(ndvi_grid)
        ndvi_mean = round(float(np.nanmean(ndvi_grid)), 3) if np.any(valid) else None

        return {
            "available": True,
            "platform": "Sentinel-2 L2A (Harmonized Optical — Resourcesat-2A Equivalent)",
            "scene_id": best.id,
            "observation_date": obs_date,
            "cloud_cover_pct": cloud_pct,
            "ndvi_mean": ndvi_mean,
            "ndvi_grid": ndvi_grid,
            "provenance": "REAL SATELLITE OBSERVATION (Live COG Band B04/B08)",
        }
    except Exception as exc:
        return {"available": False, "reason": f"Optical STAC query error: {str(exc)}"}


def fetch_real_sentinel1_sar(
    bbox: List[float], lat: float, lon: float, start_date: str, end_date: str
) -> Dict[str, Any]:
    """Queries Planetary Computer STAC for real C-Band SAR (EOS-04 C-Band equivalent) VV/VH backscatter."""
    try:
        catalog = pystac_client.Client.open(PC_STAC_URL, modifier=planetary_computer.sign_inplace)
        search = catalog.search(
            collections=["sentinel-1-rtc"],
            bbox=bbox,
            datetime=f"{start_date}/{end_date}",
            max_items=3,
        )
        items = list(search.items())
        if not items:
            return {"available": False, "reason": "No C-Band SAR pass found in selected date window."}

        items.sort(key=lambda x: x.datetime or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
        latest = items[0]
        obs_date = latest.datetime.strftime("%Y-%m-%d %H:%M UTC") if latest.datetime else "Unknown"

        vv_patch = sample_cog_window(latest.assets["vv"].href, lon, lat) if "vv" in latest.assets else None
        vh_patch = sample_cog_window(latest.assets["vh"].href, lon, lat) if "vh" in latest.assets else None

        vv_db = None
        rvi_mean = None
        if vv_patch is not None and np.any(vv_patch > 0):
            vv_linear = np.where(vv_patch > 0, vv_patch, np.nan)
            vv_db_grid = 10.0 * np.log10(vv_linear)
            vv_db = round(float(np.nanmean(vv_db_grid)), 2)

            if vh_patch is not None and np.any(vh_patch > 0):
                vh_linear = np.where(vh_patch > 0, vh_patch, np.nan)
                # Radar Vegetation Index: 4 * VH / (VV + VH)
                rvi_grid = (4.0 * vh_linear) / (vv_linear + vh_linear + 1e-6)
                rvi_mean = round(float(np.clip(np.nanmean(rvi_grid), 0.0, 1.0)), 3)

        return {
            "available": True,
            "platform": "C-Band SAR RTC (EOS-04 C-Band Equivalent)",
            "scene_id": latest.id,
            "observation_date": obs_date,
            "orbit_state": latest.properties.get("sat:orbit_state", "unknown"),
            "vv_backscatter_db": vv_db,
            "radar_vegetation_index": rvi_mean,
            "provenance": "REAL C-BAND SAR OBSERVATION (Live COG VV/VH)",
        }
    except Exception as exc:
        return {"available": False, "reason": f"C-Band SAR query error: {str(exc)}"}


def fetch_real_nisar_catalog(bbox: List[float], start_date: str, end_date: str) -> Dict[str, Any]:
    """Queries NASA CMR STAC (ASF) for real NISAR L-Band/S-Band granule observations at the selected location."""
    try:
        params = {
            "collections": ["NISAR_L2_GCOV_BETA_V1", "NISAR_L1_RSLC_BETA_V1", "NISAR_L2_GCOV_V1"],
            "bbox": ",".join(map(str, bbox)),
            "datetime": f"{start_date}T00:00:00Z/{end_date}T23:59:59Z",
            "limit": 3,
        }
        resp = requests.get(NASA_CMR_STAC_URL, params=params, timeout=8)
        if resp.status_code == 200:
            data = resp.json()
            features = data.get("features", [])
            if features:
                feat = features[0]
                props = feat.get("properties", {})
                return {
                    "available": True,
                    "granule_id": feat.get("id", "NISAR_GRANULE"),
                    "observation_date": props.get("datetime", "Recent Pass"),
                    "frequency_bands": "L-Band (1.25 GHz / 24 cm) + S-Band (3.20 GHz)",
                    "provenance": "REAL NISAR GRANULE METADATA (NASA CMR / ISRO)",
                }
        return {
            "available": False,
            "reason": "No public NISAR L2-GCOV granule archived for this exact date window yet (12-day repeat cycle).",
        }
    except Exception as exc:
        return {"available": False, "reason": f"NISAR catalog query timeout: {str(exc)}"}


def fetch_real_soil_and_weather(lat: float, lon: float) -> Dict[str, Any]:
    """Fetches real-time location-specific topsoil & root-zone volumetric soil moisture and 7-day history."""
    try:
        params = {
            "latitude": round(lat, 4),
            "longitude": round(lon, 4),
            "hourly": "soil_moisture_0_to_1cm,soil_moisture_3_to_9cm,soil_moisture_9_to_27cm,temperature_2m,precipitation",
            "past_days": 7,
            "forecast_days": 1,
            "timezone": "Asia/Kolkata",
        }
        resp = requests.get(OPEN_METEO_URL, params=params, timeout=8)
        resp.raise_for_status()
        payload = resp.json()
        hourly = payload.get("hourly", {})
        times = hourly.get("time", [])
        sm_top = hourly.get("soil_moisture_0_to_1cm", [])
        sm_mid = hourly.get("soil_moisture_3_to_9cm", [])
        sm_root = hourly.get("soil_moisture_9_to_27cm", [])
        temp_arr = hourly.get("temperature_2m", [])
        precip_arr = hourly.get("precipitation", [])

        if not times or not sm_top:
            return {"available": False}

        # Latest valid index (around current IST hour)
        idx = min(len(times) - 1, max(0, len(times) - 24))
        # Volumetric water content (m³/m³ typically 0.05 dry to 0.45 saturated) -> convert to 0-100% field capacity
        top_pct = round(min(100.0, max(0.0, (sm_top[idx] / 0.42) * 100.0)), 1)
        root_pct = round(min(100.0, max(0.0, (sm_root[idx] / 0.42) * 100.0)), 1)
        temp_c = round(float(temp_arr[idx]), 1)
        precip_7d = round(float(sum(p for p in precip_arr[:idx + 1] if p is not None)), 1)

        # Build daily historical trend over the past 7 days
        daily_trend = []
        for day_offset in range(6, -1, -1):
            sample_i = max(0, idx - (day_offset * 24))
            date_label = times[sample_i][:10]
            t_val = round(min(100.0, max(0.0, (sm_top[sample_i] / 0.42) * 100.0)), 1)
            r_val = round(min(100.0, max(0.0, (sm_root[sample_i] / 0.42) * 100.0)), 1)
            daily_trend.append({
                "date": date_label,
                "topsoil_moisture": t_val,
                "root_moisture": r_val,
            })

        return {
            "available": True,
            "observation_time_ist": times[idx],
            "topsoil_moisture_pct": top_pct,
            "root_zone_moisture_pct": root_pct,
            "raw_vwc_top_m3m3": round(float(sm_top[idx]), 3),
            "raw_vwc_root_m3m3": round(float(sm_root[idx]), 3),
            "temperature_c": temp_c,
            "precipitation_7d_mm": precip_7d,
            "daily_trend": daily_trend,
            "provenance": "REAL LAND REANALYSIS (Open-Meteo / ERA5-Land Assimilation)",
        }
    except Exception:
        return {"available": False}


def reverse_geocode_india(lat: float, lon: float) -> str:
    """Fetches real district/state name in India for the clicked coordinates."""
    try:
        resp = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={"lat": lat, "lon": lon, "format": "json", "zoom": 10},
            headers={"User-Agent": "VyomDrishti-GeoPlatform/2.0"},
            timeout=5,
        )
        if resp.status_code == 200:
            addr = resp.json().get("address", {})
            parts = [
                addr.get("village") or addr.get("town") or addr.get("city") or addr.get("county"),
                addr.get("state_district") or addr.get("district"),
                addr.get("state"),
            ]
            clean = [p for p in parts if p]
            if clean:
                return ", ".join(dict.fromkeys(clean))
    except Exception:
        pass
    return f"India ({lat:.4f}°N, {lon:.4f}°E)"


def analyze_india_location(
    geojson_geometry: dict,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    satellite_filter: str = "all",
) -> Dict[str, Any]:
    """
    Master All-India real-time satellite & environmental analysis pipeline.
    Never fabricates satellite data—reports real observations and explicitly marks unavailable sensors.
    """
    lat, lon, bbox = extract_centroid_and_bbox(geojson_geometry)

    if not is_within_india(lat, lon):
        raise ValueError(
            f"Selected coordinates ({lat:.3f}°N, {lon:.3f}°E) are outside India. "
            "Please click any agricultural region within India."
        )

    today = datetime.now(timezone.utc).date()
    if not end_date:
        end_date = today.isoformat()
    if not start_date:
        start_date = (today - timedelta(days=30)).isoformat()

    location_name = reverse_geocode_india(lat, lon)

    # Query real satellite & environmental data sources
    optical = (
        fetch_real_sentinel2_optical(bbox, lat, lon, start_date, end_date)
        if satellite_filter in ("all", "optical")
        else {"available": False, "reason": "Filtered out by user"}
    )
    c_sar = (
        fetch_real_sentinel1_sar(bbox, lat, lon, start_date, end_date)
        if satellite_filter in ("all", "eos04")
        else {"available": False, "reason": "Filtered out by user"}
    )
    nisar = (
        fetch_real_nisar_catalog(bbox, start_date, end_date)
        if satellite_filter in ("all", "nisar")
        else {"available": False, "reason": "Filtered out by user"}
    )
    soil_env = fetch_real_soil_and_weather(lat, lon)

    # Determine authentic metrics (None if unavailable—never faked)
    ndvi_val = optical.get("ndvi_mean") if optical.get("available") else None
    cloud_pct = optical.get("cloud_cover_pct") if optical.get("available") else None
    rvi_val = c_sar.get("radar_vegetation_index") if c_sar.get("available") else None
    vv_db = c_sar.get("vv_backscatter_db") if c_sar.get("available") else None

    topsoil_pct = soil_env.get("topsoil_moisture_pct") if soil_env.get("available") else None
    root_pct = soil_env.get("root_zone_moisture_pct") if soil_env.get("available") else None

    # Build real spatial heatmap cells from the actual Sentinel-2 NDVI pixel patch if available
    heatmap_cells = []
    counts = {"healthy": 0, "water_stress": 0, "pest_nutrient_stress": 0}
    ndvi_grid = optical.get("ndvi_grid")

    if ndvi_grid is not None and isinstance(ndvi_grid, np.ndarray):
        rows, cols = ndvi_grid.shape
        west, south, east, north = bbox
        lat_step = (north - south) / max(1, rows)
        lon_step = (east - west) / max(1, cols)

        for r in range(rows):
            for c in range(cols):
                val = float(ndvi_grid[r, c])
                if math.isnan(val):
                    continue
                if val >= 0.42:
                    st = "healthy"
                elif (root_pct is not None and root_pct < 38.0):
                    st = "water_stress"
                else:
                    st = "pest_nutrient_stress"
                counts[st] += 1

                cell_south = north - (r + 1) * lat_step
                cell_north = north - r * lat_step
                cell_west = west + c * lon_step
                cell_east = west + (c + 1) * lon_step

                heatmap_cells.append({
                    "bounds": [[cell_south, cell_west], [cell_north, cell_east]],
                    "status": st,
                    "ndvi": round(val, 3),
                    "moisture": topsoil_pct if topsoil_pct is not None else "N/A",
                    "root_moisture": root_pct if root_pct is not None else "N/A",
                    "nisar_vigor": rvi_val if rvi_val is not None else "N/A",
                })

    total_cells = sum(counts.values())
    if total_cells > 0:
        healthy_pct = round((counts["healthy"] / total_cells) * 100, 1)
        water_stress_pct = round((counts["water_stress"] / total_cells) * 100, 1)
        pest_stress_pct = round((counts["pest_nutrient_stress"] / total_cells) * 100, 1)
    else:
        healthy_pct = water_stress_pct = pest_stress_pct = None

    # Generate evidence-based agronomic diagnosis from real measurements
    effective_vigor = ndvi_val if ndvi_val is not None else rvi_val
    if effective_vigor is None and root_pct is None:
        diagnosis = {
            "status": "unavailable",
            "title_en": "Insufficient Satellite Data for Selected Window",
            "title_hi": "चयनित तिथि सीमा के लिए अपर्याप्त उपग्रह डेटा",
            "action_en": "Expand the observation date range (e.g., 30–60 days) to capture the latest satellite orbital pass over this location.",
            "action_hi": "इस स्थान के नवीनतम उपग्रह पास को देखने के लिए तिथि सीमा (जैसे 30-60 दिन) बढ़ाएँ।",
        }
    elif effective_vigor is not None and effective_vigor >= 0.42:
        diagnosis = {
            "status": "healthy",
            "title_en": "Healthy Vegetation Canopy Observed",
            "title_hi": "स्वस्थ फसल हरियाली दर्ज की गई",
            "action_en": f"Observed vegetation index ({effective_vigor}) indicates active chlorophyll/canopy health. Maintain current irrigation schedule.",
            "action_hi": f"दर्ज वनस्पति सूचकांक ({effective_vigor}) स्वस्थ फसल दर्शाता है। वर्तमान सिंचाई कार्यक्रम बनाए रखें।",
        }
    elif root_pct is not None and root_pct < 38.0:
        diagnosis = {
            "status": "water_stress",
            "title_en": "Root-Zone Moisture Deficit (Water Stress)",
            "title_hi": "जड़-क्षेत्र में नमी की कमी (सिंचाई आवश्यक)",
            "action_en": f"Root-zone soil moisture is low ({root_pct}%). Schedule irrigation to replenish root-zone water.",
            "action_hi": f"जड़-क्षेत्र में मिट्टी की नमी कम ({root_pct}%) है। जड़ों में नमी बहाल करने के लिए सिंचाई करें।",
        }
    else:
        diagnosis = {
            "status": "pest_nutrient_stress",
            "title_en": "Low Canopy Vigor Despite Adequate Soil Moisture",
            "title_hi": "पर्याप्त मिट्टी की नमी के बावजूद कम फसल हरियाली",
            "action_en": "Soil moisture is adequate, but vegetation vigor is low (or land is fallow/harvested). Inspect standing crops for nutrient/pest stress before irrigating.",
            "action_hi": "मिट्टी में नमी पर्याप्त है, लेकिन हरियाली कम है। सिंचाई से पहले फसल में पोषक तत्व या कीट तनाव की जाँच करें।",
        }

    # Combine real 7-day soil trend with observed NDVI reference for charting
    seasonal_trend = []
    if soil_env.get("available"):
        for pt in soil_env["daily_trend"]:
            seasonal_trend.append({
                "week": pt["date"][5:],  # MM-DD
                "ndvi": ndvi_val,
                "moisture": pt["topsoil_moisture"],
                "root_moisture": pt["root_moisture"],
            })

    return {
        "location": {
            "name": location_name,
            "lat": round(lat, 5),
            "lon": round(lon, 5),
            "bbox": [round(b, 5) for b in bbox],
            "date_window": f"{start_date} to {end_date}",
        },
        "observations": {
            "optical": {k: v for k, v in optical.items() if k != "ndvi_grid"},
            "c_band_sar": c_sar,
            "nisar": nisar,
            "soil_environment": {k: v for k, v in soil_env.items() if k != "daily_trend"},
        },
        "metrics": {
            "mean_ndvi": ndvi_val,
            "topsoil_moisture_pct": topsoil_pct,
            "root_zone_moisture_pct": root_pct,
            "nisar_biomass_vigor": rvi_val,
            "c_band_vv_db": vv_db,
            "cloud_cover_pct": cloud_pct,
            "temperature_c": soil_env.get("temperature_c"),
            "precipitation_7d_mm": soil_env.get("precipitation_7d_mm"),
        },
        "zone_breakdown": {
            "healthy_pct": healthy_pct,
            "water_stress_pct": water_stress_pct,
            "pest_nutrient_stress_pct": pest_stress_pct,
        },
        "diagnosis": diagnosis,
        "heatmap_cells": heatmap_cells,
        "seasonal_trend": seasonal_trend,
    }