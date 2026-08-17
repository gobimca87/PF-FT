from __future__ import annotations


def compute_available_context_tokens(
    *,
    model_context_window: int,
    system_tokens: int,
    agent_tokens: int,
    conversation_tokens: int,
    reserved_output_tokens: int,
    safety_margin_tokens: int,
) -> int:
    """doc 8 §76. May return <= 0 — the caller decides how to respond to overflow (§114-115)."""
    return (
        model_context_window
        - system_tokens
        - agent_tokens
        - conversation_tokens
        - reserved_output_tokens
        - safety_margin_tokens
    )
