import pywapi
import xdg.BaseDirectory

import argparse
import json
import os

from . import item

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

def get_trip_info(args):
    info = vars(args)
    #TODO: add something for when forecast cannot be fetched.
    forecasts = pywapi.get_weather_from_weather_com(info['zip_code'],
        units='imperial')['forecasts']
    if len(forecasts) < info['days']+1:
        print('warning: forecast unavailable for part of trip duration')
    info.update(minimum_temperature=min(float(daily['low'])
        for daily in forecasts[1:info['days']+1]))
    info.update(maximum_temperature=max(float(daily['high'])
        for daily in forecasts[1:info['days']+1]))

    prob_no_rain = 1
    prob_no_snow = 1
    #When evaluating the chance of precipitation, include the day you're
    #leaving/arriving (excluded above when looking at temperatures).
    for daily in forecasts[0:info['days']+1]:
        #Could argue that the first *day* shouldn't factor in the daytime
        #forecast. Simpler this way, though.
        prob_no_precip = (1-0.01*float(daily['day']['chance_precip'])*
                          1-0.01*float(daily['night']['chance_precip']))
        if float(daily['high']) >= WATER_FREEZING_POINT:
            prob_no_rain *= prob_no_precip
        if float(daily['low']) <= WATER_FREEZING_POINT:
            prob_no_snow *= prob_no_precip
    info.update(rain=1-prob_no_rain >= info['rain_threshold'])
    info.update(snow=1-prob_no_snow >= info['snow_threshold'])
    return info

def main():
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
    trip_info = get_trip_info(args)

    to_print = []
    number_column_width = 0
    for item_ in items:
        if item_.eligible(**trip_info):
            num = str(item_.number(**trip_info))
            number_column_width = max(number_column_width, len(num))
            to_print.append((num, item_.name))
    for num, name in to_print:
        print('{num} {nam}'.format(num=num.ljust(number_column_width, ' '),
                                   nam=name))

if __name__ == '__main__':
    main()
