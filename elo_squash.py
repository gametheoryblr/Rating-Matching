import sys
import datetime
import pandas as pd
import matplotlib.pyplot as plt
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
    return time_score



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






if __name__ == '__main__':
    '''
        Arguments:
        [0] fname 
        [--dataset] dataset name 
        [--mapper] dataset name (for name mapping)
        [--display] datewise/matchwise
        [--debug] run in debug mode (default is false) 
        [--output] output folder destination
    '''
    arguments = parseArguments(sys.argv)
    dataset = clean_data(arguments.dataset)

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
            graph[int(mtch['usr_id'])] = []
            players[mtch['usr_id']] = Player(mtch['usr_id'],mtch['usr_id'])
            prat[mtch['usr_id']] = {}
            plerr[mtch['usr_id']] = [0]
        if mtch['oppnt_id'] not in players.keys():
            graph[int(mtch['oppnt_id'])] = []
            players[mtch['oppnt_id']] = Player(mtch['oppnt_id'],mtch['oppnt_id'])
            prat[mtch['oppnt_id']] = {}
            plerr[mtch['oppnt_id']] = [0]

        # difference in timing...
        dscore = date_parser(mtch['date_time'])
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
        graph[int(mtch['usr_id'])].append(int(mtch['oppnt_id']))
        graph[int(mtch['oppnt_id'])].append(int(mtch['usr_id']))
        
        plerr[mtch['oppnt_id']].append(abs(pred - loser_stat))        # loss for opponent
        plerr[mtch['usr_id']].append(abs(1 - pred - winner_stat))  # loss for winner 

        players[mtch['usr_id']].rating = eloObj.elo_rate(players[mtch['usr_id']].rating,-1*delta,winner_stat,k_winner)
        players[mtch['usr_id']].wins +=1 
        
        players[mtch['oppnt_id']].rating = eloObj.elo_rate(players[mtch['oppnt_id']].rating,delta,loser_stat,k_loser)
        players[mtch['oppnt_id']].lose += 1
        
        prat[mtch['oppnt_id']][dscore]  = players[mtch['oppnt_id']].rating
        prat[mtch['usr_id']][dscore]  = players[mtch['usr_id']].rating
        
        #TODO:Add time-based updates here...
    print()
    print('Done training on data')    
    # for i in graph.keys():
    #     for j in graph[i]:
    #         print(i,j,file=fpt)
    fpt = open('./op.json','w')
    print(graph,file=fpt)
    # fpt.write(json.dumps(graph))
    fpt.close()
    colors = {}
    ccolor = 0
    colors[0] = []
    allocated_color = {}
    for i in graph.keys():
        allocated_color[int(i)] = -1

    def dfs(parent,node,color,verbose=False):
        global allocated_color
        global graph
        global colors
        if verbose:
            print(node,sep=' ')
        if color == 17:
            print(node)
        allocated_color[int(node)] = color
        colors[color].append(node)
        for child in graph[node]:
            if parent != child and allocated_color[node] == -1:
                dfs(node,child,color,verbose)


    for i in graph.keys():
        if allocated_color[int(i)] == -1:
            dfs(-1,i,ccolor)
            ccolor += 1
            colors[ccolor] = []
        else:
            print('not allocating to',i)
    print(allocated_color[3300])
    dfs(-1,3300,17,True)
    print()

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
    try:
        names = json.load(arguments.input)['input']
    except:
        print('Error while reading input, printing stats for all players')
        names = list(prat.keys())
    
    # plot data 
    plotPlayerRatings(names,prat,arguments.display,arguments)
    plotCumulativeError(names,plerr,arguments.display,arguments)
    plotWindowError(names,plerr,arguments.display,arguments)
    