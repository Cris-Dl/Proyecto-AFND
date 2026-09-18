import flet as ft
import flet_map as fmap

from services.routing_service import GAMERGEAR_STORE_LABEL
from ui.theme import (
    BORDER,
    ERROR,
    PRIMARY,
    SECONDARY,
    SUCCESS,
    SURFACE,
    SURFACE_ELEVATED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)


ESRI_TILE_URL = (
    "https://server.arcgisonline.com/ArcGIS/rest/services/"
    "World_Street_Map/MapServer/tile/{z}/{y}/{x}"
)


def _point(latitude, longitude):
    return fmap.MapLatitudeLongitude(latitude, longitude)


def _marker(coordinates, icon, color, tooltip):
    return fmap.Marker(
        coordinates=_point(*coordinates),
        width=46,
        height=46,
        content=ft.Container(
            bgcolor=SURFACE_ELEVATED,
            border=ft.border.all(2, color),
            border_radius=23,
            alignment=ft.alignment.center,
            tooltip=tooltip,
            content=ft.Icon(icon, color=color, size=25),
        ),
    )


def _timeline_item(label, state):
    if state == "done":
        icon, color = ft.Icons.CHECK_CIRCLE_ROUNDED, SUCCESS
    elif state == "active":
        icon, color = ft.Icons.RADIO_BUTTON_CHECKED_ROUNDED, PRIMARY
    else:
        icon, color = ft.Icons.RADIO_BUTTON_UNCHECKED_ROUNDED, TEXT_SECONDARY
    return ft.Row(
        controls=[
            ft.Icon(icon, size=18, color=color),
            ft.Text(label, size=12, color=TEXT_PRIMARY if state != "pending" else TEXT_SECONDARY),
        ],
        spacing=9,
    )


def build_tracking_view(
    order,
    route_result,
    progress_index,
    on_back,
    on_advance,
    on_deliver,
    on_cancel,
    layout_mode="wide",
):
    route_coordinates = route_result.primary.coordinates
    simulation_points = route_result.simulation_points
    last_index = len(simulation_points) - 1
    progress_index = min(max(0, progress_index), last_index)
    delivered = order.estado_afnd == "q6"
    cancelled = order.estado_afnd == "q10"
    in_transit = order.estado_afnd == "q5"
    at_destination = progress_index == last_index
    remaining_steps = last_index - progress_index
    remaining_seconds = route_result.primary.duration_seconds * remaining_steps / max(1, last_index)
    remaining_minutes = max(1, round(remaining_seconds / 60))
    eta = (
        "Entregado"
        if delivered
        else "Seguimiento finalizado"
        if cancelled
        else "Llegando"
        if at_destination
        else f"{remaining_minutes} min aprox."
    )

    route_points = [_point(*coordinates) for coordinates in route_coordinates]
    origin = route_coordinates[0]
    destination = route_coordinates[-1]
    center = ((origin[0] + destination[0]) / 2, (origin[1] + destination[1]) / 2)
    markers = [
        _marker(origin, ft.Icons.STORE_ROUNDED, SECONDARY, GAMERGEAR_STORE_LABEL),
        _marker(destination, ft.Icons.LOCATION_ON_ROUNDED, SUCCESS, "Punto de entrega seleccionado"),
        _marker(
            simulation_points[progress_index],
            ft.Icons.LOCAL_SHIPPING_ROUNDED,
            SUCCESS if delivered else ERROR if cancelled else PRIMARY,
            "Vehículo simulado",
        ),
    ]

    tracking_map = fmap.Map(
        initial_center=_point(*center),
        initial_zoom=14,
        min_zoom=3,
        max_zoom=19,
        interaction_configuration=fmap.MapInteractionConfiguration(flags=fmap.MapInteractiveFlag.ALL),
        layers=[
            fmap.TileLayer(url_template=ESRI_TILE_URL),
            fmap.PolylineLayer(
                polylines=[
                    fmap.PolylineMarker(
                        coordinates=route_points,
                        color=PRIMARY,
                        border_color="#083344",
                        stroke_width=6,
                        border_stroke_width=2,
                    )
                ]
            ),
            fmap.MarkerLayer(markers=markers),
            fmap.RichAttribution(
                attributions=[
                    fmap.TextSourceAttribution(
                        text="Esri and data providers",
                        prepend_copyright=True,
                    )
                ]
            ),
        ],
        expand=True,
    )

    route_label = "Ruta calculada sobre red vial" if route_result.is_road_route else "Ruta simulada"
    alternatives_label = (
        f" · {len(route_result.alternatives)} rutas encontradas"
        if route_result.is_road_route and len(route_result.alternatives) > 1
        else ""
    )
    map_panel = ft.Container(
        col={"xs": 12, "lg": 8},
        bgcolor=SURFACE_ELEVATED,
        border=ft.border.all(1, BORDER),
        border_radius=18,
        padding=12,
        content=ft.Column(
            controls=[
                ft.Container(
                    height=520 if layout_mode == "wide" else 380,
                    border_radius=14,
                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                    content=tracking_map,
                ),
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.PUBLIC_ROUNDED, size=14, color=TEXT_SECONDARY),
                        ft.Text(
                            "Tiles © Esri · Sources: Esri, HERE, Garmin, USGS, "
                            "© OpenStreetMap contributors and the GIS User Community",
                            size=9,
                            color=TEXT_SECONDARY,
                        ),
                        ft.Container(expand=True),
                        ft.Text(f"{route_label}{alternatives_label}", size=10, color=TEXT_SECONDARY),
                    ],
                    wrap=True,
                ),
            ],
            spacing=8,
        ),
    )

    information_panel = ft.Container(
        col={"xs": 12, "lg": 4},
        bgcolor=SURFACE_ELEVATED,
        border=ft.border.all(1, BORDER),
        border_radius=18,
        padding=20,
        content=ft.Column(
            controls=[
                ft.Text("SIMULACIÓN DE SEGUIMIENTO", size=10, color=PRIMARY, weight=ft.FontWeight.BOLD),
                ft.Text(f"Pedido #{order.id_pedido}", size=21, color=TEXT_PRIMARY, weight=ft.FontWeight.BOLD),
                ft.Text(order.producto, size=13, color=TEXT_SECONDARY),
                ft.Container(
                    bgcolor=SURFACE,
                    border_radius=13,
                    padding=14,
                    content=ft.Row(
                        controls=[
                            ft.Icon(
                                ft.Icons.CHECK_CIRCLE_ROUNDED
                                if delivered
                                else ft.Icons.CANCEL_ROUNDED
                                if cancelled
                                else ft.Icons.LOCAL_SHIPPING_ROUNDED,
                                color=SUCCESS if delivered else ERROR if cancelled else PRIMARY,
                            ),
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        "Entregado" if delivered else "Pedido cancelado" if cancelled else "En ruta",
                                        size=15,
                                        color=SUCCESS if delivered else ERROR if cancelled else PRIMARY,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.Text(f"ETA aproximada: {eta}", size=11, color=TEXT_SECONDARY),
                                    ft.Text(
                                        "El seguimiento de este pedido ha finalizado.",
                                        size=10,
                                        color=TEXT_SECONDARY,
                                        visible=cancelled,
                                    ),
                                    ft.Text(
                                        f"Distancia: {route_result.primary.distance_meters / 1000:.1f} km",
                                        size=11,
                                        color=TEXT_SECONDARY,
                                    ),
                                ],
                                spacing=2,
                            ),
                        ],
                        spacing=10,
                    ),
                ),
                ft.Text(route_label, size=11, color=PRIMARY if route_result.is_road_route else TEXT_SECONDARY),
                ft.Text("Progreso", size=12, color=TEXT_PRIMARY, weight=ft.FontWeight.W_600),
                ft.ProgressBar(
                    value=1 if delivered else progress_index / max(1, last_index),
                    color=SUCCESS if delivered else ERROR if cancelled else PRIMARY,
                    bgcolor=BORDER,
                ),
                ft.Column(
                    controls=(
                        [
                            _timeline_item("Pedido confirmado", "done"),
                            _timeline_item("Preparando envío", "done"),
                            ft.Row(
                                controls=[
                                    ft.Icon(ft.Icons.CANCEL_ROUNDED, size=18, color=ERROR),
                                    ft.Text("Pedido cancelado", size=12, color=ERROR),
                                ],
                                spacing=9,
                            ),
                        ]
                        if cancelled
                        else [
                            _timeline_item("Pedido confirmado", "done"),
                            _timeline_item("Preparando envío", "done"),
                            _timeline_item("En ruta", "done" if delivered else "active"),
                            _timeline_item(
                                "Entregado",
                                "done" if delivered else "active" if at_destination else "pending",
                            ),
                        ]
                    ),
                    spacing=9,
                ),
                ft.Divider(color=BORDER, height=16),
                ft.FilledButton(
                    "Simular avance",
                    icon=ft.Icons.NAVIGATION_ROUNDED,
                    width=float("inf"),
                    visible=in_transit,
                    disabled=at_destination,
                    on_click=lambda _: on_advance(),
                    style=ft.ButtonStyle(bgcolor=PRIMARY, color="#031018"),
                ),
                ft.FilledButton(
                    "Confirmar entrega",
                    icon=ft.Icons.INVENTORY_ROUNDED,
                    width=float("inf"),
                    visible=in_transit,
                    disabled=not at_destination,
                    on_click=lambda _: on_deliver(),
                    style=ft.ButtonStyle(bgcolor=SUCCESS, color="#031018"),
                ),
                ft.OutlinedButton(
                    "Cancelar pedido",
                    icon=ft.Icons.CANCEL_OUTLINED,
                    width=float("inf"),
                    visible=in_transit,
                    on_click=lambda _: on_cancel(order.id_pedido),
                    style=ft.ButtonStyle(color=ERROR, side=ft.BorderSide(1, ERROR)),
                ),
            ],
            spacing=12,
        ),
    )

    return ft.Column(
        controls=[
            ft.TextButton(
                "Volver a Pedidos",
                icon=ft.Icons.ARROW_BACK_ROUNDED,
                on_click=lambda _: on_back(),
            ),
            ft.Text("Rastrear pedido", size=30, color=TEXT_PRIMARY, weight=ft.FontWeight.BOLD),
            ft.Text(
                "Simulación de seguimiento: no representa una ubicación GPS en tiempo real.",
                size=11,
                color=TEXT_SECONDARY,
            ),
            ft.ResponsiveRow(
                controls=[map_panel, information_panel],
                spacing=14,
                run_spacing=14,
            ),
        ],
        spacing=10,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )
