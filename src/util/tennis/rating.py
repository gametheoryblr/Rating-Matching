from ..player import Player



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

