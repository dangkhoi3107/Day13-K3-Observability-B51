from __future__ import annotations

import inspect

from app import mock_llm, mock_rag


def _observation_type(func) -> str | None:
    """Read the Langfuse wrapper configuration without creating a trace."""

    return inspect.getclosurevars(func).nonlocals.get("as_type")


def test_retrieve_is_wrapped_as_span_and_preserves_behavior(monkeypatch) -> None:
    assert hasattr(mock_rag.retrieve, "__wrapped__")
    assert _observation_type(mock_rag.retrieve) == "span"

    monkeypatch.setitem(mock_rag.STATE, "tool_fail", False)
    monkeypatch.setitem(mock_rag.STATE, "rag_slow", False)

    retrieve_without_trace = mock_rag.retrieve.__wrapped__
    assert retrieve_without_trace("Explain monitoring") == [
        "Metrics detect incidents, traces localize them, logs explain root cause."
    ]
    assert retrieve_without_trace("Unrelated question") == [
        "No domain document matched. Use general fallback answer."
    ]


def test_generate_is_wrapped_as_span_and_preserves_behavior(monkeypatch) -> None:
    assert hasattr(mock_llm.FakeLLM.generate, "__wrapped__")
    assert _observation_type(mock_llm.FakeLLM.generate) == "span"

    monkeypatch.setitem(mock_llm.STATE, "cost_spike", False)
    monkeypatch.setattr(mock_llm.time, "sleep", lambda _seconds: None)
    monkeypatch.setattr(mock_llm.random, "randint", lambda _start, _end: 100)

    llm = mock_llm.FakeLLM(model="test-model")
    generate_without_trace = mock_llm.FakeLLM.generate.__wrapped__
    response = generate_without_trace(llm, "short prompt")

    assert response.model == "test-model"
    assert response.usage.input_tokens == 20
    assert response.usage.output_tokens == 100
    assert "Starter answer" in response.text
