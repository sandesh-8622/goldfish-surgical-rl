import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Sidebar from './components/layout/Sidebar'
import './App.css'

function App() {
  return (
    <BrowserRouter>
      <div className="app">
        <Sidebar />
        <main className="content">
          <Routes>
            <Route path="/" element={<div>overview</div>} />
            <Route path="/problem" element={<div>problem</div>} />
            <Route path="/reward" element={<div>reward</div>} />
            <Route path="/system" element={<div>system</div>} />
            <Route path="/research" element={<div>research</div>} />
            <Route path="/docs" element={<div>docs</div>} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}

export default App
