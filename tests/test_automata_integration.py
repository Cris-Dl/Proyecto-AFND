import unittest

from automata.afnd import AFND
from automata.integration import GamerGearAutomataIntegration


class AutomataIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.integration = GamerGearAutomataIntegration()

    def test_account_creation_followed_by_login(self):
        self.integration.account_created()
        result = self.integration.login_succeeded()
        snapshot = self.integration.snapshot()
        self.assertEqual(snapshot.chain, "C-I")
        self.assertEqual(result.active_states, frozenset({"q2"}))

    def test_authenticated_purchase_starts_a_new_valid_flow(self):
        self.integration.login_succeeded()
        result = self.integration.start_purchase()
        self.assertEqual(self.integration.snapshot().chain, "I-P")
        self.assertEqual(result.active_states, frozenset({"q3"}))

    def test_purchase_after_login_does_not_duplicate_login_symbol(self):
        self.integration.login_succeeded()
        self.integration.start_purchase()
        result = self.integration.confirm_order()
        self.assertEqual(self.integration.snapshot().chain, "I-P-G")
        self.assertEqual(result.active_states, frozenset({"q4"}))

    def test_unavailable_product_opens_all_alternative_states(self):
        result = self.integration.search_alternatives()
        self.assertEqual(self.integration.snapshot().chain, "I-P-D")
        self.assertEqual(result.active_states, frozenset({"q7", "q8", "q9"}))

    def test_each_available_source_returns_to_q3(self):
        for symbol in ("S", "B", "V"):
            with self.subTest(symbol=symbol):
                self.integration.search_alternatives()
                result = self.integration.select_alternative(symbol)
                self.assertEqual(result.active_states, frozenset({"q3"}))
                self.assertEqual(self.integration.snapshot().chain, f"I-P-D-{symbol}")

    def test_no_solution_reaches_q10(self):
        self.integration.search_alternatives()
        result = self.integration.cancel_alternatives()
        self.assertEqual(result.active_states, frozenset({"q10"}))
        self.assertEqual(self.integration.snapshot().chain, "I-P-D-X")

    def test_tracking_cancellation_reaches_q10(self):
        self.integration.start_purchase()
        self.integration.confirm_order()
        self.integration.start_tracking()
        result = self.integration.tracking_cancelled()
        self.assertEqual(self.integration.snapshot().chain, "I-P-G-R-X")
        self.assertEqual(result.active_states, frozenset({"q10"}))

    def test_each_alternative_tracking_cancellation_reaches_q10(self):
        for symbol in ("S", "B", "V"):
            with self.subTest(symbol=symbol):
                self.integration.search_alternatives()
                self.integration.select_alternative(symbol)
                self.integration.confirm_order()
                self.integration.start_tracking()
                result = self.integration.tracking_cancelled()
                self.assertEqual(
                    self.integration.snapshot().chain,
                    f"I-P-D-{symbol}-G-R-X",
                )
                self.assertEqual(result.active_states, frozenset({"q10"}))

    def test_new_purchase_does_not_depend_on_previous_flow(self):
        self.integration.search_alternatives()
        result = self.integration.start_purchase()
        self.assertEqual(self.integration.snapshot().chain, "I-P")
        self.assertEqual(result.active_states, frozenset({"q3"}))

    def test_manual_machine_does_not_overwrite_real_flow(self):
        self.integration.start_purchase()
        original = self.integration.snapshot()

        manual_machine = AFND()
        manual_result = manual_machine.process_string("I-P-D")

        self.assertEqual(manual_result.active_states, frozenset({"q7", "q8", "q9"}))
        self.assertEqual(self.integration.snapshot(), original)


if __name__ == "__main__":
    unittest.main()
