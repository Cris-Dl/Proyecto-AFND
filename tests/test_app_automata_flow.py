import unittest

from app import GamerGearApp
from automata.integration import GamerGearAutomataIntegration
from services.orders_service import OrderCreationResult, OrderRecord


class FakePage:
    def __init__(self):
        self.opened = []

    def open(self, control):
        self.opened.append(control)


class FakeOrdersService:
    def create_order(self, products, username, product_id, quantity):
        return OrderCreationResult(
            success=True,
            order=OrderRecord(1, username, "Producto", quantity, 10.0, 10.0 * quantity, "q5"),
            message="Pedido confirmado correctamente.",
        )


class AppAutomataFlowTests(unittest.TestCase):
    def setUp(self):
        self.application = GamerGearApp.__new__(GamerGearApp)
        self.application.page = FakePage()
        self.application.usuario_autenticado = "demo"
        self.application.productos = [{"id": 1, "existencia": 4}]
        self.application.selected_product = self.application.productos[0]
        self.application.selected_quantity = 1
        self.application.current_route = "detalle"
        self.application.route_before_login = "inicio"
        self.application.afnd_integration = GamerGearAutomataIntegration()
        self.application.orders_service = FakeOrdersService()
        self.application.render = lambda *args, **kwargs: None

    def test_authenticated_purchase_and_confirmation_emit_i_p_g(self):
        self.application.begin_purchase(2)
        snapshot = self.application.afnd_integration.snapshot()
        self.assertEqual(snapshot.chain, "I-P")
        self.assertEqual(snapshot.result.active_states, frozenset({"q3"}))

        self.application.confirm_real_order()
        snapshot = self.application.afnd_integration.snapshot()
        self.assertEqual(snapshot.chain, "I-P-G")
        self.assertEqual(snapshot.result.active_states, frozenset({"q4"}))

    def test_purchase_after_login_restarts_without_duplicate_i(self):
        self.application.usuario_autenticado = None
        self.application.begin_purchase(2)
        self.assertEqual(self.application.current_route, "login")
        self.assertEqual(self.application.afnd_integration.snapshot().chain, "")

        self.application.handle_auth_success("demo")
        self.assertEqual(self.application.current_route, "detalle")
        self.application.begin_purchase(2)
        self.application.confirm_real_order()

        self.assertEqual(self.application.afnd_integration.snapshot().chain, "I-P-G")

    def test_searching_alternatives_emits_i_p_d(self):
        self.application.search_alternatives()
        snapshot = self.application.afnd_integration.snapshot()
        self.assertEqual(snapshot.chain, "I-P-D")
        self.assertEqual(snapshot.result.active_states, frozenset({"q7", "q8", "q9"}))

    def test_opening_product_does_not_emit_p(self):
        self.application.open_product({"existencia": 4})
        self.assertEqual(self.application.afnd_integration.snapshot().chain, "")


if __name__ == "__main__":
    unittest.main()
