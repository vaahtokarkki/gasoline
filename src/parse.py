import urllib.parse as urlparse
from urllib.parse import parse_qs

import pandas as pd

from .route import get_route


def parse_station_details(row):
    """
    Parse station name and id from table cell.

    Args:
        table_cell: A td element parsed by beatifulsoup
    Returns:
        (id, name): Tuple containing station id and name
    """
    for cell in row.find_all("td"):
        anchor = cell.find("a")
        if not anchor or len(cell.contents) < 2:
            return None, None

        url = anchor["href"]
        parsed = parse_qs(urlparse.urlparse(url).query)
        id = parsed.get("id")
        id = id[0] if id else None
        return id, cell.contents[2]


def parse_gas_price(row):
    """
    Parse 95E10 gas price from table row.

    Args:
        table_cell: A td element parsed by beatifulsoup
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


def parse_table(table, cache):
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
        station = parse_station_details(row)
        id, name = station
        if not id:
            continue
        price = parse_gas_price(row)
        index.append(id)
        distance, duration = get_route("Myllyupuro Helsinki", f'{name} Helsinki', cache)
        total_price = ((7.2 / 100) * distance * 2 * price) + 40 * price \
            if price and distance else None
        gas_price = 40 * price if price else None
        data.append([name, price, distance, duration, total_price, gas_price])
    return pd.DataFrame(data, index=index, columns=[
        'Name', '95E10 Price', 'Distance', 'Duration', 'Total price', '40l price'
    ]).round(3)
