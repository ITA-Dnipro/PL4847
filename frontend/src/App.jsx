import { Routes, Route, Link} from "react-router-dom"
import "./App.css"
import Home from "./pages/Home"
import Login from "./pages/Login"
import Register from "./pages/Register"
import StartupView from "./pages/StartupView"
import InvestorDashboard from "./pages/InvestorDashboard"
import Inbox from "./pages/Inbox"
import InfoPage from "./components/InfoPage"
import RegisterStartup from "./pages/RegisterStartup"
import RegisterInvestor from "./pages/RegisterInvestor"

function App() {
  return (
    <>
    <nav>
      <Link to="/">Home</Link>
      {" | "}
      <Link to="/login">Login</Link>
      {" | "}
      <Link to="/register">Register</Link>
      {" | "}
      <Link to="/startups/1">Startup Info</Link>
      {" | "}
      <Link to="/dashboard">Dashboard</Link>
      {" | "}
      <Link to="/messages">Messages</Link>
      {" | "}

    </nav>

    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/register/startup" element={<RegisterStartup />} />
      <Route path="/register/investor" element={<RegisterInvestor />} />
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
