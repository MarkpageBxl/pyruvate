#!/usr/bin/env python3

from zoneinfo import ZoneInfo
from datetime import datetime
import requests
import json
from typing import List

UV_URL = "https://www.meteo.be/fr/meteo/observations/indice-uv"
TZ = "Europe/Brussels"


def fetch_data():
    req = requests.get(UV_URL)
    forecast_data_raw = [
        line.strip() for line in req.text.split("\n") if "var fc_data =" in line
    ][0]
    forecast_data_raw = forecast_data_raw.split("=", maxsplit=1)[1][:-1]
    forecast_data = json.loads(forecast_data_raw)
    return forecast_data


def main():
    data = fetch_data()
    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
