import sys
import datetime
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from plotter import PlotEngine
import json 

from src.util.squash.rating import Squash as Player
from src.v1.rating_elo.elo import Elo
from src.util.arparse import parseArguments

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
    timestamp = yr*10000 + int(month/12*100)*100 + int(day/(30 + month%2)*100)
    return time_score, timestamp



def plotPlayerRatings(names,prat,PLOT,arguments):
    def plotPlayer(name:str):
        if name not in prat.keys():
            print('ERROR: Name not found')
            return 
        if PLOT == 'datewise':
            plt.plot(prat[name].keys(),prat[name].values(),label=name)
        else:
            plt.plot(range(len(list(prat[name].keys()))),prat[name].values(),label=name)
        return
    for z in names:
        plotPlayer(z)

    plt.legend()
    if PLOT == 'datewise':
        plt.xlabel('Dates')
    else:
        plt.xlabel('Matches')
    plt.ylabel('Rating')
    plt.title(f'Player Ratings {PLOT}')
    if arguments.output == None:
        plt.show()
    else:
        plt.savefig(arguments.output+datetime.datetime.now().strftime("%y_%m_%d_%H_%M")+'.png')
        plt.close()


'''
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
'''

# cumulative error (@Varul make it for both date/matchwise)
def plotCumulativeError(ppl,plerr,PLOT,arguments):
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
    if arguments.output == None:
        plt.show()
    else:
        plt.savefig(arguments.output+datetime.datetime.now().strftime("%y_%m_%d_%H_%M")+'.png')
        plt.close()

def plotWindowError(ppl,plerr,PLOT,arguments):
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
    if arguments.output == None:
        plt.show()
    else:
        plt.savefig(arguments.output+datetime.datetime.now().strftime("%y_%m_%d_%H_%M")+'.png')
        plt.close()


def evaluateData(dataset,filename,begin_date=0,end_date=99999999):
    # Initialize variables 
    players = {}
    prat = {}
    ptime = {}
    plerr = {}
    eloObj = Elo()
    name_id = {}
    graph = {}
    
    if arguments.debug:
        print('Dataset Shape',dataset.shape[0])
    for i in range(dataset.shape[0]):
        pdone = int(100*i/dataset.shape[0])
        print('\r[',pdone*'=',(100-pdone)*'-',']',pdone,'\%',sep='',end='')
        mtch = dataset.loc[i]
        if mtch['result'] not in ['W']: # ignore draws....(losses are just repeated datapoints)
            continue
        name_id[mtch['usr_id']] = mtch['usr_id'] # TODO: change this line @Varul 
        if mtch['usr_id'] not in players.keys():
            # graph[int(mtch['usr_id'])] = []
            players[mtch['usr_id']] = Player(mtch['usr_id'],mtch['usr_id'])
            prat[str(mtch['usr_id'])] = {}
            plerr[str(mtch['usr_id'])] = {}
        if mtch['oppnt_id'] not in players.keys():
            # graph[int(mtch['oppnt_id'])] = []
            players[mtch['oppnt_id']] = Player(mtch['oppnt_id'],mtch['oppnt_id'])
            prat[str(mtch['oppnt_id'])] = {}
            plerr[str(mtch['oppnt_id'])] = {}

        # difference in timing...
        dscore,timestamp = date_parser(mtch['date_time'])
        timestamp = str(timestamp)
        #TODO:@Varul add date parser here (for datewise stuff)

        if players[mtch['oppnt_id']].last_match == -1:
            players[mtch['oppnt_id']].last_match = dscore
        if players[mtch['usr_id']].last_match == -1:
            players[mtch['usr_id']].last_match = dscore

        # This difference in time from last match will be passed as the argument to update the score...
        # 1 is added to keep the value of k_loser/k_winner >= 0
        k_winner = dscore - players[mtch['usr_id']].last_match + 1
        k_loser = dscore - players[mtch['oppnt_id']].last_match + 1
        
        players[mtch['oppnt_id']].updateTime(dscore)
        players[mtch['usr_id']].updateTime(dscore)
        delta = players[mtch['usr_id']].rating - players[mtch['oppnt_id']].rating
        # predict result of the match 
        pred = eloObj.predict(delta) # probability of a person with rating ``advantage`` DELTA winning 
        try:
            # get result of the match (statistically)
            match_ratings = get_rating(parse_score(mtch['score']))
        except Exception as e:
            print("Skipped ",mtch,e)
            continue

        winner_stat = max(match_ratings[0],match_ratings[1])/(float(match_ratings[0]) + match_ratings[1])
        loser_stat = 1 - winner_stat

        #UPDATE SCORES HERE 
        # graph[mtch['usr_id']].append(int(mtch['oppnt_id']))
        # graph[mtch['oppnt_id']].append(int(mtch['usr_id']))
        
        plerr[str(mtch['oppnt_id'])][timestamp] = (abs(pred - loser_stat))        # loss for opponent
        plerr[str(mtch['usr_id'])][timestamp] = (abs(1 - pred - winner_stat))  # loss for winner 

        players[mtch['usr_id']].rating = eloObj.elo_rate(players[mtch['usr_id']].rating,-1*delta,winner_stat,k_winner)
        players[mtch['usr_id']].wins +=1 
        
        players[mtch['oppnt_id']].rating = eloObj.elo_rate(players[mtch['oppnt_id']].rating,delta,loser_stat,k_loser)
        players[mtch['oppnt_id']].lose += 1
        
        prat[str(mtch['oppnt_id'])][timestamp]  = players[mtch['oppnt_id']].rating
        prat[str(mtch['usr_id'])][timestamp]  = players[mtch['usr_id']].rating
        
        #TODO:Add time-based updates here...
    print()
    print('Done training on data')    
    final_dict = {
        'rating':prat,
        'error':plerr
    }
    with open(filename,'w') as fp:
        json.dump(final_dict,fp)

if __name__ == '__main__':
    arguments = parseArguments(sys.argv)
    plotter = PlotEngine(arguments.display,arguments.plot_path)

    stdt = arguments.startTime
    endt = arguments.endTime
    subFilter = None 
    if arguments.input != None:
        with open(arguments.input,'r') as fp:
            subFilter = json.load(fp)['inputs']
    print(subFilter)
    dataset = clean_data(arguments.dataset)
    evaluateData(dataset,arguments.output,stdt,endt)
    plotter.load_data(arguments.output)
    plotter.plot_ratings(subFilter)
