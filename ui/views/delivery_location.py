import flet as ft
import flet_map as fmap

from services.routing_service import GAMERGEAR_STORE_LABEL, GAMERGEAR_STORE_LOCATION
from ui.theme import BORDER, PRIMARY, SECONDARY, SURFACE, SURFACE_ELEVATED, TEXT_PRIMARY, TEXT_SECONDARY


ESRI_TILE_URL = (
    "https://server.arcgisonline.com/ArcGIS/rest/services/"
    "World_Street_Map/MapServer/tile/{z}/{y}/{x}"
)


def _point(coordinates):
    return fmap.MapLatitudeLongitude(*coordinates)


def _marker(coordinates, icon, color, tooltip):
    return fmap.Marker(
        coordinates=_point(coordinates),
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


def format_location(coordinates):
    if not coordinates:
        return "Sin ubicación seleccionada"
    return f"Punto seleccionado · {coordinates[0]:.5f}, {coordinates[1]:.5f}"


def build_delivery_location_view(selected_location, on_select, on_cancel, on_use, layout_mode="wide"):
    markers = [
        _marker(
            GAMERGEAR_STORE_LOCATION,
            ft.Icons.STORE_ROUNDED,
            SECONDARY,
            GAMERGEAR_STORE_LABEL,
        )
    ]
    if selected_location:
        markers.append(
            _marker(
                selected_location,
                ft.Icons.LOCATION_ON_ROUNDED,
                PRIMARY,
                "Ubicación de entrega seleccionada",
            )
        )

    def select_point(event):
        coordinates = event.coordinates
        on_select((float(coordinates.latitude), float(coordinates.longitude)))

    delivery_map = fmap.Map(
        initial_center=_point(selected_location or GAMERGEAR_STORE_LOCATION),
        initial_zoom=14,
        min_zoom=3,
        max_zoom=19,
        interaction_configuration=fmap.MapInteractionConfiguration(flags=fmap.MapInteractiveFlag.ALL),
        on_tap=select_point,
        layers=[
            fmap.TileLayer(url_template=ESRI_TILE_URL),
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

    return ft.Column(
        controls=[
            ft.TextButton(
                "Volver al resumen",
                icon=ft.Icons.ARROW_BACK_ROUNDED,
                on_click=lambda _: on_cancel(),
            ),
            ft.Text("Seleccionar ubicación de entrega", size=30, color=TEXT_PRIMARY, weight=ft.FontWeight.BOLD),
            ft.Text(
                "Haz clic o toca el mapa para colocar el marcador. Puedes cambiarlo antes de confirmar.",
                size=12,
                color=TEXT_SECONDARY,
            ),
            ft.Container(
                bgcolor=SURFACE_ELEVATED,
                border=ft.border.all(1, BORDER),
                border_radius=18,
                padding=12,
                content=ft.Column(
                    controls=[
                        ft.Container(
                            height=520 if layout_mode == "wide" else 390,
                            border_radius=14,
                            clip_behavior=ft.ClipBehavior.HARD_EDGE,
                            content=delivery_map,
                        ),
                        ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.STORE_ROUNDED, size=16, color=SECONDARY),
                                ft.Text(GAMERGEAR_STORE_LABEL, size=11, color=TEXT_SECONDARY),
                            ],
                            wrap=True,
                        ),
                        ft.Container(
                            bgcolor=SURFACE,
                            border=ft.border.all(1, PRIMARY if selected_location else BORDER),
                            border_radius=12,
                            padding=12,
                            content=ft.Row(
                                controls=[
                                    ft.Icon(
                                        ft.Icons.LOCATION_ON_ROUNDED,
                                        color=PRIMARY if selected_location else TEXT_SECONDARY,
                                    ),
                                    ft.Text(
                                        format_location(selected_location),
                                        size=12,
                                        color=TEXT_PRIMARY if selected_location else TEXT_SECONDARY,
                                    ),
                                ],
                                wrap=True,
                            ),
                        ),
                        ft.ResponsiveRow(
                            controls=[
                                ft.Container(
                                    col={"xs": 12, "sm": 6},
                                    content=ft.OutlinedButton(
                                        "Cancelar",
                                        width=float("inf"),
                                        on_click=lambda _: on_cancel(),
                                    ),
                                ),
                                ft.Container(
                                    col={"xs": 12, "sm": 6},
                                    content=ft.FilledButton(
                                        "Usar esta ubicación",
                                        icon=ft.Icons.CHECK_CIRCLE_ROUNDED,
                                        width=float("inf"),
                                        disabled=selected_location is None,
                                        on_click=lambda _: on_use(),
                                        style=ft.ButtonStyle(bgcolor=PRIMARY, color="#031018"),
                                    ),
                                ),
                            ],
                            spacing=10,
                            run_spacing=10,
                        ),
                    ],
                    spacing=10,
                ),
            ),
        ],
        spacing=10,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )
