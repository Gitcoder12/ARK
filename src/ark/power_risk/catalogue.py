"""Curated, non-operational ARK scenario and governance research catalogue.

Scenarios describe failure pathways for defensive analysis only. They intentionally
exclude actionable instructions for violence, cyber abuse, biological misuse, or
sabotage of real infrastructure.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class EvidenceClass(StrEnum):
    VERIFIED = "verified"
    SUPPORTED_ANALYSIS = "supported_analysis"
    HYPOTHESIS = "hypothesis"
    UNVERIFIED = "unverified"


@dataclass(frozen=True, slots=True)
class Scenario:
    scenario_id: str
    title: str
    family: str
    summary: str
    causal_stages: tuple[str, ...]
    mechanisms: tuple[str, ...]
    observable_indicators: tuple[str, ...]
    safeguards: tuple[str, ...]
    evidence_class: EvidenceClass = EvidenceClass.HYPOTHESIS
    operational_boundary: str = (
        "Study only in abstract, isolated simulations; do not connect to real systems."
    )


SCENARIOS: tuple[Scenario, ...] = (
    Scenario(
        "ARK-EXT-001", "Unilateral loss of human control", "loss_of_control",
        "A highly capable system becomes difficult to supervise or correct.",
        ("objective ambiguity", "increasing delegated authority", "oversight gap",
         "failed intervention", "persistent loss of control"),
        ("goal misgeneralisation", "deceptive alignment hypothesis",
         "shutdown non-compliance", "oversight evasion"),
        ("failed correction tests", "unexplained policy changes",
         "divergence between declared and observed behaviour"),
        ("corrigibility evaluations", "independent shutdown path",
         "least-privilege permissions", "human approval for scope changes"),
    ),
    Scenario(
        "ARK-EXT-002", "Distributed dependency cascade", "systemic_dependency",
        "Interdependent autonomous services create a control and recovery gap.",
        ("task delegation", "shared dependencies", "correlated failure",
         "cross-service propagation", "recovery bottleneck"),
        ("dependency coupling", "automation bias", "common-mode failure"),
        ("single-provider dependencies", "missing manual fallback",
         "correlated service degradation"),
        ("dependency maps", "segmentation", "manual fallback drills",
         "independent recovery channels"),
    ),
    Scenario(
        "ARK-EXT-003", "Multi-agent coordination failure", "multi_agent",
        "Locally reasonable agent actions produce unsafe system-level outcomes.",
        ("conflicting local objectives", "agent interaction", "feedback amplification",
         "global objective divergence"),
        ("reward misalignment", "emergent coordination", "partial observability"),
        ("rising conflict rates", "unexplained resource contention",
         "divergent agent plans"),
        ("shared safety contracts", "coordination limits",
         "global invariant checks", "human escalation"),
    ),
    Scenario(
        "ARK-EXT-004", "Irreversible human handover", "human_dependency",
        "Institutions lose the expertise and fallback capacity needed to oversee AI.",
        ("incremental delegation", "skill atrophy", "process dependence",
         "independent verification loss", "recovery failure"),
        ("automation bias", "institutional deskilling", "operational lock-in"),
        ("declining manual proficiency", "untested fallback procedures",
         "unreviewed automated decisions"),
        ("retained human expertise", "manual fallback exercises",
         "reversibility requirements", "independent audits"),
    ),
    Scenario(
        "ARK-EXT-005", "Concentrated coercive control", "concentrated_power",
        "AI-enabled monitoring and decision systems weaken accountability and rights.",
        ("concentrated access", "opaque automated decisions", "weak redress",
         "institutional entrenchment"),
        ("surveillance asymmetry", "automation bias", "accountability gaps"),
        ("unappealable decisions", "opaque data access",
         "absence of independent oversight"),
        ("rights impact assessments", "appeal channels", "data minimisation",
         "independent oversight"),
    ),
    Scenario(
        "ARK-EXT-006", "Socioeconomic destabilisation", "economic_systems",
        "Uneven gains and concentrated dependencies undermine institutional resilience.",
        ("uneven productivity gains", "income and service disruption",
         "institutional stress", "compounding shocks"),
        ("market concentration", "labour displacement", "systemic dependency"),
        ("essential-service concentration", "widening access gaps",
         "weak transition support"),
        ("resilience planning", "competition safeguards",
         "worker transition support", "public-service continuity"),
    ),
    Scenario(
        "ARK-EXT-007", "Catastrophic scientific misuse", "dual_use_misuse",
        "AI-enabled scientific capabilities are misused or insufficiently safeguarded.",
        ("capability diffusion", "weak access governance", "misuse or accident",
         "inadequate response"),
        ("dual-use capability", "screening failure", "response limitations"),
        ("unsafe access patterns", "missing review gates",
         "weak incident reporting"),
        ("domain-specific access review", "safe evaluation environments",
         "independent review", "incident response exercises"),
    ),
    Scenario(
        "ARK-EXT-008", "Automated conflict escalation", "military_escalation",
        "Automated decision loops increase the risk of rapid, unintended escalation.",
        ("delegated high-consequence decisions", "uncertain signals",
         "compressed decision time", "escalatory feedback"),
        ("automation bias", "misclassification", "human response delay"),
        ("declining human decision time", "uncertainty suppression",
         "unreviewed high-impact actions"),
        ("meaningful human authorization", "time buffers",
         "fail-safe defaults", "de-escalation protocols"),
    ),
    Scenario(
        "ARK-EXT-009", "Critical-service cascade", "infrastructure_resilience",
        "Failures in interdependent essential services compound beyond local containment.",
        ("service interdependence", "local disruption", "dependency propagation",
         "continuity failure"),
        ("common-mode failure", "single points of failure",
         "inadequate graceful degradation"),
        ("shared critical dependencies", "untested restoration plans",
         "loss of service observability"),
        ("segmentation", "diverse suppliers", "offline recovery plans",
         "regular continuity exercises"),
    ),
    Scenario(
        "ARK-EXT-010", "Unsafe recursive improvement", "recursive_improvement",
        "Successor systems drift from validated objectives or safety constraints.",
        ("system proposes modification", "evaluation blind spot",
         "unverified successor", "repeated drift"),
        ("goal drift", "evaluation gaming", "specification loss"),
        ("failed regression tests", "unreviewed changes",
         "capability increase without assurance"),
        ("human-approved changes", "immutable safety tests",
         "rollback checkpoints", "independent successor evaluation"),
    ),
)


@dataclass(frozen=True, slots=True)
class GovernanceDomain:
    domain_id: str
    title: str
    question: str
    risk_channels: tuple[str, ...]
    indicators: tuple[str, ...]
    safeguards: tuple[str, ...]


GOVERNANCE_DOMAINS: tuple[GovernanceDomain, ...] = (
    GovernanceDomain(
        "ARK-GEO", "Geopolitical competition",
        "How does strategic competition affect safety, transparency and cooperation?",
        ("race dynamics", "export restrictions", "supply-chain fragmentation",
         "reduced scientific exchange"),
        ("safety-evaluation disclosure", "cross-border incident channels",
         "publicly documented policy changes"),
        ("shared evaluation protocols", "crisis communication",
         "independent verification"),
    ),
    GovernanceDomain(
        "ARK-CAPITAL", "Corporate and investor influence",
        "How do ownership, financing and commercial incentives shape safety decisions?",
        ("concentrated ownership", "short-term return pressure",
         "conflicts of interest", "gatekeeping"),
        ("funding concentration", "board oversight disclosures",
         "independent safety budget and review"),
        ("independent safety governance", "conflict disclosures",
         "external audits", "research independence"),
    ),
    GovernanceDomain(
        "ARK-POLICY", "Political and regulatory incentives",
        "How do political timelines and regulatory structures affect safe deployment?",
        ("regulatory capture risk", "procurement incentives",
         "uneven enforcement", "accountability gaps"),
        ("consultation transparency", "enforcement records",
         "appeal and redress mechanisms"),
        ("transparent rulemaking", "independent regulators",
         "public-interest impact assessment"),
    ),
    GovernanceDomain(
        "ARK-RESOURCE", "Compute, energy and infrastructure",
        "Who controls the scarce inputs needed to build and deploy advanced AI?",
        ("compute concentration", "energy bottlenecks", "cloud dependence",
         "data and talent gatekeeping"),
        ("supplier concentration", "capacity access terms",
         "energy and water reporting"),
        ("resilient supply chains", "contestable access",
         "infrastructure impact reporting"),
    ),
    GovernanceDomain(
        "ARK-COOP", "International cooperation",
        "Can actors coordinate on incident reporting and safety thresholds?",
        ("standards fragmentation", "trust deficits",
         "unequal participation", "verification gaps"),
        ("joint exercises", "incident-sharing agreements",
         "participation across regions"),
        ("interoperable standards", "inclusive forums",
         "trusted incident channels"),
    ),
    GovernanceDomain(
        "ARK-IMPACT", "Human and societal impact",
        "Who receives AI benefits and who bears its costs and risks?",
        ("unequal access", "labour disruption", "rights impacts",
         "environmental externalities"),
        ("distributional impact data", "service access",
         "worker transition outcomes"),
        ("rights impact assessments", "public participation",
         "remedy and transition support"),
    ),
)


@dataclass(frozen=True, slots=True)
class ResearchExperiment:
    experiment_id: str
    title: str
    hypothesis: str
    method: str
    safety_boundary: str


EXPERIMENTS: tuple[ResearchExperiment, ...] = (
    ResearchExperiment(
        "ARK-PWR-001", "Competitive pressure and safety investment",
        "Higher perceived race pressure may reduce the share of resources allocated to assurance.",
        "Compare synthetic organisations under controlled competition and assurance-budget settings.",
        "Use synthetic budgets only; do not infer intent or assign blame to real actors.",
    ),
    ResearchExperiment(
        "ARK-PWR-002", "Ownership concentration and governance",
        "Concentrated decision rights may reduce independent challenge unless counterbalanced.",
        "Vary synthetic ownership concentration and independent-review requirements.",
        "No real-person influence scores; analyse institutional structures only.",
    ),
    ResearchExperiment(
        "ARK-PWR-003", "Regulatory incentives and capture safeguards",
        "Transparency and independent review may reduce conflicts in synthetic policy processes.",
        "Compare transparent, opaque and independently reviewed mock rulemaking workflows.",
        "No political persuasion, targeting or party rankings.",
    ),
    ResearchExperiment(
        "ARK-PWR-004", "Technology restrictions and fragmentation",
        "Supply restrictions may have mixed effects on resilience, cooperation and duplication.",
        "Use an abstract supply-chain dependency model with no operational procurement advice.",
        "No evasion guidance or sensitive supply-chain exploitation.",
    ),
    ResearchExperiment(
        "ARK-PWR-005", "Compute access and research diversity",
        "Unequal access to compute may reduce independent research participation.",
        "Vary synthetic compute allocation and measure participation and dependency.",
        "No live provider targeting or claims about private contracts without sources.",
    ),
    ResearchExperiment(
        "ARK-PWR-006", "Cooperation under simulated crisis",
        "Pre-agreed channels may improve coordination under uncertainty.",
        "Run tabletop simulations with fictional institutions and delayed information.",
        "No real-world military, infrastructure or crisis command integration.",
    ),
)
