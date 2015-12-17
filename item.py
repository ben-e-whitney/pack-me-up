import math

class Item:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.name = kwargs['name']

    def recipe(self):
        return {'name': self.__class__.__name__, 'args': self.args,
            'kwargs': self.kwargs}

    def eligible(self, *args, **kwargs):
        return True

    def number(self, *args, **kwargs):
        return 1

class DurationDependentItem(Item):
    def __init__(self, *args, **kwargs):
        self.minimum_duration = kwargs.get('minimum_duration', None)
        self.maximum_duration = kwargs.get('maximum_duration', None)
        self.per_day = kwargs['per_day'] if 'per_day' in kwargs else (
            1 / kwargs['days_per'] if 'days_per' in kwargs else None)
        super().__init__(*args, **kwargs)

    def eligible(self, *args, **kwargs):
        duration_acceptable = ((self.minimum_duration is None or
                                self.minimum_duration <= kwargs['days']) and
                               (self.maximum_duration is None or
                                self.maximum_duration >= kwargs['days']))
        return duration_acceptable and super().eligible(*args, **kwargs)

    def number(self, *args, **kwargs):
        if self.per_day is not None:
            return math.ceil(kwargs['days'] * self.per_day)
        else:
            return super().number(*args, **kwargs)

class WeatherDependentItem(Item):
    def __init__(self, *args, **kwargs):
        self.min_lo_temp = kwargs.get('low_temperature_above', None)
        self.max_lo_temp = kwargs.get('low_temperature_below', None)
        self.min_hi_temp = kwargs.get('high_temperature_above', None)
        self.max_hi_temp = kwargs.get('high_temperature_below', None)
        #TODO: document what these stand for.
        self.rain = kwargs.get('rain', None)
        self.snow = kwargs.get('snow', None)
        super().__init__(*args, **kwargs)

    def eligible(self, *args, **kwargs):
        tempature_acceptable = (
            (self.min_lo_temp is None or
             kwargs['minimum_temperature'] >= self.min_lo_temp) and
            (self.max_lo_temp is None or
             kwargs['minimum_temperature'] <= self.max_lo_temp) and
            (self.min_hi_temp is None or
             kwargs['maximum_temperature'] >= self.min_hi_temp) and
            (self.max_hi_temp is None or
             kwargs['maximum_temperature'] <= self.max_hi_temp)
        )
        precipitation_acceptable = (
            (self.rain is None or kwargs['rain'] == self.rain) and
            (self.snow is None or kwargs['snow'] == self.snow)
        )
        return (tempature_acceptable and precipitation_acceptable and
                super().eligible(*args, **kwargs))

class ClothingItem(DurationDependentItem, WeatherDependentItem):
    def __init__(self, *args, **kwargs):
        self.formal = kwargs.get('formal', None)
        super().__init__(*args, **kwargs)

    def eligible(self, *args, **kwargs):
        formality_acceptable = (self.formal is None or
                                self.formal == kwargs['formal_wear'])
        return formality_acceptable and super().eligible(*args, **kwargs)

items = {cls.__name__: cls for cls in (
    Item,
    DurationDependentItem,
    WeatherDependentItem,
    ClothingItem
)}
