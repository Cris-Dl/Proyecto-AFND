"""Cálculo de rutas de demostración sin persistir ubicaciones personales."""

from dataclasses import dataclass
from math import asin, cos, radians, sin, sqrt

import requests


OSRM_BASE_URL = "https://router.project-osrm.org"
OSRM_USER_AGENT = "GamerGear-AFND/1.0"
OSRM_TIMEOUT_SECONDS = 8

# Sucursal ficticia usada únicamente como origen de la demostración.
GAMERGEAR_STORE_LOCATION = (14.8335, -91.5188)
GAMERGEAR_STORE_LABEL = "Sucursal GamerGear Xela — ubicación simulada"


@dataclass(frozen=True)
class RouteAlternative:
    coordinates: tuple[tuple[float, float], ...]
    distance_meters: float
    duration_seconds: float


@dataclass(frozen=True)
class RouteResult:
    alternatives: tuple[RouteAlternative, ...]
    simulation_points: tuple[tuple[float, float], ...]
    source: str

    @property
    def primary(self):
        return self.alternatives[0]

    @property
    def is_road_route(self):
        return self.source == "osrm"


def build_osrm_url(origin, destination):
    origin_latitude, origin_longitude = origin
    destination_latitude, destination_longitude = destination
    return (
        f"{OSRM_BASE_URL}/route/v1/driving/"
        f"{origin_longitude},{origin_latitude};"
        f"{destination_longitude},{destination_latitude}"
    )


def sample_route_points(coordinates, maximum_points=8):
    """Reduce la geometría conservando puntos originales y ambos extremos."""

    points = tuple(coordinates)
    if len(points) <= maximum_points:
        return points

    last_index = len(points) - 1
    indexes = [round(position * last_index / (maximum_points - 1)) for position in range(maximum_points)]
    return tuple(points[index] for index in indexes)


def _haversine_distance_meters(origin, destination):
    origin_latitude, origin_longitude = map(radians, origin)
    destination_latitude, destination_longitude = map(radians, destination)
    latitude_delta = destination_latitude - origin_latitude
    longitude_delta = destination_longitude - origin_longitude
    value = (
        sin(latitude_delta / 2) ** 2
        + cos(origin_latitude) * cos(destination_latitude) * sin(longitude_delta / 2) ** 2
    )
    return 6_371_000 * 2 * asin(sqrt(value))


def build_fallback_route(origin, destination):
    """Crea una ruta visual local dependiente del destino seleccionado."""

    origin_latitude, origin_longitude = origin
    destination_latitude, destination_longitude = destination
    coordinates = tuple(
        (
            origin_latitude + (destination_latitude - origin_latitude) * step / 6,
            origin_longitude + (destination_longitude - origin_longitude) * step / 6,
        )
        for step in range(7)
    )
    distance = _haversine_distance_meters(origin, destination)
    alternative = RouteAlternative(
        coordinates=coordinates,
        distance_meters=distance,
        duration_seconds=max(60, distance / 6.94),
    )
    return RouteResult(
        alternatives=(alternative,),
        simulation_points=coordinates,
        source="simulated",
    )


class RoutingService:
    def __init__(self, http_client=requests):
        self.http_client = http_client

    def route_for(self, destination, origin=GAMERGEAR_STORE_LOCATION):
        try:
            response = self.http_client.get(
                build_osrm_url(origin, destination),
                params={
                    "overview": "full",
                    "geometries": "geojson",
                    "steps": "false",
                    "alternatives": "true",
                },
                headers={"User-Agent": OSRM_USER_AGENT},
                timeout=OSRM_TIMEOUT_SECONDS,
            )
            if response.status_code != 200:
                return build_fallback_route(origin, destination)

            payload = response.json()
            if payload.get("code") != "Ok" or not payload.get("routes"):
                return build_fallback_route(origin, destination)

            alternatives = []
            for route in payload["routes"]:
                raw_coordinates = route.get("geometry", {}).get("coordinates", [])
                coordinates = tuple(
                    (float(latitude), float(longitude))
                    for longitude, latitude in raw_coordinates
                )
                if len(coordinates) < 2:
                    continue
                alternatives.append(
                    RouteAlternative(
                        coordinates=coordinates,
                        distance_meters=float(route.get("distance", 0)),
                        duration_seconds=float(route.get("duration", 0)),
                    )
                )

            if not alternatives:
                return build_fallback_route(origin, destination)

            return RouteResult(
                alternatives=tuple(alternatives),
                simulation_points=sample_route_points(alternatives[0].coordinates),
                source="osrm",
            )
        except (requests.RequestException, ValueError, TypeError, KeyError):
            return build_fallback_route(origin, destination)
