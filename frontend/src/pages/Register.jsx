import { Link } from "react-router-dom"
import Footer from "../components/Footer";
import './Register.css'

function Register() {
  return (
    <>
    <div className="register-picker">
      <h1>Register Page</h1>
      <Link to="/register/startup">As startup</Link>  
      <Link to="/register/investor">As investor</Link> 
    </div>
      <Footer /> 
    </>
  )
}

export default Register;