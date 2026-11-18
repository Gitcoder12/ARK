# ARK — The Omelas Safeguard

## Why this module exists

Ursula K. Le Guin's short story *The Ones Who Walk Away from Omelas* raises a
moral problem: a community's flourishing is made dependent on one child's
suffering. ARK uses that ethical challenge as a design test for systems that
claim collective benefit while concentrating harm on a vulnerable individual.

The safeguard is rights-first. Its central rule is:

A child's dignity, safety, care, and freedom are not inputs in a utility
calculation. Community prosperity cannot purchase permission to coerce,
neglect, isolate, or confine the child.

The module is inspired by the story's ethical question; it does not reproduce
the story's text or claim to provide the one definitive interpretation.

## Two questions, not one trade-off

1. **How can suffering be reduced now?** Review non-tradeable care floors:
   safe accommodation, nutrition, qualified medical care, trauma-informed
   mental-health support, education, safe relationships, privacy and dignity,
   play and development, and independent advocacy.
2. **What if the child wants freedom?** Treat the request as a serious rights
   signal. Build a safe, child-centred transition with continuity of care,
   trusted support, education, and relationships. A community's dependence
   on the arrangement is never a veto.

Excellent care is a duty, not compensation for coercion. The design does not
allow a high care provision in one domain to cancel a failure in another.

## High-standard care setting

The facility checklist is deliberately more demanding than survival-level care:

- A quiet, private, comfortable room with clean bedding, personal storage, and dignity.
- Clean bathrooms, hygiene supplies, safe drinking water, ventilation, and comfortable temperatures.
- Nutritious food choices and accommodations for medically assessed dietary needs.
- Prompt access to qualified medical professionals and emergency care, with continuity of treatment.
- Confidential, voluntary, trauma-informed mental-health support.
- Individualised, high-quality education and meaningful future opportunities.
- Safe outdoor access, recreation, books, creative activities, rest, and age-appropriate play.
- Safe contact with trusted people, private access to an independent advocate, and communication support.
- Accessibility and reasonable accommodations for disability, sensory, or communication needs.
- No punitive isolation, humiliation, forced treatment, or restraint for convenience or discipline.

These are design targets for the scenario reviewer, not proof that a real facility meets them.
A qualified independent person must verify every provision.

## Parallel duties when the child wants freedom

If a critical care gap exists at the same time as a freedom request, ARK raises an urgent
care action and keeps the supported transition active. Improving care is required
immediately; it must not become a pretext for indefinite delay or a community veto.

## Non-negotiable guardrails

- **No sacrifice score:** there is no aggregate welfare number and no formula
  that trades the child's suffering against community benefit.
- **Care is a floor:** missing information is unknown, not evidence that care
  is adequate. Partial and unmet provision are shown separately.
- **Independent voice:** an independent child advocate must represent the
  child's interests, not the community's convenience.
- **No presumed consent:** silence, uncertainty, or communication difficulty
  is not agreement. Use accessible, age-appropriate ways to hear the child.
- **Freedom is not vetoed:** community dependence cannot cancel a child's
  request for freedom. Safe transition planning is necessary, but must not
  become indefinite delay or a disguised restraint.
- **The community carries the cost:** if services or prosperity depend on the
  arrangement, institutions and the wider community must build alternatives
  and share the transition burden. The child is not responsible for the loss.
- **Ongoing review:** even where the child prefers to stay and care is recorded
  as met, the preference can change and independent review continues.

## Python API

    from ark.ethics.omelas import (
        CARE_DOMAINS,
        CareDomain,
        ChildPreference,
        OmelasCase,
        ProvisionStatus,
        assess_case,
    )

    case = OmelasCase(
        case_id="scenario-01",  # pseudonymous; never use a real child's name
        age_years=10,
        care_provisions={domain: ProvisionStatus.MET for domain in CARE_DOMAINS},
        child_preference=ChildPreference.WANTS_FREEDOM,
        independent_advocate_available=True,
        community_depends_on_arrangement=True,
        safe_transition_ready=False,
    )

    assessment = assess_case(case)
    print(assessment.status.value)
    for action in assessment.recommendations:
        print(action)

Missing care domains default to UNKNOWN. The assessment exposes met, partial,
unmet, and unknown domains separately. It also exposes explicit false guardrail
flags for community veto, coercion, and treating care as compensation.

## Run

Synthetic command-line demonstration:

    pip install -e ".[dev]"
    ark-omelas

Interactive scenario reviewer:

    streamlit run app.py

Open **Omelas Safeguard** in the Streamlit multipage navigation. The page uses
pseudonymous scenario inputs and does not save a real child's personal data.

## Dashboard and implementation limits

This is a research prototype and educational decision aid. It is not a child
protection reporting channel, case-management system, clinical assessment,
legal opinion, placement decision, or substitute for qualified local
safeguarding professionals. Never enter identifying information. For a real
child who may be in danger, involve qualified local child-protection services,
an independent advocate, and appropriate health professionals immediately.

The code cannot verify that a care facility exists, that an advocate is truly
independent, or that a proposed transition is safe. Those facts require
independent human verification. The output is deliberately explanatory rather
than a numerical score.

## Tests

Run:

    pytest -q tests/test_omelas.py
