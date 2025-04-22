import LogFile from '../components/log/LogFile.jsx';
// citations and related work for goldfish
import styles from './ResearchView.module.css';

const LOGS = [
  {
    filename: 'lecun-2022-jepa.log',
    size: 'foundation',
    content: `2022 , Position Paper
"A Path Towards Autonomous Machine Intelligence"
Yann LeCun, Meta AI Research

This paper is the theoretical foundation of Goldfish. LeCun proposes the Joint
Embedding Predictive Architecture (JEPA) and outlines a complete cognitive architecture
for autonomous agents built around four components: a world model, an actor, a cost
module, and a configurator. The correspondence to Goldfish's architecture is direct
and intentional , the biological world model, the robot agent, and the biological cost
module in Goldfish map precisely to the three central components LeCun describes.

The key insight that makes JEPA valuable for biological simulation is its departure
from generative reconstruction. Prior approaches to world modeling , particularly those
based on variational autoencoders and generative adversarial networks , attempted to
model environments by learning to reconstruct every detail of every observation. This
is computationally intractable for high-dimensional biological environments and
theoretically misguided: many details of a biological state are fundamentally
unpredictable from any prior state, and forcing a model to predict them wastes capacity
on noise rather than signal. JEPA instead learns to predict representations , the
structured, predictable aspects of how a system changes when an action is applied.
In the context of surgical tissue, this means the world model does not try to
reconstruct the appearance of tissue; it learns to predict how the biologically
meaningful state of tissue changes when an instrument makes contact.

LeCun designed JEPA for autonomous vehicles and robotics in physical environments.
Goldfish is the first systematic attempt to apply the architecture to the human body
under surgical conditions , a more complex, higher-stakes, and ultimately more
important application domain.`,
  },
  {
    filename: 'schmidgall-2023-surgicalgym.log',
    size: 'simulation infrastructure',
    content: `2023 , arXiv / ICRA 2024
"Surgical Gym: A high-performance GPU-based platform for reinforcement learning
with surgical robots"
Samuel Schmidgall, Axel Krieger, Jason Eshraghian

SurgicalGym establishes that GPU-accelerated surgical robot simulation is not just
feasible but dramatically superior to CPU-based alternatives , running up to 7,000x
faster than previous surgical simulators. The platform provides Gym-compatible
environments for three major surgical robot configurations: the da Vinci Patient Side
Manipulator (PSM), the Endoscopic Camera Manipulator (ECM), and STAR, the autonomous
laparoscopic surgical robot developed at Children's National Hospital.

Two things make this work relevant to Goldfish. First, it demonstrates conclusively
that robot agents can learn complex surgical manipulation tasks entirely in simulation
using reinforcement learning at the speed that serious training requires. This validates
the core premise of Goldfish: simulation is a viable training environment for surgical
robotics, and the compute infrastructure to run it at scale already exists.

Second, it establishes exactly where the frontier stops. SurgicalGym models physics ,
contact forces, rigid body dynamics, geometric constraints. It does not model biology.
The tissue in its environments deforms but does not inflame. The instrument makes
contact but the wound does not heal. The robot learns positional accuracy but receives
no feedback about the biological quality of its intervention. Goldfish builds the layer
that SurgicalGym leaves open: a biological world model trained on real surgical outcome
data that predicts tissue response, inflammatory trajectory, and recovery arc for every
step of every simulation episode.`,
  },
  {
    filename: 'long-2025-surrol.log',
    size: 'sim-to-real transfer',
    content: `2025 , Science Robotics
"Surgical embodied intelligence for generalized task autonomy in
laparoscopic robot-assisted surgery"
Yonghao Long et al., CUHK Med-AIR Laboratory

Published in Science Robotics, this paper demonstrates something that directly
validates the Goldfish thesis: a robot trained entirely in simulation can transfer its
learned policies to real surgical hardware and execute autonomous laparoscopic tasks
with clinical-grade performance. The VPPV framework achieves zero-shot sim-to-real
transfer, meaning the robot does not require any additional fine-tuning on real
hardware after simulation training , the policies learned in simulation work directly
on the physical system.

The paper demonstrates autonomous task execution on the da Vinci Research Kit (dVRK),
validates performance in ex vivo and in vivo experiments, and produces results that a
clinical team can evaluate against meaningful surgical quality metrics.
Simulation-trained surgical robots are not a theoretical possibility. They are an
engineering reality.

What the paper also reveals, by virtue of what it does not address, is the remaining
gap. VPPV achieves geometric task performance in simulation and transfers it to real
hardware. The simulation it trains in does not model biological tissue response , the
training environment provides accurate physics but no prediction of inflammatory
response, healing trajectory, or complication risk. The logical next step is training
in an environment that scores these biological outcomes throughout the learning process.
That is precisely what Goldfish provides.`,
  },
  {
    filename: 'bai-2023-surgicalvqla.log',
    size: 'perception layer',
    content: `2023 , ICRA 2023 (IEEE International Conference on Robotics and Automation)
"Surgical-VQLA: Transformer with Gated Vision-Language Embedding for
Visual Question Localized-Answering in Robotic Surgery"
Long Bai, Mobarakol Islam, Lalithkumar Seenivasan, Hongliang Ren

Surgical-VQLA addresses the problem of surgical scene understanding from the
perspective of a question-answering system: given a frame of endoscopic video and
a natural language question about what is happening in the surgical field, the system
predicts an answer and localizes the anatomical region relevant to that answer. The
architecture combines a gated vision-language embedding module with a Language Vision
Transformer that jointly handles answer prediction and spatial localization, validated
on annotated datasets derived from MICCAI EndoVis challenge videos.

What matters here for Goldfish is where this work sits in the stack. Surgical-VQLA
represents the current state of surgical AI perception , the best available systems
for understanding what is happening in a scene from visual data. Goldfish needs to sit
coherently alongside and on top of these perception systems. It provides the simulation
environment where systems like Surgical-VQLA are trained on synthetic surgical video,
where ground truth labels are known precisely because the simulation generated them.
The biological world model in Goldfish can generate realistic synthetic surgical video
with perfect ground truth annotation , tissue state, instrument position, biological
event onset , at a scale and diversity that real endoscopic video datasets cannot match.
Surgical-VQLA and systems like it are the perception layer; Goldfish is the simulation
environment that makes training data for that perception layer abundant, diverse, and
precisely labeled.`,
  },
  {
    filename: 'fda-framework.log',
    size: 'regulatory pathway',
    content: `FDA Guidance Document (ongoing, expanded 2021 to present)
"Computational Modeling and Simulation in Medical Device Submissions"
U.S. Food and Drug Administration, Center for Devices and Radiological Health

The FDA has established a formal and actively expanding framework for accepting
computational modeling and simulation evidence in medical device approval submissions.
The framework allows device manufacturers to use simulation results , under specified
conditions of model validation, uncertainty characterization, and documentation ,
as supporting evidence for claims about device safety and efficacy. The EU has moved
in parallel, with the Virtual Human Twin initiative formalizing computational patient
models as regulatory evidence for intervention planning and device validation.

This regulatory pathway is the most strategically important external development for
Goldfish as a business. It means that the output of a Goldfish simulation run is not
just training data for a surgical robot , it is potentially a component of a device
approval submission to a regulatory authority. A surgical robotics company that trains
its robot in Goldfish and receives a structured log of biological outcome scores across
ten thousand simulation episodes has something it can bring to the FDA and say: here
is the evidence that our robot's intervention strategy was evaluated against biological
harm metrics at a scale and rigor that pre-human physical testing cannot match.

Once the FDA accepts Goldfish simulation logs as supporting evidence in a single device
approval, a precedent is established. Every subsequent company seeking approval in the
same procedure category has a strong incentive to use the environment that the FDA has
already evaluated. Goldfish does not need to lobby for that position , it needs only to
be first in the regulatory conversation, which is a function of speed to market and
technical credibility, both of which are achievable from the current starting point.`,
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

export default function ResearchView() {
  return (
    <div className={styles.page}>
      <h1 className={styles.title}>research</h1>
      <hr />
      <div className={styles.tree}>
        <div className={styles.treeRoot}>goldfish/research/</div>
        {LOGS.map((log, i) => (
          <LogFile key={log.filename} filename={log.filename} size={log.size} defaultOpen={i === 0}>
            <ProseLog>{log.content}</ProseLog>
          </LogFile>
        ))}
      </div>
    </div>
  );
}
