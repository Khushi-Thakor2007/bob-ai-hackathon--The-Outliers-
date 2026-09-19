import { Zap } from "lucide-react";
import { runPortStrike, runTempExcursion, resetSimulation } from "../../services/api";

interface DemoBannerProps {
  onSimulate: () => void;
}

export default function DemoBanner({ onSimulate }: DemoBannerProps) {
  const trigger = async (fn: () => Promise<unknown>, label: string) => {
    try {
      await fn();
      alert(`${label} simulation activated! Refresh to see impact.`);
      onSimulate();
    } catch {
      alert("Simulation error — ensure backend is running.");
    }
  };

  return (
    <div className="bg-gradient-to-r from-blue-900/50 to-purple-900/50 border border-blue-700/50 rounded-lg p-3 flex items-center gap-4 flex-wrap">
      <div className="flex items-center gap-2 text-blue-300 text-sm font-medium">
        <Zap className="w-4 h-4" />
        Demo Triggers:
      </div>
      <button
        onClick={() => trigger(runPortStrike, "Port Strike")}
        className="px-3 py-1 bg-red-700 hover:bg-red-600 rounded text-xs text-white font-medium transition-colors"
      >
        🚢 Port Strike
      </button>
      <button
        onClick={() => trigger(runTempExcursion, "Temperature Excursion")}
        className="px-3 py-1 bg-orange-700 hover:bg-orange-600 rounded text-xs text-white font-medium transition-colors"
      >
        🌡️ Temp Excursion
      </button>
      <button
        onClick={() => trigger(resetSimulation, "Reset")}
        className="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded text-xs text-white font-medium transition-colors"
      >
        ↩ Reset
      </button>
    </div>
  );
}
