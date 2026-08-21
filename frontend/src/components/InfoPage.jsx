import { useParams } from 'react-router-dom';

function InfoPage() {
    const { slug } = useParams();

    return (
        <div className="info-page">
            <h1>Сторінка: {slug.replace('-', ' ')}</h1>
            <p>Контент для розділу {slug} знаходиться у розробці.</p>
        </div>
    );
}

export default InfoPage;
