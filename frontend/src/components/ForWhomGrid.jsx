import React, { useEffect, useRef, useState } from 'react';
import './ForWhomGrid.css';
import { ICONS } from './icons';

const SKELETON_COUNT = 8;
const SECTION_TITLE = 'Для кого';

function normalizeForWhom(json) {
  const raw = json?.for_whom;
  if (!Array.isArray(raw)) return null;

  const cards = raw
    .filter((c) => c && typeof c.title === 'string' && c.title.trim().length > 0)
    .map((c, i) => ({
      id: `${c.icon || 'card'}-${i}`,
      icon: c.icon,
      title: c.title,
      desc: typeof c.desc === 'string' ? c.desc : null,
    }));

  if (cards.length === 0) return null;

  return { title: SECTION_TITLE, cards };
}

export default function ForWhomGrid({ endpoint = '/api/content/landing/' }) {
  const [status, setStatus] = useState('loading');
  const [content, setContent] = useState(null);
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

        const payload = normalizeForWhom(json);

        if (payload) {
          setContent(payload);
          setStatus('success');
        } else {
          setContent(null);
          setStatus('empty');
        }
      } catch (err) {
        if (err.name === 'AbortError' || !mounted.current) return;
        setContent(null);
        setStatus('error');
      }
    }

    load();
    return () => controller.abort();
  }, [endpoint]);

  if (status === 'loading') {
    return (
      <section className="forwhom-section" aria-busy="true" aria-label="Для кого">
        <div className="forwhom-inner">
          <h2 className="forwhom-title">Для кого</h2>
          <div className="forwhom-grid" role="list">
            {Array.from({ length: SKELETON_COUNT }).map((_, i) => (
              <div key={i} className="forwhom-skeleton-card" role="listitem">
                <span className="forwhom-skeleton-icon" />
                <span className="forwhom-skeleton-line" />
              </div>
            ))}
          </div>
        </div>
      </section>
    );
  }

  if (status === 'error') {
    return (
      <section className="forwhom-section" aria-label="Для кого">
        <div className="forwhom-inner">
          <h2 className="forwhom-title">Для кого</h2>
          <p className="forwhom-error-note">
            Не вдалося завантажити дані. Спробуйте оновити сторінку пізніше.
          </p>
        </div>
      </section>
    );
  }

  if (status === 'empty') {
    return (
      <section className="forwhom-section" aria-label="Для кого">
        <div className="forwhom-inner">
          <h2 className="forwhom-title">Для кого</h2>
          <p className="forwhom-error-note">Контент ще не додано.</p>
        </div>
      </section>
    );
  }

  return (
    <section className="forwhom-section" aria-label={content.title}>
      <div className="forwhom-inner">
        <h2 className="forwhom-title">{content.title}</h2>

        <div className="forwhom-grid" role="list">
          {content.cards.map((card) => {
            const Icon = ICONS[card.icon] || ICONS.people;
            return (
              <div key={card.id} className="forwhom-card" role="listitem" tabIndex={0}>
                <span className="forwhom-icon-wrap">
                  <Icon />
                </span>
                <p className="forwhom-card-title">{card.title}</p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
} 