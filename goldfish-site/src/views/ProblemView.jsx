import LogFile from '../components/log/LogFile.jsx';
import styles from './ProblemView.module.css';

const ECM_GIF = 'https://github.com/SamuelSchmidgall/SurgicalGym/raw/main/media/ecm_target_reach.gif';
const SVQLA = '/assets/svqla.png';
const SURROL_OVERVIEW = 'https://github.com/med-air/SurRoL/raw/SR-VPPV/README.assets/img/overview.png';

const LOGS = [
  {
    filename: 'surgical-robots-operate-blind.log',
    size: '5 lines',
    content: `Surgical robots are extraordinarily precise instruments. They assist in over one
million procedures every year across the world. They reduce hand tremors, enable
minimally invasive access to anatomical regions a human hand cannot reach, and improve
positional accuracy far beyond what unassisted surgery allows. And yet, despite all of
this capability, every one of these robots is operating without a predictive model of
what the tissue it is touching will do next.

The surgeon operating the system sees pre-operative imaging taken hours or days before
the procedure and real-time visual feedback from an endoscopic camera. The robot
executes the movements it is commanded to execute. But nothing in that entire loop ,
not the imaging, not the visual feed, not the robot's control system , contains a model
that predicts what will happen to the tissue when it is cut, sutured, cauterized, or
compressed. There is no layer that says: if you make this incision here, the inflammatory
response will begin at this location, the healing trajectory will follow this curve,
and the probability of a complication presenting within 72 hours is this number.

That predictive layer , a biological world model for surgical intervention , does not
exist anywhere in the surgical robotics stack today. Every robot in every operating room
in the world is making contact with human tissue without a forward model of what that
tissue will do. Goldfish builds that model.`,
    media: [
      {
        type: 'gif',
        src: ECM_GIF,
        caption: 'Endoscopic Camera Manipulator (ECM) learning positioning tasks in GPU-accelerated simulation (SurgicalGym, ICRA 2024). The robot learns where to look , but has no model of what the tissue will do once the instrument arrives. Goldfish adds the biological prediction layer that is missing from every surgical simulation environment in use today.',
      },
    ],
  },
  {
    filename: 'the-compliance-wall.log',
    size: '4 lines',
    content: `The path to deploying an autonomous surgical robot is blocked by a structural
contradiction that the industry has not yet resolved. You cannot train a surgical robot
on real patients until it has been demonstrated safe. You cannot demonstrate it safe
without training it in conditions that resemble real procedures closely enough to
generate meaningful evidence. These two requirements are in direct conflict, and the
field has been stuck inside that conflict for years.

The partial solution that exists today is simulation , robots train in physics simulators
that model the geometry of tissue and the kinematics of surgical instruments. This has
produced real progress. Systems like SurRoL have demonstrated zero-shot sim-to-real
transfer for certain task categories. STAR performed the first autonomous laparoscopic
surgery, trained entirely in simulation. But the fundamental limitation remains: the
simulations model physics, not biology. They tell the robot where the tissue is. They
do not tell it what the tissue will do.

The complete solution requires a simulation environment that is biologically faithful
enough that its outcomes predict real clinical outcomes with calibrated uncertainty. The
FDA has a formal framework for this , Computational Modeling and Simulation evidence ,
and it is actively expanding as the surgical robotics field matures. The EMA has the
Virtual Human Twin initiative moving in the same direction. The regulatory pathway
exists. What has not existed is a standardized, comprehensive simulation environment
built specifically to generate evidence that satisfies it. Goldfish is built to be
exactly that environment.`,
    media: null,
  },
  {
    filename: 'no-carla-for-surgery.log',
    size: '4 lines',
    content: `The autonomous vehicle industry faced a version of this same problem a decade ago.
Training autonomous driving systems required millions of miles of edge-case scenarios
that could not be safely collected by driving real cars on real roads. The field needed
a simulation environment that was realistic enough to train systems that would transfer
to the real world, and credible enough that regulators could evaluate performance
against standardized benchmarks. CARLA was built to fill that gap. It became the
default platform for the entire field , not because it was legislated into that position,
but because it was first, it was comprehensive, and by the time competitors appeared,
CARLA was already embedded in the regulatory conversation and in the development
pipelines of every major autonomous vehicle program.

Autonomous surgery is at the equivalent moment. The field is ready for simulation-based
training , the tools exist, the compute is available, the research community has
demonstrated that sim-to-real transfer is achievable for surgical tasks. What is missing
is the platform that ties it together into a standardized environment that the industry
converges on. Right now, every surgical robotics lab and company builds their own
limited simulator. Development is fragmented. Sims are shallow. The real-to-sim
transfer gap is a known, published, actively debated unsolved problem in every major
robotics conference. Goldfish is the platform that ends the fragmentation.`,
    media: [
      {
        type: 'img',
        src: SURROL_OVERVIEW,
        caption: 'SurRoL (Science Robotics 2025, CUHK Med-AIR) , an open-source reinforcement learning platform for surgical robot training that has demonstrated zero-shot sim-to-real transfer for autonomous laparoscopic tasks. SurRoL proves that simulation-trained surgical robots can transfer to real hardware. Goldfish provides the biological world model layer that is missing from that transfer: not just where the instrument ends up, but what the tissue does afterward.',
      },
    ],
  },
  {
    filename: 'why-existing-medical-ai-is-not-enough.log',
    size: '3 lines',
    content: `The past five years have produced remarkable progress in medical AI , foundation
models for pathology, vision-language systems that can answer questions about surgical
scenes, multimodal AI that integrates imaging, genomics, and clinical records to support
diagnosis. This progress is real and important. But it addresses a fundamentally
different problem from the one Goldfish solves.

Diagnostic AI tells you what is there. It observes, classifies, and predicts from
existing data. Systems like Surgical-VQLA can localize answers to questions about what
is visible in endoscopic video with impressive accuracy. These systems are valuable. But
they all stop at the boundary of observation. They see the tissue. They do not simulate
what happens to the tissue when you intervene.

Goldfish operates on the other side of that boundary. It is not a diagnostic tool or
a perception system. It is a forward model of biological consequence , an environment
where you specify an intervention and receive a simulation of what the body does in
response, scored against biological harm metrics, across the full temporal arc from
the moment of incision to the trajectory of recovery. No existing medical AI product
does this. This is the gap Goldfish fills.`,
    media: [
      {
        type: 'img',
        src: SVQLA,
        caption: 'Surgical-VQLA (ICRA 2023, IEEE) , a transformer architecture for visual question localized-answering in robotic surgery. The system answers questions about what is visible in the surgical scene and localizes the relevant anatomical area. This represents the state of the art in surgical scene understanding. Goldfish operates at the next level: simulating what happens inside that scene when an intervention is executed, and predicting the biological consequences that follow.',
      },
    ],
  },
  {
    filename: 'what-is-missing.log',
    size: '4 items',
    content: `The gap the industry has not filled is a platform that does all four of the
following things together, as a unified system:

Simulate the biology, not just the geometry. A surgical procedure needs to be modeled
with physically accurate tissue mechanics and biologically faithful tissue response.
That means the downstream biological events: the onset of bleeding, the inflammatory
cascade, the cellular response to trauma, and the healing trajectory that follows. No
current surgical simulation environment models all of these. Most model none of them.

Provide a standard agent interface. Any surgical robot control system should be able
to execute that procedure inside the simulation, receive scored feedback on the
biological quality of each intervention, and iterate on its policy across thousands of
episodes. The interface needs to be compatible with standard robot learning frameworks
so that any team can plug their system in without building a custom integration layer.

Score outcomes clinically. Every simulation run should be scored on biological harm,
procedure efficacy, and expected recovery trajectory using metrics that correspond to
what a clinical team and a regulatory reviewer would actually care about. Positional
accuracy alone is not sufficient. A robot that places a needle with sub-millimeter
precision but causes unnecessary tissue trauma is not a robot that should proceed to a
human trial.

Produce regulatory-grade evidence. Simulation logs need to satisfy the FDA's
Computational Modeling and Simulation evidence framework. That means not just generating
data, but generating the right data, documented in the right way, with the right
statistical characterization of uncertainty, to be usable as evidence in a device
approval submission.

That combination , biological simulation, agent training, clinical scoring, and
regulatory evidence output , does not exist as a product today. Goldfish is built to
be exactly that.`,
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

export default function ProblemView() {
  return (
    <div className={styles.page}>
      <h1 className={styles.title}>the problem</h1>
      <hr />
      <div className={styles.tree}>
        <div className={styles.treeRoot}>goldfish/problem/</div>
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
    </div>
  );
}
