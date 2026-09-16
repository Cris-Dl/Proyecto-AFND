import unittest

from services.orders_service import OrderRecord
from services.routing_service import GAMERGEAR_STORE_LOCATION, build_fallback_route
from ui.theme import ERROR
from ui.views.orders import _order_card
from ui.views.tracking import build_tracking_view


class CancellationViewsTests(unittest.TestCase):
    def order(self, state):
        return OrderRecord(1, "ana", "Producto", 1, 10.0, 10.0, state)

    def test_orders_actions_are_only_visible_for_q5(self):
        for state, expected in (("q5", True), ("q6", False), ("q10", False)):
            with self.subTest(state=state):
                card = _order_card(self.order(state), lambda _id: None, lambda _id: None)
                track_button = card.content.controls[-2]
                cancel_button = card.content.controls[-1]
                self.assertEqual(track_button.visible, expected)
                self.assertEqual(cancel_button.visible, expected)

    def test_cancelled_order_card_uses_friendly_red_status(self):
        card = _order_card(self.order("q10"), lambda _id: None, lambda _id: None)
        header = card.content.controls[0]
        status = header.controls[1].controls[1]
        self.assertEqual(status.value, "Cancelado")
        self.assertEqual(status.color, ERROR)

    def test_cancelled_tracking_hides_all_actions(self):
        route = build_fallback_route(GAMERGEAR_STORE_LOCATION, (14.8400, -91.5258))
        view = build_tracking_view(
            order=self.order("q10"),
            route_result=route,
            progress_index=2,
            on_back=lambda: None,
            on_advance=lambda: None,
            on_deliver=lambda: None,
            on_cancel=lambda _id: None,
        )
        information_panel = view.controls[-1].controls[1]
        controls = information_panel.content.controls
        self.assertFalse(controls[-3].visible)
        self.assertFalse(controls[-2].visible)
        self.assertFalse(controls[-1].visible)


if __name__ == "__main__":
    unittest.main()
