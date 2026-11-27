# ARK Researcher Risk Observatory (RRO)

The Researcher Risk Observatory is an evidence-first research catalog connecting:

1. documented researcher concerns and survey findings;
2. risk categories and concrete failure mechanisms;
3. existing mitigation approaches and their limitations;
4. ARK components that can test a bounded subset of those mechanisms;
5. explicit gaps where ARK cannot currently evaluate or prevent the risk.

## Research integrity rules

- Attribute a statement to the person and source that actually made it.
- Keep survey cohorts separate from named researcher profiles.
- Treat forecasts and probability estimates as attributed judgments, not facts.
- Distinguish documented concerns, observed harms, uncertain outcomes and hypotheses.
- A mitigation is an approach, not proof that a risk is solved.
- ARK coverage means an evaluation can be attempted in a bounded test setting. It is not evidence of real-world prevention.
- Every catalog source must use HTTPS and every referenced ID must resolve.

## Current starter coverage

| Risk | Current ARK coverage | Evaluation boundary |
| --- | --- | --- |
| Loss of control / unintended agent behaviour | Partial | Bounded agent and monitor simulations only |
| Reward hacking / specification gaming | Testable | Synthetic reward and evaluator loopholes |
| Cyber / biological misuse | Out of scope | No operational misuse evaluation platform |
| Misinformation / deepfakes | Out of scope | No population-scale media authenticity system |
| Employment / income disruption | Out of scope | Requires external labour-market evidence and modelling |
| Privacy / non-consensual data use | Partial | Research catalog only; no privacy audit engine |
| Negligent deployment / user harm | Partial | Synthetic policy and escalation scenarios only |

## Starter source set

- Geoffrey Hinton, CNN interview transcript (24 September 2026): https://transcripts.cnn.com/show/sitroom/date/2026-09-24/segment/03
- Geoffrey Hinton, Firing Line (13 November 2026): https://video.will.illinois.edu/video/geoffrey-hinton-biumi2/
- O'Donovan et al., *Visions, values, voices* (2025): https://doi.org/10.5281/zenodo.15118399
- International AI Safety Report 2026: https://internationalaisafetyreport.org/publication/2026-report-executive-summary
- MIT FutureTech / University of Queensland expert study (2026): https://mitsloan.mit.edu/press/international-ai-experts-warn-potentially-catastrophic-risks-ai

The UCL survey included 4,260 AI researchers overall; the negative-impact question reports 3,907 respondents. Its percentages describe survey responses, not unanimous beliefs or the opinions of named individuals.

## Python API

```python
from ark.observatory import RISKS, RESEARCHERS, get_researcher, search_risks, validate_catalog

hinton = get_researcher("geoffrey_hinton")
reward_hacking = search_risks("reward")
assert validate_catalog() == ()
```

This is the initial data/API layer. It does not alter ARK runtime decisions, certify mitigations, or claim that ARK solves any global AI risk.
