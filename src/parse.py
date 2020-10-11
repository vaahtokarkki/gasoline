import json
import urllib.parse as urlparse
from datetime import datetime
from urllib.parse import parse_qs

import pandas as pd
import requests
from bs4 import BeautifulSoup

from .cache import Cache


URL = "https://www.polttoaine.net/index.php?cmd=haku&act=hae"
DATA = "'nimi%5B%5D=520&nimi%5B%5D=2&nimi%5B%5D=5&nimi%5B%5D=11&nimi%5B%5D=18&nimi%5B%5D=19&nimi%5B%5D=20&nimi%5B%5D=23&nimi%5B%5D=29&nimi%5B%5D=31&nimi%5B%5D=32&nimi%5B%5D=39&nimi%5B%5D=41&nimi%5B%5D=44&nimi%5B%5D=47&nimi%5B%5D=49&nimi%5B%5D=52&nimi%5B%5D=53&nimi%5B%5D=58&nimi%5B%5D=59&nimi%5B%5D=66&nimi%5B%5D=68&nimi%5B%5D=69&nimi%5B%5D=77&nimi%5B%5D=78&nimi%5B%5D=84&nimi%5B%5D=85&nimi%5B%5D=88&nimi%5B%5D=90&nimi%5B%5D=92&nimi%5B%5D=99&nimi%5B%5D=104&nimi%5B%5D=105&nimi%5B%5D=106&nimi%5B%5D=107&nimi%5B%5D=113&nimi%5B%5D=124&nimi%5B%5D=125&nimi%5B%5D=130&nimi%5B%5D=136&nimi%5B%5D=142&nimi%5B%5D=143&nimi%5B%5D=144&nimi%5B%5D=149&nimi%5B%5D=160&nimi%5B%5D=161&nimi%5B%5D=162&nimi%5B%5D=163&nimi%5B%5D=168&nimi%5B%5D=171&nimi%5B%5D=177&nimi%5B%5D=184&nimi%5B%5D=185&nimi%5B%5D=186&nimi%5B%5D=188&nimi%5B%5D=195&nimi%5B%5D=527&nimi%5B%5D=221&nimi%5B%5D=222&nimi%5B%5D=227&nimi%5B%5D=228&nimi%5B%5D=229&nimi%5B%5D=233&nimi%5B%5D=238&nimi%5B%5D=240&nimi%5B%5D=241&nimi%5B%5D=245&nimi%5B%5D=250&nimi%5B%5D=252&nimi%5B%5D=263&nimi%5B%5D=264&nimi%5B%5D=267&nimi%5B%5D=271&nimi%5B%5D=273&nimi%5B%5D=283&nimi%5B%5D=284&nimi%5B%5D=289&nimi%5B%5D=291&nimi%5B%5D=528&nimi%5B%5D=292&nimi%5B%5D=293&nimi%5B%5D=296&nimi%5B%5D=302&nimi%5B%5D=306&nimi%5B%5D=318&nimi%5B%5D=530&nimi%5B%5D=329&nimi%5B%5D=333&nimi%5B%5D=338&nimi%5B%5D=354&nimi%5B%5D=365&nimi%5B%5D=369&nimi%5B%5D=374&nimi%5B%5D=381&nimi%5B%5D=385&nimi%5B%5D=197&nimi%5B%5D=388&nimi%5B%5D=398&nimi%5B%5D=416&nimi%5B%5D=419&nimi%5B%5D=420&nimi%5B%5D=423&haku=Hae+asemat'"  # noqa: E501

HEADER = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like " +
                  "Gecko) Chrome/50.0.2661.75 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Content-Type": "application/x-www-form-urlencoded"
}


class PolttoaineNet(object):
    def __init__(self):
        self.stations_cache = Cache('polttoaine_net', 'stations.json')
        self.station_locations = self._fetch_station_locations()

    def fetch_stations(self):
        table = self._fetch_table()
        parsed = self._parse_table(table)
        return parsed

    def __repr__(self):
        return 'Polttoaine.net'

    def __str__(self):
        return self.__repr__()

    def _fetch_table(self):
        resp = requests.post(URL, headers=HEADER, data=DATA)
        soup = BeautifulSoup(resp.text, 'html.parser')
        return soup.find(id="Hinnat").find("table").find_all("tr")

    def _parse_table(self, table):
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
            name = station.get("name")
            data.append([name, price, timestamp, station.get('lat'), station.get('lon')])
        return pd.DataFrame(data, index=index, columns=[
            'Name', '95E10 Price', 'Timestamp', 'lat', 'lon'
        ]) \
            .dropna(subset=['95E10 Price', 'lat', 'lon']) \
            .astype({"95E10 Price": float, "lat": float, "lon": float})

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
            if not set(cell.attrs.get("class")).isdisjoint(set(["Pvm", "PvmTd"])):
                day, month = cell.contents[0][:-1].split(".")
                return datetime.now().replace(month=int(month), day=int(day))
        return None

    def _fetch_station_locations(self):
        """ Fetch coordinates for stations """
        if self.stations_cache.cache:
            return self.stations_cache.cache
        headers = HEADER.copy()
        headers["Referer"] = "https://www.polttoaine.net"
        resp = requests.post('https://www.polttoaine.net/ajax.php', {
            "act": "map",
            "lat": 60.21,
            "lon": 25.08
        }, headers=headers)
        if resp.status_code != 200:
            return {}
        stations = {station["id"]: {
            "name": station["nimi"],
            "lat": station["lat"],
            "lon": station["lon"]
        } for station in json.loads(resp.text)}
        self.stations_cache.update(stations)
        self.stations_cache.write_cache()
        return stations
