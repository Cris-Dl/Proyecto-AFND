import flet as ft

from login import VistaLogin
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
    WARNING,
)


def _text_field(label, icon, password=False):
    return ft.TextField(
        label=label,
        prefix_icon=icon,
        password=password,
        can_reveal_password=password,
        border_radius=14,
        border_color=BORDER,
        focused_border_color=PRIMARY,
        bgcolor=SURFACE,
        color=TEXT_PRIMARY,
        label_style=ft.TextStyle(color=TEXT_SECONDARY),
    )


class GamerGearLoginView(VistaLogin):
    """Presentación GamerGear que reutiliza la lógica original de VistaLogin."""

    def __init__(self, page, on_auth_success=None, on_registration_success=None):
        self.active_view = "menu"
        self.face_status_text = None
        self.face_status_icon = None
        self.scroll_host = None
        super().__init__(
            page,
            on_auth_success=on_auth_success,
            on_registration_success=on_registration_success,
        )

    def actualizar_pantalla(self):
        try:
            self.update()
        except (AssertionError, RuntimeError):
            pass

    def mostrar_mensaje(self, texto, color):
        if self.active_view == "face" and self.face_status_text and self.face_status_icon:
            if color == ft.Colors.GREEN:
                estado, icono, estado_color = "Éxito", ft.Icons.CHECK_CIRCLE_ROUNDED, SUCCESS
            elif color == ft.Colors.ORANGE:
                estado, icono, estado_color = "Advertencia", ft.Icons.WARNING_AMBER_ROUNDED, WARNING
            elif color == ft.Colors.RED:
                estado, icono, estado_color = "Error", ft.Icons.ERROR_OUTLINE_ROUNDED, ERROR
            else:
                estado, icono, estado_color = "Escaneando", ft.Icons.FACE_RETOUCHING_NATURAL, PRIMARY

            self.face_status_text.value = estado
            self.face_status_text.color = estado_color
            self.face_status_icon.name = icono
            self.face_status_icon.color = estado_color
            self.actualizar_pantalla()

        super().mostrar_mensaje(texto, color)

    def _set_card(self, eyebrow, title, subtitle, controls):
        self.limpiar_vista()
        self.controls.append(
            ft.Container(
                width=float("inf"),
                bgcolor=SURFACE_ELEVATED,
                border=ft.border.all(1, BORDER),
                border_radius=22,
                padding=ft.padding.symmetric(horizontal=26, vertical=24),
                content=ft.Column(
                    controls=[
                        ft.Text(eyebrow, size=10, color=PRIMARY, weight=ft.FontWeight.BOLD),
                        ft.Text(title, size=27, color=TEXT_PRIMARY, weight=ft.FontWeight.BOLD),
                        ft.Text(subtitle, size=13, color=TEXT_SECONDARY),
                        ft.Container(height=4),
                        *controls,
                    ],
                    spacing=12,
                ),
            )
        )
        self.actualizar_pantalla()
        if self.scroll_host:
            try:
                self.scroll_host.scroll_to(offset=0, duration=120)
            except (AssertionError, RuntimeError):
                pass

    def _method_card(self, icon, title, description, on_click, accent):
        return ft.Container(
            col={"xs": 12, "md": 6},
            bgcolor=SURFACE,
            border=ft.border.all(1, BORDER),
            border_radius=16,
            padding=18,
            on_click=on_click,
            content=ft.Column(
                controls=[
                    ft.Icon(icon, size=32, color=accent),
                    ft.Text(title, size=16, color=TEXT_PRIMARY, weight=ft.FontWeight.W_600),
                    ft.Text(description, size=12, color=TEXT_SECONDARY, max_lines=2),
                    ft.Row(
                        controls=[
                            ft.Text("Continuar", size=12, color=accent, weight=ft.FontWeight.W_600),
                            ft.Icon(ft.Icons.ARROW_FORWARD_ROUNDED, size=16, color=accent),
                        ],
                        spacing=6,
                    ),
                ],
                spacing=8,
            ),
        )

    def construir_menu_principal(self):
        self.active_view = "menu"
        methods = ft.ResponsiveRow(
            controls=[
                self._method_card(
                    ft.Icons.PASSWORD_ROUNDED,
                    "Usuario y contraseña",
                    "Accede con tus credenciales de GamerGear.",
                    lambda _: self.construir_vista_password(),
                    PRIMARY,
                ),
                self._method_card(
                    ft.Icons.FACE_RETOUCHING_NATURAL,
                    "Face ID",
                    "Verifica tu identidad mediante la cámara.",
                    lambda _: self.construir_vista_faceid(),
                    SECONDARY,
                ),
            ],
            spacing=14,
            run_spacing=14,
        )

        secondary_actions = ft.ResponsiveRow(
            controls=[
                ft.Container(
                    col={"xs": 12, "sm": 6},
                    content=ft.TextButton(
                        "Crear cuenta",
                        icon=ft.Icons.PERSON_ADD_ROUNDED,
                        on_click=lambda _: self.construir_vista_registro(),
                    ),
                ),
                ft.Container(
                    col={"xs": 12, "sm": 6},
                    content=ft.TextButton(
                        "Recuperar cuenta",
                        icon=ft.Icons.LOCK_RESET_ROUNDED,
                        on_click=lambda _: self.construir_vista_recuperar(),
                    ),
                ),
            ],
            spacing=4,
            run_spacing=2,
        )

        self._set_card(
            "ACCESO SEGURO",
            "Bienvenido a GamerGear",
            "Elige cómo quieres iniciar sesión.",
            [
                methods,
                ft.Divider(color=BORDER, height=18),
                secondary_actions,
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.SCIENCE_OUTLINED, size=15, color=TEXT_SECONDARY),
                        ft.TextButton(
                            "Huella digital · prototipo",
                            on_click=lambda _: super(GamerGearLoginView, self).construir_vista_huella(),
                            style=ft.ButtonStyle(color=TEXT_SECONDARY),
                        ),
                    ],
                    spacing=2,
                ),
            ],
        )

    def construir_vista_password(self):
        self.active_view = "password"
        self.user_input = _text_field("Usuario", ft.Icons.PERSON_OUTLINE_ROUNDED)
        self.pass_input = _text_field("Contraseña", ft.Icons.LOCK_OUTLINE_ROUNDED, password=True)

        self._set_card(
            "CREDENCIALES",
            "Iniciar sesión",
            "Ingresa tu usuario y contraseña para continuar.",
            [
                self.user_input,
                self.pass_input,
                ft.FilledButton(
                    "Entrar",
                    icon=ft.Icons.LOGIN_ROUNDED,
                    on_click=self.procesar_login_normal,
                    style=ft.ButtonStyle(
                        bgcolor=PRIMARY,
                        color="#031018",
                        padding=ft.padding.symmetric(horizontal=24, vertical=15),
                    ),
                ),
                ft.TextButton(
                    "Volver a métodos de acceso",
                    icon=ft.Icons.ARROW_BACK_ROUNDED,
                    on_click=lambda _: self.construir_menu_principal(),
                ),
            ],
        )

    def construir_vista_faceid(self):
        self.active_view = "face"
        self.face_status_icon = ft.Icon(ft.Icons.RADAR_ROUNDED, size=22, color=PRIMARY)
        self.face_status_text = ft.Text("Preparado", size=13, color=PRIMARY, weight=ft.FontWeight.W_600)

        visual = ft.Container(
            height=156,
            bgcolor=SURFACE,
            border=ft.border.all(1, BORDER),
            border_radius=18,
            alignment=ft.alignment.center,
            content=ft.Stack(
                controls=[
                    ft.Container(
                        width=112,
                        height=112,
                        border_radius=56,
                        bgcolor="#132D3B",
                        alignment=ft.alignment.center,
                        content=ft.Icon(ft.Icons.FACE_RETOUCHING_NATURAL, size=66, color=PRIMARY),
                    ),
                    ft.Container(
                        right=18,
                        top=16,
                        content=ft.Icon(ft.Icons.AUTO_AWESOME_ROUNDED, size=20, color=SECONDARY),
                    ),
                ]
            ),
        )

        status = ft.Container(
            bgcolor=SURFACE,
            border_radius=12,
            padding=ft.padding.symmetric(horizontal=14, vertical=10),
            content=ft.Row(controls=[self.face_status_icon, self.face_status_text], spacing=9),
        )

        self._set_card(
            "IDENTIDAD BIOMÉTRICA",
            "Face ID",
            "Coloca tu rostro frente a la cámara y mantén una iluminación uniforme.",
            [
                visual,
                status,
                ft.FilledButton(
                    "Iniciar escaneo",
                    icon=ft.Icons.CAMERA_ALT_ROUNDED,
                    on_click=self.procesar_login_faceid,
                    style=ft.ButtonStyle(
                        bgcolor=PRIMARY,
                        color="#031018",
                        padding=ft.padding.symmetric(horizontal=24, vertical=15),
                    ),
                ),
                ft.TextButton(
                    "Volver",
                    icon=ft.Icons.ARROW_BACK_ROUNDED,
                    on_click=lambda _: self.construir_menu_principal(),
                ),
            ],
        )

    def construir_vista_registro(self):
        self.active_view = "register"
        self.reg_nombre = _text_field("Nombre y apellido", ft.Icons.BADGE_OUTLINED)
        self.reg_correo = _text_field("Correo electrónico", ft.Icons.EMAIL_OUTLINED)
        self.reg_sexo = ft.Dropdown(
            label="Sexo",
            border_radius=14,
            border_color=BORDER,
            focused_border_color=PRIMARY,
            bgcolor=SURFACE,
            options=[ft.dropdown.Option("Masculino"), ft.dropdown.Option("Femenino")],
        )
        self.reg_telefono = _text_field("Teléfono", ft.Icons.PHONE_OUTLINED)
        self.reg_direccion = _text_field("Dirección de entrega", ft.Icons.LOCATION_ON_OUTLINED)
        self.reg_user = _text_field("Usuario", ft.Icons.PERSON_ADD_OUTLINED)
        self.reg_pass = _text_field("Contraseña", ft.Icons.LOCK_OUTLINE_ROUNDED, password=True)
        self.usar_face_id = ft.Switch(
            label="Registrar Face ID con la cámara",
            value=False,
            active_color=PRIMARY,
        )

        fields = ft.ResponsiveRow(
            controls=[
                ft.Container(col={"xs": 12, "md": 6}, content=self.reg_nombre),
                ft.Container(col={"xs": 12, "md": 6}, content=self.reg_correo),
                ft.Container(col={"xs": 12, "md": 6}, content=self.reg_sexo),
                ft.Container(col={"xs": 12, "md": 6}, content=self.reg_telefono),
                ft.Container(col=12, content=self.reg_direccion),
                ft.Container(col={"xs": 12, "md": 6}, content=self.reg_user),
                ft.Container(col={"xs": 12, "md": 6}, content=self.reg_pass),
            ],
            spacing=12,
            run_spacing=12,
        )

        self._set_card(
            "NUEVA CUENTA",
            "Crear cuenta",
            "Completa tus datos para registrarte en GamerGear.",
            [
                fields,
                ft.Container(
                    bgcolor=SURFACE,
                    border_radius=12,
                    padding=ft.padding.symmetric(horizontal=12, vertical=6),
                    content=self.usar_face_id,
                ),
                ft.FilledButton(
                    "Crear cuenta",
                    icon=ft.Icons.PERSON_ADD_ROUNDED,
                    on_click=self.guardar_cuenta,
                    style=ft.ButtonStyle(bgcolor=PRIMARY, color="#031018"),
                ),
                ft.TextButton(
                    "Volver",
                    icon=ft.Icons.ARROW_BACK_ROUNDED,
                    on_click=lambda _: self.construir_menu_principal(),
                ),
            ],
        )

    def construir_vista_recuperar(self):
        self.active_view = "recovery"
        self.rec_correo = _text_field("Correo registrado", ft.Icons.EMAIL_OUTLINED)

        self._set_card(
            "RECUPERACIÓN",
            "Recuperar cuenta",
            "Consulta las credenciales asociadas a tu correo registrado.",
            [
                self.rec_correo,
                ft.FilledButton(
                    "Recuperar datos",
                    icon=ft.Icons.LOCK_RESET_ROUNDED,
                    on_click=self.recuperar_cuenta,
                    style=ft.ButtonStyle(bgcolor=PRIMARY, color="#031018"),
                ),
                ft.TextButton(
                    "Volver",
                    icon=ft.Icons.ARROW_BACK_ROUNDED,
                    on_click=lambda _: self.construir_menu_principal(),
                ),
            ],
        )


def build_login_view(page, on_auth_success, on_registration_success, on_back):
    auth_view = GamerGearLoginView(
        page,
        on_auth_success=on_auth_success,
        on_registration_success=on_registration_success,
    )
    login_view = ft.Column(
        controls=[
            ft.TextButton(
                "Volver",
                icon=ft.Icons.ARROW_BACK_ROUNDED,
                on_click=lambda _: on_back(),
            ),
            ft.ResponsiveRow(
                controls=[
                    ft.Container(
                        col={"xs": 12, "md": 10, "lg": 8, "xl": 7},
                        content=auth_view,
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ],
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )
    auth_view.scroll_host = login_view
    return login_view
