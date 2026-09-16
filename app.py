import asyncio

import flet as ft

from productos.gestor_productos import obtener_productos
from ui.components import build_sidebar, build_top_bar
from ui.theme import BACKGROUND, configure_page
from ui.views import (
    build_home_view,
    build_login_view,
    build_placeholder_view,
    build_product_detail_view,
    build_products_view,
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
        if self.current_route == "detalle":
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
                on_back=lambda: self.navigate("productos"),
            )

        if self.current_route == "pedidos":
            return build_placeholder_view(
                "Pedidos",
                "Esta sección se integrará en la siguiente fase.",
                ft.Icons.RECEIPT_LONG_ROUNDED,
            )

        if self.current_route == "perfil":
            return build_placeholder_view(
                "Perfil",
                "Esta sección se integrará en la siguiente fase.",
                ft.Icons.PERSON_ROUNDED,
            )

        if self.current_route == "login":
            return build_login_view(
                self.page,
                on_auth_success=self.handle_auth_success,
                on_back=lambda: self.navigate("inicio"),
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
        self.current_route = "detalle"
        self.render()

    def open_account(self):
        self.navigate("perfil" if self.usuario_autenticado else "login")

    def search_products(self, query):
        self.search_query = query
        self.current_route = "productos"
        self.selected_product = None
        self.render()

    def handle_auth_success(self, usuario):
        self.usuario_autenticado = usuario
        self.navigate("inicio")

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
