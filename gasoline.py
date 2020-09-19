from datetime import datetime

import click
from rich import box, print
from rich.console import Console
from rich.emoji import Emoji
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from src.parse import PolttoaineNet


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


def print_stations(stations, amount):
    index = 0
    grid = Table(box=box.MINIMAL)
    grid.add_column()
    grid.add_column(Text('Station name and address', style="grey58"), justify="left",
                    no_wrap=True)
    grid.add_column(Text('95E10', style="grey58"), justify="center")
    grid.add_column(Text(f'40l {Emoji("car")}', style="grey58"), justify="center")
    grid.add_column(Text(f'40l {Emoji("fuelpump")}', style="grey58"), justify="center")
    grid.add_column(Text('Recorded', style="grey58"))

    for i, row in stations.head(amount).iterrows():
        style = get_style_for_row(index)
        price_style = style if row["95E10 Price"] < 1.45 else 'red1'
        name = (row["Name"][:45] + '...') if len(row["Name"]) > 48 else row["Name"]
        time_str = _format_timestamp(row["Timestamp"])
        grid.add_row(
            Text(f'{str(index+1)}. ', style=style),
            Text(name, style=style),
            Text(str(row["95E10 Price"]), style=price_style),
            Text(str(row["Total price"]), style=price_style),
            Text(str(row["40l price"]), style=price_style),
            Text(time_str, style=price_style)
        )
        index += 1
    Console().print(grid)


def _format_timestamp(timestamp):
    now = datetime.now()
    return 'Today' if now.day == timestamp.day else \
        f'{(now-timestamp).days} day{"s" if((now-timestamp).days > 1) else ""} ago'


@click.command()
@click.option('--count', '-c', default=10, help='Number of stations to display')
@click.option('--age', '-a', default=5, help='Ignore x days older price records')
@click.argument('location', nargs=-1)
def main(count, location, age):
    """ Fetch cheapest gas station for you based on given location """
    location = " ".join(location)
    for provider in providers:
        print(Panel.fit(f'Fetching prices from {provider} using location {location}'))
        stations = provider.fetch_stations(location)
        print_stations(stations, count)


if __name__ == '__main__':
    main()
