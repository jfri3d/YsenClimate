import os

import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path='.envrc')

LAT = os.environ.get("LAT")
LON = os.environ.get("LON")
ACCUWEATHER_TOKEN = os.environ.get("ACCUWEATHER_TOKEN")


def get_location():
    response = requests.get(
        'http://dataservice.accuweather.com/locations/v1/cities/geoposition/search',
        params={'q': '{},{}'.format(LAT, LON), 'apikey': ACCUWEATHER_TOKEN},
    )

    return response.json()['Key']


def get_forecast(loc_key):
    response = requests.get(
        'http://dataservice.accuweather.com/forecasts/v1/hourly/12hour/{}'.format(loc_key),
        params={'metric': True, 'details': True, 'apikey': ACCUWEATHER_TOKEN},
    )

    return response.json()


def get_current(loc_key):
    response = requests.get(
        'http://dataservice.accuweather.com/currentconditions/v1/{}'.format(loc_key),
        params={'metric': True, 'details': True, 'apikey': ACCUWEATHER_TOKEN},
    )

    return response.json()


loc_key = get_location()
resp = get_forecast(loc_key)
resp2 = get_current(loc_key)
