import unittest

from app import GamerGearApp
from automata.integration import GamerGearAutomataIntegration
from services.alternative_availability import evaluate_alternative_availability, get_demo_products
from services.orders_service import OrderCreationResult, OrderRecord
from services.routing_service import GAMERGEAR_STORE_LOCATION, build_fallback_route


class FakePage:
    def __init__(self):
        self.opened = []
        self.closed = []

    def open(self, control):
        self.opened.append(control)

    def close(self, control):
        self.closed.append(control)


class FakeOrdersService:
    def __init__(self):
        self.order = OrderRecord(1, "demo", "Producto", 1, 10.0, 10.0, "q5")
        self.create_calls = 0

    def create_order(self, products, username, product_id, quantity):
        self.create_calls += 1
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

    def cancel_order(self, order_id, username):
        if self.order.id_pedido != order_id:
            return False, "No existe.", None
        if self.order.usuario != username:
            return False, "No autorizado.", None
        if self.order.estado_afnd != "q5":
            return False, "Estado inválido.", None
        self.order = OrderRecord(
            self.order.id_pedido,
            self.order.usuario,
            self.order.producto,
            self.order.cantidad,
            self.order.precio,
            self.order.total,
            "q10",
        )
        return True, "Pedido cancelado correctamente.", self.order


class FailingCreateOrdersService(FakeOrdersService):
    def create_order(self, products, username, product_id, quantity):
        return OrderCreationResult(success=False, message="Creación rechazada.")


class FailingDeliveryOrdersService(FakeOrdersService):
    def finish_order(self, order_id):
        return False, "Entrega rechazada.", None


class FailingCancellationOrdersService(FakeOrdersService):
    def cancel_order(self, order_id, username):
        return False, "Cancelación rechazada.", None


class FakeRoutingService:
    def route_for(self, destination):
        return build_fallback_route(GAMERGEAR_STORE_LOCATION, destination)


class FakeAlternativeOrdersService:
    def __init__(self, orders_service):
        self.orders_service = orders_service
        self.create_calls = 0

    def create_order(self, product, username, quantity, source_symbol):
        self.create_calls += 1
        self.orders_service.order = OrderRecord(
            1,
            username,
            product["nombre"],
            quantity,
            product["precio"],
            product["precio"] * quantity,
            "q5",
        )
        return OrderCreationResult(
            success=True,
            order=self.orders_service.order,
            message="Pedido alternativo confirmado correctamente.",
        )


class AppAutomataFlowTests(unittest.TestCase):
    def setUp(self):
        self.application = GamerGearApp.__new__(GamerGearApp)
        self.application.page = FakePage()
        self.application.usuario_autenticado = "demo"
        self.application.productos = [
            {
                "id": 1,
                "nombre": "Producto",
                "precio": 10.0,
                "categoria": "Prueba",
                "existencia": 4,
            }
        ]
        self.application.selected_product = self.application.productos[0]
        self.application.selected_quantity = 1
        self.application.current_route = "detalle"
        self.application.route_before_login = "inicio"
        self.application.afnd_integration = GamerGearAutomataIntegration()
        self.application.orders_service = FakeOrdersService()
        self.application.alternative_orders_service = FakeAlternativeOrdersService(
            self.application.orders_service
        )
        self.application.selected_order_id = None
        self.application.tracking_progress = {}
        self.application.selected_delivery_location = (14.8400, -91.5258)
        self.application.delivery_location_draft = None
        self.application.delivery_locations = {}
        self.application.tracking_routes = {}
        self.application.location_selection_order_id = None
        self.application.routing_service = FakeRoutingService()
        self.application.alternative_availability = None
        self.application.selected_supply_symbol = None
        self.application.selected_supply_source = None
        self.application.alternative_cancelled = False
        self.application.order_supply_sources = {}
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
        self.application.selected_product = get_demo_products()[1]
        self.application.search_alternatives()
        snapshot = self.application.afnd_integration.snapshot()
        self.assertEqual(snapshot.chain, "I-P-D")
        self.assertEqual(snapshot.result.active_states, frozenset({"q7", "q8", "q9"}))
        self.assertEqual(self.application.current_route, "alternativas")

    def test_selecting_bodega_emits_b_and_returns_to_q3(self):
        self.application.selected_product = get_demo_products()[1]
        self.application.search_alternatives()

        self.application.select_alternative_source("B")

        snapshot = self.application.afnd_integration.snapshot()
        self.assertEqual(snapshot.chain, "I-P-D-B")
        self.assertEqual(snapshot.result.active_states, frozenset({"q3"}))
        self.assertEqual(self.application.selected_supply_source, "Bodega")
        self.assertEqual(self.application.current_route, "revisar_pedido")

    def test_x_cancels_without_creating_order_or_changing_stock(self):
        product = get_demo_products()[3]
        original = dict(product)
        self.application.selected_product = product
        self.application.search_alternatives()

        self.application.cancel_alternative_request()

        snapshot = self.application.afnd_integration.snapshot()
        self.assertEqual(snapshot.chain, "I-P-D-X")
        self.assertEqual(snapshot.result.active_states, frozenset({"q10"}))
        self.assertEqual(self.application.orders_service.create_calls, 0)
        self.assertEqual(self.application.alternative_orders_service.create_calls, 0)
        self.assertEqual(product, original)
        self.assertTrue(self.application.alternative_cancelled)

    def test_alternative_purchase_reaches_q5_without_local_stock_change(self):
        product = get_demo_products()[1]
        original = dict(product)
        self.application.selected_product = product
        self.application.search_alternatives()
        self.application.select_alternative_source("B")
        self.application.selected_delivery_location = (14.8400, -91.5258)

        self.application.confirm_real_order()

        snapshot = self.application.afnd_integration.snapshot()
        self.assertEqual(snapshot.chain, "I-P-D-B-G-R")
        self.assertEqual(snapshot.result.active_states, frozenset({"q5"}))
        self.assertEqual(product, original)
        self.assertEqual(self.application.orders_service.create_calls, 0)
        self.assertEqual(self.application.alternative_orders_service.create_calls, 1)
        self.assertEqual(self.application.order_supply_sources[1], "Bodega")

    def test_alternative_location_selection_emits_no_symbol(self):
        self.application.selected_product = get_demo_products()[0]
        self.application.search_alternatives()
        self.application.select_alternative_source("S")
        original_chain = self.application.afnd_integration.snapshot().chain

        self.application.open_delivery_location()
        self.application.select_delivery_point((14.842, -91.53))
        self.application.use_delivery_location()

        self.assertEqual(self.application.afnd_integration.snapshot().chain, original_chain)

    def test_alternative_order_reuses_tracking_r_and_delivery_e(self):
        product = get_demo_products()[2]
        self.application.selected_product = product
        self.application.search_alternatives()
        self.application.select_alternative_source("V")
        self.application.selected_delivery_location = (14.8400, -91.5258)
        self.application.confirm_real_order()

        route = self.application.tracking_routes[1]
        self.application.open_tracking(1)
        for _ in range(len(route.simulation_points) - 1):
            self.application.advance_tracking()
        self.application.deliver_order()

        snapshot = self.application.afnd_integration.snapshot()
        self.assertTrue(snapshot.chain.startswith("I-P-D-V-G-R"))
        self.assertTrue(snapshot.chain.endswith("E"))
        self.assertEqual(snapshot.result.active_states, frozenset({"q6"}))
        self.assertTrue(snapshot.result.accepted)

    def test_opening_product_does_not_emit_p(self):
        self.application.open_product({"existencia": 4})
        self.assertEqual(self.application.afnd_integration.snapshot().chain, "")

    def test_tracking_progress_moves_without_changing_persisted_state(self):
        self.application.tracking_routes[1] = self.application.routing_service.route_for(
            self.application.selected_delivery_location
        )
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
        route = self.application.routing_service.route_for(self.application.selected_delivery_location)
        self.application.tracking_routes[1] = route
        self.application.open_tracking(1)
        for _ in range(len(route.simulation_points) - 1):
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

    def test_confirmation_without_location_does_not_emit_g_or_create_order(self):
        self.application.begin_purchase(1)
        self.application.selected_delivery_location = None

        self.application.confirm_real_order()

        snapshot = self.application.afnd_integration.snapshot()
        self.assertEqual(snapshot.chain, "I-P")
        self.assertEqual(snapshot.result.active_states, frozenset({"q3"}))

    def test_selecting_or_changing_location_does_not_emit_symbols(self):
        self.application.begin_purchase(1)
        original_chain = self.application.afnd_integration.snapshot().chain

        self.application.open_delivery_location()
        self.application.select_delivery_point((14.842, -91.53))
        self.application.use_delivery_location()

        self.assertEqual(self.application.current_route, "revisar_pedido")
        self.assertEqual(self.application.afnd_integration.snapshot().chain, original_chain)

    def test_failed_finalize_sale_does_not_emit_e(self):
        self.application.orders_service = FailingDeliveryOrdersService()
        route = self.application.routing_service.route_for(self.application.selected_delivery_location)
        self.application.tracking_routes[1] = route
        self.application.open_tracking(1)
        self.application.tracking_progress[1] = len(route.simulation_points) - 1

        self.application.deliver_order()

        snapshot = self.application.afnd_integration.snapshot()
        self.assertEqual(snapshot.chain, "I-P-G-R")
        self.assertEqual(snapshot.result.active_states, frozenset({"q5"}))
        self.assertEqual(self.application.orders_service.order.estado_afnd, "q5")

    def test_first_cancel_click_only_opens_confirmation(self):
        self.application.begin_purchase(1)
        self.application.confirm_real_order()
        chain_before = self.application.afnd_integration.snapshot().chain

        self.application.request_order_cancellation(1)

        self.assertEqual(self.application.orders_service.order.estado_afnd, "q5")
        self.assertEqual(self.application.afnd_integration.snapshot().chain, chain_before)
        self.assertIsInstance(self.application.page.opened[-1], __import__("flet").AlertDialog)

    def test_normal_order_cancellation_persists_before_x(self):
        self.application.begin_purchase(1)
        self.application.confirm_real_order()
        self.application.advance_tracking()

        self.application.confirm_order_cancellation(1)

        snapshot = self.application.afnd_integration.snapshot()
        self.assertEqual(self.application.orders_service.order.estado_afnd, "q10")
        self.assertEqual(snapshot.chain, "I-P-G-R-R-X")
        self.assertEqual(snapshot.result.active_states, frozenset({"q10"}))

    def test_alternative_b_order_can_be_cancelled_in_tracking(self):
        product = get_demo_products()[1]
        self.application.selected_product = product
        self.application.search_alternatives()
        self.application.select_alternative_source("B")
        self.application.selected_delivery_location = (14.8400, -91.5258)
        self.application.confirm_real_order()
        self.application.advance_tracking()

        self.application.confirm_order_cancellation(1)

        snapshot = self.application.afnd_integration.snapshot()
        self.assertEqual(snapshot.chain, "I-P-D-B-G-R-R-X")
        self.assertEqual(snapshot.result.active_states, frozenset({"q10"}))
        self.assertEqual(self.application.orders_service.order.estado_afnd, "q10")

    def test_cancelled_order_cannot_advance_or_be_delivered(self):
        self.application.begin_purchase(1)
        self.application.confirm_real_order()
        self.application.confirm_order_cancellation(1)
        chain_after_cancel = self.application.afnd_integration.snapshot().chain
        progress_after_cancel = self.application.tracking_progress[1]

        self.application.advance_tracking()
        self.application.deliver_order()

        self.assertEqual(self.application.afnd_integration.snapshot().chain, chain_after_cancel)
        self.assertEqual(self.application.tracking_progress[1], progress_after_cancel)
        self.assertEqual(self.application.orders_service.order.estado_afnd, "q10")

    def test_sqlite_failure_does_not_emit_x(self):
        self.application.orders_service = FailingCancellationOrdersService()
        self.application.alternative_orders_service = FakeAlternativeOrdersService(
            self.application.orders_service
        )
        self.application.begin_purchase(1)
        self.application.confirm_real_order()
        chain_before = self.application.afnd_integration.snapshot().chain

        self.application.confirm_order_cancellation(1)

        self.assertEqual(self.application.afnd_integration.snapshot().chain, chain_before)
        self.assertEqual(self.application.orders_service.order.estado_afnd, "q5")

    def test_delivered_order_cannot_be_cancelled_or_receive_x(self):
        self.application.begin_purchase(1)
        self.application.confirm_real_order()
        route = self.application.tracking_routes[1]
        for _ in range(len(route.simulation_points) - 1):
            self.application.advance_tracking()
        self.application.deliver_order()
        chain_after_delivery = self.application.afnd_integration.snapshot().chain

        self.application.confirm_order_cancellation(1)

        self.assertEqual(self.application.afnd_integration.snapshot().chain, chain_after_delivery)
        self.assertEqual(self.application.orders_service.order.estado_afnd, "q6")

    def test_cancelled_order_cannot_be_cancelled_twice(self):
        self.application.begin_purchase(1)
        self.application.confirm_real_order()
        self.application.confirm_order_cancellation(1)
        chain_after_cancel = self.application.afnd_integration.snapshot().chain

        self.application.confirm_order_cancellation(1)

        self.assertEqual(self.application.afnd_integration.snapshot().chain, chain_after_cancel)
        self.assertEqual(self.application.orders_service.order.estado_afnd, "q10")


if __name__ == "__main__":
    unittest.main()
