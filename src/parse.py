import json
import urllib.parse as urlparse
from datetime import datetime
from urllib.parse import parse_qs

import pandas as pd
import requests
from bs4 import BeautifulSoup

from .cache import RouteCache
from .route import get_route


URL = "https://www.polttoaine.net/Helsinki"

HEADER = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like " +
                  "Gecko) Chrome/50.0.2661.75 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
}


class PolttoaineNet(object):
    def __init__(self):
        self.cache = RouteCache('polttoaine_net')
        self.station_locations = self._fetch_station_locations()

    def fetch_stations(self, location):
        table = self._fetch_table()
        parsed = self._parse_table(table, location)
        self.cache.write_cache()
        return parsed

    def __repr__(self):
        return 'Polttoaine.net'

    def __str__(self):
        return self.__repr__()

    def _fetch_table(self):
        resp = requests.get(URL, headers=HEADER)
        soup = BeautifulSoup(resp.text, 'html.parser')
        return soup.find(id="Hinnat").find("table").find_all("tr")

    def _parse_table(self, table, location):
        """
        Parse stations and gas price from table parsed by beatifulsoup

        Args:
            table: A table element parsed by beatifulsoup
        Returns:
            DataFrame containing station details and gas price
        """
        index = []
        data = []
        for row in table:
            station = self._parse_station_details(row)
            if not station.get("id"):
                continue
            price = self._parse_gas_price(row)
            timestamp = self._parse_timestamp(row)
            index.append(station.get("id"))
            distance, duration = get_route(location, _get_route_params(station),
                                           self.cache)
            total_price = ((7.2 / 100) * distance * 2 * price) + 40 * price \
                if price and distance else None
            gas_price = 40 * price if price else None
            name = station.get("name")
            data.append([name, price, distance, duration, total_price, gas_price,
                         timestamp])
        return pd.DataFrame(data, index=index, columns=[
            'Name', '95E10 Price', 'Distance', 'Duration', 'Total price', '40l price',
            'Timestamp'
        ]).round(3).sort_values("Total price")

    def _parse_station_details(self, row):
        """
        Parse station name and id from table cell.

        Args:
            table_cell: A td element parsed by beatifulsoup
        Returns:

        """
        for cell in row.find_all("td"):
            anchor = cell.find("a")
            if not anchor or len(cell.contents) < 2:
                return {}

            url = anchor["href"]
            parsed = parse_qs(urlparse.urlparse(url).query)
            id = parsed.get("id")
            id = id[0] if id else None
            output = {
                "id": id,
                "name": cell.contents[2]
            }
            if id and id in self.station_locations:
                station = self.station_locations.get(id)
                output.update({
                    "name": station.get("name"),
                    "lat": station.get("lat"),
                    "lon": station.get("lon"),
                })
            return output
        return {}

    def _parse_gas_price(self, row):
        """
        Parse 95E10 gas price from table row.

        Args:
            table_row: A tr element parsed by beatifulsoup
        Returns:
            (String) Gas price
        """
        for cell in row.find_all("td"):
            title = cell.get("title")
            if title == "95E10":
                try:
                    return float(cell.contents[0])
                except ValueError:
                    return None
        return None

    def _parse_timestamp(self, row):
        """
        Parse timestamp for gasoline prices from table row.
        Args:
            table_row: A tr element parsed by beatifulsoup
        Returns:
            (Datetime) Timestamp
        """
        cell = None
        for cell in row.find_all("td"):
            if not cell.attrs:
                continue
            if any(key in cell.attrs.get("class") for key in ["Pvm", "PvmTD"]):
                day, month = cell.contents[0][:-1].split(".")
                return datetime.now().replace(month=int(month), day=int(day))
        return None

    def _fetch_station_locations(self):
        """ Fetch coordinates for stations """
        headers = HEADER.copy()
        headers["Referer"] = "https://www.polttoaine.net"
        resp = requests.post('https://www.polttoaine.net/ajax.php', {
            "act": "map",
            "lat": 60.21,
            "lon": 25.08
        }, headers=headers)
        if resp.status_code != 200:
            return {}
        return {station["id"]: {
            "name": station["nimi"],
            "lat": station["lat"],
            "lon": station["lon"]
        } for station in json.loads(resp.text)}


def _get_route_params(station):
    if "lat" in station and "lon" in station:
        lat = station.get("lat")
        lon = station.get("lon")
        return f'{lat},{lon}'
    name = station.get("name")
    return f'{name} Helsinki'
