#!/usr/bin/env python3

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

import requests
from django.conf import settings
from django.core.cache import cache

UV_URL = "https://www.meteo.be/fr/meteo/observations/indice-uv"


@dataclass(init=False)
class UvDataPoint:
    SAFE_EXPOSURE_FACTORS = (2.5, 3, 4, 5, 8, 15)
    instant: datetime
    uv_index: float

    def __init__(self, raw_data_point: dict[str, Any]):
        timestamp: int = raw_data_point["UNIX_TIMESTAMP"]
        uv_index: float = raw_data_point["UV_INDEX"]
        tz = ZoneInfo(settings.TIME_ZONE) if settings.USE_TZ else None
        self.instant = datetime.fromtimestamp(timestamp, tz=tz)
        self.uv_index = uv_index

    def safe_exposure_time(self, skin_type: int) -> float:
        try:
            return (200 * UvDataPoint.SAFE_EXPOSURE_FACTORS[skin_type - 1]) / (
                3 * self.uv_index
            )
        except IndexError:
            raise ValueError(f"Skin type must be 1 to 6. Got {skin_type}.")


class UvDataEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UvDataPoint):
            safe_exposure = {
                f"type{k}": obj.safe_exposure_time(k)
                for k in map(lambda x: x + 1, range(6))
            }
            return {
                "instant": obj.instant,
                "uv_index": obj.uv_index,
                "safe_exposure_time": safe_exposure,
            }
        if isinstance(obj, datetime):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)


def fetch_raw() -> list[UvDataPoint]:
    cached_value = cache.get("uv_data")
    if cached_value:
        return cached_value
    req = requests.get(UV_URL)
    req.raise_for_status()
    forecast_data_raw = [
        line.strip() for line in req.text.split("\n") if "var fc_data =" in line
    ][0]
    forecast_data_raw = forecast_data_raw.split("=", maxsplit=1)[1]
    forecast_data_raw = forecast_data_raw[: forecast_data_raw.index(";")]
    forecast_data_raw = json.loads(forecast_data_raw)
    forecast_data = [UvDataPoint(x) for x in forecast_data_raw]
    cache.set("uv_data", forecast_data)
    return forecast_data


def get_current():
    points = fetch_raw()
    tz = ZoneInfo(settings.TIME_ZONE) if settings.USE_TZ else None
    now = datetime.now(tz=tz)
    previous = None
    for point in points:
        current = point
        if now < current.instant:
            current = previous
            break
        previous = current
    return current
