import { useState } from "react";
import "./App.css";
import Sidebar from "./components/Layout/Sidebar";
import BobChatWidget from "./components/Bob/BobChatWidget";
import DashboardPage from "./pages/DashboardPage";
import ShipmentsPage from "./pages/ShipmentsPage";
import DisruptionsPage from "./pages/DisruptionsPage";
import FleetPage from "./pages/FleetPage";
import ColdChainPage from "./pages/ColdChainPage";
import BobAssistantPage from "./pages/BobAssistantPage";

export default function App() {
  const [page, setPage] = useState("dashboard");

  const renderPage = () => {
    switch (page) {
      case "shipments": return <ShipmentsPage />;
      case "disruptions": return <DisruptionsPage />;
      case "fleet": return <FleetPage />;
      case "coldchain": return <ColdChainPage />;
      case "bob": return <BobAssistantPage />;
      default: return <DashboardPage />;
    }
  };

  return (
    <div className="flex h-screen bg-gray-950 text-white overflow-hidden">
      <Sidebar activePage={page} onNavigate={setPage} />
      <main className="flex-1 overflow-hidden flex flex-col">
        {renderPage()}
      </main>
      {page !== "bob" && <BobChatWidget />}
    </div>
  );
}
