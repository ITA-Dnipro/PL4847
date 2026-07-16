import { useParams  } from "react-router-dom";

function StartupDetail() {
    const { id } = useParams()

    return (
        <div>
            <h1>Startup details</h1>
            <p>Startup ID: {id}</p>
        </div>
    )
}

export default StartupDetail;