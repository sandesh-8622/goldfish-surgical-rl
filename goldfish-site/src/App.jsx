import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Sidebar from './components/layout/Sidebar'
import BottomNav from './components/layout/BottomNav'
import OverviewView from './views/OverviewView'
import ProblemView from './views/ProblemView'
import RewardView from './views/RewardView'
import SystemView from './views/SystemView'
import ResearchView from './views/ResearchView'
import './App.css'

function App() {
  return (
    <BrowserRouter>
      <div className="app">
        <Sidebar />
        <main className="content">
          <Routes>
            <Route path="/" element={<OverviewView />} />
            <Route path="/problem" element={<ProblemView />} />
            <Route path="/reward" element={<RewardView />} />
            <Route path="/system" element={<SystemView />} />
            <Route path="/research" element={<ResearchView />} />
            <Route path="/docs" element={<div>docs</div>} />
          </Routes>
        </main>
        <BottomNav />
      </div>
    </BrowserRouter>
  )
}

export default App
