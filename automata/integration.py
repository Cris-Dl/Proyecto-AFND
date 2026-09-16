"""Adaptador entre eventos reales de GamerGear y el motor formal."""

from .session import AutomataSession


class GamerGearAutomataIntegration:
    def __init__(self, session=None):
        self.session = session or AutomataSession()

    def account_created(self):
        self.session.start_flow("Creación de cuenta")
        return self.session.record("C", "Cuenta creada correctamente")

    def login_succeeded(self):
        if self.session.machine.active_states != {"q1"}:
            self.session.start_flow("Inicio de sesión")
        return self.session.record("I", "Autenticación correcta")

    def start_purchase(self):
        self.session.start_flow("Compra de producto disponible")
        self.session.record("I", "Sesión autenticada existente")
        return self.session.record("P", "Producto seleccionado para compra")

    def search_alternatives(self):
        self.session.start_flow("Búsqueda de alternativas")
        self.session.record("I", "Sesión autenticada existente")
        self.session.record("P", "Producto seleccionado para compra")
        return self.session.record("D", "Producto sin disponibilidad")

    def confirm_order(self):
        return self.session.record("G", "Pedido confirmado para la etapa previa al rastreo")

    def start_tracking(self):
        return self.session.record("R", "Pedido persistido e incorporado al rastreo")

    def resume_tracking(self):
        self.session.start_flow("Rastreo de pedido persistido")
        self.session.record("I", "Sesión autenticada existente")
        self.session.record("P", "Pedido persistido seleccionado")
        self.session.record("G", "Pedido confirmado previamente")
        return self.session.record("R", "Pedido recuperado en rastreo")

    def tracking_update(self):
        return self.session.record("R", "Actualización simulada de rastreo")

    def delivery_completed(self):
        return self.session.record("E", "Entrega persistente confirmada")

    def snapshot(self):
        return self.session.snapshot()
