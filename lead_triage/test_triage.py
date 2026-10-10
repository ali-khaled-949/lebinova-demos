import unittest

from triage import COLD, HOT, WARM, Lead, evaluate, rule_label, triage

SAMPLES = [
    (Lead("a", 1, "just browsing", False), COLD),
    (Lead("b", 25, "need pricing this month", True), HOT),
    (Lead("c", 5, "maybe next year", False), WARM),
    (Lead("d", 2, "we have budget for 40 seats", True), HOT),
]


def fake_llm(lead: Lead) -> str:
    return WARM if "maybe" in lead.message else HOT if "budget" in lead.message else WARM


class TriageTests(unittest.TestCase):
    def test_rules_handle_clear_cases_without_llm(self):
        self.assertEqual(rule_label(SAMPLES[0][0]), COLD)
        self.assertEqual(rule_label(SAMPLES[1][0]), HOT)

    def test_ambiguous_lead_goes_to_llm(self):
        self.assertIsNone(rule_label(SAMPLES[2][0]))
        _, source = triage(SAMPLES[2][0], fake_llm)
        self.assertEqual(source, "llm")

    def test_invalid_llm_answer_falls_back_to_review(self):
        label, source = triage(SAMPLES[2][0], lambda lead: "urgent!!")
        self.assertEqual((label, source), (WARM, "llm-invalid"))

    def test_evaluate_reports_accuracy_and_llm_share(self):
        report = evaluate(SAMPLES, fake_llm)
        self.assertEqual(report["total"], 4)
        self.assertEqual(report["llm_share"], 2 / 4)
        self.assertAlmostEqual(report["accuracy"], 1.0)


if __name__ == "__main__":
    unittest.main()
