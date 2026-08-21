import { fireEvent, render, screen } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import Login from "./Login"

const originalFetch = global.fetch

function renderLogin() {
  return render(
    <MemoryRouter>
      <Login />
    </MemoryRouter>
  )
}

describe("Login", () => {
  afterEach(() => {
    vi.restoreAllMocks()

    if (originalFetch === undefined) {
      delete global.fetch
    } else {
      global.fetch = originalFetch
    }
  })

  it("shows required errors when form is empty", () => {
    global.fetch = vi.fn()

    renderLogin()

    fireEvent.click(
      screen.getByRole("button", { name: "Login" })
    )

    expect(
      screen.getByText("Email is required")
    ).toBeInTheDocument()

    expect(
      screen.getByText("Password is required")
    ).toBeInTheDocument()

    expect(global.fetch).not.toHaveBeenCalled()
  })

  it("shows validation errors for invalid values", () => {
    global.fetch = vi.fn()

    renderLogin()

    fireEvent.change(screen.getByLabelText("Email"), {
      target: { value: "wrong-email" },
    })

    fireEvent.change(screen.getByLabelText("Password"), {
      target: { value: "123" },
    })

    fireEvent.click(
      screen.getByRole("button", { name: "Login" })
    )

    expect(
      screen.getByText("Enter a valid email")
    ).toBeInTheDocument()

    expect(
      screen.getByText(
        "Password must be at least 8 characters"
      )
    ).toBeInTheDocument()

    expect(global.fetch).not.toHaveBeenCalled()
  })

  it("shows credential error on 401 response", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 401,
    })

    renderLogin()

    fireEvent.change(screen.getByLabelText("Email"), {
      target: { value: "test@example.com" },
    })

    fireEvent.change(screen.getByLabelText("Password"), {
      target: { value: "password123" },
    })

    fireEvent.click(
      screen.getByLabelText("Remember me")
    )

    fireEvent.click(
      screen.getByRole("button", { name: "Login" })
    )

    expect(
      await screen.findByText("Invalid email or password")
    ).toBeInTheDocument()

    expect(global.fetch).toHaveBeenCalledWith(
      "/api/auth/login/",
      expect.objectContaining({
        method: "POST",
      })
    )

    const requestOptions = global.fetch.mock.calls[0][1]

    expect(JSON.parse(requestOptions.body)).toEqual({
      email: "test@example.com",
      password: "password123",
      remember: true,
    })
    })

  it("shows lock message on 429 response", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 429,
    })

    renderLogin()

    fireEvent.change(screen.getByLabelText("Email"), {
      target: { value: "test@example.com" },
    })

    fireEvent.change(screen.getByLabelText("Password"), {
      target: { value: "password123" },
    })

    fireEvent.click(
      screen.getByRole("button", { name: "Login" })
    )

    expect(
      await screen.findByText(
        "Too many login attempts. Please try again later."
      )
    ).toBeInTheDocument()
  })

  it("shows loading state while login request is running", () => {
    global.fetch = vi.fn(
      () => new Promise(() => {})
    )

    renderLogin()

    fireEvent.change(screen.getByLabelText("Email"), {
      target: { value: "test@example.com" },
    })

    fireEvent.change(screen.getByLabelText("Password"), {
      target: { value: "password123" },
    })

    fireEvent.click(
      screen.getByRole("button", { name: "Login" })
    )

    expect(
      screen.getByRole("button", { name: "Logging in..." })
    ).toBeDisabled()
  })

  it("has forgot password link", () => {
    renderLogin()

    expect(
      screen.getByRole("link", {
        name: "Forgot password?",
      })
    ).toHaveAttribute("href", "/forgot-password")
  })
})