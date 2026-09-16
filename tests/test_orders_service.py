import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import patch

import pedidos_ventas
from services.orders_service import OrdersService


class OrdersServiceTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.db_path = str(Path(self.temporary_directory.name) / "gamergear.db")
        self.db_patch = patch.object(pedidos_ventas, "DB_NAME", self.db_path)
        self.db_patch.start()
        pedidos_ventas.inicializar_bd_pedidos()
        self.service = OrdersService(db_path=self.db_path, initialize=False)
        self.products = [
            {
                "id": 7,
                "nombre": "Laptop de prueba",
                "precio": 125.50,
                "categoria": "Computadoras",
                "existencia": 5,
                "thumbnail": None,
            }
        ]

    def tearDown(self):
        self.db_patch.stop()
        self.temporary_directory.cleanup()

    def test_create_order_uses_existing_product_logic_and_persists_q5(self):
        result = self.service.create_order(self.products, "ana", 7, 2)

        self.assertTrue(result.success)
        self.assertEqual(result.order.estado_afnd, "q5")
        self.assertEqual(result.order.total, 251.0)
        self.assertEqual(self.products[0]["existencia"], 3)
        self.assertEqual(self.service.get_order_by_id(result.order.id_pedido), result.order)

    def test_invalid_quantity_does_not_persist_or_change_stock(self):
        result = self.service.create_order(self.products, "ana", 7, 8)

        self.assertFalse(result.success)
        self.assertEqual(self.products[0]["existencia"], 5)
        self.assertEqual(self.service.get_orders_by_user("ana"), [])

    def test_orders_are_isolated_by_user(self):
        self.service.create_order(self.products, "ana", 7, 1)
        self.service.create_order(self.products, "luis", 7, 1)

        ana_orders = self.service.get_orders_by_user("ana")
        luis_orders = self.service.get_orders_by_user("luis")
        self.assertEqual([order.usuario for order in ana_orders], ["ana"])
        self.assertEqual([order.usuario for order in luis_orders], ["luis"])

    def test_order_remains_available_from_a_new_service_instance(self):
        created = self.service.create_order(self.products, "ana", 7, 1).order
        restarted_service = OrdersService(db_path=self.db_path, initialize=False)

        self.assertEqual(restarted_service.get_order_by_id(created.id_pedido), created)

    def test_existing_finalize_sale_persists_q6(self):
        created = self.service.create_order(self.products, "ana", 7, 1).order

        success, _message, delivered = self.service.finish_order(created.id_pedido)

        self.assertTrue(success)
        self.assertEqual(delivered.estado_afnd, "q6")
        restarted_service = OrdersService(db_path=self.db_path, initialize=False)
        self.assertEqual(restarted_service.get_order_by_id(created.id_pedido).estado_afnd, "q6")

    def test_database_uses_only_existing_columns(self):
        with closing(sqlite3.connect(self.db_path)) as connection:
            columns = [row[1] for row in connection.execute("PRAGMA table_info(pedidos)")]
        self.assertEqual(
            columns,
            ["id_pedido", "usuario", "producto", "cantidad", "precio", "total", "estado_afnd"],
        )


if __name__ == "__main__":
    unittest.main()
