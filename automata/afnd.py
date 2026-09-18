"""Implementación pura del AFND formal de GamerGear."""

from dataclasses import dataclass
from typing import Iterable


ALPHABET = frozenset({"C", "I", "P", "D", "S", "B", "V", "G", "R", "E", "X"})
STATES = frozenset(f"q{index}" for index in range(11))
INITIAL_STATE = "q0"
ACCEPTING_STATE = "q6"
REJECTING_STATE = "q10"

TRANSITIONS = {
    ("q0", "C"): frozenset({"q1"}),
    ("q0", "I"): frozenset({"q2"}),
    ("q1", "I"): frozenset({"q2"}),
    ("q2", "P"): frozenset({"q3"}),
    ("q3", "G"): frozenset({"q4"}),
    ("q3", "D"): frozenset({"q7", "q8", "q9"}),
    ("q7", "S"): frozenset({"q3"}),
    ("q8", "B"): frozenset({"q3"}),
    ("q9", "V"): frozenset({"q3"}),
    ("q3", "X"): frozenset({"q10"}),
    ("q7", "X"): frozenset({"q10"}),
    ("q8", "X"): frozenset({"q10"}),
    ("q9", "X"): frozenset({"q10"}),
    ("q4", "R"): frozenset({"q5"}),
    ("q5", "R"): frozenset({"q5"}),
    ("q5", "E"): frozenset({"q6"}),
    # X representa cancelación o finalización del proceso sin solución.
    ("q5", "X"): frozenset({"q10"}),
}


@dataclass(frozen=True)
class TransitionStep:
    """Un paso procesado, conservando los conjuntos antes y después."""

    index: int
    symbol: str
    source_states: frozenset[str]
    target_states: frozenset[str]


@dataclass(frozen=True)
class AFNDResult:
    """Instantánea inmutable del resultado actual del motor."""

    symbols: tuple[str, ...]
    active_states: frozenset[str]
    history: tuple[TransitionStep, ...]
    paths: tuple[tuple[str, ...], ...]
    accepted: bool
    rejected: bool
    invalid_symbol: str | None
    empty: bool


def parse_symbols(sequence: str | Iterable[str]) -> tuple[str, ...]:
    """Acepta cadenas como ``I-P-D``, ``IPD`` o iterables de símbolos."""

    if isinstance(sequence, str):
        return tuple(character.upper() for character in sequence if character.isalpha())
    return tuple(str(symbol).strip().upper() for symbol in sequence if str(symbol).strip())


class AFND:
    """AFND sin dependencias de interfaz, base de datos ni red."""

    def __init__(self):
        self.reset()

    def reset(self):
        self.active_states = {INITIAL_STATE}
        self.current_symbol = None
        self.symbols = []
        self.history = []
        self.paths = [(INITIAL_STATE,)]
        self.invalid_symbol = None
        self._pending_symbols = ()
        self._pending_index = 0
        return self.result()

    def prepare(self, sequence: str | Iterable[str]):
        """Reinicia y prepara una cadena para avanzar con :meth:`step`."""

        self.reset()
        self._pending_symbols = parse_symbols(sequence)
        return self.result()

    @property
    def has_pending(self):
        return self._pending_index < len(self._pending_symbols) and self.invalid_symbol is None

    def process_symbol(self, symbol: str):
        normalized = str(symbol).strip().upper()
        if normalized not in ALPHABET:
            self.current_symbol = normalized
            self.invalid_symbol = normalized
            return self.result()

        source_states = frozenset(self.active_states)
        next_states = set()
        next_paths = []

        for path in self.paths:
            source = path[-1]
            for target in sorted(TRANSITIONS.get((source, normalized), frozenset())):
                next_states.add(target)
                next_paths.append((*path, target))

        self.current_symbol = normalized
        self.symbols.append(normalized)
        self.active_states = next_states
        self.paths = next_paths
        self.history.append(
            TransitionStep(
                index=len(self.history),
                symbol=normalized,
                source_states=source_states,
                target_states=frozenset(next_states),
            )
        )
        return self.result()

    def step(self):
        """Procesa un símbolo de la cadena preparada y devuelve una instantánea."""

        if not self.has_pending:
            return self.result()
        symbol = self._pending_symbols[self._pending_index]
        self._pending_index += 1
        return self.process_symbol(symbol)

    def process_string(self, sequence: str | Iterable[str], reset=True):
        if reset:
            self.prepare(sequence)
            while self.has_pending:
                self.step()
            return self.result()

        for symbol in parse_symbols(sequence):
            result = self.process_symbol(symbol)
            if result.invalid_symbol:
                break
        return self.result()

    def result(self):
        accepted = ACCEPTING_STATE in self.active_states and self.invalid_symbol is None
        return AFNDResult(
            symbols=tuple(self.symbols),
            active_states=frozenset(self.active_states),
            history=tuple(self.history),
            paths=tuple(self.paths),
            accepted=accepted,
            rejected=not accepted,
            invalid_symbol=self.invalid_symbol,
            empty=not self.symbols and self.invalid_symbol is None,
        )
