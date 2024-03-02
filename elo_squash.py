import sys
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import json 
from src.util.squash.rating import Squash as Player
from src.v1.rating_elo.elo import Elo

def parse_score(score:str):
    return json.loads(score)


def clean_data(filename:str):
    matches = pd.read_csv(filename)

    # Cleaning the data.... 
    '''
        Required Params:
                - usr_id
                - date_time (for temporal k)
                - result 
                - score 
                - sets-won
                - cntr_id (for clustering)
                - oppnt_id
                - user_id
                - opponent 
                - centre_id
    '''
    matches_dropset = ['match_id',
        'centre_user_verified', 'centre_verified', 'created', 'match_type', 'sport', 'status', 'team',
        'user_opponent_verified', 'user_verified', 'verified', 'booking_id']
    try:
        matches.drop(matches_dropset,inplace=True,axis=1)
    except Exception as e:
        print("Keys not found")

    # check if identifier is unique (can be used as primary key)
    primary_keys = []
    for k in matches.keys():
        if matches[k].is_unique:
                primary_keys.append(k)
    print('All keys', matches.keys())
    print('Primary keys',primary_keys)
    return matches
    
def get_rating(score:list,result='W'):
    winner = 0
    score_p0 = 0
    score_p1 = 0
    w0 = 0 
    w1 = 0
    for st in score:
        if st[0] > st[1]:
            winner += 1
            w0 += 1
            score_p0 += st[0]*130/(st[0] + st[1])
            score_p1 += st[1]*130/(st[0] + st[1])
        else:
            w1 += 1
            score_p1 = st[1]*130/(st[0] + st[1])
            score_p0 = st[0]*130/(st[0] + st[1])
    # can omit this tbh
    # if result == 'W':
    #     score_p0 += 200 
    ssc = float(score_p0 + score_p1)
    return (score_p0/ssc,score_p1/ssc)

def date_parser(date:str): 
    date = date.split('_')[0].split('-')
    yr = int(date[0])
    month = int(date[1])
    day = int(date[0])
    time_score = (yr - 1950)*365 + (month-1)*30 + day
    return time_score


dataset = clean_data('./dataset/squash_dataset.csv')
players = {}
prat = {}
ptime = {}
plerr = {}
eloObj = Elo()
name_id = {}
print(dataset.shape[0])
for i in range(dataset.shape[0]):
    pdone = int(100*i/dataset.shape[0])
    # print('\r',pdone,end=' ')
    # print('\r[',pdone*'=',(100-pdone)*'-',']',pdone,'\%',sep='',end='')
    mtch = dataset.loc[i]
    if mtch['result'] != 'W' and mtch['result'] != 'D': # only win or draw (draws are repeated currently)
        continue
    name_id[mtch['usr_id']] = mtch['usr_id']
    if mtch['usr_id'] not in players.keys():
        players[mtch['usr_id']] = Player(mtch['usr_id'],mtch['usr_id'])
        prat[mtch['usr_id']] = {}
        plerr[mtch['usr_id']] = [0]
    if mtch['oppnt_id'] not in players.keys():
        players[mtch['oppnt_id']] = Player(mtch['oppnt_id'],mtch['oppnt_id'])
        prat[mtch['oppnt_id']] = {}
        plerr[mtch['oppnt_id']] = [0]
    
    # difference in timing...
    dscore = date_parser(mtch['date_time'])
    if players[mtch['oppnt_id']].last_match == -1:
        players[mtch['oppnt_id']].last_match = dscore
    if players[mtch['usr_id']].last_match == -1:
        players[mtch['usr_id']].last_match = dscore
    k_loser = dscore - players[mtch['oppnt_id']].last_match
    k_winner = dscore - players[mtch['usr_id']].last_match
    
    players[mtch['oppnt_id']].updateTime(dscore)
    players[mtch['usr_id']].updateTime(dscore)
    delta = players[mtch['usr_id']].rating - players[mtch['oppnt_id']].rating
    # predict result of the match 
    pred = eloObj.predict(delta) # probability of a person with rating ``advantage`` DELTA winning?? 
    try:
        # get result of the match (statistically)
        match_ratings = get_rating(parse_score(mtch['score']))
    except Exception as e:
        print("Skipped ",mtch,e)
        continue
    winner_stat = max(match_ratings[0],match_ratings[1])/(float(match_ratings[0]) + match_ratings[1])
    loser_stat = 1 - winner_stat

    plerr[mtch['oppnt_id']].append(abs(pred - loser_stat))        # might need to change this 
    plerr[mtch['usr_id']].append(abs(1 - pred - winner_stat))  # might need to change this 

    players[mtch['usr_id']].rating = eloObj.elo_rate(players[mtch['usr_id']].rating,-1*delta,winner_stat,k_winner)
    players[mtch['usr_id']].wins +=1 
    players[mtch['oppnt_id']].rating = eloObj.elo_rate(players[mtch['oppnt_id']].rating,delta,loser_stat,k_loser)
    players[mtch['oppnt_id']].lose += 1
    prat[mtch['oppnt_id']][dscore]  = players[mtch['oppnt_id']].rating
    prat[mtch['usr_id']][dscore]  = players[mtch['usr_id']].rating
    
names = list(prat.keys())
''' 
Name mapping can't be done as there are some issues in linking 
def mapNames(filename):
    df = pd.read_csv(filename)
    id2n_map = {}
    for i in range(df.shape[0]):
        entry = df.loc[i]
        print(i,entry)
        id2n_map[entry['cntct_id']] = entry['name']
    return id2n_map

name_mapping = mapNames('./dataset/squash_player_maps.csv')
'''
PLOT = 'matchwise'
def plotPlayer(name:str):
    if name not in prat.keys():
        print('ERROR: Name not found')
        return 
    if PLOT == 'datewise':
        plt.plot(prat[name].keys(),prat[name].values(),label=name)
    else:
        plt.plot(range(len(list(prat[name].keys()))),prat[name].values(),label=name)
    # print(name,prat[name][-1])
    # plt.savefig('./outputs/'+random.random()+'.png')
    return

plotPlayer(names[0])
plotPlayer(names[1])
plotPlayer(names[2])
plt.legend()
plt.savefig('./outputs/player_ratings'+datetime.datetime.now().strftime("%y_%m_%d_%H_%M")+'.png')
plt.close()

ppl = list(prat.keys())[:20]
print(ppl)
for i in ppl:
    print(i,players[i].wins,players[i].lose)
    # plotPlayer(i)
    if PLOT == 'datewise':
        plt.plot(prat[i].keys(),prat[i].values(),label=i)
    else:
        plt.plot(range(len(list(prat[i].keys()))),prat[i].values(),label=i)
plt.title('Change in Elo Rating with time')
plt.xlabel('Number of Matches')
plt.ylabel('Elo-Rating')
plt.legend()
plt.savefig('./outputs/Rating_change'+datetime.datetime.now().strftime("%y_%m_%d_%H_%M")+'.png')
plt.close()

# cumulative error 
for i in ppl:
    # plotPlayer(i)
    nmat = []
    for x in plerr[i]:
        if len(nmat) == 0:
            nmat.append(x)
        else:
            nmat.append((x+nmat[-1]*len(nmat))/(len(nmat) + 1))
    plt.plot(range(len(nmat)),nmat,label=i)
plt.title('Cumulative Error')
plt.legend()
plt.savefig('./outputs/Cumulative_error'+datetime.datetime.now().strftime("%y_%m_%d_%H_%M")+'.png')
plt.close()


# window error  
window_size = 15 
for i in ppl:
    # plotPlayer(i)
    nmat = []
    for x in range(len(plerr[i])):
        if x < window_size:
            y = 0
            ans = 0
            while y <= x:
                ans += plerr[i][y]
                y += 1
            nmat.append(ans)
        else:
            ans = 0
            y = 0 
            while y < window_size:
                y += 1
                ans += plerr[i][x - y]
            nmat.append(ans)
    plt.plot(range(len(nmat)),nmat,label=i)
plt.title('Window Error')
plt.legend()
plt.savefig('./outputs/Window_Error'+datetime.datetime.now().strftime("%y_%m_%d_%H_%M")+'.png')
plt.close()

