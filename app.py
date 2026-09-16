import asyncio

import flet as ft

from automata.integration import GamerGearAutomataIntegration
from productos.gestor_productos import obtener_productos
from services.orders_service import OrdersService
from ui.components import build_sidebar, build_top_bar
from ui.theme import BACKGROUND, ERROR, SUCCESS, configure_page
from ui.views import (
    ROUTE_COORDINATES,
    build_afnd_visualizer,
    build_home_view,
    build_login_view,
    build_order_review_view,
    build_orders_view,
    build_placeholder_view,
    build_product_detail_view,
    build_products_view,
    build_profile_view,
    build_tracking_view,
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
        self.afnd_integration = GamerGearAutomataIntegration()
        self.orders_service = OrdersService()
        self.selected_order_id = None
        self.tracking_progress = {}

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
        if self.current_route == "tracking":
            return "pedidos"
        if self.current_route == "afnd":
            return "perfil"
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
                on_search_alternatives=self.search_alternatives,
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
                on_confirm=self.confirm_real_order,
                layout_mode=self.layout_mode,
            )

        if self.current_route == "pedidos":
            orders = self.orders_service.get_orders_by_user(self.usuario_autenticado)
            return build_orders_view(
                username=self.usuario_autenticado,
                orders=orders,
                on_login=self.open_account,
                on_track=self.open_tracking,
            )

        if self.current_route == "tracking" and self.usuario_autenticado:
            order = self.orders_service.get_order_by_id(
                self.selected_order_id,
                username=self.usuario_autenticado,
            )
            if order:
                return build_tracking_view(
                    order=order,
                    progress_index=self.tracking_progress.get(order.id_pedido, 0),
                    on_back=lambda: self.navigate("pedidos"),
                    on_advance=self.advance_tracking,
                    on_deliver=self.deliver_order,
                    layout_mode=self.layout_mode,
                )

        if self.current_route == "perfil":
            return build_profile_view(
                usuario=self.usuario_autenticado,
                on_login=self.open_account,
                on_logout=self.logout,
                on_open_afnd=lambda: self.navigate("afnd"),
            )

        if self.current_route == "afnd":
            return build_afnd_visualizer(
                session=self.afnd_integration.session,
                on_back=lambda: self.navigate("perfil"),
                layout_mode=self.layout_mode,
            )

        if self.current_route == "login":
            return build_login_view(
                self.page,
                on_auth_success=self.handle_auth_success,
                on_registration_success=self.handle_registration_success,
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
        self.afnd_integration.login_succeeded()
        self.return_from_login()

    def handle_registration_success(self, _usuario):
        self.afnd_integration.account_created()

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
        self.afnd_integration.start_purchase()
        self.current_route = "revisar_pedido"
        self.render()

    def search_alternatives(self):
        if not self.usuario_autenticado:
            self.route_before_login = "detalle"
            self.current_route = "login"
            self.render()
            return
        self.afnd_integration.search_alternatives()
        self.page.open(
            ft.SnackBar(
                ft.Text("Búsqueda de alternativas iniciada."),
                bgcolor=SUCCESS,
            )
        )

    def return_to_product(self):
        if self.selected_product:
            self.current_route = "detalle"
            self.render()
            return
        self.navigate("productos")

    def confirm_real_order(self):
        self.afnd_integration.confirm_order()
        result = self.orders_service.create_order(
            products=self.productos,
            username=self.usuario_autenticado,
            product_id=self.selected_product["id"],
            quantity=self.selected_quantity,
        )
        if not result.success or not result.order or result.order.estado_afnd != "q5":
            self.page.open(ft.SnackBar(ft.Text(result.message), bgcolor=ERROR))
            return

        self.afnd_integration.start_tracking()
        self.current_route = "pedidos"
        self.selected_product = None
        self.selected_quantity = 1
        self.render()
        self.page.open(
            ft.SnackBar(
                ft.Text(f"Pedido #{result.order.id_pedido} confirmado y en ruta."),
                bgcolor=SUCCESS,
            )
        )

    def open_tracking(self, order_id):
        order = self.orders_service.get_order_by_id(
            order_id,
            username=self.usuario_autenticado,
        )
        if not order or order.estado_afnd != "q5":
            self.page.open(ft.SnackBar(ft.Text("Este pedido no está disponible para rastreo."), bgcolor=ERROR))
            return
        if self.afnd_integration.snapshot().result.active_states != frozenset({"q5"}):
            self.afnd_integration.resume_tracking()
        self.selected_order_id = order.id_pedido
        self.tracking_progress.setdefault(order.id_pedido, 0)
        self.current_route = "tracking"
        self.render()

    def advance_tracking(self):
        order = self.orders_service.get_order_by_id(
            self.selected_order_id,
            username=self.usuario_autenticado,
        )
        if not order or order.estado_afnd != "q5":
            return
        last_index = len(ROUTE_COORDINATES) - 1
        current = self.tracking_progress.get(order.id_pedido, 0)
        if current >= last_index:
            return
        self.tracking_progress[order.id_pedido] = min(current + 1, last_index)
        self.afnd_integration.tracking_update()
        self.render()

    def deliver_order(self):
        order = self.orders_service.get_order_by_id(
            self.selected_order_id,
            username=self.usuario_autenticado,
        )
        last_index = len(ROUTE_COORDINATES) - 1
        if (
            not order
            or order.estado_afnd != "q5"
            or self.tracking_progress.get(order.id_pedido, 0) < last_index
        ):
            return

        success, message, updated_order = self.orders_service.finish_order(order.id_pedido)
        if not success or not updated_order or updated_order.estado_afnd != "q6":
            self.page.open(ft.SnackBar(ft.Text(message), bgcolor=ERROR))
            return

        self.afnd_integration.delivery_completed()
        self.render()
        self.page.open(ft.SnackBar(ft.Text("Pedido entregado correctamente."), bgcolor=SUCCESS))

    def logout(self):
        self.usuario_autenticado = None
        self.route_before_login = "inicio"
        if self.current_route in {"perfil", "revisar_pedido", "tracking"}:
            self.current_route = "inicio"
        self.selected_product = None
        self.selected_order_id = None
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
