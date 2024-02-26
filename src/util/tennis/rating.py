from ..player import Player

def get_rating(score:list):
    winner = 0
    score_p0 = 0
    score_p1 = 0
    for st in score:
        if st[0] > st[1]:
            winner += 1
            score_p0 = 130 - (10*st[1])
            score_p1 = 10*st[1]
        else:
            score_p1 = 130 - (10*st[0])
            score_p0 = 10*st[0]
    if winner >= 2:
        winner = 0
    else:
        winner = 1
    if len(score) == 2:
        if winner == 0:
            score_p0 += 140
        else:
            score_p1 += 140
    return (score_p0,score_p1)


def parse_score(score:str):
    pass


class Tennis(Player):
    def __init__(self,player_id,player_name):
        super(Tennis,self).__init__(player_id,player_name)
        self.surface_rating = {'hard':1500,'clay':1500,'grass':1500}
    
    def updateTime(self,time):
        if len(self.times) < 10:
            self.times.append(time)
        else:
            self.times[self.index] = time
            self.index += 1
            self.index %= 10
        csum = 0
        for i in self.times:
            csum += i
        csum /= len(self.times)
        self.last_match = csum 

    def updateProfile(self,score:list,result:str,opponent):
        self.matches.append((opponent.id,score))

