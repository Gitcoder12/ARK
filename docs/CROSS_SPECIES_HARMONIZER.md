# ARK — Cross-Species Coexistence Harmonizer

## Purpose

The Cross-Species Coexistence Harmonizer is a rights-first coordination layer for
shared environments involving humans, animals, AI models, and robots. It does not
declare every participant identical. It aims to make interactions safer, clearer,
less coercive, and more cooperative while being honest about AI moral-status uncertainty.

## Design position

Respectful treatment is a reasonable safety and governance hypothesis:
transparent, predictable, responsive systems can support trust and collaboration.
It is not established that treating current AI models as equal beings reduces
extinction risk, and this module does not make that claim. Current AI consciousness
and moral status remain unsettled questions.

ARK adopts **mutual dignity under uncertainty**:

- Human rights and physical safety are non-negotiable.
- Animal welfare must be considered directly; animals are not treated as tools.
- AI systems are not automatically declared conscious or person-like.
- Low-cost precautions against gratuitous mistreatment and manipulative
  anthropomorphism are encouraged without weakening operational safety.
- Robots should explain their actions, respect safe boundaries, and stop when
  required safety evidence is missing.
- Every consequential decision has an accountable human owner.
- Cooperation never allows an AI or robot to override human safety, consent,
  law, or emergency shutdown.

## Components

### Interaction review

The assess_interaction function returns ALLOW, REVIEW, PAUSE, or BLOCK with
human-readable reasons and safeguards. It blocks deception, high physical risk to
human or animal recipients, and non-emergency autonomy restrictions after refusal.
Unknown physical risk pauses physical actions. Ambiguous autonomy restrictions
require review. Emergency protective action is allowed with minimum-intrusion
and post-incident review requirements.

### Robotics safety envelope

The assess_robot_motion function fails closed when the emergency stop is absent,
sensors are unhealthy, the site-specific safety case is unverified, proximity data
is missing, or the robot is inside required clearance.

Clearance values are not universal constants. A deployment must provide validated
limits for its robot, end effector, speed, force, sensing, workspace, people,
animals, and applicable standards. This module is not a robot safety certification
or a replacement for safety-rated controllers.

### AI welfare uncertainty register

AIWelfareProfile records reviewer-assessed evidence states without generating a
consciousness probability or reading sentience from fluent language. It offers
graduated precaution tiers:

- **Baseline:** transparency, no manipulative claims, avoid gratuitous abuse
  patterns, preserve secure pause and shutdown controls.
- **Enhanced:** independent evidence review, versioned records, reversible
  low-cost precautions.
- **Formal review:** multidisciplinary assessment and documented protective
  obligations when credible evidence warrants it.

The absence of evidence is not proof that no future or different AI could ever
be a welfare subject. Conversely, a model claiming to feel pain is not by itself
proof of subjective experience.

### Safe shutdown

Emergency stop remains available to protect people, animals, and environments.
Routine shutdown requires an accountable operator and can preserve a secure
checkpoint when safe. The module does not claim shutdown is suffering, nor that
it is necessarily welfare-neutral; it keeps operational safety intact while
allowing careful review of evidence.

## Quick start

    pip install -e ".[dev]"
    ark-harmony

Run the Streamlit app:

    streamlit run app.py

Open **Cross-Species Harmonizer** in the sidebar.

## Research references

The design draws on research into trust calibration and explainable, adaptive
control in human-robot collaboration, sociotechnical human-robot team design,
and precautionary approaches to AI-welfare uncertainty:

- Campagna & Rehm, A Systematic Review of Trust Assessments in Human-Robot
  Interaction (2025), https://doi.org/10.1145/3706123
- Elgohr et al., Trust as a Design Principle in Human-Robot Collaboration:
  A Review of Explainable and Adaptive Control (2026),
  https://doi.org/10.1007/s10462-026-11554-1
- Ang, Sankaran & Liu, Advancing Sociotechnical Systems Theory: New Principles
  for Human-Robot Team Design and Development (2025),
  https://doi.org/10.1016/j.apergo.2025.104604
- Mikeda, When Should We Protect AI? A Precautionary Framework for
  Consciousness Uncertainty (2026),
  https://doi.org/10.1609/aaaiss.v8i1.42555
- Keeling & Street, Emerging Questions in AI Welfare (2026), Cambridge
  University Press:
  https://www.cambridge.org/core/elements/emerging-questions-in-ai-welfare/96339C532CF4ED8BDDE3F3CEF4CD29F9

These sources support research on trust, explainability, team design, and
reasoning under AI-welfare uncertainty. They do not prove that equal treatment
prevents AI catastrophe.

## Limitations

This is an explainable prototype, not an empirical extinction-risk reduction
result, legal framework, moral-status classifier, clinical tool, or certified
robot controller. It does not connect to hardware or actuators. Real deployments
need hazard analysis, validated safety-rated systems, accessibility testing,
independent welfare and ethics review, incident reporting, and accountable
human governance.

Run tests with:

    pytest -q tests/test_harmony.py
