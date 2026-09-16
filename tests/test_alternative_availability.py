import unittest

from services.alternative_availability import (
    evaluate_alternative_availability,
    get_demo_products,
    scenario_for_product,
)


class AlternativeAvailabilityTests(unittest.TestCase):
    def test_demo_collection_has_all_four_explicit_scenarios(self):
        products = get_demo_products()
        self.assertEqual([product["alternative_scenario"] for product in products], ["S", "B", "V", "X"])
        self.assertTrue(all(product["existencia"] == 0 for product in products))
        self.assertTrue(all(product["demo_afnd"] for product in products))

    def test_each_solution_marks_only_its_matching_option_available(self):
        for product in get_demo_products()[:3]:
            with self.subTest(product=product["nombre"]):
                result = evaluate_alternative_availability(product)
                available = [option.symbol for option in result.options if option.available]
                self.assertEqual(available, [product["alternative_scenario"]])
                self.assertTrue(result.has_solution)

    def test_x_marks_all_three_options_unavailable(self):
        result = evaluate_alternative_availability(get_demo_products()[3])
        self.assertEqual(result.scenario, "X")
        self.assertFalse(result.has_solution)
        self.assertFalse(any(option.available for option in result.options))

    def test_remote_zero_stock_rule_is_deterministic_and_non_mutating(self):
        product = {"id": 42, "existencia": 0, "nombre": "Agotado", "precio": 10.0}
        original = dict(product)
        first = scenario_for_product(product)
        second = scenario_for_product(product)
        self.assertEqual(first, second)
        self.assertEqual(product, original)

    def test_available_local_product_is_rejected(self):
        with self.assertRaises(ValueError):
            evaluate_alternative_availability({"id": 1, "existencia": 2})


if __name__ == "__main__":
    unittest.main()
