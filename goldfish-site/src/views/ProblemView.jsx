// the problem statement view
import styles from './ProblemView.module.css'

export default function ProblemView() {
  return (
    <section className={styles.problem}>
      <h1>The problem</h1>
      <p>
        surgical robots are getting better at moving. they are not getting
        better at deciding what to do. most reward functions reduce surgery
        to a positioning task. surgery is not a positioning task.
      </p>
    </section>
  )
}
