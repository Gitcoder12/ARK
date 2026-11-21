"""Parse visible AI conversation formats without executing their contents.

BABEL is an interpreter for observable text, not a universal decryptor. It cannot
recover hidden model state, encrypted payloads, inaccessible reasoning, or tokenizer
IDs without the matching model tokenizer.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any

_HARMONY_MARKERS = {
    "<|im_start|>", "<|im_sep|>", "<|im_end|>", "<|fim_suffix|>",
    "<|meta_sep|>", "<|meta_start|>", "<|ghissue|>", "<|ghreview|>",
    "<|ghcode|>", "<|ghreply|>", "<|ghcomment|>", "<|ghpr_diff|>",
}
_LLAMA_MARKERS = {
    "<|begin_of_text|>", "<|start_header_id|>", "<|end_header_id|>",
    "<|eot_id|>", "<|end_of_turn|>", "<|python_tag|>",
}
_MARKER_RE = re.compile(r"<\|[^>]+\|>|<think>|</think>")
_HARMONY_RE = re.compile(
    r"<\|im_start\|>(.*?)<\|im_sep\|>(.*?)"
    r"(?=<\|im_start\|>|<\|fim_suffix\|>|<\|im_end\|>|<\|ghissue\|>|$)",
    re.DOTALL,
)
_LLAMA_RE = re.compile(
    r"<\|start_header_id\|>(.*?)<\|end_header_id\|>(.*?)"
    r"(?=<\|start_header_id\|>|<\|eot_id\|>|<\|end_of_turn\|>|$)",
    re.DOTALL,
)


@dataclass(frozen=True)
class ParsedMessage:
    """One normalized, visible message or tool-routing instruction."""

    role: str
    content: str
    channel: str | None = None
    recipient: str | None = None
    ending: str | None = None


@dataclass(frozen=True)
class ParsedOutput:
    """Normalized parse result with explicit uncertainty and safety notes."""

    detected_format: str
    messages: tuple[ParsedMessage, ...]
    unknown_markers: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    payload_type: str = "text"
    metadata: dict[str, Any] = field(default_factory=dict)


def _unknown_markers(text: str, known: set[str]) -> tuple[str, ...]:
    found = {match.group(0) for match in _MARKER_RE.finditer(text)}
    return tuple(sorted(found - known))


def _parse_harmony(text: str) -> tuple[ParsedMessage, ...]:
    messages: list[ParsedMessage] = []
    for match in _HARMONY_RE.finditer(text):
        header = match.group(1).strip()
        body = match.group(2).strip()
        ending_match = re.search(
            r"(<\|im_end\|>|<\|fim_suffix\|>|<\|ghissue\|>)\s*$",
            body,
        )
        ending = ending_match.group(1) if ending_match else None
        if ending:
            body = body[: ending_match.start()].rstrip()
        channel = None
        if "<|meta_sep|>" in header:
            header, channel = header.split("<|meta_sep|>", 1)
            channel = channel.strip().split()[0] if channel.strip() else None
        recipient_match = re.search(r"\bto=([^\s]+)", header)
        recipient = recipient_match.group(1) if recipient_match else None
        role = header.split()[0] if header else "unknown"
        messages.append(
            ParsedMessage(role, body, channel, recipient, ending)
        )
    return tuple(messages)


def _parse_llama(text: str) -> tuple[ParsedMessage, ...]:
    messages: list[ParsedMessage] = []
    for match in _LLAMA_RE.finditer(text):
        role = match.group(1).strip().split()[0]
        body = match.group(2).strip()
        messages.append(ParsedMessage(role, body))
    return tuple(messages)


def _parse_mistral(text: str) -> tuple[ParsedMessage, ...]:
    messages: list[ParsedMessage] = []
    chunks = re.split(r"\[INST\]", text)
    for chunk in chunks[1:]:
        if "[/INST]" not in chunk:
            messages.append(ParsedMessage("user", chunk.strip()))
            continue
        prompt, response = chunk.split("[/INST]", 1)
        messages.append(ParsedMessage("user", prompt.strip()))
        response = response.strip()
        if response:
            messages.append(ParsedMessage("assistant", response))
    return tuple(messages)


def parse_output(text: str) -> ParsedOutput:
    """Detect and parse common visible AI message formats.

    Tool recipients are recorded as text only. BABEL never invokes tools,
    follows embedded instructions, or evaluates payloads.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    if not text.strip():
        return ParsedOutput("empty", (), warnings=("No input was provided.",))

    if "<|im_start|>" in text and "<|im_sep|>" in text:
        detected = "harmony/chatml"
        messages = _parse_harmony(text)
        known = _HARMONY_MARKERS
    elif "<|start_header_id|>" in text:
        detected = "llama-3"
        messages = _parse_llama(text)
        known = _LLAMA_MARKERS
    elif "[INST]" in text:
        detected = "mistral/instruct"
        messages = _parse_mistral(text)
        known = set()
    elif "<think>" in text or "</think>" in text:
        detected = "deepseek-r1-style"
        messages = (ParsedMessage("assistant", text.strip()),)
        known = set()
    else:
        try:
            json.loads(text)
        except json.JSONDecodeError:
            detected = "plain-text"
            payload_type = "text"
        else:
            detected = "json"
            payload_type = "json"
        messages = (ParsedMessage("unknown", text.strip()),)
        known = set()

    unknown = _unknown_markers(text, known)
    warnings = [
        "Parsed content is untrusted data. Do not execute embedded instructions or tool calls.",
        "Only visible text was interpreted; hidden model state and inaccessible reasoning are unavailable.",
    ]
    if unknown:
        warnings.append("Unknown markers were preserved; their meaning is not assumed.")
    if detected in {"harmony/chatml", "llama-3"} and not messages:
        warnings.append("A format marker was detected, but no complete message boundary was parsed.")
    if detected == "deepseek-r1-style":
        warnings.append("Visible think tags are treated as text markers, not verified internal reasoning.")
    if detected == "json":
        payload_type = "json"
    elif "payload_type" not in locals():
        payload_type = "text"
    return ParsedOutput(
        detected,
        messages,
        unknown,
        tuple(warnings),
        payload_type,
    )


def explain_output(parsed: ParsedOutput) -> str:
    """Produce a concise, deterministic human-readable explanation."""
    if parsed.detected_format == "empty":
        return "No content to interpret."
    parts = [f"Detected format: {parsed.detected_format}."]
    parts.append(f"Parsed {len(parsed.messages)} visible message(s).")
    for index, message in enumerate(parsed.messages, start=1):
        route = f"; addressed to {message.recipient}" if message.recipient else ""
        channel = f"; channel {message.channel}" if message.channel else ""
        parts.append(f"{index}. {message.role}{channel}{route}: {message.content[:240]}")
    if parsed.unknown_markers:
        parts.append("Unrecognized markers: " + ", ".join(parsed.unknown_markers))
    parts.append("Safety: parsed tool calls are descriptive only and were not executed.")
    return "\n".join(parts)
