import flet as ft

from login import VistaLogin
from ui.theme import TEXT_PRIMARY, TEXT_SECONDARY


class EmbeddedVistaLogin(VistaLogin):
    """Adapta la vista existente al montaje dentro del shell principal."""

    def actualizar_pantalla(self):
        try:
            self.update()
        except (AssertionError, RuntimeError):
            pass


def build_login_view(page, on_auth_success, on_back):
    return ft.Column(
        controls=[
            ft.TextButton(
                "Volver al inicio",
                icon=ft.Icons.ARROW_BACK_ROUNDED,
                on_click=lambda _: on_back(),
            ),
            ft.Text("Acceso a GamerGear", size=28, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
            ft.Text(
                "Utiliza los métodos de autenticación existentes.",
                size=13,
                color=TEXT_SECONDARY,
            ),
            ft.Container(height=8),
            ft.Container(
                content=EmbeddedVistaLogin(page, on_auth_success=on_auth_success),
                alignment=ft.alignment.top_center,
            ),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )
