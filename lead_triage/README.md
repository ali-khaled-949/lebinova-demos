# Lead triage: rules first, LLM second, scored

Most inbound leads are clear: a tiny company with no budget, or a large company that names a budget. Rules label those without a model call. Everything else goes to an LLM, and any answer outside the allowed labels (hot, warm, cold) falls back to warm for human review.

`evaluate()` runs the full pipeline over a labeled set and reports accuracy and the share of leads that needed the LLM. That second number is what drives cost.

- `triage.py`: `rule_label`, `triage`, `evaluate`
- `test_triage.py`: covers rule decisions, the LLM path, invalid answers, and the evaluation report

The LLM is a function argument. In a real run it would wrap a model call; here a fake classifier keeps the tests offline.

Run: `python3 -m unittest`
