import pywapi
import xdg.BaseDirectory

import argparse
import json
import os

import item

#TODO: import some type of logging framework.

WATER_FREEZING_POINT = 32
APPLICATION_NAME = 'pack-me-up'
DATA_NAME_DEFAULT = 'items.json'

parser = argparse.ArgumentParser(description=
                                 'Produce a packing list for a trip.')
parser.add_argument('zip_code', help='ZIP code of destination',
                    metavar='ZIP-code')
parser.add_argument('days', type=int, help='duration of trip in days')
parser.add_argument('--formal-wear', help='whether formal wear will be needed',
                    action='store_true')
parser.add_argument('--exercise', help='whether exercise clothes will be '
                    'needed', action='store_true')
parser.add_argument('--rain_threshold', type=float, default=0.1,
                    help='probability of rain above which to pack rain gear')
parser.add_argument('--snow_threshold', type=float, default=0.1,
                    help='probability of snow above which to pack snow gear')
#TODO: explain default here.
parser.add_argument('--data_path', help='file with Items definitions',
                    default='')


#TODO: make this a function if you don't end up using it as a class.
class Forecast:
    def __init__(self, weather, days):
        forecasts = weather['forecasts']
        if len(forecasts) < days+1:
            print('warning: forecast unavailable for part of trip duration')
        self.minimum_temperature = min(float(daily['low']) for daily in
                                       forecasts[1:days+1])
        self.maximum_temperature = max(float(daily['high']) for daily in
                                       forecasts[1:days+1])
        prob_no_rain = 1
        prob_no_snow = 1
        #When evaluating the chance of precipitation, include the day you're
        #leaving/arriving (excluded above when looking at temperatures).
        for daily in forecasts[0:days+1]:
            #Could argue that the first *day* shouldn't factor in the daytime
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
    args = parser.parse_args()
    if not args.data_path:
        for directory in xdg.BaseDirectory.load_data_paths(APPLICATION_NAME):
            path = os.path.join(directory, DATA_NAME_DEFAULT)
            if os.path.isfile(path):
                args.data_path = path
                break
        else:
            raise RuntimeError('No data found.')
    items = []
    with open(args.data_path, 'r') as f:
        items = [
            item.items[info['name']](*info['args'], **info['kwargs'])
            for info in json.load(f)
        ]

if __name__ == '__main__':
    main()
