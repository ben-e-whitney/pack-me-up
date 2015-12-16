class Item:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.name = kwargs['name']

    def to_JSON(self, f):
        json.dump({'args': self.args, 'kwargs': self.kwargs}, f)

    def eligible(self, *args, **kwargs):
        return True

    def number(self, *args, **kwargs):
        return 1

class DurationDependentItem(Item):
    def __init__(self, *args, **kwargs):
        self.minimum_duration = kwargs.get('minimum_duration', None)
        self.maximum_duration = kwargs.get('maximum_duration', None)
        self.per_day = kwargs.get('per_day', None)
        super().__init__(*args, **kwargs)

    def eligible(self, *args, **kwargs):
        duration = kwargs['duration']
        duration_acceptable = ((self.minimum_duration is None or
                                self.minimum_duration <= duration) and
                               (self.maximum_duration is None or
                                self.maximum_duration >= duration))
        return duration_acceptable and super().eligible(*args, **kwargs)

    def number(self, *args, **kwargs):
        if self.per_day is not None:
            return math.ceil(kwargs['duration'] * self.per_day)
        else:
            return super().number(*args, **kwargs)

class WeatherDependentItem(Item):
    def __init__(self, *args, **kwargs):
        self.minimum_temperature = kwargs.get('minimum_temperature', None)
        self.maximum_temperature = kwargs.get('maximum_temperature', None)
        #TODO: document what these stand for.
        self.rain = kwargs.get('rain', None)
        self.snow = kwargs.get('snow', None)
        super().__init__(*args, **kwargs)

    def eligible(self, *args, **kwargs):
        weather = kwargs['weather']
        tempature_acceptable = (
            (self.minimum_temperature is None or
             weather.minimum_temperature >= self.minimum_temperature) and
            (self.maximum_temperature is None or
             weather.maximum_temperature <= self.maximum_temperature)
        )
        precipitation_acceptable = (
            (self.rain is None or weather.rain == self.rain) and
            (self.snow is None or weather.snow == self.snow)
        )
        return (tempature_acceptable and precipitation_acceptable and
                super().eligible(*args, **kwargs))

class ClothingItem(DurationDependentItem, WeatherDependentItem):
    def __init__(self, *args, **kwargs):
        self.formal = kwargs.get('formal', None)
        super().__init__(*args, **kwargs)

    def eligible(self, *args, **kwargs):
        formal = kwargs['formal']
        formality_acceptable = self.formal is None or self.formal == formal
        return formality_acceptable and super().eligible(*args, **kwargs)
