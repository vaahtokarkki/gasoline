from functools import partial

import pandas as pd
import pyproj
from rich.box import SIMPLE
from rich.live_render import LiveRender
from rich.panel import Panel
from shapely.geometry import LineString, Point
from shapely.ops import transform

from .cache import RouteCache
from .route import Router
from .UI import console


PROJECTION = partial(
    pyproj.transform,
    pyproj.Proj('EPSG:4326'),
    pyproj.Proj('EPSG:32633')
)


class PriceCalculator(object):
    def __init__(self, location, amount, consumption):
        super().__init__()
        self.location = location
        self.amount = amount
        self.consumption = consumption
        self.route_cache = RouteCache('data')
        self.router = Router()
        self.pane = LiveRender("")
        console.print(self.pane.position_cursor())
        console.print(self.pane)

    def update_count(self, count):
        self.pane.set_renderable(Panel(f'Api requests made: {count}', box=SIMPLE))
        console.print(self.pane.position_cursor())
        console.print(self.pane)

    def calc(self, row):
        lat = row["lat"]
        lon = row["lon"]
        name = row["Name"]
        price = row["95E10 Price"]

        route_query = f"{lat},{lon}" if lat and lon else f'{name} Helsinki'
        distance, duration, route_path = self.router.get_route(
            self.location, route_query, self.route_cache
        )
        self.update_count(self.router.count)

        total_price = ((self.consumption / 100) * distance * 2 * price) + self.amount \
            * price if price and distance else None
        gas_price = self.amount * price if price else None
        return pd.Series({
            "Distance": f'{round(distance * 2)}km',
            "Duration": f'{round(duration * 2)}min',
            "Total price": total_price,
            "40l price": gas_price
        })

    def cal_via(self, row, shortest_distance, shortest_duration):
        lat = row["lat"]
        lon = row["lon"]
        price = row["95E10 Price"]
        origin, destination = self.location

        station = f"{lat},{lon}"
        distance_from_origin, duration_from_origin, _ = \
            self.router.get_route(origin, station, self.route_cache)
        distance_from_station, duration_from_station, _ = \
            self.router.get_route(station, destination, self.route_cache)
        self.update_count(self.router.count)

        full_distance = distance_from_origin + distance_from_station
        full_duration = round(duration_from_origin + duration_from_station)
        total_price = ((self.consumption / 100) * full_distance * 2 * price) \
            + self.amount * price if price and full_distance else None
        gas_price = self.amount * price if price else None
        return pd.Series({
            "Distance": f'+{round((full_distance-shortest_distance)*1000)}m',
            "Duration": f'+{round(full_duration-shortest_duration)}min',
            "Total price": total_price,
            "40l price": gas_price
        })

    def calc_via_route(self, stations):
        start, end = self.location
        distance, duration, route_path = \
            self.router.get_route(start, end, self.route_cache)
        self.update_count(self.router.count)

        line = _project(LineString(route_path))
        notnull_stations = stations.merge(stations.apply(
            lambda row: pd.Series({"point": _project(Point(row["lat"], row["lon"]))}),
            axis=1
        ), left_index=True, right_index=True)

        stations_on_path = notnull_stations[notnull_stations.apply(
            lambda x: line.distance(x["point"]) <= 1000, axis=1
        )]
        return {"distance": round(distance), "duration": round(duration)}, \
            stations_on_path.merge(stations_on_path.apply(lambda x: self.cal_via(
                x, distance, duration), axis=1), left_index=True, right_index=True)

    def calculate_prices(self, stations):
        route_data, updated_stations = (None, stations.merge(
            stations.apply(self.calc, axis=1), left_index=True, right_index=True
        )) if not isinstance(self.location, tuple) else self.calc_via_route(stations)
        self.route_cache.write_cache()
        updated_stations = updated_stations \
            .round({"Total price": 2, "40l price": 2, "95E10 Price": 3}) \
            .sort_values("Total price")

        return route_data, updated_stations


def _project(element):
    return transform(PROJECTION, element)
