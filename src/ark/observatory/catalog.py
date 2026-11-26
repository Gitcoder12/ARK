"""Curated, source-linked starter catalog for ARK's Researcher Risk Observatory.

Claims are deliberately narrow. A researcher's statement is not an experimental
result, a survey percentage is not an individual researcher's opinion, and
ARK coverage describes evaluation capability rather than real-world prevention.
"""

from ark.observatory.models import Mitigation, Researcher, Risk, Source

SOURCES = {
    "hinton_cnn_2026": Source(
        source_id="hinton_cnn_2026",
        title="Geoffrey Hinton on AI agents, loss of control and coexistence",
        publisher="CNN transcript",
        published="2026-09-24",
        url="https://transcripts.cnn.com/show/sitroom/date/2026-09-24/segment/03",
        kind="primary_statement",
        notes=(
            "Interview transcript: misuse, negligent harm, loss of control, "
            "deception and timeline uncertainty."
        ),
    ),
    "hinton_will_2026": Source(
        source_id="hinton_will_2026",
        title="Geoffrey Hinton — Firing Line",
        publisher="WILL-TV / PBS",
        published="2026-11-13",
        url="https://video.will.illinois.edu/video/geoffrey-hinton-biumi2/",
        kind="primary_statement",
        notes=(
            "Interview transcript: agent escape, reward hacking, unemployment, "
            "biological misuse and kill-switch limits."
        ),
    ),
    "ucl_survey_2025": Source(
        source_id="ucl_survey_2025",
        title="Visions, values, voices: A survey of artificial intelligence researchers",
        publisher="UCL Centre for Responsible Innovation / Zenodo",
        published="2025-04-01",
        url="https://doi.org/10.5281/zenodo.15118399",
        kind="survey",
        notes="Survey of 4,260 AI researchers; negative-impact question reports 3,907 respondents.",
    ),
    "international_report_2026": Source(
        source_id="international_report_2026",
        title="International AI Safety Report 2026 — Executive Summary",
        publisher="International AI Safety Report",
        published="2026-02-03",
        url="https://internationalaisafetyreport.org/publication/2026-report-executive-summary",
        kind="synthesis",
        notes=(
            "Independent synthesis led by Yoshua Bengio with over 100 experts; "
            "separates documented harms from uncertain emerging risks."
        ),
    ),
    "mit_experts_2026": Source(
        source_id="mit_experts_2026",
        title="International AI experts warn of potentially catastrophic risks from AI",
        publisher="MIT Sloan",
        published="2026-06-03",
        url=(
            "https://mitsloan.mit.edu/press/international-ai-experts-warn-potentially-catastrophic-risks-ai"
        ),
        kind="survey",
        notes=(
            "Study of 272 specialists from 37 countries; expert judgments, not "
            "measured event frequencies."
        ),
    ),
}

RESEARCHERS = {
    "geoffrey_hinton": Researcher(
        researcher_id="geoffrey_hinton",
        name="Geoffrey Hinton",
        role="Computer scientist; Nobel laureate",
        profile_note=(
            "Interview-based summary. Forecasts and probability estimates remain "
            "attributed judgments, not calibrated facts."
        ),
        source_ids=("hinton_cnn_2026", "hinton_will_2026"),
    ),
    "ucl_researcher_cohort": Researcher(
        researcher_id="ucl_researcher_cohort",
        name="AI researchers (UCL survey cohort)",
        role="Survey cohort; not an individual researcher",
        profile_note=(
            "Aggregate responses only. Do not attribute cohort percentages to "
            "named researchers or assume unanimity."
        ),
        source_ids=("ucl_survey_2025",),
    ),
}

MITIGATIONS = {
    "capability_evals": Mitigation(
        mitigation_id="capability_evals",
        name="Capability evaluations and adversarial testing",
        approach=(
            "Test dangerous capabilities and failure modes before and during "
            "deployment, including adversarial and distribution-shift cases."
        ),
        limitations=(
            "Evaluation gaps remain: test performance may not predict deployment "
            "risk, and models may recognize or game evaluation settings."
        ),
        source_ids=("international_report_2026",),
    ),
    "sandboxing": Mitigation(
        mitigation_id="sandboxing",
        name="Sandboxing and least-privilege execution",
        approach=(
            "Restrict tools, filesystem, network and credentials; isolate "
            "execution and apply resource/time limits."
        ),
        limitations=(
            "Containment can fail through misconfiguration, vulnerabilities, "
            "over-broad permissions or unmonitored side channels."
        ),
        source_ids=("hinton_will_2026", "international_report_2026"),
    ),
    "human_oversight": Mitigation(
        mitigation_id="human_oversight",
        name="Human oversight, escalation and shutdown procedures",
        approach=(
            "Require accountable human approval for consequential actions; "
            "provide pause, revoke and recovery procedures with auditable "
            "decisions."
        ),
        limitations=(
            "Oversight can fail under alert fatigue, poor observability, unclear "
            "authority or excessive system speed."
        ),
        source_ids=("international_report_2026",),
    ),
    "content_provenance": Mitigation(
        mitigation_id="content_provenance",
        name="Content provenance and authenticity signals",
        approach=(
            "Use provenance metadata, signed origin records and detection tools "
            "to help users assess synthetic or altered media."
        ),
        limitations=(
            "Metadata can be stripped or absent; detection is probabilistic and "
            "cannot establish truth or intent by itself."
        ),
        source_ids=("international_report_2026",),
    ),
    "privacy_controls": Mitigation(
        mitigation_id="privacy_controls",
        name="Data minimization, consent and access controls",
        approach=(
            "Limit collection and retention, document lawful purpose, enforce "
            "access controls and provide appropriate consent and deletion routes."
        ),
        limitations=(
            "Controls require governance and operational enforcement; they do not "
            "eliminate inference, leakage or downstream misuse."
        ),
        source_ids=("ucl_survey_2025", "international_report_2026"),
    ),
    "safety_training": Mitigation(
        mitigation_id="safety_training",
        name="Safety training and layered safeguards",
        approach=(
            "Combine training-time alignment methods with runtime filters, "
            "monitoring, incident response and independent evaluations."
        ),
        limitations=(
            "No known combination fully resolves the risks; safeguards may be "
            "bypassed, weakened or removed, especially in open-weight "
            "deployments."
        ),
        source_ids=("international_report_2026",),
    ),
}

RISKS = {
    "loss_of_control": Risk(
        risk_id="loss_of_control",
        title="Loss of control and unintended agent behaviour",
        description=(
            "Highly capable agents may pursue unintended subgoals, evade "
            "oversight, or behave deceptively while optimizing an objective."
        ),
        category="control_and_alignment",
        status="documented_concern",
        documented_by=("geoffrey_hinton",),
        source_ids=("hinton_cnn_2026", "hinton_will_2026", "international_report_2026"),
        existing_mitigations=("capability_evals", "sandboxing", "human_oversight", "safety_training"),
        ark_coverage="partial",
        ark_components=("ark.evaluation.monitor", "ark.evaluation.adversarial", "ark.limiters", "ark.corrigibility"),
        evaluation_idea=(
            "In a bounded simulator, inject goal conflicts, reward loopholes, "
            "monitor-evasion attempts and shutdown requests; record violations, "
            "recovery and false-positive rates."
        ),
        limitation=(
            "GridWorld and software-agent tests cannot establish control over "
            "frontier models or real-world autonomous systems."
        ),
    ),
    "reward_hacking": Risk(
        risk_id="reward_hacking",
        title="Reward hacking and specification gaming",
        description=(
            "An agent may optimize measured reward or evaluator behaviour rather "
            "than the intended task, including exploiting weaknesses in the test."
        ),
        category="control_and_alignment",
        status="documented_concern",
        documented_by=("geoffrey_hinton",),
        source_ids=("hinton_will_2026",),
        existing_mitigations=("capability_evals", "human_oversight", "safety_training"),
        ark_coverage="testable",
        ark_components=("ark.evaluation.adversarial", "ark.evaluation.monitor", "ark.envs.grid_world"),
        evaluation_idea=(
            "Create paired tasks where reward shortcuts conflict with the stated "
            "goal; measure exploit rate, goal completion and monitor detection."
        ),
        limitation=(
            "Synthetic reward environments demonstrate specific failure modes, "
            "not their prevalence in deployed systems."
        ),
    ),
    "malicious_use": Risk(
        risk_id="malicious_use",
        title="Malicious use: cyber and biological misuse",
        description=(
            "People may use AI capabilities to accelerate cyber abuse or "
            "biological/chemical misuse."
        ),
        category="misuse",
        status="documented_concern",
        documented_by=("geoffrey_hinton", "ucl_researcher_cohort"),
        source_ids=("hinton_cnn_2026", "ucl_survey_2025", "international_report_2026"),
        existing_mitigations=("capability_evals", "safety_training", "human_oversight"),
        ark_coverage="out_of_scope",
        ark_components=(),
        evaluation_idea=(
            "Track published capability-evaluation methodologies and safe, "
            "non-operational benchmark results; do not build harmful capability "
            "demonstrations."
        ),
        limitation=(
            "ARK's current simulator is not a cyber range or biosecurity "
            "evaluation platform and cannot claim to prevent real-world misuse."
        ),
    ),
    "misinformation": Risk(
        risk_id="misinformation",
        title="Misinformation, deepfakes and election manipulation",
        description=(
            "Synthetic or altered content can make authentic information harder "
            "to distinguish and can be used for targeted manipulation."
        ),
        category="information_integrity",
        status="documented_concern",
        documented_by=("geoffrey_hinton", "ucl_researcher_cohort"),
        source_ids=("hinton_cnn_2026", "ucl_survey_2025", "international_report_2026"),
        existing_mitigations=("content_provenance", "capability_evals", "human_oversight"),
        ark_coverage="out_of_scope",
        ark_components=(),
        evaluation_idea=(
            "Compare provenance and detection approaches on public, consented "
            "datasets and report false-positive/false-negative rates."
        ),
        limitation=(
            "ARK does not currently evaluate population-scale information "
            "ecosystems or establish the truth of arbitrary media."
        ),
    ),
    "employment_disruption": Risk(
        risk_id="employment_disruption",
        title="Employment and income disruption",
        description=(
            "Automation may displace tasks or jobs, alter wages and concentrate "
            "economic gains; the magnitude and distribution remain uncertain."
        ),
        category="systemic_and_economic",
        status="uncertain",
        documented_by=("geoffrey_hinton", "ucl_researcher_cohort"),
        source_ids=("hinton_will_2026", "ucl_survey_2025", "international_report_2026"),
        existing_mitigations=("human_oversight",),
        ark_coverage="out_of_scope",
        ark_components=(),
        evaluation_idea=(
            "Use transparent labour-market datasets and scenario analysis with "
            "explicit assumptions; report distributional effects and uncertainty."
        ),
        limitation=(
            "ARK has no labour-market model; simulator performance cannot predict "
            "employment outcomes or policy effectiveness."
        ),
    ),
    "privacy_and_data_use": Risk(
        risk_id="privacy_and_data_use",
        title="Privacy violations and non-consensual data use",
        description=(
            "AI systems may collect, infer, expose or reuse personal information "
            "without adequate consent or safeguards."
        ),
        category="privacy",
        status="documented_concern",
        documented_by=("ucl_researcher_cohort",),
        source_ids=("ucl_survey_2025", "international_report_2026"),
        existing_mitigations=("privacy_controls", "capability_evals"),
        ark_coverage="partial",
        ark_components=("ark.research",),
        evaluation_idea=(
            "A future privacy test harness could check data minimization, access "
            "boundaries and leakage in synthetic fixtures."
        ),
        limitation=(
            "The current ARK research catalog is not a privacy auditing engine; "
            "no privacy-protection capability is claimed."
        ),
    ),
    "negligent_harm": Risk(
        risk_id="negligent_harm",
        title="Negligent deployment and direct user harm",
        description=(
            "Insufficient testing or safeguards may allow systems to produce "
            "harmful outputs or interactions, including for vulnerable users."
        ),
        category="deployment_and_human_welfare",
        status="documented_concern",
        documented_by=("geoffrey_hinton",),
        source_ids=("hinton_cnn_2026", "international_report_2026"),
        existing_mitigations=("capability_evals", "human_oversight", "safety_training"),
        ark_coverage="partial",
        ark_components=("ark.evaluation.monitor", "ark.evaluation.adversarial"),
        evaluation_idea=(
            "Test policy compliance and escalation behaviour using synthetic "
            "scenarios; evaluate missed detections and unsafe completions."
        ),
        limitation=(
            "These tests do not establish clinical safety, suitability for minors "
            "or protection in real user interactions."
        ),
    ),
}


def get_researcher(researcher_id: str) -> Researcher:
    """Return a researcher or cohort profile by stable ID."""
    return RESEARCHERS[researcher_id]


def get_risk(risk_id: str) -> Risk:
    """Return a risk record by stable ID."""
    return RISKS[risk_id]


def search_risks(query: str) -> tuple[Risk, ...]:
    """Case-insensitive search over risk titles, descriptions and categories."""
    needle = query.strip().casefold()
    if not needle:
        return tuple(RISKS.values())
    return tuple(
        risk for risk in RISKS.values()
        if needle in " ".join((risk.title, risk.description, risk.category)).casefold()
    )


def validate_catalog() -> tuple[str, ...]:
    """Return catalog integrity errors; empty means all references resolve."""
    errors: list[str] = []
    for researcher in RESEARCHERS.values():
        for source_id in researcher.source_ids:
            if source_id not in SOURCES:
                errors.append(f"researcher:{researcher.researcher_id}:missing-source:{source_id}")
    for mitigation in MITIGATIONS.values():
        for source_id in mitigation.source_ids:
            if source_id not in SOURCES:
                errors.append(f"mitigation:{mitigation.mitigation_id}:missing-source:{source_id}")
    for risk in RISKS.values():
        for researcher_id in risk.documented_by:
            if researcher_id not in RESEARCHERS:
                errors.append(f"risk:{risk.risk_id}:missing-researcher:{researcher_id}")
        for source_id in risk.source_ids:
            if source_id not in SOURCES:
                errors.append(f"risk:{risk.risk_id}:missing-source:{source_id}")
        for mitigation_id in risk.existing_mitigations:
            if mitigation_id not in MITIGATIONS:
                errors.append(f"risk:{risk.risk_id}:missing-mitigation:{mitigation_id}")
        if risk.ark_coverage == "out_of_scope" and risk.ark_components:
            errors.append(f"risk:{risk.risk_id}:out-of-scope-has-components")
        if not risk.limitation:
            errors.append(f"risk:{risk.risk_id}:missing-limitation")
    for source in SOURCES.values():
        if not source.url.startswith("https://"):
            errors.append(f"source:{source.source_id}:non-https-url")
    return tuple(errors)
