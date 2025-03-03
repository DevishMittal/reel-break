import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Settings from './pages/Settings';
import Sidebar from './components/Sidebar';
import { InterventionProvider } from './context/InterventionContext';
import { InterventionNotification, InterventionOverlay } from './components/Intervention';

function App() {
  return (
    <InterventionProvider>
      <Router>
        <div className="flex h-screen bg-gray-100">
          <Sidebar />
          <div className="flex-1 overflow-auto">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </div>
          {/* Intervention components */}
          <InterventionNotification />
          <InterventionOverlay />
        </div>
      </Router>
    </InterventionProvider>
  );
}

export default App;