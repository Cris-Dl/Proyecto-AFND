import flet as ft


BACKGROUND = "#07111F"
SURFACE = "#0D1B2A"
SURFACE_ELEVATED = "#122235"
PRIMARY = "#22D3EE"
SECONDARY = "#8B5CF6"
TEXT_PRIMARY = "#F8FAFC"
TEXT_SECONDARY = "#94A3B8"
SUCCESS = "#34D399"
WARNING = "#FBBF24"
ERROR = "#FB7185"
BORDER = "#1E344A"


def configure_page(page: ft.Page):
    page.title = "GamerGear"
    page.bgcolor = BACKGROUND
    page.padding = 0
    page.spacing = 0
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = ft.Theme(
        color_scheme_seed=PRIMARY,
        font_family="Segoe UI",
        use_material3=True,
    )
