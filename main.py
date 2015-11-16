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
parser.add_argument('days', help='duration of trip in days')
args = parser.parse_args()

if os.path.isfile(args.config_file):
    with open(args.config_file, 'r') as f:
        preferences = json.load(f)
    #TODO: make this more user-friendly.
    for key in DEFAULT_PREFERENCES:
        assert key in preferences
else:
    preferences = DEFAULT_PREFERENCES
    print('writing a default config file to {fil} ...'.format(
        fil=args.config_file))
    with open(args.config_file, 'w') as f:
        json.dump(preferences, f)

class Forecast:
    def __init__(self, weather, days):
        self.minimum_temperature = min(float(daily['low']) for daily in
                                       weather['forecasts'][1:days+1])
        self.minimum_temperature = max(float(daily['high']) for daily in
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

class Item:
    def __init__(self, **kwargs):
        self.name = kwargs['name']

    def to_XML(self):
        #TODO: write this.
        pass

    #TODO: or whatever.
    @classmethod
    def amount_to_bring(*args):
        return max(*args) if all(*args) else 0

class DurationDependentItem(Item):
    def __init__(self, **kwargs):
        self.minimum_duration = kwargs.get('minimum_duration', None)
        self.maximum_duration = kwargs.get('maximum_duration', None)
        self.per_day = kwargs.get('per_day', None)

    def evaluate(self, **kwargs):
        duration = kwargs['duration']
        acceptable = ((self.minimum_duration is None or
                       self.minimum_duration <= duration) and
                      (self.maximum_duration is None or
                       self.maximum_duration >= duration))
        if acceptable and self.per_day is not None:
            return math.ceil(duration*self.per_day)
        else:
            return int(acceptable)

class WeatherDependentItem(Item):
    def __init__(self, **kwargs):
        self.minimum_temperature = kwargs.get('minimum_temperature', None)
        self.maximum_temperature = kwargs.get('maximum_temperature', None)
        self.rain = kwargs.get('rain', None)
        self.snow = kwargs.get('snow', None)

    def evaluate(self, **kwargs):
        weather = kwargs['weather']
        acceptable = (
            (self.minimum_temperature is None or
             weather.minimum_temperature >= self.minimum_temperature) and
            (self.maximum_temperature is None or
             weather.maximum_temperature <= self.maximum_temperature)
        )
        acceptable = acceptable and (
            (self.rain is None or weather.rain == self.rain) and
            (self.snow is None or weather.snow == self.snow)
        )
        return int(acceptable)

class ClothingItem(DurationDependentItem, WeatherDependentItem):
    def __init__(self, **kwargs):
        super(TimeDependentItem).__init__(**kwargs)
        super(WeatherDependentItem).__init__(**kwargs)
        self.formal = kwargs.get('formal', None)

    def evaluate(self, **kwargs):
        formal = kwargs['formal']
        acceptable = self.formal is None or self.formal == formal
        #TODO: this isn't right. Need maybe class method or something for
        #combining amounts.
        return (acceptable and super(TimeDependentItem).evaluate(**kwargs) and
                super(WeatherDependentItem).evaluate(**kwargs))

def main():
    weather = Forecast(
        pywapi.get_weather_from_weather_com(args.zip_code, units='imperial'),
        args.days,
    )

if __name__ == '__main__':
    main()
