import pandas as pd
from shapely.geometry import LineString, Point
from shapely.ops import transform
import pyproj
from .cache import RouteCache
from .route import get_route
from functools import partial


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

    def calc(self, row):
        lat = row["lat"]
        lon = row["lon"]
        name = row["Name"]
        price = row["95E10 Price"]

        route_query = f"{lat},{lon}" if lat and lon else f'{name} Helsinki'
        distance, duration, route_path = get_route(self.location, route_query,
                                                   self.route_cache)
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
            get_route(origin, station, self.route_cache)
        distance_from_station, duration_from_station, _ = \
            get_route(station, destination, self.route_cache)

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
            get_route(start, end, self.route_cache)

        line = _project(LineString(route_path))
        notnull_stations = stations.merge(stations.apply(
            lambda row: pd.Series({"point": _project(Point(row["lat"], row["lon"]))}),
            axis=1
        ), left_index=True, right_index=True)

        stations_on_path = notnull_stations[notnull_stations.apply(
            lambda x: line.distance(x["point"]) <= 1000, axis=1
        )]
        return stations_on_path.merge(stations_on_path.apply(
            lambda x: self.cal_via(x, distance, duration), axis=1),
            left_index=True, right_index=True)

    def calculate_prices(self, stations):
        updated_stations = stations.merge(
            stations.apply(self.calc, axis=1), left_index=True, right_index=True
        ) if not isinstance(self.location, tuple) else self.calc_via_route(stations)
        self.route_cache.write_cache()
        updated_stations = updated_stations \
            .round({"Total price": 2, "40l price": 2, "95E10 Price": 3}) \
            .sort_values("Total price")

        return updated_stations


def _project(element):
    return transform(PROJECTION, element)
