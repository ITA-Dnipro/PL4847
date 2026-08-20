import { fireEvent, render, screen, waitFor } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { describe, expect, it, vi, beforeEach, afterEach } from "vitest"
import PasswordResetRequest from "./PasswordResetRequest"
import PasswordResetConfirm from "./PasswordResetConfirm"

const renderWithRoute = (element, initialEntries = ["/"]) => render(
  <MemoryRouter initialEntries={initialEntries}>{element}</MemoryRouter>,
)

describe("password reset request", () => {
  beforeEach(() => { vi.stubGlobal("fetch", vi.fn()) })
  afterEach(() => { vi.unstubAllGlobals() })

  it("prevents a request and announces invalid email", async () => {
    renderWithRoute(<PasswordResetRequest />)
    fireEvent.click(screen.getByRole("button", { name: /send reset/i }))
    expect(screen.getByRole("alert")).toHaveTextContent(/email address/i)
    expect(fetch).not.toHaveBeenCalled()
  })

  it("shows the generic success state", async () => {
    fetch.mockResolvedValue({ ok: true, status: 200 })
    renderWithRoute(<PasswordResetRequest />)
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: "user@example.com" } })
    fireEvent.click(screen.getByRole("button", { name: /send reset/i }))
    await waitFor(() => expect(screen.getByText(/if the email exists/i)).toBeInTheDocument())
  })
})

describe("password reset confirm", () => {
  beforeEach(() => { vi.stubGlobal("fetch", vi.fn()) })
  afterEach(() => { vi.unstubAllGlobals() })

  it("parses the deep link and focuses the password field", () => {
    renderWithRoute(<PasswordResetConfirm />, ["/reset-password/?uid=abc&token=secret-token"])
    expect(screen.getByLabelText(/new password/i)).toHaveFocus()
    expect(screen.queryByDisplayValue("secret-token")).not.toBeInTheDocument()
  })

  it("sends the approved payload and shows success", async () => {
    fetch.mockResolvedValue({ ok: true, status: 200, json: async () => ({ detail: "Password changed successfully." }) })
    renderWithRoute(<PasswordResetConfirm />, ["/reset-password/?uid=abc&token=secret-token"])
    fireEvent.change(screen.getByLabelText(/new password/i), { target: { value: "StrongPass123" } })
    fireEvent.change(screen.getByLabelText(/confirm password/i), { target: { value: "StrongPass123" } })
    fireEvent.click(screen.getByRole("button", { name: /set new password/i }))
    await waitFor(() => expect(screen.getByText(/password changed successfully/i)).toBeInTheDocument())
    expect(fetch).toHaveBeenCalledWith("/api/auth/password-reset/confirm/", expect.objectContaining({ body: JSON.stringify({ uid: "abc", token: "secret-token", password: "StrongPass123" }) }))
  })
})
