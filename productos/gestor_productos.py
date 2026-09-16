import requests

def obtener_productos():

    url = "https://dummyjson.com/products?limit=0"

    respuesta = requests.get(url)

    if respuesta.status_code == 200:

        datos = respuesta.json()

        productos = []

        categorias = {
            "beauty": "Belleza",
            "fragrances": "Fragancias",
            "furniture": "Muebles",
            "groceries": "Comestibles",
            "home-decoration": "Decoración del hogar",
            "kitchen-accessories": "Accesorios de cocina",
            "laptops": "Computadoras",
            "mens-shirts": "Camisas para hombre",
            "mens-shoes": "Zapatos para hombre",
            "mens-watches": "Relojes para hombre",
            "mobile-accessories": "Accesorios móviles",
            "motorcycle": "Motocicletas",
            "skin-care": "Cuidado de la piel",
            "smartphones": "Teléfonos",
            "sports-accessories": "Accesorios deportivos",
            "sunglasses": "Lentes de sol",
            "tablets": "Tabletas",
            "tops": "Blusas",
            "vehicle": "Vehículos",
            "womens-bags": "Bolsos para mujer",
            "womens-dresses": "Vestidos para mujer",
            "womens-jewellery": "Joyería para mujer",
            "womens-shoes": "Zapatos para mujer",
            "womens-watches": "Relojes para mujer"
        }

        for producto in datos["products"]:

            categoria = producto["category"]

            if categoria in categorias:
                categoria = categorias[categoria]

            productos.append({
                "id": producto["id"],
                "nombre": producto["title"],
                "precio": producto["price"],
                "categoria": categoria,
                "existencia": producto["stock"]
            })

        return productos

    else:

        print("No se pudieron obtener los productos.")
        return []

def mostrar_productos(productos):

    print("\n========== PRODUCTOS ==========")

    for producto in productos:

        print(
            f"ID: {producto['id']} | "
            f"Producto: {producto['nombre']} | "
            f"Precio: Q{producto['precio']:.2f} | "
            f"Categoría: {producto['categoria']} | "
            f"Existencia: {producto['existencia']}"
        )

def buscar_producto(productos, id_producto):

    for producto in productos:

        if producto["id"] == id_producto:
            return producto

    return None


def realizar_pedido(productos, id_producto, cantidad):

    producto = buscar_producto(productos, id_producto)

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

    print("\n========== PEDIDO ==========")
    print("Pedido realizado correctamente.")
    print(f"Producto: {pedido['producto']}")
    print(f"Cantidad: {pedido['cantidad']}")
    print(f"Precio: Q{pedido['precio']:.2f}")
    print(f"Total: Q{pedido['total']:.2f}")

    return pedido

if __name__ == "__main__":
    productos = obtener_productos()

    if productos:

        mostrar_productos(productos)

        print("\n========== BUSCAR PRODUCTO ==========")

        id_producto = int(input("Ingrese el ID del producto: "))

        producto = buscar_producto(productos, id_producto)

        if producto:

            print("\nProducto encontrado.")
            print(f"ID: {producto['id']}")
            print(f"Nombre: {producto['nombre']}")
            print(f"Precio: Q{producto['precio']:.2f}")
            print(f"Categoría: {producto['categoria']}")
            print(f"Existencia: {producto['existencia']}")

        else:

            print("Producto no encontrado.")

        print("\n========== REALIZAR PEDIDO ==========")

        id_producto = int(input("Ingrese el ID del producto: "))
        cantidad = int(input("Ingrese la cantidad: "))

        realizar_pedido(productos, id_producto, cantidad)

    else:

        print("No hay productos disponibles.")
