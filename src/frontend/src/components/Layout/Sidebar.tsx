import { Package, AlertTriangle, Truck, Thermometer, LayoutDashboard, Bot, Zap } from "lucide-react";

interface SidebarProps {
  activePage: string;
  onNavigate: (page: string) => void;
}

const NAV_ITEMS = [
  { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
  { id: "shipments", label: "Shipments", icon: Package },
  { id: "disruptions", label: "Disruptions", icon: AlertTriangle },
  { id: "fleet", label: "Fleet", icon: Truck },
  { id: "coldchain", label: "Cold Chain", icon: Thermometer },
  { id: "bob", label: "Bob AI", icon: Bot },
];

export default function Sidebar({ activePage, onNavigate }: SidebarProps) {
  return (
    <aside className="w-64 bg-gray-950 border-r border-gray-800 flex flex-col min-h-screen">
      {/* Logo */}
      <div className="p-6 border-b border-gray-800">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-blue-600 rounded-lg flex items-center justify-center">
            <Zap className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="text-sm font-bold text-white leading-tight">Control Tower</div>
            <div className="text-xs text-gray-400">Supply Chain AI</div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1">
        {NAV_ITEMS.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => onNavigate(id)}
            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
              activePage === id
                ? "bg-blue-600 text-white"
                : "text-gray-400 hover:text-white hover:bg-gray-800"
            }`}
          >
            <Icon className="w-4 h-4 flex-shrink-0" />
            {label}
          </button>
        ))}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-gray-800">
        <div className="text-xs text-gray-500 text-center">The Outliers — IBM Hackathon</div>
      </div>
    </aside>
  );
}
