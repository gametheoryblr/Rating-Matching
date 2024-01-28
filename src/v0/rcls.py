import elo 
from rating_elo.elo import EloType,Elo

class Rating:
    def __init__(self,eloType=EloType.vanilla):
        self.players = {}
        self.elo = Elo(eloType)
    '''
        Abstract method; to be implemented in the derived class (depending on sport)
    '''
    def conduct_match(self,player_1:str,player_2:str,score:list,meta:dict):
        pass 

    def change_rating(self,winner:str,loser:float):
        new_ratings = elo.rate_1vs1(self.players[winner].rating,self.players[loser].rating)
        self.players[winner] = new_ratings[0] 
        self.players[loser] = new_ratings[1]

    def addPlayer(self,player_id,player_obj):
        if player_id in self.players.keys():
            print('ERROR: Player already exists')
        self.players[player_id] = player_obj
    
    

class Tennis(Rating):
    def __init__(self,rtype=EloType.vanilla):
        super(rtype)
        self.sport = 'tennis'

    def parse_score(self,score:str):
        sc = []
        for st in score.split(' '):
            sc.append([0,0])
            idx = 0
            for pt in st.split('-'):
                sc[-1][idx] = int(pt)
                idx+=1
        return sc

    def conduct_match(self, player_1: str, player_2: str, score: list, meta: dict):
        p1 = 0
        p2 = 0
        for st in score:
            if st[0] > st[1]:
                p1 += 1
            else: 
                p2 += 1
        if p1 > p2:
            self.change_rating(player_1,player_2)
        else:
            self.change_rating(player_2,player_1)
 
        return super().conduct_match(player_1, player_2, score, meta)    