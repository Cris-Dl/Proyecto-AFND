import unittest

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

    def test_new_purchase_does_not_depend_on_previous_flow(self):
        self.integration.search_alternatives()
        result = self.integration.start_purchase()
        self.assertEqual(self.integration.snapshot().chain, "I-P")
        self.assertEqual(result.active_states, frozenset({"q3"}))


if __name__ == "__main__":
    unittest.main()
