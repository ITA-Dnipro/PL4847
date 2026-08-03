import { render, screen, fireEvent } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import StartupsGrid from "./StartupsGrid"

const originalFetch = global.fetch

function renderGrid() {
    return render(
        <MemoryRouter>
            <StartupsGrid />
        </MemoryRouter>
    )
}

describe("StartupsGrid", () => {
    afterEach(() => {
        vi.restoreAllMocks()

        if (originalFetch === undefined) {
            delete global.fetch
        } else {
            global.fetch = originalFetch
        }
    })

    it('shows loading state before fetch resolves', () => {
        global.fetch = vi.fn(() => new Promise(() => {}))
        renderGrid()
        expect(screen.getByText("Loading...")).toBeInTheDocument()
    })

    it('shows resolved fetch response', async () => {
        global.fetch = vi.fn().mockResolvedValue({
            ok: true,
            json: async () => ({
                count:2,
                next: null,
                previous: null,
                results: [
                    { id:1, company_name: "First Company", short_description: "...", location: "Kyiv", tags: []},
                    { id:2, company_name: "Second Company", short_description: "...", location: "Dnipro", tags: []},
                ],
            }),
        })
        
        renderGrid()
        expect(await screen.findByText("First Company")).toBeInTheDocument()
        expect(screen.getByText("Second Company")).toBeInTheDocument()
        expect(screen.queryByText("Loading...")).not.toBeInTheDocument()
    })

    it("shows empty state when there are no results", async () => {
        global.fetch = vi.fn().mockResolvedValue({
            ok: true,
            json: async () => ({
                count: 0,
                next: null,
                previous: null,
                results: [],
            }),
        })
        
        renderGrid()
        expect(await screen.findByText("No startups yet.")).toBeInTheDocument()
    })
    
    it('falls back to mock startups when fetch rejects', async () => {
        global.fetch = vi.fn().mockRejectedValue(new Error("Network Error"))
        
        renderGrid()
        expect(await screen.findByText("Handmade Co")).toBeInTheDocument()
        expect(
            screen.getByText("Couldn't load live data — showing sample startups.")
        ).toBeInTheDocument()
    })
    
    it("falls back to mock startups when response is not ok", async () => {
        global.fetch = vi.fn().mockResolvedValue({ok: false})
        
        renderGrid()
        expect(await screen.findByText("Handmade Co")).toBeInTheDocument()
    })
    
    it("fetches and appends the next page when 'View more' is clicked", async () => {
        global.fetch = vi.fn().mockResolvedValueOnce({
            ok: true,
            json: async () => ({
                count: 2,
                next: "http://api.test/api/startups/?page=2",
                previous: null,
                results:[{ id: 1, company_name: "First Company", short_description: "...", location: "Kyiv", tags: []}]
            }),
        }).mockResolvedValueOnce({
            ok: true,
            json: async () => ({
                count: 2,
                next: null,
                previous: "http://api.test/api/startups/?page=1",
                results: [{id: 2, company_name: "Second Company", short_description: "...", location: "Dnipro", tags: []}]
            })
        })

        renderGrid()
        expect(await screen.findByText("First Company")).toBeInTheDocument()

        fireEvent.click(screen.getByText("View more"))

        expect(await screen.findByText("Second Company")).toBeInTheDocument()
        expect(screen.getByText("First Company")).toBeInTheDocument()
        expect(screen.queryByText("View more")).not.toBeInTheDocument()
        expect(global.fetch).toHaveBeenNthCalledWith(2, "/api/startups/?page=2")
    })

    it("shows a pagination-specific error when loading the next page fails", async () => {
        global.fetch = vi.fn().mockResolvedValueOnce({
            ok: true,
            json: async () => ({
                count: 2,
                next: "http://api.test/api/startups/?page=2",
                previous: null,
                results: [{ id: 1, company_name: "First Company", short_description: "...", location: "Kyiv", tags: [] }],
            }),
        }).mockRejectedValueOnce(new Error("Network error"))

        renderGrid()
        expect(await screen.findByText("First Company")).toBeInTheDocument()

        fireEvent.click(screen.getByText("View more"))

        expect(await screen.findByText("Couldn't load more startups right now.")).toBeInTheDocument()
        expect(screen.getByText("First Company")).toBeInTheDocument()
        expect(
            screen.queryByText("Couldn't load live data — showing sample startups.")
        ).not.toBeInTheDocument()
        expect(screen.getByText("View more")).toBeInTheDocument()
    })

    it("disables view more while the next page request is in flight", async () => {
        let resolveNextPage;

        global.fetch = vi
            .fn()
            .mockResolvedValueOnce({
                ok: true,
                json: async () => ({
                    count: 2,
                    next: "http://api.test/api/startups/?page=2",
                    previous: null,
                    results: [{ id: 1, company_name: "First Company", short_description: "...", location: "Kyiv", tags: [] }],
                }),
            })
            .mockReturnValueOnce(
                new Promise((resolve) => {
                    resolveNextPage = resolve;
                })
            )

        renderGrid()
        expect(await screen.findByText("First Company")).toBeInTheDocument()

        const viewMoreButton = screen.getByRole("button", { name: "View more" })
        fireEvent.click(viewMoreButton)
        fireEvent.click(viewMoreButton)

        expect(global.fetch).toHaveBeenCalledTimes(2)
        expect(screen.getByRole("button", { name: "Loading..." })).toBeDisabled()

        resolveNextPage({
            ok: true,
            json: async () => ({
                count: 2,
                next: null,
                previous: "http://api.test/api/startups/?page=1",
                results: [{ id: 2, company_name: "Second Company", short_description: "...", location: "Dnipro", tags: [] }],
            }),
        })

        expect(await screen.findByText("Second Company")).toBeInTheDocument()
        expect(screen.queryByRole("button", { name: "Loading..." })).not.toBeInTheDocument()
    })
})