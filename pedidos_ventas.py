import sqlite3

DB_NAME = "gamergear.db"


def inicializar_bd_pedidos():
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pedidos (
            id_pedido INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT,
            producto TEXT,
            cantidad INTEGER,
            precio REAL,
            total REAL,
            estado_afnd TEXT
        )
    ''')
    conexion.commit()
    conexion.close()


def obtener_pedidos_a_entregar():
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT id_pedido, usuario, producto, cantidad, total, estado_afnd FROM pedidos WHERE estado_afnd = 'q5'")
    pedidos = cursor.fetchall()
    conexion.close()
    return pedidos


def finalizar_venta(id_pedido):
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()
    cursor.execute("SELECT estado_afnd FROM pedidos WHERE id_pedido = ?", (id_pedido,))
    resultado = cursor.fetchone()

    if not resultado:
        conexion.close()
        return False, "Error: El pedido no existe."

    estado_actual = resultado[0]

    if estado_actual == 'q5':
        cursor.execute("UPDATE pedidos SET estado_afnd = 'q6' WHERE id_pedido = ?", (id_pedido,))
        conexion.commit()
        conexion.close()
        return True, f"¡Transición exitosa! Pedido {id_pedido} en estado q6 (Entregado)."
    else:
        conexion.close()
        return False, f"Transición inválida. El pedido está en {estado_actual}."


def crear_pedido_prueba(usuario, producto, cantidad, precio):
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()
    total = precio * cantidad
    cursor.execute(
        "INSERT INTO pedidos (usuario, producto, cantidad, precio, total, estado_afnd) VALUES (?, ?, ?, ?, ?, 'q5')",
        (usuario, producto, cantidad, precio, total)
    )
    conexion.commit()
    conexion.close()

inicializar_bd_pedidos()