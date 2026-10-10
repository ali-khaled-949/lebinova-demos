"""Bounded agent worker: low-risk actions run, risky ones wait for approval, failures escalate.

Pattern: an agent proposes an action; the worker decides what happens next. The agent never acts on its own
for anything marked risky, and a run that errors or has no evidence is recorded as an escalation, not a success.
"""
import sqlite3
from dataclasses import dataclass, field
from typing import Callable

LOW, RISKY = "low", "risky"


@dataclass
class Proposal:
    action: str
    risk: str
    evidence: list[str] = field(default_factory=list)


class Worker:
    def __init__(self, db_path: str = ":memory:"):
        self.db = sqlite3.connect(db_path)
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS runs (id INTEGER PRIMARY KEY, task TEXT, status TEXT, detail TEXT)"
        )
        self.approvals: list[dict] = []
        self.executed: list[str] = []

    def _log(self, task: str, status: str, detail: str) -> str:
        self.db.execute("INSERT INTO runs (task, status, detail) VALUES (?, ?, ?)", (task, status, detail))
        self.db.commit()
        return status

    def run(self, task: str, agent: Callable[[str], Proposal]) -> str:
        try:
            proposal = agent(task)
        except Exception as exc:  # provider or runtime failure: say so, do not claim success
            return self._log(task, "escalated", f"agent error: {exc}")
        if not proposal.evidence:
            return self._log(task, "escalated", "no evidence attached")
        if proposal.risk == RISKY:
            self.approvals.append({"task": task, "action": proposal.action})
            return self._log(task, "awaiting_approval", proposal.action)
        if proposal.risk != LOW:
            return self._log(task, "escalated", f"unknown risk level: {proposal.risk}")
        self.executed.append(proposal.action)
        return self._log(task, "done", proposal.action)

    def approve(self, index: int) -> str:
        item = self.approvals.pop(index)
        self.executed.append(item["action"])
        return self._log(item["task"], "done_after_approval", item["action"])

    def audit(self) -> list[tuple]:
        return self.db.execute("SELECT task, status, detail FROM runs ORDER BY id").fetchall()
