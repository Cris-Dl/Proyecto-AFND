import unittest

from automata.afnd import AFND
from ui.theme import ERROR, PRIMARY, SECONDARY, SUCCESS
from ui.views.afnd_visualizer import STATE_LABELS, _active_state_chips, _state_node


def chip_labels(active_states):
    row = _active_state_chips(active_states)
    return [control.content.value for control in row.controls[1:]]


class AFNDVisualizerTests(unittest.TestCase):
    def test_three_nondeterministic_states_have_three_active_chips(self):
        result = AFND().process_string("I-P-D")
        chips = _active_state_chips(result.active_states)
        self.assertEqual(
            [control.content.value for control in chips.controls[1:]],
            ["q7 Otra sucursal", "q8 Bodega", "q9 Proveedor"],
        )
        self.assertTrue(chips.wrap)
        for state in result.active_states:
            node = _state_node(state, result.active_states)
            self.assertEqual(node.border.top.color, PRIMARY)
            self.assertEqual(node.border.top.width, 2)

    def test_replay_steps_rebuild_chips_from_current_active_states(self):
        machine = AFND()
        machine.prepare("I-P-D")
        expected = [
            ["q2 Autenticado"],
            ["q3 Disponibilidad"],
            ["q7 Otra sucursal", "q8 Bodega", "q9 Proveedor"],
        ]
        for labels in expected:
            result = machine.step()
            self.assertEqual(chip_labels(result.active_states), labels)

    def test_initial_state_keeps_purple_badge_without_active_border(self):
        node = _state_node("q0", frozenset())
        identifier = node.content.controls[0].controls[0]
        badge = node.content.controls[2].controls[0]
        self.assertEqual(identifier.color, SECONDARY)
        self.assertNotEqual(node.border.top.color, PRIMARY)
        self.assertEqual(badge.content.value, "Inicial")
        self.assertEqual(badge.content.color, SECONDARY)

    def test_inactive_regular_state_identifier_remains_readable(self):
        node = _state_node("q1", frozenset())
        identifier = node.content.controls[0].controls[0]
        self.assertEqual(identifier.color, "#A9B8C9")
        self.assertEqual(node.height, 92)

    def test_acceptance_and_rejection_keep_semantic_badges(self):
        cases = (("q6", "Aceptación", SUCCESS), ("q10", "Rechazo", ERROR))
        for state, label, color in cases:
            with self.subTest(state=state):
                node = _state_node(state, frozenset({state}))
                identifier = node.content.controls[0].controls[0]
                badge = node.content.controls[2].controls[0]
                self.assertEqual(node.border.top.color, PRIMARY)
                self.assertEqual(identifier.color, PRIMARY)
                self.assertEqual(badge.content.value, label)
                self.assertEqual(badge.content.color, color)
                self.assertEqual(chip_labels({state}), [f"{state} {STATE_LABELS[state]}"])


if __name__ == "__main__":
    unittest.main()
