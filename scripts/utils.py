import os
from datetime import datetime as dt

import requests
from PIL import Image, ImageFont, ImageDraw
from constants import ASSET_PATH, ICONS
from dotenv import load_dotenv
from font_fredoka_one import FredokaOne
from inky import InkyPHAT

load_dotenv(dotenv_path='.envrc')

ACCUWEATHER_NAME = os.environ.get("ACCUWEATHER_NAME")
ACCUWEATHER_KEY = os.environ.get("ACCUWEATHER_KEY")
ACCUWEATHER_TOKEN = os.environ.get("ACCUWEATHER_TOKEN")


def get_daily(loc_key):
    r = requests.get(
        'http://dataservice.accuweather.com/forecasts/v1/daily/1day/{}'.format(loc_key),
        params={'metric': True, 'details': True, 'apikey': ACCUWEATHER_TOKEN},
    )

    return r.json()


def get_current(loc_key):
    r = requests.get(
        'http://dataservice.accuweather.com/currentconditions/v1/{}'.format(loc_key),
        params={'metric': True, 'details': True, 'apikey': ACCUWEATHER_TOKEN},
    )

    return r.json()


def get_weather():
    current = get_current(ACCUWEATHER_KEY)[0]
    daily = get_daily(ACCUWEATHER_KEY)

    weather = {
        "MinTemp": float(daily['DailyForecasts'][0]['RealFeelTemperature']['Minimum']['Value']),
        "MaxTemp": float(daily['DailyForecasts'][0]['RealFeelTemperature']['Maximum']['Value']),
        "Temp": float(current['RealFeelTemperature']['Metric']['Value']),
        "WeatherText": str(current['WeatherText']),
        "WeatherIcon": int(current['WeatherIcon']),
        "HasPrecipitation": bool(current['HasPrecipitation']),
        "PrecipitationType": current['PrecipitationType'],
    }

    # # format raw
    # weather = {
    #     "Temp": 14.1,
    #     "MinTemp": -5.2,
    #     "MaxTemp": 14.1,
    #     "WeatherText": "Cloudy",
    #     "WeatherIcon": 44,
    #     "HasPrecipitation": False,
    #     "PrecipitationType": None,
    # }

    return weather


def _load_image(path, dy):
    # open image
    im = Image.open(path)

    # keep aspect ratio
    ratio = im.size[0] / im.size[1]
    im = im.resize((int(ratio * dy), dy), resample=Image.LANCZOS)

    # build appropriate INKY palette
    pal_img = Image.new("P", (1, 1))
    pal_img.putpalette((255, 255, 255, 0, 0, 0, 255, 0, 0) + (0, 0, 0) * 252)

    return im.convert("RGB").quantize(palette=pal_img)


def update_inky():
    # initialize inky
    inky = InkyPHAT("yellow")
    inky.set_border(inky.BLACK)

    # draw empty image
    img = Image.new("P", (inky.WIDTH, inky.HEIGHT))
    inky.set_image(img)

    # initiate image
    img = Image.new("P", (inky.WIDTH, inky.HEIGHT))
    draw = ImageDraw.Draw(img)

    # add weather data
    data = get_weather()

    # HEADER
    # ======

    # include weather location
    font = ImageFont.truetype(FredokaOne, 14)
    draw.text((2, 0), ACCUWEATHER_NAME, inky.BLACK, font)

    # include date/time of last "run"
    header = dt.now().strftime("%d.%m.%Y %H:%M")
    font = ImageFont.truetype(FredokaOne, 14)
    w, h = font.getsize(header)
    draw.text((inky.WIDTH - w - 2, 0), header, inky.BLACK, font)

    draw.line((0, 15, inky.WIDTH, 15), fill=inky.BLACK, width=2)

    y_header = 17

    # BODY
    # ====

    edge = 5

    # add weather icon
    x_icon = 60
    icon = _load_image(os.path.join(ASSET_PATH, ICONS[data['WeatherIcon']]), x_icon)
    img.paste(icon, box=(edge, y_header))

    # add description
    message = data['WeatherText']
    font = ImageFont.truetype(FredokaOne, 14)
    w, h = font.getsize(message)
    draw.text((edge, inky.HEIGHT - h - edge), message, inky.BLACK, font)

    # ADD THE TEMPERATURE
    # ===================
    font = ImageFont.truetype(FredokaOne, 14)

    # add MIN temp data
    message = "{}°C".format(int(data['MinTemp']))
    w, h = font.getsize(message)
    draw.text((inky.WIDTH - w - edge, inky.HEIGHT - h - edge), message, inky.BLACK, font)
    top_min = inky.HEIGHT - h - 2 * edge

    # add MAX temp data
    message = "{}°C".format(int(data['MaxTemp']))
    w, h = font.getsize(message)
    draw.text((inky.WIDTH - w - edge, y_header + edge), message, inky.BLACK, font)
    bottom_max = y_header + h + 2 * edge

    # add temperature "line"
    x_temp_line = inky.WIDTH - 20
    draw.line((x_temp_line, top_min, x_temp_line, bottom_max), fill=inky.BLACK, width=1)

    # interpolate along line
    ratio = (data['MaxTemp'] - data['Temp']) / (data['MaxTemp'] - data['MinTemp'])
    dist = int((top_min - bottom_max) * ratio)
    temp_y = dist + bottom_max

    # current temperature (along vertical scale)
    dr = 2
    draw.ellipse((x_temp_line - dr, temp_y - dr, x_temp_line + dr, temp_y + dr), fill=inky.YELLOW)

    # add temp data
    message = "{}°C".format(int(data['Temp']))
    font = ImageFont.truetype(FredokaOne, 32)
    w, h = font.getsize(message)
    draw.text((x_temp_line - w - 20, temp_y - h // 2), message, inky.YELLOW, font)

    inky.set_image(img)
    inky.show()
