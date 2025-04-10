import styles from './DocsView.module.css';

const batchModules = [
  {
    name: 'Batch 1',
    path: 'goldfish-training-batch1-main',
    status: 'runnable foundation',
    command: 'python demos/needle_insertion_v1.py --quick',
    summary:
      'This is the first working version and the baseline module. It has the full needle insertion environment, Kelvin-Voigt tissue layers, PPO training, reward shaping, and JSON logs in one place.',
    includes: [
      'NeedleInsertionEnv, this is where the agent actually moves the needle',
      'BiologicalCostModule, this scores strain, force, vessels, and inflammation',
      'GoldfishPPOTrainer, this is the repeatable PPO training path',
      'SimulationWorldModel, this is the rollout model for later planning work',
    ],
  },
  {
    name: 'Batch 2',
    path: '-goldfish-training-batch2-Kelvin-Voigt-main',
    status: 'Kelvin-Voigt continuation',
    command: 'python demos/needle_insertion_v1.py --timesteps 300000 --output ./results',
    summary:
      'This is the second batch, and it keeps the same needle insertion target so the comparison does not get messy. The point is to keep the Kelvin-Voigt work separate from Batch 1, train it as its own module, and compare the outputs cleanly.',
    includes: [
      'Same package shape as Batch 1, so the comparison is not guesswork',
      'Architecture docs for the observation space, action space, reward, and training loop',
      'Tests for the environment and the core pieces',
      'Project summary cleaned up so it only explains the technical module',
    ],
  },
];

const architectureRows = [
  ['Environment', 'NeedleInsertionEnv', 'This is the Gym-style task. The agent gets an observation and sends back a 6D action.'],
  ['Physics', 'LayeredTissueSimulator', 'This models the soft, muscle, and fat layers with Kelvin-Voigt mechanics.'],
  ['Training', 'GoldfishPPOTrainer', 'This is the PPO training wrapper. It uses the 15D observation and saves the policy.'],
  ['Biology', 'BiologicalCostModule', 'This scores trauma, force, vessel distance, and inflammation after the environment step.'],
  ['Planning', 'SimulationWorldModel', 'This is the next-state model from rollouts. It is useful later for lookahead planning.'],
];

export default function DocsView() {
  return (
    <main className={styles.page}>
      <header className={styles.header}>
        <div>
          <p className={styles.kicker}>Goldfish manual</p>
          <h1>Before you train</h1>
          <p className={styles.lede}>
            I built Goldfish as a surgical robot training environment for needle
            insertion into layered soft tissue, and this page is the simple map of what
            is here. I also wanted it to show what each batch does and how I keep the
            runs separate, so I do not confuse one result for another later.
          </p>
        </div>
        <aside className={styles.notice}>
          <strong>Current scope</strong>
          <span>
            I have a runnable reinforcement learning environment right now, and I think
            that is the honest scope. I do not have a validated clinical simulator, FDA
            package, or robot controller yet, and that is important to say clearly.
          </span>
        </aside>
      </header>

      <section className={styles.section}>
        <h2>Start here</h2>
        <p>
          Batch 1 is the smallest working baseline, and Batch 2 is the next
          Kelvin-Voigt batch. The important thing is to keep results, checkpoints, and
          evidence logs in separate folders because otherwise the comparison gets
          confusing fast.
        </p>
        <div className={styles.steps}>
          <div><span>1</span>Install requirements inside the batch folder being tested.</div>
          <div><span>2</span>Run the quick demo first to make sure the environment works.</div>
          <div><span>3</span>Run the longer training job only after the quick run passes.</div>
          <div><span>4</span>Compare success rate, trauma, vessel distance, and reward.</div>
        </div>
      </section>

      <section className={styles.section}>
        <h2>Trained modules</h2>
        <div className={styles.moduleGrid}>
          {batchModules.map((module) => (
            <article className={styles.module} key={module.name}>
              <div className={styles.moduleTop}>
                <h3>{module.name}</h3>
                <span>{module.status}</span>
              </div>
              <p>{module.summary}</p>
              <code>{module.path}</code>
              <pre>{module.command}</pre>
              <ul>
                {module.includes.map((item) => <li key={item}>{item}</li>)}
              </ul>
            </article>
          ))}
        </div>
      </section>

      <section className={styles.section}>
        <h2>Architecture map</h2>
        <div className={styles.table}>
          {architectureRows.map(([layer, component, detail]) => (
            <div className={styles.row} key={component}>
              <span>{layer}</span>
              <strong>{component}</strong>
              <p>{detail}</p>
            </div>
          ))}
        </div>
      </section>

      <section className={styles.section}>
        <h2>Safety and honesty</h2>
        <p>
          I built the current implementation for research iteration, so PPO training,
          Kelvin-Voigt tissue mechanics, cited biological thresholds, and structured
          logs are the current foundation. I am not claiming full SOFA, PhysiCell, or
          SimVascular integration yet, and the JEPA biological world model is still a
          target architecture until I have real tissue data.
        </p>
      </section>

      <section className={styles.section}>
        <h2>What success looks like</h2>
        <ol className={styles.successList}>
          <li>The quick demo runs without errors in the selected batch folder.</li>
          <li>The full training job saves a policy and evidence output.</li>
          <li>The evaluation gives success rate, mean trauma, and mean reward.</li>
          <li>Batch 1 and Batch 2 outputs stay separate, so the comparison is direct.</li>
        </ol>
      </section>
    </main>
  );
}
