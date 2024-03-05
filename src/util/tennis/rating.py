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
    winning_bonus = 0.25
    multiplication_factor = (1 - winning_bonus)/len(score)
    for st in score:
        if st[0] > st[1]:
            winner += 1
            w0 += 1
            score_p0 += multiplication_factor*st[0]/(st[0] + st[1])
            score_p1 += multiplication_factor*st[1]/(st[0] + st[1])
        else:
            w1 += 1
            score_p1 = multiplication_factor*st[1]/(st[0] + st[1])
            score_p0 = multiplication_factor*st[0]/(st[0] + st[1])
    if winner > len(score)/2:
        winner = 0
        score_p0 += winning_bonus
    else:
        winner = 1
        score_p1 += winning_bonus
    if abs(w0-w1) >= 2:
        if winner == 0:
            score_p0 += 140
        else:
            score_p1 += 140
    sscore = score_p0 + score_p1
    score_p0 = score_p0 /sscore
    score_p1 = score_p1/sscore
    return (score_p0,score_p1)



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

