"""Lead triage: rules decide the easy cases, an LLM decides the rest.

Every decision is checked against a labeled set, so accuracy and LLM usage are measured, not guessed.
"""
from dataclasses import dataclass
from typing import Callable, Iterable

HOT, WARM, COLD = "hot", "warm", "cold"
LABELS = {HOT, WARM, COLD}


@dataclass(frozen=True)
class Lead:
    name: str
    company_size: int
    message: str
    budget_mentioned: bool


def rule_label(lead: Lead) -> str | None:
    """Return a label only when the rule is confident; None means ask the LLM."""
    if lead.company_size < 3 and not lead.budget_mentioned:
        return COLD
    if lead.budget_mentioned and lead.company_size >= 10:
        return HOT
    return None


def triage(lead: Lead, llm_classify: Callable[[Lead], str]) -> tuple[str, str]:
    """Return (label, source) where source is 'rules', 'llm' or 'llm-invalid'."""
    label = rule_label(lead)
    if label:
        return label, "rules"
    answer = llm_classify(lead)
    if answer not in LABELS:
        # Never trust an out-of-range answer: fall back to a human-review label.
        return WARM, "llm-invalid"
    return answer, "llm"


def evaluate(examples: Iterable[tuple[Lead, str]], llm_classify: Callable[[Lead], str]) -> dict:
    """Score the full pipeline against expected labels."""
    total = correct = llm_calls = 0
    for lead, expected in examples:
        label, source = triage(lead, llm_classify)
        total += 1
        correct += label == expected
        llm_calls += source.startswith("llm")
    return {
        "accuracy": correct / total if total else 0.0,
        "llm_share": llm_calls / total if total else 0.0,
        "total": total,
    }
