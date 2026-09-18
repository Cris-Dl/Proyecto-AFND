import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pedidos_ventas
from automata.integration import GamerGearAutomataIntegration
from services.orders_service import OrdersService


class FullOrderFlowTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.db_path = str(Path(self.temporary_directory.name) / "gamergear.db")
        self.db_patch = patch.object(pedidos_ventas, "DB_NAME", self.db_path)
        self.db_patch.start()
        pedidos_ventas.inicializar_bd_pedidos()
        self.service = OrdersService(db_path=self.db_path, initialize=False)
        self.integration = GamerGearAutomataIntegration()
        self.products = [
            {
                "id": 9,
                "nombre": "Teléfono de prueba",
                "precio": 250.0,
                "categoria": "Teléfonos",
                "existencia": 3,
                "thumbnail": None,
            }
        ]

    def tearDown(self):
        self.db_patch.stop()
        self.temporary_directory.cleanup()

    def test_purchase_tracking_and_delivery_complete_the_real_chain(self):
        self.integration.start_purchase()
        self.integration.confirm_order()
        creation = self.service.create_order(self.products, "ana", 9, 1)
        self.assertTrue(creation.success)

        self.integration.start_tracking()
        self.assertEqual(creation.order.estado_afnd, "q5")
        self.assertEqual(self.integration.snapshot().chain, "I-P-G-R")
        self.assertEqual(self.integration.snapshot().result.active_states, frozenset({"q5"}))

        self.integration.tracking_update()
        self.integration.tracking_update()
        self.assertEqual(self.service.get_order_by_id(creation.order.id_pedido).estado_afnd, "q5")
        self.assertEqual(len(self.service.get_orders_by_user("ana")), 1)
        self.assertEqual(self.integration.snapshot().chain, "I-P-G-R-R-R")

        success, _message, delivered = self.service.finish_order(creation.order.id_pedido)
        self.assertTrue(success)
        self.assertEqual(delivered.estado_afnd, "q6")
        self.integration.delivery_completed()

        snapshot = self.integration.snapshot()
        self.assertEqual(snapshot.chain, "I-P-G-R-R-R-E")
        self.assertEqual(snapshot.result.active_states, frozenset({"q6"}))
        self.assertTrue(snapshot.result.accepted)

        restarted_service = OrdersService(db_path=self.db_path, initialize=False)
        self.assertEqual(restarted_service.get_order_by_id(creation.order.id_pedido).estado_afnd, "q6")
        self.assertEqual(restarted_service.get_orders_by_user("otro"), [])


if __name__ == "__main__":
    unittest.main()
