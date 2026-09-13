from producto import productos

def mostrar_productos():
    for producto in productos:
        print(
            f"{producto['id']} - {producto['nombre']} - "
            f"Q{producto['precio']:.2f} - "
            f"Existencia: {producto['existencia']}"
        )

def buscar_producto(id_producto):
    for producto in productos:
        if producto["id"] == id_producto:
            return producto
    return None

def realizar_pedido(id_producto, cantidad):
    producto = buscar_producto(id_producto)

    if producto is None:
        print("Producto no encontrado.")
        return None

    if cantidad <= 0:
        print("La cantidad debe ser mayor que cero.")
        return None

    if producto["existencia"] < cantidad:
        print("No hay suficiente existencia.")
        return None

    total = producto["precio"] * cantidad

    pedido = {
        "producto": producto["nombre"],
        "cantidad": cantidad,
        "precio": producto["precio"],
        "total": total
    }

    producto["existencia"] -= cantidad

    print("\nPedido realizado correctamente.")
    print(f"Producto: {pedido['producto']}")
    print(f"Cantidad: {pedido['cantidad']}")
    print(f"Total: Q{pedido['total']:.2f}")

    return pedido

print("===== PRODUCTOS =====")
mostrar_productos()

print("\n===== REALIZAR PEDIDO =====")
realizar_pedido(2, 3)

print("\n===== PRODUCTOS ACTUALIZADOS =====")
mostrar_productos()