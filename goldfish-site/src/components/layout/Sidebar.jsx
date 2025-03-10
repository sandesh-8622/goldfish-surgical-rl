import styles from './Sidebar.module.css'

export default function Sidebar() {
  return (
    <aside className={styles.sidebar}>
      <div className={styles.logo}>goldfish</div>
      <nav>
        <ul>
          <li>Overview</li>
          <li>Problem</li>
          <li>Reward</li>
          <li>System</li>
          <li>Research</li>
          <li>Docs</li>
        </ul>
      </nav>
    </aside>
  )
}
