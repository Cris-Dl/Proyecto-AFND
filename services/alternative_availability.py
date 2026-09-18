"""Disponibilidad alternativa simulada y determinista para la demostración AFND."""

from dataclasses import dataclass


ALTERNATIVE_SOURCES = {
    "S": ("q7", "Otra sucursal"),
    "B": ("q8", "Bodega"),
    "V": ("q9", "Proveedor"),
}
SUPPORTED_SCENARIOS = frozenset((*ALTERNATIVE_SOURCES, "X"))


DEMO_AFND_PRODUCTS = (
    {
        "id": 9001,
        "nombre": "Demo AFND - Otra sucursal",
        "precio": 649.00,
        "categoria": "Demo AFND",
        "existencia": 0,
        "thumbnail": None,
        "demo_afnd": True,
        "alternative_scenario": "S",
    },
    {
        "id": 9002,
        "nombre": "Demo AFND - Bodega",
        "precio": 899.00,
        "categoria": "Demo AFND",
        "existencia": 0,
        "thumbnail": None,
        "demo_afnd": True,
        "alternative_scenario": "B",
    },
    {
        "id": 9003,
        "nombre": "Demo AFND - Proveedor",
        "precio": 549.00,
        "categoria": "Demo AFND",
        "existencia": 0,
        "thumbnail": None,
        "demo_afnd": True,
        "alternative_scenario": "V",
    },
    {
        "id": 9004,
        "nombre": "Demo AFND - Sin solución",
        "precio": 749.00,
        "categoria": "Demo AFND",
        "existencia": 0,
        "thumbnail": None,
        "demo_afnd": True,
        "alternative_scenario": "X",
    },
)


@dataclass(frozen=True)
class AvailabilityOption:
    symbol: str
    state: str
    label: str
    available: bool


@dataclass(frozen=True)
class AlternativeAvailability:
    scenario: str
    options: tuple[AvailabilityOption, ...]

    @property
    def has_solution(self):
        return self.scenario in ALTERNATIVE_SOURCES

    @property
    def source_label(self):
        return ALTERNATIVE_SOURCES[self.scenario][1] if self.has_solution else None


def get_demo_products():
    """Devuelve copias para mantener la colección local separada del catálogo remoto."""

    return [dict(product) for product in DEMO_AFND_PRODUCTS]


def scenario_for_product(product):
    """Resuelve una simulación reproducible sin modificar el producto ni usar azar."""

    explicit_scenario = str(product.get("alternative_scenario", "")).upper()
    if explicit_scenario in SUPPORTED_SCENARIOS:
        return explicit_scenario

    # Para productos remotos agotados, el ID selecciona siempre el mismo escenario.
    scenarios = ("S", "B", "V", "X")
    return scenarios[abs(int(product["id"])) % len(scenarios)]


def evaluate_alternative_availability(product):
    if int(product.get("existencia", 0)) > 0:
        raise ValueError("La disponibilidad alternativa sólo aplica a productos sin stock local.")

    scenario = scenario_for_product(product)
    return AlternativeAvailability(
        scenario=scenario,
        options=tuple(
            AvailabilityOption(
                symbol=symbol,
                state=state,
                label=label,
                available=scenario == symbol,
            )
            for symbol, (state, label) in ALTERNATIVE_SOURCES.items()
        ),
    )
