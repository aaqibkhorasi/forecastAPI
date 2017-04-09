#!/usr/bin/env python

import os
from datetime import datetime, timedelta
from time import mktime
import csv

import requests
import pandas as pd

try:
        DSKY_KEY = os.environ["DSKY_KEY"]
except:
        print("Please set DarkSky API Key (DSKY_KEY) as an environment variable")
        exit(1)

try:
        GMAPS_KEY = os.environ["GMAPS_KEY"]
except:
        print("Please set Google Maps API Key (GMAPS_KEY) as an environment variable")
        exit(1)

def getForecast(lat, lng, timestamp):
    return requests.get("https://api.darksky.net/forecast/{0}/{1},{2},{3}".format(
        DSKY_KEY, lat, lng, timestamp
    )).json()['daily']['data'][0]

#TODO: Retry if API fails to respond
def getLatLng(zipcode):
    res = requests.get("https://maps.googleapis.com/maps/api/geocode/" + \
            "json?components=postal_code:{0}&key={1}".format(
                zipcode, GMAPS_KEY
        )).json()
    if res['status'] == 'ZERO_RESULTS':
        return None, None

    lat = res['results'][0]['geometry']['location']['lat']
    lng = res['results'][0]['geometry']['location']['lng']
    return lat, lng

#TODO: Take locations file address as input
#TODO: Create a function to download locations file if it doesn't exist in
#      current directory
#TODO: Error handling for Geocode and DarkSky responses
#TODO: Make apis link global vars
def main():
    report = {}

    with open('./locations.csv', 'r') as f:
        reader = csv.reader(f)
        header = next(reader)
        #TODO: Try not hardcoding key names, get it from csv header
        for row in reader:
            location = row[0]
            postal_code = row[1]
            date_start = row[2]
            date_end = row[3]
            report[location] = {'postal_code' : postal_code,
                                'date_first' : date_start,
                                'date_last' : date_end,
                                'weather' : {}
                                }

    for location in report.keys():
        print(report[location])
        lat, lng = getLatLng(report[location]['postal_code'])
        # TODO: Improve it
        if lat == None:
            continue
        start_date = (datetime.utcfromtimestamp(float(report[location]['date_first']))).date()
        end_date   = (datetime.utcfromtimestamp(float(report[location]['date_last']))).date()
        delta = end_date - start_date
        for i in range(delta.days + 1):
            #print(start_date + timedelta(days=i))
            nextDate = str(start_date + timedelta(days=i))
            timestamp = mktime(datetime.strptime(nextDate, "%Y-%m-%d").timetuple())
            report[location]['weather'][nextDate] = getForecast(lat, lng, int(timestamp))
        break

    print(report)

    #data = pd.read_csv("./locations.csv", nrows=1)

    #dic = pd.Series.from_csv('./locations.csv', header=None).to_dict()

if name == '__main__':
    main()