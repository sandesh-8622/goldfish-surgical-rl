import LogFile from '../components/log/LogFile.jsx';
import styles from './SystemView.module.css';

const STAR_GIF = 'https://github.com/SamuelSchmidgall/SurgicalGym/raw/main/media/STAR_track.gif';

const ARCH = `platform architecture
---------------------

  surgical robot SDK / control API
  (any robot platform, any procedure type)
       |
       v
  +------------------------------------------+
  |        goldfish simulation layer          |
  |                                           |
  |  physics engine     MuJoCo / PyBullet     |
  |  tissue mechanics   SOFA framework        |
  |  cell response      PhysiCell             |
  |  vascular model     SimVascular           |
  |                                           |
  |  biological world model  (JEPA-based)    |
  |  predicts tissue response to             |
  |  intervention across all timescales      |
  +------------------------------------------+
       |                      |
       v                      v
  +-------------+    +--------------------+
  |  robot      |    |  biological cost   |
  |  agent      |    |  module            |
  |  (RL / IL)  |    |                    |
  |             |    |  tissue trauma     |
  |             |    |  inflammation      |
  |             |    |  recovery score    |
  |             |    |  systemic risk     |
  +-------------+    +--------------------+
       |
       v
  structured simulation logs
  FDA-compatible evidence output
  policy export for real robot deployment`;

const LOGS = [
  {
    filename: 'three-components.log',
    size: '3 items',
    content: `Goldfish is built from three interlocking components. Each one is necessary.
Together they form the only simulation platform that produces biologically meaningful
evidence about surgical robot behavior.

The first component is the biological world model , a learned simulation of human
tissue that predicts how the body responds to surgical intervention across multiple
timescales and biological scales. This is the core of what makes Goldfish different
from every existing surgical simulator. Current simulators model the geometry and
mechanics of tissue deformation. They tell the robot where the tissue is and how it
moves when pressed. The Goldfish world model goes further: it predicts what the tissue
does biologically in response to intervention.
Bleeding onset, inflammatory cascade, cellular response to trauma, healing trajectory,
vascular adaptation, and systemic effects all propagate through the model from the
moment of instrument contact forward in time.

The second component is the robot agent environment , an OpenAI Gym-compatible
interface that allows any surgical robot control system to execute procedures inside
the simulation, receive feedback on every step, and iterate on its policy across
as many episodes as the training run requires. The interface is designed to be
compatible with the frameworks that surgical robotics researchers already use , SurRoL,
SurgicalGym, custom environments built on MuJoCo or PyBullet , so that integration
requires configuration rather than a complete rewrite of a team's existing pipeline.

The third component is the biological cost module , the scoring system that defines
what a good outcome and a bad outcome look like inside the simulation. This is what
allows the training signal to carry clinical weight rather than just mechanical
accuracy. A robot that places a needle with perfect positional precision but causes
unnecessary tissue trauma is not a robot that should proceed to a human trial. The
cost module catches that. It scores every simulation run against tissue trauma
thresholds, inflammatory response markers, vascular proximity risk, and recovery
trajectory projections, and it uses those scores to guide the agent away from
technically precise but biologically harmful intervention strategies.`,
    media: null,
  },
  {
    filename: 'world-model.log',
    size: '8 lines',
    content: `The world model is the intellectual core of Goldfish, and its architecture is
grounded in the most significant recent advance in autonomous agent research: Yann
LeCun's Joint Embedding Predictive Architecture, published in 2022 as the theoretical
foundation for a new generation of autonomous intelligence systems.

JEPA makes a critical departure from generative models that attempt to reconstruct
every detail of an environment. Rather than learning to predict pixels, JEPA learns
to predict representations , the abstract structure of how a system changes when an
action is applied to it. Details that are fundamentally unpredictable are not modeled;
the architecture focuses its capacity on what is learnable. In the context of surgical
simulation, this means the world model does not attempt to reconstruct the appearance
of tissue at every timestep. It learns to predict how the state of the tissue ,
represented at the right level of biological abstraction , changes when an instrument
makes contact.

The hierarchy of the model mirrors the hierarchy of biological consequence:

  Immediate timescale   ,   tissue deformation, bleeding onset, instrument force
  Short timescale       ,   inflammatory response initiation, suture tension, local edema
  Medium timescale      ,   healing trajectory, complication probability, scar formation
  Long timescale        ,   recovery outcome, functional restoration, systemic adaptation

This chain of prediction , from the moment of incision through to the patient's
recovery trajectory , does not exist in any surgical simulation environment today.
Building it is the central research and engineering challenge that Goldfish is designed
to solve. The architecture that makes it tractable is JEPA, applied to biological
state rather than visual scenes or physical environments.`,
    media: null,
  },
  {
    filename: 'robot-agent.log',
    size: '2 modes',
    content: `The robot agent in Goldfish operates in two distinct modes, each serving a
different phase of the training and deployment pipeline.

In reactive mode, the agent executes learned policies from a library built through
prior simulation training runs. This mode is computationally efficient , it does not
require rolling out the full world model at every step , and is well suited to
standard procedures where the intervention strategy is well-established and the
relevant policy has been validated through extensive prior simulation. Reactive mode
is what a deployed surgical robot uses during a real procedure: it draws on a library
of validated policies rather than computing optimal actions from scratch in real time.

In deliberate mode, the agent uses the world model as a forward simulator before
committing to any action. It considers a set of candidate intervention sequences,
rolls each one forward through the world model to predict the biological consequences,
scores those consequences against the cost module, and selects the sequence that
minimizes predicted harm while maximizing predicted procedure efficacy. This is
computationally expensive , it is model predictive control at the biological scale ,
but it is what produces the validated, high-quality policies that populate the policy
library for reactive mode.

The training loop works as follows: the agent runs thousands of deliberate mode
episodes, building up a library of validated policies for progressively more complex
procedure variants. That library is what gets exported when the simulation run is
complete , a set of policies accompanied by the full statistical record of every
biological outcome score across every episode. That record is the foundation of the
regulatory evidence package.`,
    media: [
      {
        type: 'gif',
        src: STAR_GIF,
        caption: 'STAR (Smart Tissue Autonomous Robot) performing autonomous laparoscopic tracking in simulation , the first robot system to demonstrate fully autonomous laparoscopic surgery in a live animal, trained entirely in simulation and validated before any clinical contact. Goldfish is designed to be the platform where the next generation of STAR-class autonomous surgical systems develops, validates, and prepares its regulatory evidence before any human trial begins.',
      },
    ],
  },
  {
    filename: 'cost-module.log',
    size: '2 parts',
    content: `The biological cost module is what grounds Goldfish's training signal in
clinical reality. Without it, a surgical robot trained in Goldfish would optimize
for the same metrics that every existing surgical simulator optimizes for , positional
accuracy, path efficiency, task completion time. With it, the robot learns to optimize
for what actually matters in a clinical context: biological outcomes.

The cost module has two parts that serve different purposes.

The intrinsic cost layer consists of fixed, non-trainable thresholds derived from
established clinical standards and biological safety limits. Tissue trauma indicators,
bleeding onset thresholds, nerve proximity signals, inflammatory response markers, and
systemic destabilization signals are all computed at every step of the simulation and
checked against these fixed limits. They are non-trainable by design , an agent should
not be able to learn a policy that finds a technical workaround to avoid triggering
a tissue trauma threshold while still causing tissue trauma. The intrinsic costs are
the hard floor below which no procedure is acceptable regardless of how well it performs
on other metrics.

The trainable critic is a learned model that predicts future biological cost from the
current state of the simulation. It is calibrated against historical surgical case
outcome data , cases where the biological cost scores at intermediate points in the
procedure predicted the eventual patient outcome. The critic is updated as new
procedure data is integrated into the platform. Over time, its predictions become more
accurate, and the agent's training signal becomes more precisely aligned with the
outcomes that real clinical teams care about. An intervention strategy that looks
efficient in a physics-only simulator but is predicted by the trained critic to carry
elevated complication risk is penalized during training and does not make it into the
validated policy library.`,
    media: null,
  },
  {
    filename: 'open-source-stack.log',
    size: '6 tools',
    content: `Goldfish does not rebuild what the open-source research community
has already built and validated. Each major component of the simulation stack is
assembled from existing tools, each of which handles one biological or physical layer
with the depth and rigor that a single new project could not achieve. The contribution
of Goldfish is the integration architecture and the biological world model that ties
these tools into a coherent, jointly-trained system.

MuJoCo serves as the primary physics engine for the robot agent environment, providing
the contact physics and rigid body dynamics that govern instrument-tissue interaction
at the mechanical level. PyBullet provides an alternative physics backend compatible
with SurRoL-based surgical environments for teams whose existing pipelines depend on it.

SOFA handles soft tissue mechanics , the deformation, stretching, cutting, and suturing
behavior of biological soft tissue under surgical instrument contact. It is the most
mature open-source framework for surgical tissue simulation and is used by surgical
robotics research groups worldwide.

PhysiCell handles cell-level biological simulation , the cellular response to trauma,
the dynamics of cell populations under stress, and the local biological environment
that determines how healing proceeds after an intervention.

SimVascular provides the vascular flow and blood simulation layer , modeling blood
flow dynamics, bleeding onset under vascular damage, and the systemic effects of
vascular events during a surgical procedure.

I-JEPA, Meta's implementation of the Joint Embedding Predictive Architecture, provides
the core architecture of the biological world model , the learned representation system
that ties all of these simulation layers together into a unified predictive model of
biological state across scales and timescales.`,
    media: null,
  },
  {
    filename: 'architecture.txt',
    size: 'diagram',
    content: ARCH,
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

export default function SystemView() {
  return (
    <div className={styles.page}>
      <h1 className={styles.title}>the system</h1>
      <hr />
      <div className={styles.tree}>
        <div className={styles.treeRoot}>goldfish/system/</div>
        {LOGS.map((log, i) => (
          <LogFile key={log.filename} filename={log.filename} size={log.size} defaultOpen={i === 0}>
            {log.filename === 'architecture.txt' ? (
              <pre className={styles.body}>{log.content}</pre>
            ) : (
              <ProseLog>{log.content}</ProseLog>
            )}
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
    </div>
  );
}
