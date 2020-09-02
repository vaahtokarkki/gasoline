import json
import os
import sys
from datetime import datetime

CACHE_EXPIRY = 7  # Days


class Cache(object):
    def __init__(self):
        self.routes = self._read_cache('routes.json')
        self.prices = self._read_cache('prices.txt')

    def _get_cache_path(self, file):
        main_path = os.path.abspath(sys.modules['__main__'].__file__)
        path = "/".join(main_path.split("/")[:-1])
        return f'{path}/data/{file}'

    def _read_cache(self, file):
        try:
            with open(self._get_cache_path(file), mode='r') as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def get_route_from_cache(self, start, end):
        if f'{start}-{end}' not in self.routes:
            return None

        now = datetime.now()

        route = self.routes.get(f'{start}-{end}')
        route_timestamp = datetime.fromisoformat(route.get("timestamp"))
        if (now - route_timestamp).days >= CACHE_EXPIRY:
            return None
        return route.get("distance"), route.get("duration")

    def add_route_to_cache(self, start, end, distance, duration):
        now = datetime.now().isoformat()

        self.routes[f'{start}-{end}'] = {
            "distance": distance,
            "duration": duration,
            "timestamp": now
        }

    def write_cache(self):
        with open(self._get_cache_path("routes.json"), 'w') as outfile:
            json.dump(self.routes, outfile)
