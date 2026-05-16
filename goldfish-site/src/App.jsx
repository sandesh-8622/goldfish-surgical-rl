import { Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/layout/Sidebar.jsx';
import BottomNav from './components/layout/BottomNav.jsx';
import OverviewView   from './views/OverviewView.jsx';
import ProblemView    from './views/ProblemView.jsx';
import SystemView     from './views/SystemView.jsx';
import ResearchView   from './views/ResearchView.jsx';
import DocsView       from './views/DocsView.jsx';
import RewardView     from './views/RewardView.jsx';
import './App.css';

export default function App() {
  return (
    <div className="app-page">
      <aside className="app-sidebar">
        <Sidebar />
      </aside>

      <div className="app-content">
        <div className="app-panel">
          <Routes>
            <Route path="/"          element={<Navigate to="/overview" replace />} />
            <Route path="/overview"  element={<OverviewView />} />
            <Route path="/problem"   element={<ProblemView />} />
            <Route path="/system"    element={<SystemView />} />
            <Route path="/research"  element={<ResearchView />} />
            <Route path="/docs"      element={<DocsView />} />
            <Route path="/reward"    element={<RewardView />} />
          </Routes>
        </div>
      </div>

      <BottomNav />
    </div>
  );
}
