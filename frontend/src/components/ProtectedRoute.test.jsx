import { render, screen } from "@testing-library/react"
import {
  MemoryRouter,
  Route,
  Routes,
} from "react-router-dom"

import AuthContext from "../context/AuthContext"
import ProtectedRoute from "./ProtectedRoute"

function renderRoute(authValue) {
  return render(
    <AuthContext.Provider value={authValue}>
      <MemoryRouter initialEntries={["/dashboard"]}>
        <Routes>
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <h1>Dashboard</h1>
              </ProtectedRoute>
            }
          />

          <Route
            path="/login"
            element={<h1>Login page</h1>}
          />
        </Routes>
      </MemoryRouter>
    </AuthContext.Provider>
  )
}

describe("ProtectedRoute", () => {
  it("shows protected content when authenticated", () => {
    renderRoute({
      isAuthenticated: true,
      isLoading: false,
    })

    expect(
      screen.getByRole("heading", {
        name: "Dashboard",
      })
    ).toBeInTheDocument()
  })

  it("redirects to login when not authenticated", () => {
    renderRoute({
      isAuthenticated: false,
      isLoading: false,
    })

    expect(
      screen.getByRole("heading", {
        name: "Login page",
      })
    ).toBeInTheDocument()
  })

  it("does not render protected content while loading", () => {
    renderRoute({
      isAuthenticated: false,
      isLoading: true,
    })

    expect(
      screen.queryByRole("heading", {
        name: "Dashboard",
      })
    ).not.toBeInTheDocument()

    expect(
      screen.queryByRole("heading", {
        name: "Login page",
      })
    ).not.toBeInTheDocument()
  })
})