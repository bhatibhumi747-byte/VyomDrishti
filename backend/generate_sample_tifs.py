import os
import numpy as np
import rasterio
from rasterio.transform import from_bounds

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Exact GPS bounding box matching our map scene (Sehore / Kothri Kalan, MP)
WEST, SOUTH, EAST, NORTH = 76.95, 23.00, 77.05, 23.10
WIDTH, HEIGHT = 500, 400

transform = from_bounds(WEST, SOUTH, EAST, NORTH, WIDTH, HEIGHT)

np.random.seed(42)
y_grid, x_grid = np.mgrid[0:HEIGHT, 0:WIDTH]
x_norm = x_grid / WIDTH

red_band = np.zeros((HEIGHT, WIDTH), dtype=np.float32)
nir_band = np.zeros((HEIGHT, WIDTH), dtype=np.float32)
eos04_vv_db = np.zeros((HEIGHT, WIDTH), dtype=np.float32)    # EOS-04 C-Band VV (topsoil moisture)
nisar_hh_db = np.zeros((HEIGHT, WIDTH), dtype=np.float32)    # NISAR L-Band HH (deep root-zone moisture)
nisar_hv_db = np.zeros((HEIGHT, WIDTH), dtype=np.float32)    # NISAR L-Band HV (crop canopy biomass)

# Zone 1 (Left, x < 0.35): Healthy irrigated crops
mask_healthy = x_norm < 0.35
red_band[mask_healthy] = 0.08 + np.random.normal(0, 0.015, mask_healthy.sum())
nir_band[mask_healthy] = 0.52 + np.random.normal(0, 0.03, mask_healthy.sum())
eos04_vv_db[mask_healthy] = -10.5 + np.random.normal(0, 0.8, mask_healthy.sum())
nisar_hh_db[mask_healthy] = -9.8 + np.random.normal(0, 0.7, mask_healthy.sum())
nisar_hv_db[mask_healthy] = -14.2 + np.random.normal(0, 0.6, mask_healthy.sum())

# Zone 2 (Middle, 0.35 <= x < 0.70): Water-stressed dry fields
mask_dry = (x_norm >= 0.35) & (x_norm < 0.70)
red_band[mask_dry] = 0.28 + np.random.normal(0, 0.02, mask_dry.sum())
nir_band[mask_dry] = 0.34 + np.random.normal(0, 0.025, mask_dry.sum())
eos04_vv_db[mask_dry] = -18.5 + np.random.normal(0, 0.9, mask_dry.sum())
nisar_hh_db[mask_dry] = -19.2 + np.random.normal(0, 0.8, mask_dry.sum())
nisar_hv_db[mask_dry] = -18.8 + np.random.normal(0, 0.7, mask_dry.sum())

# Zone 3 (Right, x >= 0.70): Pest/Nutrient-stressed wet fields
mask_pest = x_norm >= 0.70
red_band[mask_pest] = 0.25 + np.random.normal(0, 0.02, mask_pest.sum())
nir_band[mask_pest] = 0.36 + np.random.normal(0, 0.025, mask_pest.sum())
eos04_vv_db[mask_pest] = -9.2 + np.random.normal(0, 0.7, mask_pest.sum())
nisar_hh_db[mask_pest] = -8.9 + np.random.normal(0, 0.6, mask_pest.sum())
nisar_hv_db[mask_pest] = -19.5 + np.random.normal(0, 0.8, mask_pest.sum())

# Clip to realistic sensor dB/reflectance bounds
red_band = np.clip(red_band, 0.01, 0.95)
nir_band = np.clip(nir_band, 0.01, 0.95)
eos04_vv_db = np.clip(eos04_vv_db, -25.0, -5.0)
nisar_hh_db = np.clip(nisar_hh_db, -25.0, -5.0)
nisar_hv_db = np.clip(nisar_hv_db, -28.0, -8.0)

# 1. Resourcesat-2A Optical GeoTIFF
resourcesat_path = os.path.join(DATA_DIR, "resourcesat2a_optical.tif")
with rasterio.open(
    resourcesat_path, "w", driver="GTiff", height=HEIGHT, width=WIDTH,
    count=2, dtype="float32", crs="EPSG:4326", transform=transform,
) as dst:
    dst.write(red_band, 1)
    dst.set_band_description(1, "Red_Band")
    dst.write(nir_band, 2)
    dst.set_band_description(2, "NIR_Band")

# 2. EOS-04 C-Band SAR GeoTIFF
eos04_path = os.path.join(DATA_DIR, "eos04_sar.tif")
with rasterio.open(
    eos04_path, "w", driver="GTiff", height=HEIGHT, width=WIDTH,
    count=1, dtype="float32", crs="EPSG:4326", transform=transform,
) as dst:
    dst.write(eos04_vv_db, 1)
    dst.set_band_description(1, "EOS04_C_Band_VV_dB")

# 3. NISAR L-Band Dual-Pol SAR GeoTIFF
nisar_path = os.path.join(DATA_DIR, "nisar_lband_sar.tif")
with rasterio.open(
    nisar_path, "w", driver="GTiff", height=HEIGHT, width=WIDTH,
    count=2, dtype="float32", crs="EPSG:4326", transform=transform,
) as dst:
    dst.write(nisar_hh_db, 1)
    dst.set_band_description(1, "NISAR_L_Band_HH_dB")
    dst.write(nisar_hv_db, 2)
    dst.set_band_description(2, "NISAR_L_Band_HV_dB")

print("Success! Generated 3 satellite GeoTIFF datasets inside:", DATA_DIR)