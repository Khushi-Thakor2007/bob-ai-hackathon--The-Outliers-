import { useEffect, useRef } from "react";
import type { Shipment, Disruption } from "../../types";

interface LogisticsMapProps {
  shipments: Shipment[];
  disruptions: Disruption[];
}

declare global {
  interface Window {
    L: typeof import("leaflet");
  }
}

const RISK_COLORS: Record<string, string> = {
  Critical: "#ef4444",
  High: "#f97316",
  Medium: "#eab308",
  Low: "#22c55e",
};

export default function LogisticsMap({ shipments, disruptions }: LogisticsMapProps) {
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<unknown>(null);

  useEffect(() => {
    if (!mapRef.current) return;
    if (mapInstanceRef.current) return; // already init

    // Leaflet loaded via CDN
    const L = window.L;
    if (!L) return;

    const map = L.map(mapRef.current, {
      center: [20.5937, 78.9629],
      zoom: 5,
      zoomControl: true,
    });

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: "© OpenStreetMap",
      maxZoom: 18,
    }).addTo(map);

    // Plot shipments
    shipments.forEach((s) => {
      if (s.current_lat && s.current_lon) {
        const color = RISK_COLORS[s.risk_level] || "#6b7280";
        const marker = L.circleMarker([s.current_lat, s.current_lon], {
          radius: s.risk_level === "Critical" ? 9 : 6,
          fillColor: color,
          color: "#fff",
          weight: 1.5,
          opacity: 1,
          fillOpacity: 0.9,
        });
        marker.bindPopup(`
          <b>${s.shipment_id}</b><br/>
          ${s.cargo_type} | ${s.risk_level} Risk<br/>
          ${s.origin} → ${s.destination}<br/>
          Score: ${s.current_risk_score.toFixed(0)}
        `);
        marker.addTo(map);
      }
    });

    // Plot disruptions
    disruptions.filter((d) => d.is_active && d.latitude && d.longitude).forEach((d) => {
      const circle = L.circle([d.latitude!, d.longitude!], {
        radius: (d.radius_km || 150) * 1000,
        color: "#ef4444",
        fillColor: "#ef4444",
        fillOpacity: 0.08,
        weight: 2,
        dashArray: "6 4",
      });
      circle.bindPopup(`<b>${d.name}</b><br/>${d.severity} | ${d.type}`);
      circle.addTo(map);
    });

    mapInstanceRef.current = map;

    return () => {
      map.remove();
      mapInstanceRef.current = null;
    };
  }, []);

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
      <div className="px-4 py-3 border-b border-gray-800 flex items-center gap-4">
        <h3 className="text-sm font-semibold text-white">Live Logistics Map</h3>
        <div className="flex items-center gap-3 text-xs">
          {Object.entries(RISK_COLORS).map(([level, color]) => (
            <span key={level} className="flex items-center gap-1 text-gray-400">
              <span className="w-2.5 h-2.5 rounded-full inline-block" style={{ background: color }} />
              {level}
            </span>
          ))}
        </div>
      </div>
      <div ref={mapRef} className="h-72 w-full" />
    </div>
  );
}
