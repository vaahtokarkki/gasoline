import requests
from bs4 import BeautifulSoup

from src.cache import Cache
from src.parse import parse_table


cache = Cache()

URL = "https://www.polttoaine.net/Helsinki"

header = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like " +
                  "Gecko) Chrome/50.0.2661.75 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
}

r = requests.get(URL, headers=header)

soup = BeautifulSoup(r.text, 'html.parser')

table = soup.find(id="Hinnat").find("table").find_all("tr")


parsed = parse_table(table, cache)
cache.write_cache()
print(parsed.sort_values("Total price"))
