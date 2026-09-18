import flet as ft

from ui.theme import BORDER, PRIMARY, SURFACE, SURFACE_ELEVATED, TEXT_PRIMARY, TEXT_SECONDARY


def build_profile_view(usuario, on_login, on_logout, on_open_afnd):
    authenticated = bool(usuario)
    action = (
        ft.OutlinedButton(
            "Cerrar sesión",
            icon=ft.Icons.LOGOUT_ROUNDED,
            on_click=lambda _: on_logout(),
            style=ft.ButtonStyle(color=TEXT_SECONDARY, side=ft.BorderSide(1, BORDER)),
        )
        if authenticated
        else ft.FilledButton(
            "Iniciar sesión",
            icon=ft.Icons.LOGIN_ROUNDED,
            on_click=lambda _: on_login(),
            style=ft.ButtonStyle(bgcolor=PRIMARY, color="#031018"),
        )
    )

    profile_card = ft.Container(
        width=560,
        bgcolor=SURFACE_ELEVATED,
        border=ft.border.all(1, BORDER),
        border_radius=22,
        padding=ft.padding.symmetric(horizontal=28, vertical=30),
        content=ft.Column(
                controls=[
                    ft.Container(
                        width=82,
                        height=82,
                        border_radius=41,
                        bgcolor=SURFACE,
                        border=ft.border.all(1, BORDER),
                        alignment=ft.alignment.center,
                        content=ft.Icon(
                            ft.Icons.PERSON_ROUNDED if authenticated else ft.Icons.PERSON_OFF_ROUNDED,
                            size=42,
                            color=PRIMARY if authenticated else TEXT_SECONDARY,
                        ),
                    ),
                    ft.Text(
                        "Sesión activa" if authenticated else "Perfil",
                        size=11,
                        color=PRIMARY,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Text(
                        usuario if authenticated else "Aún no has iniciado sesión",
                        size=26,
                        color=TEXT_PRIMARY,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        "Tu sesión se conserva únicamente mientras utilizas la aplicación."
                        if authenticated
                        else "Inicia sesión para acceder a tu perfil de GamerGear.",
                        size=13,
                        color=TEXT_SECONDARY,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(height=4),
                    action,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
                tight=True,
        ),
    )

    tools_card = ft.Container(
        width=560,
        bgcolor=SURFACE_ELEVATED,
        border=ft.border.all(1, BORDER),
        border_radius=18,
        padding=20,
        content=ft.Column(
            controls=[
                ft.Text("Herramientas", size=11, color=PRIMARY, weight=ft.FontWeight.BOLD),
                ft.Text("Visualizador AFND", size=19, color=TEXT_PRIMARY, weight=ft.FontWeight.W_600),
                ft.Text(
                    "Consulta el flujo formal generado por la tienda o procesa una cadena manual.",
                    size=12,
                    color=TEXT_SECONDARY,
                ),
                ft.OutlinedButton(
                    "Abrir visualizador",
                    icon=ft.Icons.ACCOUNT_TREE_ROUNDED,
                    on_click=lambda _: on_open_afnd(),
                    style=ft.ButtonStyle(color=PRIMARY, side=ft.BorderSide(1, BORDER)),
                ),
            ],
            spacing=8,
        ),
    )

    return ft.Column(
        controls=[profile_card, tools_card],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=14,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )
