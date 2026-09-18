import flet as ft

from ui.theme import BORDER, PRIMARY, SURFACE_ELEVATED, TEXT_PRIMARY, TEXT_SECONDARY


def build_status_panel(icon, title, message, color=PRIMARY, action_label=None, on_action=None):
    controls = [
        ft.Icon(icon, size=34, color=color),
        ft.Text(title, size=18, weight=ft.FontWeight.W_600, color=TEXT_PRIMARY),
        ft.Text(message, size=13, color=TEXT_SECONDARY, text_align=ft.TextAlign.CENTER),
    ]

    if action_label and on_action:
        controls.append(
            ft.OutlinedButton(
                action_label,
                icon=ft.Icons.REFRESH_ROUNDED,
                on_click=lambda _: on_action(),
            )
        )

    return ft.Container(
        content=ft.Column(
            controls=controls,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        ),
        bgcolor=SURFACE_ELEVATED,
        border=ft.border.all(1, BORDER),
        border_radius=18,
        padding=28,
        alignment=ft.alignment.center,
    )
