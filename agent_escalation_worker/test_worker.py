import unittest

from worker import LOW, RISKY, Proposal, Worker


class WorkerTests(unittest.TestCase):
    def setUp(self):
        self.worker = Worker()

    def test_low_risk_with_evidence_runs(self):
        status = self.worker.run("t1", lambda t: Proposal("update lead status", LOW, ["crm row 12"]))
        self.assertEqual(status, "done")
        self.assertEqual(self.worker.executed, ["update lead status"])

    def test_risky_action_waits_for_approval(self):
        status = self.worker.run("t2", lambda t: Proposal("send quote email", RISKY, ["pricing page"]))
        self.assertEqual(status, "awaiting_approval")
        self.assertEqual(self.worker.executed, [])
        self.assertEqual(self.worker.approve(0), "done_after_approval")
        self.assertEqual(self.worker.executed, ["send quote email"])

    def test_agent_exception_is_escalated_not_reported_as_success(self):
        def broken(task):
            raise TimeoutError("provider timed out")

        self.assertEqual(self.worker.run("t3", broken), "escalated")
        self.assertIn("provider timed out", self.worker.audit()[-1][2])

    def test_missing_evidence_is_escalated(self):
        status = self.worker.run("t4", lambda t: Proposal("update lead status", LOW, []))
        self.assertEqual(status, "escalated")
        self.assertEqual(self.worker.executed, [])


if __name__ == "__main__":
    unittest.main()
