from enum import Enum
import numpy as np 

class EloType(Enum):
    vanilla = 'vanilla'
    continuous = 'continuous'
    temporal_vanilla = 'temporal-vanilla'
    temporal_continuous = 'temporal-continuous'

class Elo:
    def __init__(self,elo_type=EloType.temporal_continuous):
        self.base = 10.0 
        self.const = 400.0 
        self.k = 4
        self.__elo_type = elo_type
    '''
        delta is the rating difference in the current match's performance
    '''
    def predict(self,delta):
        return 1 / (1 + self.base**(delta/self.const))
        

    def vanilla_elo(self,old_ratings, delta, result,time=1):
        ea = 1 / (1 + self.base**(delta/self.const))
        return old_ratings + self.k*(result - ea)

    def temporal_elo(self,old_ratings, delta, result,time_k=1):
        time_k = 1 # to test 
        ea = 1 / (1 + self.base**(delta/self.const))
        return old_ratings + self.k*time_k*(result - ea)

    def elo_rate(self,old_ratings,delta,result,time=1):
        if old_ratings > 2000:
            self.k = 8
        else:
            self.k = 16
        if self.__elo_type == EloType.vanilla:
            return self.vanilla_elo(old_ratings,delta,result,time)
        if self.__elo_type == EloType.temporal_continuous:
            return self.temporal_elo(old_ratings,delta,result,1) # timestamping is not making much difference so omitted for now 