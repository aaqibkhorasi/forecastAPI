import os
from datetime import datetime, timedelta
from time import mktime

from requests import get
import pandas as pd

try:
        KEY = os.environ["DSKY_KEY"]
except:
        print("Please set DarkSky API Key (DSKY_KEY) as an environment variable")
        exit(1)

try:
        KEY = os.environ["GMAPS_KEY"]
except:
        print("Please set Google Maps API Key (GMAPS_KEY) as an environment variable")
        exit(1)

def build_url(lat, lng, timestamp):
    return "https://api.darksky.net/forecast/{0}/{1},{2},{3}".format(
        KEY, lat, lng, timestamp
    )

def main():
    start_date = (datetime.utcfromtimestamp(float('1485907200'))).date()
    end_date   = (datetime.utcfromtimestamp(float('1488326400'))).date()

    delta = end_date - start_date

    for i in range(delta.days + 1):
        print(start_date + timedelta(days=i))
        nextDate = str(start_date + timedelta(days=i))
        print(mktime(datetime.strptime(nextDate, "%Y-%m-%d").timetuple()))

if __name__ == '__main__':
    main()