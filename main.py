## Importing all the necessary libaries
import re
from getpass4 import getpass
import os
import sys
import logging
import json
import time,datetime
import click,requests
import pytz
from collections import defaultdict
from itertools import groupby

SAMPLE_API_KEY = ''
DATA_PATH = click.get_app_dir('weather')
API = {'current': 'https://api.openweathermap.org/data/2.5/weather',
       'forecast': 'https://api.openweathermap.org/data/2.5/forecast',
       }
UTC = pytz.utc

logging.root.setLevel(logging.NOTSET)

file_formatter = logging.Formatter(
    '%(asctime)s:%(levelname)s:%(message)s',
    datefmt="%m/%d/%Y %I:%M:%S %p")

history_filename = os.path.join(DATA_PATH, 'history.log')
os.makedirs(os.path.dirname(history_filename), exist_ok=True)
historical_handler = logging.FileHandler(
    filename=history_filename,
    mode="a")
historical_handler.setLevel(logging.DEBUG)
historical_handler.setFormatter(file_formatter)
logging.root.addHandler(historical_handler)

screen_handler = logging.StreamHandler()
screen_handler.setFormatter(logging.Formatter('%(levelname)s:%(message)s'))
logging.root.addHandler(screen_handler)


class ApiKey(click.ParamType):
    """
    Custom click type for validating API keys. API keys must be 32-character
    """
    name = 'api-key'

    def convert(self, value, param, ctx):
        found = re.match(r'[0-9a-f]{32}', value)

        if not found:
            self.fail(
                f'{value} is not a 32-character hexadecimal string',
                param,
                ctx,
            )
        return value


def build_query(ctx: click.core.Context, location: str) -> dict:
    """
    Builds a query dictionary for the OpenWeatherMap API. The query will
    include the API key, the units (imperial), and the location. The location
    can be either a city name or a city id code.    
    """
    query = {
        'appid': ctx.obj['api_key'],
        'units': 'imperial',
        }

    city_data = get_city_data()
    locations = [city.lower() for city in city_data]

    if location.isdigit():
        query['id'] = location
    elif location.lower() in locations:
        query['id'] = city_data[location.title()]['id']
    else:
        query['q'] = location

    return query


def get_api_response(ctx: click.core.Context, api: str, location: str) -> dict:
    """
    Gets the response from the OpenWeatherMap API. If the response is a 404,
    the program will exit. If the response is a 200, the response will be
    cached to a file in the data directory. If the response is cached and
    less than 10 minutes old, the cached response will be returned instead of
    making a new request.    
    :param ctx: current click Context object
    :param api: either 'current' or 'forecast'
    :param location: name or id code of location    
    """

    if api not in API:
        raise ValueError("api must be 'current' or 'forecast'")

    datapath = os.path.join(DATA_PATH, f"{location.title()}-{api}.json")

    if (os.path.exists(datapath)
            and (time.time() - os.stat(datapath).st_mtime) <= 600):
        with open(datapath, 'r') as fp:
            response = json.load(fp)
        logging.info("Returning cached copy of request")
        return response

    params = build_query(ctx, location)
    url = API[api]

    logging.info("Getting response from host")
    response = requests.get(url, params)

    if response.json()['cod'] not in [200, '200']:
        cod = response.json()['cod']
        message = response.json()['message']
        print_color_text(f"{cod}: {message}")
        logging.error(f"Error {cod}: {message}")
        sys.exit(1)

    logging.info(f"Caching response to {datapath}")
    with open(datapath, 'w') as fp:
        json.dump(response.json(), fp)
    return response.json()


@click.group()
@click.option(
    '--api-key', '-a',
    type=ApiKey(),
    help='Enter Your API key for the OpenWeatherMap API',
)
@click.option(
    '--api-key-file', '-c',
    type=click.Path(),
    default='~/.weather.apikey.txt',
)
@click.option('-q', '--quiet', count=True)
@click.option('-v', '--verbose', count=True)
@click.version_option(version='0.1.0')
@click.pass_context
def main(ctx, api_key, api_key_file, quiet, verbose):
    """
    Experience the convenience of a compact command-line weather tool that instantly provides the current weather for any LOCATION you desire. Provide the city name and optionally a two-digit country code. Here are two examples:

    1. London,UK -> "weather temp London"
    
    2. Mumbai -> "weather temp Mumbai"

    You need a valid API key from OpenWeatherMap for the tool to work. You can
    sign up for a free account at https://openweathermap.org/appid.
    """    
    screen_handler.setLevel(30+10*(quiet-verbose))
    if not os.path.exists(DATA_PATH):
        logging.info("Creating default data folder")
        os.mkdir(DATA_PATH)

    if ctx.invoked_subcommand not in ["log", "showdata"]:
        lastrun_handler = logging.FileHandler(
            filename=os.path.join(DATA_PATH, 'weather.log'),
            mode="w")
        lastrun_handler.setFormatter(file_formatter)
        lastrun_handler.setLevel(logging.INFO)
        logging.root.addHandler(lastrun_handler)

    filename = os.path.expanduser(api_key_file)

    if not api_key and os.path.exists(filename):
        with open(filename) as cfg:
            api_key = cfg.read()

    ctx.obj = {
        'api_key': api_key,
        'api_key_file': filename,
    }


@main.command()
@click.pass_context
def storeapi(ctx):
    """
    Store the API key for OpenWeatherMap.
    The application will prompt you for your key.
    """
    logging.info('Setting API Key File')
    api_key_file = ctx.obj['api_key_file']

    api_key = getpass(click.style("Please enter your API key ", fg='cyan', bold=True, italic=True))

    with open(api_key_file, 'w') as cfg:
        cfg.write(api_key)

@main.command()
@click.pass_context
def log(ctx):
    """Print the log of the last run"""
    with open(os.path.join(DATA_PATH, 'weather.log'), 'r') as fp:
        click.echo(click.style(fp.read(),fg='cyan'), nl=False)


def get_city_data():
    """
    Returns a dictionary of previously stored city IDs.
    The list of City IDs can be download from
    http://bulk.openweathermap.org/sample/city.list.json.gz
    """
    cities_path = os.path.join(DATA_PATH, 'cities.json')    
    if not os.path.exists(cities_path) or os.stat(cities_path).st_size == 0:
        logging.info("Creating empty cities file")
        with open(cities_path, 'w') as fp:
            json.dump(dict(), fp)
        return {}

    with open(cities_path, 'r') as fp:
        data = json.load(fp)
    return data


def write_city_data(city_data):
    """
    Stores the city data
    """
    logging.info("Writing city data")
    cities_path = os.path.join(DATA_PATH, 'cities.json')
    with open(cities_path, 'w') as fp:
        json.dump(city_data, fp)

@main.command()
@click.argument('location')
@click.pass_context
def current(ctx, location):
    """
    Show the current weather for a location using OpenWeatherMap data.
    """
    logging.info("Getting current weather for %s", location)
    response = get_api_response(ctx, 'current', location)

    weather = response['weather'][0]['description']
    click.echo(click.style(f"The weather in {location} right now: {click.style(weather,underline=True)}.",fg='cyan',bold=True,italic=True))

@main.command()
@click.argument('location')
@click.pass_context
def humidity(ctx,location):
    """
    Show the current humidity for a location using OpenWeatherMap data.
    """
    logging.info("Getting humidity for %s", location)
    response = get_api_response(ctx, 'current', location)

    humidity = response['main']['humidity']
    click.echo(click.style(f"The humidity in {location} right now: {humidity}%.",fg='cyan',bold=True,italic=True))

@main.command()
@click.argument('location')
@click.argument('temperature_unit')
@click.pass_context
def temp(ctx, location,temperature_unit):
    """
    Show the current temperature and the deviation of the current temperature.
    -> Temperature Unit can be F or C.
    """
    logging.info("Getting temperature for %s", location)
    response = get_api_response(ctx, 'current', location)
    if temperature_unit=="F":
        temp = response['main']['temp']
        low = response['main']['temp_min']
        high = response['main']['temp_max']
        print_color_text(f"Current Temperature is {temp}°F with a range of {low}°F to {high}°F")
    else:    
        temp = round((response['main']['temp']-32)*5/9,1)
        low = round((response['main']['temp_min']-32)*5/9,1)
        high = round((response['main']['temp_max']-32)*5/9,1)    
        print_color_text(f"Current Temperature is {temp}°C with a range of {low}°C to {high}°C")


def underline_numbers(match):
    return click.style(match.group(0), underline=True, fg='cyan', bold=True, italic=True)

def print_color_text(text):
    """
    Print text in color using Click
    """                
    styled_text = re.sub(r'\d+|\.', underline_numbers, text)
    styled_text = click.style(styled_text, fg='cyan', bold=True, italic=True)
    click.echo(styled_text)


@main.command()
@click.argument('location')
@click.pass_context
def dump(ctx, location):
    """
    Show the json response for current weather information
    """
    logging.info("Getting JSON dump for %s", location)
    response = get_api_response(ctx, 'current', location)
    click.echo(click.style(json.dumps(response,indent=4),fg='cyan'))


def date_bit(text):
    """Return a datetime.date representation of a datetime stamp"""
    return datetime.datetime.strptime(text, "%Y-%m-%d %H:%M:%S").date()


@main.command()
@click.argument('location')
@click.pass_context
def forecast(ctx, location):
    """
    List the lows and highs for the next few days
    """
    logging.info("Getting 5-day highs forcast")
    response = get_api_response(ctx, 'forecast', location)
    data = defaultdict(list)

    for thing in response['list']:
        data[date_bit(thing['dt_txt'])].append(
                (float(thing['main']['temp_min']),
                 float(thing['main']['temp_max']),
                 thing['weather'][0]['description']))

    for day in sorted(data):
        print(day,
              "{:5.2f}".format(min([item[0] for item in data[day]])),
              "{:5.2f}".format(max([item[1] for item in data[day]])),
              ', '.join([k for k, g in groupby(item[2] for item in data[day])]))


@main.command()
@click.argument('location')
@click.pass_context
def howmuchrain(ctx, location):
    """
    Total the amount of rain for the next five days.
    """
    logging.info("Getting 5-day rain totals")
    response = get_api_response(ctx, 'forecast', location)
    data = defaultdict(float)

    for thing in response['list']:
        if 'rain' in thing:
            data[date_bit(thing['dt_txt'])] += thing['rain'].get('3h', 0.0)

    for day in sorted(data):
        print(f"{day:%a %m/%d} {data[day]:5.2f}mm",
              f"({data[day]*0.03937:0.02} inches)")
    total = sum(data[day] for day in data)
    formatted_total_mm = "{:.2f}".format(total)
    formatted_total_inches = "{:.3f}".format(total * 0.03937)
    colored_total_mm = click.style(formatted_total_mm, fg='cyan', bold=True)
    colored_total_inches = click.style(formatted_total_inches, fg='green')
    click.echo(f"Total: {colored_total_mm}mm ({colored_total_inches} inches)")


@main.command()
@click.argument('location')
@click.pass_context
def daylight(ctx, location):
    """
    Today's sunrise and sunset
    """
    logging.info("Getting Sunrise and Sunset data")    
    response = get_api_response(ctx, 'current', location)        
    sunrise = datetime.datetime.utcfromtimestamp(response['sys']['sunrise']) + datetime.timedelta(hours=(response['timezone']/3600))
    sunset = datetime.datetime.utcfromtimestamp(response['sys']['sunset']) + datetime.timedelta(hours=(response['timezone']/3600))
    print_color_text(f"Daylight Hours in {location} timezone: {sunrise.time():%I:%M %p} - {sunset.time():%I:%M %p}")
