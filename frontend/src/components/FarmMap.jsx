// import { useEffect, useRef, useState } from "react";
// import L from "leaflet";
// import { Layers, MousePointerClick, RotateCcw, Sparkles } from "lucide-react";

// const SCENE_BOUNDS = [
//   [23.0, 76.95],
//   [23.1, 77.05],
// ];

// const PRESET_FARMS = {
//   healthy: {
//     label: "Demo: Healthy Farm",
//     coords: [
//       [23.03, 76.96],
//       [23.03, 76.98],
//       [23.07, 76.98],
//       [23.07, 76.96],
//     ],
//   },
//   water_stress: {
//     label: "Demo: Dry Soil Zone",
//     coords: [
//       [23.03, 76.99],
//       [23.03, 77.01],
//       [23.07, 77.01],
//       [23.07, 76.99],
//     ],
//   },
//   pest_stress: {
//     label: "Demo: Pest/Nutrient Zone",
//     coords: [
//       [23.03, 77.02],
//       [23.03, 77.04],
//       [23.07, 77.04],
//       [23.07, 77.02],
//     ],
//   },
// };

// const STATUS_COLORS = {
//   healthy: "#10b981",
//   water_stress: "#ef4444",
//   pest_nutrient_stress: "#f59e0b",
// };

// export default function FarmMap({ heatmapCells, onPolygonChange, lang }) {
//   const mapContainerRef = useRef(null);
//   const mapInstanceRef = useRef(null);
//   const baseLayerRef = useRef(null);
//   const drawnLayerRef = useRef(null);
//   const heatmapLayerRef = useRef(null);

//   const [baseMapType, setBaseMapType] = useState("satellite");
//   const [drawMode, setDrawMode] = useState(false);
//   const [points, setPoints] = useState(PRESET_FARMS.water_stress.coords);

//   // 1. Initialize Leaflet Map safely (handles Vite hot-reloads without crashing)
//   useEffect(() => {
//     const container = mapContainerRef.current;
//     if (!container) return;

//     // Reset any leftover Leaflet ID if Vite hot-reloaded the component
//     if (container._leaflet_id) {
//       container._leaflet_id = null;
//     }

//     const map = L.map(container, {
//       center: [23.05, 77.0],
//       zoom: 13,
//     });

//     const satelliteLayer = L.tileLayer(
//       "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
//       { attribution: "Esri & ISRO Bhuvan Reference" }
//     );
//     satelliteLayer.addTo(map);
//     baseLayerRef.current = satelliteLayer;

//     L.rectangle(SCENE_BOUNDS, {
//       color: "#38bdf8",
//       weight: 2,
//       dashArray: "6, 6",
//       fillOpacity: 0.03,
//     })
//       .addTo(map)
//       .bindTooltip("ISRO Bhoonidhi Scene Coverage (76.95°E–77.05°E, 23.00°N–23.10°N)", {
//         direction: "top",
//       });

//     drawnLayerRef.current = L.layerGroup().addTo(map);
//     heatmapLayerRef.current = L.layerGroup().addTo(map);
//     mapInstanceRef.current = map;

//     return () => {
//       map.remove();
//       mapInstanceRef.current = null;
//       drawnLayerRef.current = null;
//       heatmapLayerRef.current = null;
//     };
//   }, []);

//   // 2. Switch Base Map Layer
//   useEffect(() => {
//     const map = mapInstanceRef.current;
//     if (!map) return;

//     if (baseLayerRef.current) {
//       map.removeLayer(baseLayerRef.current);
//     }

//     let nextLayer;
//     if (baseMapType === "bhuvan") {
//       const osmFallback = L.tileLayer(
//         "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
//         { attribution: "© OpenStreetMap | ISRO Bhuvan WMS" }
//       );
//       const bhuvanWms = L.tileLayer.wms(
//         "https://bhuvan-vec1.nrsc.gov.in/bhuvan/gwc/service/wms",
//         {
//           layers: "india3",
//           format: "image/png",
//           transparent: true,
//           attribution: "ISRO Bhuvan",
//         }
//       );
//       nextLayer = L.layerGroup([osmFallback, bhuvanWms]);
//     } else if (baseMapType === "street") {
//       nextLayer = L.tileLayer(
//         "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
//         { attribution: "© OpenStreetMap contributors" }
//       );
//     } else {
//       nextLayer = L.tileLayer(
//         "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
//         { attribution: "Satellite Imagery | ISRO Bhoonidhi Data" }
//       );
//     }

//     nextLayer.addTo(map);
//     baseLayerRef.current = nextLayer;
//   }, [baseMapType]);

//   // 3. Handle clicking on the map when Draw Mode is active
//   useEffect(() => {
//     const map = mapInstanceRef.current;
//     if (!map) return;

//     const handleMapClick = (e) => {
//       if (!drawMode) return;
//       const { lat, lng } = e.latlng;
//       setPoints((prev) => [...prev, [Number(lat.toFixed(5)), Number(lng.toFixed(5))]]);
//     };

//     map.on("click", handleMapClick);
//     return () => {
//       map.off("click", handleMapClick);
//     };
//   }, [drawMode]);

//   // 4. Redraw farm polygon & notify parent App whenever points change
//   useEffect(() => {
//     const layerGroup = drawnLayerRef.current;
//     if (!layerGroup) return;

//     layerGroup.clearLayers();

//     points.forEach((pt, idx) => {
//       L.circleMarker(pt, {
//         radius: 5,
//         color: "#38bdf8",
//         fillColor: "#ffffff",
//         fillOpacity: 1,
//         weight: 2,
//       })
//         .addTo(layerGroup)
//         .bindTooltip(`Corner ${idx + 1}`);
//     });

//     if (points.length >= 3) {
//       L.polygon(points, {
//         color: "#38bdf8",
//         weight: 2.5,
//         fillColor: "#38bdf8",
//         fillOpacity: 0.08,
//       }).addTo(layerGroup);

//       const ring = points.map(([lat, lon]) => [lon, lat]);
//       ring.push(ring[0]);

//       onPolygonChange({
//         type: "Polygon",
//         coordinates: [ring],
//       });
//     } else {
//       onPolygonChange(null);
//     }
//   }, [points, onPolygonChange]);

//   // 5. Render Green / Yellow / Red Heatmap cells returned by FastAPI
//   useEffect(() => {
//     const heatGroup = heatmapLayerRef.current;
//     if (!heatGroup) return;

//     heatGroup.clearLayers();
//     if (!Array.isArray(heatmapCells) || heatmapCells.length === 0) return;

//     heatmapCells.forEach((cell) => {
//       const color = STATUS_COLORS[cell.status] || "#10b981";
//       L.rectangle(cell.bounds, {
//         color: color,
//         weight: 0.6,
//         fillColor: color,
//         fillOpacity: 0.58,
//       })
//         .addTo(heatGroup)
//         // .bindPopup(
//         //   `<strong>Status:</strong> ${cell.status.replace("_", " ").toUpperCase()}<br/>
//         //    <strong>Leaf NDVI:</strong> ${cell.ndvi}<br/>
//         //    <strong>Soil Moisture:</strong> ${cell.moisture}%`
//         // );
//         .bindPopup(
//           `<strong>Status:</strong> ${cell.status.replace("_", " ").toUpperCase()}<br/>
//            <strong>Resourcesat NDVI:</strong> ${cell.ndvi}<br/>
//            <strong>EOS-04 Topsoil Moisture:</strong> ${cell.moisture}%<br/>
//            <strong>NISAR Root Moisture:</strong> ${cell.root_moisture ?? cell.moisture}%<br/>
//            <strong>NISAR Canopy Vigor:</strong> ${cell.nisar_vigor ?? "N/A"}`
//         );
//     });
//   }, [heatmapCells]);

//   const applyPreset = (key) => {
//     setDrawMode(false);
//     setPoints(PRESET_FARMS[key].coords);
//   };

//   const startCustomDraw = () => {
//     setPoints([]);
//     setDrawMode(true);
//   };

//   return (
//     <div className="panel">
//       <div className="panel-header">
//         <div className="panel-title">
//           <Layers size={18} color="#38bdf8" />
//           <span>
//             {lang === "hi"
//               ? "खेत का नक्शा और उपग्रह हीटमैप"
//               : "Farm Boundary & Satellite Heatmap"}
//           </span>
//         </div>

//         <div className="control-bar">
//           <button
//             className={`btn ${baseMapType === "satellite" ? "btn-active" : ""}`}
//             onClick={() => setBaseMapType("satellite")}
//           >
//             Satellite
//           </button>
//           <button
//             className={`btn ${baseMapType === "bhuvan" ? "btn-active" : ""}`}
//             onClick={() => setBaseMapType("bhuvan")}
//           >
//             ISRO Bhuvan
//           </button>
//           <button
//             className={`btn ${baseMapType === "street" ? "btn-active" : ""}`}
//             onClick={() => setBaseMapType("street")}
//           >
//             Street
//           </button>
//         </div>
//       </div>

//       <div className="control-bar">
//         <button className="btn" onClick={() => applyPreset("healthy")}>
//           <Sparkles size={14} color="#10b981" />
//           {PRESET_FARMS.healthy.label}
//         </button>
//         <button className="btn" onClick={() => applyPreset("water_stress")}>
//           <Sparkles size={14} color="#ef4444" />
//           {PRESET_FARMS.water_stress.label}
//         </button>
//         <button className="btn" onClick={() => applyPreset("pest_stress")}>
//           <Sparkles size={14} color="#f59e0b" />
//           {PRESET_FARMS.pest_stress.label}
//         </button>
//         <button
//           className={`btn ${drawMode ? "btn-active" : ""}`}
//           onClick={startCustomDraw}
//         >
//           <MousePointerClick size={14} />
//           {drawMode ? "Click Map Corners (3+)" : "Draw Custom Farm"}
//         </button>
//         {points.length > 0 && (
//           <button
//             className="btn"
//             onClick={() => {
//               setPoints([]);
//               setDrawMode(true);
//             }}
//             title="Clear polygon"
//           >
//             <RotateCcw size={14} />
//           </button>
//         )}
//       </div>

//       <div className="map-wrapper">
//         <div ref={mapContainerRef} className="leaflet-map" />
//       </div>

//       <div className="map-legend">
//         <div className="legend-item">
//           <span className="dot" style={{ background: "#10b981" }}></span>
//           <span>{lang === "hi" ? "स्वस्थ फसल (Healthy)" : "Healthy Crop"}</span>
//         </div>
//         <div className="legend-item">
//           <span className="dot" style={{ background: "#ef4444" }}></span>
//           <span>
//             {lang === "hi"
//               ? "पानी की कमी (Water Stress)"
//               : "Water Stress (Needs Irrigation)"}
//           </span>
//         </div>
//         <div className="legend-item">
//           <span className="dot" style={{ background: "#f59e0b" }}></span>
//           <span>
//             {lang === "hi"
//               ? "कीट / पोषक तत्व तनाव (Pest/Nutrient)"
//               : "Pest / Nutrient Stress (Wet Soil)"}
//           </span>
//         </div>
//       </div>
//     </div>
//   );
// }
import { useEffect, useRef, useState } from "react";
import L from "leaflet";
import { Crosshair, Layers, MapPin, MousePointerClick, RotateCcw } from "lucide-react";

const INDIA_HUBS = [
  { name: "Sehore, MP", lat: 23.105, lon: 77.085, zoom: 12 },
  { name: "Ludhiana, Punjab", lat: 30.901, lon: 75.857, zoom: 12 },
  { name: "Yavatmal, Vidarbha", lat: 20.389, lon: 78.131, zoom: 12 },
  { name: "Thanjavur, TN", lat: 10.787, lon: 79.138, zoom: 12 },
  { name: "Varanasi, UP", lat: 25.318, lon: 82.974, zoom: 12 },
];

const STATUS_COLORS = {
  healthy: "#10b981",
  water_stress: "#ef4444",
  pest_nutrient_stress: "#f59e0b",
};

export default function FarmMap({ heatmapCells, selectedBbox, onLocationSelect, lang }) {
  const mapContainerRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const baseLayerRef = useRef(null);
  const selectionLayerRef = useRef(null);
  const heatmapLayerRef = useRef(null);

  const [baseMapType, setBaseMapType] = useState("satellite");
  const [mode, setMode] = useState("point"); // 'point' (click anywhere) | 'polygon' (custom corners)
  const [clickedPoint, setClickedPoint] = useState([23.105, 77.085]);
  const [polyPoints, setPolyPoints] = useState([]);

  // 1. Initialize Pan-India Leaflet Map
  useEffect(() => {
    const container = mapContainerRef.current;
    if (!container) return;
    if (container._leaflet_id) container._leaflet_id = null;

    const map = L.map(container, {
      center: [22.35, 79.0],
      zoom: 5,
      minZoom: 4,
    });

    const satelliteLayer = L.tileLayer(
      "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
      { attribution: "Esri World Imagery | ISRO Bhuvan & NASA Earthdata" }
    );
    satelliteLayer.addTo(map);
    baseLayerRef.current = satelliteLayer;

    selectionLayerRef.current = L.layerGroup().addTo(map);
    heatmapLayerRef.current = L.layerGroup().addTo(map);
    mapInstanceRef.current = map;

    return () => {
      map.remove();
      mapInstanceRef.current = null;
      selectionLayerRef.current = null;
      heatmapLayerRef.current = null;
    };
  }, []);

  // 2. Switch Base Map Layer (Satellite / ISRO Bhuvan WMS / Street)
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map) return;
    if (baseLayerRef.current) map.removeLayer(baseLayerRef.current);

    let nextLayer;
    if (baseMapType === "bhuvan") {
      const osmBase = L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "© OpenStreetMap | ISRO Bhuvan WMS",
      });
      const bhuvanWms = L.tileLayer.wms(
        "https://bhuvan-vec1.nrsc.gov.in/bhuvan/gwc/service/wms",
        {
          layers: "india3",
          format: "image/png",
          transparent: true,
          attribution: "ISRO Bhuvan",
        }
      );
      nextLayer = L.layerGroup([osmBase, bhuvanWms]);
    } else if (baseMapType === "street") {
      nextLayer = L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "© OpenStreetMap contributors",
      });
    } else {
      nextLayer = L.tileLayer(
        "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        { attribution: "Esri Satellite | Live STAC Observation Grid" }
      );
    }

    nextLayer.addTo(map);
    baseLayerRef.current = nextLayer;
  }, [baseMapType]);

  // 3. Handle Click Anywhere in India
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map) return;

    const onMapClick = (e) => {
      const lat = Number(e.latlng.lat.toFixed(5));
      const lon = Number(e.latlng.lng.toFixed(5));

      if (mode === "point") {
        setClickedPoint([lat, lon]);
      } else {
        setPolyPoints((prev) => [...prev, [lat, lon]]);
      }
    };

    map.on("click", onMapClick);
    return () => map.off("click", onMapClick);
  }, [mode]);

  // 4. Sync Selected Point or Polygon to Backend Query
  useEffect(() => {
    const layerGroup = selectionLayerRef.current;
    if (!layerGroup) return;
    layerGroup.clearLayers();

    if (mode === "point" && clickedPoint) {
      const [lat, lon] = clickedPoint;
      L.circleMarker([lat, lon], {
        radius: 7,
        color: "#38bdf8",
        fillColor: "#0ea5e9",
        fillOpacity: 0.9,
        weight: 2.5,
      })
        .addTo(layerGroup)
        .bindTooltip(`Target: ${lat}°N, ${lon}°E`, { direction: "top" });

      if (selectedBbox && selectedBbox.length === 4) {
        const [west, south, east, north] = selectedBbox;
        L.rectangle(
          [
            [south, west],
            [north, east],
          ],
          { color: "#38bdf8", weight: 2, dashArray: "5,5", fillOpacity: 0.05 }
        ).addTo(layerGroup);
      }

      onLocationSelect({
        type: "Point",
        coordinates: [lon, lat],
      });
    } else if (mode === "polygon") {
      polyPoints.forEach((pt, idx) => {
        L.circleMarker(pt, {
          radius: 5,
          color: "#38bdf8",
          fillColor: "#ffffff",
          fillOpacity: 1,
          weight: 2,
        })
          .addTo(layerGroup)
          .bindTooltip(`Corner ${idx + 1}`);
      });

      if (polyPoints.length >= 3) {
        L.polygon(polyPoints, {
          color: "#38bdf8",
          weight: 2.5,
          fillColor: "#38bdf8",
          fillOpacity: 0.08,
        }).addTo(layerGroup);

        const ring = polyPoints.map(([lat, lon]) => [lon, lat]);
        ring.push(ring[0]);
        onLocationSelect({
          type: "Polygon",
          coordinates: [ring],
        });
      }
    }
  }, [mode, clickedPoint, polyPoints, selectedBbox, onLocationSelect]);

  // 5. Render Real Sentinel-2 NDVI Heatmap Cells
  useEffect(() => {
    const heatGroup = heatmapLayerRef.current;
    if (!heatGroup) return;
    heatGroup.clearLayers();
    if (!Array.isArray(heatmapCells) || heatmapCells.length === 0) return;

    heatmapCells.forEach((cell) => {
      const color = STATUS_COLORS[cell.status] || "#10b981";
      L.rectangle(cell.bounds, {
        color,
        weight: 0.5,
        fillColor: color,
        fillOpacity: 0.55,
      })
        .addTo(heatGroup)
        .bindPopup(
          `<strong>Real Pixel NDVI:</strong> ${cell.ndvi}<br/>
           <strong>Topsoil Moisture:</strong> ${cell.moisture}%<br/>
           <strong>Root Moisture (9–27cm):</strong> ${cell.root_moisture}%<br/>
           <strong>C-Band RVI:</strong> ${cell.nisar_vigor}`
        );
    });
  }, [heatmapCells]);

  const jumpToHub = (hub) => {
    setMode("point");
    setClickedPoint([hub.lat, hub.lon]);
    if (mapInstanceRef.current) {
      mapInstanceRef.current.flyTo([hub.lat, hub.lon], hub.zoom, { duration: 1.1 });
    }
  };

  return (
    <div className="panel">
      <div className="panel-header">
        <div className="panel-title">
          <Layers size={18} color="#38bdf8" />
          <span>
            {lang === "hi"
              ? "अखिल भारतीय उपग्रह मानचित्र (कहीं भी क्लिक करें)"
              : "All-India Interactive Satellite Map (Click Anywhere)"}
          </span>
        </div>

        <div className="control-bar">
          <button
            className={`btn ${baseMapType === "satellite" ? "btn-active" : ""}`}
            onClick={() => setBaseMapType("satellite")}
          >
            Satellite
          </button>
          <button
            className={`btn ${baseMapType === "bhuvan" ? "btn-active" : ""}`}
            onClick={() => setBaseMapType("bhuvan")}
          >
            ISRO Bhuvan
          </button>
          <button
            className={`btn ${baseMapType === "street" ? "btn-active" : ""}`}
            onClick={() => setBaseMapType("street")}
          >
            Street
          </button>
        </div>
      </div>

      {/* Mode Switcher & Quick-Jump Indian Agricultural Regions */}
      <div className="control-bar">
        <button
          className={`btn ${mode === "point" ? "btn-active" : ""}`}
          onClick={() => setMode("point")}
        >
          <Crosshair size={14} />
          {lang === "hi" ? "बिंदु चुनें" : "Click Any Location"}
        </button>
        <button
          className={`btn ${mode === "polygon" ? "btn-active" : ""}`}
          onClick={() => {
            setPolyPoints([]);
            setMode("polygon");
          }}
        >
          <MousePointerClick size={14} />
          {mode === "polygon" ? `Draw Polygon (${polyPoints.length} pts)` : "Draw Farm Boundary"}
        </button>
        {mode === "polygon" && polyPoints.length > 0 && (
          <button className="btn" onClick={() => setPolyPoints([])} title="Reset corners">
            <RotateCcw size={14} />
          </button>
        )}
      </div>

      <div className="control-bar">
        <span style={{ fontSize: "0.78rem", color: "#94a3b8", display: "flex", alignItems: "center", gap: 4 }}>
          <MapPin size={13} color="#10b981" /> Quick Jump:
        </span>
        {INDIA_HUBS.map((hub) => (
          <button key={hub.name} className="btn" style={{ padding: "5px 9px", fontSize: "0.78rem" }} onClick={() => jumpToHub(hub)}>
            {hub.name}
          </button>
        ))}
      </div>

      <div className="map-wrapper" style={{ height: "500px" }}>
        <div ref={mapContainerRef} className="leaflet-map" />
      </div>

      <div className="map-legend">
        <div className="legend-item">
          <span className="dot" style={{ background: "#10b981" }}></span>
          <span>Healthy Canopy (NDVI ≥ 0.42)</span>
        </div>
        <div className="legend-item">
          <span className="dot" style={{ background: "#ef4444" }}></span>
          <span>Water Stress (Low Root Moisture)</span>
        </div>
        <div className="legend-item">
          <span className="dot" style={{ background: "#f59e0b" }}></span>
          <span>Low Vigor / Fallow (Adequate Moisture)</span>
        </div>
      </div>
    </div>
  );
}