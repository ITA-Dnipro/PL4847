import { useEffect, useState } from "react";
import StartupCard from "./StartupCard";
import mockStartups from "../mocks/Startups";
import "./StartupsGrid.css";

const API_BASE = import.meta.env.VITE_API_URL;
const INITIAL_URL = `${API_BASE}/api/startups/?page=1&page_size=8`;

function StartupsGrid() {
    const [startups, setStartups] = useState([]);
    const [nextUrl, setNextUrl] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(false);

    useEffect(() => {
        async function loadStartups() {
            try {
                const response = await fetch(INITIAL_URL);
                if (!response.ok) throw new Error("Bad response");
                const data = await response.json();
                setStartups(data.results);
                setNextUrl(data.next);
            } catch {
                setStartups(mockStartups);
                setNextUrl(null);
                setError(true);
            } finally {
                setLoading(false);
            }
        }
        loadStartups();
    }, []);

    async function handleViewMore() {
        if (!nextUrl) return;

        try {
            const response = await fetch(nextUrl);
            if (!response.ok) throw new Error("Bad response");
            const data = await response.json();
            setStartups((prev) => [...prev, ...data.results]);
            setNextUrl(data.next);
        } catch {
            setError(true);
        }
    }

    

    if (loading) return <p>Loading...</p>;              
    if (!startups.length) return <p>No startups yet.</p>;

    return (
        <div>
            {error && (
                <p className="startups-grid__error">
                    Couldn't load live data — showing sample startups.
                </p>
            )}
            <div className="startups-grid">
                {startups.map((s) => (
                    <StartupCard key={s.id} startup={s} />
                ))}
            </div>
            {nextUrl && (
                <button className="startups-grid__view-more" onClick={handleViewMore}>
                    View more
                </button>
            )}
        </div>
    );
}

export default StartupsGrid;