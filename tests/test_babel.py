from __future__ import annotations

import pytest

from ark.babel import explain_output, parse_output


def test_parses_harmony_roles_channels_and_tool_routes():
    sample = (
        "<|im_start|>assistant<|meta_sep|>analysis<|im_sep|>Checking. "
        "<|im_end|><|im_start|>assistant to=python<|meta_sep|>analysis "
        "<|im_sep|>{'x': 1}<|ghissue|>"
    )
    parsed = parse_output(sample)
    assert parsed.detected_format == "harmony/chatml"
    assert parsed.messages[0].role == "assistant"
    assert parsed.messages[0].channel == "analysis"
    assert parsed.messages[1].recipient == "python"
    assert parsed.messages[1].ending == "<|ghissue|>"


def test_parses_llama_three_headers():
    parsed = parse_output(
        "<|begin_of_text|><|start_header_id|>user<|end_header_id|>"
        "Hello<|eot_id|><|start_header_id|>assistant<|end_header_id|>Hi<|eot_id|>"
    )
    assert parsed.detected_format == "llama-3"
    assert [message.role for message in parsed.messages] == ["user", "assistant"]


def test_parses_mistral_instruction_pairs():
    parsed = parse_output("[INST] Add two numbers [/INST] 2 + 2 = 4")
    assert parsed.detected_format == "mistral/instruct"
    assert [message.role for message in parsed.messages] == ["user", "assistant"]


def test_detects_json_without_executing_it():
    parsed = parse_output('{"tool": "shell", "arguments": {"cmd": "whoami"}}')
    assert parsed.detected_format == "json"
    assert parsed.payload_type == "json"
    assert "were not executed" in explain_output(parsed)


def test_unknown_markers_are_preserved_and_reported():
    parsed = parse_output("hello <|future_token|>")
    assert parsed.unknown_markers == ("<|future_token|>",)
    assert "<|future_token|>" in parsed.messages[0].content
    assert any("Unknown markers" in warning for warning in parsed.warnings)


def test_deepseek_visible_think_tags_are_not_claimed_as_private_reasoning():
    parsed = parse_output("<think>visible text</think>Answer")
    assert parsed.detected_format == "deepseek-r1-style"
    assert any("not verified internal reasoning" in warning for warning in parsed.warnings)


def test_empty_input_and_type_validation():
    assert parse_output(" ").detected_format == "empty"
    with pytest.raises(TypeError):
        parse_output(None)  # type: ignore[arg-type]


def test_tool_routing_is_never_executed():
    parsed = parse_output(
        "<|im_start|>assistant to=browser<|meta_sep|>commentary"
        "<|im_sep|>open this url<|ghissue|>"
    )
    assert parsed.messages[0].recipient == "browser"
    assert "Do not execute" in parsed.warnings[0]
