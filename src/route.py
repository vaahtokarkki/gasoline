import json
import logging

import requests

from .settings import BING_KEY


log = logging.getLogger("rich")
log.setLevel(logging.ERROR)

BASE_URL = 'http://dev.virtualearth.net/REST/v1/'


def _get_url_params_for_route(start, end):
    return {
        "wayPoint.1": start,
        "wayPoint.2": end,
        "key": BING_KEY,
        "routeAttributes": "routePath"
    }


def _get_url_params_for_geocode(address):
    return {
        "key": BING_KEY,
    }


class Router(object):
    def __init__(self):
        super().__init__()
        self.count = 0

    def get_route(self, start, end, cache):
        """
        Return distance (km) and duration (min) and collection of coordinates as
        route path from start location to end location
        """
        route = cache.get_route_from_cache(start, end)
        if route:
            return route

        resp = requests.get(f'{BASE_URL}/Routes/',
                            params=_get_url_params_for_route(start, end))
        self.count += 1
        if resp.status_code != 200:
            log.error(f"Error {resp.status_code} when getting route {start} - {end}")
            return None, None, None
        data = json.loads(resp.content)
        route_data = data["resourceSets"][0]["resources"][0]

        distance = route_data["travelDistance"]
        duration = route_data["travelDuration"] / 60
        route_path = route_data["routePath"]["line"]["coordinates"]

        cache.add_route_to_cache(start, end, distance, duration, route_path)
        return distance, duration, route_path

    def get_point(self, address, cache=None):
        point = cache.get_point_from_cache(address) if cache else None
        if point:
            return point

        resp = requests.get(f'{BASE_URL}/Locations/{address}',
                            params=_get_url_params_for_geocode(address))
        self.count += 1
        if resp.status_code != 200:
            print("ERR", resp.status_code, address)
            return None, None
        data = json.loads(resp.content)
        coordinates = data["resourceSets"][0]["resources"][0]["point"]["coordinates"]
        lat = coordinates[0]
        lon = coordinates[1]
        if cache:
            cache.add_point_to_cache((lat, lon), address)
        return lat, lon
