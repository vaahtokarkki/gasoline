import urllib.parse
from datetime import datetime

import click
from rich import box
from rich.emoji import Emoji
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from src.calc import PriceCalculator
from src.parse import PolttoaineNet
from src.UI import console


providers = [PolttoaineNet()]

parsed = PolttoaineNet()


def get_style_for_row(index):
    if index == 0:
        return 'bold green1'
    if index == 1:
        return 'green_yellow'
    if index == 2:
        return 'yellow2'
    if index == 3:
        return 'wheat1'
    if index == 4:
        return 'cornsilk1'
    return 'white'


def get_maps_link(row, location):
    name = row["Name"]
    if not isinstance(location, tuple):
        return f'[link=https://maps.google.com?q={urllib.parse.quote_plus(name)}]'
    origin, destination = location
    url_params = {"origin": origin, "destination": destination, "waypoints": name}
    return "[link=https://www.google.com/maps/dir/?api=1&" + \
        f'{urllib.parse.urlencode(url_params)}]'


def print_stations(stations, amount, location):
    index = 0
    grid = Table(box=box.MINIMAL)
    grid.add_column()
    grid.add_column(Text('Station name and address', style="grey58"), justify="left",
                    no_wrap=True)
    grid.add_column(Text('95E10', style="grey58"), justify="center")
    grid.add_column(Text(f'40l {Emoji("car")}', style="grey58"), justify="center")
    grid.add_column(Text(f'40l {Emoji("fuelpump")}', style="grey58"), justify="center")
    grid.add_column(Text('Recorded', style="grey58"))
    grid.add_column(Text('Dist (m)/Dur (min)', style="grey58"))

    for i, row in stations.head(amount).iterrows():
        style = get_style_for_row(index)
        price_style = style if row["95E10 Price"] < 1.45 else 'red1'
        name = (row["Name"][:45] + '...') if len(row["Name"]) > 48 else row["Name"]
        time_str = _format_timestamp(row["Timestamp"])
        grid.add_row(
            Text(f'{str(index+1)}. ', style=style),
            Text.from_markup(
                get_maps_link(row, location) +
                f'{name}[/link]', style=style
            ),
            Text(str(row["95E10 Price"]), style=price_style),
            Text(str(row["Total price"]), style=price_style),
            Text(str(row["40l price"]), style=price_style),
            Text(time_str, style=price_style),
            Text(f'{row["Distance"]}, {row["Duration"]}', style=price_style)
        )
        index += 1
    console.print(grid)


def _format_timestamp(timestamp):
    now = datetime.now()
    return 'Today' if now.day == timestamp.day else \
        f'{(now-timestamp).days} day{"s" if((now-timestamp).days > 1) else ""} ago'


@click.command()
@click.option('--count', '-c', default=10, help='Number of stations to display')
@click.option('--age', default=5, help='Ignore x days older price records')  # TODO
@click.option('--to', '-t', help='Specify an end point for route, instead of back and '
                                 'forth trip')
@click.option('--amount', '-a', default=40, help='Amount of gasoline to refuel')
@click.option('--consumption', '-co', default=7.2, help='Fuel consumption of car')
@click.option('--distance', '-d', default=0, help='Radius from given location to ' +
              'include stations, or in router mode distance from optimal route. ' +
              'Defaults to 20km, in route mode 1.5km')
@click.argument('location', nargs=-1)
def main(count, location, age, to, amount, consumption, distance):
    """ Fetch cheapest gas station for you based on given location """
    location = " ".join(location)
    if to:
        location = (location, to)
        distance = 1.5 if not distance else float(distance)
    else:
        distance = 20 if not distance else float(distance)
    age = 5 if age < 0 or age > 5 else age
    calculator = PriceCalculator(location, amount, consumption, distance, age)
    for provider in providers:
        location_str = location if not isinstance(location, tuple) else \
            f'{location[0]} --> {location[1]}'
        console.print(
            Panel.fit(f'Fetching prices from {provider} using location {location_str}')
        )
        stations = provider.fetch_stations()
        route_data, calculated_data = calculator.calculate_prices(stations)
        if route_data:
            console.print(
                Panel.fit(f'Best route is {route_data["distance"]}km and '
                          f'{route_data["duration"]}min')
            )
        else:
            console.print(Panel.fit('Best stations for you'))
        print_stations(calculated_data, count, location)


if __name__ == '__main__':
    main()
