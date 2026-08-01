import { useEffect, useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  MapPin,
  Navigation,
  Phone,
  Star,
  Clock,
  ExternalLink,
  X,
  Loader2,
  Hospital,
  Ambulance,
  Stethoscope
} from "lucide-react";

// ─────────────────────────────────────────────
// HOSPITAL MAP COMPONENT
// ─────────────────────────────────────────────

export default function HospitalMap({
  hospitals = [],
  userLocation = null,
  onClose = null,
  isOpen = false
}) {
  const [selectedHospital, setSelectedHospital] = useState(null);
  const [loading, setLoading] = useState(false);
  const [mapLoaded, setMapLoaded] = useState(false);
  const mapContainerRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const markersRef = useRef([]);

  // ─────────────────────────
  // LOAD GOOGLE MAPS SCRIPT
  // ─────────────────────────

  useEffect(() => {
    if (!isOpen) return;

    // Load Google Maps script
    const loadGoogleMaps = () => {
      if (window.google && window.google.maps) {
        setMapLoaded(true);
        return;
      }

      const script = document.createElement("script");
      script.src = `https://maps.googleapis.com/maps/api/js?key=YOUR_GOOGLE_MAPS_API_KEY&libraries=places`;
      script.async = true;
      script.defer = true;
      script.onload = () => {
        setMapLoaded(true);
      };
      script.onerror = () => {
        console.error("Failed to load Google Maps");
      };
      document.head.appendChild(script);
    };

    loadGoogleMaps();

    return () => {
      // Cleanup markers
      if (markersRef.current.length > 0) {
        markersRef.current.forEach(marker => {
          if (marker.setMap) {
            marker.setMap(null);
          }
        });
        markersRef.current = [];
      }
    };
  }, [isOpen]);

  // ─────────────────────────
  // INITIALIZE MAP
  // ─────────────────────────

  useEffect(() => {
    if (!mapLoaded || !mapContainerRef.current || !isOpen) return;

    try {
      const defaultLocation = userLocation || { lat: 28.6139, lng: 77.2090 };
      
      // Create map
      const map = new window.google.maps.Map(mapContainerRef.current, {
        center: defaultLocation,
        zoom: 13,
        styles: getMapStyles(),
        mapTypeControl: false,
        streetViewControl: false,
        fullscreenControl: false,
        zoomControl: true,
        zoomControlOptions: {
          position: window.google.maps.ControlPosition.RIGHT_BOTTOM
        }
      });

      mapInstanceRef.current = map;

      // Add user location marker
      addUserMarker(map, defaultLocation);

      // Add hospital markers
      if (hospitals.length > 0) {
        addHospitalMarkers(map, hospitals);
      }

      // Fit bounds to show all markers
      fitBounds(map, hospitals, defaultLocation);

    } catch (error) {
      console.error("Error initializing map:", error);
    }

    return () => {
      if (mapInstanceRef.current) {
        // Cleanup
      }
    };
  }, [mapLoaded, hospitals, userLocation, isOpen]);

  // ─────────────────────────
  // ADD USER LOCATION MARKER
  // ─────────────────────────

  const addUserMarker = (map, location) => {
    try {
      const marker = new window.google.maps.Marker({
        position: location,
        map: map,
        icon: {
          path: window.google.maps.SymbolPath.CIRCLE,
          fillColor: "#06b6d4",
          fillOpacity: 1,
          strokeColor: "#ffffff",
          strokeWeight: 3,
          scale: 10
        },
        zIndex: 1000,
        title: "Your Location"
      });

      // Add pulse animation
      const pulseCircle = new window.google.maps.Circle({
        map: map,
        center: location,
        radius: 50,
        fillColor: "#06b6d4",
        fillOpacity: 0.2,
        strokeColor: "#06b6d4",
        strokeOpacity: 0.4,
        strokeWeight: 2
      });

      // Animate pulse
      let radius = 50;
      let growing = true;
      setInterval(() => {
        if (growing) {
          radius += 5;
          if (radius > 150) growing = false;
        } else {
          radius -= 5;
          if (radius < 50) growing = true;
        }
        pulseCircle.setRadius(radius);
      }, 100);

      markersRef.current.push(marker);
      markersRef.current.push(pulseCircle);
    } catch (error) {
      console.error("Error adding user marker:", error);
    }
  };

  // ─────────────────────────
  // ADD HOSPITAL MARKERS
  // ─────────────────────────

  const addHospitalMarkers = (map, hospitals) => {
    try {
      hospitals.forEach((hospital, index) => {
        const position = {
          lat: hospital.latitude || hospital.lat || 0,
          lng: hospital.longitude || hospital.lng || 0
        };

        if (!position.lat || !position.lng) return;

        // Create custom marker
        const marker = new window.google.maps.Marker({
          position: position,
          map: map,
          icon: getHospitalIcon(index),
          zIndex: 999 - index,
          title: hospital.name || "Hospital"
        });

        // Create info window
        const infoWindow = new window.google.maps.InfoWindow({
          content: getInfoWindowContent(hospital)
        });

        // Add click listener
        marker.addListener("click", () => {
          setSelectedHospital(hospital);
          infoWindow.open(map, marker);
        });

        markersRef.current.push(marker);
      });
    } catch (error) {
      console.error("Error adding hospital markers:", error);
    }
  };

  // ─────────────────────────
  // FIT BOUNDS
  // ─────────────────────────

  const fitBounds = (map, hospitals, userLocation) => {
    try {
      const bounds = new window.google.maps.LatLngBounds();
      
      // Add user location
      if (userLocation) {
        bounds.extend(userLocation);
      }

      // Add hospital locations
      hospitals.forEach(hospital => {
        const lat = hospital.latitude || hospital.lat;
        const lng = hospital.longitude || hospital.lng;
        if (lat && lng) {
          bounds.extend({ lat, lng });
        }
      });

      // If no markers, set default zoom
      if (bounds.isEmpty()) {
        map.setZoom(13);
        return;
      }

      // Fit bounds with padding
      map.fitBounds(bounds, { top: 50, bottom: 50, left: 50, right: 50 });

      // Don't zoom too far
      const listener = window.google.maps.event.addListener(map, "zoom_changed", () => {
        if (map.getZoom() > 15) {
          map.setZoom(15);
        }
        window.google.maps.event.removeListener(listener);
      });

    } catch (error) {
      console.error("Error fitting bounds:", error);
    }
  };

  // ─────────────────────────
  // GET HOSPITAL ICON
  // ─────────────────────────

  const getHospitalIcon = (index) => {
    const colors = ["#3b82f6", "#06b6d4", "#8b5cf6", "#ec4899", "#f59e0b"];
    const color = colors[index % colors.length];

    return {
      path: "M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z",
      fillColor: color,
      fillOpacity: 1,
      strokeColor: "#ffffff",
      strokeWeight: 2,
      scale: 1.2,
      anchor: new window.google.maps.Point(12, 22)
    };
  };

  // ─────────────────────────
  // GET INFO WINDOW CONTENT
  // ─────────────────────────

  const getInfoWindowContent = (hospital) => {
    return `
      <div style="padding: 12px 16px; max-width: 250px; font-family: system-ui, sans-serif;">
        <h3 style="font-weight: 600; font-size: 16px; color: #1a1a1a; margin-bottom: 4px;">
          ${hospital.name || "Hospital"}
        </h3>
        ${hospital.address ? `<p style="color: #666; font-size: 13px; margin-bottom: 8px;">${hospital.address}</p>` : ""}
        ${hospital.distance ? `<p style="color: #06b6d4; font-size: 13px; font-weight: 500;">📏 ${hospital.distance.toFixed(1)} km away</p>` : ""}
        ${hospital.rating ? `<p style="color: #f59e0b; font-size: 13px;">⭐ ${hospital.rating} / 5</p>` : ""}
        <button onclick="window.selectHospital(${JSON.stringify(hospital)})" style="
          margin-top: 8px;
          background: #06b6d4;
          color: white;
          border: none;
          padding: 6px 16px;
          border-radius: 8px;
          font-weight: 500;
          cursor: pointer;
          font-size: 13px;
        ">View Details</button>
      </div>
    `;
  };

  // ─────────────────────────
  // GET MAP STYLES
  // ─────────────────────────

  const getMapStyles = () => {
    return [
      {
        featureType: "all",
        elementType: "labels.text.fill",
        stylers: [{ color: "#6b7280" }]
      },
      {
        featureType: "water",
        elementType: "geometry",
        stylers: [{ color: "#e5e7eb" }]
      },
      {
        featureType: "road.highway",
        elementType: "geometry",
        stylers: [{ color: "#d1d5db" }]
      },
      {
        featureType: "road.arterial",
        elementType: "geometry",
        stylers: [{ color: "#e5e7eb" }]
      },
      {
        featureType: "road.local",
        elementType: "geometry",
        stylers: [{ color: "#f3f4f6" }]
      },
      {
        featureType: "poi.park",
        elementType: "geometry",
        stylers: [{ color: "#dcfce7" }]
      }
    ];
  };

  // ─────────────────────────
  // OPEN GOOGLE MAPS
  // ─────────────────────────

  const openGoogleMaps = (hospital) => {
    const lat = hospital.latitude || hospital.lat;
    const lng = hospital.longitude || hospital.lng;
    const name = hospital.name || "Hospital";
    
    if (lat && lng) {
      window.open(
        `https://www.google.com/maps/dir/?api=1&destination=${lat},${lng}&destination_place_id=${name}`,
        "_blank"
      );
    } else {
      window.open(
        `https://www.google.com/maps/search/${encodeURIComponent(name)}`,
        "_blank"
      );
    }
  };

  // ─────────────────────────
  // RENDER HOSPITAL LIST
  // ─────────────────────────

  const renderHospitalList = () => {
    if (hospitals.length === 0) {
      return (
        <div className="flex flex-col items-center justify-center h-full text-slate-400">
          <Hospital className="w-12 h-12 mb-3 opacity-50" />
          <p className="text-center">No hospitals found nearby</p>
          <p className="text-sm mt-1">Try adjusting your location</p>
        </div>
      );
    }

    return (
      <div className="space-y-3 max-h-[400px] overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-white/10">
        {hospitals.map((hospital, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
            className={`p-4 rounded-2xl border transition-all cursor-pointer ${
              selectedHospital === hospital
                ? "bg-cyan-500/10 border-cyan-400/30"
                : "bg-white/5 border-white/10 hover:bg-white/10"
            }`}
            onClick={() => setSelectedHospital(hospital)}
          >
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 rounded-xl bg-cyan-400/20 flex items-center justify-center flex-shrink-0">
                <Hospital className="w-5 h-5 text-cyan-400" />
              </div>
              
              <div className="flex-1 min-w-0">
                <h4 className="font-medium text-sm text-white">
                  {hospital.name || "Medical Facility"}
                </h4>
                
                {hospital.address && (
                  <p className="text-xs text-slate-400 mt-0.5 line-clamp-1">
                    {hospital.address}
                  </p>
                )}
                
                <div className="flex items-center gap-3 mt-1.5">
                  {hospital.distance && (
                    <span className="text-xs text-cyan-400 flex items-center gap-0.5">
                      <Navigation className="w-3 h-3" />
                      {hospital.distance.toFixed(1)} km
                    </span>
                  )}
                  
                  {hospital.rating && (
                    <span className="text-xs text-amber-400 flex items-center gap-0.5">
                      <Star className="w-3 h-3 fill-amber-400" />
                      {hospital.rating}
                    </span>
                  )}
                  
                  {hospital.phone && (
                    <span className="text-xs text-slate-400 flex items-center gap-0.5">
                      <Phone className="w-3 h-3" />
                      {hospital.phone}
                    </span>
                  )}
                </div>
              </div>

              <button
                onClick={(e) => {
                  e.stopPropagation();
                  openGoogleMaps(hospital);
                }}
                className="w-8 h-8 rounded-lg bg-cyan-400/10 hover:bg-cyan-400/20 flex items-center justify-center transition flex-shrink-0"
              >
                <ExternalLink className="w-4 h-4 text-cyan-400" />
              </button>
            </div>
          </motion.div>
        ))}
      </div>
    );
  };

  // ─────────────────────────
  // MODAL CONTENT
  // ─────────────────────────

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4"
        onClick={(e) => {
          if (e.target === e.currentTarget && onClose) {
            onClose();
          }
        }}
      >
        <motion.div
          initial={{ scale: 0.9, y: 20 }}
          animate={{ scale: 1, y: 0 }}
          exit={{ scale: 0.9, y: 20 }}
          className="bg-black border border-white/10 rounded-3xl w-full max-w-5xl max-h-[90vh] overflow-hidden shadow-2xl"
        >
          {/* HEADER */}
          <div className="flex items-center justify-between px-6 py-4 border-b border-white/10 bg-white/5">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-cyan-400/20 flex items-center justify-center">
                <MapPin className="w-5 h-5 text-cyan-400" />
              </div>
              <div>
                <h2 className="text-lg font-bold text-white">
                  Nearby Hospitals
                </h2>
                <p className="text-xs text-slate-400">
                  {hospitals.length} hospitals found nearby
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => {
                  if (userLocation) {
                    window.open(
                      `https://www.google.com/maps/search/hospitals/@${userLocation.lat},${userLocation.lng},13z`,
                      "_blank"
                    );
                  }
                }}
                className="px-4 py-2 rounded-xl bg-cyan-400/10 hover:bg-cyan-400/20 text-cyan-400 text-sm font-medium transition flex items-center gap-2"
              >
                <ExternalLink className="w-4 h-4" />
                Open in Maps
              </button>
              
              {onClose && (
                <button
                  onClick={onClose}
                  className="w-10 h-10 rounded-xl bg-white/5 hover:bg-white/10 transition flex items-center justify-center"
                >
                  <X className="w-5 h-5 text-slate-400" />
                </button>
              )}
            </div>
          </div>

          {/* MAP & LIST */}
          <div className="flex flex-col lg:flex-row">
            {/* MAP */}
            <div className="lg:flex-1 h-[300px] lg:h-[500px] bg-slate-900/50 relative">
              {!mapLoaded && (
                <div className="absolute inset-0 flex flex-col items-center justify-center text-slate-400">
                  <Loader2 className="w-8 h-8 animate-spin mb-3" />
                  <p>Loading map...</p>
                </div>
              )}
              
              <div
                ref={mapContainerRef}
                className="w-full h-full"
                style={{ display: mapLoaded ? "block" : "none" }}
              />

              {/* Map Legend */}
              <div className="absolute bottom-4 left-4 bg-black/80 backdrop-blur-md rounded-xl px-3 py-2 border border-white/10">
                <div className="flex items-center gap-2 text-xs text-slate-300">
                  <div className="flex items-center gap-1">
                    <div className="w-3 h-3 rounded-full bg-cyan-400 ring-2 ring-white/30" />
                    <span>You</span>
                  </div>
                  <div className="w-px h-3 bg-white/10" />
                  <div className="flex items-center gap-1">
                    <MapPin className="w-3 h-3 text-blue-400" />
                    <span>Hospitals</span>
                  </div>
                </div>
              </div>

              {/* Selected Hospital Info */}
              {selectedHospital && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="absolute bottom-4 right-4 max-w-xs bg-black/90 backdrop-blur-xl rounded-2xl border border-white/10 p-4 shadow-2xl"
                >
                  <div className="flex items-start gap-3">
                    <div className="w-10 h-10 rounded-xl bg-cyan-400/20 flex items-center justify-center flex-shrink-0">
                      <Hospital className="w-5 h-5 text-cyan-400" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h4 className="font-medium text-white text-sm">
                        {selectedHospital.name || "Hospital"}
                      </h4>
                      {selectedHospital.address && (
                        <p className="text-xs text-slate-400 mt-0.5">
                          {selectedHospital.address}
                        </p>
                      )}
                      {selectedHospital.distance && (
                        <p className="text-xs text-cyan-400 mt-1">
                          📏 {selectedHospital.distance.toFixed(1)} km away
                        </p>
                      )}
                    </div>
                  </div>
                  <button
                    onClick={() => openGoogleMaps(selectedHospital)}
                    className="mt-3 w-full py-2 bg-cyan-400 hover:bg-cyan-300 text-black font-medium rounded-xl transition text-sm"
                  >
                    Get Directions
                  </button>
                </motion.div>
              )}
            </div>

            {/* HOSPITAL LIST */}
            <div className="lg:w-80 p-4 border-t lg:border-t-0 lg:border-l border-white/10 bg-white/5">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-medium text-slate-400">
                  {hospitals.length} results
                </h3>
                <button
                  onClick={() => {
                    // Sort by distance
                    const sorted = [...hospitals].sort((a, b) => 
                      (a.distance || 999) - (b.distance || 999)
                    );
                    // Would need to update parent state
                  }}
                  className="text-xs text-cyan-400 hover:text-cyan-300 transition"
                >
                  Sort by distance
                </button>
              </div>
              {renderHospitalList()}
            </div>
          </div>

          {/* FOOTER */}
          <div className="px-6 py-3 border-t border-white/10 bg-white/5 flex items-center justify-between text-xs text-slate-500">
            <span>📍 Showing hospitals near your location</span>
            <span className="flex items-center gap-2">
              <Ambulance className="w-3 h-3" />
              Emergency services available
            </span>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}