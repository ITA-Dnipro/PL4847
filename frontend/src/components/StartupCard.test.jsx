import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import StartupCard from './StartupCard'

const mockStartup = {
    id: 1,
    company_name: "Test Company",
    short_description: "Small company created for testing",
    thumbnail_url: "Some url",
    location: "Kyiv",
    tags: ["testing", "companies"],
}

function renderCard(startup) {
    return render(
        <MemoryRouter>
            <StartupCard startup={startup} />
        </MemoryRouter>
    )
}

describe('StartupCard', () => {
    it('renders startup details', () => {
        renderCard(mockStartup)
        expect(screen.getByText(mockStartup.company_name)).toBeInTheDocument()
        expect(screen.getByText(mockStartup.location)).toBeInTheDocument()
        expect(screen.getByText(mockStartup.short_description)).toBeInTheDocument()
        mockStartup.tags.forEach((tag) => {
            expect(screen.getByText(tag)).toBeInTheDocument()
        })
    })

    it('links to the startup deatil page', () => {
        renderCard(mockStartup)
        const link = screen.getByRole("link")
        expect(link).toHaveAttribute("href", `/startups/${mockStartup.id}`)
    })

    it('renders nothing when startup is missing', () => {
        const { container } = renderCard(undefined)
        expect(container).toBeEmptyDOMElement()
    })
})