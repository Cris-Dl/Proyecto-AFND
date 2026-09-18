import unittest

import requests

from services.routing_service import (
    GAMERGEAR_STORE_LOCATION,
    OSRM_TIMEOUT_SECONDS,
    OSRM_USER_AGENT,
    RoutingService,
    build_fallback_route,
    build_osrm_url,
    sample_route_points,
)


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self.payload = payload
        self.status_code = status_code

    def json(self):
        return self.payload


class FakeHttpClient:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.calls = []

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        if self.error:
            raise self.error
        return self.response


class RoutingServiceTests(unittest.TestCase):
    def setUp(self):
        self.destination = (14.8400, -91.5258)
        self.primary_geojson = [
            [-91.5188, 14.8335],
            [-91.5195, 14.8341],
            [-91.5202, 14.8348],
            [-91.5210, 14.8357],
            [-91.5220, 14.8368],
            [-91.5231, 14.8377],
            [-91.5240, 14.8385],
            [-91.5250, 14.8393],
            [-91.5258, 14.8400],
        ]

    def test_osrm_request_and_geojson_coordinate_conversion(self):
        response = FakeResponse(
            {
                "code": "Ok",
                "routes": [
                    {
                        "geometry": {"coordinates": self.primary_geojson},
                        "distance": 2300.0,
                        "duration": 510.0,
                    },
                    {
                        "geometry": {"coordinates": self.primary_geojson[:2]},
                        "distance": 2500.0,
                        "duration": 560.0,
                    },
                ],
            }
        )
        client = FakeHttpClient(response=response)

        result = RoutingService(http_client=client).route_for(self.destination)

        self.assertTrue(result.is_road_route)
        self.assertEqual(len(result.alternatives), 2)
        self.assertEqual(result.primary.coordinates[0], GAMERGEAR_STORE_LOCATION)
        self.assertEqual(result.primary.coordinates[-1], self.destination)
        self.assertEqual(
            client.calls[0][0],
            build_osrm_url(GAMERGEAR_STORE_LOCATION, self.destination),
        )
        self.assertEqual(client.calls[0][1]["headers"], {"User-Agent": OSRM_USER_AGENT})
        self.assertEqual(client.calls[0][1]["timeout"], OSRM_TIMEOUT_SECONDS)
        self.assertEqual(
            client.calls[0][1]["params"],
            {
                "overview": "full",
                "geometries": "geojson",
                "steps": "false",
                "alternatives": "true",
            },
        )

    def test_sampled_vehicle_points_belong_to_osrm_geometry(self):
        geometry = tuple((latitude, longitude) for longitude, latitude in self.primary_geojson)

        sampled = sample_route_points(geometry, maximum_points=8)

        self.assertEqual(len(sampled), 8)
        self.assertEqual(sampled[0], geometry[0])
        self.assertEqual(sampled[-1], geometry[-1])
        self.assertTrue(all(point in geometry for point in sampled))

    def test_osrm_failure_uses_location_aware_fallback(self):
        client = FakeHttpClient(error=requests.Timeout("sin conexión"))

        result = RoutingService(http_client=client).route_for(self.destination)

        self.assertFalse(result.is_road_route)
        self.assertEqual(result.source, "simulated")
        self.assertEqual(result.primary.coordinates[0], GAMERGEAR_STORE_LOCATION)
        self.assertEqual(result.primary.coordinates[-1], self.destination)
        self.assertEqual(len(result.simulation_points), 7)

    def test_non_ok_or_empty_response_uses_fallback(self):
        for payload in ({"code": "NoRoute", "routes": []}, {"code": "Ok", "routes": []}):
            with self.subTest(payload=payload):
                result = RoutingService(http_client=FakeHttpClient(FakeResponse(payload))).route_for(
                    self.destination
                )
                self.assertFalse(result.is_road_route)

    def test_fallback_never_discards_selected_destination(self):
        result = build_fallback_route(GAMERGEAR_STORE_LOCATION, self.destination)
        self.assertEqual(result.simulation_points[0], GAMERGEAR_STORE_LOCATION)
        self.assertEqual(result.simulation_points[-1], self.destination)


if __name__ == "__main__":
    unittest.main()
