import {
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react"
import AuthContext from "./AuthContext"

const REFRESH_TOKEN_KEY = "authRefreshToken"
const REFRESH_BUFFER_MS = 60_000
const REQUEST_TIMEOUT_MS = 10_000

function getTokenExpiration(token) {
  try {
    const payload = token.split(".")[1]

    if (!payload) {
      return null
    }

    const base64 = payload
      .replace(/-/g, "+")
      .replace(/_/g, "/")

    const padded = base64.padEnd(
      Math.ceil(base64.length / 4) * 4,
      "="
    )

    const data = JSON.parse(atob(padded))

    return typeof data.exp === "number"
      ? data.exp * 1000
      : null
  } catch {
    return null
  }
}

function AuthProvider({ children }) {
  const [accessToken, setAccessToken] = useState(null)

  const [refreshToken, setRefreshToken] = useState(() =>
    localStorage.getItem(REFRESH_TOKEN_KEY)
  )

  const [user, setUser] = useState(null)

  const [isLoading, setIsLoading] = useState(
    Boolean(refreshToken)
  )

  const sessionIdRef = useRef(0)
  const activeRefreshRef = useRef(null)

  const abortActiveRefresh = useCallback(() => {
    if (activeRefreshRef.current) {
      activeRefreshRef.current.controller.abort()
      activeRefreshRef.current = null
    }
  }, [])

  const invalidateSession = useCallback(() => {
    sessionIdRef.current += 1
    abortActiveRefresh()

    return sessionIdRef.current
  }, [abortActiveRefresh])

  const clearAuthState = useCallback(() => {
    setAccessToken(null)
    setRefreshToken(null)
    setUser(null)
    setIsLoading(false)

    localStorage.removeItem(REFRESH_TOKEN_KEY)
  }, [])

  const clearAuth = useCallback(() => {
    invalidateSession()
    clearAuthState()
  }, [invalidateSession, clearAuthState])

  const refresh = useCallback(() => {
    if (!refreshToken) {
      return Promise.resolve(null)
    }

    const sessionId = sessionIdRef.current
    const currentRequest = activeRefreshRef.current

    if (
      currentRequest &&
      currentRequest.sessionId === sessionId
    ) {
      return currentRequest.promise
    }

    abortActiveRefresh()

    const controller = new AbortController()

    const timeoutId = setTimeout(() => {
      controller.abort()
    }, REQUEST_TIMEOUT_MS)

    const request = {
      sessionId,
      controller,
      promise: null,
    }

    const promise = (async () => {
      try {
        const response = await fetch(
          "/api/auth/refresh/",
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              refresh: refreshToken,
            }),
            signal: controller.signal,
          }
        )

        if (sessionIdRef.current !== sessionId) {
          return null
        }

        if (!response.ok) {
          throw new Error("Token refresh failed")
        }

        const data = await response.json()

        if (sessionIdRef.current !== sessionId) {
          return null
        }

        setAccessToken(data.access)

        if (data.refresh) {
          const remembered =
            localStorage.getItem(REFRESH_TOKEN_KEY) ===
            refreshToken

          setRefreshToken(data.refresh)

          if (remembered) {
            localStorage.setItem(
              REFRESH_TOKEN_KEY,
              data.refresh
            )
          }
        }

        return data.access
      } catch {
        if (sessionIdRef.current === sessionId) {
          clearAuth()
        }

        return null
      } finally {
        clearTimeout(timeoutId)

        if (activeRefreshRef.current === request) {
          activeRefreshRef.current = null
        }
      }
    })()

    request.promise = promise
    activeRefreshRef.current = request

    return promise
  }, [
    refreshToken,
    abortActiveRefresh,
    clearAuth,
  ])

  const login = useCallback(
    async (email, password, remember = false) => {
      const sessionId = invalidateSession()

      setIsLoading(false)

      const response = await fetch("/api/auth/login/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email,
          password,
          remember,
        }),
      })

      if (!response.ok) {
        const error = new Error("Login failed")
        error.status = response.status
        throw error
      }

      const data = await response.json()

      if (sessionIdRef.current !== sessionId) {
        return null
      }

      setAccessToken(data.access)
      setRefreshToken(data.refresh)
      setUser(data.user ?? null)

      if (remember) {
        localStorage.setItem(
          REFRESH_TOKEN_KEY,
          data.refresh
        )
      } else {
        localStorage.removeItem(REFRESH_TOKEN_KEY)
      }

      return data
    },
    [invalidateSession]
  )

  const logout = useCallback(async () => {
    const token = refreshToken

    clearAuth()

    if (!token) {
      return
    }

    const controller = new AbortController()

    const timeoutId = setTimeout(() => {
      controller.abort()
    }, REQUEST_TIMEOUT_MS)

    try {
      await fetch("/api/auth/logout/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          refresh: token,
        }),
        signal: controller.signal,
      })
    } catch {
      // Local authentication is already cleared.
    } finally {
      clearTimeout(timeoutId)
    }
  }, [refreshToken, clearAuth])

  useEffect(() => {
    if (!refreshToken || accessToken) {
      return undefined
    }

    const timer = setTimeout(() => {
      refresh().finally(() => {
        setIsLoading(false)
      })
    }, 0)

    return () => clearTimeout(timer)
  }, [refreshToken, accessToken, refresh])

  useEffect(() => {
    if (!accessToken || !refreshToken) {
      return undefined
    }

    const expiration = getTokenExpiration(accessToken)

    if (!expiration) {
      return undefined
    }

    const delay = Math.max(
      expiration - Date.now() - REFRESH_BUFFER_MS,
      0
    )

    const timer = setTimeout(() => {
      refresh()
    }, delay)

    return () => clearTimeout(timer)
  }, [accessToken, refreshToken, refresh])

  useEffect(() => {
    return () => {
      sessionIdRef.current += 1
      abortActiveRefresh()
    }
  }, [abortActiveRefresh])

  const value = {
    accessToken,
    user,
    isAuthenticated: Boolean(accessToken),
    isLoading,
    login,
    logout,
    refresh,
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export default AuthProvider