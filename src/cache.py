import json
import os
import sys
from datetime import datetime


ROUTE_CACHE_EXPIRY = 7  # Days

CACHE_FOLDER = 'data'


class Cache(object):
    def __init__(self, prefix, name):
        self.prefix = prefix
        self.file = name
        self.cache = self._read_cache()

    def _get_cache_folder_path(self):
        main_path = os.path.abspath(sys.modules['__main__'].__file__)
        path = "/".join(main_path.split("/")[:-1])
        return f'{path}/{CACHE_FOLDER}'

    def _get_cache_path(self):
        path = self._get_cache_folder_path()
        return f'{path}/{self.prefix}_{self.file}'

    def _read_cache(self):
        try:
            with open(self._get_cache_path(), mode='r') as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def write_cache(self):
        if not os.path.exists(self._get_cache_folder_path()):
            os.makedirs(self._get_cache_folder_path())
        with open(self._get_cache_path(), 'w+') as outfile:
            json.dump(self.cache, outfile)

    def update(self, obj):
        self.cache.update(obj)

    def get(self, key):
        return self.cache.get(key)


class RouteCache(object):
    def __init__(self, prefix):
        self.prefix = prefix
        self.routes = Cache(prefix, 'routes.json')

    def get_route_from_cache(self, start, end):
        route = self.routes.get(f'{start}-{end}')
        if not route:
            return None

        now = datetime.now()

        route_timestamp = datetime.fromisoformat(route.get("timestamp"))
        if (now - route_timestamp).days >= ROUTE_CACHE_EXPIRY:
            return None
        return route.get("distance"), route.get("duration"), route.get("route_path")

    def add_route_to_cache(self, start, end, distance, duration, route_path):
        payload = {f'{start}-{end}': {
            "distance": distance,
            "duration": duration,
            "timestamp": datetime.now().isoformat(),
            "route_path": route_path
        }}
        self.routes.update(payload)

    def add_point_to_cache(self, point, address):
        lat, lon = point
        payload = {address: {
            "lat": lat,
            "lon": lon,
            "timestamp": datetime.now().isoformat()
        }}
        self.routes.update(payload)

    def get_point_from_cache(self, address):
        point = self.routes.get(address)
        if not point:
            return None

        now = datetime.now()
        point_timestamp = datetime.fromisoformat(point.get("timestamp"))
        if (now - point_timestamp).days >= ROUTE_CACHE_EXPIRY:
            return None
        return float(point.get("lat")), float(point.get("lon"))

    def write_cache(self):
        self.routes.write_cache()
