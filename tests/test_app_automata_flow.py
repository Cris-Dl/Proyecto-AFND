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
    def __init__(self):
        self.order = OrderRecord(1, "demo", "Producto", 1, 10.0, 10.0, "q5")

    def create_order(self, products, username, product_id, quantity):
        self.order = OrderRecord(1, username, "Producto", quantity, 10.0, 10.0 * quantity, "q5")
        return OrderCreationResult(
            success=True,
            order=self.order,
            message="Pedido confirmado correctamente.",
        )

    def get_order_by_id(self, order_id, username=None):
        if self.order.id_pedido != order_id:
            return None
        if username is not None and self.order.usuario != username:
            return None
        return self.order

    def finish_order(self, order_id):
        if self.order.id_pedido != order_id or self.order.estado_afnd != "q5":
            return False, "No se pudo finalizar.", None
        self.order = OrderRecord(
            self.order.id_pedido,
            self.order.usuario,
            self.order.producto,
            self.order.cantidad,
            self.order.precio,
            self.order.total,
            "q6",
        )
        return True, "Entregado.", self.order


class FailingCreateOrdersService(FakeOrdersService):
    def create_order(self, products, username, product_id, quantity):
        return OrderCreationResult(success=False, message="Creación rechazada.")


class FailingDeliveryOrdersService(FakeOrdersService):
    def finish_order(self, order_id):
        return False, "Entrega rechazada.", None


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
        self.application.selected_order_id = None
        self.application.tracking_progress = {}
        self.application.render = lambda *args, **kwargs: None

    def test_authenticated_purchase_and_confirmation_emit_i_p_g_r(self):
        self.application.begin_purchase(2)
        snapshot = self.application.afnd_integration.snapshot()
        self.assertEqual(snapshot.chain, "I-P")
        self.assertEqual(snapshot.result.active_states, frozenset({"q3"}))

        self.application.confirm_real_order()
        snapshot = self.application.afnd_integration.snapshot()
        self.assertEqual(snapshot.chain, "I-P-G-R")
        self.assertEqual(snapshot.result.active_states, frozenset({"q5"}))

    def test_purchase_after_login_restarts_without_duplicate_i(self):
        self.application.usuario_autenticado = None
        self.application.begin_purchase(2)
        self.assertEqual(self.application.current_route, "login")
        self.assertEqual(self.application.afnd_integration.snapshot().chain, "")

        self.application.handle_auth_success("demo")
        self.assertEqual(self.application.current_route, "detalle")
        self.application.begin_purchase(2)
        self.application.confirm_real_order()

        self.assertEqual(self.application.afnd_integration.snapshot().chain, "I-P-G-R")

    def test_searching_alternatives_emits_i_p_d(self):
        self.application.search_alternatives()
        snapshot = self.application.afnd_integration.snapshot()
        self.assertEqual(snapshot.chain, "I-P-D")
        self.assertEqual(snapshot.result.active_states, frozenset({"q7", "q8", "q9"}))

    def test_opening_product_does_not_emit_p(self):
        self.application.open_product({"existencia": 4})
        self.assertEqual(self.application.afnd_integration.snapshot().chain, "")

    def test_tracking_progress_moves_without_changing_persisted_state(self):
        self.application.open_tracking(1)
        self.application.advance_tracking()
        self.application.advance_tracking()

        self.assertEqual(self.application.current_route, "tracking")
        self.assertEqual(self.application.tracking_progress[1], 2)
        self.assertEqual(self.application.orders_service.order.estado_afnd, "q5")
        self.assertEqual(self.application.afnd_integration.snapshot().chain, "I-P-G-R-R-R")
        self.assertEqual(
            self.application.afnd_integration.snapshot().result.active_states,
            frozenset({"q5"}),
        )

    def test_delivery_persists_q6_before_emitting_e(self):
        self.application.open_tracking(1)
        for _ in range(2):
            self.application.advance_tracking()

        self.application.deliver_order()

        snapshot = self.application.afnd_integration.snapshot()
        self.assertEqual(self.application.orders_service.order.estado_afnd, "q6")
        self.assertTrue(snapshot.chain.endswith("E"))
        self.assertEqual(snapshot.result.active_states, frozenset({"q6"}))
        self.assertTrue(snapshot.result.accepted)

    def test_failed_creation_does_not_emit_r(self):
        self.application.orders_service = FailingCreateOrdersService()
        self.application.begin_purchase(1)

        self.application.confirm_real_order()

        snapshot = self.application.afnd_integration.snapshot()
        self.assertEqual(snapshot.chain, "I-P-G")
        self.assertEqual(snapshot.result.active_states, frozenset({"q4"}))

    def test_failed_finalize_sale_does_not_emit_e(self):
        self.application.orders_service = FailingDeliveryOrdersService()
        self.application.open_tracking(1)
        self.application.tracking_progress[1] = 2

        self.application.deliver_order()

        snapshot = self.application.afnd_integration.snapshot()
        self.assertEqual(snapshot.chain, "I-P-G-R")
        self.assertEqual(snapshot.result.active_states, frozenset({"q5"}))
        self.assertEqual(self.application.orders_service.order.estado_afnd, "q5")


if __name__ == "__main__":
    unittest.main()
