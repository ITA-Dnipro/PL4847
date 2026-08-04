import { useEffect, useRef, useState } from 'react';
import whyWorthMock from '../mocks/whyWorth';
import './WhyWorthGrid.css';

const SKELETON_COUNT = 4;
const SECTION_TITLE = 'Чому варто';

function normalizeWhyWorth(json) {
	const raw = json?.why_worth;
	if (!Array.isArray(raw)) return null;

	const cards = raw
		.filter(
			(card) =>
				card &&
				typeof card.title === 'string' &&
				card.title.trim().length > 0 &&
				typeof card.desc === 'string' &&
				card.desc.trim().length > 0
		)
		.map((card, index) => ({
			id: `why-worth-${index}`,
			title: card.title,
			desc: card.desc,
		}));

	if (cards.length < 4 || card.length > 6) return null;

	return { title: SECTION_TITLE, cards };
}

function fallbackContent() {
	return {
		title: SECTION_TITLE,
		cards: whyWorthMock.map((card, index) => ({
			id: `why-worth-fallback-${index}`,
			title: card.title,
			desc: card.desc,
		})),
	};
}

export default function WhyWorthGrid({ endpoint = '/api/content/landing/' }) {
	const [content, setContent] = useState(null);
	const [status, setStatus] = useState('loading');
	const mounted = useRef(true);

	useEffect(() => {
		mounted.current = true;
		return () => {
			mounted.current = false;
		};
	}, []);

	useEffect(() => {
		const controller = new AbortController();

		async function load() {
			setStatus('loading');

			try {
				const res = await fetch(endpoint, {
					signal: controller.signal,
					headers: { Accept: 'application/json' },
				});
				if (!res.ok) throw new Error(`Request failed: ${res.status}`);
				const json = await res.json();

				if (!mounted.current) return;

				const payload = normalizeWhyWorth(json) ?? fallbackContent();
				setContent(payload);
				setStatus('success');
			} catch (err) {
				if (err.name === 'AbortError' || !mounted.current) return;
				setContent(fallbackContent());
				setStatus('success');
			}
		}

		load();
		return () => controller.abort();
	}, [endpoint]);

	if (status === 'loading') {
		return (
			<section className="whyworth-section" aria-busy="true" aria-label="Чому варто">
				<h2 className="whyworth-title">Чому варто</h2>
				<div className="whyworth-grid" role="list">
					{Array.from({ length: SKELETON_COUNT }).map((_, index) => (
						<div key={index} className="whyworth-skeleton-card" role="listitem">
							<span className="whyworth-skeleton-title" />
							<span className="whyworth-skeleton-desc" />
						</div>
					))}
				</div>
			</section>
		);
	}

	return (
		<section className="whyworth-section" aria-label={content.title}>
			<h2 className="whyworth-title">{content.title}</h2>
			<div className="whyworth-grid" role="list">
				{content.cards.map((card) => (
					<article
						key={card.id}
						className="whyworth-card"
						role="listitem"
						tabIndex={0}
						aria-label={card.title}
					>
						<h3 className="whyworth-card-title">{card.title}</h3>
						<p className="whyworth-card-desc">{card.desc}</p>
					</article>
				))}
			</div>
		</section>
	);
}
