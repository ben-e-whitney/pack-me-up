import pywapi

import sys

class Forecast:
    pass

class Item:
    pass

class TimeDependentItem(Item):
    def __init__(self, **kwargs):
        self.minimum_duration = kwargs.get('minimum_duration', None)
        self.maximum_duration = kwargs.get('maximum_duration', None)

    def evaluate(self, **kwargs):
        try:
            duration = kwargs['duration']
        except KeyError:
            print('TimeDependentItem.evaluate not given duration.')
            sys.exit()
        try:
            acceptable = ((self.minimum_duration is None or
                           self.minimum_duration <= duration) and
                          (self.maximum_duration is None or
                           self.maximum_duration >= duration))
        except TypeError:
            print('Encountered error in comparing minimum duration ({mnd}), '
                  'maximum duration ({mxd}), and duration ({dur}).'.format(
                      mnd=self.minimum_duration, mxd=self.maximum_duration,
                      dur=duration))
    return int(acceptable)

class WeatherDependentItem(Item):
    def __init__(self, **kwargs):
        self.minimum_temperature = kwargs.get('minimum_temperature', None)
        self.maximum_temperature = kwargs.get('maximum_temperature', None)
        self.rain = kwargs.get('rain', None)
        self.snow = kwargs.get('snow', None)

    def evaluate(self, **kwargs):
        try:
            weather = kwargs['weather']
        except KeyError:
            print('Error: WeatherDependentItem.evaluate not given weather.')
            sys.exit()
        try:
            acceptable = (
                self.minimum_temperature <= weather.minimum_temperature and
                weather.maximum_temperature <= self.maximum_temperature
            )
        except TypeError:
            print('Encountered error in comparing minimum temperature '
                  '({mnt}), forecasted low ({low}), maximum temperature '
                  '({mxt}), and forecasted high ({hig}).'.format(
                      mnt=self.minimum_temperature,
                      low=weather.minimum_temperature,
                      mxt=self.maximum_temperature,
                      hig=weather.maximum_temperature))
            sys.exit()
        try:
            acceptable = (acceptable and (self.rain is None or
                          weather.rain == self.rain) and (self.snow is None or
                          weather.snow == self.snow))
        except TypeError:
            print('Encountered error in comparing rain forecast ({rfo}) and '
                  'rain preference ({rai}) or snow forecast ({sfo}) and '
                  'snow preference ({sno})'.format(rfo=weather.rain,
                      rai=self.rain, sfo=weather.snow, sno=self.snow))
            sys.exit()
        return int(acceptable)

def main():
    questions = ['ZIP code', 'Days', 'Exercise (y/n)',
                 'Formal wear needed (y/n)']

    trip = {question: input('{que}? ').format(que=question).lower()
            for question in questions}
    forecast = Forecast(pywapi.get_weather_from_weather_com(trip['ZIP code'],
                                                            units='imperial'))

if __name__ == '__main__':
    main()
