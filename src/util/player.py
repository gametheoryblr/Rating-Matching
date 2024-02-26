from abc import ABC,abstractmethod

class Player(ABC):
    def __init__(self,player_id,player_name):
        self.id = player_id
        self.name = player_name
        self.rating = 1500 # initial Elo rating 
        self.matches = []
        self.wins = 0
        self.lose = 0
        self.times = []
        self.index = 0
        self.last_match = -1
    
    @abstractmethod     
    def updateTime(self,time):
        pass 
    
    @abstractmethod
    def updateProfile(self,score:list,result:str,opponent):
        pass

