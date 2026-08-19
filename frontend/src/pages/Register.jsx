import { Link } from "react-router-dom"
import Footer from "../components/Footer"
import "./Register.css"

function Register() {
  return (
    <>
      <div className="register-picker">
        <h1 className="register-picker__heading">Оберіть тип реєстрації</h1>

        <div className="register-picker__cards">
          <Link className="register-picker__card" to="/register/startup">
            <span className="register-picker__card-title">Зареєструватися як стартап</span>
          </Link>

          <Link className="register-picker__card" to="/register/investor">
            <span className="register-picker__card-title">Зареєструватися як інвестор</span>
          </Link>
        </div>
      </div>
      <Footer />
    </>
  )
}

export default Register;
