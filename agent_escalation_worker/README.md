# Bounded agent worker with approval and escalation

An agent proposes one action per task. The worker decides what happens next:

| Outcome | When |
|---|---|
| `done` | Low-risk action with evidence attached. Runs immediately. |
| `awaiting_approval` | Risky action. Queued until a person approves it with `approve()`. |
| `escalated` | Agent threw an error, returned no evidence, or gave an unknown risk level. The error is logged, never reported as success. |

Every outcome is written to a SQLite audit log.

This follows the same design as the Lead Operator agent in the LebiNova platform: the agent can prepare work, but customer messages, quotes, spending, and deletions stay behind explicit approval.

Files: `worker.py`, `test_worker.py`

Run: `python3 -m unittest`
