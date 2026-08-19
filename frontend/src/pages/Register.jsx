import { Link } from "react-router-dom"
import Footer from "../components/Footer";

function Register() {
  return (
    <>
      <h1>Register Page</h1>
      <Link to="/register/startup">As startup</Link>  
      <Link to="/register/investor">As investor</Link> 
      <Footer /> 
    </>
  )
}

export default Register;