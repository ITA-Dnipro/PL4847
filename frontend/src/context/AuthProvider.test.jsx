import { act, fireEvent, render, screen, waitFor } from "@testing-library/react"
import { useContext } from "react"

import AuthContext from "./AuthContext"
import AuthProvider from "./AuthProvider"

const originalFetch = global.fetch

function TestComponent() {
  const {
    accessToken,
    isAuthenticated,
    login,
    logout,
    refresh,
  } = useContext(AuthContext)

  return (
    <>
      <p data-testid="authenticated">
        {String(isAuthenticated)}
      </p>

      <p data-testid="access-token">
        {accessToken ?? "none"}
      </p>

      <button
        type="button"
        onClick={() =>
          login(
            "test@example.com",
            "password123",
            true
          )
        }
      >
        Login
      </button>

      <button
        type="button"
        onClick={() => refresh()}
      >
        Refresh
      </button>

      <button
        type="button"
        onClick={() => logout()}
      >
        Logout
      </button>
    </>
  )
}

function renderProvider() {
  return render(
    <AuthProvider>
      <TestComponent />
    </AuthProvider>
  )
}

describe("AuthProvider", () => {
  beforeEach(() => {
    localStorage.clear()
    global.fetch = vi.fn()
  })

  afterEach(() => {
    vi.restoreAllMocks()
    vi.useRealTimers()
    localStorage.clear()

    if (originalFetch === undefined) {
      delete global.fetch
    } else {
      global.fetch = originalFetch
    }
  })

  it("logs in and stores refresh token when remember is enabled", async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => ({
        access: "access-token",
        refresh: "refresh-token",
        user: {
          id: 1,
          email: "test@example.com",
          role: "investor",
        },
      }),
    })

    renderProvider()

    await act(async () => {
      fireEvent.click(
        screen.getByRole("button", {
          name: "Login",
        })
      )
    })

    expect(
      screen.getByTestId("authenticated")
    ).toHaveTextContent("true")

    expect(
      screen.getByTestId("access-token")
    ).toHaveTextContent("access-token")

    expect(
      localStorage.getItem("authRefreshToken")
    ).toBe("refresh-token")

    expect(global.fetch).toHaveBeenCalledWith(
      "/api/auth/login/",
      expect.objectContaining({
        method: "POST",
      })
    )
  })

  it("refreshes the access token", async () => {
    localStorage.setItem(
      "authRefreshToken",
      "refresh-token"
    )

    global.fetch.mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        access: "new-access-token",
      }),
    })

    renderProvider()

    await waitFor(() => {
      expect(
        screen.getByTestId("access-token")
      ).toHaveTextContent("new-access-token")
    })

    expect(global.fetch).toHaveBeenCalledWith(
      "/api/auth/refresh/",
      expect.objectContaining({
        method: "POST",
      })
    )
  })

  it("logs out when token refresh fails", async () => {
    localStorage.setItem(
      "authRefreshToken",
      "invalid-refresh-token"
    )

    global.fetch.mockResolvedValue({
      ok: false,
      status: 401,
    })

    renderProvider()

    await waitFor(() => {
      expect(
        localStorage.getItem("authRefreshToken")
      ).toBeNull()
    })

    expect(
      screen.getByTestId("authenticated")
    ).toHaveTextContent("false")

    expect(
      screen.getByTestId("access-token")
    ).toHaveTextContent("none")
  })

  it("clears authentication on logout", async () => {
    global.fetch
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          access: "access-token",
          refresh: "refresh-token",
          user: {
            id: 1,
            email: "test@example.com",
          },
        }),
      })
      .mockResolvedValue({
        ok: true,
        status: 204,
      })

    renderProvider()

    await act(async () => {
      fireEvent.click(
        screen.getByRole("button", {
          name: "Login",
        })
      )
    })

    await act(async () => {
      fireEvent.click(
        screen.getByRole("button", {
          name: "Logout",
        })
      )
    })

    expect(
      screen.getByTestId("authenticated")
    ).toHaveTextContent("false")

    expect(
      localStorage.getItem("authRefreshToken")
    ).toBeNull()
  })

  it("automatically refreshes access token before expiry", async () => {
    vi.useFakeTimers()
    vi.setSystemTime(
      new Date("2026-08-20T12:00:00Z")
    )

    const expiration =
      Math.floor(Date.now() / 1000) + 120

    const payload = btoa(
      JSON.stringify({
        exp: expiration,
      })
    )

    const accessToken =
      `header.${payload}.signature`

    global.fetch
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          access: accessToken,
          refresh: "refresh-token",
          user: {
            id: 1,
            email: "test@example.com",
          },
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          access: "refreshed-access-token",
        }),
      })

    renderProvider()

    await act(async () => {
      fireEvent.click(
        screen.getByRole("button", {
          name: "Login",
        })
      )
    })

    expect(global.fetch).toHaveBeenCalledTimes(1)

    await act(async () => {
      await vi.advanceTimersByTimeAsync(60_000)
    })

    expect(global.fetch).toHaveBeenCalledWith(
      "/api/auth/refresh/",
      expect.objectContaining({
        method: "POST",
      })
    )

    expect(
      screen.getByTestId("access-token")
    ).toHaveTextContent(
      "refreshed-access-token"
    )
  })
})