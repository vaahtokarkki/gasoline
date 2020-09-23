import pandas as pd

from .cache import RouteCache
from .route import get_route


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
        distance, duration = get_route(self.location, route_query, self.route_cache)
        total_price = ((self.consumption / 100) * distance * 2 * price) + self.amount \
            * price if price and distance else None
        gas_price = self.amount * price if price else None
        return pd.Series({
            "Distance": distance,
            "Duration": duration,
            "Total price": total_price,
            "40l price": gas_price
        })

    def calculate_prices(self, stations):
        updated_stations = stations \
            .merge(stations.apply(self.calc, axis=1), left_index=True, right_index=True) \
            .round({"Total price": 2, "40l price": 2, "95E10 Price": 3})
        self.route_cache.write_cache()
        return updated_stations
