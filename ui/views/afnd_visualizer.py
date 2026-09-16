import flet as ft

from automata.afnd import (
    ACCEPTING_STATE,
    INITIAL_STATE,
    REJECTING_STATE,
    AFND,
    parse_symbols,
)
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


STATE_LABELS = {
    "q0": "Inicio",
    "q1": "Crear cuenta",
    "q2": "Autenticado",
    "q3": "Disponibilidad",
    "q4": "Confirmado",
    "q5": "Rastreo",
    "q6": "Entregado",
    "q7": "Otra sucursal",
    "q8": "Bodega",
    "q9": "Proveedor",
    "q10": "Cancelado",
}

TRANSITION_LABELS = (
    "q0 —C→ q1    q0 —I→ q2    q1 —I→ q2",
    "q2 —P→ q3    q3 —G→ q4    q4 —R→ q5",
    "q3 —D→ {q7, q8, q9}",
    "q7 —S→ q3    q8 —B→ q3    q9 —V→ q3",
    "q3/q7/q8/q9 —X→ q10",
    "q5 —R→ q5    q5 —E→ q6",
)


def _format_states(states):
    return "{" + ", ".join(sorted(states, key=lambda state: int(state[1:]))) + "}"


def _format_history(history):
    if not history:
        return "Sin transiciones procesadas."
    return "\n".join(
        f"{_format_states(step.source_states)} —{step.symbol}→ {_format_states(step.target_states)}"
        for step in history
    )


def _format_paths(paths):
    if not paths:
        return "Sin rutas activas."
    return "\n".join(" → ".join(path) for path in paths)


def _result_label(result):
    if result.invalid_symbol:
        return f"Símbolo inválido: {result.invalid_symbol}", ERROR
    if result.empty:
        return "Cadena vacía", TEXT_SECONDARY
    if result.accepted:
        return "Aceptada", SUCCESS
    return "No aceptada", WARNING


def _state_node(state, active):
    is_active = state in active
    if is_active:
        color, background = PRIMARY, "#123747"
    elif state == ACCEPTING_STATE:
        color, background = SUCCESS, SURFACE
    elif state == REJECTING_STATE:
        color, background = ERROR, SURFACE
    elif state == INITIAL_STATE:
        color, background = SECONDARY, SURFACE
    else:
        color, background = BORDER, SURFACE

    badges = []
    if state == INITIAL_STATE:
        badges.append("inicial")
    if state == ACCEPTING_STATE:
        badges.append("aceptación")
    if state == REJECTING_STATE:
        badges.append("rechazo")

    return ft.Container(
        col={"xs": 6, "sm": 4, "md": 3},
        height=92,
        padding=11,
        bgcolor=background,
        border=ft.border.all(2 if is_active else 1, color),
        border_radius=13,
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text(state, size=16, color=color, weight=ft.FontWeight.BOLD),
                        ft.Container(expand=True),
                        ft.Icon(
                            ft.Icons.RADIO_BUTTON_CHECKED if is_active else ft.Icons.CIRCLE_OUTLINED,
                            size=15,
                            color=color,
                        ),
                    ],
                    spacing=5,
                ),
                ft.Text(STATE_LABELS[state], size=11, color=TEXT_PRIMARY, max_lines=2),
                ft.Text(" · ".join(badges), size=9, color=color, visible=bool(badges)),
            ],
            spacing=4,
        ),
    )


def _diagram(active_states):
    return ft.Container(
        bgcolor=SURFACE_ELEVATED,
        border=ft.border.all(1, BORDER),
        border_radius=18,
        padding=16,
        content=ft.Column(
            controls=[
                ft.Text("Diagrama de estados", size=18, color=TEXT_PRIMARY, weight=ft.FontWeight.BOLD),
                ft.Text(
                    "Los estados con borde cyan están activos simultáneamente.",
                    size=11,
                    color=TEXT_SECONDARY,
                ),
                ft.ResponsiveRow(
                    controls=[_state_node(f"q{index}", active_states) for index in range(11)],
                    spacing=9,
                    run_spacing=9,
                ),
                ft.Divider(color=BORDER, height=18),
                ft.Text("Transiciones", size=13, color=TEXT_PRIMARY, weight=ft.FontWeight.W_600),
                *[ft.Text(label, size=11, color=TEXT_SECONDARY) for label in TRANSITION_LABELS],
            ],
            spacing=8,
        ),
    )


def _information_panel(title, subtitle, result, extra_controls=None):
    status, status_color = _result_label(result)
    return ft.Container(
        bgcolor=SURFACE_ELEVATED,
        border=ft.border.all(1, BORDER),
        border_radius=18,
        padding=16,
        content=ft.Column(
            controls=[
                ft.Text(title, size=18, color=TEXT_PRIMARY, weight=ft.FontWeight.BOLD),
                ft.Text(subtitle, size=11, color=TEXT_SECONDARY),
                *(extra_controls or []),
                ft.Divider(color=BORDER, height=16),
                ft.Text("Cadena", size=11, color=TEXT_SECONDARY),
                ft.Text(" → ".join(result.symbols) or "∅", size=17, color=PRIMARY, weight=ft.FontWeight.BOLD),
                ft.Text("Estados activos", size=11, color=TEXT_SECONDARY),
                ft.Text(_format_states(result.active_states), size=15, color=TEXT_PRIMARY),
                ft.Text(status, size=12, color=status_color, weight=ft.FontWeight.W_600),
                ft.Divider(color=BORDER, height=16),
                ft.Text("Historial", size=12, color=TEXT_PRIMARY, weight=ft.FontWeight.W_600),
                ft.Text(_format_history(result.history), size=11, color=TEXT_SECONDARY),
                ft.Text("Rutas posibles", size=12, color=TEXT_PRIMARY, weight=ft.FontWeight.W_600),
                ft.Text(_format_paths(result.paths), size=11, color=TEXT_SECONDARY),
            ],
            spacing=7,
        ),
    )


def build_afnd_visualizer(session, on_back, layout_mode="wide"):
    mode = {"value": "real"}
    replay_machine = AFND()
    replay_started = {"value": False}
    manual_machine = AFND()
    manual_prepared = {"symbols": None}

    content_host = ft.Container()
    real_button = ft.FilledButton("Flujo real", icon=ft.Icons.STORE_ROUNDED)
    manual_button = ft.OutlinedButton("Cadena manual", icon=ft.Icons.EDIT_NOTE_ROUNDED)

    def refresh():
        real_button.style = ft.ButtonStyle(
            bgcolor=PRIMARY if mode["value"] == "real" else SURFACE,
            color="#031018" if mode["value"] == "real" else TEXT_SECONDARY,
        )
        manual_button.style = ft.ButtonStyle(
            bgcolor=SECONDARY if mode["value"] == "manual" else SURFACE,
            color=TEXT_PRIMARY if mode["value"] == "manual" else TEXT_SECONDARY,
        )
        content_host.content = build_real_mode() if mode["value"] == "real" else build_manual_mode()
        try:
            root.update()
        except (AssertionError, RuntimeError):
            pass

    def set_mode(selected):
        mode["value"] = selected
        refresh()

    def start_replay(_):
        snapshot = session.snapshot()
        replay_machine.prepare(tuple(event.symbol for event in snapshot.events))
        replay_started["value"] = True
        refresh()

    def next_replay(_):
        replay_machine.step()
        refresh()

    def build_real_mode():
        snapshot = session.snapshot()
        displayed_result = replay_machine.result() if replay_started["value"] else snapshot.result
        event_lines = [
            ft.Text(f"{event.symbol} · {event.description}", size=10, color=TEXT_SECONDARY)
            for event in snapshot.events
        ] or [ft.Text("Todavía no hay eventos reales.", size=11, color=TEXT_SECONDARY)]
        controls = [
            ft.Text(f"Último flujo: {snapshot.name}", size=11, color=SECONDARY),
            *event_lines,
            ft.ResponsiveRow(
                controls=[
                    ft.Container(
                        col={"xs": 12, "sm": 6},
                        content=ft.OutlinedButton(
                            "Reproducir flujo",
                            icon=ft.Icons.REPLAY_ROUNDED,
                            width=float("inf"),
                            on_click=start_replay,
                        ),
                    ),
                    ft.Container(
                        col={"xs": 12, "sm": 6},
                        content=ft.FilledButton(
                            "Paso siguiente",
                            icon=ft.Icons.SKIP_NEXT_ROUNDED,
                            width=float("inf"),
                            disabled=not replay_started["value"] or not replay_machine.has_pending,
                            on_click=next_replay,
                        ),
                    ),
                ],
                spacing=8,
                run_spacing=8,
            ),
        ]
        return _mode_layout(
            _diagram(displayed_result.active_states),
            _information_panel(
                "Flujo real",
                "Generado automáticamente por acciones de GamerGear.",
                displayed_result,
                controls,
            ),
        )

    manual_input = ft.TextField(
        label="Cadena",
        hint_text="Ejemplo: I-P-D",
        border_color=BORDER,
        focused_border_color=PRIMARY,
        bgcolor=SURFACE,
    )

    def process_manual(_):
        manual_machine.process_string(manual_input.value or "")
        manual_prepared["symbols"] = None
        refresh()

    def step_manual(_):
        symbols = parse_symbols(manual_input.value or "")
        if manual_prepared["symbols"] != symbols:
            manual_machine.prepare(symbols)
            manual_prepared["symbols"] = symbols
        manual_machine.step()
        refresh()

    def reset_manual(_):
        manual_machine.reset()
        manual_prepared["symbols"] = None
        refresh()

    def build_manual_mode():
        result = manual_machine.result()
        controls = [
            manual_input,
            ft.ResponsiveRow(
                controls=[
                    ft.Container(
                        col={"xs": 12, "sm": 4},
                        content=ft.FilledButton(
                            "Procesar",
                            icon=ft.Icons.PLAY_ARROW_ROUNDED,
                            width=float("inf"),
                            on_click=process_manual,
                        ),
                    ),
                    ft.Container(
                        col={"xs": 12, "sm": 4},
                        content=ft.OutlinedButton(
                            "Paso a paso",
                            icon=ft.Icons.SKIP_NEXT_ROUNDED,
                            width=float("inf"),
                            on_click=step_manual,
                        ),
                    ),
                    ft.Container(
                        col={"xs": 12, "sm": 4},
                        content=ft.TextButton(
                            "Reiniciar",
                            icon=ft.Icons.RESTART_ALT_ROUNDED,
                            width=float("inf"),
                            on_click=reset_manual,
                        ),
                    ),
                ],
                spacing=7,
                run_spacing=7,
            ),
        ]
        return _mode_layout(
            _diagram(result.active_states),
            _information_panel(
                "Cadena manual",
                "Este análisis está aislado y no modifica el flujo real de la tienda.",
                result,
                controls,
            ),
        )

    def _mode_layout(diagram, information):
        return ft.ResponsiveRow(
            controls=[
                ft.Container(col={"xs": 12, "lg": 8}, content=diagram),
                ft.Container(col={"xs": 12, "lg": 4}, content=information),
            ],
            spacing=14,
            run_spacing=14,
        )

    real_button.on_click = lambda _: set_mode("real")
    manual_button.on_click = lambda _: set_mode("manual")

    root = ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.TextButton(
                        "Volver",
                        icon=ft.Icons.ARROW_BACK_ROUNDED,
                        on_click=lambda _: on_back(),
                    ),
                    ft.Container(expand=True),
                ]
            ),
            ft.Text("Visualizador AFND", size=30, color=TEXT_PRIMARY, weight=ft.FontWeight.BOLD),
            ft.Text(
                "Observa el flujo real o analiza una cadena académica sin alterar la tienda.",
                size=12,
                color=TEXT_SECONDARY,
            ),
            ft.ResponsiveRow(
                controls=[
                    ft.Container(col={"xs": 12, "sm": 6}, content=real_button),
                    ft.Container(col={"xs": 12, "sm": 6}, content=manual_button),
                ],
                spacing=8,
                run_spacing=8,
            ),
            content_host,
        ],
        spacing=10,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )
    content_host.content = build_real_mode()
    return root
