"""Estado en memoria del flujo AFND generado por la tienda."""

from dataclasses import dataclass

from .afnd import AFND, AFNDResult


@dataclass(frozen=True)
class StoreEvent:
    symbol: str
    description: str
    active_states: frozenset[str]


@dataclass(frozen=True)
class RealFlowSnapshot:
    name: str
    events: tuple[StoreEvent, ...]
    result: AFNDResult

    @property
    def chain(self):
        return "-".join(event.symbol for event in self.events)


class AutomataSession:
    """Conserva únicamente en memoria el último flujo real de GamerGear."""

    def __init__(self):
        self.machine = AFND()
        self.flow_name = "Sesión iniciada"
        self.events = []

    def start_flow(self, name):
        self.flow_name = name
        self.events = []
        self.machine.reset()
        return self.snapshot()

    def record(self, symbol, description):
        result = self.machine.process_symbol(symbol)
        self.events.append(
            StoreEvent(
                symbol=symbol,
                description=description,
                active_states=result.active_states,
            )
        )
        return result

    def snapshot(self):
        return RealFlowSnapshot(
            name=self.flow_name,
            events=tuple(self.events),
            result=self.machine.result(),
        )
