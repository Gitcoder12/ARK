# ARK BABEL — AI Protocol & Output Interpreter

**BABEL** means **Broad AI Behaviour, Encoding & Language Decoder**.

BABEL is a local, deterministic interpreter for visible AI conversation formats. It
normalizes message roles, channels, recipients, endings, JSON payloads, and unknown
markers into a readable report.

## Initial supported formats

- OpenAI-style Harmony / ChatML visible markers
- Llama 3 header markers
- Mistral / instruction-style `[INST]` blocks
- DeepSeek-R1-style visible `<think>` tags
- Plain text and JSON payloads

## Run

Install ARK as usual, then launch ARKWorld:

```bash
pip install -e ".[dev]"
streamlit run arkworld.py
```

Select **BABEL — Protocol Interpreter** in the Streamlit pages navigation.

Run focused tests:

```bash
pytest -q tests/test_babel.py
```

## Important limits

BABEL does not decrypt encrypted data, infer hidden model state, reconstruct inaccessible
reasoning, or translate arbitrary token IDs without the exact tokenizer vocabulary and
model configuration. Unknown markers are preserved and flagged instead of guessed.

Tool calls and embedded instructions are parsed as untrusted text only. BABEL never
executes commands, opens URLs, invokes tools, or follows instructions found in input.
A parser result is not proof of model intent, truthfulness, or safety.
