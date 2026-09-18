import unittest

from automata.afnd import AFND


class AFNDTests(unittest.TestCase):
    def setUp(self):
        self.afnd = AFND()

    def test_accepted_chains(self):
        accepted = (
            "C-I-P-G-R-E",
            "I-P-G-R-E",
            "I-P-D-B-G-R-E",
            "I-P-D-S-G-R-E",
            "I-P-D-V-G-R-E",
        )
        for chain in accepted:
            with self.subTest(chain=chain):
                result = self.afnd.process_string(chain)
                self.assertTrue(result.accepted)
                self.assertEqual(result.active_states, frozenset({"q6"}))

    def test_rejected_chains(self):
        rejected = ("I-P-D-X", "C-I-P-D-S-X", "I-P", "C-I-P-D")
        for chain in rejected:
            with self.subTest(chain=chain):
                self.assertTrue(self.afnd.process_string(chain).rejected)

    def test_nondeterministic_transition_keeps_three_active_states(self):
        result = self.afnd.process_string("I-P-D")
        self.assertEqual(result.active_states, frozenset({"q7", "q8", "q9"}))
        self.assertEqual(len(result.paths), 3)

    def test_tracking_cycle(self):
        result = self.afnd.process_string("I-P-G-R-R-R-E")
        self.assertTrue(result.accepted)
        self.assertEqual([step.target_states for step in result.history[3:6]], [
            frozenset({"q5"}),
            frozenset({"q5"}),
            frozenset({"q5"}),
        ])

    def test_requested_tracking_chain_reaches_delivery(self):
        result = self.afnd.process_string("I-P-G-R-R-E")
        self.assertTrue(result.accepted)
        self.assertEqual(result.active_states, frozenset({"q6"}))

    def test_tracking_cancellation_chains_reach_q10(self):
        chains = (
            "I-P-G-R-X",
            "I-P-G-R-R-R-X",
            "I-P-D-B-G-R-X",
            "I-P-D-X",
        )
        for chain in chains:
            with self.subTest(chain=chain):
                result = self.afnd.process_string(chain)
                self.assertEqual(result.active_states, frozenset({"q10"}))
                self.assertTrue(result.rejected)

    def test_delivered_order_has_no_x_transition(self):
        result = self.afnd.process_string("I-P-G-R-E-X")
        self.assertEqual(result.active_states, frozenset())
        self.assertTrue(result.rejected)

    def test_invalid_symbol_is_reported(self):
        result = self.afnd.process_string("I-P-D-Z-G-R-E")
        self.assertEqual(result.invalid_symbol, "Z")
        self.assertEqual(result.symbols, ("I", "P", "D"))
        self.assertEqual(result.active_states, frozenset({"q7", "q8", "q9"}))

    def test_empty_chain_stays_at_initial_state(self):
        result = self.afnd.process_string("")
        self.assertTrue(result.empty)
        self.assertTrue(result.rejected)
        self.assertEqual(result.active_states, frozenset({"q0"}))

    def test_step_by_step(self):
        self.afnd.prepare("I-P-D")
        self.assertEqual(self.afnd.step().active_states, frozenset({"q2"}))
        self.assertEqual(self.afnd.step().active_states, frozenset({"q3"}))
        self.assertEqual(self.afnd.step().active_states, frozenset({"q7", "q8", "q9"}))
        self.assertFalse(self.afnd.has_pending)

    def test_undefined_transition_returns_empty_set(self):
        result = self.afnd.process_string("I-G")
        self.assertEqual(result.active_states, frozenset())
        self.assertTrue(result.rejected)


if __name__ == "__main__":
    unittest.main()
