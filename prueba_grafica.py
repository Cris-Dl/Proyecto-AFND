import flet as ft


from pedidos_ventas import (
    obtener_pedidos_a_entregar,
    finalizar_venta,
    crear_pedido_prueba
)

def main(page: ft.Page):
    page.title = "Prueba de AFND - Entregas"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window_width = 850
    page.window_height = 600

    def inyectar_valores_quemados():
        pedidos_actuales = obtener_pedidos_a_entregar()
        if not pedidos_actuales:
            crear_pedido_prueba("Cristhian", "Silla Gamer Corsair", 1, 1500.00)
            crear_pedido_prueba("Marvin", "Tarjeta Gráfica RTX 4060", 2, 3200.50)
            crear_pedido_prueba("Diego", "Memoria RAM 32GB RGB", 4, 450.00)
            crear_pedido_prueba("Santiago", "SSD M.2 1TB", 1, 850.00)

    inyectar_valores_quemados()

    def mostrar_mensaje(texto, color):
        page.snack_bar = ft.SnackBar(ft.Text(texto), bgcolor=color)
        page.snack_bar.open = True
        page.update()

    def cargar_tabla():
        tabla_pedidos.rows.clear()

        pedidos = obtener_pedidos_a_entregar()

        if not pedidos:
            texto_sin_pedidos.visible = True
            tabla_pedidos.visible = False
        else:
            texto_sin_pedidos.visible = False
            tabla_pedidos.visible = True
            for pedido in pedidos:
                id_ped, usr, prod, cant, tot, estado = pedido

                btn_entregar = ft.ElevatedButton(
                    "Entregar",
                    icon=ft.Icons.LOCAL_SHIPPING,
                    color=ft.Colors.WHITE,
                    bgcolor=ft.Colors.GREEN_700,
                    on_click=lambda e, pid=id_ped: procesar_entrega(pid)
                )

                tabla_pedidos.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(str(id_ped), weight=ft.FontWeight.BOLD)),
                            ft.DataCell(ft.Text(usr)),
                            ft.DataCell(ft.Text(prod)),
                            ft.DataCell(ft.Text(str(cant))),
                            ft.DataCell(ft.Text(f"Q{tot:.2f}")),
                            ft.DataCell(ft.Text(estado, color=ft.Colors.BLUE_400)),
                            ft.DataCell(btn_entregar),
                        ]
                    )
                )
        page.update()

    def procesar_entrega(id_pedido):
        exito, mensaje = finalizar_venta(id_pedido)
        if exito:
            mostrar_mensaje(mensaje, ft.Colors.GREEN)
            cargar_tabla()
        else:
            mostrar_mensaje(mensaje, ft.Colors.RED)

    titulo = ft.Text("Módulo de Entregas", size=32, weight=ft.FontWeight.BOLD)
    subtitulo = ft.Text("Gestiona los pedidos que están en la etapa de rastreo (estado q5).", color=ft.Colors.GREY_400)

    texto_sin_pedidos = ft.Text("No hay pedidos en estado q5 pendientes de entrega.", color=ft.Colors.ORANGE_400,
                                size=16)

    tabla_pedidos = ft.DataTable(
        heading_row_color=ft.Colors.GREY_900,
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Cliente")),
            ft.DataColumn(ft.Text("Producto")),
            ft.DataColumn(ft.Text("Cant.")),
            ft.DataColumn(ft.Text("Total")),
            ft.DataColumn(ft.Text("Estado AFND")),
            ft.DataColumn(ft.Text("Acción")),
        ],
        rows=[]
    )

    page.add(
        ft.Container(height=10),
        titulo,
        subtitulo,
        ft.Container(height=20),
        texto_sin_pedidos,
        tabla_pedidos
    )

    cargar_tabla()


if __name__ == "__main__":
    ft.run(main)