interface KpiCardProps {
  label: string;
  value: string | number;
  sub?: string;
  color?: "blue" | "red" | "orange" | "green" | "yellow";
  icon?: React.ReactNode;
}

const COLORS = {
  blue: "border-blue-500/30 bg-blue-900/10 text-blue-400",
  red: "border-red-500/30 bg-red-900/10 text-red-400",
  orange: "border-orange-500/30 bg-orange-900/10 text-orange-400",
  green: "border-green-500/30 bg-green-900/10 text-green-400",
  yellow: "border-yellow-500/30 bg-yellow-900/10 text-yellow-400",
};

export default function KpiCard({ label, value, sub, color = "blue", icon }: KpiCardProps) {
  return (
    <div className={`rounded-xl border p-4 ${COLORS[color]}`}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs text-gray-400 uppercase tracking-wide mb-1">{label}</p>
          <p className="text-2xl font-bold text-white">{value}</p>
          {sub && <p className="text-xs text-gray-500 mt-1">{sub}</p>}
        </div>
        {icon && <div className="opacity-70">{icon}</div>}
      </div>
    </div>
  );
}
