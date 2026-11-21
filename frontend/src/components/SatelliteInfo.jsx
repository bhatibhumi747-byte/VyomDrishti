const API_BASE = (import.meta.env.VITE_API_BASE_URL || "").replace(/\/$/, "");
import { useEffect, useState } from "react";
import {
  Building2,
  Calendar,
  Compass,
  Cpu,
  Database,
  Layers,
  Radar,
  Satellite,
  Target,
} from "lucide-react";

export default function SatelliteInfo({ lang }) {
  const [satellites, setSatellites] = useState([]);
  const [selectedId, setSelectedId] = useState("all");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch(`${API_BASE}/api/satellites`)
      .then((res) => {
        if (!res.ok) throw new Error("Failed to load satellite catalog.");
        return res.json();
      })
      .then((data) => {
        setSatellites(data.satellites || []);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  const visibleSatellites =
    selectedId === "all"
      ? satellites
      : satellites.filter((sat) => sat.id === selectedId);

  return (
    <div className="sat-info-container">
      {/* Header Banner */}
      <div className="sat-hero">
        <div>
          <span className="brand-badge" style={{ marginBottom: 8, display: "inline-block" }}>
            TRI-SATELLITE CONSTELLATION ARCHITECTURE
          </span>
          <h2>
            {lang === "hi"
              ? "व्योमदृष्टि उपग्रह जानकारी केंद्र (Satellite Information)"
              : "VyomDrishti Satellite Information & Sensor Specifications"}
          </h2>
          <p>
            {lang === "hi"
              ? "यह प्रणाली ऑप्टिकल (Resourcesat-2A), C-बैंड रडार (EOS-04), और L/S-बैंड रडार (NISAR) उपग्रहों के डेटा को मिलाकर सटीक कृषि सलाह देती है।"
              : "Explore the exact orbital platforms, radar/optical instruments, resolutions, and data fusion workflow powering VyomDrishti."}
          </p>
        </div>

        {/* Filter Pills */}
        <div className="control-bar">
          <button
            className={`btn ${selectedId === "all" ? "btn-active" : ""}`}
            onClick={() => setSelectedId("all")}
          >
            All Satellites (3)
          </button>
          {satellites.map((sat) => (
            <button
              key={sat.id}
              className={`btn ${selectedId === sat.id ? "btn-active" : ""}`}
              onClick={() => setSelectedId(sat.id)}
            >
              {sat.name}
            </button>
          ))}
        </div>
      </div>

      {loading && <p style={{ color: "#94a3b8" }}>Loading satellite specifications...</p>}
      {error && <div className="error-banner">{error}</div>}

      {/* Satellite Cards Grid */}
      <div className="sat-grid">
        {visibleSatellites.map((sat) => (
          <article
            key={sat.id}
            className="sat-card"
            style={{ borderTop: `4px solid ${sat.accent_color}` }}
          >
            {/* 1. Satellite Name & Badge */}
            <div className="sat-card-header">
              <div>
                <span
                  className="sat-type-pill"
                  style={{
                    color: sat.accent_color,
                    borderColor: sat.accent_color,
                  }}
                >
                  {sat.badge}
                </span>
                <h3>{sat.name}</h3>
                {/* 2. Full Form & Introduction */}
                <p className="sat-fullform">{sat.full_form}</p>
              </div>
              <Satellite size={28} color={sat.accent_color} />
            </div>

            {/* 3 & 4. Space Agency, Launch Date & Orbit */}
            <div className="sat-meta-grid">
              <div className="sat-meta-item">
                <Building2 size={15} color={sat.accent_color} />
                <div>
                  <span className="meta-label">Space Agency</span>
                  <strong>{sat.agency}</strong>
                </div>
              </div>
              <div className="sat-meta-item">
                <Calendar size={15} color={sat.accent_color} />
                <div>
                  <span className="meta-label">Launch Date</span>
                  <strong>{sat.launch_date}</strong>
                </div>
              </div>
              <div className="sat-meta-item">
                <Compass size={15} color={sat.accent_color} />
                <div>
                  <span className="meta-label">Orbit</span>
                  <strong>{sat.orbit}</strong>
                </div>
              </div>
            </div>

            {/* 5. Mission Objectives */}
            <div className="sat-section">
              <h4>
                <Target size={15} color={sat.accent_color} /> Mission Objectives
              </h4>
              <ul>
                {sat.objectives.map((obj, i) => (
                  <li key={i}>{obj}</li>
                ))}
              </ul>
            </div>

            {/* 6. Sensors & Instruments Used */}
            <div className="sat-section">
              <h4>
                <Radar size={15} color={sat.accent_color} /> Sensors & Instruments
              </h4>
              <ul>
                {sat.sensors.map((sensor, i) => (
                  <li key={i}>{sensor}</li>
                ))}
              </ul>
            </div>

            {/* 7. Data Types & Resolutions */}
            <div className="sat-section">
              <h4>
                <Database size={15} color={sat.accent_color} /> Data Types & Resolutions
              </h4>
              <div className="res-box">
                <div>
                  <span>Format / Data:</span>{" "}
                  <strong>{sat.data_and_resolution.data_type}</strong>
                </div>
                <div>
                  <span>Spatial Resolution:</span>{" "}
                  <strong>{sat.data_and_resolution.spatial_resolution}</strong>
                </div>
                <div>
                  <span>Revisit Cycle:</span>{" "}
                  <strong>{sat.data_and_resolution.revisit_time}</strong>
                </div>
              </div>
            </div>

            {/* 8. Applications & Use Cases */}
            <div className="sat-section">
              <h4>
                <Layers size={15} color={sat.accent_color} /> Key Applications & Use Cases
              </h4>
              <ul>
                {sat.applications.map((appItem, i) => (
                  <li key={i}>{appItem}</li>
                ))}
              </ul>
            </div>

            {/* 9. How Its Data Is Utilized in VyomDrishti */}
            <div
              className="sat-utilization-box"
              style={{ borderLeftColor: sat.accent_color }}
            >
              <h4>
                <Cpu size={15} color={sat.accent_color} /> How It Is Used in VyomDrishti
              </h4>
              <p>{sat.project_utilization}</p>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}