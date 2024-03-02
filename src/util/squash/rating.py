from ..player import Player

def parse_score(score:str):
    sc = []
    for st in score.split(' '):
        sc.append([0,0])
        idx = 0
        for pt in st.split('-'):
            sc[-1][idx] = int(pt.split('(')[0])
            idx+=1
    return sc

def get_rating(score:list):
    winner = 0
    score_p0 = 0
    score_p1 = 0
    w0 = 0
    w1 = 0
    for st in score:
        if st[0] > st[1]:
            winner += 1
            w0 += 1
            score_p0 += 130*st[0]/(st[0] + st[1])
            score_p1 += 130*st[1]/(st[0] + st[1])
        else:
            w1 += 1
            score_p1 = 130*st[1]/(st[0] + st[1])
            score_p0 = 130*st[0]/(st[0] + st[1])
    if winner > len(score)/2:
        winner = 0
        score_p0 += 200 
    else:
        winner = 1
        score_p1 += 200
    if abs(w0-w1) >= 2:
        if winner == 0:
            score_p0 += 140
        else:
            score_p1 += 140
    return (score_p0,score_p1)


class Squash(Player):
    def __init__(self,player_id,player_name):
        super(Squash,self).__init__(player_id,player_name)

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

