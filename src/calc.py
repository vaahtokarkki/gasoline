from datetime import datetime
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
    def __init__(self, location, amount, consumption, distance, age):
        super().__init__()
        self.location = location
        self.amount = amount
        self.consumption = consumption
        self.distance = distance * 1000
        self.age = age
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
            f"{self.amount}l price": gas_price
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
        distance_delta = full_distance - shortest_distance
        total_price = ((self.consumption / 100) * distance_delta * 2 * price) \
            + self.amount * price if price and distance_delta is not None else None
        gas_price = self.amount * price if price else None
        return pd.Series({
            "Distance": f'+{round((distance_delta)*1000)}m',
            "Duration": f'+{round(full_duration-shortest_duration)}min',
            "Total price": total_price,
            "40l price": gas_price
        })

    def filter_stations(self, stations, filter_by_distance=False):
        notnull_stations = stations.merge(stations.apply(
            lambda row: pd.Series({"point": _project(Point(row["lat"], row["lon"]))}),
            axis=1
        ), left_index=True, right_index=True)
        now = datetime.now()
        notnull_stations = notnull_stations[notnull_stations.apply(
            lambda row: (now - row["Timestamp"]).days <= self.age, axis=1
        )]
        if filter_by_distance:
            lat, lon = self.router.get_point(self.location, self.route_cache)
            from_point = _project(Point(lat, lon))
            notnull_stations = notnull_stations[notnull_stations.apply(
                lambda row: row["point"].distance(from_point) <= self.distance, axis=1
            )]
        return notnull_stations

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
            lambda x: line.distance(x["point"]) <= self.distance, axis=1
        )]
        return {"distance": round(distance), "duration": round(duration)}, \
            stations_on_path.merge(stations_on_path.apply(lambda x: self.cal_via(
                x, distance, duration), axis=1), left_index=True, right_index=True)

    def calc_from_point(self, stations):
        filtered_stations = self.filter_stations(stations, filter_by_distance=True)
        return None, filtered_stations.merge(
            filtered_stations.apply(self.calc, axis=1), left_index=True, right_index=True
        )

    def calculate_prices(self, stations):
        route_data, updated_stations = self.calc_from_point(stations) \
            if not isinstance(self.location, tuple) else self.calc_via_route(stations)
        self.route_cache.write_cache()
        updated_stations = updated_stations \
            .round({"Total price": 2, f"{self.amount}l price": 2, "95E10 Price": 3}) \
            .sort_values("Total price")

        return route_data, updated_stations


def _project(element):
    return transform(PROJECTION, element)
