import pywapi

import argparse
import json
import math
import os
import sys
import xml.etree.ElementTree as ETR

#TODO: import some type of logging framework.
WATER_FREEZING_POINT = 32
DEFAULT_PREFERENCES = {
    'rain_threshold': 0.1,
    'snow_threshold': 0.1,
}

parser = argparse.ArgumentParser(description=
                                 'Produce a packing list for a trip.')
parser.add_argument('zip_code', help='ZIP code of destination',
                    metavar='ZIP-code')
parser.add_argument('--formal-wear', help='whether formal wear will be needed',
                    action='store_true')
parser.add_argument('--exercise', help='whether exercise clothes will be '
                    'needed', action='store_true')
parser.add_argument('--config-file', help='custom location of configuration '
                    'file', default=os.path.join(os.environ['HOME'],
                                                 '.pack-me-up'))
parser.add_argument('days', type=int, help='duration of trip in days')
args = parser.parse_args()

preferences = DEFAULT_PREFERENCES
if os.path.isfile(args.config_file):
    with open(args.config_file, 'r') as f:
        preferences.update(json.load(f))
else:
    print('writing a default config file to {fil} ...'.format(
        fil=args.config_file))
    with open(args.config_file, 'w') as f:
        json.dump(preferences, f)

class Forecast:
    def __init__(self, weather, days):
        self.minimum_temperature = min(float(daily['low']) for daily in
                                       weather['forecasts'][1:days+1])
        self.maximum_temperature = max(float(daily['high']) for daily in
                                       weather['forecasts'][1:days+1])
        prob_no_rain = 1
        prob_no_snow = 1
        #When evaluating the chance of precipitation, include the day you're
        #leaving/arriving (excluded above when looking at temperatures).
        for daily in weather['forecasts'][0:days+1]:
            #Could argue that the first day shouldn't factor in the daytime
            #forecast. Simpler this way, though.
            prob_no_precip = (1-0.01*float(daily['day']['chance_precip'])*
                              1-0.01*float(daily['night']['chance_precip']))
            if float(daily['high']) >= WATER_FREEZING_POINT:
                prob_no_rain *= prob_no_precip
            if float(daily['low']) <= WATER_FREEZING_POINT:
                prob_no_snow *= prob_no_precip
        self.rain = 1-prob_no_rain >= preferences['rain_threshold']
        self.snow = 1-prob_no_snow >= preferences['snow_threshold']

def main():
    weather = Forecast(
        pywapi.get_weather_from_weather_com(args.zip_code, units='imperial'),
        args.days,
    )

if __name__ == '__main__':
    main()
