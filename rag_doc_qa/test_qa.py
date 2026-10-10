import unittest

from qa import Index, chunk_markdown, recall_at_k

DOC = """# Pricing
Managed desktops start at a monthly per-seat fee.
Annual plans include a discount.

# Backups
Snapshots run daily and are kept for seven days.

# Security
Multi-factor sign-in is required for every account.
"""


class QATests(unittest.TestCase):
    def setUp(self):
        self.index = Index(chunk_markdown(DOC, "faq.md"))

    def test_chunks_keep_section_titles(self):
        sections = [c["section"] for c in chunk_markdown(DOC, "faq.md")]
        self.assertEqual(sections, ["Pricing", "Backups", "Security"])

    def test_answer_cites_the_right_section(self):
        result = self.index.answer("how long are backups kept?")
        self.assertEqual(result["citations"][0], "faq.md > Backups")

    def test_unrelated_question_returns_no_answer(self):
        result = self.index.answer("what is the weather in Paris")
        self.assertEqual(result["context"], [])
        self.assertEqual(result["citations"], [])

    def test_recall_at_one_on_labeled_questions(self):
        cases = [
            ("per seat monthly price", "faq.md > Pricing"),
            ("daily snapshot retention", "faq.md > Backups"),
            ("multi-factor sign in", "faq.md > Security"),
        ]
        self.assertEqual(recall_at_k(self.index, cases, k=1), 1.0)


if __name__ == "__main__":
    unittest.main()
