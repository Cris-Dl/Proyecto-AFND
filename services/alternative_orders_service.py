"""Persistencia limitada de pedidos abastecidos por la simulación alternativa."""

import sqlite3
from contextlib import closing

from database_config import DB_PATH
from pedidos_ventas import inicializar_bd_pedidos
from services.alternative_availability import evaluate_alternative_availability
from services.orders_service import OrderCreationResult, OrderRecord


class AlternativeOrdersService:
    """Crea pedidos q5 sin presentar stock alternativo como inventario local."""

    def __init__(self, db_path=DB_PATH, initialize=True):
        self.db_path = db_path
        if initialize:
            inicializar_bd_pedidos()

    def create_order(self, product, username, quantity, source_symbol):
        try:
            normalized_quantity = int(quantity)
            price = float(product["precio"])
            availability = evaluate_alternative_availability(product)
        except (KeyError, TypeError, ValueError):
            return OrderCreationResult(False, message="El producto alternativo no es válido.")

        normalized_source = str(source_symbol).upper()
        if (
            not username
            or normalized_quantity < 1
            or not availability.has_solution
            or availability.scenario != normalized_source
        ):
            return OrderCreationResult(
                False,
                message="La fuente alternativa seleccionada no está disponible.",
            )

        total = price * normalized_quantity
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
                        product["nombre"],
                        normalized_quantity,
                        price,
                        total,
                    ),
                )
                order_id = cursor.lastrowid
                connection.commit()
        except sqlite3.Error:
            return OrderCreationResult(
                False,
                message="No fue posible guardar el pedido alternativo.",
            )

        return OrderCreationResult(
            success=True,
            order=OrderRecord(
                id_pedido=order_id,
                usuario=username,
                producto=product["nombre"],
                cantidad=normalized_quantity,
                precio=price,
                total=total,
                estado_afnd="q5",
            ),
            message="Pedido alternativo confirmado correctamente.",
        )
