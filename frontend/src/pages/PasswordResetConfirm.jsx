import { useEffect, useRef, useState } from "react"
import { Link, useLocation } from "react-router-dom"
import "./PasswordReset.css"

function passwordHint(password) {
  if (!password) return "Use at least 8 characters with letters and numbers."
  const rules = [password.length >= 8, /[A-Za-z]/.test(password), /\d/.test(password)]
  return `${rules.filter(Boolean).length}/3 password requirements met`
}

export default function PasswordResetConfirm() {
  const location = useLocation()
  const passwordRef = useRef(null)
  const params = new URLSearchParams(location.search)
  const uid = params.get("uid") || ""
  const token = params.get("token") || ""
  const [password, setPassword] = useState("")
  const [confirmation, setConfirmation] = useState("")
  const [state, setState] = useState(uid && token ? "idle" : "invalid")
  const [message, setMessage] = useState(uid && token ? "" : "This reset link is invalid or expired.")

  useEffect(() => { if (uid && token) passwordRef.current?.focus() }, [uid, token])

  async function submit(event) {
    event.preventDefault()
    if (password.length < 8 || !/[A-Za-z]/.test(password) || !/\d/.test(password)) {
      setState("invalid")
      setMessage("Choose a password with at least 8 characters, including letters and numbers.")
      return
    }
    if (password !== confirmation) {
      setState("invalid")
      setMessage("Passwords do not match.")
      return
    }
    setState("loading")
    setMessage("")
    try {
      const response = await fetch("/api/auth/password-reset/confirm/", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ uid, token, password }),
      })
      const data = await response.json().catch(() => ({}))
      if (response.ok) {
        setState("success")
        setMessage(data.detail || "Password changed successfully.")
      } else if (response.status === 429) {
        setState("error"); setMessage("Too many attempts. Please try again later.")
      } else if (data.password) {
        setState("error"); setMessage(Array.isArray(data.password) ? data.password[0] : data.password)
      } else {
        setState("invalid"); setMessage("This reset link is invalid or expired.")
      }
    } catch {
      setState("error"); setMessage("We could not process your request. Please try again.")
    }
  }

  if (state === "success") return <main className="reset-shell"><section className="reset-card" aria-live="polite">
    <h1>Password updated</h1><p>{message}</p><Link className="reset-button" to="/login">Go to login</Link>
  </section></main>

  return <main className="reset-shell"><section className="reset-card">
    <h1>Set a new password</h1><p>Choose a strong password for your account.</p>
    <form onSubmit={submit} noValidate>
      <label htmlFor="new-password">New password</label>
      <input ref={passwordRef} id="new-password" type="password" value={password} onChange={(event) => setPassword(event.target.value)} autoComplete="new-password" aria-describedby="password-hint" />
      <small id="password-hint">{passwordHint(password)}</small>
      <label htmlFor="confirm-password">Confirm password</label>
      <input id="confirm-password" type="password" value={confirmation} onChange={(event) => setConfirmation(event.target.value)} autoComplete="new-password" />
      <div className="reset-message" aria-live="polite" role={state !== "idle" ? "alert" : undefined}>{message}</div>
      {state === "invalid" || state === "error" ? <Link className="reset-link" to="/forgot-password">Request a new reset link</Link> : null}
      <button type="submit" disabled={state === "loading"}>{state === "loading" ? "Updating…" : "Set new password"}</button>
    </form>
  </section></main>
}
