import { fireEvent, render, screen } from "@testing-library/react"
import { MemoryRouter, Route, Routes } from "react-router-dom"
import Login from "./Login"
import AuthContext from "../context/AuthContext"

const mockLogin = vi.fn()

function renderLogin() {
  return render(
    <AuthContext.Provider value={{ login: mockLogin }}>
      <MemoryRouter initialEntries={["/login"]}>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<h1>Home</h1>} />
        </Routes>
      </MemoryRouter>
    </AuthContext.Provider>
  )
}

describe("Login", () => {
  afterEach(() => {
    vi.restoreAllMocks()
    mockLogin.mockReset()
  })

  it("shows required errors when form is empty", () => {
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

    expect(mockLogin).not.toHaveBeenCalled()
  })

  it("shows validation errors for invalid values", () => {
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

    expect(mockLogin).not.toHaveBeenCalled()
  })

  it("shows credential error on 401 response", async () => {
    const error = new Error("Login failed")
    error.status = 401

    mockLogin.mockRejectedValueOnce(error)

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

    expect(mockLogin).toHaveBeenCalledWith(
      "test@example.com",
      "password123",
      true
    )
  })

  it("shows lock message on 429 response", async () => {
    const error = new Error("Login failed")
    error.status = 429

    mockLogin.mockRejectedValueOnce(error)

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
    mockLogin.mockImplementationOnce(
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
      screen.getByRole("button", {
        name: "Logging in...",
      })
    ).toBeDisabled()
  })

  it("redirects to home after successful login", async () => {
    mockLogin.mockResolvedValueOnce({
      access: "access-token",
      refresh: "refresh-token",
      user: {
        id: 1,
        email: "test@example.com",
      },
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
      await screen.findByRole("heading", {
        name: "Home",
      })
    ).toBeInTheDocument()
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