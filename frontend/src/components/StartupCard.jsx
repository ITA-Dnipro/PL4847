import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import "./StartupCard.css";

const API_BASE = import.meta.env.VITE_API_URL;
const API_PREFIX = API_BASE ?? "";
const SUBSCRIBE_URL = `${API_PREFIX}/api/subscribe/`;
const TOAST_DURATION_MS = 3000;

function getCsrfToken() {
    const match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
    return match ? decodeURIComponent(match[1]) : '';
}

function StartupCard({ startup }) {

    const [subscribed, setSubscribed] = useState(false);
    const [subscribing, setSubscribing] = useState(false);
    const [toast, setToast] = useState(null);
    const toastTimeoutRef = useRef(null);

    useEffect(() => {
        return () => {
            if (toastTimeoutRef.current) clearTimeout(toastTimeoutRef.current);
        };
    }, []);

    if (!startup) return null;

    function showToast(type, message) {
        setToast({ type, message });
        if (toastTimeoutRef.current) clearTimeout(toastTimeoutRef.current);
        toastTimeoutRef.current = setTimeout(() => setToast(null), TOAST_DURATION_MS);
    }

    async function handleSubscribe(event) {
        event.preventDefault();
        event.stopPropagation();

        if (subscribing || subscribed) return;

        setSubscribing(true);
        try {
            const token = localStorage.getItem('access') || localStorage.getItem('token');
            const headers = {
                "Content-Type": "application/json",
                "X-CSRFToken": getCsrfToken(),
            };
            if (token) {
                headers["Authorization"] = `Bearer ${token}`;
            }

            const response = await fetch(SUBSCRIBE_URL, {
                method: "POST",
                headers,
                credentials: "same-origin",
                body: JSON.stringify({ startup_id: startup.id }),
            });

            if (response.status === 401 || response.status === 403) {
                showToast("error", "Будь ласка, увійдіть у систему для підписки.");
                // Припускаємо, що у вас є роутинг на /login або функція переходу
                window.location.href = "/login"; 
                return;
            }

            if (!response.ok) throw new Error("Subscribe request failed");

            setSubscribed(true);
            showToast("success", `Ви підписалися на оновлення «${startup.company_name}»`);
        } catch {
            showToast("error", "Не вдалося підписатися. Спробуйте ще раз.");
        } finally {
            setSubscribing(false);
        }
    }

    return (
         <div className="startup-card">
            <Link to={`/startups/${startup.id}`} className="startup-card__link">
                <div className="startup-card__image-wrap">
                    <img
                        className="startup-card__image"
                        src={startup.thumbnail_url}
                        alt={startup.company_name || "Startup"}
                    />
                </div>
                <div className="startup-card__body">
                    <h3 className="startup-card__name">{startup.company_name}</h3>
                    <p className="startup-card__location">{startup.location}</p>
                    <p className="startup-card__description">{startup.short_description}</p>
                    <div className="startup-card__tags">
                        {startup.tags?.map((tag) => (
                            <span className="startup-card__tag" key={tag}>{tag}</span>
                        ))}
                    </div>
                </div>
            </Link>

            <button
                type="button"
                className={`startup-card__subscribe${subscribed ? " startup-card__subscribe--active" : ""}`}
                onClick={handleSubscribe}
                disabled={subscribing}
                aria-pressed={subscribed}
                aria-label={subscribed ? "Ви підписані на оновлення" : "Підписатися на оновлення"}
                title={subscribed ? "Ви підписані на оновлення" : "Підписатися на оновлення"}
            >
                <svg viewBox="0 0 24 24" className="startup-card__subscribe-icon" aria-hidden="true">
                    <path
                        d="M12 2.5l2.9 6.32 6.93.66-5.24 4.66 1.55 6.82L12 17.77l-6.14 3.19 1.55-6.82L2.17 9.48l6.93-.66L12 2.5z"
                        fill={subscribed ? "currentColor" : "none"}
                        stroke="currentColor"
                        strokeWidth="1.6"
                        strokeLinejoin="round"
                    />
                </svg>
            </button>

            {toast && (
                <div
                    className={`startup-card__toast startup-card__toast--${toast.type}`}
                    role="status"
                    aria-live="polite"
                >
                    {toast.message}
                </div>
             )}
        </div>
    );
}

export default StartupCard;