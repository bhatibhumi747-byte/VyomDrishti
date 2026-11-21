
import { useCallback, useEffect, useState } from "react";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import {
  Activity,
  Calendar,
  CheckCircle2,
  CloudRain,
  Droplets,
  Filter,
  Info,
  LayoutDashboard,
  Leaf,
  Loader2,
  MapPin,
  Radio,
  Satellite,
  AlertCircle,
} from "lucide-react";
import FarmMap from "./components/FarmMap";
import SatelliteInfo from "./components/SatelliteInfo";

const API_BASE = (import.meta.env.VITE_API_BASE_URL || "").replace(/\/$/, "");
const API_URL = `${API_BASE}/api/analyze`;

function getDefaultDates() {
  const end = new Date();
  const start = new Date();
  start.setDate(end.getDate() - 30);
  return {
    start: start.toISOString().slice(0, 10),
    end: end.toISOString().slice(0, 10),
  };
}

export default function App() {
  const defaults = getDefaultDates();
  const [activeTab, setActiveTab] = useState("dashboard");
  const [lang, setLang] = useState("en");
  const [geometry, setGeometry] = useState(null);
  const [startDate, setStartDate] = useState(defaults.start);
  const [endDate, setEndDate] = useState(defaults.end);
  const [satelliteFilter, setSatelliteFilter] = useState("all");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [analysis, setAnalysis] = useState(null);

  const handleLocationSelect = useCallback((newGeom) => {
    setGeometry(newGeom);
  }, []);

  const fetchRealSatelliteData = useCallback(async () => {
    if (!geometry) return;

    setLoading(true);
    setError("");

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          geometry,
          start_date: startDate,
          end_date: endDate,
          satellite_filter: satelliteFilter,
        }),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Failed to retrieve satellite observations.");
      }
      setAnalysis(data);
    } catch (err) {
      setError(err.message || "Error connecting to VyomDrishti backend.");
    } finally {
      setLoading(false);
    }
  }, [geometry, startDate, endDate, satelliteFilter]);

  useEffect(() => {
    if (geometry) {
      fetchRealSatelliteData();
    }
  }, [geometry, fetchRealSatelliteData]);

  const fmtVal = (val, suffix = "") =>
    val === null || val === undefined ? "Unavailable" : `${val}${suffix}`;

  return (
    <div>
      {/* Top Navigation Header */}
      <header className="navbar">
        <div className="brand">
          <span className="brand-badge">PAN-INDIA EO PLATFORM</span>
          <div>
            <h1>VyomDrishti</h1>
            <p>
              {lang === "hi"
                ? "अखिल भारतीय वास्तविक-समय उपग्रह कृषि एवं मृदा निगरानी प्रणाली"
                : "All-India Real-Time Multi-Satellite Crop & Soil Monitoring Platform"}
            </p>
          </div>
        </div>

        <nav className="nav-tabs">
          <button
            className={`nav-tab ${activeTab === "dashboard" ? "active" : ""}`}
            onClick={() => setActiveTab("dashboard")}
          >
            <LayoutDashboard size={16} />
            <span>{lang === "hi" ? "अखिल भारतीय विश्लेषण" : "India Satellite Explorer"}</span>
          </button>
          <button
            className={`nav-tab ${activeTab === "satellites" ? "active" : ""}`}
            onClick={() => setActiveTab("satellites")}
          >
            <Info size={16} />
            <span>{lang === "hi" ? "उपग्रह जानकारी" : "Satellite Information"}</span>
          </button>
        </nav>

        <div className="lang-toggle">
          <button
            className={`lang-btn ${lang === "en" ? "active" : ""}`}
            onClick={() => setLang("en")}
          >
            English
          </button>
          <button
            className={`lang-btn ${lang === "hi" ? "active" : ""}`}
            onClick={() => setLang("hi")}
          >
            हिंदी (Hindi)
          </button>
        </div>
      </header>

      {activeTab === "satellites" ? (
        <SatelliteInfo lang={lang} />
      ) : (
        <main className="dashboard-grid">
          {/* Left Column: Pan-India Interactive Map */}
          <FarmMap
            heatmapCells={analysis?.heatmap_cells || []}
            selectedBbox={analysis?.location?.bbox || null}
            onLocationSelect={handleLocationSelect}
            lang={lang}
          />

          {/* Right Column: Filters, Live Satellite Observations & Analytics */}
          <section className="panel">
            <div className="panel-header">
              <div className="panel-title">
                <Satellite size={18} color="#10b981" />
                <span>
                  {lang === "hi"
                    ? "लाइव उपग्रह डेटा और कृषि विश्लेषण"
                    : "Live Satellite Observations & Diagnostics"}
                </span>
              </div>

              <button
                className="btn btn-primary"
                onClick={fetchRealSatelliteData}
                disabled={loading || !geometry}
              >
                {loading ? (
                  <>
                    <Loader2 size={15} className="spin" /> Querying STAC...
                  </>
                ) : (
                  "Refresh Satellite Data"
                )}
              </button>
            </div>

            {/* Interactive Date & Satellite Filters */}
            <div className="slider-card" style={{ gap: 10 }}>
              <div className="control-bar" style={{ justifyContent: "space-between" }}>
                <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: "0.82rem" }}>
                  <Calendar size={14} color="#38bdf8" />
                  <input
                    type="date"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    style={{
                      background: "#0b1320",
                      color: "#f1f5f9",
                      border: "1px solid #263854",
                      borderRadius: 6,
                      padding: "4px 8px",
                    }}
                  />
                  <span>to</span>
                  <input
                    type="date"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    style={{
                      background: "#0b1320",
                      color: "#f1f5f9",
                      border: "1px solid #263854",
                      borderRadius: 6,
                      padding: "4px 8px",
                    }}
                  />
                </div>

                <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: "0.82rem" }}>
                  <Filter size={14} color="#10b981" />
                  <select
                    value={satelliteFilter}
                    onChange={(e) => setSatelliteFilter(e.target.value)}
                    style={{
                      background: "#0b1320",
                      color: "#f1f5f9",
                      border: "1px solid #263854",
                      borderRadius: 6,
                      padding: "5px 8px",
                    }}
                  >
                    <option value="all">All Sensors (Optical + C-SAR + NISAR)</option>
                    <option value="optical">Optical Only (Resourcesat-2A / S2)</option>
                    <option value="eos04">C-Band SAR Only (EOS-04 / S1)</option>
                    <option value="nisar">NISAR L/S-Band Catalog</option>
                  </select>
                </div>
              </div>
            </div>

            {error && <div className="error-banner">{error}</div>}

            {loading && !analysis && (
              <div className="slider-card" style={{ alignItems: "center", padding: 28 }}>
                <Loader2 size={26} color="#38bdf8" />
                <p style={{ fontSize: "0.9rem", color: "#cbd5e1" }}>
                  Querying live STAC satellite archives & reading GeoTIFF pixels...
                </p>
              </div>
            )}

            {analysis && (
              <>
                {/* Selected Indian Location Metadata Banner */}
                <div
                  className="slider-card"
                  style={{
                    flexDirection: "row",
                    justifyContent: "space-between",
                    alignItems: "center",
                    flexWrap: "wrap",
                  }}
                >
                  <div>
                    <div style={{ display: "flex", alignItems: "center", gap: 6, fontWeight: 700, fontSize: "0.95rem" }}>
                      <MapPin size={16} color="#38bdf8" />
                      <span>{analysis.location.name}</span>
                    </div>
                    <div style={{ fontSize: "0.78rem", color: "#94a3b8", marginTop: 2 }}>
                      Coordinates: {analysis.location.lat}°N, {analysis.location.lon}°E • Window:{" "}
                      {analysis.location.date_window}
                    </div>
                  </div>
                  <div style={{ fontSize: "0.8rem", color: "#cbd5e1", textAlign: "right" }}>
                    <div>Temp: <strong>{fmtVal(analysis.metrics.temperature_c, "°C")}</strong></div>
                    <div>7-Day Rain: <strong>{fmtVal(analysis.metrics.precipitation_7d_mm, " mm")}</strong></div>
                  </div>
                </div>

                {/* Evidence-Based Diagnosis Card */}
                <div className={`diagnosis-card ${analysis.diagnosis.status}`}>
                  <h3>
                    {lang === "hi"
                      ? analysis.diagnosis.title_hi
                      : analysis.diagnosis.title_en}
                  </h3>
                  <p>
                    {lang === "hi"
                      ? analysis.diagnosis.action_hi
                      : analysis.diagnosis.action_en}
                  </p>
                </div>

                {/* 3 Real Measurement KPI Cards */}
                <div className="kpi-grid">
                  <div className="kpi-box">
                    <div className="kpi-label">
                      <Leaf size={13} style={{ marginRight: 4 }} />
                      Real Optical NDVI
                    </div>
                    <div className="kpi-value" style={{ color: "#10b981" }}>
                      {fmtVal(analysis.metrics.mean_ndvi)}
                    </div>
                    <div className="kpi-sub">
                      Cloud Cover: {fmtVal(analysis.metrics.cloud_cover_pct, "%")}
                    </div>
                  </div>

                  <div className="kpi-box">
                    <div className="kpi-label">
                      <Droplets size={13} style={{ marginRight: 4 }} />
                      Topsoil / Root Moisture
                    </div>
                    <div className="kpi-value" style={{ color: "#38bdf8" }}>
                      {fmtVal(analysis.metrics.topsoil_moisture_pct, "%")} /{" "}
                      <span style={{ color: "#a855f7" }}>
                        {fmtVal(analysis.metrics.root_zone_moisture_pct, "%")}
                      </span>
                    </div>
                    <div className="kpi-sub">0–1 cm & 9–27 cm Depth</div>
                  </div>

                  <div className="kpi-box">
                    <div className="kpi-label">
                      <Radio size={13} style={{ marginRight: 4 }} />
                      C-Band SAR RVI / VV
                    </div>
                    <div className="kpi-value" style={{ color: "#a855f7" }}>
                      {fmtVal(analysis.metrics.nisar_biomass_vigor)}
                    </div>
                    <div className="kpi-sub">
                      Backscatter: {fmtVal(analysis.metrics.c_band_vv_db, " dB")}
                    </div>
                  </div>
                </div>

                {/* Live Satellite Provenance & Scene Pass Ledger */}
                <div className="chart-box" style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                  <div className="chart-title" style={{ marginBottom: 2 }}>
                    Data Provenance & Live Orbital Pass Verification
                  </div>

                  {/* Optical Pass */}
                  <div style={{ fontSize: "0.8rem", display: "flex", gap: 8, alignItems: "flex-start" }}>
                    {analysis.observations.optical.available ? (
                      <CheckCircle2 size={15} color="#10b981" style={{ marginTop: 2, flexShrink: 0 }} />
                    ) : (
                      <AlertCircle size={15} color="#f59e0b" style={{ marginTop: 2, flexShrink: 0 }} />
                    )}
                    <div>
                      <strong>Optical (Resourcesat-2A / Sentinel-2 L2A): </strong>
                      {analysis.observations.optical.available ? (
                        <span style={{ color: "#cbd5e1" }}>
                          {analysis.observations.optical.provenance} — Scene{" "}
                          <code>{analysis.observations.optical.scene_id}</code> (
                          {analysis.observations.optical.observation_date})
                        </span>
                      ) : (
                        <span style={{ color: "#fbbf24" }}>{analysis.observations.optical.reason}</span>
                      )}
                    </div>
                  </div>

                  {/* C-Band SAR Pass */}
                  <div style={{ fontSize: "0.8rem", display: "flex", gap: 8, alignItems: "flex-start" }}>
                    {analysis.observations.c_band_sar.available ? (
                      <CheckCircle2 size={15} color="#38bdf8" style={{ marginTop: 2, flexShrink: 0 }} />
                    ) : (
                      <AlertCircle size={15} color="#f59e0b" style={{ marginTop: 2, flexShrink: 0 }} />
                    )}
                    <div>
                      <strong>C-Band SAR (EOS-04 Equivalent): </strong>
                      {analysis.observations.c_band_sar.available ? (
                        <span style={{ color: "#cbd5e1" }}>
                          {analysis.observations.c_band_sar.provenance} — Scene{" "}
                          <code>{analysis.observations.c_band_sar.scene_id}</code> (
                          {analysis.observations.c_band_sar.observation_date})
                        </span>
                      ) : (
                        <span style={{ color: "#fbbf24" }}>{analysis.observations.c_band_sar.reason}</span>
                      )}
                    </div>
                  </div>

                  {/* NISAR Pass */}
                  <div style={{ fontSize: "0.8rem", display: "flex", gap: 8, alignItems: "flex-start" }}>
                    {analysis.observations.nisar.available ? (
                      <CheckCircle2 size={15} color="#a855f7" style={{ marginTop: 2, flexShrink: 0 }} />
                    ) : (
                      <AlertCircle size={15} color="#94a3b8" style={{ marginTop: 2, flexShrink: 0 }} />
                    )}
                    <div>
                      <strong>NISAR (NASA-ISRO L/S-Band SAR): </strong>
                      {analysis.observations.nisar.available ? (
                        <span style={{ color: "#cbd5e1" }}>
                          {analysis.observations.nisar.provenance} — Granule{" "}
                          <code>{analysis.observations.nisar.granule_id}</code> (
                          {analysis.observations.nisar.observation_date})
                        </span>
                      ) : (
                        <span style={{ color: "#94a3b8" }}>{analysis.observations.nisar.reason}</span>
                      )}
                    </div>
                  </div>
                </div>

                {/* 7-Day Real Soil Moisture & Observed NDVI Trend Chart */}
                {analysis.seasonal_trend && analysis.seasonal_trend.length > 0 && (
                  <div className="chart-box">
                    <div className="chart-title">
                      7-Day Soil Moisture Profile (0–1 cm Topsoil vs. 9–27 cm Root Zone)
                    </div>
                    <div style={{ width: "100%", height: 195 }}>
                      <ResponsiveContainer>
                        <LineChart data={analysis.seasonal_trend}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#263854" />
                          <XAxis dataKey="week" stroke="#94a3b8" fontSize={12} />
                          <YAxis domain={[0, 100]} stroke="#38bdf8" fontSize={12} />
                          <Tooltip
                            contentStyle={{
                              backgroundColor: "#0b1320",
                              borderColor: "#263854",
                              color: "#f1f5f9",
                            }}
                          />
                          <Legend />
                          <Line
                            type="monotone"
                            dataKey="moisture"
                            name="Topsoil Moisture 0–1cm (%)"
                            stroke="#38bdf8"
                            strokeWidth={2.5}
                            dot={{ r: 3 }}
                          />
                          <Line
                            type="monotone"
                            dataKey="root_moisture"
                            name="Root-Zone Moisture 9–27cm (%)"
                            stroke="#a855f7"
                            strokeWidth={2.5}
                            dot={{ r: 3 }}
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                )}
              </>
            )}
          </section>
        </main>
      )}
    </div>
  );
}