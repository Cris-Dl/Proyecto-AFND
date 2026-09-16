"""Persistencia productiva de pedidos sobre el esquema existente."""

import sqlite3
from contextlib import closing
from dataclasses import dataclass

from database_config import DB_PATH
from pedidos_ventas import finalizar_venta, inicializar_bd_pedidos
from productos.gestor_productos import buscar_producto, realizar_pedido


@dataclass(frozen=True)
class OrderRecord:
    id_pedido: int
    usuario: str
    producto: str
    cantidad: int
    precio: float
    total: float
    estado_afnd: str

    @classmethod
    def from_row(cls, row):
        return cls(*row)


@dataclass(frozen=True)
class OrderCreationResult:
    success: bool
    order: OrderRecord | None = None
    message: str = ""


class OrdersService:
    """Adapta catálogo y SQLite sin reemplazar la lógica de los compañeros."""

    def __init__(self, db_path=DB_PATH, initialize=True):
        self.db_path = db_path
        if initialize:
            inicializar_bd_pedidos()

    def create_order(self, products, username, product_id, quantity):
        order_data = realizar_pedido(products, product_id, quantity)
        if not order_data:
            return OrderCreationResult(
                success=False,
                message="No fue posible completar el pedido. Verifica la cantidad y existencia.",
            )

        try:
            with closing(sqlite3.connect(self.db_path)) as connection:
                cursor = connection.execute(
                    """
                    INSERT INTO pedidos
                        (usuario, producto, cantidad, precio, total, estado_afnd)
                    VALUES (?, ?, ?, ?, ?, 'q5')
                    """,
                    (
                        username,
                        order_data["producto"],
                        order_data["cantidad"],
                        order_data["precio"],
                        order_data["total"],
                    ),
                )
                order_id = cursor.lastrowid
                connection.commit()
        except sqlite3.Error:
            product = buscar_producto(products, product_id)
            if product is not None:
                product["existencia"] += quantity
            return OrderCreationResult(
                success=False,
                message="No fue posible guardar el pedido. El stock no fue modificado.",
            )

        return OrderCreationResult(
            success=True,
            order=OrderRecord(
                id_pedido=order_id,
                usuario=username,
                producto=order_data["producto"],
                cantidad=order_data["cantidad"],
                precio=order_data["precio"],
                total=order_data["total"],
                estado_afnd="q5",
            ),
            message="Pedido confirmado correctamente.",
        )

    def get_orders_by_user(self, username):
        if not username:
            return []
        with closing(sqlite3.connect(self.db_path)) as connection:
            rows = connection.execute(
                """
                SELECT id_pedido, usuario, producto, cantidad, precio, total, estado_afnd
                FROM pedidos
                WHERE usuario = ?
                ORDER BY id_pedido DESC
                """,
                (username,),
            ).fetchall()
        return [OrderRecord.from_row(row) for row in rows]

    def get_order_by_id(self, order_id, username=None):
        query = """
            SELECT id_pedido, usuario, producto, cantidad, precio, total, estado_afnd
            FROM pedidos
            WHERE id_pedido = ?
        """
        parameters = [order_id]
        if username is not None:
            query += " AND usuario = ?"
            parameters.append(username)

        with closing(sqlite3.connect(self.db_path)) as connection:
            row = connection.execute(query, parameters).fetchone()
        return OrderRecord.from_row(row) if row else None

    def finish_order(self, order_id):
        success, message = finalizar_venta(order_id)
        return success, message, self.get_order_by_id(order_id) if success else None
