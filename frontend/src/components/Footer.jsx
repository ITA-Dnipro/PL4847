import { useEffect, useRef, useState } from 'react';
import './Footer.css';
import { fetchFooterContent } from './Footer_api';
import { CraftmergeMark, MailIcon, PhoneIcon, OpentechLogo } from './FooterIcons';

const COMPANY = {
  name: 'CRAFTMERGE',
  address_lines: ['Львівська Політехніка', 'вул. Степана Бандери 12, Львів'],
  email: 'qwerty@gmail.com',
  phone: '+38 050 234 23 23',
};

const NAV_TITLES = { left: 'Підприємства', right: 'Сектори' };

const LEGAL_LINKS = [
  { id: 'privacy', label: 'Політика конфіденційності', url: '/privacy' },
  { id: 'terms', label: 'Умови користування', url: '/terms' },
  { id: 'feedback', label: 'Зворотній зв’язок', url: '/feedback' },
];

function NavGroup({ side, links }) {
  if (!links || links.length === 0) return null;
  return (
    <nav aria-label={NAV_TITLES[side]} className="footer__group">
      <h3>{NAV_TITLES[side]}</h3>
      <ul>
        {links.map((link) => (
          <li key={link.url}>
            <a href={link.url}>{link.name}</a>
          </li>
        ))}
      </ul>
    </nav>
  );
}

export default function Footer() {
  const [footerLinks, setFooterLinks] = useState(null);
  const [error, setError] = useState(false);
  const mounted = useRef(true);

  useEffect(() => {
    mounted.current = true;
    return () => {
      mounted.current = false;
    };
  }, []);

  useEffect(() => {
    const controller = new AbortController();

    fetchFooterContent(controller.signal)
      .then((data) => {
        if (!mounted.current) return;
        setFooterLinks(data?.footer_links ?? { left: [], right: [] });
      })
      .catch((err) => {
        if (err.name === 'AbortError' || !mounted.current) return;
        setError(true);
      });

    return () => controller.abort();
  }, []);

  if (error) {
    return (
      <footer className="footer" aria-label="Футер сайту">
        <div className="footer__inner">
          <p className="footer__error">Не вдалося завантажити вміст футера.</p>
        </div>
      </footer>
    );
  }

  if (!footerLinks) {
    return <footer className="footer" aria-label="Футер сайту" aria-busy="true" />;
  }

  const { left = [], right = [] } = footerLinks;

  return (
    <footer className="footer" aria-label="Футер сайту">
      <div className="footer__inner">
        <div className="footer__brand-col">
          <div className="footer__logo">
            <CraftmergeMark />
            <span>{COMPANY.name}</span>
          </div>

          <address>
            {COMPANY.address_lines.map((line) => (
              <p key={line}>{line}</p>
            ))}
          </address>

          <ul className="footer__contacts">
            <li>
              <a href={`mailto:${COMPANY.email}`}>
                <MailIcon />
                {COMPANY.email}
              </a>
            </li>
            <li>
              <a href={`tel:${COMPANY.phone.replace(/\s+/g, '')}`}>
                <PhoneIcon />
                {COMPANY.phone}
              </a>
            </li>
          </ul>
        </div>

        <div className="footer__nav-col">
          <NavGroup side="left" links={left} />
          <NavGroup side="right" links={right} />
        </div>

        <div className="footer__meta-col">
          <div className="footer__credit">
            <span className="footer__credit-logo">
              <OpentechLogo /> <span>| softserve</span>
            </span>
          </div>

          <ul className="footer__legal">
            {LEGAL_LINKS.map((link) => (
              <li key={link.id}>
                <a href={link.url}>{link.label}</a>
              </li>
            ))}
          </ul>

          <p className="footer__copyright">
            Copyright {new Date().getFullYear()} Forum. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}