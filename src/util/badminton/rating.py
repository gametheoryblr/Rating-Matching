from ..player import Player


class Badminton(Player):
    def __init__(self,player_id,player_name):
        super(Badminton,self).__init__(player_id,player_name)

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

