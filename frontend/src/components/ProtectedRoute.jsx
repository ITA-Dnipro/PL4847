import { useContext } from "react"
import { Navigate, useLocation } from "react-router-dom"
import AuthContext from "../context/AuthContext"

function ProtectedRoute({ children }) {
  const { isAuthenticated, isLoading } = useContext(AuthContext)
  const location = useLocation()

  if (isLoading) {
    return null
  }

  if (!isAuthenticated) {
    return (
      <Navigate
        to="/login"
        replace
        state={{ from: location }}
      />
    )
  }

  return children
}

export default ProtectedRoute