import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import StartupCard from "./StartupCard";
import mockStartups from "../mocks/Startups";
import "./StartupsGrid.css";

const API_BASE = import.meta.env.VITE_API_URL;
const API_PREFIX = API_BASE ?? "";
const INITIAL_URL = `${API_PREFIX}/api/startups/?page=1&page_size=8`;

function normalizeNextUrl(nextUrl) {
    if (!nextUrl) return null;

    if (nextUrl.startsWith("/api/")) {
        return `${API_PREFIX}${nextUrl}`;
    }

    try {
        const parsedUrl = new URL(nextUrl, window.location.origin);

        if (parsedUrl.pathname.startsWith("/api/")) {
            return parsedUrl.toString();
        }
    } catch {
        return nextUrl;
    }

    return nextUrl;
}

function StartupsGrid() {
    const [startups, setStartups] = useState([]);
    const [nextUrl, setNextUrl] = useState(null);
    const [loading, setLoading] = useState(true);
    const [loadingMore, setLoadingMore] = useState(false);
    const [initialLoadError, setInitialLoadError] = useState(false);
    const [paginationError, setPaginationError] = useState(false);

    useEffect(() => {
        async function loadStartups() {
            try {
                const response = await fetch(INITIAL_URL);
                if (!response.ok) throw new Error("Bad response");
                const data = await response.json();
                setStartups(data.results);
                setNextUrl(normalizeNextUrl(data.next));
                setInitialLoadError(false);
            } catch {
                setStartups(mockStartups);
                setNextUrl(null);
                setInitialLoadError(true);
            } finally {
                setLoading(false);
            }
        }
        loadStartups();
    }, []);

    async function handleViewMore() {
        if (!nextUrl || loadingMore) return;

        try {
            setLoadingMore(true);
            setPaginationError(false);
            const response = await fetch(nextUrl);
            if (!response.ok) throw new Error("Bad response");
            const data = await response.json();
            setStartups((prev) => [...prev, ...data.results]);
            setNextUrl(normalizeNextUrl(data.next));
        } catch {
            setPaginationError(true);
        } finally {
            setLoadingMore(false);
        }
    }

    return (
        <section className="startups-section" aria-label="Нові учасники">
            <div className="startups-section__header">
                <h2 className="startups-section__title">Нові учасники</h2>
                <Link to="/startups" className="startups-section__link">
                    <span className="startups-section__link-frame">
                        <span className="startups-section__link-label">Всі підприємства</span>
                        <span className="startups-section__link-underline" />
                    </span>
                    <span className="startups-section__link-icon" aria-hidden="true">→</span>
                </Link>
            </div>

            {initialLoadError && (
                <p className="startups-grid__error">
                    Couldn't load live data — showing sample startups.
                </p>
            )}

            {loading ? (
                <p>Loading...</p>
            ) : !startups.length ? (
                <p>No startups yet.</p>
            ) : (
                <>
                    <div className="startups-grid">
                        {startups.map((s) => (
                            <StartupCard key={s.id} startup={s} />
                        ))}
                    </div>
                    {paginationError && (
                        <p className="startups-grid__pagination-error">
                            Couldn't load more startups right now.
                        </p>
                    )}
                    {nextUrl && (
                        <button
                            className="startups-grid__view-more"
                            onClick={handleViewMore}
                            disabled={loadingMore}
                        >
                            {loadingMore ? "Loading..." : "View more"}
                        </button>
                    )}
                </>
            )}
        </section>
    );
}

export default StartupsGrid;