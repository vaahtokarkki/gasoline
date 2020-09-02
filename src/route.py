import requests
import json

from .settings import BING_KEY

BASE_URL = 'http://dev.virtualearth.net/REST/v1/Routes'


def _get_url_params(start, end):
    return {
        "wayPoint.1": start,
        "wayPoint.2": end,
        "key": BING_KEY
    }


def get_route(start, end, cache):
    """ Return distance (km) and duration (min) from start location to end location """
    route = cache.get_route_from_cache(start, end)
    if route:
        return route

    resp = requests.get(BASE_URL, params=_get_url_params(start, end))
    if resp.status_code != 200:
        print("ERR", resp.status_code)
        return None, None
    data = json.loads(resp.content)
    route_data = data["resourceSets"][0]["resources"][0]

    distance = route_data["travelDistance"]
    duration = route_data["travelDuration"]/60

    cache.add_route_to_cache(start, end, distance, duration)

    return distance, duration
