import styles from './RewardView.module.css';

const versions = [
  {
    name: 'v0',
    title: 'I only rewarded distance',
    result: '12 percent success',
    text:
      'I started with the most obvious reward I could write, where if the needle got closer to the target it got points, and at first that felt reasonable enough. But the agent did exactly what I asked, which was the problem, because it moved straight through the tissue as fast as possible since I never told it that damage mattered.',
    code: 'reward = (prev_distance - distance) * 8.0 - 0.05',
  },
  {
    name: 'v1',
    title: 'I added tissue trauma',
    result: '34 percent success',
    text:
      'Then I added a penalty when strain passed the yield limit for the tissue layer the needle was inside, and this helped right away because the agent finally had a reason to slow down. Moving fast made the force spike, so it became less aggressive, but it still did not care about blood vessels because I had not put that into the reward yet.',
    code: 'reward = progress * 8.0 - step_trauma * 3.0 - 0.05',
  },
  {
    name: 'v2',
    title: 'I added vessel distance',
    result: '61 percent success',
    text:
      'This was the biggest jump because I added a penalty when the needle moved within 3 mm of a vessel, and that changed the behavior a lot. This mattered because a tiny strain mistake and a vessel puncture are not the same thing, as one is annoying and the other can become a serious surgical problem.',
    code: 'reward = progress * 8.0 - trauma * 3.0 - max(0, 3.0 - vessel_mm) * 5.0 - 0.05',
  },
  {
    name: 'v3',
    title: 'I made time matter',
    result: '78 percent success',
    text:
      'After the safety penalties started working, the agent found another loophole and started moving in these huge safe arcs around everything. Technically that was safe, but it was also not useful, so the step penalty made it care about finishing in a reasonable number of moves.',
    code: 'step_penalty = -0.05',
  },
  {
    name: 'v4',
    title: 'I made success depend on trauma',
    result: '87 percent success',
    text:
      'The final version gives a bonus for reaching the target, but a clean insertion gets more reward than a messy one, which is the behavior I actually wanted. I also kept a floor in the formula because if the bonus can go all the way to zero, the agent learns that not trying is safer than trying badly.',
    code: 'if success: reward += 100.0 * (0.5 + 0.5 * (1.0 - cumulative_trauma))',
  },
];

const mistakes = [
  'I first treated all costs as equal, and that was wrong because vessel damage is not the same as a little extra strain.',
  'I tried using the full cost module as the reward, but it was too noisy for PPO, so I kept the reward simple and used the cost module for evaluation instead.',
  'I used one yield threshold for all tissues at first, which was wrong because muscle tears earlier than soft tissue.',
  'I tried a success bonus with no floor, and the agent started learning that not trying could be safer than reaching the target badly.',
];

export default function RewardView() {
  return (
    <main className={styles.page}>
      <header className={styles.header}>
        <p className={styles.kicker}>Training notes</p>
        <h1>Reward function engineering</h1>
        <p>
          I wrote this from my reward function notes, and I removed the images because
          they were not needed here. The main thing is pretty simple: I changed one
          reward term at a time, trained again, watched what the agent did, and then
          kept the changes that made the needle insertion safer.
        </p>
      </header>

      <section className={styles.section}>
        <h2>What I was training</h2>
        <p>
          I trained a PPO agent to insert a needle into layered soft tissue, and at
          first this sounds easy because the obvious goal is just to reach the target.
          But in surgery that is not enough, because the needle also has to avoid
          vessels, keep strain under the damage threshold, and not take some ridiculous
          path just to look safe.
        </p>
        <p>
          The tissue uses a Kelvin-Voigt model, and the simple way I think about it is
          a spring and a shock absorber working together. The spring resists
          compression, the damper resists speed, and so if the agent rushes, force goes
          up and damage becomes more likely.
        </p>
      </section>

      <section className={styles.section}>
        <h2>The final reward</h2>
        <pre className={styles.code}>{`reward =
  (prev_distance - distance) * 8.0       # I reward progress toward the target
  - step_trauma * 3.0                    # I punish tissue damage when strain gets too high
  - max(0.0, 3.0 - vascular_distance_mm) * 5.0
                                          # I punish the needle for getting too close to vessels
  - 0.05                                  # I add a small cost so it does not waste steps

if success:
  reward += 100.0 * (0.5 + 0.5 * (1.0 - cumulative_trauma))
                                          # I still reward success, but cleaner success gets more`}</pre>
        <p>
          I kept the reward simple on purpose because PPO needs a signal it can
          actually follow. The biological cost module can be more detailed because that
          is for logging and evaluation, so it is using the same data but doing a
          different job.
        </p>
      </section>

      <section className={styles.section}>
        <h2>How I got there</h2>
        <div className={styles.timeline}>
          {versions.map((version) => (
            <article className={styles.card} key={version.name}>
              <div className={styles.cardTop}>
                <span>{version.name}</span>
                <strong>{version.result}</strong>
              </div>
              <h3>{version.title}</h3>
              <p>{version.text}</p>
              <code>{version.code}</code>
            </article>
          ))}
        </div>
      </section>

      <section className={styles.section}>
        <h2>What the agent sees</h2>
        <p>
          The agent sees fifteen numbers, including needle position, target delta,
          tissue type, strain, insertion force, vascular distance, cumulative trauma,
          and time remaining. I normalized the values because neural networks behave
          better when the inputs live in a similar range.
        </p>
      </section>

      <section className={styles.section}>
        <h2>How I evaluate it</h2>
        <p>
          I do not use the reward as the final human score, because after training I
          use an insertion quality score instead. Accuracy gets 50 percent, safety gets
          40 percent, and speed gets 10 percent, which feels right because a fast but
          dangerous insertion should lose to a slower safe one.
        </p>
      </section>

      <section className={styles.section}>
        <h2>Mistakes I fixed</h2>
        <ul className={styles.list}>
          {mistakes.map((mistake) => <li key={mistake}>{mistake}</li>)}
        </ul>
      </section>

      <section className={styles.section}>
        <h2>Takeaway</h2>
        <p>
          The reward function is the only way I tell the agent what good means, so when
          the agent does something dumb, I try not to blame the algorithm first. Most of
          the time the reward said that behavior was allowed, so I change one thing,
          train again, and check what actually changed.
        </p>
      </section>
    </main>
  );
}
