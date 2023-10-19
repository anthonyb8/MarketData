import random 
import datetime

class RandomBardata:
    def __init__(self):
        self.bardata = []
        self.date = '2023-01-01'

    def _next_valid_date(self):
        date = datetime.datetime.strptime(self.date, '%Y-%m-%d')
        date += datetime.timedelta(days=1)
        formatted_date = date.strftime('%Y-%m-%d')
        return formatted_date
    
    def _generate_random_float(self):
        return round(random.uniform(0.5, 50),2)

    def create_bars(self, num_bars:int):
        for _ in range(num_bars):
            new_bar = {
                'date' : self.date,
                'open': self._generate_random_float(),
                'close': self._generate_random_float(),
                'high': self._generate_random_float(),
                'low': self._generate_random_float(),
                'volume': random.choice(range(1, 1000, 2)),
                'adjusted_close' : self._generate_random_float(),
            }
            self.bardata.append(new_bar)
            self.date = self._next_valid_date()
