import asyncio

import flet as ft

from productos.gestor_productos import obtener_productos
from ui.components import build_sidebar, build_top_bar
from ui.theme import BACKGROUND, SUCCESS, configure_page
from ui.views import (
    build_home_view,
    build_login_view,
    build_order_review_view,
    build_placeholder_view,
    build_product_detail_view,
    build_products_view,
    build_profile_view,
)


NARROW_BREAKPOINT = 760
WIDE_BREAKPOINT = 1180


class GamerGearApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.current_route = "inicio"
        self.usuario_autenticado = None
        self.productos = []
        self.products_loading = True
        self.products_error = None
        self.search_query = ""
        self.selected_product = None
        self.selected_quantity = 1
        self.route_before_login = "inicio"
        self.layout_mode = self.get_layout_mode(page.width or WIDE_BREAKPOINT)
        self.compact_navigation = self.layout_mode != "wide"
        self.secondary_navigation = []

        configure_page(page)
        page.on_resized = self.handle_resize

        self.sidebar_host = ft.Container()
        self.top_bar_host = ft.Container()
        self.view_host = ft.Container(expand=True)
        self.main_column = ft.Column(
            controls=[self.top_bar_host, self.view_host],
            spacing=0,
            expand=True,
        )
        self.shell = ft.Row(
            controls=[self.sidebar_host, self.main_column],
            spacing=0,
            expand=True,
        )

        self.render(update=False)
        page.add(self.shell)
        page.run_task(self.load_products)

    @staticmethod
    def get_layout_mode(width):
        if width < NARROW_BREAKPOINT:
            return "narrow"
        if width < WIDE_BREAKPOINT:
            return "medium"
        return "wide"

    def cards_per_row(self):
        return {"narrow": 1, "medium": 2, "wide": 3}[self.layout_mode]

    def selected_navigation_route(self):
        if self.current_route in {"detalle", "revisar_pedido"}:
            return "productos"
        return self.current_route

    def render(self, update=True):
        self.sidebar_host.content = build_sidebar(
            selected=self.selected_navigation_route(),
            on_navigate=self.navigate,
            compact=self.compact_navigation,
            secondary_items=self.secondary_navigation,
        )
        self.top_bar_host.content = build_top_bar(
            usuario=self.usuario_autenticado,
            on_account=self.open_account,
            on_search=self.search_products,
            compact=self.layout_mode == "narrow",
        )
        self.view_host.padding = ft.padding.symmetric(
            horizontal={"narrow": 12, "medium": 20, "wide": 26}[self.layout_mode],
            vertical=16,
        )
        self.view_host.content = self.build_current_view()

        if update:
            self.page.update()

    def build_current_view(self):
        if self.current_route == "productos":
            return build_products_view(
                productos=self.productos,
                loading=self.products_loading,
                error=self.products_error,
                on_retry=self.retry_products,
                on_view=self.open_product,
                initial_query=self.search_query,
                columns=self.cards_per_row(),
            )

        if self.current_route == "detalle" and self.selected_product:
            return build_product_detail_view(
                self.selected_product,
                quantity=self.selected_quantity,
                on_quantity_change=self.update_selected_quantity,
                on_buy=self.begin_purchase,
                on_back=lambda: self.navigate("productos"),
                layout_mode=self.layout_mode,
            )

        if (
            self.current_route == "revisar_pedido"
            and self.selected_product
            and self.usuario_autenticado
        ):
            return build_order_review_view(
                usuario=self.usuario_autenticado,
                producto=self.selected_product,
                quantity=self.selected_quantity,
                on_back=self.return_to_product,
                on_continue=self.continue_order,
                layout_mode=self.layout_mode,
            )

        if self.current_route == "pedidos":
            return build_placeholder_view(
                "Pedidos",
                "Esta sección se integrará en la siguiente fase.",
                ft.Icons.RECEIPT_LONG_ROUNDED,
            )

        if self.current_route == "perfil":
            return build_profile_view(
                usuario=self.usuario_autenticado,
                on_login=self.open_account,
                on_logout=self.logout,
            )

        if self.current_route == "login":
            return build_login_view(
                self.page,
                on_auth_success=self.handle_auth_success,
                on_back=self.return_from_login,
            )

        return build_home_view(
            productos=self.productos,
            loading=self.products_loading,
            error=self.products_error,
            on_explore=lambda: self.navigate("productos"),
            on_retry=self.retry_products,
            on_view=self.open_product,
            columns=self.cards_per_row(),
            wide_layout=self.layout_mode == "wide",
        )

    def navigate(self, route):
        if route == "productos" and self.current_route != "detalle":
            self.search_query = ""
        self.current_route = route
        self.selected_product = None
        self.render()

    def open_product(self, producto):
        self.selected_product = producto
        self.selected_quantity = 1
        self.current_route = "detalle"
        self.render()

    def open_account(self):
        if self.usuario_autenticado:
            self.navigate("perfil")
            return

        if self.current_route == "detalle" and self.selected_product:
            self.route_before_login = "detalle"
            self.current_route = "login"
            self.render()
            return

        self.route_before_login = self.current_route
        self.navigate("login")

    def search_products(self, query):
        self.search_query = query
        self.current_route = "productos"
        self.selected_product = None
        self.render()

    def handle_auth_success(self, usuario):
        self.usuario_autenticado = usuario
        self.return_from_login()

    def return_from_login(self):
        destination = self.route_before_login
        if destination == "login":
            destination = "inicio"
        if destination == "detalle" and self.selected_product:
            self.current_route = "detalle"
            self.render()
            return
        self.navigate(destination)

    def update_selected_quantity(self, quantity):
        self.selected_quantity = quantity

    def begin_purchase(self, quantity):
        self.selected_quantity = quantity
        if not self.usuario_autenticado:
            self.route_before_login = "detalle"
            self.current_route = "login"
            self.render()
            return
        self.current_route = "revisar_pedido"
        self.render()

    def return_to_product(self):
        if self.selected_product:
            self.current_route = "detalle"
            self.render()
            return
        self.navigate("productos")

    def continue_order(self):
        self.page.open(
            ft.SnackBar(
                ft.Text("El pedido está listo para ser procesado."),
                bgcolor=SUCCESS,
            )
        )

    def logout(self):
        self.usuario_autenticado = None
        self.route_before_login = "inicio"
        if self.current_route in {"perfil", "revisar_pedido"}:
            self.current_route = "inicio"
        self.selected_product = None
        self.selected_quantity = 1
        self.render()

    def retry_products(self):
        self.products_loading = True
        self.products_error = None
        self.render()
        self.page.run_task(self.load_products)

    async def load_products(self):
        self.products_loading = True
        self.products_error = None
        self.render()

        try:
            productos = await asyncio.to_thread(obtener_productos)
            if not productos:
                raise RuntimeError("El servicio no devolvió productos.")
            self.productos = productos
        except Exception:
            self.productos = []
            self.products_error = "Revisa tu conexión e inténtalo nuevamente."
        finally:
            self.products_loading = False
            self.render()

    def handle_resize(self, _):
        layout_mode = self.get_layout_mode(self.page.width or WIDE_BREAKPOINT)
        if layout_mode != self.layout_mode:
            self.layout_mode = layout_mode
            self.compact_navigation = layout_mode != "wide"
            self.render()


def main(page: ft.Page):
    GamerGearApp(page)


if __name__ == "__main__":
    ft.app(target=main)
