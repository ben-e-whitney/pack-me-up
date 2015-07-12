import pywapi

import sys

class Item:
    pass

class TimeDependentItem(Item):
    def __init__(self, minimum_duration=None, maximum_duration=None):
        self.minimum_duration = int(minimum_duration)
        self.maximum_duration = int(maximum_duration)

    def evaluate(self, queries):
        try:
            duration = queries['duration']
        except KeyError:
            print('TimeDependentItem not given duration query.')
            sys.exit()
        return int(self.minimum_duration <= duration.duration <=
                   self.maximum_duration)

class WeatherDependentItem(Item):
    def __init__(self, minimum_temperature=-float('inf'),
                 maximum_temperature=float('inf'), rain=None, snow=None):
        try:
            self.minimum_temperature = float(minimum_temperature)
        except TypeError:
            print('Could not interpret minimum temperature {tem} as a float.'
                  .format(tem=minimum_temperature))
            sys.exit()
        try:
            self.maximum_temperature = float(maximum_temperature)
        except TypeError:
            print('Could not interpret maximum temperature {tem} as a float.'
                  .format(tem=maximum_temperature))
            sys.exit()
        if rain is None:
            self.rain = rain
        else:
            try:
                self.rain = bool(rain)
            except TypeError:
                print('Could not interpret rain setting {rai} as a boolean.'
                      .format(rai=rain))
        if snow is None:
            self.snow = snow
        else:
            try:
                self.snow = bool(snow)
            except TypeError:
                print('Could not interpret rain setting {rai} as a boolean.'
                      .format(rai=rain))

    def evaluate(self, queries):
        try:
            weather = queries['weather']
        except KeyError:
            print('Error: WeatherDependentItem not given weather query.')
            sys.exit()
        if not (
                self.minimum_temperature <= weather.minimum_temperature and
                weather.maximum_temperature <= self.maximum_temperature
        ):
            return 0
        elif self.rain is not None:
            if weather.rain != self.rain:
                return 0
        elif self.snow is not None:
            if weather.snow != self.snow:
                return 0
        else:
            return 1

if __name__ == "__main__":
    questions = ["zip code", "days", "nights",
                     "exercise (y/n)", "formal wear needed (y/n)"]

    trip = { q: input(q + "? ").lower() for q in questions }

