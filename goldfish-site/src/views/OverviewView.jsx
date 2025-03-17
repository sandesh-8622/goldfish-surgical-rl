import styles from './OverviewView.module.css'

export default function OverviewView() {
  return (
    <section className={styles.overview}>
      <h1>goldfish</h1>
      <p className={styles.tagline}>
        a surgical robot training environment built on physics, not vibes.
      </p>
    </section>
  )
}
