import { Link } from "react-router-dom";
import "./StartupCard.css";

function StartupCard({ startup }) {
    if (!startup) return null;

    return (
        <Link to={`/startups/${startup.id}`} className="startup-card">
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
    )
}

export default StartupCard;