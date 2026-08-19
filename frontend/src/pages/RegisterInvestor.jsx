import { Link } from "react-router-dom"

function RegisterInvestor() {
    return (
        <div>
            <h1>Register as Investor</h1>
            <p>
                Ви вже зареєстровані? <Link to="/login">Увійти</Link>
            </p>
        </div>
    )
}

export default RegisterInvestor;
