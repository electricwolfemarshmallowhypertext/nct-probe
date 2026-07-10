import unittest

from nct_probe import AI_SAMPLE, HUMAN_SAMPLE, trap_score


class NCTProbeTests(unittest.TestCase):
    def test_reference_pair_reproduces_reported_scores(self):
        ai_score = trap_score(AI_SAMPLE)["trap_score"]
        human_score = trap_score(HUMAN_SAMPLE)["trap_score"]

        self.assertEqual(ai_score, 90.0)
        self.assertEqual(human_score, 19.3)
        self.assertEqual(round(ai_score - human_score, 1), 70.7)

    def test_empty_input_is_clean(self):
        self.assertEqual(trap_score("")["trap_score"], 0.0)


if __name__ == "__main__":
    unittest.main()
