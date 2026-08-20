import { useState } from "react"
import { Link } from "react-router-dom"
import "./PasswordReset.css"

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

export default function PasswordResetRequest() {
  const [email, setEmail] = useState("")
  const [state, setState] = useState("idle")
  const [message, setMessage] = useState("")

  async function submit(event) {
    event.preventDefault()
    const value = email.trim()
    if (!value) {
      setState("invalid")
      setMessage("Enter your email address.")
      return
    }
    if (!EMAIL_PATTERN.test(value)) {
      setState("invalid")
      setMessage("Enter a valid email address.")
      return
    }
    setState("loading")
    setMessage("")
    try {
      const response = await fetch("/api/auth/password-reset/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: value }),
      })
      if (response.status === 429) {
        setState("error")
        setMessage("Too many requests. Please try again later.")
      } else if (!response.ok) {
        throw new Error("request failed")
      } else {
        setState("success")
        setMessage("If the email exists, you will receive reset instructions.")
      }
    } catch {
      setState("error")
      setMessage("We could not process your request. Please try again.")
    }
  }

  if (state === "success") {
    return <main className="reset-shell"><section className="reset-card" aria-live="polite">
      <h1>Check your inbox</h1><p>{message}</p><Link className="reset-link" to="/login">Back to login</Link>
    </section></main>
  }

  return <main className="reset-shell"><section className="reset-card">
    <h1>Forgot password?</h1>
    <p>Enter the email linked to your account and we’ll send reset instructions.</p>
    <form onSubmit={submit} noValidate>
      <label htmlFor="reset-email">Email address</label>
      <input id="reset-email" name="email" type="email" value={email} onChange={(event) => setEmail(event.target.value)} autoComplete="email" aria-invalid={state === "invalid"} />
      <div className="reset-message" aria-live="polite" role={state === "invalid" || state === "error" ? "alert" : undefined}>{message}</div>
      <button type="submit" disabled={state === "loading"}>{state === "loading" ? "Sending…" : "Send reset link"}</button>
    </form>
    <Link className="reset-link" to="/login">Back to login</Link>
  </section></main>
}
