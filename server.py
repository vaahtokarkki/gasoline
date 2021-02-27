import json
from fastapi import Request, FastAPI
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.calc import PriceCalculator
from src.parse import PolttoaineNet
from src.settings import DEV

app = FastAPI()

if DEV:
    origins = ['*']

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.mount("/static", StaticFiles(directory="frontend/build/static"), name="static")

templates = Jinja2Templates(directory="frontend/build")


def _format_timestamp(timestamp):
    now = datetime.now()
    return 'Today' if now.day == timestamp.day else \
        f'{(now-timestamp).days} day{"s" if((now-timestamp).days > 1) else ""} ago'


def stationToJSON(s):
    time_str = _format_timestamp(s["Timestamp"])
    return {
        "name": s["Name"],
        "95E10/l": s["95E10 Price"],
        "price_age": time_str,
        "total_price": s["Total price"],
        "only_gas": s["40l price"],
        "lat": s["lat"],
        "lon": s["lon"],
        "distance": s["Distance"],
        "durations": s["Duration"],
    }


@app.get("/")
async def serve_spa(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api")
async def get_stations(request: Request):
    body = await request.body()
    body = json.loads(body)
    location = body["from"]
    if "to" in body and body["to"]:
        location = (location, body["to"])
    age = body["age"]
    distance = body["distance"]
    amount = body["amount"]
    consumption = body["consumption"]
    calculator = PriceCalculator(location, amount, consumption, distance, age)
    stations = PolttoaineNet().fetch_stations()
    route_data, calculated_data = calculator.calculate_prices(stations)
    print(calculated_data)
    output = [
        stationToJSON(s)
        for _, s in calculated_data.iterrows()
    ]
    return output
