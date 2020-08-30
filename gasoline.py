from test import test_data

import requests
from bs4 import BeautifulSoup

from src.parse import parse_table


URL = "https://www.polttoaine.net/Helsinki"

header = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like " +
                  "Gecko) Chrome/50.0.2661.75 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
}

# r = requests.get(URL, headers=header)

soup = BeautifulSoup(test_data, 'html.parser')

table = soup.find(id="Hinnat").find("table").find_all("tr")

parsed = parse_table(table)
print(parsed.sort_values("95E10 Price"))
