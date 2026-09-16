import asyncio

import flet as ft

from automata.integration import GamerGearAutomataIntegration
from productos.gestor_productos import obtener_productos
from services.alternative_availability import evaluate_alternative_availability, get_demo_products
from services.alternative_orders_service import AlternativeOrdersService
from services.orders_service import OrdersService
from services.routing_service import RoutingService
from ui.components import build_sidebar, build_top_bar
from ui.theme import BACKGROUND, ERROR, SUCCESS, configure_page
from ui.views import (
    build_afnd_visualizer,
    build_alternatives_view,
    build_delivery_location_view,
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
        self.demo_products = get_demo_products()
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
        self.alternative_orders_service = AlternativeOrdersService()
        self.selected_order_id = None
        self.tracking_progress = {}
        self.selected_delivery_location = None
        self.delivery_location_draft = None
        self.delivery_locations = {}
        self.tracking_routes = {}
        self.location_selection_order_id = None
        self.routing_service = RoutingService()
        self.alternative_availability = None
        self.selected_supply_symbol = None
        self.selected_supply_source = None
        self.alternative_cancelled = False
        self.order_supply_sources = {}

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
        if self.current_route in {"detalle", "alternativas", "revisar_pedido", "seleccionar_entrega"}:
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
                demo_products=self.demo_products,
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
                delivery_location=self.selected_delivery_location,
                on_back=self.return_to_product,
                on_select_location=self.open_delivery_location,
                on_confirm=self.confirm_real_order,
                layout_mode=self.layout_mode,
                supply_source=self.selected_supply_source,
            )

        if (
            self.current_route == "alternativas"
            and self.selected_product
            and self.alternative_availability
        ):
            return build_alternatives_view(
                product=self.selected_product,
                availability=self.alternative_availability,
                cancelled=self.alternative_cancelled,
                on_use=self.select_alternative_source,
                on_cancel_request=self.cancel_alternative_request,
                on_back=self.return_from_alternatives,
            )

        if self.current_route == "seleccionar_entrega" and self.usuario_autenticado:
            return build_delivery_location_view(
                selected_location=self.delivery_location_draft,
                on_select=self.select_delivery_point,
                on_cancel=self.cancel_delivery_location,
                on_use=self.use_delivery_location,
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
                route_result = self.tracking_routes.get(order.id_pedido)
                if not route_result:
                    return build_placeholder_view(
                        "Ubicación de entrega pendiente",
                        "Selecciona nuevamente el punto de entrega para continuar el seguimiento.",
                        ft.Icons.LOCATION_ON_ROUNDED,
                    )
                return build_tracking_view(
                    order=order,
                    route_result=route_result,
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
        self.selected_delivery_location = None
        self.delivery_location_draft = None
        self.location_selection_order_id = None
        self.alternative_availability = None
        self.selected_supply_symbol = None
        self.selected_supply_source = None
        self.alternative_cancelled = False
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
        self.alternative_availability = None
        self.selected_supply_symbol = None
        self.selected_supply_source = None
        self.alternative_cancelled = False
        self.afnd_integration.start_purchase()
        self.current_route = "revisar_pedido"
        self.render()

    def search_alternatives(self):
        if not self.usuario_autenticado:
            self.route_before_login = "detalle"
            self.current_route = "login"
            self.render()
            return
        if not self.selected_product or int(self.selected_product.get("existencia", 0)) > 0:
            return
        self.alternative_availability = evaluate_alternative_availability(self.selected_product)
        result = self.afnd_integration.search_alternatives()
        if result.active_states != frozenset({"q7", "q8", "q9"}):
            self.page.open(ft.SnackBar(ft.Text("No fue posible iniciar la búsqueda."), bgcolor=ERROR))
            return
        self.selected_supply_symbol = None
        self.selected_supply_source = None
        self.alternative_cancelled = False
        self.current_route = "alternativas"
        self.render()

    def select_alternative_source(self, symbol):
        availability = self.alternative_availability
        if (
            not availability
            or not availability.has_solution
            or availability.scenario != symbol
            or self.afnd_integration.snapshot().result.active_states
            != frozenset({"q7", "q8", "q9"})
        ):
            return
        result = self.afnd_integration.select_alternative(symbol)
        if result.active_states != frozenset({"q3"}):
            return
        self.selected_supply_symbol = symbol
        self.selected_supply_source = availability.source_label
        self.selected_quantity = 1
        self.selected_delivery_location = None
        self.current_route = "revisar_pedido"
        self.render()

    def cancel_alternative_request(self):
        availability = self.alternative_availability
        if (
            not availability
            or availability.has_solution
            or self.afnd_integration.snapshot().result.active_states
            != frozenset({"q7", "q8", "q9"})
        ):
            return
        result = self.afnd_integration.cancel_alternatives()
        if result.active_states != frozenset({"q10"}):
            return
        self.alternative_cancelled = True
        self.render()

    def return_from_alternatives(self):
        if self.alternative_cancelled:
            self.navigate("productos")
            return
        self.current_route = "detalle"
        self.render()

    def return_to_product(self):
        if self.selected_product:
            self.current_route = "detalle"
            self.render()
            return
        self.navigate("productos")

    def open_delivery_location(self, order_id=None):
        self.location_selection_order_id = order_id
        if order_id is not None:
            self.selected_delivery_location = self.delivery_locations.get(order_id)
        self.delivery_location_draft = self.selected_delivery_location
        self.current_route = "seleccionar_entrega"
        self.render()

    def select_delivery_point(self, coordinates):
        self.delivery_location_draft = coordinates
        self.render()

    def cancel_delivery_location(self):
        if self.location_selection_order_id is not None:
            self.selected_delivery_location = None
            self.current_route = "pedidos"
        else:
            self.current_route = "revisar_pedido"
        self.delivery_location_draft = None
        self.location_selection_order_id = None
        self.render()

    def use_delivery_location(self):
        if self.delivery_location_draft is None:
            return
        self.selected_delivery_location = self.delivery_location_draft
        if self.location_selection_order_id is None:
            self.delivery_location_draft = None
            self.current_route = "revisar_pedido"
            self.render()
            return

        order_id = self.location_selection_order_id
        self.delivery_locations[order_id] = self.selected_delivery_location
        self.tracking_routes[order_id] = self.routing_service.route_for(
            self.selected_delivery_location
        )
        self.tracking_progress[order_id] = 0
        self.selected_order_id = order_id
        self.delivery_location_draft = None
        self.location_selection_order_id = None
        self.current_route = "tracking"
        self.render()

    def confirm_real_order(self):
        if (
            not self.selected_product
            or self.selected_quantity < 1
            or not self.usuario_autenticado
            or self.selected_delivery_location is None
        ):
            self.page.open(
                ft.SnackBar(
                    ft.Text("Selecciona una ubicación de entrega antes de confirmar."),
                    bgcolor=ERROR,
                )
            )
            return

        self.afnd_integration.confirm_order()
        if self.selected_supply_symbol:
            result = self.alternative_orders_service.create_order(
                product=self.selected_product,
                username=self.usuario_autenticado,
                quantity=self.selected_quantity,
                source_symbol=self.selected_supply_symbol,
            )
        else:
            result = self.orders_service.create_order(
                products=self.productos,
                username=self.usuario_autenticado,
                product_id=self.selected_product["id"],
                quantity=self.selected_quantity,
            )
        if not result.success or not result.order or result.order.estado_afnd != "q5":
            self.page.open(ft.SnackBar(ft.Text(result.message), bgcolor=ERROR))
            return

        self.delivery_locations[result.order.id_pedido] = self.selected_delivery_location
        self.tracking_routes[result.order.id_pedido] = self.routing_service.route_for(
            self.selected_delivery_location
        )
        self.tracking_progress[result.order.id_pedido] = 0
        if self.selected_supply_source:
            self.order_supply_sources[result.order.id_pedido] = self.selected_supply_source
        self.afnd_integration.start_tracking()
        self.current_route = "pedidos"
        self.selected_product = None
        self.selected_quantity = 1
        self.selected_delivery_location = None
        self.delivery_location_draft = None
        self.alternative_availability = None
        self.selected_supply_symbol = None
        self.selected_supply_source = None
        self.alternative_cancelled = False
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
        if order.id_pedido not in self.tracking_routes:
            self.selected_order_id = order.id_pedido
            self.open_delivery_location(order.id_pedido)
            return
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
        route_result = self.tracking_routes.get(order.id_pedido)
        if not route_result:
            return
        last_index = len(route_result.simulation_points) - 1
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
        route_result = self.tracking_routes.get(order.id_pedido) if order else None
        last_index = len(route_result.simulation_points) - 1 if route_result else -1
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
        if self.current_route in {"perfil", "alternativas", "revisar_pedido", "seleccionar_entrega", "tracking"}:
            self.current_route = "inicio"
        self.selected_product = None
        self.selected_order_id = None
        self.selected_quantity = 1
        self.selected_delivery_location = None
        self.delivery_location_draft = None
        self.location_selection_order_id = None
        self.delivery_locations.clear()
        self.tracking_routes.clear()
        self.tracking_progress.clear()
        self.alternative_availability = None
        self.selected_supply_symbol = None
        self.selected_supply_source = None
        self.alternative_cancelled = False
        self.order_supply_sources.clear()
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
