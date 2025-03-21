import { NavLink } from 'react-router-dom';
import LogFile from '../components/log/LogFile.jsx';
import styles from './OverviewView.module.css';

const SURGICALGYM_MAIN = 'https://github.com/SamuelSchmidgall/SurgicalGym/raw/main/media/mainfigure.jpg';
const PSM_GIF = 'https://github.com/SamuelSchmidgall/SurgicalGym/raw/main/media/psm_target_reach.gif';

const LOGS = [
  {
    filename: 'what-is-goldfish.log',
    size: '4 lines',
    content: `Goldfish is the simulation environment where surgical robots train before they are
allowed near a real patient.

A surgical robotics company plugs their robot's control system into Goldfish, defines a
procedure , say, a laparoscopic incision or a needle insertion into soft tissue , and
Goldfish simulates the tissue mechanics, the physics, and the biological response in full
fidelity. The robot trains inside that environment millions of times. It fails, it
adjusts, it iterates. Its outcomes are scored against biological harm metrics and efficacy
targets. Nothing touches a real human until the simulation says the intervention is ready.

This is not a visualization tool and it is not a planning assistant. Goldfish is a full
training environment , the place where surgical autonomy is developed, validated, and
prepared for clinical deployment.`,
    media: null,
  },
  {
    filename: 'the-picks-and-shovels-play.log',
    size: '5 lines',
    content: `Goldfish is not a surgical robot. It is the environment every surgical robot company
needs in order to exist.

During the gold rush, the people who sold shovels made more reliable money than the
miners. The miners competed against each other, failed, and left. The shovel sellers
served all of them. This is the same logic. Every surgical robotics company ,
Intuitive Surgical, CMR Surgical, Moon Surgical, Activ Surgical, and every lab building
the next generation of autonomous surgical systems , has the same unsolved problem: they
cannot train their robots on real patients, and they have no simulation environment
faithful enough to replace them. Goldfish solves that problem once, and sells the
solution to all of them.

The closest analogy in another field is CARLA , the open simulation environment that
made autonomous vehicle development possible. Before CARLA, every company built their
own limited simulator. Development was fragmented, sims were shallow, and no regulatory
body had a standard environment to evaluate against. CARLA became the default by being
first, being comprehensive, and becoming embedded in the regulatory conversation early.
Goldfish does the same thing for surgical autonomy.`,
    media: [
      {
        type: 'img',
        src: SURGICALGYM_MAIN,
        caption: 'SurgicalGym (ICRA 2024) , a GPU-accelerated surgical robot simulation platform capable of running 7,000x faster than real-time. Goldfish builds on top of environments like this, adding the biological world model layer that makes simulation outcomes more than physically approximate - the outputs predict real clinical consequences.',
      },
    ],
  },
  {
    filename: 'business-model.log',
    size: '3 tiers',
    content: `The platform naturally supports three revenue tiers from the same underlying product,
each serving a different segment of the surgical robotics market.

Tier one is API access for surgical robotics startups and academic research labs. These
teams need a simulation environment but do not have the resources to build one. They call
Goldfish the same way they call any cloud API , define a procedure, submit a robot
control policy, receive simulation results and biological cost scores. Pricing follows a
per-simulation-run or monthly subscription model. This tier generates early revenue,
produces diverse training data across many procedure types, and builds the case study
library that enterprise customers require before signing contracts.

Tier two is enterprise licensing for the large surgical robotics companies , Intuitive
Surgical, Medtronic, Johnson & Johnson MedTech , who need the simulation environment
deployed on their own infrastructure with custom tissue models built specifically for
their procedures and their robot hardware. These are annual contracts in the range of
one to five million dollars. The switching costs once a company has integrated Goldfish
into their robot development workflow are enormous , their entire training pipeline, their
validation data, and their regulatory submission evidence all depend on the environment.

Tier three is the highest-value segment and the most defensible long-term position:
regulatory evidence packages. The FDA and EMA have established frameworks for accepting
computational modeling and simulation evidence in medical device approval submissions.
Goldfish generates simulation logs in formats structured to meet those requirements.
Once a device approval is built on Goldfish simulation evidence, the company that used
Goldfish to get approved becomes a reference. Every subsequent company wanting approval
in the same category wants the simulation environment that has already been validated
by the regulatory body. This is a compounding moat. The more approvals Goldfish evidence
appears in, the more indispensable the platform becomes.`,
    media: null,
  },
  {
    filename: 'three-moats.log',
    size: '3 items',
    content: `Software simulation companies are often dismissed as easily copied. Goldfish has
three structural moats that compound with time and make the platform progressively
harder to displace.

The data moat works as follows: every simulation run executed inside Goldfish produces
outcome data that is fed back into the biological world model, making its tissue response
predictions more accurate. A competitor who builds a similar platform six months or two
years later starts with a model trained on zero procedures. Goldfish starts with a model
trained on every procedure that has ever run on the platform. The gap widens with every
simulation session. By the time a competitor is usable, Goldfish's model is an order of
magnitude more accurate on the procedures that matter commercially.

The regulatory moat is even more powerful. Once the FDA accepts a Goldfish simulation
log as supporting evidence in a single approved device submission, that creates a
precedent. The next company to apply for approval in the same procedure category looks
at the precedent, sees that Goldfish evidence was accepted, and wants to use the same
environment rather than risk having their own novel simulation methodology questioned
during review. The moat does not require exclusivity agreements or patents , it requires
simply being first in the regulatory conversation, which is a function of speed to market
rather than capital.

The integration moat compounds on top of both. Once a surgical robotics company has
built their training pipeline, their validation protocols, and their regulatory evidence
strategy around Goldfish, switching to a different platform means rebuilding all three
from scratch. The transition cost is measured not just in software engineering time but
in months of revalidation work and potential delays to their device approval timeline.
No rational engineering organization chooses to absorb that cost voluntarily.`,
    media: [
      {
        type: 'gif',
        src: PSM_GIF,
        caption: 'da Vinci Patient Side Manipulator (PSM) learning to reach targets in GPU-accelerated simulation (SurgicalGym, ICRA 2024). The robot improves through reinforcement learning without any human patient involvement. Goldfish extends this training loop with a biological cost module that scores tissue trauma, inflammatory response, and recovery trajectory - giving the training signal clinical weight rather than just mechanical accuracy.',
      },
    ],
  },
  {
    filename: 'v1-what-we-build-first.log',
    size: '3 lines',
    content: `The first version of Goldfish does not attempt to simulate every surgical procedure
on every robot platform. It solves one problem completely and demonstrates that the
platform concept works.

The target for version one is needle insertion into soft tissue. This is the standard
benchmark task in surgical robotics research , simple enough to be tractable in six
months, clinically meaningful enough to be taken seriously by a research lab or a
robotics startup, and representative enough to demonstrate all three core components
of the Goldfish platform: the tissue simulation, the robot agent training loop, and
the biological cost module.

The goal of the v1 demo is to show a robot agent improving its needle insertion
accuracy over ten thousand simulation episodes, with biological outcome scores
(tissue trauma, depth accuracy, vascular proximity) tracked across the training run
and logged in a structured format. That demonstration answers the only question that
matters to a first customer: does the simulation produce outcomes that are
directionally faithful to what happens in a real procedure? It does not need to be
perfect. It needs to be measurably improving and scientifically defensible. That is
enough to begin a conversation with a surgical robotics lab, secure a pilot integration,
and generate the first real case study.`,
    media: null,
  },
];

function ProseLog({ children }) {
  return (
    <div className={styles.body}>
      {children.trim().split(/\n\s*\n/).map((paragraph) => (
        <p key={paragraph}>{paragraph.replace(/\s*\n\s*/g, ' ')}</p>
      ))}
    </div>
  );
}

export default function OverviewView() {
  return (
    <div className={styles.page}>
      <div className={styles.pageHeader}>
        <h1 className={styles.title}>goldfish</h1>
        <p className={styles.sub}>the simulation environment for surgical robots</p>
      </div>
      <hr />
      <div className={styles.tree}>
        <div className={styles.treeRoot}>goldfish/logs/</div>
        {LOGS.map((log, i) => (
          <LogFile key={log.filename} filename={log.filename} size={log.size} defaultOpen={i === 0}>
            <ProseLog>{log.content}</ProseLog>
            {log.media && (
              <div className={styles.mediaGrid}>
                {log.media.map((m, j) => (
                  <figure key={j} className={styles.figure}>
                    <img src={m.src} alt={m.caption} className={styles.media} loading="lazy" />
                    <figcaption className={styles.caption}>{m.caption}</figcaption>
                  </figure>
                ))}
              </div>
            )}
          </LogFile>
        ))}
      </div>
      <hr />
      <div className={styles.nav}>
        <NavLink to="/problem" className={styles.nextLink}>the problem in detail</NavLink>
        <NavLink to="/system"  className={styles.nextLink}>how the system works</NavLink>
        <NavLink to="/docs" className={styles.joinLink}>read the docs</NavLink>
      </div>
    </div>
  );
}
