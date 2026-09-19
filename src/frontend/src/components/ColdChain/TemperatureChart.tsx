import type { SensorPoint } from "../../types";

interface TemperatureChartProps {
  data: SensorPoint[];
  minAllowed?: number;
  maxAllowed?: number;
}

export default function TemperatureChart({ data, minAllowed, maxAllowed }: TemperatureChartProps) {
  if (!data || data.length === 0) {
    return <div className="text-xs text-gray-500 p-4">No sensor data available.</div>;
  }

  const temps = data.map((d) => d.temperature);
  const minT = Math.min(...temps, minAllowed ?? Infinity) - 1;
  const maxT = Math.max(...temps, maxAllowed ?? -Infinity) + 1;
  const range = maxT - minT || 1;

  const W = 480;
  const H = 120;
  const PAD = { top: 10, right: 10, bottom: 20, left: 30 };
  const chartW = W - PAD.left - PAD.right;
  const chartH = H - PAD.top - PAD.bottom;

  const xStep = chartW / Math.max(data.length - 1, 1);
  const yPos = (t: number) => PAD.top + chartH - ((t - minT) / range) * chartH;

  const points = data.map((d, i) => ({
    x: PAD.left + i * xStep,
    y: yPos(d.temperature),
    excursion: d.is_excursion,
  }));

  const polyline = points.map((p) => `${p.x},${p.y}`).join(" ");

  const yMin = minAllowed !== undefined ? yPos(minAllowed) : null;
  const yMax = maxAllowed !== undefined ? yPos(maxAllowed) : null;

  return (
    <div className="overflow-x-auto">
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full" style={{ minWidth: 300 }}>
        {/* Allowed range band */}
        {yMin !== null && yMax !== null && (
          <rect
            x={PAD.left} y={yMax}
            width={chartW} height={yMin - yMax}
            fill="rgba(34,197,94,0.07)"
            stroke="rgba(34,197,94,0.3)"
            strokeWidth={0.5}
            strokeDasharray="4 3"
          />
        )}
        {/* Max line */}
        {yMax !== null && (
          <line x1={PAD.left} y1={yMax} x2={W - PAD.right} y2={yMax}
            stroke="#ef4444" strokeWidth={1} strokeDasharray="4 2" opacity={0.7} />
        )}
        {/* Min line */}
        {yMin !== null && (
          <line x1={PAD.left} y1={yMin} x2={W - PAD.right} y2={yMin}
            stroke="#3b82f6" strokeWidth={1} strokeDasharray="4 2" opacity={0.7} />
        )}
        {/* Polyline */}
        <polyline
          points={polyline}
          fill="none"
          stroke="#22d3ee"
          strokeWidth={2}
          strokeLinejoin="round"
        />
        {/* Dots */}
        {points.map((p, i) => (
          <circle
            key={i}
            cx={p.x} cy={p.y} r={3.5}
            fill={p.excursion ? "#ef4444" : "#22d3ee"}
            stroke="#111827"
            strokeWidth={1.5}
          />
        ))}
        {/* Y labels */}
        {[minT, (minT + maxT) / 2, maxT].map((v, i) => (
          <text
            key={i}
            x={PAD.left - 4}
            y={yPos(v) + 4}
            fontSize={8}
            fill="#6b7280"
            textAnchor="end"
          >
            {v.toFixed(1)}°
          </text>
        ))}
      </svg>
    </div>
  );
}
