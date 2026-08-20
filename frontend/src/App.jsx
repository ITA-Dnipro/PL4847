import { Routes, Route, Link} from "react-router-dom"
import "./App.css"
import Home from "./pages/Home"
import Login from "./pages/Login"
import Register from "./pages/Register"
import StartupView from "./pages/StartupView"
import InvestorDashboard from "./pages/InvestorDashboard"
import Inbox from "./pages/Inbox"
import PasswordResetRequest from "./pages/PasswordResetRequest"
import PasswordResetConfirm from "./pages/PasswordResetConfirm"


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
      <Route path="/forgot-password" element={<PasswordResetRequest />} />
      <Route path="/reset-password/" element={<PasswordResetConfirm />} />
      <Route path="/register" element={<Register />} />
      <Route path="/startups/:id" element={<StartupView />} />
      <Route path="/dashboard" element={<InvestorDashboard />} />
      <Route path="/messages" element={<Inbox />} />
    </Routes>
      </>
  )
}

export default App
