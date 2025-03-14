import { NavLink } from 'react-router-dom';
import styles from './Sidebar.module.css';

const NAV = [
  { to: '/overview',  label: 'overview' },
  { to: '/problem',   label: 'the problem' },
  { to: '/system',    label: 'the system' },
  { to: '/research',  label: 'research' },
  { to: '/docs',      label: 'docs' },
  { to: '/reward',    label: 'reward engineering' },
];

const GitHubIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
    <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z"/>
  </svg>
);

export default function Sidebar() {
  return (
    <aside className={styles.sidebar}>
      <div className={styles.inner}>
        <div className={styles.brand}>
          <span className={styles.brandName}>goldfish</span>
          <span className={styles.brandSub}>surgical simulation platform</span>
        </div>
        <nav className={styles.nav}>
          {NAV.map(({ to, label }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}
            >
              {label}
            </NavLink>
          ))}
        </nav>
        <div className={styles.footer}>
          <a
            href="https://github.com/sandesh-8622"
            target="_blank"
            rel="noopener noreferrer"
            className={styles.githubLink}
            aria-label="GitHub"
          >
            <GitHubIcon />
          </a>
        </div>
      </div>
    </aside>
  );
}
