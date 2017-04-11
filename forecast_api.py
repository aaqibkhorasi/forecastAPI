#!/usr/bin/env python

import os
from datetime import datetime, timedelta
from time import mktime
import csv

import requests
import pandas as pd

# Session object to be re-used by many calls to the DarkSky api
# Opening up many different connections in a small period of time
# may stop getting response
s = requests.Session()

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
    """
    Get the daily forecast for the given latitude, longitude and timestamp
    using DarSky Forecast API
    """
    return s.get("https://api.darksky.net/forecast/{0}/{1},{2},{3}".format(
        DSKY_KEY, lat, lng, timestamp
    )).json()['daily']['data'][0]

#TODO: Retry if API fails to respond
def getLatLng(zipcode):
    """
    Get the latitude and longitude of a given zipcode using
    GoogleMaps Geo API
    """
    res = requests.get("https://maps.googleapis.com/maps/api/geocode/" + \
            "json?components=postal_code:{0}&key={1}".format(
                zipcode, GMAPS_KEY
        )).json()
    if res['status'] == 'ZERO_RESULTS':
        return None, None

    lat = res['results'][0]['geometry']['location']['lat']
    lng = res['results'][0]['geometry']['location']['lng']
    return lat, lng

def getData(report, date, locations):
    """
    Get the precipitation probability of all the locations for
    the given date
    """
    data = []
    for location in locations:
        try:
            data.append(report[location]['weather'][date]['precipProbability']*100)
        except:
            data.append('NaN')

    return data

#TODO: Take locations file address as input
#TODO: Create a function to download locations file if it doesn't exist in
#      current directory
#TODO: Error handling for Geocode and DarkSky responses
#TODO: Make apis link global vars
def main():
    report = {}
    locations = []

    # Reading locations file data
    with open('./locations.csv', 'r') as f:
        reader = csv.reader(f)
        # Skipping the header
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

    frames = []
    allDates = []
    index = 0

    # Gather daily weather data
    for location, d in report.items():
        locations.append(location)
        lat, lng = getLatLng(report[location]['postal_code'])
        # TODO: Improve it
        if lat == None or lng == None:
            continue
        start_date = (datetime.utcfromtimestamp(float(report[location]['date_first']))).date()
        end_date   = (datetime.utcfromtimestamp(float(report[location]['date_last']))).date()
        delta = end_date - start_date
        del report[location]['date_first']
        del report[location]['date_last']
        del report[location]['postal_code']
        for i in range(delta.days + 1):
            nextDate = str(start_date + timedelta(days=i))
            timestamp = mktime(datetime.strptime(nextDate, "%Y-%m-%d").timetuple())
            report[location]['weather'][nextDate] = getForecast(lat, lng, int(timestamp))

            # Calculating all dates for the PivotTable
            if nextDate not in allDates:
                allDates.append(nextDate)

        # The index of following dataframe will be the keys of report[location]['weather']
        frames.append(pd.DataFrame.from_dict(report[location]['weather']))

        print("{0} out of {1} locations data gathered".format(index+1, len(report.keys())))
        index += 1
    print("{0} out of {1} locations data gathered".format(len(report.keys()), len(report.keys())))

    # Multi-Index
    t = pd.concat(frames, keys=locations)
    t.index.set_names(['loc_id', 'weather'], inplace=True)
    t.to_csv('weatherreport.csv')

    # Produce Pivot Table
    pivotTable = {}
    for date in allDates:
        pivotTable[date] = pd.Series((getData(report, date, locations)), index=locations)

    pd.DataFrame(pivotTable).to_csv('pivottable.csv')

if __name__ == '__main__':
    main()
