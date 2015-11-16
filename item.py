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

