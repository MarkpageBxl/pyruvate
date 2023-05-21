#!/usr/bin/env python3

import json
from typing import List

import requests
from django.conf import settings

UV_URL = "https://www.meteo.be/fr/meteo/observations/indice-uv"


def fetch():
    req = requests.get(UV_URL)
    req.raise_for_status()
    forecast_data_raw = [
        line.strip() for line in req.text.split("\n") if "var fc_data =" in line
    ][0]
    forecast_data_raw = forecast_data_raw.split("=", maxsplit=1)[1][:-1]
    forecast_data = json.loads(forecast_data_raw)
    return forecast_data


if __name__ == "__main__":
    data = fetch()
    print(json.dumps(data, indent=2))
