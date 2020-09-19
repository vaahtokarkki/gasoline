from datetime import datetime

from rich import print
from rich.emoji import Emoji
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
    grid = Table.grid(padding=(0, 4))
    grid.add_column()
    grid.add_column(justify="left", no_wrap=True)
    grid.add_column(justify="center")
    grid.add_row(Text(''), Text('Station name and address'), Text('95E10'),
                 Text(f'40l {Emoji("car")}'), Text(f'40l {Emoji("fuelpump")}'),
                 Text("Recorded"), style="grey58")
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
    print(grid)


def _format_timestamp(timestamp):
    now = datetime.now()
    return 'Today' if now.day == timestamp.day else \
        f'{(now-timestamp).days} day{"s" if((now-timestamp).days > 1) else ""} ago'


for provider in providers:
    print(f'Fetching prices from {provider}')
    print()
    stations = provider.fetch_stations()
    print_stations(stations, 10)
