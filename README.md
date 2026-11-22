# 🛰️ VyomDrishti

<div align="center">

<img src="https://img.icons8.com/color/144/satellite-in-orbit.png" alt="VyomDrishti Logo" width="120" />

### 🌾 All-Weather Crop & Soil Intelligence Using ISRO Satellites for Indian Farmers.

Draw your farm on **ISRO Bhuvan**, fuse **Resourcesat-2A**, **EOS-04**, and **NISAR** satellite data from **Bhoonidhi**, and get instant crop health, soil moisture, and **Hindi voice advisories** — even through monsoon clouds.

![Open Source](https://img.shields.io/badge/OPEN%20SOURCE-ASTRA%202026-FF6B00?style=for-the-badge)
![ISRO Powered](https://img.shields.io/badge/ISRO-BHOONIDHI%20%26%20BHUVAN-4CAF50?style=for-the-badge)
![React Frontend](https://img.shields.io/badge/REACT-FRONTEND-0288D1?style=for-the-badge)
![FastAPI Backend](https://img.shields.io/badge/PYTHON%20FASTAPI-BACKEND-689F38?style=for-the-badge)
![Made For Bharat](https://img.shields.io/badge/MADE%20FOR-BHARAT-FF6B00?style=for-the-badge)

</div>

---

## 📌 Overview

* 🛰️ **Multi-Mission ISRO Fusion** — Resourcesat-2A (Optical) + EOS-04 (C-SAR) + NISAR (S-SAR)
* 🗺️ **Official Geoportal Anchoring** — ISRO Bhuvan Land Use / Land Cover (`LULC 250K`) WMS Layers

---

## ✨ Features

* **Triple-Sensor Crop & Soil Checkup:** Combines **Resourcesat-2A** leaf greenness (`NDVI`) with **EOS-04** and **NISAR** cloud-piercing radar (`RVI`) to monitor farms 365 days a year—even during heavy monsoon cloud cover.
* **Root-Cause Stress Diagnosis:** Automatically separates **thirsty crops** (*Dry Soil + Weak Leaves*) from **diseased/nutrient-deficient crops** (*Wet Soil + Weak Leaves*), and flags **storm crop lodging** when NISAR structural backscatter drops.
* **Interactive Farm Observatory:** Draw a polygon around any farm on the **ISRO Bhuvan** map to generate sub-second heatmaps, health zone charts, and switchable sensor overlays.
* **Dedicated Satellite Information Portal:** Built-in reference dashboard detailing mission objectives, launch dates, sensors, resolutions, and utilization for **NISAR**, **Resourcesat-2A**, **EOS-04**, and **ISRO Bhuvan**.
* **Bilingual & Hindi Audio Support:** Translates complex satellite indices into plain **English & Hindi** farming steps with instant Hindi voice narration.

---

## 🛠️ Tech Stack

| Layer | Technology | Role in VyomDrishti |
| :--- | :--- | :--- |
| **ISRO Data & Maps** | Bhoonidhi & Bhuvan | Resourcesat-2A, EOS-04, NISAR GeoTIFFs & LULC WMS maps |
| **Backend API** | Python & FastAPI | High-speed REST API & request handling |
| **Geo Engine** | Rasterio, NumPy & Shapely | Clips satellite rasters & computes NDVI / SAR radar indices |
| **Frontend UI** | React (Vite) & Tailwind CSS | Farm Observatory, Satellite Info portal & Hindi voice UI |
| **Maps & Charts** | React-Leaflet, Leaflet-Draw & Recharts | Interactive polygon drawing, heatmap overlays & analytics |

---

## 📁 Project Structure

```text
Vyomdrishti/
├── backend/
│   ├── data/
│   │   ├── eos04_sar_moisture.tif
│   │   ├── eos04_sar.tif
│   │   ├── nisar_lband_sar.tif
│   │   └── resourcesat2a_optical.tif
│   ├── generate_sample_tif.py
│   ├── main.py
│   ├── requirements.txt
│   └── satellite_engine.py
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   │   ├── FarmMap.jsx
│   │   │   └── SatelliteInfo.jsx
│   │   ├── App.css
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   ├── eslint.config.js
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── .gitignore
└── README.md
```

---------

## 🚀 Getting Started

### 1. Clone the Repository

    git clone https://github.com/<your-username>/vyomdrishti.git
    cd vyomdrishti

### 2. Backend Setup

    cd backend
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    python generate_sample.py
    uvicorn main:app --reload --port 8000

*(On Windows, activate the virtual environment using `venv\Scripts\activate`)*

### 3. Frontend Setup

    cd ../frontend
    npm install
    npm run dev

Open `http://localhost:5173` in your browser to launch **VyomDrishti**.

---

## 🔌 API Reference

## GET /api/health 

Returns `{"status": "online"}` along with active ISRO satellite missions — use to check if the backend is running.

## GET /api/default-region  

Returns the default agricultural map bounds and center coordinates.  
## POST /api/analyze-polygon  

Accepts a GeoJSON farm polygon and returns sub-second **Resourcesat-2A**, **EOS-04**, and **NISAR** metrics, base64 heatmap overlays, and bilingual Hindi/English advisories.

---

## 💖 Support the Project

If you like this project:

⭐ Star the repository  
🍴 Fork the project  
🐛 Raise issues  
🚀 Contribute to the project  

---
 ## BY VOIDRUNNERS
BHUMI BHATI  
NISHTHA SAHU
