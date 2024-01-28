from enum import Enum

class EloType(Enum):
    vanilla = 'vanilla'
    continuous = 'continuous'
    temporal_vanilla = 'temporal-vanilla'
    temporal_continuous = 'temporal-continuous'

class Elo:
    def __init__(self,elo_type=EloType.vanilla):
        self.base = 10.0 
        self.const = 400.0 
        self.k = 1
        self.__elo_type = elo_type
    '''
        delta is the rating difference in the current match's performance
    '''
    def vanilla_elo(self,old_ratings, delta,time=1):
        ea = 1 / (1 + self.base**(delta/self.const))
        if delta > 0:
            delta = 1
        else:
            delta = 0
        return old_ratings + self.k*(delta - ea)

    def elo_rate(self,old_ratings,delta,time=1):
        if self.__elo_type == EloType.vanilla:
            return self.vanilla_elo(old_ratings,delta,time)
        