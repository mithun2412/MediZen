import { useState, useEffect } from "react";
import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  useMap,
} from "react-leaflet";

import L from "leaflet";

import "leaflet/dist/leaflet.css";

// ─────────────────────────────────────────────────────────
// FIX LEAFLET ICONS
// ─────────────────────────────────────────────────────────
delete L.Icon.Default.prototype._getIconUrl;

L.Icon.Default.mergeOptions({
  iconRetinaUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png",

  iconUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png",

  shadowUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png",
});

// USER ICON
const userIcon = new L.Icon({
  iconUrl:
    "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png",

  shadowUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png",

  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
});

// HOSPITAL ICON
const hospitalIcon = new L.Icon({
  iconUrl:
    "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png",

  shadowUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png",

  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
});

// ─────────────────────────────────────────────────────────
// DISEASE MAPPING
// ─────────────────────────────────────────────────────────
const DISEASE_MAP = {
  "chest pain": {
    label: "Cardiac Hospital",
  },

  heart: {
    label: "Cardiac Hospital",
  },

  stroke: {
    label: "Neurology Hospital",
  },

  seizure: {
    label: "Neurology Hospital",
  },

  fracture: {
    label: "Orthopedic Hospital",
  },

  bone: {
    label: "Orthopedic Hospital",
  },

  eye: {
    label: "Eye Hospital",
  },

  child: {
    label: "Children Hospital",
  },

  cancer: {
    label: "Cancer Hospital",
  },

  kidney: {
    label: "Nephrology Hospital",
  },

  breathing: {
    label: "Pulmonology Hospital",
  },

  lungs: {
    label: "Pulmonology Hospital",
  },

  skin: {
    label: "Dermatology Hospital",
  },

  mental: {
    label: "Psychiatric Hospital",
  },

  depression: {
    label: "Psychiatric Hospital",
  },

  pregnancy: {
    label: "Maternity Hospital",
  },

  fever: {
    label: "General Hospital",
  },

  infection: {
    label: "General Hospital",
  },
};

// ─────────────────────────────────────────────────────────
// GET HOSPITAL INFO
// ─────────────────────────────────────────────────────────
function getHospitalInfo(disease = "") {
  const lower = disease.toLowerCase();

  for (const [key, val] of Object.entries(DISEASE_MAP)) {
    if (lower.includes(key)) {
      return val;
    }
  }

  return {
    label: "General Hospital",
  };
}

// ─────────────────────────────────────────────────────────
// MAP CONTROLLER
// ─────────────────────────────────────────────────────────
function MapController({ center }) {
  const map = useMap();

  useEffect(() => {
    if (center) {
      map.setView(center, 14);
    }
  }, [center]);

  return null;
}

// ─────────────────────────────────────────────────────────
// MAIN COMPONENT
// ─────────────────────────────────────────────────────────
export default function HospitalFinder({
  disease = "",
  autoSearch = false,
}) {
  const [hospitals, setHospitals] = useState([]);

  const [userLocation, setUserLocation] = useState(null);

  const [hospitalInfo, setHospitalInfo] = useState(null);

  const [loading, setLoading] = useState(false);

  const [error, setError] = useState("");

  const [searched, setSearched] = useState(false);

  // AUTO SEARCH
  useEffect(() => {
    if (autoSearch && disease) {
      findHospitals();
    }
  }, [autoSearch, disease]);

  // ─────────────────────────────────────────────────────────
  // GET USER LOCATION
  // ─────────────────────────────────────────────────────────
  const getLocation = () =>
    new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        reject("Geolocation not supported.");
        return;
      }

      navigator.geolocation.getCurrentPosition(
        (pos) => {
          resolve({
            lat: pos.coords.latitude,
            lng: pos.coords.longitude,
          });
        },

        () => {
          reject(
            "Location access denied. Please allow location access."
          );
        }
      );
    });

  // ─────────────────────────────────────────────────────────
  // FETCH HOSPITALS
  // ─────────────────────────────────────────────────────────
  const fetchHospitals = async (lat, lng) => {
    const radius = 5000;

    const query = `
      [out:json][timeout:25];
      (
        node["amenity"="hospital"](around:${radius},${lat},${lng});
        way["amenity"="hospital"](around:${radius},${lat},${lng});
        node["healthcare"="hospital"](around:${radius},${lat},${lng});
        way["healthcare"="hospital"](around:${radius},${lat},${lng});
      );
      out center 10;
    `;

    const res = await fetch(
      "https://overpass-api.de/api/interpreter",
      {
        method: "POST",
        body: query,
      }
    );

    const data = await res.json();

    return data.elements
      .map((el) => {
        const elLat = el.lat ?? el.center?.lat;

        const elLng = el.lon ?? el.center?.lon;

        if (!elLat || !elLng) return null;

        const name =
          el.tags?.name ||
          el.tags?.["name:en"] ||
          "Hospital";

        const address =
          [
            el.tags?.["addr:street"],
            el.tags?.["addr:city"],
          ]
            .filter(Boolean)
            .join(", ") || "Address not available";

        const phone =
          el.tags?.phone ||
          el.tags?.["contact:phone"] ||
          null;

        // DISTANCE
        const dist = (
          Math.sqrt(
            Math.pow(elLat - lat, 2) +
              Math.pow(elLng - lng, 2)
          ) * 111
        ).toFixed(1);

        return {
          name,
          address,
          phone,
          lat: elLat,
          lng: elLng,
          distance: dist,

          directions_url: `https://www.google.com/maps/dir/?api=1&destination=${elLat},${elLng}`,
        };
      })

      .filter(Boolean)

      .sort((a, b) => a.distance - b.distance)

      .slice(0, 8);
  };

  // ─────────────────────────────────────────────────────────
  // FIND HOSPITALS
  // ─────────────────────────────────────────────────────────
  const findHospitals = async () => {
    setLoading(true);

    setError("");

    setSearched(true);

    setHospitals([]);

    let location;

    try {
      location = await getLocation();

      setUserLocation(location);
    } catch (err) {
      setError(err);

      setLoading(false);

      return;
    }

    const info = getHospitalInfo(disease);

    setHospitalInfo(info);

    try {
      const results = await fetchHospitals(
        location.lat,
        location.lng
      );

      setHospitals(results);

      if (results.length === 0) {
        setError(
          "No hospitals found within 5km."
        );
      }
    } catch (err) {
      setError(
        "Failed to fetch hospitals."
      );
    } finally {
      setLoading(false);
    }
  };

  // ─────────────────────────────────────────────────────────
  // UI
  // ─────────────────────────────────────────────────────────
  return (
    <div>

      {/* HEADER */}
      <div className="bg-white rounded-2xl shadow-lg p-6 mb-4">

        <div className="flex items-start justify-between gap-4 flex-wrap">

          <div>
            <h2 className="text-gray-800 font-bold text-lg flex items-center gap-2">
              🏥 Nearby Hospital Finder
            </h2>

            {disease && hospitalInfo && (
              <p className="text-gray-500 text-sm mt-1">
                Searching for{" "}
                <span className="text-indigo-600 font-semibold">
                  {hospitalInfo.label}
                </span>

                {" "}based on:

                <em className="text-gray-600">
                  {" "}
                  "{disease}"
                </em>
              </p>
            )}

            <p className="text-gray-400 text-xs mt-1">
              📍 Uses your location
            </p>
          </div>

          <button
            onClick={findHospitals}
            disabled={loading}
            className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold px-5 py-2.5 rounded-xl transition disabled:opacity-50 text-sm whitespace-nowrap"
          >
            {loading
              ? "🔍 Searching..."
              : searched
              ? "🔄 Search Again"
              : "📍 Find Hospitals"}
          </button>
        </div>

        {/* ERROR */}
        {error && (
          <div className="bg-red-50 border border-red-300 text-red-700 rounded-xl p-3 mt-4 text-sm">
            ⚠️ {error}
          </div>
        )}
      </div>

      {/* MAP */}
      {userLocation && (
        <div
          className="bg-white rounded-2xl shadow-lg overflow-hidden mb-4"
          style={{ height: 320 }}
        >
          <MapContainer
            center={[
              userLocation.lat,
              userLocation.lng,
            ]}

            zoom={14}

            style={{
              height: "100%",
              width: "100%",
            }}

            scrollWheelZoom={false}
          >
            <TileLayer
              attribution='&copy; OpenStreetMap contributors'

              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />

            <MapController
              center={[
                userLocation.lat,
                userLocation.lng,
              ]}
            />

            {/* USER MARKER */}
            <Marker
              position={[
                userLocation.lat,
                userLocation.lng,
              ]}

              icon={userIcon}
            >
              <Popup>
                <strong>
                  📍 You are here
                </strong>
              </Popup>
            </Marker>

            {/* HOSPITAL MARKERS */}
            {hospitals.map((h, i) => (
              <Marker
                key={i}
                position={[h.lat, h.lng]}
                icon={hospitalIcon}
              >
                <Popup>
                  <div style={{ minWidth: 160 }}>

                    <p
                      style={{
                        fontWeight: 600,
                        margin: "0 0 4px",
                      }}
                    >
                      {h.name}
                    </p>

                    <p
                      style={{
                        fontSize: 12,
                        color: "#666",
                        margin: "0 0 4px",
                      }}
                    >
                      {h.address}
                    </p>

                    <p
                      style={{
                        fontSize: 12,
                        margin: "0 0 6px",
                      }}
                    >
                      📏 {h.distance} km away
                    </p>

                    {h.phone && (
                      <p
                        style={{
                          fontSize: 12,
                          margin: "0 0 6px",
                        }}
                      >
                        📞 {h.phone}
                      </p>
                    )}

                    <a
                      href={h.directions_url}
                      target="_blank"
                      rel="noreferrer"

                      style={{
                        fontSize: 12,
                        color: "#6366f1",
                        fontWeight: 600,
                      }}
                    >
                      Get Directions →
                    </a>
                  </div>
                </Popup>
              </Marker>
            ))}
          </MapContainer>
        </div>
      )}

      {/* HOSPITAL LIST */}
      {hospitals.length > 0 && (
        <div className="space-y-3">

          <p className="text-gray-600 text-sm font-semibold">
            Found {hospitals.length} hospitals nearby
          </p>

          {hospitals.map((h, i) => (
            <div
              key={i}
              className="bg-white rounded-2xl shadow p-4 flex gap-4 items-start"
            >

              {/* NUMBER */}
              <div className="w-9 h-9 rounded-full bg-red-100 text-red-600 font-bold text-sm flex items-center justify-center flex-shrink-0">
                {i + 1}
              </div>

              {/* DETAILS */}
              <div className="flex-1 min-w-0">

                <p className="font-semibold text-gray-800 text-sm truncate">
                  {h.name}
                </p>

                <p className="text-gray-500 text-xs mt-0.5">
                  {h.address}
                </p>

                <div className="flex items-center gap-3 mt-2 flex-wrap">

                  <span className="text-xs text-indigo-600 font-semibold bg-indigo-50 px-2 py-0.5 rounded-full">
                    📏 {h.distance} km
                  </span>

                  {h.phone && (
                    <a
                      href={`tel:${h.phone}`}
                      className="text-xs text-green-600 font-semibold bg-green-50 px-2 py-0.5 rounded-full"
                    >
                      📞 {h.phone}
                    </a>
                  )}
                </div>
              </div>

              {/* BUTTON */}
              <a
                href={h.directions_url}
                target="_blank"
                rel="noreferrer"
                className="bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold px-3 py-2 rounded-xl transition whitespace-nowrap flex-shrink-0"
              >
                Directions →
              </a>

            </div>
          ))}
        </div>
      )}

      {/* EMPTY STATE */}
      {searched &&
        !loading &&
        hospitals.length === 0 &&
        !error && (
          <div className="text-center text-gray-400 py-10">

            <p className="text-4xl mb-3">
              🏥
            </p>

            <p>No hospitals found nearby.</p>

            <p className="text-sm mt-1">
              Try allowing location access.
            </p>
          </div>
        )}
    </div>
  );
}