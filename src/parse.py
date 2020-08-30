import urllib.parse as urlparse
from urllib.parse import parse_qs

import pandas as pd


def parse_station_details(table_cell):
    """
    Parse station name and id from table cell.

    Args:
        table_cell: A td element parsed by beatifulsoup
    Returns:
        (id, name): Tuple containing station id and name
    """
    anchor = table_cell.find("a")
    if not anchor or len(table_cell.contents) < 2:
        return

    url = anchor["href"]
    parsed = parse_qs(urlparse.urlparse(url).query)
    id = parsed.get("id")
    id = id[0] if id else None
    return id, table_cell.contents[2]


def parse_gas_price(cell):
    """
    Parse 95E10 gas price from table cell.

    Args:
        table_cell: A td element parsed by beatifulsoup
    Returns:
        (String) Gas price
    """
    title = cell.get("title")
    if title == "95E10":
        return cell.contents[0]


def parse_table(table):
    """
    Parse stations and gas price from table parsed by beatifulsoup

    Args:
        table: A table element parsed by beatifulsoup
    Returns:
        DataFrame containing station details and gas price
    """
    index = []
    data = []
    for r in table:
        row = []
        for c in r.find_all("td"):
            station = parse_station_details(c)
            price = parse_gas_price(c)
            if station:
                id, name = station
                if id and name:
                    index.append(id)
                    row.append(name)

            if price:
                row.append(price)
        if row:
            data.append(row)
    return pd.DataFrame(data, index=index, columns=['Name', '95E10 Price'])
