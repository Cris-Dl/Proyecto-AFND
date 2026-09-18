import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import patch

import pedidos_ventas
from services.alternative_availability import get_demo_products
from services.alternative_orders_service import AlternativeOrdersService


class AlternativeOrdersServiceTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.db_path = str(Path(self.temporary_directory.name) / "gamergear.db")
        self.db_patch = patch.object(pedidos_ventas, "DB_NAME", self.db_path)
        self.db_patch.start()
        pedidos_ventas.inicializar_bd_pedidos()
        self.service = AlternativeOrdersService(db_path=self.db_path, initialize=False)

    def tearDown(self):
        self.db_patch.stop()
        self.temporary_directory.cleanup()

    def test_alternative_order_persists_q5_without_decreasing_local_stock(self):
        product = get_demo_products()[1]
        original = dict(product)

        result = self.service.create_order(product, "ana", 1, "B")

        self.assertTrue(result.success)
        self.assertEqual(result.order.estado_afnd, "q5")
        self.assertEqual(product, original)
        with closing(sqlite3.connect(self.db_path)) as connection:
            stored = connection.execute(
                "SELECT usuario, producto, cantidad, precio, total, estado_afnd FROM pedidos"
            ).fetchone()
        self.assertEqual(stored, ("ana", product["nombre"], 1, product["precio"], product["precio"], "q5"))

    def test_wrong_source_does_not_create_order_or_change_product(self):
        product = get_demo_products()[0]
        original = dict(product)

        result = self.service.create_order(product, "ana", 1, "V")

        self.assertFalse(result.success)
        self.assertEqual(product, original)
        with closing(sqlite3.connect(self.db_path)) as connection:
            count = connection.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]
        self.assertEqual(count, 0)

    def test_x_scenario_cannot_create_order(self):
        product = get_demo_products()[3]
        result = self.service.create_order(product, "ana", 1, "X")
        self.assertFalse(result.success)
        with closing(sqlite3.connect(self.db_path)) as connection:
            count = connection.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]
        self.assertEqual(count, 0)


if __name__ == "__main__":
    unittest.main()
