import { Routes, Route} from "react-router-dom"
import "./App.css"
import Header from "./components/Header/Header"
import Home from "./pages/Home"
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
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/startups/:id" element={<StartupView />} />
        <Route path="/dashboard" element={<InvestorDashboard />} />
        <Route path="/messages" element={<Inbox />} />
      </Routes>
    </>
  )
}

export default App