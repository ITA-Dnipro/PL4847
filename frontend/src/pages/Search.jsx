import { useSearchParams } from "react-router-dom"


function Search() {
  const [searchParams] = useSearchParams()
  const query = searchParams.get("q") ?? ""

  return (
    <main>
      <h1>Search</h1>

      <p>
        Search results for: {query || "No search query"}
      </p>
    </main>
  )
}

export default Search