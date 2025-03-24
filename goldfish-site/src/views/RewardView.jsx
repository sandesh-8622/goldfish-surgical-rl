import styles from './RewardView.module.css'

export default function RewardView() {
  return (
    <section className={styles.reward}>
      <h1>The reward function</h1>
      <p>
        every threshold in the reward function is taken from a real biomechanics
        paper. none of them are guessed.
      </p>
    </section>
  )
}
