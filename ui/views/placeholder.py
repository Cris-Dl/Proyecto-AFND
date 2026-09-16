import flet as ft

from ui.theme import BORDER, PRIMARY, SURFACE_ELEVATED, TEXT_PRIMARY, TEXT_SECONDARY


def build_placeholder_view(title, message, icon):
    return ft.Container(
        expand=True,
        alignment=ft.alignment.center,
        content=ft.Container(
            width=520,
            bgcolor=SURFACE_ELEVATED,
            border=ft.border.all(1, BORDER),
            border_radius=22,
            padding=34,
            content=ft.Column(
                controls=[
                    ft.Icon(icon, size=44, color=PRIMARY),
                    ft.Text(title, size=26, color=TEXT_PRIMARY, weight=ft.FontWeight.BOLD),
                    ft.Text(message, size=14, color=TEXT_SECONDARY, text_align=ft.TextAlign.CENTER),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
                tight=True,
            ),
        ),
    )
