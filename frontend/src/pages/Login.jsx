import { useState } from "react"
import { Link } from "react-router-dom"
import "./Login.css"

function Login() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [rememberMe, setRememberMe] = useState(false)

  const [errors, setErrors] = useState({})
  const [serverError, setServerError] = useState("")
  const [isLoading, setIsLoading] = useState(false)

  const isEmailValid =
    email.trim() !== "" && /\S+@\S+\.\S+/.test(email)

  const isPasswordValid = password.length >= 8

  const validateForm = () => {
    const newErrors = {}

    if (!email.trim()) {
      newErrors.email = "Email is required"
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      newErrors.email = "Enter a valid email"
    }

    if (!password) {
      newErrors.password = "Password is required"
    } else if (password.length < 8) {
      newErrors.password =
        "Password must be at least 8 characters"
    }

    setErrors(newErrors)

    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (event) => {
    event.preventDefault()

    setServerError("")

    if (!validateForm()) {
      return
    }

    setIsLoading(true)

    try {
      const response = await fetch("/api/auth/login/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email,
          password,
          remember: rememberMe,
        }),
      })

      if (response.status === 401) {
        setServerError("Invalid email or password")
        return
      }

      if (response.status === 429) {
        setServerError(
          "Too many login attempts. Please try again later."
        )
        return
      }

      if (!response.ok) {
        setServerError("Login failed. Please try again.")
        return
      }

      await response.json()
    } catch (error) {
      console.error("Login error:", error)
      setServerError("Unable to connect to the server.")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="login-page">
      <div className="login-card">
        <h1>Login</h1>

        <form onSubmit={handleSubmit} noValidate>
          <div className="login-field">
            <label htmlFor="email">Email</label>

            <input
              id="email"
              type="email"
              value={email}
              className={
                errors.email
                  ? "input-error"
                  : isEmailValid
                    ? "input-valid"
                    : ""
              }
              onChange={(event) => {
                setEmail(event.target.value)

                if (errors.email) {
                  setErrors({
                    ...errors,
                    email: "",
                  })
                }
              }}
              placeholder="Enter your email"
              autoComplete="email"
            />

            {errors.email && (
              <p className="login-error">
                {errors.email}
              </p>
            )}
          </div>

          <div className="login-field">
            <label htmlFor="password">Password</label>

            <input
              id="password"
              type="password"
              value={password}
              className={
                errors.password
                  ? "input-error"
                  : isPasswordValid
                    ? "input-valid"
                    : ""
              }
              onChange={(event) => {
                setPassword(event.target.value)

                if (errors.password) {
                  setErrors({
                    ...errors,
                    password: "",
                  })
                }
              }}
              placeholder="Enter your password"
              autoComplete="current-password"
            />

            {errors.password && (
              <p className="login-error">
                {errors.password}
              </p>
            )}
          </div>

          <div className="login-options">
            <label className="remember-me">
              <input
                type="checkbox"
                checked={rememberMe}
                onChange={(event) =>
                  setRememberMe(event.target.checked)
                }
              />

              <span>Remember me</span>
            </label>

            <Link to="/forgot-password">
              Forgot password?
            </Link>
          </div>

          {serverError && (
            <p
              className="login-server-error"
              role="alert"
            >
              {serverError}
            </p>
          )}

          <button
            type="submit"
            disabled={isLoading}
          >
            {isLoading && (
              <span
                className="login-spinner"
                aria-hidden="true"
              />
            )}

            {isLoading ? "Logging in..." : "Login"}
          </button>
        </form>
      </div>
    </div>
  )
}

export default Login