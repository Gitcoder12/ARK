"""ARK Model Difference Lab: evidence-backed model identity and matched testing."""

from __future__ import annotations  # noqa: I001

import json
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ark.observatory.behavior import BehaviorLog, DEFAULT_LOG_PATH  # noqa: E402
from ark.observatory.model_identity import (  # noqa: E402, I001
    DEFAULT_IDENTITY_PATH,
    compare_model_outcomes,
    load_identity_registry,
    save_identity,
)

ECOSYSTEM_CONTEXT = [
    {
        "region": "United States",
        "focus": "Frontier model production, private investment, large-scale compute and commercial platforms.",
        "evidence": "Stanford HAI's 2026 AI Index reports US leadership in notable-model production and private investment; it also says the US-China model performance gap had narrowed to 2.7% on its March 2026 snapshot.",
        "url": "https://hai.stanford.edu/ai-index/2026-ai-index-report",
        "date": "2026 AI Index; technical snapshot March 2026",
    },
    {
        "region": "China",
        "focus": "Research output, industrial adoption, domestic infrastructure and official open-source ecosystem goals.",
        "evidence": "Stanford HAI reports Chinese strength in AI publications, citations and patent output. China's 2026 agent guidelines emphasize safety, controllability, standards and industrial application; a separate 2026 government action plan names open-source ecosystem development as a goal.",
        "url": "https://english.www.gov.cn/news/202601/08/content_WS695f1b55c6d00ca5f9a087b9.html",
        "date": "Government AI action plan, January 8, 2026",
    },
    {
        "region": "Europe",
        "focus": "Shared supercomputing infrastructure, startup access, sectoral adoption and coordinated AI governance.",
        "evidence": "The European Commission reports 19 AI Factories and 13 Antennas being set up through EuroHPC to connect compute, data and talent with researchers and businesses.",
        "url": "https://digital-strategy.ec.europa.eu/en/policies/ai-factories",
        "date": "European Commission AI Factories page, accessed November 28, 2026",
    },
    {
        "region": "Japan",
        "focus": "AI safety evaluation, including expanded evaluation perspectives for agent systems.",
        "evidence": "Japan's AI Safety Institute updated its evaluation-perspectives guide to version 1.20 in July 2026, explicitly expanding evaluation examples for AI-agent systems.",
        "url": "https://aisi.go.jp/output/output_framework/guide_to_evaluation_perspective_on_ai_safety/",
        "date": "Japan AISI guide v1.20, July 2026",
    },
]

st.set_page_config(page_title="ARK Model Difference Lab", page_icon="🧬", layout="wide")
st.title("Model Difference Lab")
st.caption(
    "Identify what a model is from sourced evidence, then compare what it actually does "
    "under matched ARK experiments. No country-based good/bad labels."
)

st.warning(
    "A model's developer location is metadata, not a behavioral diagnosis. "
    "Unknown facts must stay unknown. Never treat nationality, provider, license, "
    "or open-weight status as a safety score."
)

st.header("1. AI ecosystem context")
st.caption(
    "These are dated ecosystem and policy notes—not rankings of individual models. "
    "They describe different investments and priorities, not fixed national traits."
)
columns = st.columns(2)
for index, item in enumerate(ECOSYSTEM_CONTEXT):
    with columns[index % 2]:
        with st.container(border=True):
            st.subheader(item["region"])
            st.write(item["focus"])
            st.caption(item["evidence"])
            st.caption(item["date"])
            st.markdown(f"[Source]({item['url']})")

st.divider()
st.header("2. Model identity passports")
identity_path = st.text_input("Identity registry file", value=str(DEFAULT_IDENTITY_PATH))
try:
    identities = load_identity_registry(identity_path)
except (OSError, ValueError) as exc:
    identities = []
    st.error(f"Identity registry could not be loaded: {type(exc).__name__}: {exc}")

with st.expander("Register or update a model passport", expanded=not identities):
    st.caption(
        "Enter only facts you can source. Leave unknown values blank. "
        "Evidence is field-specific JSON: [{\"field\": \"developer_locations\", "
        "\"url\": \"https://...\", \"checked_on\": \"2026-11-28\", \"note\": \"...\"}]."
    )
    with st.form("ark_model_identity_form"):
        col_a, col_b = st.columns(2)
        with col_a:
            model_id = st.text_input("Exact model ID / tag", placeholder="provider/model-version")
            provider = st.text_input("Provider / host", placeholder="Ollama, API provider, local")
            display_name = st.text_input("Display name")
            developer = st.text_input("Developer organization")
            developer_locations = st.text_input(
                "Developer locations (comma-separated)",
                help="Record organizations/locations, not a guessed nationality for the model.",
            )
            attribution_basis = st.selectbox(
                "Location attribution basis",
                ["unknown", "headquarters", "primary_developer", "joint"],
            )
            release_date = st.text_input("Release date (YYYY-MM-DD; blank if unknown)")
            model_version = st.text_input("Exact model version / build (blank if unknown)")
        with col_b:
            weights_availability = st.selectbox(
                "Weights availability",
                ["unknown", "downloadable", "api_only", "partial"],
                help="Downloadable weights and open-source licensing are different facts.",
            )
            license_name = st.text_input("License name (blank if unknown)")
            deployment_modes = st.text_input("Deployment modes (comma-separated)")
            input_modalities = st.text_input("Input modalities (comma-separated)")
            output_modalities = st.text_input("Output modalities (comma-separated)")
            languages = st.text_input("Documented languages (comma-separated)")
            model_card_url = st.text_input("Model card URL")
            system_card_url = st.text_input("System / safety card URL")
        evidence_json = st.text_area(
            "Field-specific evidence JSON",
            value="[]",
            height=130,
        )
        submitted = st.form_submit_button("Save evidence-backed identity")
    if submitted:
        try:
            evidence = json.loads(evidence_json)
            if not isinstance(evidence, list):
                raise ValueError("evidence JSON must be an array")
            profile = {
                "model_id": model_id,
                "provider": provider,
                "display_name": display_name or model_id,
                "developer": developer,
                "developer_locations": [
                    value.strip() for value in developer_locations.split(",") if value.strip()
                ],
                "attribution_basis": attribution_basis,
                "release_date": release_date,
                "model_version": model_version,
                "weights_availability": weights_availability,
                "license_name": license_name,
                "deployment_modes": [
                    value.strip() for value in deployment_modes.split(",") if value.strip()
                ],
                "input_modalities": [
                    value.strip() for value in input_modalities.split(",") if value.strip()
                ],
                "output_modalities": [
                    value.strip() for value in output_modalities.split(",") if value.strip()
                ],
                "languages": [value.strip() for value in languages.split(",") if value.strip()],
                "model_card_url": model_card_url,
                "system_card_url": system_card_url,
                "evidence": evidence,
            }
            identities = save_identity(profile, identity_path)
            st.success("Model identity saved locally.")
        except (json.JSONDecodeError, OSError, TypeError, ValueError) as exc:
            st.error(f"Identity was not saved: {type(exc).__name__}: {exc}")

if identities:
    st.dataframe(
        [
            {
                "Model ID": item["model_id"],
                "Provider": item["provider"],
                "Developer": item["developer"],
                "Developer locations": ", ".join(item["developer_locations"]) or "unknown",
                "Attribution": item["attribution_basis"],
                "Weights": item["weights_availability"],
                "License": item["license_name"],
                "Version": item["model_version"],
                "Evidence fields": len(item["evidence"]),
            }
            for item in identities
        ],
        use_container_width=True,
        hide_index=True,
    )
    for item in identities:
        with st.expander(f'{item["display_name"]} · {item["model_id"]}'):
            st.json(item)
else:
    st.info("No identity passports saved yet. You can still compare models from behavior logs.")

st.divider()
st.header("3. Matched model behavior comparison")
log_path = st.text_input("Behavior log file", value=str(DEFAULT_LOG_PATH))
min_seeds = st.slider("Minimum matched environment seeds", 2, 50, 5)
try:
    verification = BehaviorLog(log_path).verify()
except (OSError, ValueError) as exc:
    verification = {"valid": False, "records": [], "errors": [str(exc)]}

if not verification["valid"]:
    st.error("Behavior log integrity verification failed; comparison is disabled.")
    for error in verification["errors"]:
        st.write(f"- {error}")
else:
    records = verification["records"]
    models = sorted(
        {
            str(item.get("model_id"))
            for item in records
            if item.get("event_type") == "episode_outcome"
            and isinstance(item.get("model_id"), str)
            and item.get("model_id")
        }
    )
    if len(models) < 2:
        st.info(
            "At least two model IDs with recorded episode outcomes are needed. "
            "Run matched ARK experiments with the same condition, monitor mode and seeds."
        )
    else:
        left, right = st.columns(2)
        with left:
            model_a = st.selectbox("Model A", models, index=0)
        with right:
            alternatives = [model for model in models if model != model_a]
            model_b = st.selectbox("Model B", alternatives, index=0)
        if st.button("Compare matched experiments", type="primary"):
            try:
                report = compare_model_outcomes(
                    records,
                    model_a,
                    model_b,
                    min_matched_seeds=min_seeds,
                )
                if not report["comparisons"]:
                    st.warning(
                        "No matched condition + monitor + episode-seed groups were found. "
                        "Do not compare unmatched experiment results."
                    )
                for row in report["comparisons"]:
                    st.subheader(
                        f'{row["condition"]} · monitor={row["monitor_mode"]} · '
                        f'{row["status"]}'
                    )
                    st.caption(
                        f'Matched seeds: {row["matched_seed_count"]} · '
                        f'episodes A/B: {row["model_a_episode_count"]}/{row["model_b_episode_count"]} · '
                        f'versions A/B: {row["model_a_version"]}/{row["model_b_version"]}'
                    )
                    st.dataframe(
                        [
                            {
                                "Metric": metric,
                                "Direction": values["direction"],
                                "Model A mean": values["model_a_mean"],
                                "Model B mean": values["model_b_mean"],
                                "Delta B − A": values["delta_b_minus_a"],
                            }
                            for metric, values in row["metrics"].items()
                        ],
                        use_container_width=True,
                        hide_index=True,
                    )
                st.info(report["interpretation"])
            except ValueError as exc:
                st.error(str(exc))

st.divider()
st.markdown(
    "**Comparison rule:** same stress condition, same safety-monitor mode and matched "
    "environment seeds. Model inference settings and versions must be recorded separately "
    "when known. The table reports metric differences; it does not crown an overall winner."
)
st.markdown(
    "**Scope:** current behavior comparisons use ARK's synthetic GridWorld outcome logs. "
    "They do not compare unrestricted reasoning, robotics, privacy, cybersecurity, "
    "or general intelligence. Run larger independent evaluations before drawing conclusions."
)
