import { useState } from "react"
import { Link, useNavigate } from "react-router-dom"

import "./Header.css"


function Header() {
  const [searchQuery, setSearchQuery] = useState("")
  const navigate = useNavigate()
  const isAuthenticated = false

  const handleSearch = (event) => {
    event.preventDefault()

    const query = searchQuery.trim()

    if (query) {
      navigate(`/search?q=${encodeURIComponent(query)}`)
    }
  }

  return (
    <header className="header">
      <div className="header__container">
        <Link className="header__logo" to="/">
          Forum
        </Link>

        <form className="header__search" onSubmit={handleSearch}>
          <input
            aria-label="Search"
            onChange={(event) => setSearchQuery(event.target.value)}
            placeholder="Search startups and projects"
            type="search"
            value={searchQuery}
          />

          <button type="submit">
            Search
          </button>
        </form>

        <nav className="header__navigation">
          <Link to="/">Home</Link>
          <Link to="/startups/1">Startups</Link>
          <Link to="/dashboard">Dashboard</Link>
          <Link to="/messages">Messages</Link>
        </nav>

        <div className="header__auth">
          {isAuthenticated ? (
            <Link className="header__login" to="/dashboard">
              Account
            </Link>
          ) : (
            <>
              <Link className="header__login" to="/login">
                Login
              </Link>

              <Link className="header__register" to="/register">
                Register
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  )
}

export default Header