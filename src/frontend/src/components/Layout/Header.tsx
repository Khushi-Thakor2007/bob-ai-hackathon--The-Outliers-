import { Bell, RefreshCw } from "lucide-react";

interface HeaderProps {
  title: string;
  onRefresh?: () => void;
  loading?: boolean;
}

export default function Header({ title, onRefresh, loading }: HeaderProps) {
  return (
    <header className="bg-gray-950 border-b border-gray-800 px-6 py-4 flex items-center justify-between">
      <div>
        <h1 className="text-lg font-semibold text-white">{title}</h1>
        <p className="text-xs text-gray-500">Supply Chain Disruption Assistant & Fleet Utilisation Optimizer</p>
      </div>
      <div className="flex items-center gap-3">
        {onRefresh && (
          <button
            onClick={onRefresh}
            disabled={loading}
            className="flex items-center gap-2 px-3 py-1.5 bg-gray-800 hover:bg-gray-700 rounded-lg text-xs text-gray-300 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
            Refresh
          </button>
        )}
        <button className="relative p-2 rounded-lg bg-gray-800 hover:bg-gray-700 transition-colors">
          <Bell className="w-4 h-4 text-gray-400" />
          <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
        </button>
      </div>
    </header>
  );
}
