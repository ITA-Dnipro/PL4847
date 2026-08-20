import { Routes, Route } from "react-router-dom"

import "./App.css"
import Header from "./components/Header/Header"
import InfoPage from "./components/InfoPage"
import Home from "./pages/Home"
import Search from "./pages/Search"
import Login from "./pages/Login"
import Register from "./pages/Register"
import StartupView from "./pages/StartupView"
import InvestorDashboard from "./pages/InvestorDashboard"
import Inbox from "./pages/Inbox"

function App() {
  return (
    <>
      <Header />

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/search" element={<Search />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/startups/:id" element={<StartupView />} />
        <Route path="/dashboard" element={<InvestorDashboard />} />
        <Route path="/messages" element={<Inbox />} />
        <Route path="/manufacturers" element={<InfoPage />} />
        <Route path="/importers" element={<InfoPage />} />
        <Route path="/retail-chains" element={<InfoPage />} />
        <Route path="/horeca" element={<InfoPage />} />
        <Route path="/other-services" element={<InfoPage />} />
      </Routes>
    </>
  )
}

export default App